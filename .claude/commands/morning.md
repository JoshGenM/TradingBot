---
description: Run the morning workflow manually (research + trade execution). Uses local .env credentials.
---

Run the morning research and trade execution workflow using local credentials from .env.

This mirrors routines/morning.md exactly, but reads credentials from the local .env file
instead of process environment variables. No git commit or push at the end — local mode only.

Follow all steps in routines/morning.md:
- STEP 1: Read memory files
- STEP 2: Pull live account state
- STEP 3: Perplexity research queries
- STEP 4: Write dated RESEARCH-LOG entry
- STEP 5: Validate and execute trades (buy-side gate)
- STEP 6: Place 10% trailing stops on new positions
- STEP 7: Append trades to TRADE-LOG
- STEP 8: ClickUp notification if trade placed

Skip the git commit/push steps — this is a local ad-hoc run.
