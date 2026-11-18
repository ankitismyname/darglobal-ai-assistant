"""Scrape public English listing data from wasalt.sa, following https://wasalt.sa/llms.txt.

Source: public category pages listed in Wasalt's category sitemap, e.g. /en/apartments-for-rent-in-north-riyadh-al-nakheel.
Each server-rendered page holds up to 32 listings as structured JSON in __NEXT_DATA__.props.pageProps.searchResult,
plus (city/region pages) an SEO area guide and FAQ. Paging is client-side via /search (disallowed by robots.txt), so
coverage comes from sampling many district pages. The listing URLs in the product sitemap are mostly stale (404).

Rules kept:
  * robots.txt: never touch /search; low request rate with an honest bot User-Agent
  * llms.txt: public listing content only; NO phone/WhatsApp numbers, owner or agent contact details are stored
    (fields are copied from an explicit whitelist); answers must cite "Source: Wasalt.sa" and link the live page
  * blog.wasalt.sa answers 403 to scripts, so it is skipped

Output:
  data/raw/wasalt_listings.jsonl   one row per listing (deduplicated by id)
  data/raw/wasalt_pages.jsonl      area guides + FAQs from category pages, and the corporate page
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.robotparser

from bs4 import BeautifulSoup

from common import RAW_DIR, Fetcher, clean_ws, html_to_text, next_data, now_iso, sitemap_urls, write_jsonl

BASE = "https://wasalt.sa"
CITIES = ["riyadh", "jeddah", "dammam", "al-khobar", "makkah", "madinah"]
TYPES = (r"apartments|villas|floors|lands|commercial-properties|furnished-apartments|offices|showrooms|warehouses|"
         r"duplexes|[1-5]-bedroom-apartments")
# /en/<type>-for-<sale|rent>-in-[<north|south|east|west|central>-]<city>[-<district>]
CATEGORY = re.compile(
    rf"^/en/(?P<type>{TYPES})-for-(?P<purpose>sale|rent)-in-(?P<region>(?:north|south|east|west|central)-)?"
    rf"(?P<city>{'|'.join(CITIES)})(?P<district>-[a-z0-9-]+)?$"
)


def pick_categories(paths: list[str], per_group: int, seed: int = 7) -> list[str]:
    """All city- and region-level pages, plus a seeded sample of district pages per (city, type, purpose).

    Category pages only render their first 32 results server-side (paging goes through /search, which robots.txt
    disallows), so coverage comes from many narrow district pages instead of deep paging.
    """
    import random

    top, groups = [], {}
    for p in paths:
        m = CATEGORY.match(p)
        if not m:
            continue
        if not m.group("district"):
            top.append(p)
        else:
            groups.setdefault((m.group("city"), m.group("type"), m.group("purpose")), []).append(p)
    rng = random.Random(seed)
    sample = []
    for key in sorted(groups):
        items = sorted(groups[key])
        sample += rng.sample(items, min(per_group, len(items)))
    return sorted(top) + sorted(sample)
ATTR_KEEP = {"noOfBedrooms", "noOfBathrooms", "noOfLivingrooms", "noOfGuestrooms", "builtUpArea", "carpetArea",
             "plotArea", "completionYear", "furnishingType", "floorNumber", "noOfFloors"}


def num(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def parse_listing(p: dict, category: str) -> dict | None:
    """Copy only whitelisted, non-personal fields from one search-result item."""
    pi = p.get("propertyInfo") or {}
    if not pi.get("slug") or not pi.get("propertyFor"):
        return None
    attrs = {a["key"]: a.get("value") for a in p.get("attributes") or []
             if isinstance(a, dict) and a.get("key") in ATTR_KEEP and a.get("value") not in (None, "")}
    rent = pi.get("rentFreq") or {}
    rent_year = num((rent.get("yearly") or {}).get("amount"))
    rent_month = num((rent.get("monthly") or {}).get("amount"))
    if pi.get("propertyFor") == "rent" and rent_year is None and rent_month is None:
        amount = num(pi.get("expectedRent"))
        if amount is not None:
            if "month" in str(pi.get("expectedRentType", "")).lower():
                rent_month = amount
            else:
                rent_year = amount
    amenities: list[str] = []
    for a in p.get("featureAmenities") or []:
        items = a if isinstance(a, list) else [a]
        for x in items:
            name = x.get("name") if isinstance(x, dict) else None
            if isinstance(name, dict):
                name = name.get("en")
            if isinstance(name, str) and name.strip():
                amenities.append(clean_ws(name))
    facing = None
    for s in p.get("streetInfo") or []:
        facing = ((s or {}).get("en") or {}).get("facing") or facing
    area = num(attrs.get("builtUpArea")) or num(p.get("floorSize")) or num(attrs.get("plotArea")) \
        or num(attrs.get("carpetArea"))
    return {
        "id": str(p.get("id")),
        "url": f"{BASE}/en/property/{pi['propertyFor']}/{pi['slug']}",
        "title": clean_ws(pi.get("title") or ""),
        "purpose": pi.get("propertyFor"),  # sale | rent
        "main_type": pi.get("propertyMainType"),  # Residential | Commercial
        "property_type": pi.get("propertySubType"),  # Apartment, Villa, Floor, Land ...
        "city": pi.get("city"),
        "region": pi.get("territory"),  # e.g. North Riyadh
        "district": pi.get("district") or pi.get("zone"),
        "address": clean_ws(pi.get("address") or ""),
        "price_sar": num(pi.get("salePrice")) if pi.get("propertyFor") == "sale" else None,
        "rent_year_sar": rent_year,
        "rent_month_sar": rent_month,
        "bedrooms": num(attrs.get("noOfBedrooms")),
        "bathrooms": num(attrs.get("noOfBathrooms")),
        "living_rooms": num(attrs.get("noOfLivingrooms")),
        "area_sqm": area,
        "completion": str(attrs.get("completionYear")) if attrs.get("completionYear") is not None else None,
        "furnishing": attrs.get("furnishingType"),
        "amenities": sorted(set(amenities)),
        "facing": facing,
        "verified": str(p.get("isVerified")).lower() == "true",
        "rega_licensed": str(p.get("isRegaProp")).lower() == "true",
        "published_at": (p.get("publishedAt") or "")[:10],
        "updated_at": (p.get("updatedAt") or "")[:10],
        "category": category,
        "source": "wasalt",
    }


def category_page_doc(url: str, pp: dict) -> dict | None:
    """The area guide + FAQ block that Wasalt shows under each category page."""
    meta = pp.get("metaData") or {}
    title = clean_ws(meta.get("h1tag") or meta.get("title_tag") or "")
    parts = []
    if isinstance(pp.get("para"), str):
        parts.append(html_to_text(pp["para"]))
    faq = pp.get("FAQSchema") or {}
    for q in faq.get("mainEntity") or []:
        question = clean_ws(q.get("name") or "")
        answer = html_to_text((q.get("acceptedAnswer") or {}).get("text") or "")
        if question and answer:
            parts.append(f"Q: {question}\nA: {answer}")
    text = "\n".join(x for x in parts if x)
    if len(text) < 100:
        return None
    sr = pp.get("searchResult") or {}
    if sr.get("count"):
        text = f"Wasalt had {sr['count']:,} live listings in this category on the scrape date.\n" + text
    return {"source": "wasalt", "url": url, "section": "area-guide", "title": title, "date": "",
            "description": clean_ws(meta.get("meta_description") or ""), "text": text, "scraped_at": now_iso()}


def visible_text_doc(url: str, html: str, section: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "svg"]):
        tag.decompose()
    root = soup.find("main") or soup.body
    text = html_to_text(str(root)) if root else ""
    lines, seen = [], set()
    for line in text.split("\n"):
        if len(line.split()) >= 3 and line not in seen:
            seen.add(line)
            lines.append(line)
    if not lines:
        return None
    title = clean_ws(soup.title.get_text()) if soup.title else url
    return {"source": "wasalt", "url": url, "section": section, "title": title, "date": "", "description": "",
            "text": "\n".join(lines), "scraped_at": now_iso()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=5,
                    help="district pages sampled per (city, type, sale/rent) group; each page has up to 32 listings")
    ap.add_argument("--limit", type=int, default=0, help="only the first N categories (testing)")
    args = ap.parse_args()

    f = Fetcher(delay=1.2)
    robots = urllib.robotparser.RobotFileParser()
    robots.parse(f.get(f"{BASE}/robots.txt")[1].splitlines())

    _, xml = f.get("https://cdn.wasalt.sa/sitemap/category_sitemap_en_sa.xml.gz")
    cats = pick_categories(sorted({u.replace(BASE, "") for u in sitemap_urls(xml)}), args.per_group)
    if args.limit:
        cats = cats[: args.limit]
    print(f"{len(cats)} Wasalt category pages", flush=True)

    listings: dict[str, dict] = {}
    pages: list[dict] = []
    failed = []
    scraped_at = now_iso()
    for ci, cat in enumerate(cats, 1):
        url = f"{BASE}{cat}"  # includes some price-bucket pages ("...-for-sar-500k"); several hold real listings
        if not robots.can_fetch("*", url):
            failed.append((url, "robots"))
            continue
        status, html = f.get(url)
        nd = next_data(html) if status == 200 else None
        pp = (nd or {}).get("props", {}).get("pageProps", {}) or {}
        sr = pp.get("searchResult") or {}
        if not sr.get("properties"):
            failed.append((url, status if status != 200 else "no results"))
            continue
        if not CATEGORY.match(cat).group("district"):  # district pages repeat the city guide; keep city/region ones
            doc = category_page_doc(url, pp)
            if doc:
                pages.append(doc)
        for item in sr["properties"]:
            for p in item if isinstance(item, list) else [item]:  # some results are grouped carousels
                rec = parse_listing(p, cat.split("/")[-1]) if isinstance(p, dict) else None
                if rec and rec["id"] not in listings:
                    rec["scraped_at"] = scraped_at
                    listings[rec["id"]] = rec
        if ci % 20 == 0 or ci == len(cats):
            print(f"  {ci}/{len(cats)} pages: {len(listings)} listings so far ({f.network_hits} requests)", flush=True)

    status, html = f.get(f"{BASE}/en/corporate")
    if status == 200:
        doc = visible_text_doc(f"{BASE}/en/corporate", html, "company")
        if doc:
            pages.append(doc)

    # Wasalt's own public description of itself (llms.txt "Description" section)
    status, txt = f.get(f"{BASE}/llms.txt")
    m = re.search(r"# Description\s*\n(.+?)(?:\n\s*\n|\n#)", txt, re.S) if status == 200 else None
    if m:
        pages.append({"source": "wasalt", "url": f"{BASE}/llms.txt", "section": "company",
                      "title": "About Wasalt (wasalt.sa)", "date": "", "description": "",
                      "text": "Wasalt (wasalt.sa): " + clean_ws(m.group(1).replace("\n", " ")),
                      "scraped_at": now_iso()})

    rows = list(listings.values())
    write_jsonl(RAW_DIR / "wasalt_listings.jsonl", rows)
    write_jsonl(RAW_DIR / "wasalt_pages.jsonl", pages)
    print(f"saved {len(rows)} listings, {len(pages)} pages; {len(failed)} pages failed/empty")
    for u, s in failed[:20]:
        print("   ", s, u)


if __name__ == "__main__":
    sys.exit(main())
