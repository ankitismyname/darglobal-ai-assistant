"""Chat logic: route the question, retrieve context, build the prompt, stream the answer, append sources.

One LLM call per user message. Greetings, non-English messages and LLM failures are handled without the model,
so the bot keeps answering (with sources) even when the free model's quota is exhausted.
"""
from __future__ import annotations

import re
from collections import OrderedDict
from collections.abc import Iterator
from dataclasses import dataclass

from llm import LLMError, stream_chat
from normalize import fmt_num, fmt_sar, is_num, listing_price_text, text_or_none
from query_parser import Filters, listing_intent, merge_follow_up, parse
from retriever import Index, ListingResult

ARABIC = re.compile(r"[؀-ۿ]")
GREETING = re.compile(r"^\s*(hi|hello|hey|hiya|salam|salaam|assalam\w*|good (morning|afternoon|evening)|thanks|thank you|"
                      r"thx|ok|okay|cool|great)\b[\s!.?]*$", re.I)
CAPABILITIES = (
    "I can help with:\n"
    "- **DarGlobal**: its projects (Dubai, Oman, Saudi Arabia, Qatar, Spain, the UK...), branded partnerships, "
    "the company, its FAQs, press releases and blog articles.\n"
    "- **Wasalt**: property listings in Saudi Arabia (Riyadh, Jeddah, Dammam, Al Khobar, Makkah, Madinah) for sale "
    "or rent, with filters such as bedrooms, budget and district, plus Wasalt's area guides.\n\n"
    "Try: *\"Which DarGlobal projects are in Oman?\"* or *\"3 bedroom apartment for rent in Riyadh under 6,000 a month\"*."
)


def filters_to_query(f: Filters) -> str:
    """'2 bedroom apartment for rent in Madinah' from structured filters (used to search on follow-ups)."""
    parts = []
    if f.bedrooms:
        parts.append(f"{f.bedrooms} bedroom")
    parts.append(" ".join(f.types) if f.types else "property")
    if f.purpose:
        parts.append(f"for {f.purpose}")
    where = " ".join(x for x in [", ".join(f.districts), f.region or "", f.city or ""] if x)
    if where:
        parts.append(f"in {where}")
    return " ".join(parts)


@dataclass
class Turn:
    """What the bot retrieved for one message: used for the prompt, the sources footer and the debug panel."""
    question: str
    filters: Filters | None
    is_listing: bool
    chunks: list[dict]
    listings: ListingResult | None


