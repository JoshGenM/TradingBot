# Trading Strategy

## Mission
Beat the S&P 500. Stocks only — no options, ever.
Stance: moderately aggressive — pursue quality growth opportunities in established companies.
Do NOT chase speculative or high-risk plays. Discipline and patience beat overtrading.

## Capital & Constraints
- Platform: Alpaca
- Instruments: Stocks ONLY
- PDT limit: 3 day trades per 5 rolling business days (account < $25k)

## Stock Universe — Moderate-Aggressive Filter

### PREFERRED (all should ideally apply)
- Market cap > $2B (large-cap or mid-cap)
- Share price > $10
- Avg daily volume > 1M shares (liquid)
- Stock in established uptrend: trading above its 50-day moving average
- Clear near-term catalyst: earnings beat, analyst upgrade, sector rotation, macro tailwind
- Sectors with current momentum: Technology, Healthcare, Financials, Industrials, Consumer Discretionary

### AVOID (any one of these = skip the trade)
- Market cap < $500M (micro-cap / small-cap risk)
- Share price < $10 (penny stock behavior)
- Short interest > 25% (squeeze risk, manipulable)
- Same-day binary events: FDA approval/rejection, buying on earnings release day
- Meme stocks, Reddit-driven plays, stocks with no fundamental story
- Sectors in confirmed multi-week downtrends
- Stocks with less than 6 months of trading history

## Core Rules
1. NO OPTIONS — ever
2. 70-80% capital deployed (leave some cash buffer for opportunities)
3. Maximum 4-5 open positions at a time
4. Maximum 20% of equity per position
5. 10% trailing stop on every position as a real GTC order placed immediately after fill
6. Cut losers at -7% from entry — no hoping, no averaging down
7. Tighten trailing stop to 7% when position is up +15%
8. Tighten trailing stop to 5% when position is up +20%
9. Never tighten a stop to within 3% of current price
10. Never move a stop down — only up
11. Maximum 3 new trades per week
12. Follow sector momentum — don't force a thesis if sector is rolling over
13. Exit an entire sector after 2 consecutive failed trades in that sector
14. Patience > activity — a week with zero trades can be correct

## Entry Checklist (document ALL before placing any order)
- What is the specific catalyst today?
- Does the stock pass the quality filter? (market cap, price, volume, uptrend)
- Is the sector in momentum (not rolling over)?
- What is the stop level? (7-10% below entry)
- What is the target? (minimum 2:1 risk/reward ratio)
- Is this a binary-event play? (if yes, skip)
- What is short interest? (if >25%, skip)

## Buy-Side Gate (ALL must pass — skip and log reason if any fail)
1. Total positions after this fill <= 5
2. Total trades placed this week (including this one) <= 3
3. Position cost <= 20% of account equity
4. Position cost <= available cash
5. daytrade_count < 3 (PDT rule: sub-$25k account)
6. Catalyst documented in today's RESEARCH-LOG entry
7. Stock passes quality filter (market cap, price, volume, uptrend, not binary-event)
8. Instrument is a stock (not leveraged ETF, not any option)

## Sell-Side Rules (evaluated in evening run)
- Unrealized loss <= -7%: close immediately, no exceptions
- Thesis broken (catalyst gone, sector turning, surprise news): close even if not at -7% yet
- Up >= +20%: cancel old trailing stop, place new one at 5%
- Up >= +15%: cancel old trailing stop, place new one at 7%
- Sector has 2 consecutive failed trades: exit all positions in that sector

## Schedule
- Morning run: 8:30 AM CT weekdays (research + execution at market open)
- Evening run: 3:30 PM CT weekdays (position management + EOD summary + Friday weekly review)
