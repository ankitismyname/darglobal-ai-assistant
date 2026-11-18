"""Build the search index from data/raw/*.jsonl into data/index/.

  chunks.jsonl + chunk_emb.npy        knowledge chunks (DarGlobal pages/projects, Wasalt area guides) + embeddings
  listings.parquet + listing_emb.npy  Wasalt listings (normalised, one text 'doc' per listing) + embeddings
  meta.json                           counts and scrape dates shown in the UI and README

Runs on a laptop or inside `docker build`; it needs only the raw JSONL files and the embedding model.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import time

import numpy as np
import pandas as pd

from config import EMBED_MODEL, INDEX_DIR, MODEL_DIR, RAW_DIR
from normalize import listing_doc, norm_city

MAX_WORDS, OVERLAP = 220, 40


def read_jsonl(name: str) -> list[dict]:
    path = RAW_DIR / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def chunk_text(text: str, max_words: int = MAX_WORDS, overlap: int = OVERLAP) -> list[str]:
    """Pack paragraphs into ~max_words chunks; split very long paragraphs by sentence; carry a small overlap."""
    units: list[str] = []
    for para in [p.strip() for p in text.split("\n") if p.strip()]:
        if len(para.split()) <= max_words:
            units.append(para)
        else:
            units.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip())
    chunks, cur = [], []
    for u in units:
        if cur and len(" ".join(cur).split()) + len(u.split()) > max_words:
            chunks.append("\n".join(cur))
            tail = " ".join(cur).split()[-overlap:]
            cur = [" ".join(tail)] if overlap else []
        cur.append(u)
    if cur:
        chunks.append("\n".join(cur))
    return [c for c in chunks if len(c.split()) >= 8]


INDEX_PAGES = re.compile(r"darglobal\.co\.uk/(blog|press|insights)$|darglobal\.co\.uk/projects/.+")
COUNTRY_RULES = [
    ("United Arab Emirates", r"dubai|uae|emirates|ras al khaimah|\brak\b|marjan"),
    ("Oman", r"oman|muscat|aida|sohar"),
    ("Saudi Arabia", r"saudi|ksa|jeddah|riyadh|makkah|madinah"),
    ("Qatar", r"qatar|doha"),
    ("Spain", r"spain|marbella|cortes[ií]n|benahav[ií]s|estepona"),
    ("United Kingdom", r"london|united kingdom|\buk\b"),
]


def country_of(location: str) -> str:
    for country, rx in COUNTRY_RULES:
        if re.search(rx, location or "", re.I):
            return country
    return "Other / worldwide"


def portfolio_pages() -> list[dict]:
    """Synthetic overview pages built from the structured project data, so list-style questions
    ('Which DarGlobal projects are in Oman?') retrieve one complete answer instead of scattered blog posts."""
    projects = read_jsonl("darglobal_projects.jsonl")
    by_country: dict[str, list[dict]] = {}
    for p in projects:
        if p["name"].lower().startswith(("buy property", "invest in")):
            continue
        by_country.setdefault(country_of(p["location"]), []).append(p)
    pages, overview = [], []
    for country, items in sorted(by_country.items()):
        lines = []
        for p in sorted(items, key=lambda x: x["name"]):
            kind = p["facts"].get("Property Type") or ""
            units = p["facts"].get("Unit type") or p["facts"].get("Unit Type") or ""
            status = p["facts"].get("Status") or ""
            extra = "; ".join(x for x in [kind, units, status] if x)
            lines.append(f"- {p['name']} ({p['location']}){': ' + extra if extra else ''}. Page: {p['url']}")
        overview.append(f"{country}: " + ", ".join(sorted(p["name"] for p in items)))
        pages.append({"source": "darglobal", "url": "https://darglobal.co.uk/projects", "section": "project",
                      "title": f"DarGlobal projects in {country}", "date": "", "description": "",
                      "text": f"DarGlobal projects in {country} (from darglobal.co.uk project pages):\n" + "\n".join(lines)})
    if overview:
        pages.append({"source": "darglobal", "url": "https://darglobal.co.uk/projects", "section": "project",
                      "title": "DarGlobal project portfolio by country", "date": "", "description": "",
                      "text": "DarGlobal's projects listed on darglobal.co.uk, by country (several are branded "
                              "partnerships, e.g. Trump, Missoni, Pagani, Aston Martin, Mouawad, Marriott, W, "
                              "Mulliner/Bentley):\n" + "\n".join(overview)})
    return pages


def title_from_url(url: str) -> str:
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"[-_]+", " ", slug).strip().capitalize()


def build_chunks() -> list[dict]:
    pages = portfolio_pages() + read_jsonl("darglobal_pages.jsonl") + read_jsonl("wasalt_pages.jsonl")
    chunks, seen_text = [], set()
    for p in pages:
        p["title"] = (p.get("title") or "").strip() or title_from_url(p["url"])
        # Listing/index pages (blog index, project filter pages) only repeat content that has its own pages
        if INDEX_PAGES.search(p["url"]):
            continue
        fingerprint = hash(re.sub(r"\W+", "", p["text"].lower())[:5000])
        if fingerprint in seen_text:
            continue
        seen_text.add(fingerprint)
        site = "DarGlobal" if p["source"] == "darglobal" else "Wasalt"
        body = p["text"]
        if p.get("description") and p["description"] not in body:
            body = p["description"] + "\n" + body
        # Project pages are short and self-contained: keep them whole so all facts stay together
        parts = [body] if p["section"] == "project" and len(body.split()) < 450 else chunk_text(body)
        for i, part in enumerate(parts):
            chunks.append({
                "id": f"{p['source']}:{p['url']}#{i}",
                "source": p["source"],
                "site": site,
                "section": p["section"],
                "title": p["title"],
                "url": p["url"],
                "date": p.get("date") or "",
                "text": part,
            })
    return chunks


def build_listings() -> pd.DataFrame:
    rows = read_jsonl("wasalt_listings.jsonl")
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["city"] = df["city"].map(norm_city)
    df["property_type_key"] = df["property_type"].fillna("").str.lower().str.strip()
    df["district_key"] = df["district"].fillna("").str.lower().str.strip()
    df["region_key"] = df["region"].fillna("").str.lower().str.strip()
    df["amenities"] = df["amenities"].map(lambda a: list(a) if isinstance(a, (list, np.ndarray)) else [])
    df["doc"] = [listing_doc(r) for r in df.to_dict("records")]
    return df.reset_index(drop=True)


def embed(texts: list[str]) -> np.ndarray:
    from fastembed import TextEmbedding

    model = TextEmbedding(EMBED_MODEL, cache_dir=str(MODEL_DIR))
    vecs = np.array(list(model.embed(texts, batch_size=64)), dtype=np.float32)
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
    return vecs


def main() -> None:
    t0 = time.time()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    chunks = build_chunks()
    listings = build_listings()
    print(f"{len(chunks)} knowledge chunks, {len(listings)} listings", flush=True)

    chunk_emb = embed([f"{c['title']}\n{c['text']}" for c in chunks])
    listing_emb = embed(listings["doc"].tolist()) if len(listings) else np.zeros((0, 384), np.float32)

    with (INDEX_DIR / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    np.save(INDEX_DIR / "chunk_emb.npy", chunk_emb)
    listings.to_parquet(INDEX_DIR / "listings.parquet", index=False)
    np.save(INDEX_DIR / "listing_emb.npy", listing_emb)

    scraped = [r.get("scraped_at", "")[:10] for r in read_jsonl("darglobal_pages.jsonl") + read_jsonl("wasalt_pages.jsonl")]
    scraped += listings["scraped_at"].str[:10].tolist() if len(listings) else []
    scraped = sorted(s for s in scraped if s)
    sections: dict[str, int] = {}
    for c in chunks:
        sections[f"{c['site']}/{c['section']}"] = sections.get(f"{c['site']}/{c['section']}", 0) + 1
    meta = {
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "embed_model": EMBED_MODEL,
        "scraped_from": scraped[0] if scraped else "",
        "scraped_to": scraped[-1] if scraped else "",
        "n_chunks": len(chunks),
        "chunks_by_section": sections,
        "n_darglobal_pages": len(read_jsonl("darglobal_pages.jsonl")),
        "n_darglobal_projects": len(read_jsonl("darglobal_projects.jsonl")),
        "project_names": sorted({p["name"] for p in read_jsonl("darglobal_projects.jsonl") if p.get("name")}),
        "n_wasalt_pages": len(read_jsonl("wasalt_pages.jsonl")),
        "n_listings": int(len(listings)),
        "listings_by_city": listings["city"].value_counts().to_dict() if len(listings) else {},
        "listings_by_purpose": listings["purpose"].value_counts().to_dict() if len(listings) else {},
        "listings_by_type": listings["property_type"].value_counts().to_dict() if len(listings) else {},
    }
    (INDEX_DIR / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"index built in {time.time() - t0:.0f}s -> {INDEX_DIR}")


if __name__ == "__main__":
    main()
