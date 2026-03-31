"""
skills/crop-margin-simulator/scripts/crop_margin.py

Integration layer for the Crop Margin Simulator skill.

Imports the existing financial engine and NASS module without modifying either.
Exposes one public function (run_crop_margin) and the OpenClaw tool definition (TOOL).

Price resolution order (when no price_override is given):
  1. USDA AMS MARS  — today's Iowa cash bid (live API, no CSV fallback)
  2. CSV fallback   — mars_fallback.csv from last successful MARS fetch
  3. USDA NASS      — latest Iowa annual price received (live API, no CSV fallback)
  4. CSV fallback   — nass_fallback.csv from last successful NASS fetch
  5. ISU baseline   — corn $4.35/bu, soybeans $9.80/bu  (ISU AgDM A1-20 2024)

Why we call with use_fallback_on_error=False then load the CSV explicitly:
  abe.py uses use_fallback_on_error=True on both APIs, which silently merges the
  CSV into the result. We need to distinguish "USDA NASS" from "CSV fallback" as
  a price_source string, so we separate the two steps ourselves.
"""

import sqlite3
import sys
from pathlib import Path
from typing import Optional

# ── Path setup ─────────────────────────────────────────────────────────────────
# File lives at:  ABE/skills/crop-margin-simulator/scripts/crop_margin.py
# parents[0] = scripts/
# parents[1] = crop-margin-simulator/
# parents[2] = skills/
# parents[3] = ABE/  ← project root
ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(ROOT))   # for scripts.nass_api
# calculator.py lives in the same scripts/ directory — no extra path needed

# ── Import existing modules — do not modify these files ───────────────────────
from scripts.nass_api import (                          # noqa: E402
    get_iowa_cash_prices,
    get_iowa_data,
    load_mars_fallback,
    load_fallback,
)
from calculator import calculate_margin         # noqa: E402

# ── Constants ──────────────────────────────────────────────────────────────────
DATA_DIR            = ROOT / "data"          # ABE/data/  — all databases live here
ABE_DB              = DATA_DIR / "abe.db"    # A1-20 aggregate costs (seeded by scripts/seed_costs.py)
ISU_BASELINE        = {"corn": 4.35, "soybeans": 9.80}
DEFAULT_RENTAL_RATE = 230.0   # ISU Extension Iowa statewide average (2024)

