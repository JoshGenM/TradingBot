#!/usr/bin/env bash
# Ford Transit Connect EcoBlue van scraper — UK listing sites.
# Usage: bash scripts/van-scraper.sh [--format=table|json] [--sites=autotrader,motors]
# No credentials required. Public web scraping only.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Ensure Python dependencies are available
if ! python3 -c "import requests, bs4" 2>/dev/null; then
  echo "Installing required Python packages..." >&2
  pip3 install -q requests beautifulsoup4
fi

python3 "$ROOT/scripts/van_scraper.py" "$@"
echo
