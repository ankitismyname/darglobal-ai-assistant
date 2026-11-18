"""Shared helpers for the scrapers: polite cached fetching, Next.js data extraction, text cleanup."""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import pathlib
import random
import re
import time

try:  # this Mac's network needs the OS trust store for HTTPS; harmless elsewhere
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache"
RAW_DIR = ROOT / "data" / "raw"
USER_AGENT = "Mozilla/5.0 (compatible; RealEstateQA-DemoBot/0.1; public pages only; low request rate)"


class Fetcher:
    """GET with a minimum delay between network requests, retries with backoff, and an on-disk cache.

    Only successful (200) responses are cached, so re-running a scraper never re-fetches a page it already has.
    """

    def __init__(self, delay: float = 1.2, timeout: int = 40):
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en"})
        self._last = 0.0
        self.network_hits = 0
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, url: str) -> pathlib.Path:
        return CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".html")

    def get(self, url: str) -> tuple[int, str]:
        path = self._cache_path(url)
        if path.exists():
            return 200, path.read_text(encoding="utf-8", errors="ignore")
        status, text = 0, ""
        for attempt in range(4):
            wait = self.delay + random.uniform(0, 0.5) - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            self.network_hits += 1
            try:
                r = self.session.get(url, timeout=self.timeout)
                status, text = r.status_code, r.text
            except requests.RequestException as e:
                status, text = 0, str(e)
            if status == 200:
                path.write_text(text, encoding="utf-8")
                return status, text
            if status in (404, 410, 403):
                return status, text
            time.sleep(2 ** attempt * 2)  # 429 / 5xx / network error: back off and retry
        return status, text


def next_data(html: str) -> dict | None:
    """Return the parsed __NEXT_DATA__ JSON of a Next.js page, or None."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def html_to_text(fragment: str) -> str:
    """Strip HTML tags to readable text, keeping paragraph breaks."""
    if not fragment:
        return ""
    if "<" not in fragment:
        return clean_ws(fragment)
    soup = BeautifulSoup(fragment, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for tag in soup.find_all(BLOCK_TAGS):  # line breaks only after block elements, so inline links stay in the sentence
        tag.append("\n")
    for li in soup.find_all("li"):
        li.insert(0, "- ")
    text = soup.get_text("")
    lines = [clean_ws(x) for x in text.split("\n")]
    return "\n".join(x for x in lines if x)


BLOCK_TAGS = ["p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "blockquote", "section", "article", "ul", "ol"]


def is_rich_blocks(obj) -> bool:
    """Strapi v4 'blocks' rich text: a list of {type, children} nodes."""
    return isinstance(obj, list) and bool(obj) and all(isinstance(x, dict) and "type" in x and "children" in x for x in obj)


def blocks_to_text(blocks) -> str:
    """Render Strapi rich-text blocks (paragraph, heading, list, quote) to plain text."""
    out: list[str] = []

    def inline(nodes) -> str:
        parts = []
        for n in nodes or []:
            if "text" in n:
                parts.append(n["text"])
            elif n.get("children"):
                parts.append(inline(n["children"]))
        return clean_ws("".join(parts))

    def block(b, depth=0):
        t = b.get("type")
        if t == "list":
            for item in b.get("children") or []:
                if item.get("type") == "list":
                    block(item, depth + 1)
                else:
                    s = inline(item.get("children"))
                    if s:
                        out.append("  " * depth + "- " + s)
        else:
            s = inline(b.get("children"))
            if s:
                out.append(s)

    for b in blocks:
        block(b)
    return "\n".join(out)


def clean_ws(s: str) -> str:
    s = s.replace(" ", " ").replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"[ \t\r\f\v]+", " ", s).strip()


def page_meta(html: str) -> dict:
    """<title> and meta description of an HTML page."""
    soup = BeautifulSoup(html[:200_000], "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    desc = soup.find("meta", attrs={"name": "description"})
    return {"title": clean_ws(title), "description": clean_ws(desc.get("content", "")) if desc else ""}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def write_jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def sitemap_urls(xml: str) -> list[str]:
    # Some sitemaps double-escape entities (e.g. "&amp;apos;"), so unescape until stable
    out = []
    for u in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml):
        prev = None
        while prev != u:
            prev, u = u, html.unescape(u)
        out.append(clean_ws(u))
    return out
