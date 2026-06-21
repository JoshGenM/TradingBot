# Ford Transit Connect Van Scraper

A tool for scanning UK used-van listing sites for Ford Transit Connect EcoBlue vans matching a fixed set of criteria.

## Search Criteria

| Field  | Value                         |
|--------|-------------------------------|
| Make   | Ford                          |
| Model  | Transit Connect               |
| Year   | 2018 or newer                 |
| Mileage| ≤110,000 miles                |
| Engine | EcoBlue (diesel, keyword match)|

## Usage

### As a Claude slash command

```
/ford-van-search
```

Claude will run the scraper and present results as a formatted table with flags for high-mileage or unusually-cheap listings.

### Direct from the terminal

```bash
# Table output (human-readable)
bash scripts/van-scraper.sh --format=table

# JSON output (for further processing)
bash scripts/van-scraper.sh --format=json

# Restrict to one site
bash scripts/van-scraper.sh --format=table --sites=autotrader
bash scripts/van-scraper.sh --format=table --sites=motors
```

### Python script directly

```bash
python3 scripts/van_scraper.py --format=table
python3 scripts/van_scraper.py --format=json --sites=autotrader,motors
```

## Output

### Table format

```
Ford Transit Connect — EcoBlue — 2018+ — ≤110,000 miles
Found 12 listing(s)

Price    | Year | Mileage   | Engine                 | Location           | Source       | URL
------------------------------------------------------------------------------------------...
£11,500  | 2019 | 67,000    | 1.5 EcoBlue 100ps      | Manchester         | autotrader   | https://...
£12,950  | 2020 | 54,321    | 1.5L EcoBlue Diesel    | Birmingham         | motors.co.uk | https://... ★ low price
£18,750  | 2022 | 103,000   | EcoBlue Diesel         | London             | autotrader   | https://... ⚠ high miles
```

Flags:
- `⚠ high miles` — mileage over 100,000
- `★ low price` — price under £10,000 (verify condition)

### JSON format

Each listing:

```json
{
  "title": "Ford Transit Connect 1.5 EcoBlue 100ps L2 Trend Van",
  "year": 2020,
  "mileage": 54000,
  "price": "£12,950",
  "engine": "1.5L EcoBlue Diesel",
  "location": "Birmingham",
  "seller": "Van World Ltd",
  "url": "https://www.autotrader.co.uk/...",
  "source": "autotrader"
}
```

## Sites Scraped

| Site           | URL                                 | Notes                              |
|----------------|-------------------------------------|------------------------------------|
| AutoTrader UK  | autotrader.co.uk/van-search         | Primary source, largest UK database|
| Motors.co.uk   | motors.co.uk/search/van/ford/...    | Secondary source                   |

The scraper first attempts to extract listing data from each site's embedded `__NEXT_DATA__` JSON (Next.js SSR pattern), then falls back to BeautifulSoup HTML parsing if that fails.

## Dependencies

No credentials or API keys required. The scraper installs its own Python dependencies on first run:

```
requests
beautifulsoup4
```

The bash wrapper (`van-scraper.sh`) handles the install automatically.

## Troubleshooting

**"HTTP 403 — skipping"**: The site's bot detection blocked the request. Try again in a few minutes or use a different network. The scraper uses a realistic browser User-Agent but does not use proxies.

**"No listings found"**: Either no listings exist matching the criteria right now, or parsing failed due to a site redesign. Check the sites directly using the links below.

**Direct search links** (pre-filtered):
- [AutoTrader UK — Transit Connect EcoBlue 2018+](https://www.autotrader.co.uk/van-search?make=Ford&model=Transit%20Connect&year-from=2018&maximum-mileage=110000&fuel-type=Diesel)
- [Motors.co.uk — Transit Connect 2018+](https://www.motors.co.uk/search/van/ford/transit-connect/?year_from=2018&mileage_to=110000&fuel=diesel)