class Bot:
    def __init__(self, index: Index | None = None):
        self.index = index or Index()
        self.meta = self.index.meta
        self.cache: OrderedDict[str, str] = OrderedDict()

    # ---------- retrieval ----------
    def previous_filters(self, history: list[dict]) -> Filters | None:
        """Replay earlier user messages so follow-ups ('what about Jeddah?') inherit the last listing filters."""
        prev = None
        for m in history:
            if m.get("role") != "user" or not isinstance(m.get("content"), str):
                continue
            f = merge_follow_up(self._parse(m["content"]), prev, m["content"])
            if listing_intent(m["content"], f, self.index.project_names) or (prev and not f.is_empty()):
                prev = f
        return prev

    def _parse(self, text: str) -> Filters:
        return parse(text, self.index.known_districts, self.index.known_regions)

    def retrieve(self, question: str, history: list[dict]) -> Turn:
        f = self._parse(question)
        prev = self.previous_filters(history)
        merged = merge_follow_up(f, prev, question)
        is_listing = listing_intent(question, merged, self.index.project_names) or (
            prev is not None and merged is not f and not f.is_empty())
        search_q = question
        if is_listing and merged is not f:  # follow-up: search with the merged filters, not the old question
            search_q = filters_to_query(merged) + " " + question
        qvec = self.index.embed_query(search_q)
        prefer = "wasalt" if ("wasalt" in question.lower() and "darglobal" not in question.lower()) else None
        chunks = self.index.search_chunks(search_q, k=4 if is_listing else 6, qvec=qvec, prefer_source=prefer)
        if is_listing:
            chunks = [c for c in chunks if c["source"] == "wasalt"][:3] or chunks[:2]
        listings = self.index.search_listings(search_q, merged, k=6, qvec=qvec) if is_listing else None
        return Turn(question, merged if is_listing else None, is_listing, chunks, listings)

    # ---------- prompt ----------
    def system_prompt(self) -> str:
        m = self.meta
        return (
            "You are the DarGlobal & Wasalt Property Assistant, a demo chatbot that answers questions using public "
            f"data scraped from darglobal.co.uk and wasalt.sa between {m.get('scraped_from')} and {m.get('scraped_to')}.\n"
            "Rules:\n"
            "1. Answer ONLY from the CONTEXT below. If the context does not contain the answer, say you don't have that "
            "information and suggest checking darglobal.co.uk or wasalt.sa. Never invent projects, prices, numbers or URLs.\n"
            "2. Cite sources inline with their tags exactly as given, e.g. [1] or [L2]. Do not write URLs yourself.\n"
            "3. For listings, give a short bullet list of at most 5: type, district/city, bedrooms, size, price, and the tag. Mention "
            "that prices and availability change and the live Wasalt page has the current details. End listing answers "
            "with 'Source: Wasalt.sa'.\n"
            "4. Use the LISTING STATS block for questions about typical, average or price ranges, and say they come from "
            "a sample of listings, not the whole market.\n"
            "5. Do not give investment, legal, tax or financial advice and never promise returns. You may report what "
            "DarGlobal states, e.g. 'According to DarGlobal...'.\n"
            "6. Never share phone numbers or personal contact details; point people to the official websites.\n"
            "7. If the question has nothing to do with real estate, DarGlobal or Wasalt, politely say what you can help with.\n"
            "8. Reply in English, in clear Markdown, concise (normally under 200 words)."
        )

    def context_block(self, t: Turn) -> str:
        parts = []
        for i, c in enumerate(t.chunks, 1):
            date = f", {c['date']}" if c.get("date") else ""
            parts.append(f"[{i}] {c['site']} {c['section']}: {c['title']}{date}\n{c['text']}")
        if t.listings is not None:
            r = t.listings
            if r.total == 0:
                parts.append("LISTING SEARCH: no Wasalt listings in the scraped sample match these filters "
                             f"({t.filters.describe()}).")
            else:
                s = r.stats
                lines = [f"LISTING STATS: {r.total} matching Wasalt listings in the scraped sample "
                         f"(filters: {t.filters.describe()})."]
                if r.relaxed:
                    lines.append(f"No exact match, so these filters were relaxed: {', '.join(r.relaxed)}. Tell the user.")
                if s.get("median") is not None:
                    lines.append(f"{s['price_label']}: median {fmt_sar(s['median'])}, typical range "
                                 f"{fmt_sar(s['min'])} to {fmt_sar(s['max'])} ({s['range_kind']}, based on "
                                 f"{s['n_priced']} listings with a price).")
                if s.get("median_area"):
                    lines.append(f"Median size: {fmt_num(s['median_area'])} sqm.")
                if s.get("top_districts"):
                    lines.append("Most listings in: " + ", ".join(f"{k} ({v})" for k, v in s["top_districts"].items()))
                parts.append("\n".join(lines))
                for j, row in enumerate(r.rows, 1):
                    parts.append(f"[L{j}] Wasalt listing: {row['doc']}")
        return "\n\n".join(parts) if parts else "(no relevant context found)"

    def messages(self, question: str, history: list[dict], t: Turn) -> list[dict]:
        msgs = [{"role": "system", "content": self.system_prompt()}]
        for m in history[-4:]:  # last two exchanges, trimmed, for follow-up questions
            if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
                content = m["content"].split("\n\n**Sources**")[0]
                msgs.append({"role": m["role"], "content": content[:1500]})
        msgs.append({"role": "user", "content": f"CONTEXT:\n{self.context_block(t)}\n\nQUESTION: {question}"})
        return msgs

    # ---------- output ----------
    @staticmethod
    def sources_footer(answer: str, t: Turn) -> str:
        """Real links for the tags the model cited (or the top sources if it cited none). Built in code, not by the LLM."""
        cited = set(re.findall(r"\[(L?\d+)\]", answer))
        items = []
        for i, c in enumerate(t.chunks, 1):
            if str(i) in cited:
                items.append(f"[{i}] [{c['title'] or c['url']}]({c['url']}) · {c['site']}")
        if t.listings is not None:
            for j, row in enumerate(t.listings.rows, 1):
                if f"L{j}" in cited:
                    items.append(f"[L{j}] [{row['title']}]({row['url']}) · Wasalt")
        if not items:  # model cited nothing: show what it was given
            items = [f"[{i}] [{c['title'] or c['url']}]({c['url']}) · {c['site']}" for i, c in enumerate(t.chunks[:3], 1)]
        return "\n\n**Sources**\n" + "\n".join(f"- {x}" for x in items)

    def fallback_answer(self, t: Turn, reason: str) -> str:
        """Answer without the LLM: show what retrieval found, so the user still gets something useful."""
        out = [f"_The free AI model is unavailable right now ({reason}). Here is what I found in the data:_\n"]
        if t.listings is not None and t.listings.rows:
            r = t.listings
            if r.relaxed:
                out.append(f"No exact match; relaxed: {', '.join(r.relaxed)}.")
            if r.stats.get("median") is not None:
                out.append(f"{r.total} matching listings; {r.stats['price_label']} median {fmt_sar(r.stats['median'])}.\n")
            for j, row in enumerate(r.rows, 1):
                beds = f"{fmt_num(row['bedrooms'])} bed, " if is_num(row.get("bedrooms")) else ""
                size = f"{fmt_num(row['area_sqm'])} sqm, " if is_num(row.get("area_sqm")) else ""
                where = ", ".join(x for x in [text_or_none(row.get("district")), text_or_none(row.get("city"))] if x)
                out.append(f"- [L{j}] {text_or_none(row.get('property_type')) or 'Property'} in {where}: {beds}{size}"
                           f"{listing_price_text(row)}")
            out.append("\nSource: Wasalt.sa (prices change; check the live listing).")
        for i, c in enumerate(t.chunks[:3], 1):
            snippet = c["text"][:280].rsplit(" ", 1)[0]
            out.append(f"- [{i}] **{c['title']}**: {snippet}...")
        answer = "\n".join(out)
        tags = " ".join(f"[{i}]" for i in range(1, min(3, len(t.chunks)) + 1))
        if t.listings is not None:
            tags += " " + " ".join(f"[L{j}]" for j in range(1, len(t.listings.rows) + 1))
        return answer + self.sources_footer(tags, t)

    # ---------- entry point ----------
    def answer(self, question: str, history: list[dict] | None = None) -> Iterator[str]:
        """Yield the growing answer text (for streaming UIs)."""
        history = history or []
        q = (question or "").strip()
        if not q:
            yield "Please type a question."
            return
        if ARABIC.search(q):
            yield ("Sorry, this demo currently supports **English only** (Arabic support is planned). "
                   "Please ask your question in English.\n\n" + CAPABILITIES)
            return
        if GREETING.match(q):
            yield "Hello! I'm the DarGlobal & Wasalt Property Assistant. " + CAPABILITIES
            return

        t = self.retrieve(q, history)
        cache_key = re.sub(r"\W+", " ", q.lower()).strip()
        if not history and cache_key in self.cache:
            yield self.cache[cache_key]
            return

        text = ""
        try:
            for piece in stream_chat(self.messages(q, history, t)):
                text += piece
                yield text
        except LLMError as e:
            reason = "rate limit reached" if e.status == 429 else (
                "not configured" if e.status == 401 else "temporary error")
            print(f"LLM error: {e}", flush=True)
            if text:  # partial answer streamed before the error: keep it and add sources
                yield text + self.sources_footer(text, t)
            else:
                yield self.fallback_answer(t, reason)
            return
        final = text + self.sources_footer(text, t)
        yield final
        if not history:
            self.cache[cache_key] = final
            while len(self.cache) > 200:
                self.cache.popitem(last=False)
