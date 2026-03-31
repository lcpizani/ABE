"""
run_rental.py — CLI wrapper for ABE's rental rate check skill.

Usage:
  python3 run_rental.py --county "Linn" --quality high
  python3 run_rental.py --county "Story" --quality medium --quoted 295

Queries abe.db cash_rent table and prints JSON result to stdout.
"""

import argparse
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "abe.db"

QUALITY_MAP = {
    "high": ("high_rent", "High quality third"),
    "medium": ("med_rent", "Medium quality third"),
    "low": ("low_rent", "Low quality third"),
}

def run(county: str, quality: str, quoted: float = None):
    quality = quality.strip().lower()
    if quality not in QUALITY_MAP:
        print(json.dumps({"error": f"quality must be high, medium, or low — got '{quality}'"}))
        return

    rent_col, quality_label = QUALITY_MAP[quality]

    if not DB_PATH.exists():
        print(json.dumps({"error": f"Database not found at {DB_PATH}"}))
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            f"""
            SELECT county, district, csr2_index,
                   avg_rent, high_rent, med_rent, low_rent,
                   corn_yield_avg, soy_yield_avg,
                   rent_per_csr2, source, year
            FROM cash_rent
            WHERE lower(county) = lower(?)
            """,
            (county.strip(),),
        ).fetchone()

    if row is None:
        print(json.dumps({"error": f"No data found for county '{county}'. Check spelling."}))
        return

    benchmark = row[rent_col]
    result = {
        "county": row["county"],
        "quality_tier": quality_label,
        "benchmark_avg": row["avg_rent"],
        "benchmark_high": row["high_rent"],
        "benchmark_med": row["med_rent"],
        "benchmark_low": row["low_rent"],
        "tier_benchmark": benchmark,
        "csr2_index": row["csr2_index"],
        "rent_per_csr2": row["rent_per_csr2"],
        "source": f"{row['source']}",
        "year": row["year"],
    }

    if quoted is not None:
        result["quoted_rate"] = quoted
        if quoted > row["high_rent"]:
            result["verdict"] = "above_range"
            result["verdict_label"] = f"Above the high end of the range (${row['high_rent']}/acre)"
        elif quoted > row["avg_rent"]:
            result["verdict"] = "above_average"
            result["verdict_label"] = f"Above average (${row['avg_rent']}/acre) but within range"
        elif quoted >= row["med_rent"]:
            result["verdict"] = "at_average"
            result["verdict_label"] = f"At or near the average (${row['avg_rent']}/acre)"
        else:
            result["verdict"] = "below_average"
            result["verdict_label"] = f"Below average (${row['avg_rent']}/acre)"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--county", required=True)
    parser.add_argument("--quality", required=True, choices=["high", "medium", "low"])
    parser.add_argument("--quoted", type=float, default=None)
    args = parser.parse_args()
    run(args.county, args.quality, args.quoted)
