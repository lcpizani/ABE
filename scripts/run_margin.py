"""
run_margin.py — CLI wrapper for ABE's crop margin simulator skill.

Estimates net margin per acre and total profit/loss for an Iowa corn or
soybean operation using ISU AgDM A1-20 benchmarks and live USDA pricing.

Usage:
  .venv/bin/python scripts/run_margin.py --crop corn --acres 500 --county "Linn County"
  .venv/bin/python scripts/run_margin.py --crop soybeans --acres 300 --county "Story County" --price 10.50
  .venv/bin/python scripts/run_margin.py --crop corn --acres 500 --county "Palo Alto County" \\
      --farmer-cost seed=95 --farmer-cost nitrogen=70

Arguments:
  --crop          corn or soybeans (required)
  --acres         Total acres (required)
  --county        Iowa county name, e.g. "Linn County" (required)
  --price         Price per bushel override (optional; uses live USDA data if omitted)
  --rent          Farmer's actual cash rent per acre (optional; defaults to ISU average $274)
  --farmer-cost   KEY=VALUE for any farmer input cost per acre (repeatable).
                  Corn keys:     seed, fertilizer, pesticide, machinery, labor,
                                 drying, crop_insurance, miscellaneous
                  Soybean keys:  same except no drying

Output: JSON margin report.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "crop-margin-simulator" / "scripts"))

from crop_margin import run_crop_margin


def parse_farmer_costs(cost_list: list[str]) -> dict:
    """Parse ['key=value', ...] into {key: float}."""
    out = {}
    for item in cost_list:
        if "=" not in item:
            print(f"Warning: ignoring malformed cost '{item}' (expected KEY=VALUE)", file=sys.stderr)
            continue
        k, v = item.split("=", 1)
        try:
            out[k.strip()] = float(v.strip())
        except ValueError:
            print(f"Warning: ignoring cost '{item}' — value is not a number", file=sys.stderr)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ABE Crop Margin Simulator")
    parser.add_argument("--crop",         required=True, choices=["corn", "soybeans"])
    parser.add_argument("--acres",        type=float, required=True)
    parser.add_argument("--county",       required=True)
    parser.add_argument("--price",        type=float, default=None,
                        help="Price per bushel override (omit to use live USDA data)")
    parser.add_argument("--rent",         type=float, default=None,
                        help="Farmer's actual cash rent per acre (omit to use ISU average $274)")
    parser.add_argument("--farmer-cost",  action="append", default=[],
                        metavar="KEY=VALUE",
                        help="Farmer input cost per acre. Repeatable.")
    args = parser.parse_args()

    farmer_costs = parse_farmer_costs(args.farmer_cost)

    try:
        result = run_crop_margin(
            crop           = args.crop,
            acres          = args.acres,
            county         = args.county,
            price_override = args.price,
            rental_rate    = args.rent,
            farmer_costs   = farmer_costs if farmer_costs else None,
        )
    except (ValueError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

    print(json.dumps(result, indent=2))
