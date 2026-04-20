# Workflow Documentation

Detailed breakdown of what the bot does on each run.

---

## Morning Run — 8:30 AM CT (Mon–Fri)

**Purpose**: Research today's market, identify trade opportunities, execute approved trades.

**Cron**: `30 8 * * 1-5` (America/Chicago)

**Cloud routine prompt**: `routines/morning.md`

**Local slash command**: `/morning`

### Steps

**1. Read memory**
- `memory/TRADING-STRATEGY.md` — loads all rules and stock filters
- `memory/TRADE-LOG.md` (last 100 lines) — checks current positions and weekly trade count
- `memory/RESEARCH-LOG.md` (last 50 lines) — reviews recent research context

**2. Pull live account state**
```bash
bash scripts/alpaca.sh account     # equity, cash, buying power, daytrade count
bash scripts/alpaca.sh positions   # all open positions with unrealized P&L
bash scripts/alpaca.sh orders      # open orders including trailing stops
```

**3. Research via Perplexity** (~6–8 queries)
- S&P 500 futures pre-market
- VIX level and market sentiment
- Top large-cap catalysts today (earnings beats, upgrades, sector news)
- S&P 500 sector momentum rankings
- Economic calendar (CPI, FOMC, jobs data)
- News on each currently held ticker

**4. Write research log entry**
Appends a dated section to `memory/RESEARCH-LOG.md` with:
- Account snapshot
- Market context summary
- 2–3 trade ideas (each with catalyst, quality filter check, entry/stop/target, R:R)
- Risk factors
- Decision: TRADE or HOLD (default is HOLD)

**5. Execute trades** (only if TRADE decision)
- Re-validates each planned ticker with fresh quotes
- Runs the full buy-side gate (all 8 checks must pass)
- Places market buy orders
- Immediately places 10% trailing stop GTC for each fill

**6. Update trade log**
Appends each executed trade to `memory/TRADE-LOG.md`

**7. Notify**
Sends a ClickUp message only if a trade was placed. Silent otherwise.

**8. Commit and push**
```bash
git add memory/RESEARCH-LOG.md memory/TRADE-LOG.md
git commit -m "morning research + trades YYYY-MM-DD"
git push origin master
```

---

## Evening Run — 3:30 PM CT (Mon–Fri)

**Purpose**: Manage open positions, enforce stop rules, record EOD snapshot. On Fridays, also run the weekly review.

**Cron**: `30 15 * * 1-5` (America/Chicago)

**Cloud routine prompt**: `routines/evening.md`

**Local slash command**: `/evening`

### Steps

**1. Read memory**
- `memory/TRADING-STRATEGY.md` — exit rules and stop-tightening thresholds
- `memory/TRADE-LOG.md` — entries, thesis per position, yesterday's EOD equity
- Today's `memory/RESEARCH-LOG.md` — morning thesis for each position

**2. Pull end-of-day state**
```bash
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders
```

**3. Cut losers** (–7% rule)
For any position with unrealized P&L ≤ –7%:
```bash
bash scripts/alpaca.sh close SYM
bash scripts/alpaca.sh cancel ORDER_ID
```
Logs exit price, realized P&L, and "cut at –7% per rule" to TRADE-LOG.

**4. Tighten stops on winners**
- Up ≥ +20%: cancel old stop, place new trailing stop at 5%
- Up ≥ +15%: cancel old stop, place new trailing stop at 7%
- Never tighten within 3% of current price

**5. Thesis check**
Reviews each position's original catalyst against today's news. If thesis is broken, closes the position even if not at –7% yet.

**6. Set PDT-blocked stops**
If any stops were queued from the morning run due to PDT restrictions, places them now.

**7. Compute EOD metrics**
- Day P&L = today's equity – yesterday's closing equity
- Phase cumulative P&L = today's equity – starting equity
- Trades placed today and this week

**8. Write EOD snapshot**
Appends a dated EOD snapshot table to `memory/TRADE-LOG.md`

**8b. Friday only — Weekly Review**
- Reads all week's TRADE-LOG and RESEARCH-LOG entries
- Queries Perplexity for S&P 500 weekly return
- Computes: week return, win rate, profit factor, best/worst trade
- Appends full review to `memory/WEEKLY-REVIEW.md`
- Updates `memory/TRADING-STRATEGY.md` if any rule needs changing

**9. Send ClickUp summary**
Always sends one message, even on no-trade days. Under 15 lines.
On Friday includes week grade and S&P comparison.

**10. Commit and push** (mandatory — tomorrow's P&L math depends on this)
```bash
git add memory/TRADE-LOG.md memory/RESEARCH-LOG.md
git commit -m "EOD snapshot YYYY-MM-DD"
git push origin master
```

---

## Ad-hoc Commands (Local Only)

### `/portfolio`
Read-only snapshot. No orders, no file changes.
- Prints account equity, cash, buying power
- Lists all open positions with entry price, current price, unrealized P&L, stop
- Lists all open orders
- Flags any position without a stop or with a stop below current price

### `/trade SYMBOL SHARES buy|sell`
Manual trade helper with full rule validation.
- Runs the complete buy-side gate
- Prints validation results
- Asks for confirmation before placing
- Places the order and immediately sets a 10% trailing stop
- Logs to TRADE-LOG and sends ClickUp notification
- Refuses any trade that fails a rule check

### `/morning`
Same as the cloud morning routine but runs locally using `.env` credentials. No git push.

### `/evening`
Same as the cloud evening routine but runs locally using `.env` credentials. No git push.

---

## Notification Rules

The bot is intentionally quiet. You read important messages; you tune out noise.

| Run | Sends notification when |
|-----|------------------------|
| Morning | Only if a trade was placed |
| Evening | Always — one message, ≤15 lines |
| Evening (Friday) | Always — includes week grade and S&P comparison |

---

## What Happens When Something Goes Wrong

| Problem | What the bot does |
|---------|------------------|
| Perplexity API key missing | Falls back to Claude's native WebSearch, flags in log |
| ClickUp credentials missing | Appends message to `DAILY-SUMMARY.md` locally, continues |
| Alpaca rejects trailing stop (PDT) | Falls back to fixed stop; if also blocked, queues for evening |
| Git push fails (divergence) | Runs `git pull --rebase` then pushes again |
| Morning research log missing at market open | Runs research inline before executing any trades |
| Partial failure mid-run | Next run reads live Alpaca positions and reconciles |
