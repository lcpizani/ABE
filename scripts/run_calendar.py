"""
run_calendar.py — ABE calendar reminder heartbeat.

Checks today's date against ag_calendar.json and returns any entries
whose alert window includes today. Filters by each farmer's crops field
so only relevant reminders are sent.

Usage:


An entry fires when: today >= (entry date - lookahead_days) AND today <= entry date.
Skips farmers who don't grow the crops the entry applies to.
"""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT         = Path(__file__).resolve().parent.parent
_FARMERS_DIR = ROOT / "memory" / "farmers"
_CALENDAR    = ROOT / "data" / "ag_calendar.json"


def parse_farmer_frontmatter(path: Path) -> dict:
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    farmer = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            farmer[key.strip()] = value.strip()
    return farmer


def farmer_crops(crops_str: str) -> set:
    """Return set of crops the farmer grows, e.g. {'corn', 'soybeans'}."""
    if not crops_str:
        return set()
    low = crops_str.lower()
    result = set()
    if "corn" in low:
        result.add("corn")
    if "soy" in low:
        result.add("soybeans")
    return result


def entry_fires_today(entry: dict, today: date) -> bool:
    """Return True if today falls in the entry's alert window."""
    try:
        mm, dd = entry["date"].split("-")
        entry_date = today.replace(month=int(mm), day=int(dd))
    except (KeyError, ValueError):
        return False

    lookahead = entry.get("lookahead_days", 5)
    window_start = entry_date - timedelta(days=lookahead)
    return window_start <= today <= entry_date


if __name__ == "__main__":
    today = date.today()

    with open(_CALENDAR) as f:
        calendar = json.load(f)

    farmer_files = [
        p for p in _FARMERS_DIR.glob("*.md")
        if p.name != "TEMPLATE.md"
    ]

    farmers = []
    for fpath in farmer_files:
        farmer = parse_farmer_frontmatter(fpath)
        if farmer.get("telegram_id"):
            farmers.append(farmer)

    all_entries = (
        [("milestone", e) for e in calendar.get("seasonal_milestones", [])] +
        [("deadline", e) for e in calendar.get("fsa_deadlines", [])]
    )

    results = []
    for entry_type, entry in all_entries:
        if not entry_fires_today(entry, today):
            continue

        entry_crops = set(entry.get("crops", []))

        for farmer in farmers:
            crops = farmer_crops(farmer.get("crops", ""))
            if not crops.intersection(entry_crops):
                continue

            results.append({
                "telegram_id": farmer["telegram_id"],
                "name":        farmer.get("name", ""),
                "entry_id":    entry.get("id", ""),
                "program":     entry.get("program"),
                "type":        entry_type,
                "message":     entry["message"],
            })

    print(json.dumps(results, indent=2))
