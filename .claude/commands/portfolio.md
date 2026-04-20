---
description: Read-only snapshot of account, positions, open orders, and stops
---

Print a clean ad-hoc portfolio snapshot. No state changes, no orders, no file writes.

1. bash scripts/alpaca.sh account
2. bash scripts/alpaca.sh positions
3. bash scripts/alpaca.sh orders

Format output as:

Portfolio — <today's date>
Equity: $X | Cash: $X (X%) | Buying power: $X
Daytrade count: N | PDT warning: <yes/no>

Positions:
  SYM | Shares | Entry -> Now | Unrealized P&L | Stop type | Stop level

Open orders:
  TYPE | SYM | qty | trail%/stop_price | order_id

No commentary unless something is broken:
- Flag any position with no stop order
- Flag any stop price that is below current price
- Flag any position where unrealized loss is approaching -7%
