#!/usr/bin/env python3
"""
Ford Transit Connect van scraper — UK listing sites.
Sources: AutoTrader UK (GraphQL API), Gumtree (HTML).
Criteria: Ford Transit Connect, 2018+, ≤110,000 miles, EcoBlue diesel engine.
"""

import sys
import json
import time
import re
import uuid
import argparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip3 install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

YEAR_FROM   = 2018
MAX_MILEAGE = 110_000
ECOBLUE_RE  = re.compile(r"ecoblue", re.IGNORECASE)
PRICE_RE    = re.compile(r"£\s*[\d,]+")
MILEAGE_RE  = re.compile(r"([\d,]+)\s*miles?", re.IGNORECASE)

# AutoTrader: their internal GraphQL endpoint (no auth required)
AT_URL = "https://www.autotrader.co.uk/at-gateway"
AT_HEADERS = {
    "User-Agent":           "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Content-Type":         "application/json",
    "x-sauron-app-name":    "sauron-search-results-app",
    "x-sauron-app-version": "3868",
    "Referer":              "https://www.autotrader.co.uk/van-search?make=Ford&model=Transit%20Connect",
    "Origin":               "https://www.autotrader.co.uk",
    "Accept":               "*/*",
    "Accept-Language":      "en-GB,en;q=0.9",
}

AT_GRAPHQL_QUERY = """
query SearchResultsListingsGridQuery(
    $filters: [FilterInput!]!, $channel: Channel!, $page: Int,
    $sortBy: SearchResultsSort, $listingType: [ListingType!],
    $searchId: String!, $featureFlags: [FeatureFlag]
) {
    searchResults(input: {
        facets: [], filters: $filters, channel: $channel,
        page: $page, sortBy: $sortBy, listingType: $listingType,
        searchId: $searchId, featureFlags: $featureFlags
    }) {
        listings {
            ... on SearchListing {
                advertId title subTitle attentionGrabber price
                vehicleLocation sellerType fpaLink
                trackingContext { advertContext { year } }
            }
        }
        page { number count results { count } }
    }
}
"""

# Gumtree: HTML scraping using data-q attributes
GUMTREE_URL = (
    "https://www.gumtree.com/search"
    "?search_category=vans"
    "&q=ford+transit+connect+ecoblue"
    "&search_scope=false"
    "&vehicle_make=ford"
    "&vehicle_model=ford-transit-connect"
)
GT_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}


def scrape_autotrader(max_pages: int = 3) -> list[dict]:
    search_id = f"vansearch-{uuid.uuid4().hex[:8]}"
    filters = [
        {"filter": "make",                 "selected": ["Ford"]},
        {"filter": "model",                "selected": ["Transit Connect"]},
        {"filter": "price_search_type",    "selected": ["total"]},
        {"filter": "postcode",             "selected": ["SW1A 1AA"]},
        {"filter": "min_year_manufactured","selected": [str(YEAR_FROM)]},
        {"filter": "max_mileage",          "selected": [str(MAX_MILEAGE)]},
        {"filter": "keywords",             "selected": ["EcoBlue"]},
    ]
    results = []

    for page_num in range(1, max_pages + 1):
        payload = {
            "operationName": "SearchResultsListingsGridQuery",
            "variables": {
                "filters":      filters,
                "channel":      "vans",
                "page":         page_num,
                "searchId":     search_id,
                "featureFlags": [],
            },
            "query": AT_GRAPHQL_QUERY,
        }
        try:
            resp = requests.post(AT_URL, headers=AT_HEADERS, json=payload, timeout=15)
        except requests.RequestException as e:
            print(f"  AutoTrader page {page_num}: request failed — {e}", file=sys.stderr)
            break

        if resp.status_code != 200:
            print(f"  AutoTrader page {page_num}: HTTP {resp.status_code}", file=sys.stderr)
            break

        data = resp.json()
        if "errors" in data:
            msg = data["errors"][0].get("message", "unknown error")
            print(f"  AutoTrader GraphQL error: {msg}", file=sys.stderr)
            break

        sr = (data.get("data") or {}).get("searchResults") or {}
        listings = [l for l in sr.get("listings", []) if l.get("advertId")]

        for lst in listings:
            subtitle = lst.get("subTitle") or ""
            if not ECOBLUE_RE.search(subtitle):
                continue
            year_val = (
                (lst.get("trackingContext") or {})
                .get("advertContext", {})
                .get("year")
            )
            if year_val and int(year_val) < YEAR_FROM:
                continue

            fpa = lst.get("fpaLink") or ""
            url = "https://www.autotrader.co.uk" + fpa.split("?")[0] if fpa else ""

            location = lst.get("vehicleLocation") or "Unknown"
            location = re.sub(r"\s*\(\d+ miles?\)$", "", location, flags=re.IGNORECASE).strip()

            results.append({
                "title":    f"Ford Transit Connect {subtitle}",
                "year":     year_val,
                "mileage":  None,  # server-filtered ≤110k; exact figure on listing page
                "price":    lst.get("price") or "POA",
                "engine":   subtitle,
                "location": location,
                "seller":   (lst.get("sellerType") or "").title(),
                "url":      url,
                "source":   "autotrader",
            })

        page_info = sr.get("page") or {}
        total_pages = page_info.get("count") or 1
        if page_num >= total_pages or page_num >= max_pages:
            break
        time.sleep(1.5)

    return results


