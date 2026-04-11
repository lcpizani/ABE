"""
run_cost_production.py — CLI wrapper for ABE's cost-of-production skill.

Calculates a full, line-by-line cost breakdown for an Iowa corn or soybean
operation using ISU AgDM A1-20 2026 benchmarks, with optional farmer overrides.

Usage:
  python3 scripts/run_cost_production.py --crop corn --acres 500
  python3 scripts/run_cost_production.py --crop corn --acres 500 --rotation following_corn --tier low
  python3 scripts/run_cost_production.py --crop soybeans --acres 300 --price 10.50
  python3 scripts/run_cost_production.py --crop corn --acres 500 --price 4.50 \\
      --override seed=95 --override nitrogen=70 --override cash_rent=250

Arguments:
  --crop        corn or soybeans (required)
  --acres       Total acres (required)
  --rotation    following_soybeans | following_corn | silage (default: following_soybeans for corn, following_corn for soybeans)
  --tier        low | mid | high (default: mid)
  --price       Expected price per bushel (optional, for net-return calculation)
  --override    KEY=VALUE pair for any farmer cost override (repeatable).
                Keys: seed, nitrogen, phosphate, potash, lime, herbicide,
                crop_insurance, miscellaneous, interest, labor, cash_rent,
                drying, haul, combine, grain_cart, handle, preharvest

Output: JSON cost report.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "cost-of-production" / "scripts"))

from cost_calculator import calculate_cost, CostResult


def result_to_dict(r: CostResult) -> dict:
    sections_out = {}
    for name, sec in r.sections.items():
        sections_out[name] = {
            "fixed_per_acre":    sec.fixed_per_acre,
            "variable_per_acre": sec.variable_per_acre,
            "total_per_acre":    sec.total_per_acre,
            "pct_of_total":      sec.pct_of_total,
        }

    items_out = [
        {
            "section":          li.section,
            "cost_item":        li.cost_item,
            "cost_type":        li.cost_type,
            "units_quantity":   li.units_quantity,
            "cost_per_acre":    li.cost_per_acre,
            "isu_benchmark":    li.isu_cost_per_acre,
            "is_overridden":    li.is_overridden,
            "savings_per_acre": li.savings_per_acre if li.is_overridden else None,
        }
        for li in r.line_items
    ]

    return {
        "crop":                   r.crop,
        "rotation":               r.budget_type,
        "acres":                  r.acres,
        "yield_tier":             r.yield_tier,
        "yield_bu_per_acre":      r.yield_bu,
        "price_per_bu":           r.price_per_bu,
        "fixed_per_acre":         r.fixed_per_acre,
        "variable_per_acre":      r.variable_per_acre,
        "total_per_acre":         r.total_per_acre,
        "total_per_bushel":       r.total_per_bushel,
        "total_operation":        r.total_operation,
        "gross_revenue_per_acre": r.gross_revenue_per_acre,
        "net_return_per_acre":    r.net_return_per_acre,
        "net_return_total":       r.net_return_total,
        "sections":               sections_out,
        "line_items":             items_out,
        "overrides_applied":      r.overrides_applied,
        "data_year":              r.data_year,
        "source":                 r.source,
    }


def parse_overrides(override_list: list[str]) -> dict:
    """Parse ['key=value', ...] into {key: float}."""
    out = {}
    for item in override_list:
        if "=" not in item:
            print(f"Warning: ignoring malformed override '{item}' (expected KEY=VALUE)", file=sys.stderr)
            continue
        k, v = item.split("=", 1)
        try:
            out[k.strip()] = float(v.strip())
        except ValueError:
            print(f"Warning: ignoring override '{item}' — value is not a number", file=sys.stderr)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ABE Cost-of-Production Calculator")
    parser.add_argument("--crop",     required=True, choices=["corn", "soybeans"])
    parser.add_argument("--acres",    type=float, required=True)
    parser.add_argument("--rotation", default=None,
                        choices=["following_soybeans", "following_corn", "silage"])
    parser.add_argument("--tier",     default="mid", choices=["low", "mid", "high"])
    parser.add_argument("--price",    type=float, default=None,
                        help="Expected price per bushel (for net-return calc)")
    parser.add_argument("--override", action="append", default=[],
                        metavar="KEY=VALUE",
                        help="Farmer cost override. Repeatable. E.g. --override seed=95")
    args = parser.parse_args()

    # Default rotation by crop
    rotation = args.rotation
    if rotation is None:
        rotation = "following_soybeans" if args.crop == "corn" else "following_corn"

    overrides = parse_overrides(args.override)

    try:
        result = calculate_cost(
            crop             = args.crop,
            acres            = args.acres,
            rotation         = rotation,
            yield_tier       = args.tier,
            price_per_bu     = args.price,
            farmer_overrides = overrides if overrides else None,
        )
    except (ValueError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

    print(json.dumps(result_to_dict(result), indent=2))
