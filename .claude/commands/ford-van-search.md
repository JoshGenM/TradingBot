---
description: Search UK listing sites for Ford Transit Connect vans (2018+, ≤110k miles, EcoBlue diesel)
---

Search AutoTrader UK and Motors.co.uk for Ford Transit Connect EcoBlue vans.

Criteria hard-coded in the scraper:
- Make/Model: Ford Transit Connect
- Year: 2018 or newer
- Mileage: ≤110,000 miles
- Engine: EcoBlue diesel (filtered by keyword match)

Steps:

1. Run the scraper:
   ```
   bash scripts/van-scraper.sh --format=table
   ```

2. Present the results as a clean markdown table with columns:
   Price | Year | Mileage | Engine | Location | Source | Link

3. Sort by price ascending (scraper already does this).

4. After the table, add a brief summary:
   - Total listings found
   - Sites searched
   - Price range (lowest → highest)
   - Flag any listing with mileage >100,000 as "high miles — inspect carefully"
   - Flag any listing priced under £10,000 as "unusually low — verify condition"

5. If the scraper returns zero results, say:
   "No EcoBlue listings found right now — try again later or check the sites directly."
   Then provide direct search links to autotrader.co.uk and motors.co.uk with the
   pre-filled filters.

6. If the scraper errors or is blocked, explain the issue briefly and suggest
   the user visit the sites directly.