def scrape_gumtree() -> list[dict]:
    # Fresh session with no cookies avoids Cloudflare rbzns challenge
    session = requests.Session()
    session.cookies.clear()

    try:
        resp = session.get(GUMTREE_URL, headers=GT_HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"  Gumtree: request failed — {e}", file=sys.stderr)
        return []

    # Cloudflare challenge page is tiny (~521 bytes)
    if resp.status_code != 200 or len(resp.text) < 10_000:
        print("  Gumtree: bot-protection active — skipping", file=sys.stderr)
        return []

    results = []
    # Split on listing boundary markers using data-q attributes
    blocks = re.split(r'(?=data-q="search-result")', resp.text)

    for block in blocks[1:]:
        if 'data-q="search-result"' not in block:
            continue

        title_m  = re.search(r'data-q="tile-title"[^>]*>([^<]+)<', block)
        url_m    = re.search(r'data-q="search-result-anchor" href="(/p/[^"]+)"', block)
        price_m  = re.search(r'data-q="tile-price"[^>]*>£([\d,]+)', block)
        year_m   = re.search(r'data-q="motors-year"[^>]*>(\d{4})<', block)
        mile_m   = re.search(r'data-q="motors-mileage"[^>]*>([\d,]+)<', block)
        fuel_m   = re.search(r'data-q="motors-fuel-type"[^>]*>([^<]+)<', block)
        eng_m    = re.search(r'data-q="motors-engine-size"[^>]*>([^<]+)<', block)
        loc_m    = re.search(r'data-q="tile-location"[^>]*>([^<]+)<', block)
        seller_m = re.search(r'data-q="motors-seller-type"[^>]*>([^<]+)<', block)

        title = title_m.group(1).strip() if title_m else ""
        if not ECOBLUE_RE.search(title):
            continue

        year_str = year_m.group(1) if year_m else "0"
        mile_str = (mile_m.group(1).replace(",", "") if mile_m else "0")

        if int(year_str) < YEAR_FROM:
            continue
        if int(mile_str) > MAX_MILEAGE:
            continue

        fuel      = fuel_m.group(1).strip() if fuel_m else "Diesel"
        engine_cc = eng_m.group(1).strip() if eng_m else ""
        engine_desc = "1.5 EcoBlue " + fuel + (f" ({engine_cc}cc)" if engine_cc else "")

        results.append({
            "title":    title[:80],
            "year":     int(year_str) if year_str != "0" else None,
            "mileage":  int(mile_str) if mile_str != "0" else None,
            "price":    f"£{price_m.group(1)}" if price_m else "POA",
            "engine":   engine_desc,
            "location": loc_m.group(1).strip() if loc_m else "Unknown",
            "seller":   seller_m.group(1).strip() if seller_m else "",
            "url":      "https://www.gumtree.com" + url_m.group(1) if url_m else "",
            "source":   "gumtree",
        })

    return results


