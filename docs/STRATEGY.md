# Trading Strategy Documentation

Full explanation of every rule, why it exists, and how it is enforced.

---

## Philosophy

This is a **moderately aggressive swing trading strategy** for stocks only.

- **Moderately aggressive** means we pursue quality growth opportunities in established companies with clear catalysts. We do not chase meme stocks, penny stocks, or speculative plays.
- **Swing trading** means holding positions for days to weeks — not day trading, not buy-and-hold.
- **Disciplined** means hard rules enforced programmatically. The agent cannot override them.

---

## Stock Universe

Only trade stocks that pass ALL of these filters:

| Filter | Requirement | Why |
|--------|------------|-----|
| Market cap | >$2B (large or mid-cap) | Liquidity, stability, less manipulation |
| Share price | >$10 | Penny stocks have erratic behavior |
| Avg daily volume | >1M shares | Ensures easy entry and exit |
| Trend | Above 50-day moving average | Don't fight the trend |
| Short interest | <25% | Avoid squeeze risk and manipulated stocks |
| Binary events | None same day | No FDA decisions, no buying on earnings day |
| History | >6 months trading | New listings are unpredictable |

**Preferred sectors** (currently in momentum):
- Technology
- Healthcare
- Financials
- Industrials
- Consumer Discretionary

**Avoid entirely**: meme stocks, micro-caps, penny stocks, highly shorted names, crypto-adjacent stocks.

---

## Position Sizing

| Rule | Value | Why |
|------|-------|-----|
| Max open positions | 4–5 | Concentration gives better returns; too many dilutes edge |
| Max per position | 20% of equity | Limits single-stock disaster |
| Capital deployed | 70–80% | Keep cash buffer for opportunities and emergencies |
| Max new trades/week | 3 | Prevents overtrading and PDT rule violations |

### Example on a $10,000 account
- Max position size: $2,000 (20%)
- Target deployed: $7,000–$8,000
- Cash buffer: $2,000–$3,000

---

## Entry Rules

Every trade requires ALL of the following documented before placing an order:

1. **Specific catalyst** — what is happening TODAY that makes this stock move?
   - Earnings beat, analyst upgrade, product launch, sector rotation, macro tailwind
   - "It looks good" is not a catalyst
2. **Sector check** — is the sector in momentum or rolling over?
3. **Stop level** — 7–10% below entry price
4. **Target** — minimum 2:1 risk/reward ratio
   - If stop is 8% below entry, target must be at least 16% above entry
5. **Quality filter passed** — all filters from the Stock Universe section above

### The Buy-Side Gate

Before any order is placed, ALL of these must pass:

- [ ] Total positions after fill ≤ 5
- [ ] Total trades this week ≤ 3
- [ ] Position cost ≤ 20% of account equity
- [ ] Position cost ≤ available cash
- [ ] Daytrade count < 3 (PDT rule for sub-$25k accounts)
- [ ] Catalyst documented in today's research log
- [ ] Stock passes all quality filters
- [ ] Instrument is a stock (not an option, not a leveraged ETF)

If any check fails, the trade is skipped and the reason is logged.

---

## Stop Loss Rules

**Every position gets a real trailing stop order placed on Alpaca immediately after the fill.** Never a mental stop.

### Default stop: 10% trailing
```json
{"symbol":"XOM","qty":"12","side":"sell","type":"trailing_stop","trail_percent":"10","time_in_force":"gtc"}
```

### PDT fallback: fixed stop
If Alpaca rejects the trailing stop due to pattern day trader rules:
```json
{"symbol":"XOM","qty":"12","side":"sell","type":"stop","stop_price":"140.00","time_in_force":"gtc"}
```

### Stop tightening (winners)
| Position gain | Action |
|--------------|--------|
| +15% or more | Cancel old stop, place new trailing stop at 7% |
| +20% or more | Cancel old stop, place new trailing stop at 5% |

**Guard rail**: Never tighten a stop to within 3% of current price. Never move a stop down.

---

## Exit Rules

Evaluated every evening run and opportunistically:

| Trigger | Action |
|---------|--------|
| Unrealized loss ≤ –7% | Close immediately. No exceptions. No hoping. |
| Thesis broken | Close even if not at –7% yet |
| Up ≥ +20% | Tighten trailing stop to 5% |
| Up ≥ +15% | Tighten trailing stop to 7% |
| 2 consecutive failed trades in a sector | Exit all positions in that sector |

### What "thesis broken" means
- The catalyst that prompted the buy has been invalidated
- Unexpected bad news for the company
- The sector is visibly rolling over
- A macro event changes the setup entirely

---

## Pattern Day Trader (PDT) Rule

For accounts under $25,000:
- Maximum 3 day trades per 5 rolling business days
- A "day trade" = buying and selling the same stock on the same day

**How the bot handles it:**
- Checks `daytrade_count` from Alpaca before every buy
- Uses trailing stops (GTC) rather than same-day stops to avoid PDT issues
- Fallback ladder: trailing stop → fixed stop → queue stop for next morning

---

## Weekly Discipline

- Max 3 new trades per week — enforced by counting entries in TRADE-LOG dated that week
- A week with zero trades is perfectly acceptable — patience beats overtrading
- Weekly review every Friday evaluates performance and adjusts strategy if needed

---

## Risk Management Summary

| Risk | Mitigation |
|------|-----------|
| Single stock blowup | 20% position cap, –7% hard stop |
| Overtrading | 3 trades/week cap |
| Sector concentration | 2-strike sector exit rule |
| Market crash | 20–30% cash buffer, trailing stops |
| Speculative plays | Stock quality filter (market cap, price, volume) |
| Emotion-driven trades | Hard rules enforced programmatically, not by judgment |
