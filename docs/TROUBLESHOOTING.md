# Troubleshooting Guide

Common problems and fixes.

---

## Cloud Routine Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Repository not accessible" / clone fails | Claude GitHub App not installed | Install it, grant access to this specific repo |
| `git push` fails with proxy/permission error | "Allow unrestricted branch pushes" is off | Enable it in the routine's environment settings |
| `ALPACA_API_KEY not set in environment` | Env var missing from routine config | Add it in the routine's environment — NOT in a `.env` file |
| Agent creates a `.env` file | Prompt was modified — lost the "DO NOT create .env" block | Re-paste prompt from `routines/*.md` verbatim |
| Yesterday's trades missing from today's run | Previous run didn't commit+push | Check `git log` on GitHub. Verify STEP 9 of the prompt is intact |
| Push fails "fetch first" / non-fast-forward | Another run pushed between clone and push | Prompt handles this with `git pull --rebase`. Check for actual merge conflict |
| ClickUp message didn't arrive | One of the three `CLICKUP_*` vars is missing | Script falls back to `DAILY-SUMMARY.md`. Add the missing vars to the routine |
| Perplexity calls didn't happen | `PERPLEXITY_API_KEY` missing | Script exits 3, agent falls back to WebSearch. Add the key or accept fallback |
| Alpaca rejects stop with PDT error | Same-day stop on same-day buy | Prompt's fallback ladder handles this. If not cascading, re-paste STEP 5 verbatim |

---

## Local Setup Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ALPACA_API_KEY not set` running locally | `.env` file missing or not in repo root | Copy `env.template` to `.env` and fill in credentials |
| Scripts not executable | Missing execute permission | Run `chmod +x scripts/*.sh` |
| `python3: command not found` | Python not installed | Install Python 3: [python.org](https://python.org) |
| `curl: command not found` | curl not installed | Install curl via your OS package manager |
| `/portfolio` shows wrong account | Wrong `ALPACA_ENDPOINT` | Check `.env` — paper is `paper-api.alpaca.markets`, live is `api.alpaca.markets` |

---

## Trading Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Buy order rejected | Insufficient buying power | Check `bash scripts/alpaca.sh account` — may be fully deployed |
| Trailing stop rejected | PDT rule violation | Fallback to fixed stop. Check `daytrade_count` in account response |
| Position closed at wrong price | Market gap through trailing stop | Trailing stops don't protect against overnight gaps — by design |
| Order stuck as "pending" | Low-liquidity stock | Check bid/ask spread with `bash scripts/alpaca.sh quote SYM` |
| Stop not cancelled after position closed | Race condition | Run `bash scripts/alpaca.sh cancel-all` to clean up orphaned orders |

---

## Memory / Git Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Research log entry missing | Morning run failed before STEP 9 | Check GitHub commit history. Re-run `/morning` locally to backfill |
| Duplicate EOD snapshot | Evening run ran twice | Delete the duplicate section manually and push a cleanup commit |
| Merge conflict in memory files | Two runs pushed at the same time (don't schedule this way) | Resolve conflict manually, keeping both entries, and push |
| Trade in Alpaca but not in TRADE-LOG | Run failed mid-way after order placement | Next run reconciles by reading live positions. Add manual entry if needed |

---

## Checking Logs

```bash
# See all commits the bot has made
git log --oneline origin/master

# See what changed in the last commit
git show HEAD

# See the full research log
cat memory/RESEARCH-LOG.md

# See recent trades
tail -100 memory/TRADE-LOG.md

# Check if a stop order exists for a position
bash scripts/alpaca.sh orders
```

---

## Emergency Commands

```bash
# See everything open right now
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders

# Cancel ALL open orders (e.g. to remove all stops before manual intervention)
bash scripts/alpaca.sh cancel-all

# Close a specific position immediately (market sell)
bash scripts/alpaca.sh close AAPL

# Close ALL positions immediately
bash scripts/alpaca.sh close-all
```

> **Warning**: `close-all` will market-sell every open position immediately. Use only in emergencies.
