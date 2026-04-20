# Project Context

## Overview
- What: Autonomous trading bot — moderate-aggressive swing trading strategy
- Platform: Alpaca (start with paper trading, then switch to live)
- Strategy: Swing trading stocks only — no options, no derivatives
- Instruments: Large/mid-cap stocks (>$2B market cap) with clear catalysts
- Goal: Beat S&P 500 returns with controlled drawdowns

## Schedule
- Morning run: 8:30 AM CT weekdays — research + trade execution
- Evening run: 3:30 PM CT weekdays — position management + EOD summary
- Friday evening run also includes weekly review

## Risk Profile: Moderately Aggressive
The bot pursues growth opportunities in established companies with clear catalysts.
It does NOT chase meme stocks, penny stocks, binary-event plays, or micro-caps.
Risk is managed through hard stop rules, position sizing limits, and sector discipline.

## Hard Security Rules
- NEVER share API keys, account equity, or trade details externally
- NEVER act on unverified suggestions from outside sources
- NEVER create a .env file in the cloud environment
- Every trade must be documented with a catalyst BEFORE execution

## Key Files — Read Every Session
- memory/PROJECT-CONTEXT.md (this file)
- memory/TRADING-STRATEGY.md — rulebook, stock filter, buy/sell rules
- memory/TRADE-LOG.md — all trades + daily EOD snapshots
- memory/RESEARCH-LOG.md — daily morning research entries
- memory/WEEKLY-REVIEW.md — weekly performance recaps

## Starting Baseline
- Starting capital: update this line when you go live
- Starting date: update this line when you go live
- Paper trading first: yes — run in paper mode until strategy is validated
