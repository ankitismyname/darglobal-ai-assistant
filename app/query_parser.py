"""Rule-based parser that turns a property question into structured listing filters.

No LLM call is used here: it is instant, deterministic, testable, and saves the free-model quota for the answer.
Example: "3 bed flat for rent in north Riyadh under 5k a month"
  -> purpose=rent, types=[apartment], city=Riyadh, region=north riyadh, bedrooms=3, price_max=5000, period=month
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from normalize import CITY_ALIASES, TYPE_ALIASES

NUM = r"(\d+(?:[.,]\d+)*)\s*(k|m|mn|million|thousand|mil)?"
FOREIGN = re.compile(
    r"\b(dubai|uae|emirates|oman|muscat|aida|spain|marbella|estepona|qatar|doha|london|uk|united kingdom|england|"
    r"bosnia|sarajevo|maldives|ras al khaimah|rak|al marjan|europe)\b"
)
DARGLOBAL = re.compile(
    r"\bdar\s*global\b|\bdarglobal\b|\bdar al arkan\b|\b(trump|missoni|pagani|aston martin|lamborghini|mouawad|"
    r"elie saab|w residences|marriott|mulliner|dg1|astera|marea|tierra viva|les vagues|neptune|la collina)\b"
)


@dataclass
class Filters:
    purpose: str | None = None  # sale | rent
    types: list[str] = field(default_factory=list)  # lower-case Wasalt property types
    city: str | None = None
    districts: list[str] = field(default_factory=list)  # lower-case district names found in the data
    region: str | None = None  # e.g. "north riyadh"
    bedrooms: int | None = None
    bedrooms_min: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    period: str | None = None  # month | year (rent prices only)
    area_min: float | None = None
    area_max: float | None = None
    furnished: bool = False
    sort: str | None = None  # cheapest | priciest | newest | largest

    def is_empty(self) -> bool:
        return not any(v for k, v in asdict(self).items() if k != "sort")

    def describe(self) -> str:
        d = {k: v for k, v in asdict(self).items() if v not in (None, [], False)}
        return ", ".join(f"{k}={v}" for k, v in d.items()) or "none"


def parse_amount(num: str, unit: str | None) -> float | None:
    try:
        x = float(num.replace(",", ""))
    except ValueError:
        return None
    unit = (unit or "").lower()
    if unit in ("k", "thousand"):
        x *= 1_000
    elif unit in ("m", "mn", "million", "mil"):
        x *= 1_000_000
    return x


def _find_amounts(q: str) -> tuple[float | None, float | None]:
    """Return (min, max) price from phrases like 'under 2M', 'between 50k and 80k', 'over 1 million'."""
    pmin = pmax = None
    m = re.search(rf"between\s+(?:sar\s*)?{NUM}\s*(?:sar\s*)?(?:and|to|-)\s*(?:sar\s*)?{NUM}", q)
    if not m:
        m = re.search(rf"(?:sar\s*)?{NUM}\s*(?:sar\s*)?(?:-|to)\s*(?:sar\s*)?{NUM}\s*(?:sar|riyals?)", q)
    if m:
        lo = parse_amount(m.group(1), m.group(2) or m.group(4))
        hi = parse_amount(m.group(3), m.group(4))
        if lo and hi:
            return min(lo, hi), max(lo, hi)
    m = re.search(rf"(?:under|below|less than|max(?:imum)?|up to|upto|within|budget(?: of| is)?|cheaper than|no more than|<)\s*(?:sar\s*)?{NUM}", q)
    if m:
        pmax = parse_amount(m.group(1), m.group(2))
    m = re.search(rf"(?:over|above|more than|at least|min(?:imum)?|from|starting|>)\s*(?:sar\s*)?{NUM}\s*(?:sar|riyals?|k\b|m\b|million)?", q)
    if m and not re.search(rf"(?:over|above|more than|at least|min(?:imum)?|from)\s*{NUM}\s*(?:bed|br|bhk|room|sqm|m2|square)", q):
        val = parse_amount(m.group(1), m.group(2))
        if val and val >= 1000:  # avoid "at least 3" (bedrooms) being read as a price
            pmin = val
    if pmax is not None and pmax < 1000:  # "under 5" without unit is not a SAR price
        pmax = None
    return pmin, pmax


def parse(query: str, known_districts: set[str] | None = None, known_regions: set[str] | None = None) -> Filters:
    q = " " + re.sub(r"\s+", " ", query.lower().replace("’", "'")) + " "
    f = Filters()

    if re.search(r"\b(rent|rental|renting|lease|leasing|to let|per month|monthly|a month|/month|per year|yearly|annual)\b", q):
        f.purpose = "rent"
    if re.search(r"\b(buy|buying|purchase|for sale|on sale|sale|freehold)\b", q):
        f.purpose = "sale" if f.purpose is None or "for sale" in q or "buy" in q else f.purpose

    words = sorted(TYPE_ALIASES, key=len, reverse=True)
    for w in words:
        if re.search(rf"\b{re.escape(w)}\b", q) and TYPE_ALIASES[w] not in f.types:
            f.types.append(TYPE_ALIASES[w])
    if re.search(r"\bfurnished\b", q) and not re.search(r"\bun-?furnished\b", q):
        f.furnished = True

    for alias in sorted(CITY_ALIASES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", q):
            f.city = CITY_ALIASES[alias]
            break

    for region in sorted(known_regions or [], key=len, reverse=True):
        if region and re.search(rf"\b{re.escape(region)}\b", q):
            f.region = region
            break
    for d in sorted(known_districts or [], key=len, reverse=True):
        if len(d) >= 4 and re.search(rf"\b{re.escape(d)}\b", q):
            f.districts.append(d)
            if len(f.districts) >= 3:
                break

    m = re.search(r"(\d+)\s*\+\s*(?:bed|br|bhk|bedroom)", q) or re.search(
        r"(?:at least|minimum|min|more than)\s*(\d+)\s*(?:-|\s)?(?:bed|br|bhk|bedroom)", q)
    if m:
        f.bedrooms_min = int(m.group(1)) + (1 if "more than" in m.group(0) else 0)
    else:
        m = re.search(r"\b(\d+|one|two|three|four|five|six)\s*(?:-|\s)?(?:bed|beds|bedroom|bedrooms|br|bhk|bd)\b", q)
        if m:
            words_to_n = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
            f.bedrooms = words_to_n.get(m.group(1)) or int(m.group(1))
    if re.search(r"\bstudios?\b", q) and f.bedrooms is None:
        f.bedrooms = None  # studios are listed with 0 or 1 bedroom; leave the bedroom filter open

    m = re.search(r"(?:over|above|more than|at least|min(?:imum)?|bigger than|larger than)\s*(\d[\d,]*)\s*(?:sqm|sq m|m2|square met)", q)
    if m:
        f.area_min = float(m.group(1).replace(",", ""))
    m = re.search(r"(?:under|below|less than|max(?:imum)?|smaller than|up to)\s*(\d[\d,]*)\s*(?:sqm|sq m|m2|square met)", q)
    if m:
        f.area_max = float(m.group(1).replace(",", ""))

    q_no_area = re.sub(r"\d[\d,]*\s*(?:sqm|sq m|m2|square met\w*)", " ", q)
    q_no_area = re.sub(r"\d+\s*(?:-|\s)?(?:bed|beds|bedroom|bedrooms|br|bhk|bd)\b", " ", q_no_area)
    f.price_min, f.price_max = _find_amounts(q_no_area)
    if re.search(r"\b(per month|monthly|a month|/month|/mo|pm)\b", q):
        f.period = "month"
    elif re.search(r"\b(per year|yearly|a year|annual|annually|/year|/yr)\b", q):
        f.period = "year"
    elif f.purpose == "rent" and f.price_max and f.price_max < 15_000:
        f.period = "month"  # "rent under 5000" almost always means per month

    if re.search(r"\b(cheapest|lowest price|most affordable|cheap|budget|affordable)\b", q):
        f.sort = "cheapest"
    elif re.search(r"\b(most expensive|priciest|luxur\w*|high[- ]end|premium)\b", q):
        f.sort = "priciest"
    elif re.search(r"\b(newest|latest|recent|new listings?)\b", q):
        f.sort = "newest"
    elif re.search(r"\b(largest|biggest|most spacious)\b", q):
        f.sort = "largest"
    return f


def listing_intent(query: str, f: Filters, project_names: set[str] | None = None) -> bool:
    """Is this a request for Wasalt listings (vs. a question about DarGlobal, projects or general info)?"""
    q = query.lower()
    if DARGLOBAL.search(q) and "wasalt" not in q:
        return False
    if any(name and name in q for name in project_names or []):
        return False
    if FOREIGN.search(q) and not f.city:
        return False
    if re.search(r"\b(listings?|properties for|property for|for rent|for sale|to rent|to buy|show me|find me|looking for|"
                 r"search for|available)\b", q) and (f.types or f.city or f.purpose):
        return True
    strong = sum([bool(f.types), bool(f.city or f.districts or f.region), bool(f.purpose),
                  bool(f.bedrooms or f.bedrooms_min), bool(f.price_min or f.price_max)])
    return strong >= 2


FOLLOW_UP = re.compile(r"^\s*(what about|how about|and |and\?|any |show more|more |cheaper|bigger|smaller|only |"
                       r"in |with |under |below |above |over |same )", re.I)


def merge_follow_up(new: Filters, prev: Filters | None, query: str) -> Filters:
    """'What about Jeddah?' after a Riyadh villa search keeps the villa/rent filters and swaps the city."""
    if prev is None or prev.is_empty():
        return new
    if not (FOLLOW_UP.search(query) or len(query.split()) <= 6):
        return new
    merged = Filters(**asdict(prev))
    for k, v in asdict(new).items():
        if v not in (None, [], False):
            setattr(merged, k, v)
    if new.city and new.city != prev.city:  # a new city makes the old districts/region meaningless
        merged.districts = new.districts
        merged.region = new.region
    return merged
