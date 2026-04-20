# Full Setup Guide

Step-by-step instructions to get the trading bot running from scratch.

---

## Step 1 — Accounts & API Keys

You need four services. Sign up for each before proceeding.

### Alpaca (trading)
1. Go to [alpaca.markets](https://alpaca.markets) and create a free account
2. Start with **Paper Trading** — no real money at risk while testing
3. Go to **Paper Trading → API Keys → Generate New Key**
4. Save your **API Key ID** and **Secret Key**
5. Paper trading endpoint: `https://paper-api.alpaca.markets/v2`
6. When ready for live trading, generate Live API keys and switch the endpoint to `https://api.alpaca.markets/v2`

### Perplexity (research)
1. Go to [perplexity.ai](https://perplexity.ai) and sign in
2. Click your profile icon → **Settings → API**
3. Click **Generate** to create an API key (format: `pplx-xxxx`)
4. Add a credit card and load a minimum balance (~$5 lasts 5+ months)

### ClickUp (notifications)
1. Go to [clickup.com](https://clickup.com) and create a free account
2. In the left sidebar, click **Chat** → **+ New Channel**
3. Name it "Trading Bot" (or anything you like)
4. Your **Workspace ID**: visible in the URL — `app.clickup.com/`**`90121659000`**`/...`
5. Your **Channel ID**: open the channel → `...` menu → **Copy link** → the ID after `/chat/r/` in the URL

### GitHub (memory storage)
1. Go to [github.com](https://github.com) and create a free account
2. Create a **new private repository** (no README, no .gitignore — we provide these)
3. Note your repo URL: `https://github.com/USERNAME/REPONAME.git`

---

## Step 2 — Local Setup

```bash
# Clone your repo
git clone https://github.com/USERNAME/REPONAME.git
cd REPONAME

# Make scripts executable
chmod +x scripts/*.sh

# Set up credentials
cp env.template .env
```

Edit `.env` and fill in all values:
```
ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2
ALPACA_DATA_ENDPOINT=https://data.alpaca.markets/v2
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
PERPLEXITY_API_KEY=pplx-your_key_here
PERPLEXITY_MODEL=sonar
CLICKUP_API_KEY=pk_your_key_here
CLICKUP_WORKSPACE_ID=your_workspace_id
CLICKUP_CHANNEL_ID=your_channel_id
```

---

## Step 3 — Smoke Tests

Run these to verify each integration works before going live.

### Test Alpaca
```bash
bash scripts/alpaca.sh account
```
You should see your paper account equity, cash, and buying power in JSON.

### Test Perplexity
```bash
bash scripts/perplexity.sh "What is the S&P 500 doing today?"
```
You should see a JSON response with a cited answer.

### Test ClickUp
```bash
bash scripts/clickup.sh "Test message from trading bot"
```
Check your ClickUp Chat channel — the message should appear within seconds.

---

## Step 4 — Local Manual Run

Open this repo in **Claude Code** (desktop or VS Code extension) and run:

```
/portfolio
```

You should see a clean account snapshot. If it works, try:

```
/morning
```

This runs the full morning workflow manually using your local `.env` credentials (no git push at the end in local mode).

---

## Step 5 — Cloud Routines Setup

This is the production path. Cloud routines fire automatically on a schedule.

### One-time prerequisites

**Install the Claude GitHub App:**
1. Go to Claude Code settings → GitHub → Install App
2. Select only your trading bot repo (least privilege)
3. Grant both read and write access

### Create the Morning Routine
1. Go to [claude.ai/code](https://claude.ai/code) → **Routines → New Routine**
2. Fill in:
   - **Name**: `Trading Bot Morning`
   - **Repository**: your GitHub repo
   - **Branch**: `master`
   - **Cron schedule**: `30 8 * * 1-5`
   - **Timezone**: `America/Chicago`
3. Add all 9 environment variables (same values as your `.env`)
4. Toggle **"Allow unrestricted branch pushes"** → ON
5. **Prompt**: open `routines/morning.md`, select all, paste verbatim
6. Save

### Create the Evening Routine
Repeat the above with:
- **Name**: `Trading Bot Evening`
- **Cron schedule**: `30 15 * * 1-5`
- **Prompt**: contents of `routines/evening.md`

### Test Both Routines
Click **"Run now"** on each routine immediately after creating it. Watch the logs. Verify:
- Morning: a new dated entry appears in `memory/RESEARCH-LOG.md` on GitHub
- Evening: a new EOD snapshot appears in `memory/TRADE-LOG.md` on GitHub
- Both: a ClickUp message arrives in your channel

Do not wait for the first scheduled run to discover a problem.

---

## Step 6 — Go Live

When paper trading results are satisfactory:
1. Generate Live API keys on Alpaca
2. Update `ALPACA_ENDPOINT` to `https://api.alpaca.markets/v2` in both the cloud routine env vars and your local `.env`
3. Update `memory/PROJECT-CONTEXT.md` with your starting capital and start date
4. Seed `memory/TRADE-LOG.md` with a Day 0 EOD snapshot reflecting your actual starting equity

---

## Cron Schedule Reference

All times are **America/Chicago (CT)**. US markets open at 8:30 AM CT and close at 3:00 PM CT.

| Routine | Cron | Time | Purpose |
|---------|------|------|---------|
| Morning | `30 8 * * 1-5` | 8:30 AM Mon–Fri | Research + trade execution |
| Evening | `30 15 * * 1-5` | 3:30 PM Mon–Fri | Position management + EOD summary |

The evening routine automatically detects Friday and runs the weekly review in the same session.
