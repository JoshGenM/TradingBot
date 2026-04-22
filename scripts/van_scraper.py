#!/usr/bin/env python3
"""
Ford Transit Connect van scraper — UK listing sites.
Searches AutoTrader UK and Motors.co.uk for:
  - Ford Transit Connect
  - 2018 or newer
  - ≤110,000 miles
  - EcoBlue engine (diesel)
"""

import sys
import json
import time
import re
import argparse
from urllib.parse import urlencode

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Run: pip3 install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

YEAR_FROM = 2018
MAX_MILEAGE = 110_000
ECOBLUE_RE = re.compile(r"ecoblue", re.IGNORECASE)
MILEAGE_RE = re.compile(r"([\d,]+)\s*(?:miles?|mi\.?)", re.IGNORECASE)
PRICE_RE = re.compile(r"£\s*[\d,]+")


def is_ecoblue(text: str) -> bool:
    return bool(ECOBLUE_RE.search(text))


def parse_mileage(text: str) -> int | None:
    m = MILEAGE_RE.search(text)
    if m:
        return int(m.group(1).replace(",", ""))
    digits = re.search(r"\b(\d{4,6})\b", text)
    if digits:
        return int(digits.group(1))
    return None


def parse_year(text: str) -> int | None:
    m = re.search(r"\b(201[89]|20[2-9]\d)\b", text)
    return int(m.group(1)) if m else None


