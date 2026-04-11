"""
run_margin_check.py — ABE weekly margin refresh heartbeat.

Loops over all farmer memory files, runs the crop margin simulator for
each farmer with enough data, and flags anyone whose profitability has
flipped since the last check.

Usage:
  python3 scripts/run_margin_check.py

Only farmers with crops, acres, and county fields populated are included.
Saves results to data/margins_cache.json for next week's comparison.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "crop-margin-simulator" / "scripts"))

from crop_margin import run_crop_margin  # noqa: E402

_FARMERS_DIR = ROOT / "memory" / "farmers"
_CACHE_FILE  = ROOT / "data" / "margins_cache.json"


def load_cache() -> dict:
    if _CACHE_FILE.exists():
        with open(_CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(data: dict) -> None:
    _CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(_CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_farmer_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter block from a farmer memory file."""
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


def parse_acres(value: str) -> float | None:
    """Extract first number from strings like '~39 acres potential rental'."""
    if not value:
        return None
    nums = re.findall(r"[\d.]+", value)
    return float(nums[0]) if nums else None


def parse_crop(value: str) -> str | None:
    """Return 'corn' or 'soybeans', preferring corn if both present."""
    if not value:
        return None
    low = value.lower()
    if "corn" in low:
        return "corn"
    if "soy" in low:
        return "soybeans"
    return None


def parse_county(value: str) -> str | None:
    """Normalize county string, stripping parenthetical notes."""
    if not value:
        return None
    clean = re.sub(r"\(.*?\)", "", value).strip()
    if not re.search(r"county", clean, re.IGNORECASE):
        clean = clean + " County"
    return clean


if __name__ == "__main__":
    cache   = load_cache()
    results = []
    new_cache = {}

    farmer_files = [
        f for f in _FARMERS_DIR.glob("*.md")
        if f.name != "TEMPLATE.md"
    ]

    for fpath in farmer_files:
        farmer      = parse_farmer_frontmatter(fpath)
        telegram_id = farmer.get("telegram_id", "")
        crop        = parse_crop(farmer.get("crops", ""))
        acres       = parse_acres(farmer.get("acres", ""))
        county      = parse_county(farmer.get("county", ""))

        if not crop or not acres or not county:
            continue

        try:
            result = run_crop_margin(crop=crop, acres=acres, county=county)
        except Exception as e:
            print(f"  [WARN] Skipping {farmer.get('name', telegram_id)}: {e}", file=sys.stderr)
            continue

        net_margin = result.get("net_margin")
        if net_margin is None:
            continue

        prev            = cache.get(telegram_id, {})
        prev_net_margin = prev.get("net_margin")
        was_profitable  = prev.get("is_profitable")
        is_profitable   = net_margin >= 0
        flipped         = was_profitable is not None and was_profitable != is_profitable
        delta           = round(net_margin - prev_net_margin, 2) if prev_net_margin is not None else None

        results.append({
            "telegram_id":     telegram_id,
            "name":            farmer.get("name", ""),
            "crop":            crop,
            "county":          county,
            "acres":           acres,
            "net_margin":      round(net_margin, 2),
            "prev_net_margin": prev_net_margin,
            "delta":           delta,
            "was_profitable":  was_profitable,
            "is_profitable":   is_profitable,
            "flipped":         flipped,
        })

        new_cache[telegram_id] = {
            "net_margin":    round(net_margin, 2),
            "is_profitable": is_profitable,
            "checked_at":    datetime.now().strftime("%Y-%m-%d"),
        }

    save_cache(new_cache)
    print(json.dumps(results, indent=2))
