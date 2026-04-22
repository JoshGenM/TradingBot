---
description: Search UK listing sites for Ford Transit Connect vans (2018+, ≤110k miles, EcoBlue diesel)
---

Search AutoTrader UK and Gumtree for Ford Transit Connect EcoBlue vans.
Hard-coded criteria: Ford Transit Connect, 2018 or newer, ≤110,000 miles, EcoBlue diesel engine.

1. Run the scraper:
   bash scripts/van-scraper.sh --format=table --pages=3

2. Present results as a clean markdown table:
   | Price | Year | Mileage | Engine/Spec | Location | Source | Link |

3. Results come pre-sorted by price ascending. Present them that way.

4. After the table, summarise:
   - Total listings found (AutoTrader N, Gumtree N)
   - Price range: lowest → highest
   - Flag any listing with mileage >100,000 as "high miles — inspect carefully"
   - Flag any listing priced under £8,000 as "unusually low — verify condition"
   - Note: AutoTrader mileage is server-filtered to ≤110k (exact figure on individual listing page)

5. If the scraper returns zero results:
   "No EcoBlue listings found right now — try again later or check directly:"
   - AutoTrader: https://www.autotrader.co.uk/van-search?make=Ford&model=Transit%20Connect&year-from=2018&maximum-mileage=110000&keywords=EcoBlue
   - Gumtree: https://www.gumtree.com/search?search_category=vans&q=ford+transit+connect+ecoblue&vehicle_make=ford&vehicle_model=ford-transit-connect

6. If the scraper errors (e.g. bot protection or network issue), say:
   "Scraper blocked or offline — visit the links above directly."
   Do not retry automatically.
