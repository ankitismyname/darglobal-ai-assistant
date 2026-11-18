"""Normalisation shared by the index builder and the query parser (city names, property types, formatting)."""
from __future__ import annotations

import math
import re

CITY_ALIASES = {
    "riyadh": "Riyadh", "ar riyadh": "Riyadh", "al riyadh": "Riyadh", "riyad": "Riyadh",
    "jeddah": "Jeddah", "jiddah": "Jeddah", "jedda": "Jeddah", "jedah": "Jeddah",
    "dammam": "Dammam", "aldammam": "Dammam", "al dammam": "Dammam", "ad dammam": "Dammam",
    "al khobar": "Al Khobar", "alkhobar": "Al Khobar", "khobar": "Al Khobar", "al khubar": "Al Khobar",
    "makkah": "Makkah", "mecca": "Makkah", "makka": "Makkah", "makkah al mukarramah": "Makkah",
    "madinah": "Madinah", "medina": "Madinah", "al madinah": "Madinah", "madina": "Madinah",
    "al madinah al munawwarah": "Madinah", "almadinah": "Madinah", "al madina": "Madinah",
}

# User words -> Wasalt propertySubType values (lower-case). Filled out after looking at the scraped data.
TYPE_ALIASES = {
    "apartment": "apartment", "apartments": "apartment", "flat": "apartment", "flats": "apartment",
    "studio": "apartment", "studios": "apartment",
    "villa": "villa", "villas": "villa", "house": "villa", "houses": "villa", "townhouse": "villa",
    "floor": "floor", "floors": "floor",
    "land": "land", "lands": "land", "plot": "land", "plots": "land",
    "duplex": "duplex", "duplexes": "duplex",
    "office": "office", "offices": "office",
    "shop": "shop", "shops": "shop", "store": "shop", "showroom": "showroom", "showrooms": "showroom",
    "warehouse": "warehouse", "warehouses": "warehouse",
    "building": "building", "buildings": "building",
    "rest house": "rest house", "resthouse": "rest house", "istiraha": "rest house", "chalet": "chalet",
}


def _key(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", (s or "").lower())).strip()


def norm_city(s: str | None) -> str | None:
    if not s:
        return None
    k = _key(s)
    return CITY_ALIASES.get(k) or CITY_ALIASES.get(k.replace(" ", "")) or s.strip().title()


def is_num(x) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def fmt_sar(x) -> str:
    if not is_num(x):
        return ""
    return f"SAR {x:,.0f}"


def fmt_num(x) -> str:
    if not is_num(x):
        return ""
    return f"{x:,.0f}" if float(x).is_integer() else f"{x:,.1f}"


def listing_price_text(r: dict) -> str:
    if r.get("purpose") == "sale":
        return f"Price {fmt_sar(r.get('price_sar'))}" if is_num(r.get("price_sar")) else "Price on request"
    year, month = r.get("rent_year_sar"), r.get("rent_month_sar")
    if is_num(year) and is_num(month):
        return f"Rent {fmt_sar(year)} per year / {fmt_sar(month)} per month"
    if is_num(year):
        return f"Rent {fmt_sar(year)} per year (≈ {fmt_sar(year / 12)} per month)"
    if is_num(month):
        return f"Rent {fmt_sar(month)} per month (≈ {fmt_sar(month * 12)} per year)"
    return "Rent on request"


def text_or_none(x) -> str | None:
    """A non-empty string, or None (pandas gives NaN floats for missing text)."""
    return x.strip() if isinstance(x, str) and x.strip() else None


def listing_doc(r: dict) -> str:
    """One-paragraph description of a listing, used for embedding and as LLM context."""
    r = {k: (text_or_none(v) if isinstance(v, (str, float)) and not is_num(v) else v) for k, v in r.items()}
    where = ", ".join(x for x in [r.get("district"), r.get("region"), r.get("city")] if x)
    bits = [f"{r.get('property_type') or 'Property'} for {r.get('purpose')} in {where}."]
    rooms = []
    if is_num(r.get("bedrooms")):
        rooms.append(f"{fmt_num(r['bedrooms'])} bedrooms")
    if is_num(r.get("bathrooms")):
        rooms.append(f"{fmt_num(r['bathrooms'])} bathrooms")
    if is_num(r.get("area_sqm")):
        rooms.append(f"{fmt_num(r['area_sqm'])} sqm")
    if rooms:
        bits.append(", ".join(rooms) + ".")
    bits.append(listing_price_text(r) + ".")
    if r.get("furnishing"):
        bits.append(f"Furnishing: {r['furnishing']}.")
    if r.get("completion"):
        bits.append(f"Completion/age: {r['completion']}.")
    if r.get("amenities"):
        bits.append("Amenities: " + ", ".join(r["amenities"]) + ".")
    if r.get("facing"):
        bits.append(f"Facing {r['facing']}.")
    if r.get("main_type"):
        bits.append(f"{r['main_type']} property.")
    if r.get("published_at"):
        bits.append(f"Listed {r['published_at']}.")
    return " ".join(bits)
