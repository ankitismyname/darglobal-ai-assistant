import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from query_parser import Filters, listing_intent, merge_follow_up, parse  # noqa: E402

DISTRICTS = {"al nakheel", "al olaya", "al malqa", "al shooalah"}
REGIONS = {"north riyadh", "north jeddah", "east riyadh"}


def p(q: str) -> Filters:
    return parse(q, DISTRICTS, REGIONS)


def test_rent_month_budget_and_bedrooms():
    f = p("3 bedroom apartment for rent in Riyadh under 6,000 a month")
    assert (f.purpose, f.types, f.city, f.bedrooms, f.price_max, f.period) == (
        "rent", ["apartment"], "Riyadh", 3, 6000, "month")


def test_sale_millions_and_region():
    f = p("Villas for sale in North Jeddah under 3 million")
    assert (f.purpose, f.types, f.city, f.region, f.price_max) == ("sale", ["villa"], "Jeddah", "north jeddah", 3_000_000)


def test_k_suffix_and_flat_synonym():
    f = p("2br flat to rent in jeddah below 45k per year")
    assert (f.types, f.bedrooms, f.price_max, f.period, f.purpose) == (["apartment"], 2, 45_000, "year", "rent")


def test_between_range():
    f = p("land for sale in dammam between 500k and 1.2m")
    assert (f.price_min, f.price_max, f.types) == (500_000, 1_200_000, ["land"])


def test_min_bedrooms_and_district():
    f = p("villa with at least 4 bedrooms in al malqa")
    assert f.bedrooms_min == 4 and f.bedrooms is None and f.districts == ["al malqa"]
    assert f.price_min is None  # "at least 4" is bedrooms, not a price


def test_area_not_read_as_price():
    f = p("apartment over 150 sqm in Riyadh for sale")
    assert f.area_min == 150 and f.price_min is None


def test_city_aliases():
    assert p("flats in mecca").city == "Makkah"
    assert p("villas in khobar").city == "Al Khobar"
    assert p("rent in medina").city == "Madinah"


def test_cheapest_sort():
    assert p("cheapest villa for rent in riyadh").sort == "cheapest"


def test_intent_listing_vs_darglobal():
    q = "3 bedroom apartment for rent in Riyadh"
    assert listing_intent(q, p(q))
    q = "Which DarGlobal projects are in Oman?"
    assert not listing_intent(q, p(q))
    q = "Tell me about Trump Tower Jeddah"
    assert not listing_intent(q, p(q))
    q = "apartments in Dubai"  # DarGlobal territory, not Wasalt (Saudi only)
    assert not listing_intent(q, p(q))
    q = "What is Wasalt?"
    assert not listing_intent(q, p(q))


def test_follow_up_keeps_previous_filters():
    first = p("villas for rent in Riyadh under 100k a year")
    follow = p("what about Jeddah?")
    merged = merge_follow_up(follow, first, "what about Jeddah?")
    assert (merged.city, merged.types, merged.purpose, merged.price_max) == ("Jeddah", ["villa"], "rent", 100_000)


def test_new_question_is_not_merged():
    first = p("villas for rent in Riyadh")
    q = "Tell me about the history of DarGlobal and its listing on the London Stock Exchange"
    assert merge_follow_up(p(q), first, q).city is None
