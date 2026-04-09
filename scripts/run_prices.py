"""
run_prices.py — ABE daily cash price check.

Fetches today's Iowa corn and soybean cash prices via USDA AMS MARS,
compares to yesterday's cached prices, and reports any significant moves.

Usage:
  python3 run_prices.py

Output (JSON to stdout):
  {
    "date": "2026-04-07",
    "corn":     { "price": 4.20, "prev": 4.05, "delta": 0.15, "significant": true },
    "soybeans": { "price": 10.81, "prev": 10.75, "delta": 0.06, "significant": false },
    "any_significant": true
  }

Significant threshold: >= 0.05 $/bu move in either direction.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from nass_api import get_iowa_cash_prices

_DATA_DIR   = Path(__file__).parent.parent / "data"
_CACHE_FILE = _DATA_DIR / "prices_cache.json"

# Alert if price moves by this many dollars per bushel or more
SIGNIFICANT_THRESHOLD = 0.05


def load_cache() -> dict:
    if _CACHE_FILE.exists():
        with open(_CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(data: dict) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_prices(mars_results: list) -> dict:
    """Extract corn and soybean prices from get_iowa_cash_prices() output."""
    prices = {}
    for row in mars_results:
        label = row.get("label", "")
        try:
            value = float(row.get("value", 0))
        except (ValueError, TypeError):
            continue
        if label == "corn_cash_iowa":
            prices["corn"] = value
        elif label == "soybean_cash_iowa":
            prices["soybeans"] = value
    return prices


if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")

    mars_results = get_iowa_cash_prices()
    today_prices = parse_prices(mars_results)

    if not today_prices:
        print(json.dumps({"error": "Could not fetch today's cash prices."}))
        sys.exit(1)

    cache = load_cache()
    prev_prices = cache.get("prices", {})

    output = {
        "date": today,
        "any_significant": False,
    }

    for commodity in ["corn", "soybeans"]:
        today_val = today_prices.get(commodity)
        prev_val  = prev_prices.get(commodity)

        if today_val is None:
            output[commodity] = {"error": "price unavailable"}
            continue

        delta = round(today_val - prev_val, 4) if prev_val is not None else None
        significant = abs(delta) >= SIGNIFICANT_THRESHOLD if delta is not None else False

        output[commodity] = {
            "price":       today_val,
            "prev":        prev_val,
            "delta":       delta,
            "significant": significant,
        }

        if significant:
            output["any_significant"] = True

    # Save today's prices for tomorrow's comparison
    save_cache({"date": today, "prices": today_prices})

    print(json.dumps(output, indent=2))
