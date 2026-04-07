"""
run_budget.py — CLI wrapper for ABE's budget planner skill.

Builds land investment scenarios from a fixed budget, pulling rent benchmarks
from abe.db and crop margins from the crop-margin-simulator skill.

Usage:
  python3 scripts/run_budget.py --budget 10000 --county "Story" --crop corn --intent rent
  python3 scripts/run_budget.py --budget 50000 --county "Linn" --crop soybeans --intent buy --down-payment-pct 0.20
  python3 scripts/run_budget.py --budget 15000 --county "Palo Alto" --crop corn --intent both

Arguments:
  --budget            Total dollars available (required)
  --county            Target Iowa county (required)
  --crop              corn or soybeans (required)
  --intent            rent, buy, or both (required)
  --quality           high, medium, or low land quality (default: medium)
  --interest-rate     Annual interest rate for buying scenario (default: 0.065)
  --down-payment-pct  Down payment as decimal for buying scenario (default: 0.20)
  --property-tax      Property tax per acre per year (default: 12.0)
  --cap-rate          Land cap rate for valuation (default: 0.035)

Output: JSON with one or more scenario objects.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "crop-margin-simulator" / "scripts"))

from crop_margin import run_crop_margin

DB_PATH = ROOT / "data" / "abe.db"

QUALITY_COL = {
    "high":   "high_rent",
    "medium": "med_rent",
    "low":    "low_rent",
}

YIELD_COL = {
    "corn":     "corn_yield_avg",
    "soybeans": "soy_yield_avg",
}


def fetch_county_row(county: str) -> dict:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM cash_rent WHERE lower(county) = lower(?)",
            (county.strip(),),
        ).fetchone()
    if row is None:
        raise ValueError(f"No data found for county '{county}'. Check spelling.")
    return dict(row)


def rent_scenario(budget: float, county_row: dict, crop: str, quality: str) -> dict:
    """How many acres can the farmer rent, and what is the season margin?"""
    rent_col  = QUALITY_COL[quality]
    rent      = county_row[rent_col]
    acres     = int(budget // rent)

    if acres == 0:
        return {
            "scenario": "rent",
            "quality":  quality,
            "error":    f"Budget of ${budget:,.0f} is too small to rent even one acre of "
                        f"{quality}-quality ground in {county_row['county']} (${rent}/acre).",
            "minimum_budget_needed": rent,
        }

    margin_result = run_crop_margin(crop=crop, acres=acres, county=county_row["county"])

    net_margin_per_acre = margin_result["net_margin"]
    # net_margin from run_crop_margin already excludes rent via ISU cost benchmarks;
    # we need to subtract rent explicitly as an additional land cost.
    net_after_rent = net_margin_per_acre - rent
    season_profit  = net_after_rent * acres

    return {
        "scenario":             "rent",
        "quality":              quality,
        "county":               county_row["county"],
        "crop":                 crop,
        "rent_per_acre":        rent,
        "affordable_acres":     acres,
        "budget_used":          rent * acres,
        "budget_remaining":     budget - (rent * acres),
        "yield_bu_per_acre":    margin_result["yield_bu_per_acre"],
        "price_per_bu":         margin_result["price_per_bu"],
        "price_source":         margin_result["price_source"],
        "gross_revenue_per_acre":   margin_result["gross_revenue"] / acres,
        "production_cost_per_acre": (margin_result["total_cost"] / acres) - rent,
        "rent_per_acre_explicit":   rent,
        "net_margin_per_acre":      round(net_after_rent, 2),
        "season_profit_total":      round(season_profit, 2),
        "cost_source":          margin_result["cost_source"],
        "rent_source":          f"{county_row['source']} {county_row['year']}",
    }


def buy_scenario(
    budget: float,
    county_row: dict,
    crop: str,
    quality: str,
    interest_rate: float,
    down_payment_pct: float,
    property_tax_per_acre: float,
    cap_rate: float,
) -> dict:
    """How many acres can the farmer buy, and what is the annual margin after financing?"""
    rent_col        = QUALITY_COL[quality]
    rent            = county_row[rent_col]
    land_value      = rent / cap_rate               # Iowa cap rate approach
    down_payment    = land_value * down_payment_pct
    loan_per_acre   = land_value - down_payment
    interest_per_acre = loan_per_acre * interest_rate
    annual_cost_per_acre = interest_per_acre + property_tax_per_acre

    acres = int(budget // down_payment)

    if acres == 0:
        return {
            "scenario": "buy",
            "quality":  quality,
            "error":    f"Budget of ${budget:,.0f} is not enough for a down payment on even one acre "
                        f"of {quality}-quality ground in {county_row['county']}. "
                        f"Estimated land value: ${land_value:,.0f}/acre. "
                        f"Down payment needed ({int(down_payment_pct*100)}%): ${down_payment:,.0f}/acre.",
            "land_value_per_acre":    round(land_value, 0),
            "down_payment_per_acre":  round(down_payment, 0),
            "minimum_budget_needed":  round(down_payment, 0),
        }

    margin_result = run_crop_margin(crop=crop, acres=acres, county=county_row["county"])

    net_margin_per_acre = margin_result["net_margin"]
    # Buying replaces rent with financing + property tax as the land holding cost.
    net_after_financing = net_margin_per_acre - annual_cost_per_acre
    season_profit       = net_after_financing * acres

    return {
        "scenario":                 "buy",
        "quality":                  quality,
        "county":                   county_row["county"],
        "crop":                     crop,
        "land_value_per_acre":      round(land_value, 0),
        "cap_rate_used":            cap_rate,
        "down_payment_pct":         down_payment_pct,
        "down_payment_per_acre":    round(down_payment, 0),
        "affordable_acres":         acres,
        "total_down_payment":       round(down_payment * acres, 0),
        "budget_remaining":         round(budget - (down_payment * acres), 0),
        "loan_per_acre":            round(loan_per_acre, 0),
        "interest_rate":            interest_rate,
        "interest_cost_per_acre":   round(interest_per_acre, 2),
        "property_tax_per_acre":    property_tax_per_acre,
        "annual_land_cost_per_acre": round(annual_cost_per_acre, 2),
        "yield_bu_per_acre":        margin_result["yield_bu_per_acre"],
        "price_per_bu":             margin_result["price_per_bu"],
        "price_source":             margin_result["price_source"],
        "gross_revenue_per_acre":   margin_result["gross_revenue"] / acres,
        "production_cost_per_acre": margin_result["total_cost"] / acres,
        "net_margin_per_acre":      round(net_after_financing, 2),
        "season_profit_total":      round(season_profit, 2),
        "cost_source":              margin_result["cost_source"],
        "rent_benchmark_for_valuation": rent,
        "rent_source":              f"{county_row['source']} {county_row['year']}",
        "note": (
            "Buying builds equity over time — annual margin alone does not capture "
            "the full return. Land appreciation and loan paydown are not included here."
        ),
    }


def run(
    budget: float,
    county: str,
    crop: str,
    intent: str,
    quality: str = "medium",
    interest_rate: float = 0.065,
    down_payment_pct: float = 0.20,
    property_tax: float = 12.0,
    cap_rate: float = 0.035,
) -> dict:
    crop   = crop.strip().lower()
    intent = intent.strip().lower()
    quality = quality.strip().lower()

    if crop not in ("corn", "soybeans"):
        return {"error": f"crop must be 'corn' or 'soybeans' — got '{crop}'"}
    if intent not in ("rent", "buy", "both"):
        return {"error": f"intent must be 'rent', 'buy', or 'both' — got '{intent}'"}
    if quality not in QUALITY_COL:
        return {"error": f"quality must be high, medium, or low — got '{quality}'"}

    try:
        county_row = fetch_county_row(county)
    except (FileNotFoundError, ValueError) as e:
        return {"error": str(e)}

    scenarios = []

    if intent in ("rent", "both"):
        scenarios.append(rent_scenario(budget, county_row, crop, quality))

    if intent in ("buy", "both"):
        scenarios.append(buy_scenario(
            budget, county_row, crop, quality,
            interest_rate, down_payment_pct, property_tax, cap_rate,
        ))

    return {
        "budget":    budget,
        "county":    county_row["county"],
        "crop":      crop,
        "intent":    intent,
        "quality":   quality,
        "scenarios": scenarios,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ABE Budget Planner")
    parser.add_argument("--budget",           type=float, required=True)
    parser.add_argument("--county",           required=True)
    parser.add_argument("--crop",             required=True, choices=["corn", "soybeans"])
    parser.add_argument("--intent",           required=True, choices=["rent", "buy", "both"])
    parser.add_argument("--quality",          default="medium", choices=["high", "medium", "low"])
    parser.add_argument("--interest-rate",    type=float, default=0.065)
    parser.add_argument("--down-payment-pct", type=float, default=0.20)
    parser.add_argument("--property-tax",     type=float, default=12.0)
    parser.add_argument("--cap-rate",         type=float, default=0.035)
    args = parser.parse_args()

    result = run(
        budget           = args.budget,
        county           = args.county,
        crop             = args.crop,
        intent           = args.intent,
        quality          = args.quality,
        interest_rate    = args.interest_rate,
        down_payment_pct = args.down_payment_pct,
        property_tax     = args.property_tax,
        cap_rate         = args.cap_rate,
    )
    print(json.dumps(result, indent=2))
