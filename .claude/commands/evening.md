---
description: Run the evening workflow manually (position management + EOD summary). Uses local .env credentials.
---

Run the evening position management and EOD summary workflow using local credentials from .env.

This mirrors routines/evening.md exactly, but reads credentials from the local .env file
instead of process environment variables. No git commit or push at the end — local mode only.

Follow all steps in routines/evening.md:
- STEP 1: Read memory files
- STEP 2: Pull end-of-day account state
- STEP 3: Cut losers at -7%
- STEP 4: Tighten stops on winners
- STEP 5: Thesis check — close broken theses
- STEP 6: Set any PDT-blocked stops from morning
- STEP 7: Compute EOD metrics
- STEP 8: Append EOD snapshot to TRADE-LOG
- STEP 8b: If Friday, run weekly review
- STEP 9: Send ClickUp EOD message

Skip the git commit/push steps — this is a local ad-hoc run.
