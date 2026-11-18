"""Search over the prebuilt index.

Knowledge chunks: hybrid retrieval = dense (bge-small cosine) + keyword (BM25), merged with reciprocal-rank fusion.
Listings: exact structured filters first (purpose, type, city, district, beds, price, area), then semantic ranking
of the matches; if nothing matches, filters are relaxed step by step and the answer says so.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

from config import EMBED_MODEL, INDEX_DIR, MODEL_DIR
from normalize import CITY_ALIASES
from query_parser import Filters

TOKEN = re.compile(r"[a-z0-9]+")
STOP = set("the a an and or of to in on for with is are was were be by at as from this that it its what which who how "
           "does do did can i you me my your our we about tell please give show list there their".split())


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP]


# Abbreviations people type vs. words the pages use (keyword search only)
SYNONYMS = {
    "ceo": "chief executive officer founder", "founder": "founder chief executive officer",
    "chairman": "chairman board", "cfo": "chief financial officer",
    "lse": "london stock exchange listed", "ipo": "listing london stock exchange",
    "listed": "listed listing stock exchange", "flat": "apartment", "flats": "apartments",
}
# Curated pages (projects, company pages) answer most questions better than the many SEO blog posts
SECTION_WEIGHT = {"project": 1.35, "page": 1.15, "company": 1.4, "press": 1.0, "insights": 1.0,
                  "area-guide": 1.0, "blog": 0.85}


def expand(q: str) -> str:
    extra = [SYNONYMS[t] for t in TOKEN.findall(q.lower()) if t in SYNONYMS]
    return q + (" " + " ".join(extra) if extra else "")


@dataclass
class ListingResult:
    rows: list[dict]
    total: int
    stats: dict
    relaxed: list[str] = field(default_factory=list)
    filters: Filters | None = None


class Index:
    def __init__(self, index_dir=INDEX_DIR):
        from fastembed import TextEmbedding

        self.chunks = [json.loads(line) for line in (index_dir / "chunks.jsonl").open(encoding="utf-8")]
        self.chunk_emb = np.load(index_dir / "chunk_emb.npy")
        self.listings = pd.read_parquet(index_dir / "listings.parquet")
        self.listing_emb = np.load(index_dir / "listing_emb.npy")
        self.meta = json.loads((index_dir / "meta.json").read_text())
        self.model = TextEmbedding(EMBED_MODEL, cache_dir=str(MODEL_DIR))
        self.bm25 = BM25Okapi([tokenize(f"{c['title']} {c['text']}") for c in self.chunks])
        self.section_weight = np.array([SECTION_WEIGHT.get(c["section"], 1.0) for c in self.chunks])
        self.chunk_source = np.array([c["source"] for c in self.chunks])
        df = self.listings
        city_names = {c.lower() for c in df["city"].dropna().unique()} | set(CITY_ALIASES)
        # a few districts share a city's name ("Al Khobar"); matching them would wrongly narrow city-wide searches
        self.known_districts = {d for d in df["district_key"].dropna().unique() if d and d not in city_names}
        self.known_regions = {r for r in df["region_key"].dropna().unique() if r}
        self.project_names = {n.lower() for n in self.meta.get("project_names", []) if len(n) >= 4}

    # ---------- knowledge ----------
    def embed_query(self, q: str) -> np.ndarray:
        v = np.array(list(self.model.query_embed([q]))[0], dtype=np.float32)
        return v / (np.linalg.norm(v) + 1e-9)

    def search_chunks(self, q: str, k: int = 6, qvec: np.ndarray | None = None, per_url: int = 2,
                      prefer_source: str | None = None) -> list[dict]:
        qvec = self.embed_query(q) if qvec is None else qvec
        dense = self.chunk_emb @ qvec
        sparse = self.bm25.get_scores(tokenize(expand(q)))
        rrf = np.zeros(len(self.chunks))
        for scores in (dense, sparse):
            order = np.argsort(-scores)[:100]
            rrf[order] += 1.0 / (60 + np.arange(1, len(order) + 1))
        rrf *= self.section_weight
        if prefer_source:
            rrf *= np.where(self.chunk_source == prefer_source, 1.5, 1.0)
        out, seen = [], {}
        for i in np.argsort(-rrf):
            c = self.chunks[i]
            if seen.get(c["url"], 0) >= per_url:
                continue
            seen[c["url"]] = seen.get(c["url"], 0) + 1
            out.append({**c, "score": float(dense[i])})
            if len(out) >= k:
                break
        return out

    # ---------- listings ----------
    def _price_series(self, df: pd.DataFrame, f: Filters) -> pd.Series:
        """Comparable price per row: sale price, or rent per month/year depending on the question."""
        if f.period == "month":
            rent = df["rent_month_sar"].fillna(df["rent_year_sar"] / 12)
        else:
            rent = df["rent_year_sar"].fillna(df["rent_month_sar"] * 12)
        return df["price_sar"].where(df["purpose"] == "sale", rent)

    def _mask(self, f: Filters, skip: set[str]) -> pd.Series:
        df = self.listings
        m = pd.Series(True, index=df.index)
        if f.purpose and "purpose" not in skip:
            m &= df["purpose"] == f.purpose
        if f.types and "types" not in skip:
            tm = pd.Series(False, index=df.index)
            for t in f.types:
                tm |= df["property_type_key"].str.contains(t, regex=False)
            m &= tm
        if f.city and "city" not in skip:
            m &= df["city"] == f.city
        if f.region and "location" not in skip:
            m &= df["region_key"] == f.region
        if f.districts and "location" not in skip:
            m &= df["district_key"].isin(f.districts)
        if "bedrooms" not in skip:
            if f.bedrooms is not None:
                m &= df["bedrooms"] == f.bedrooms
            if f.bedrooms_min is not None:
                m &= df["bedrooms"] >= f.bedrooms_min
        if (f.price_min or f.price_max) and "price" not in skip:
            price = self._price_series(df, f)
            if f.price_min:
                m &= price >= f.price_min
            if f.price_max:
                m &= price <= f.price_max
        if "area" not in skip:
            if f.area_min:
                m &= df["area_sqm"] >= f.area_min
            if f.area_max:
                m &= df["area_sqm"] <= f.area_max
        if f.furnished and "furnished" not in skip:
            m &= df["category"].str.contains("furnished") | df["furnishing"].fillna("").str.contains("urnished")
        return m

    def search_listings(self, q: str, f: Filters, k: int = 6, qvec: np.ndarray | None = None) -> ListingResult:
        df = self.listings
        relax_order = [("location", "district/area"), ("area", "size"), ("furnished", "furnished"),
                       ("price", "price range"), ("bedrooms", "bedrooms")]
        skip: set[str] = set()
        relaxed: list[str] = []
        mask = self._mask(f, skip)
        for key, label in relax_order:
            if mask.any():
                break
            if (key == "location" and (f.districts or f.region)) or (key == "price" and (f.price_min or f.price_max)) \
                    or (key == "bedrooms" and (f.bedrooms is not None or f.bedrooms_min)) \
                    or (key == "area" and (f.area_min or f.area_max)) or (key == "furnished" and f.furnished):
                skip.add(key)
                relaxed.append(label)
                mask = self._mask(f, skip)
        idx = np.flatnonzero(mask.to_numpy())
        if len(idx) == 0:
            return ListingResult([], 0, {}, relaxed, f)

        sub = df.iloc[idx]
        price = self._price_series(sub, f)
        if f.sort == "cheapest":
            order = np.argsort(price.fillna(np.inf).to_numpy(), kind="stable")
        elif f.sort == "priciest":
            order = np.argsort(-price.fillna(-np.inf).to_numpy(), kind="stable")
        elif f.sort == "newest":
            order = np.argsort(sub["published_at"].fillna("").to_numpy())[::-1]
        elif f.sort == "largest":
            order = np.argsort(-sub["area_sqm"].fillna(-1).to_numpy(), kind="stable")
        else:
            qvec = self.embed_query(q) if qvec is None else qvec
            sim = self.listing_emb[idx] @ qvec
            has_price = price.notna().to_numpy().astype(float) * 0.02  # small nudge for listings with a price
            order = np.argsort(-(sim + has_price))
        # Show variety: at most 2 listings per district unless the user asked for specific districts
        picked, per_district = [], {}
        for i in order:
            d = sub["district"].iloc[i]
            if not f.districts and per_district.get(d, 0) >= 2:
                continue
            per_district[d] = per_district.get(d, 0) + 1
            picked.append(i)
            if len(picked) >= k:
                break
        if len(picked) < k:  # not enough districts: fill up in rank order
            picked += [i for i in order if i not in set(picked)][: k - len(picked)]
        top = sub.iloc[picked].to_dict("records")

        stats = {"count": int(len(sub))}
        p = price.dropna()
        p = p[p > 0]
        if len(p):
            label = "price" if (f.purpose == "sale" or (sub["purpose"] == "sale").all()) else (
                "rent per month" if f.period == "month" else "rent per year")
            # owner-entered outliers exist (e.g. a land plot at SAR 1bn), so use the 10th-90th percentile as the
            # "typical range" once there are enough listings
            lo, hi = (p.quantile(0.1), p.quantile(0.9)) if len(p) >= 10 else (p.min(), p.max())
            stats.update({"price_label": label, "median": float(p.median()), "min": float(lo), "max": float(hi),
                          "range_kind": "10th-90th percentile" if len(p) >= 10 else "min-max",
                          "n_priced": int(len(p))})
        a = sub["area_sqm"].dropna()
        if len(a):
            stats["median_area"] = float(a.median())
        if not f.districts and len(sub) >= 5:
            stats["top_districts"] = sub["district"].value_counts().head(5).to_dict()
        return ListingResult(top, int(len(sub)), stats, relaxed, f)
