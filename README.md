# Trading Bot

An autonomous AI trading bot built on Claude Code that runs twice daily, managing a swing trading portfolio on Alpaca. Moderately aggressive strategy focused on large/mid-cap stocks with clear catalysts.

## How It Works

Claude is the bot. Every scheduled run spins up a fresh Claude Code cloud container that:
1. Clones this repo to read memory
2. Pulls live account state from Alpaca
3. Researches market conditions via Perplexity
4. Makes trade decisions based on hard strategy rules
5. Places orders and manages stops on Alpaca
6. Writes results back to memory files, commits, and pushes to this repo
7. Sends a notification to ClickUp

All state lives in the `memory/` folder as markdown files committed to `master`.

## Schedule

| Run | Time | What It Does |
|-----|------|-------------|
| Morning | 8:30 AM CT (Mon–Fri) | Market research + trade execution |
| Evening | 3:30 PM CT (Mon–Fri) | Position management + EOD summary + Friday weekly review |

## Strategy

**Moderately aggressive — quality stocks only.**

- Stocks only. No options. Ever.
- Large/mid-cap stocks only (market cap >$2B, price >$10, avg vol >1M/day)
- No penny stocks, meme stocks, binary-event plays, or short interest >25%
- Max 4–5 open positions, max 20% of equity per position
- Max 3 new trades per week
- 70–80% capital deployed
- 10% trailing stop on every position (real GTC order, not mental)
- Cut losers at –7% — no exceptions
- Tighten stop to 7% at +15%, to 5% at +20%
- Exit a sector after 2 consecutive failed trades
- Patience > activity

Full rules: [`memory/TRADING-STRATEGY.md`](memory/TRADING-STRATEGY.md)

## Repository Layout

```
trading-bot/
├── CLAUDE.md                  # Agent rulebook — auto-loaded every session
├── env.template               # Template for local .env (never commit .env)
├── .gitignore
├── .claude/
│   └── commands/              # Local slash commands for manual runs
│       ├── portfolio.md       # /portfolio — read-only account snapshot
│       ├── trade.md           # /trade — manual trade with rule validation
│       ├── morning.md         # /morning — run morning workflow locally
│       └── evening.md        # /evening — run evening workflow locally
├── routines/                  # Cloud routine prompts (paste into Claude Code UI)
│   ├── morning.md             # cron: 30 8 * * 1-5
│   └── evening.md             # cron: 30 15 * * 1-5
├── scripts/                   # API wrappers — all external calls go through here
│   ├── alpaca.sh              # Alpaca trading API
│   ├── perplexity.sh          # Perplexity research API
│   └── clickup.sh             # ClickUp notifications
└── memory/                    # Agent's persistent state (committed to master)
    ├── TRADING-STRATEGY.md    # The rulebook
    ├── TRADE-LOG.md           # Every trade + daily EOD snapshots
    ├── RESEARCH-LOG.md        # Daily morning research entries
    ├── WEEKLY-REVIEW.md       # Friday performance recaps
    └── PROJECT-CONTEXT.md     # Static background and mission
```

## Setup

### Prerequisites
- Alpaca account (paper to start: [alpaca.markets](https://alpaca.markets))
- Perplexity API key ([perplexity.ai](https://perplexity.ai))
- ClickUp account with a Chat channel for notifications
- Claude Code with cloud routines access

### Local Setup
1. Clone this repo
2. Copy `env.template` to `.env` and fill in your credentials
3. Run `chmod +x scripts/*.sh`
4. Smoke test: open repo in Claude Code and run `/portfolio`

### Cloud Routines Setup
1. Install the Claude GitHub App on this repo
2. In Claude Code → Routines → New Routine, create two routines:
   - **Morning**: paste `routines/morning.md`, cron `30 8 * * 1-5`, timezone `America/Chicago`
   - **Evening**: paste `routines/evening.md`, cron `30 15 * * 1-5`, timezone `America/Chicago`
3. Add all environment variables to each routine (see `env.template` for the full list)
4. Enable **"Allow unrestricted branch pushes"** on both routines
5. Hit **"Run now"** to test before the first scheduled run

### Environment Variables
```
ALPACA_ENDPOINT
ALPACA_DATA_ENDPOINT
ALPACA_API_KEY
ALPACA_SECRET_KEY
PERPLEXITY_API_KEY
PERPLEXITY_MODEL
CLICKUP_API_KEY
CLICKUP_WORKSPACE_ID
CLICKUP_CHANNEL_ID
```

> Never commit your `.env` file. Credentials for cloud routines are set directly in the Claude Code routine config — not in any file.

## Memory Model

The `memory/` folder is the bot's only state between runs. Every run reads from `master` and writes back to `master` via git commit. This gives free versioning, diffs, rollback, and a human-readable audit trail.

| File | Updated |
|------|---------|
| `TRADING-STRATEGY.md` | Friday only, if a rule changes |
| `TRADE-LOG.md` | Every trade + every EOD |
| `RESEARCH-LOG.md` | Every morning |
| `WEEKLY-REVIEW.md` | Every Friday evening |
| `PROJECT-CONTEXT.md` | Rarely |

## Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| Perplexity API (~160 requests) | ~$0.80 |
| Alpaca | Free (paper) / commission-free (live) |
| ClickUp | Free tier sufficient |
| Claude Code routines | Included in Claude plan |
