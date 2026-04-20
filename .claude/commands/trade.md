---
description: Manual trade helper with full strategy-rule validation. Usage: /trade SYMBOL SHARES buy|sell
---

Execute a manual trade with full rule validation. Refuse if any rule fails.

Args: SYMBOL SHARES SIDE (buy or sell). If missing, ask before proceeding.

1. Pull state:
   bash scripts/alpaca.sh account
   bash scripts/alpaca.sh positions
   bash scripts/alpaca.sh quote SYMBOL    # capture ask price P

2. For BUY, validate ALL of the following (stop and print failed checks if any fail):
   - Total positions after fill <= 5
   - Trades this week + 1 <= 3
   - SHARES * P <= 20% of equity
   - SHARES * P <= available cash
   - daytrade_count < 3
   - Market cap > $2B (ask user if unknown)
   - Price > $10/share
   - NOT a same-day binary event play
   - Short interest < 25% (ask user if unknown)
   - Catalyst documented (ask for thesis if not already stated)
   If any check fails, STOP. Print all failed checks. Do not proceed.

3. For SELL, confirm position exists with correct qty. No other checks needed.

4. Print the order JSON and all validation results. Ask: "Execute? (y/n)"

5. On confirm "y":
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy","type":"market","time_in_force":"day"}'

6. For BUYs only — immediately place 10% trailing stop GTC:
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"sell","type":"trailing_stop","trail_percent":"10","time_in_force":"gtc"}'
   PDT fallback to fixed stop if rejected. Queue if also blocked.

7. Append to memory/TRADE-LOG.md with full thesis, entry price, stop level, target, R:R.

8. bash scripts/clickup.sh with trade details (one line summary).