_CASH_LABEL = {"corn": "corn_cash_iowa",  "soybeans": "soybean_cash_iowa"}
_NASS_LABEL = {"corn": "corn_price_iowa", "soybeans": "soybean_price_iowa"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _find_value(rows: list, label: str):
    """Return the float value for the first row matching label, or None."""
    for r in rows:
        if r.get("label") == label:
            try:
                return float(r["value"])
            except (KeyError, ValueError, TypeError):
                return None
    return None


def _resolve_price(crop: str) -> tuple[float, str]:
    """
    Walk the price waterfall and return (price, price_source).
    price_source is exactly one of:
        'USDA AMS MARS' | 'USDA NASS' | 'CSV fallback' | 'ISU baseline'
    """
    cash_label = _CASH_LABEL[crop]
    nass_label = _NASS_LABEL[crop]

    # 1. MARS live
    try:
        val = _find_value(get_iowa_cash_prices(use_fallback_on_error=False), cash_label)
        if val is not None:
            return val, "USDA AMS MARS"
    except Exception:
        pass

    # 2. MARS CSV fallback
    try:
        val = _find_value(load_mars_fallback(), cash_label)
        if val is not None:
            return val, "CSV fallback"
    except Exception:
        pass

    # 3. NASS annual live
    try:
        val = _find_value(get_iowa_data(use_fallback_on_error=False), nass_label)
        if val is not None:
            return val, "USDA NASS"
    except Exception:
        pass

    # 4. NASS CSV fallback
    try:
        val = _find_value(load_fallback(), nass_label)
        if val is not None:
            return val, "CSV fallback"
    except Exception:
        pass

    # 5. ISU A1-20 baseline
    return ISU_BASELINE[crop], "ISU baseline"


# ── Public function ────────────────────────────────────────────────────────────

def run_crop_margin(
    crop: str,
    acres: float,
    county: str,
    price_override: float = None,
    farmer_costs: Optional[dict] = None,
) -> dict:
    """
    Estimate net margin for an Iowa corn or soybean operation.

    Args:
        crop:         "corn" or "soybeans" (case-insensitive).
        acres:        Total acres in the operation.
        county:       Iowa county (passed through to output; not used in math).
        price_override: If provided, use this $/bu instead of fetching live data.
        farmer_costs: Optional dict of {category: actual_cost_per_acre}. The
                      farmer's real $/acre for any input they know. The delta
                      vs. the ISU benchmark is computed inside calculate_margin.
                      Unknown categories are ignored.

    Returns:
        Dict with 12 keys:
            crop, county, acres, price_per_bu, price_source,
            gross_revenue, total_cost, net_margin,
            cost_source, yield_bu_per_acre, year,
            cost_adjustments_applied

    Raises:
        ValueError: crop is not "corn" or "soybeans".
        FileNotFoundError: data/abe.db not found (run scripts/seed_costs.py first).
    """
    crop = crop.strip().lower()
    if crop not in ("corn", "soybeans"):
        raise ValueError("crop must be 'corn' or 'soybeans'")

    # ── 1. Load ISU A1-20 yield from data/abe.db ──────────────────────────────
    # We use A1-20 yield (corn: 202 bu/acre, soybeans: 54 bu/acre) rather than
    # the ISU_BENCHMARK hardcodes in calculator.py (200 / 55) because A1-20 2024
    # is the authoritative source we seeded.
    if not ABE_DB.exists():
        raise FileNotFoundError(
            f"data/abe.db not found at {ABE_DB}. Run scripts/seed_costs.py first."
        )

    with sqlite3.connect(ABE_DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT expected_yield_bu, year "
            "FROM a1_20_costs WHERE crop = ? AND region = 'iowa_statewide'",
            (crop,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"No A1-20 data for '{crop}' in data/abe.db. "
            "Run scripts/seed_costs.py first."
        )

    expected_yield = row["expected_yield_bu"]
    a1_20_year     = row["year"]

    # ── 2. Resolve price ───────────────────────────────────────────────────────
    if price_override is not None:
        price        = float(price_override)
        price_source = "farmer override"
    else:
        price, price_source = _resolve_price(crop)

    # ── 3. Call the existing financial engine — no math performed here ─────────
    result = calculate_margin(
        crop=crop,
        acres=acres,
        yield_bu=expected_yield,
        price_per_bu=price,
        rental_rate=DEFAULT_RENTAL_RATE,
        farmer_costs=farmer_costs,
    )

    # ── 4. Return exactly 11 keys ──────────────────────────────────────────────
    # gross_revenue and total_cost are operation totals (per-acre × acres).
    # net_margin_total is already computed by the engine.
    # The multiplications below are unit conversions only — all underlying
    # financial math was performed inside calculate_margin().
    return {
        "crop":              result.crop,
        "county":            county,
        "acres":             result.acres,
        "price_per_bu":      result.price_per_bu,
        "price_source":      price_source,
        "gross_revenue":     round(result.gross_revenue_per_acre * result.acres, 2),
        "total_cost":        round(result.total_cost_per_acre    * result.acres, 2),
        "net_margin":        result.net_margin_total,
        "cost_source":              result.source,
        "yield_bu_per_acre":        result.yield_bu,
        "year":                     result.data_year,
        "farmer_cost_overrides":    result.farmer_cost_overrides,
    }


# ── OpenClaw tool definition ───────────────────────────────────────────────────
# Matches the Anthropic API tool dict format used in agent/abe.py.

TOOL = {
    "name": "crop_margin_simulator",
    "description": (
        "Estimates net margin per acre and total profit or loss for an Iowa corn or "
        "soybean operation using ISU Extension cost-of-production data and live USDA "
        "NASS pricing. Use this skill when a farmer asks about profitability, whether "
        "a crop will pencil out, what they can expect to make this season, or whether "
        "their rent is too high relative to expected returns. Trigger phrases include: "
        '"will corn pencil out", "what\'s my margin on soybeans", "can I make money '
        'at this rent", "run my numbers", "what will I clear per acre". '
        "Do NOT trigger for general market price questions with no mention of costs, "
        "acres, or operations."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "crop": {
                "type": "string",
                "enum": ["corn", "soybeans"],
                "description": "The crop being evaluated.",
            },
            "acres": {
                "type": "number",
                "description": "Total acres in the operation.",
            },
            "county": {
                "type": "string",
                "description": "Iowa county name (e.g. 'Linn County').",
            },
            "price_override": {
                "type": "number",
                "description": (
                    "Price per bushel if the farmer wants to use their own price "
                    "instead of NASS data. Optional."
                ),
            },
            "farmer_costs": {
                "type": "object",
                "description": (
                    "Optional dict of {category: actual_$/acre} for any input cost the "
                    "farmer knows. Use the farmer's actual number — the delta vs. the ISU "
                    "benchmark is computed automatically. "
                    "Corn categories: 'seed', 'fertilizer', 'pesticide', 'machinery', "
                    "'labor', 'drying', 'crop_insurance', 'miscellaneous'. "
                    "Soybean categories: same except no 'drying'. "
                    "Unknown categories are ignored."
                ),
                "additionalProperties": {"type": "number"},
            },
        },
        "required": ["crop", "acres", "county"],
    },
    "handler": run_crop_margin,
}


# ── End-to-end test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    result = run_crop_margin(crop="corn", acres=100, county="Linn County")
    print(json.dumps(result, indent=2))
    print(f"\nPrice source used: {result['price_source']}")
