"""
run_crop_progress.py — ABE weekly crop progress report.

Fetches the latest Iowa crop progress data from USDA NASS and formats
a plain-English summary for ABE to send to farmers.

Only runs during growing season (April through October).

Usage:
  .venv/bin/python scripts/run_crop_progress.py

Output (JSON to stdout):
  {
    "in_season": true,
    "week_ending": "2026-05-11",
    "records": [...],
    "summary": {
      "corn": "Iowa corn is 62% planted as of the week ending May 11.",
      "soybeans": "Iowa soybeans are 18% planted as of the week ending May 11."
    }
  }

If out of season, returns { "in_season": false } and exits without fetching.
"""

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.nass_api import get_iowa_crop_progress  # noqa: E402

# Only run during growing season
_GROWING_SEASON_MONTHS = {4, 5, 6, 7, 8, 9, 10}

# Human-readable category labels extracted from NASS short_desc strings
_CATEGORY_LABELS = {
    "PCT PLANTED":    "planted",
    "PCT EMERGED":    "emerged",
    "PCT SILKING":    "silking",
    "PCT DOUGHING":   "in dough stage",
    "PCT DENTED":     "dented",
    "PCT MATURE":     "mature",
    "PCT HARVESTED":  "harvested",
    "PCT BLOOMING":   "blooming",
    "PCT SETTING PODS": "setting pods",
    "PCT DROPPING LEAVES": "dropping leaves",
    "PCT COLORING":   "coloring",
}


def parse_category(short_desc: str) -> str:
    """Extract a human-readable label from a NASS short_desc string."""
    upper = short_desc.upper()
    for key, label in _CATEGORY_LABELS.items():
        if key in upper:
            return label
    # Fallback: strip the commodity prefix and lowercase
    parts = short_desc.split(" - ", 1)
    return parts[-1].strip().lower() if len(parts) > 1 else short_desc.lower()


def build_summary(records: list) -> dict:
    """Build a per-commodity plain-English summary sentence."""
    by_commodity = {}
    for r in records:
        commodity = r.get("commodity", "")
        if commodity not in by_commodity:
            by_commodity[commodity] = []
        by_commodity[commodity].append(r)

    summaries = {}
    for commodity, rows in by_commodity.items():
        row = rows[0]
        week = row.get("week_ending", "this week")
        value = row.get("value", "?")
        category = parse_category(row.get("category", ""))

        try:
            week_label = date.fromisoformat(week).strftime("%B %-d")
        except ValueError:
            week_label = week

        summaries[commodity] = (
            f"Iowa {commodity} is {value}% {category} "
            f"as of the week ending {week_label}."
        )

    return summaries


if __name__ == "__main__":
    today = date.today()

    if today.month not in _GROWING_SEASON_MONTHS:
        print(json.dumps({"in_season": False}))
        sys.exit(0)

    records = get_iowa_crop_progress()

    if not records:
        print(json.dumps({"error": "Could not fetch crop progress data."}))
        sys.exit(1)

    week_ending = records[0].get("week_ending", "N/A")
    summary = build_summary(records)

    print(json.dumps({
        "in_season":   True,
        "week_ending": week_ending,
        "records":     records,
        "summary":     summary,
    }, indent=2))
