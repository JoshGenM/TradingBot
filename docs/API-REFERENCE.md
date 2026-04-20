# API Reference

Documentation for all three wrapper scripts in `scripts/`.

---

## scripts/alpaca.sh

Wraps the Alpaca v2 REST API. All trading calls go through this script.

### Authentication
Reads `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` from environment (or `.env` if present).
Translates to HTTP headers: `APCA-API-KEY-ID` and `APCA-API-SECRET-KEY`.

### Endpoints
- Trading: `ALPACA_ENDPOINT` (default: `https://api.alpaca.markets/v2`)
- Market data: `ALPACA_DATA_ENDPOINT` (default: `https://data.alpaca.markets/v2`)

### Commands

```bash
# Account info — equity, cash, buying_power, daytrade_count
bash scripts/alpaca.sh account

# All open positions with unrealized P&L
bash scripts/alpaca.sh positions

# Single position
bash scripts/alpaca.sh position AAPL

# Latest quote (bid/ask) — uses data endpoint
bash scripts/alpaca.sh quote AAPL

# Orders (default: open)
bash scripts/alpaca.sh orders
bash scripts/alpaca.sh orders all
bash scripts/alpaca.sh orders closed

# Place a new order
bash scripts/alpaca.sh order '<json>'

# Cancel a specific order
bash scripts/alpaca.sh cancel ORDER_ID

# Cancel all open orders
bash scripts/alpaca.sh cancel-all

# Close (market-sell) a position
bash scripts/alpaca.sh close AAPL

# Close all positions
bash scripts/alpaca.sh close-all
```

### Order JSON Shapes

```jsonc
// Market buy (day — expires at close if unfilled)
{"symbol":"AAPL","qty":"10","side":"buy","type":"market","time_in_force":"day"}

// 10% trailing stop (default for every new position)
{"symbol":"AAPL","qty":"10","side":"sell","type":"trailing_stop","trail_percent":"10","time_in_force":"gtc"}

// Tightened trailing stop at +15%
{"symbol":"AAPL","qty":"10","side":"sell","type":"trailing_stop","trail_percent":"7","time_in_force":"gtc"}

// Tightened trailing stop at +20%
{"symbol":"AAPL","qty":"10","side":"sell","type":"trailing_stop","trail_percent":"5","time_in_force":"gtc"}

// Fixed stop (PDT fallback — 10% below entry)
{"symbol":"AAPL","qty":"10","side":"sell","type":"stop","stop_price":"153.00","time_in_force":"gtc"}
```

### Important Gotchas

| Gotcha | Details |
|--------|---------|
| `trail_percent` is a string | Use `"10"` not `10` in JSON |
| `qty` is also a string | Use `"10"` not `10` |
| Two base URLs | `data.alpaca.markets` for quotes; `api.alpaca.markets` for everything else |
| Quote shape | `quote.ap` = ask price, `quote.bp` = bid price |
| Wide spread = skip | If bid/ask spread is wide or zero, stock may be halted or illiquid |
| Trailing stops = market hours only | Overnight gaps can blow right through them |
| Alpaca timestamps = UTC | Convert to local time carefully |

### PDT Rule
- 3 day trades per 5 rolling business days on accounts under $25k
- Check `daytrade_count` from the `account` command before placing any buy
- Same-day stops on same-day buys can be rejected — use the fallback ladder

---

## scripts/perplexity.sh

Wraps the Perplexity Chat Completions API for market research.

### Authentication
Reads `PERPLEXITY_API_KEY` from environment. Exits with code 3 if unset (allows graceful fallback to WebSearch).

### Usage

```bash
bash scripts/perplexity.sh "<query>"
```

### Examples

```bash
bash scripts/perplexity.sh "S&P 500 futures premarket today"
bash scripts/perplexity.sh "VIX level right now"
bash scripts/perplexity.sh "Top large-cap stock catalysts today — earnings upgrades sector news"
bash scripts/perplexity.sh "Latest news for NVDA today"
bash scripts/perplexity.sh "S&P 500 weekly performance week ending 2025-05-02"
```

### Configuration

| Env var | Default | Notes |
|---------|---------|-------|
| `PERPLEXITY_API_KEY` | required | Get from perplexity.ai → Settings → API |
| `PERPLEXITY_MODEL` | `sonar` | The standard search model — cheapest option |

### Fallback behaviour
If `PERPLEXITY_API_KEY` is not set, the script prints a warning to stderr and exits with code 3.
The bot catches this and falls back to Claude's native WebSearch, noting the fallback in the research log.

### Pricing (sonar model)
- ~$0.005 per request
- ~$1 per 1M input tokens
- ~$1 per 1M output tokens
- Estimated monthly cost: **~$0.80** at 2 runs/day

---

## scripts/clickup.sh

Posts notifications to a ClickUp Chat channel.

### Authentication
Reads `CLICKUP_API_KEY`, `CLICKUP_WORKSPACE_ID`, and `CLICKUP_CHANNEL_ID` from environment.

### Usage

```bash
bash scripts/clickup.sh "Your message here"

# Multi-line (use quotes)
bash scripts/clickup.sh "Line 1
Line 2
Line 3"
```

### Configuration

| Env var | Format | Where to find |
|---------|--------|--------------|
| `CLICKUP_API_KEY` | `pk_XXXXXXXX_...` | ClickUp → Settings → Apps → API Token |
| `CLICKUP_WORKSPACE_ID` | numeric | URL: `app.clickup.com/`**90121659000** |
| `CLICKUP_CHANNEL_ID` | `2kxuprkr-832` | Chat channel → `...` → Copy link |

### Fallback behaviour
If any of the three ClickUp credentials are missing, the script:
1. Appends the message to `DAILY-SUMMARY.md` in the repo root
2. Prints `[clickup fallback] appended to DAILY-SUMMARY.md`
3. Exits 0 (does not crash the run)

This means the bot never fails due to missing notification credentials.

### Message format tips
- Keep messages under 15 lines for readability
- Use markdown — ClickUp Chat renders it
- Lead with the date and portfolio value on EOD messages