def scrape_autotrader() -> list[dict]:
    params = {
        "make": "Ford",
        "model": "Transit Connect",
        "year-from": str(YEAR_FROM),
        "maximum-mileage": str(MAX_MILEAGE),
        "fuel-type": "Diesel",
        "body-type": "Van",
        "page": "1",
    }
    url = "https://www.autotrader.co.uk/van-search?" + urlencode(params)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"  AutoTrader: request failed — {e}", file=sys.stderr)
        return []

    if resp.status_code != 200:
        print(f"  AutoTrader: HTTP {resp.status_code} — skipping", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    listings = []

    # Strategy 1: parse __NEXT_DATA__ embedded JSON (Next.js SSR)
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    if next_data_tag:
        try:
            data = json.loads(next_data_tag.string)
            listings = _extract_autotrader_next_data(data)
            if listings:
                return listings
        except (json.JSONDecodeError, KeyError):
            pass

    # Strategy 2: BeautifulSoup CSS selectors (fallback)
    listings = _extract_autotrader_html(soup)
    return listings


def _extract_autotrader_next_data(data: dict) -> list[dict]:
    """Walk the __NEXT_DATA__ tree to find listing objects."""
    results = []

    def _walk(obj, depth=0):
        if depth > 12 or not isinstance(obj, (dict, list)):
            return
        if isinstance(obj, list):
            for item in obj:
                _walk(item, depth + 1)
            return
        # Look for listing-shaped dicts: must have price AND (title or make)
        keys = set(obj.keys())
        if ("price" in keys or "priceGBP" in keys) and (
            "title" in keys or "heading" in keys or "make" in keys
        ):
            listing = _map_autotrader_listing(obj)
            if listing:
                results.append(listing)
            return
        for v in obj.values():
            _walk(v, depth + 1)

    _walk(data)
    return results


def _map_autotrader_listing(obj: dict) -> dict | None:
    """Map a raw AutoTrader listing dict to our standard schema."""
    title = obj.get("title") or obj.get("heading") or obj.get("derivativeTitle") or ""
    if isinstance(obj.get("make"), str) and isinstance(obj.get("model"), str):
        if not title:
            title = f"{obj['make']} {obj['model']}"

    # Mileage
    mileage_raw = obj.get("mileage") or obj.get("mileageValue") or ""
    if isinstance(mileage_raw, int):
        mileage = mileage_raw
    else:
        mileage = parse_mileage(str(mileage_raw)) or 0

    # Year
    year_raw = obj.get("year") or obj.get("modelYear") or obj.get("firstRegisteredYear") or ""
    if isinstance(year_raw, int):
        year = year_raw
    else:
        year = parse_year(str(year_raw)) or 0

    # Price
    price_raw = obj.get("price") or obj.get("priceGBP") or obj.get("advertisedPrice") or ""
    if isinstance(price_raw, (int, float)):
        price = f"£{int(price_raw):,}"
    else:
        price = str(price_raw).strip() or "POA"

    # Engine / fuel
    engine = (
        obj.get("engine") or obj.get("engineSize") or
        obj.get("fuelType") or obj.get("derivative") or ""
    )

    # Location
    location = (
        obj.get("location") or obj.get("dealerLocation") or
        (obj.get("dealer") or {}).get("location") or
        (obj.get("seller") or {}).get("location") or ""
    )

    # Seller
    seller = (
        obj.get("sellerName") or obj.get("dealerName") or
        (obj.get("dealer") or {}).get("name") or
        (obj.get("seller") or {}).get("name") or ""
    )

    # URL
    url = obj.get("url") or obj.get("href") or obj.get("listingUrl") or ""
    if url and not url.startswith("http"):
        url = "https://www.autotrader.co.uk" + url

    # Quality gates
    if year and year < YEAR_FROM:
        return None
    if mileage and mileage > MAX_MILEAGE:
        return None

    combined_text = f"{title} {engine} {obj.get('description', '')}"
    if not is_ecoblue(combined_text):
        return None

    return {
        "title": title,
        "year": year or None,
        "mileage": mileage or None,
        "price": price,
        "engine": engine or "EcoBlue Diesel",
        "location": location or "Unknown",
        "seller": seller or "",
        "url": url,
        "source": "autotrader",
    }


def _extract_autotrader_html(soup: BeautifulSoup) -> list[dict]:
    """Fallback: parse AutoTrader listing cards from raw HTML."""
    results = []
    # AutoTrader uses article tags or li tags for listings
    cards = soup.select("li[data-testid='trader-seller-listing']")
    if not cards:
        cards = soup.select("article.listing-fpa-content")
    if not cards:
        cards = soup.select("[class*='listing-']")

    for card in cards:
        text = card.get_text(" ", strip=True)

        if not is_ecoblue(text):
            continue

        year = parse_year(text) or 0
        if year and year < YEAR_FROM:
            continue

        mileage = parse_mileage(text) or 0
        if mileage and mileage > MAX_MILEAGE:
            continue

        price_m = PRICE_RE.search(text)
        price = price_m.group(0) if price_m else "POA"

        title_tag = card.select_one("h2, h3, [class*='title']")
        title = title_tag.get_text(strip=True) if title_tag else "Ford Transit Connect"

        a_tag = card.find("a", href=True)
        href = a_tag["href"] if a_tag else ""
        if href and not href.startswith("http"):
            href = "https://www.autotrader.co.uk" + href

        results.append({
            "title": title,
            "year": year or None,
            "mileage": mileage or None,
            "price": price,
            "engine": "EcoBlue Diesel",
            "location": "See listing",
            "seller": "",
            "url": href,
            "source": "autotrader",
        })

    return results


def scrape_motors() -> list[dict]:
    params = {
        "year_from": str(YEAR_FROM),
        "mileage_to": str(MAX_MILEAGE),
        "fuel": "diesel",
    }
    url = "https://www.motors.co.uk/search/van/ford/transit-connect/?" + urlencode(params)

    time.sleep(1)  # polite delay between site requests

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"  Motors.co.uk: request failed — {e}", file=sys.stderr)
        return []

    if resp.status_code != 200:
        print(f"  Motors.co.uk: HTTP {resp.status_code} — skipping", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Try __NEXT_DATA__ first
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    if next_data_tag:
        try:
            data = json.loads(next_data_tag.string)
            results = _extract_motors_next_data(data)
            if results:
                return results
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback: HTML parsing
    cards = soup.select("[class*='listing'], [class*='vehicle-card'], article")
    for card in cards:
        text = card.get_text(" ", strip=True)
        if not is_ecoblue(text):
            continue

        year = parse_year(text) or 0
        if year and year < YEAR_FROM:
            continue

        mileage = parse_mileage(text) or 0
        if mileage and mileage > MAX_MILEAGE:
            continue

        price_m = PRICE_RE.search(text)
        price = price_m.group(0) if price_m else "POA"

        a_tag = card.find("a", href=True)
        href = a_tag["href"] if a_tag else ""
        if href and not href.startswith("http"):
            href = "https://www.motors.co.uk" + href

        results.append({
            "title": "Ford Transit Connect EcoBlue",
            "year": year or None,
            "mileage": mileage or None,
            "price": price,
            "engine": "EcoBlue Diesel",
            "location": "See listing",
            "seller": "",
            "url": href,
            "source": "motors.co.uk",
        })

    return results


def _extract_motors_next_data(data: dict) -> list[dict]:
    results = []

    def _walk(obj, depth=0):
        if depth > 12 or not isinstance(obj, (dict, list)):
            return
        if isinstance(obj, list):
            for item in obj:
                _walk(item, depth + 1)
            return
        keys = set(obj.keys())
        if ("price" in keys or "advertisedPrice" in keys) and (
            "title" in keys or "make" in keys or "heading" in keys
        ):
            listing = _map_motors_listing(obj)
            if listing:
                results.append(listing)
            return
        for v in obj.values():
            _walk(v, depth + 1)

    _walk(data)
    return results


def _map_motors_listing(obj: dict) -> dict | None:
    title = obj.get("title") or obj.get("heading") or "Ford Transit Connect"

    mileage_raw = obj.get("mileage") or obj.get("mileageValue") or ""
    mileage = mileage_raw if isinstance(mileage_raw, int) else (parse_mileage(str(mileage_raw)) or 0)

    year_raw = obj.get("year") or obj.get("registrationYear") or ""
    year = year_raw if isinstance(year_raw, int) else (parse_year(str(year_raw)) or 0)

    price_raw = obj.get("price") or obj.get("advertisedPrice") or ""
    price = f"£{int(price_raw):,}" if isinstance(price_raw, (int, float)) else str(price_raw) or "POA"

    engine = obj.get("engine") or obj.get("engineDescription") or obj.get("fuelType") or ""
    location = obj.get("location") or obj.get("dealerTown") or ""
    seller = obj.get("sellerName") or obj.get("dealerName") or ""

    url = obj.get("url") or obj.get("href") or ""
    if url and not url.startswith("http"):
        url = "https://www.motors.co.uk" + url

    if year and year < YEAR_FROM:
        return None
    if mileage and mileage > MAX_MILEAGE:
        return None

    combined = f"{title} {engine} {obj.get('description', '')}"
    if not is_ecoblue(combined):
        return None

    return {
        "title": title,
        "year": year or None,
        "mileage": mileage or None,
        "price": price,
        "engine": engine or "EcoBlue Diesel",
        "location": location or "Unknown",
        "seller": seller or "",
        "url": url,
        "source": "motors.co.uk",
    }


def deduplicate(listings: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for lst in listings:
        key = (lst.get("url") or "").rstrip("/")
        if key and key in seen:
            continue
        seen.add(key)
        out.append(lst)
    return out


def sort_by_price(listings: list[dict]) -> list[dict]:
    def price_int(lst):
        raw = lst.get("price", "")
        m = re.search(r"[\d,]+", raw.replace("£", ""))
        return int(m.group(0).replace(",", "")) if m else 999_999

    return sorted(listings, key=price_int)


def print_table(listings: list[dict]) -> None:
    if not listings:
        print("No listings found matching criteria.")
        return

    col_widths = {
        "price":    8,
        "year":     4,
        "mileage":  9,
        "engine":   22,
        "location": 18,
        "source":   12,
    }

    hdr = (
        f"{'Price':<{col_widths['price']}} | "
        f"{'Year':<{col_widths['year']}} | "
        f"{'Mileage':<{col_widths['mileage']}} | "
        f"{'Engine':<{col_widths['engine']}} | "
        f"{'Location':<{col_widths['location']}} | "
        f"{'Source':<{col_widths['source']}} | URL"
    )
    sep = "-" * len(hdr)
    print(f"\nFord Transit Connect — EcoBlue — 2018+ — ≤110,000 miles")
    print(f"Found {len(listings)} listing(s)\n")
    print(hdr)
    print(sep)

    for lst in listings:
        mileage = f"{lst['mileage']:,}" if lst.get("mileage") else "—"
        year = str(lst["year"]) if lst.get("year") else "—"
        engine = (lst.get("engine") or "")[:col_widths["engine"]]
        location = (lst.get("location") or "")[:col_widths["location"]]
        price = (lst.get("price") or "POA")[:col_widths["price"]]
        source = (lst.get("source") or "")[:col_widths["source"]]
        url = lst.get("url") or "—"

        note = ""
        if lst.get("mileage") and lst["mileage"] > 100_000:
            note = " ⚠ high miles"
        if lst.get("price") and isinstance(lst["price"], str):
            m = re.search(r"[\d,]+", lst["price"].replace("£", ""))
            if m and int(m.group(0).replace(",", "")) < 10_000:
                note += " ★ low price"

        print(
            f"{price:<{col_widths['price']}} | "
            f"{year:<{col_widths['year']}} | "
            f"{mileage:<{col_widths['mileage']}} | "
            f"{engine:<{col_widths['engine']}} | "
            f"{location:<{col_widths['location']}} | "
            f"{source:<{col_widths['source']}} | {url}{note}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ford Transit Connect EcoBlue van scraper")
    parser.add_argument("--format", choices=["json", "table"], default="json")
    parser.add_argument("--sites", default="autotrader,motors", help="Comma-separated site list")
    args = parser.parse_args()

    sites = [s.strip().lower() for s in args.sites.split(",")]
    all_listings: list[dict] = []

    if "autotrader" in sites:
        print("Scraping AutoTrader UK...", file=sys.stderr)
        at = scrape_autotrader()
        print(f"  {len(at)} listing(s) found on AutoTrader", file=sys.stderr)
        all_listings.extend(at)

    if "motors" in sites:
        print("Scraping Motors.co.uk...", file=sys.stderr)
        mo = scrape_motors()
        print(f"  {len(mo)} listing(s) found on Motors.co.uk", file=sys.stderr)
        all_listings.extend(mo)

    all_listings = deduplicate(all_listings)
    all_listings = sort_by_price(all_listings)

    if args.format == "table":
        print_table(all_listings)
    else:
        print(json.dumps(all_listings, indent=2))


if __name__ == "__main__":
    main()