def _parse_price_int(price_str: str) -> int | None:
    m = re.search(r"[\d,]+", price_str.replace("£", ""))
    return int(m.group(0).replace(",", "")) if m else None


def deduplicate(listings: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for lst in listings:
        key = (lst.get("url") or "").rstrip("/")
        if key and key in seen:
            continue
        seen.add(key)
        out.append(lst)
    return out


def sort_by_price(listings: list[dict]) -> list[dict]:
    return sorted(listings, key=lambda l: _parse_price_int(l.get("price") or "") or 999_999)


def print_table(listings: list[dict]) -> None:
    if not listings:
        print("No listings found matching criteria.")
        return

    print(f"\nFord Transit Connect — EcoBlue Diesel — {YEAR_FROM}+ — ≤{MAX_MILEAGE:,} miles")
    print(f"Found {len(listings)} listing(s)\n")

    header = (
        f"{'Price':<14} {'Year':<5} {'Mileage':<12} "
        f"{'Engine/Spec':<38} {'Location':<22} {'Source':<12} URL"
    )
    print(header)
    print("-" * len(header))

    for lst in listings:
        price    = (lst.get("price") or "POA")[:14]
        year     = str(lst["year"]) if lst.get("year") else "—"
        mileage  = f"{lst['mileage']:,}" if lst.get("mileage") else "≤110k*"
        engine   = (lst.get("engine") or "")[:38]
        location = (lst.get("location") or "")[:22]
        source   = (lst.get("source") or "")[:12]
        url      = lst.get("url") or "—"

        flags = []
        if lst.get("mileage") and lst["mileage"] > 100_000:
            flags.append("⚠ high miles")
        price_num = _parse_price_int(lst.get("price") or "")
        if price_num and price_num < 8_000:
            flags.append("★ check price")
        flag_str = "  [" + ", ".join(flags) + "]" if flags else ""

        print(
            f"{price:<14} {year:<5} {mileage:<12} "
            f"{engine:<38} {location:<22} {source:<12} {url}{flag_str}"
        )

    print("\n* AutoTrader mileage server-filtered to ≤110,000 — exact figure on listing page")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ford Transit Connect EcoBlue van scraper")
    parser.add_argument("--format", choices=["json", "table"], default="table")
    parser.add_argument(
        "--sites", default="autotrader,gumtree",
        help="Comma-separated list: autotrader,gumtree"
    )
    parser.add_argument(
        "--pages", type=int, default=3,
        help="AutoTrader pages to fetch (default 3, ~75 results)"
    )
    args = parser.parse_args()

    sites = [s.strip().lower() for s in args.sites.split(",")]
    all_listings: list[dict] = []

    if "autotrader" in sites:
        print("Querying AutoTrader UK (GraphQL)...", file=sys.stderr)
        at = scrape_autotrader(max_pages=args.pages)
        print(f"  {len(at)} EcoBlue listing(s)", file=sys.stderr)
        all_listings.extend(at)

    if "gumtree" in sites:
        time.sleep(1)
        print("Scraping Gumtree...", file=sys.stderr)
        gt = scrape_gumtree()
        print(f"  {len(gt)} EcoBlue listing(s)", file=sys.stderr)
        all_listings.extend(gt)

    all_listings = deduplicate(all_listings)
    all_listings = sort_by_price(all_listings)

    if args.format == "table":
        print_table(all_listings)
    else:
        print(json.dumps(all_listings, indent=2))


if __name__ == "__main__":
    main()
