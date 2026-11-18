"""Scrape public English pages of darglobal.co.uk (projects, company pages, press, insights, blog).

Every page is a Next.js page whose content sits in __NEXT_DATA__.props.pageProps (Strapi CMS), so we read that JSON
instead of the rendered HTML: no navigation/footer noise, and project pages give structured fields.

Output:
  data/raw/darglobal_pages.jsonl     one row per page: url, section, title, date, text
  data/raw/darglobal_projects.jsonl  one row per project page with structured fields
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.robotparser

from common import (RAW_DIR, Fetcher, blocks_to_text, clean_ws, html_to_text, is_rich_blocks, next_data, now_iso,
                    page_meta, sitemap_urls, write_jsonl)

BASE = "https://darglobal.co.uk"

# Pages with no useful knowledge (forms, legal, thank-you, campaigns, careers)
SKIP = re.compile(
    r"thank-you|terms|privacy|careers|internship|become-a|bookYourUnit|pay-online|landing-?page|campaigns|get-in-touch"
    r"|win-a-trip|broker-contest|/success$|new-home-page|-duplicate-\d+$",
    re.I,
)
# Keys inside pageProps that are site chrome, media or cross-links rather than page content
IGNORE_KEYS = {
    "globalData", "socialLinks", "isMobile", "locale", "otherProjectData", "thankyouPageData", "localizations",
    "versions", "OtherProject", "url", "href", "slug", "mime", "ext", "hash", "provider", "formats", "ButtonTheme",
    "iconClass", "alternativeText", "caption", "alt", "createdAt", "updatedAt", "publishedAt", "vuid",
    "versionNumber", "versionComment", "previewUrl", "provider_metadata", "metaImage", "metaSocial", "structuredData",
    "canonicalURL", "metaRobots", "keywords", "metaViewport", "galleryList", "ProgressUpdate", "image", "Image",
    "HeroBanner", "HeroBannerMobile", "desktopThumbnail", "mobileThumbnail", "file", "Link", "lat", "long",
}
PAIR_KEYS = [("positionTitle", "nameTitle"), ("subtitle", "number"),
             ("name", "value"), ("Title", "Duration"), ("question", "answer"), ("Question", "Answer"),
             ("title", "description"), ("label", "value"), ("heading", "description")]


def section_of(url: str) -> str:
    path = url.replace(BASE, "").strip("/")
    first = path.split("/")[0].lower() if path else "home"
    if first in ("blog", "press", "insights"):
        return first
    return "page"


def collect_text(obj, out: list[str], depth: int = 0) -> None:
    """Walk CMS JSON and collect human-readable text in document order."""
    if depth > 12:
        return
    if is_rich_blocks(obj):
        text = blocks_to_text(obj)
        if text:
            out.append(text)
        return
    if isinstance(obj, dict):
        # The CMS embeds a shared privacy/cookie notice in some pages; it is not page content
        if isinstance(obj.get("title"), str) and re.search(r"privacy|cookie", obj["title"], re.I):
            return
        for a, b in PAIR_KEYS:  # name/value style pairs read better joined: "Property Type: Residential Tower"
            vb_raw = obj.get(b)
            if isinstance(obj.get(a), str) and obj[a].strip() and (
                (isinstance(vb_raw, str) and vb_raw.strip()) or is_rich_blocks(vb_raw)
            ):
                va = html_to_text(obj[a])
                vb = blocks_to_text(vb_raw) if is_rich_blocks(vb_raw) else html_to_text(vb_raw)
                if not vb:
                    continue
                if len(vb) < 200 and "\n" not in vb:
                    out.append(f"{va}: {vb}")
                else:
                    out.extend([va, vb])
                rest = {k: v for k, v in obj.items() if k not in (a, b)}
                collect_text(rest, out, depth + 1)
                return
        for k, v in obj.items():
            if k in IGNORE_KEYS:
                continue
            collect_text(v, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            collect_text(v, out, depth + 1)
    elif isinstance(obj, str):
        s = obj.strip()
        if not s or s.startswith(("http", "/", "#")) or re.search(r"\.(jpe?g|png|webp|svg|gif|pdf|mp4|avif)$", s, re.I):
            return
        text = html_to_text(s)
        if len(text.split()) >= 4 or (":" in text and len(text) > 8):
            out.append(text)


def dedupe(lines: list[str]) -> list[str]:
    seen, out = set(), []
    for line in lines:
        key = re.sub(r"\W+", " ", line.lower()).strip()
        if key and key not in seen:
            seen.add(key)
            out.append(line)
    return out


def first_date(obj) -> str:
    """Find a publication date anywhere in the page JSON."""
    found = []

    def walk(o, depth=0):
        if depth > 8 or found:
            return
        if isinstance(o, dict):
            for k in ("date", "Date", "publishDate", "publishedDate", "PublishedDate", "publishedAt"):
                v = o.get(k)
                if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v):
                    found.append(v[:10])
                    return
            for v in o.values():
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:5]:
                walk(v, depth + 1)

    walk(obj)
    return found[0] if found else ""


def parse_project(pp: dict) -> dict | None:
    data = (pp.get("projectDetailsData") or {}).get("attributes") or {}
    det = data.get("ProjectDetails") or {}
    if not det:
        return None
    banner = det.get("ProjectBanner") or {}
    about = det.get("AboutProject") or {}
    loc = det.get("loaction") or det.get("location") or {}
    locd = loc.get("locationDetailsWithImages") or {}
    seo = det.get("SEO") or {}
    facts = {x.get("name"): x.get("value") for x in about.get("AboutDetailsType") or [] if x.get("name")}
    return {
        "name": clean_ws(data.get("title") or banner.get("Heading") or ""),
        "project_code": data.get("projectCode"),
        "location": clean_ws(banner.get("Location") or locd.get("location") or ""),
        "tagline": clean_ws(about.get("title") or ""),
        "about": html_to_text(about.get("description") or ""),
        "facts": facts,  # Property Type, Status, Unit type, Area (SQFT) ...
        "amenities": [clean_ws(x.get("name", "")) for x in (det.get("Amenities") or {}).get("amenitiesList") or []],
        "nearby": [f"{x.get('Title')} ({x.get('Duration')})" for x in (det.get("KeyFeatures") or {}).get("keyfeaturelist") or []
                   if x.get("Title")],
        "key_features": html_to_text((det.get("KeyFeatures") or {}).get("description") or ""),
        "location_text": html_to_text(loc.get("description") or ""),
        "why_invest": [f"{x.get('name')}: {x.get('value')}" for x in (det.get("whyInvest") or {}).get("investlist") or []
                       if x.get("name")],
        "gallery_text": html_to_text((det.get("PhotoGallery") or {}).get("description") or ""),
        "seo_title": clean_ws(seo.get("metaTitle") or ""),
        "seo_description": clean_ws(seo.get("metaDescription") or ""),
        "lat": locd.get("lat"),
        "lon": locd.get("long"),
        "has_brochure": bool(((det.get("downloadbrochure") or {}).get("file") or {}).get("data")),
    }


def project_text(p: dict) -> str:
    lines = [f"Project: {p['name']} by DarGlobal", f"Location: {p['location']}"]
    lines += [f"{k}: {v}" for k, v in p["facts"].items()]
    if p["tagline"] or p["about"]:
        lines.append(f"About: {p['tagline']} {p['about']}".strip())
    for label, key in (("Design", "gallery_text"), ("Key features", "key_features"), ("Location details", "location_text")):
        if p[key]:
            lines.append(f"{label}: {p[key]}")
    if p["nearby"]:
        lines.append("Nearby: " + ", ".join(p["nearby"]))
    if p["amenities"]:
        lines.append("Amenities: " + ", ".join(p["amenities"]))
    if p["why_invest"]:
        lines.append("Why invest (as stated by DarGlobal): " + "; ".join(p["why_invest"]))
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only scrape the first N pages (for testing)")
    args = ap.parse_args()

    f = Fetcher(delay=1.0)
    robots = urllib.robotparser.RobotFileParser()
    status, txt = f.get(f"{BASE}/robots.txt")
    robots.parse(txt.splitlines())

    _, xml = f.get(f"{BASE}/sitemap.xml")
    urls = sorted(set(sitemap_urls(xml)) | {f"{BASE}/projects"})
    urls = [u.rstrip("/") or BASE for u in urls if not SKIP.search(u)]
    urls = [u for u in urls if robots.can_fetch("*", u)]
    if args.limit:
        urls = urls[: args.limit]
    print(f"{len(urls)} DarGlobal URLs to scrape", flush=True)

    pages, projects, failed = [], [], []
    for i, url in enumerate(urls, 1):
        status, html = f.get(url)
        if status != 200:
            failed.append((url, status))
            continue
        nd = next_data(html)
        pp = (nd or {}).get("props", {}).get("pageProps", {}) or {}
        meta = page_meta(html)
        section = section_of(url)
        proj = parse_project(pp)
        if proj:
            proj["url"] = url
            proj["scraped_at"] = now_iso()
            projects.append(proj)
            section = "project"
            text = project_text(proj)
        else:
            # Blog / press articles ship their body as one HTML string; prefer it over walking the JSON
            body_html = pp.get("blogDetailsHTML") or pp.get("pressDetailsHTML") or pp.get("insightDetailsHTML") \
                or pp.get("insightsDetailsHTML") or ""
            lines: list[str] = []
            if body_html:
                lines = [html_to_text(body_html)]
            else:
                collect_text({k: v for k, v in pp.items() if k not in IGNORE_KEYS}, lines)
            text = "\n".join(dedupe(lines))
        title = meta["title"].replace(" | DarGlobal", "").strip() or (proj or {}).get("name", "")
        if len(text) < 80 and not meta["description"]:
            failed.append((url, "no text"))
            continue
        pages.append({
            "source": "darglobal",
            "url": url,
            "section": section,
            "title": title,
            "description": meta["description"],
            "date": first_date(pp.get("blogDetails") or pp.get("pressDetails") or pp)
            if section in ("blog", "press", "insights") else "",
            "text": text,
            "scraped_at": now_iso(),
        })
        if i % 25 == 0:
            print(f"  {i}/{len(urls)} done ({f.network_hits} network requests)", flush=True)

    write_jsonl(RAW_DIR / "darglobal_pages.jsonl", pages)
    write_jsonl(RAW_DIR / "darglobal_projects.jsonl", projects)
    by_section: dict[str, int] = {}
    for p in pages:
        by_section[p["section"]] = by_section.get(p["section"], 0) + 1
    print(f"saved {len(pages)} pages {by_section}, {len(projects)} projects; {len(failed)} skipped/failed")
    for u, s in failed[:20]:
        print("   ", s, u)


if __name__ == "__main__":
    sys.exit(main())
