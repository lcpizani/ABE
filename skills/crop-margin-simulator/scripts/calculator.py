"""
margin_calculator — ABE skill

Public API
----------
calculate_margin(crop, acres, yield_bu, price_per_bu, rental_rate) -> MarginResult

How the calculation works
-------------------------
Step 1 — Load ISU production costs from abe.db
    SELECT category, cost_per_acre FROM crop_costs WHERE crop = ?
    Costs are seeded from ISU Extension "Estimated Costs of Crop Production
    in Iowa" (A1-20, 2024) and cover seed, fertilizer, chemicals, machinery,
    drying, insurance, and overhead — everything except land rent.

Step 2 — Apply farmer cost overrides (optional)
    If farmer_costs is provided, each {category: actual_$/acre} replaces
    the ISU value for that category. The delta (farmer − ISU) is computed
    here — the caller only needs to know what the farmer actually pays.
    Unknown categories are ignored. The ISU benchmark comparison is never
    adjusted — it always reflects the unmodified ISU baseline.

Step 3 — Compute farmer figures (per acre)
    gross_revenue_per_acre  = yield_bu × price_per_bu
    production_cost_per_acre = sum of adjusted cost categories (no land)
    total_cost_per_acre      = production_cost_per_acre + rental_rate
    net_margin_per_acre      = gross_revenue_per_acre − total_cost_per_acre

Step 4 — Scale to operation total
    net_margin_total = net_margin_per_acre × acres

Step 5 — ISU benchmark comparison
    Uses fixed ISU baseline assumptions (corn: 200 bu/acre @ $4.50/bu,
    soybeans: 55 bu/acre @ $11.50/bu, rent: $230/acre for both) to compute
    isu_net_margin_per_acre. margin_vs_benchmark = farmer − ISU.
    Same production cost rows are reused; only yield, price, and rent differ.

No arithmetic is performed outside this module. All financial figures
originate from crop_costs.db (seeded from ISU Extension data).
"""

import sqlite3
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "abe.db"

ALLOWED_CROPS = {"corn", "soybeans"}

# ISU benchmark assumptions used for the comparison column.
# Source: ISU Extension "Estimated Costs of Crop Production in Iowa" (2024).
ISU_BENCHMARK = {
    "corn": {
        "yield_bu": 200.0,
        "price_per_bu": 4.50,
        "rental_rate": 230.0,
    },
    "soybeans": {
        "yield_bu": 55.0,
        "price_per_bu": 11.50,
        "rental_rate": 230.0,
    },
}


@dataclass
class MarginResult:
    crop: str
    acres: float
    yield_bu: float
    price_per_bu: float
    rental_rate: float

    gross_revenue_per_acre: float = 0.0
    costs_by_category: dict = field(default_factory=dict)        # {category: $/acre} after adjustments
    farmer_cost_overrides: dict = field(default_factory=dict)
    # {category: {"farmer_cost": x, "isu_cost": y, "savings_per_acre": z}}
    # savings_per_acre is positive when farmer pays less than ISU benchmark
    production_cost_per_acre: float = 0.0                        # excludes land rent
    total_cost_per_acre: float = 0.0                        # includes land rent
    net_margin_per_acre: float = 0.0
    net_margin_total: float = 0.0

    isu_gross_revenue_per_acre: float = 0.0
    isu_total_cost_per_acre: float = 0.0
    isu_net_margin_per_acre: float = 0.0
    margin_vs_benchmark: float = 0.0                        # farmer - ISU

    data_year: int = 0
    source: str = ""


def calculate_margin(
    crop: str,
    acres: float,
    yield_bu: float,
    price_per_bu: float,
    rental_rate: float,
    farmer_costs: Optional[dict] = None,
) -> MarginResult:
    """
    Calculate per-acre and total margin for a crop, comparing to ISU benchmarks.

    Args:
        crop:         Crop name — "corn" or "soybeans" (case-insensitive).
        acres:        Total acres planted.
        yield_bu:     Expected yield in bushels per acre.
        price_per_bu: Expected price in dollars per bushel.
        rental_rate:  Cash rent paid per acre.
        farmer_costs: Optional dict of {category: actual_cost_per_acre}. The
                      farmer's real $/acre for any input they know. The delta
                      vs. the ISU benchmark is computed here — the caller does
                      not need to know the benchmark values. Unknown categories
                      are ignored. The ISU benchmark comparison is never adjusted.

    Returns:
        MarginResult dataclass with gross revenue, adjusted costs by category,
        net margin per acre, and ISU benchmark comparison.

    Raises:
        ValueError: if crop is not in the allowed list or inputs are out of range.
        FileNotFoundError: if crop_costs.db has not been seeded yet.
    """
    crop = crop.strip().lower()
    if crop not in ALLOWED_CROPS:
        raise ValueError(
            f"Crop '{crop}' is not supported. Allowed crops: {sorted(ALLOWED_CROPS)}"
        )
    if acres <= 0:
        raise ValueError("acres must be greater than 0")
    if yield_bu <= 0:
        raise ValueError("yield_bu must be greater than 0")
    if price_per_bu <= 0:
        raise ValueError("price_per_bu must be greater than 0")
    if rental_rate < 0:
        raise ValueError("rental_rate cannot be negative")

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"abe.db not found at {DB_PATH}. Run data/seed_db.py first."
        )

    # --- Query ISU costs from database ---
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT category, cost_per_acre, year, source
            FROM crop_costs
            WHERE crop = ?
            ORDER BY category
            """,
            (crop,),
        ).fetchall()

    if not rows:
        raise ValueError(
            f"No cost data found for '{crop}' in abe.db. "
            "Check that seed_db.py ran successfully."
        )

    costs_by_category = {r["category"]: r["cost_per_acre"] for r in rows}
    data_year = rows[0]["year"]
    source = rows[0]["source"]

    # --- Apply farmer cost overrides (only for known categories) ---
    # farmer_costs values are actual $/acre the farmer pays; delta is computed here.
    farmer_cost_overrides = {}
    if farmer_costs:
        for category, farmer_cost in farmer_costs.items():
            if category in costs_by_category:
                isu_cost = costs_by_category[category]
                costs_by_category[category] = farmer_cost
                farmer_cost_overrides[category] = {
                    "farmer_cost":    round(farmer_cost, 2),
                    "isu_cost":       round(isu_cost, 2),
                    "savings_per_acre": round(isu_cost - farmer_cost, 2),
                }

    production_cost_per_acre = sum(costs_by_category.values())
    total_cost_per_acre = production_cost_per_acre + rental_rate
    gross_revenue_per_acre = yield_bu * price_per_bu
    net_margin_per_acre = gross_revenue_per_acre - total_cost_per_acre

    # --- ISU benchmark comparison (always unmodified ISU costs) ---
    bench = ISU_BENCHMARK[crop]
    isu_gross = bench["yield_bu"] * bench["price_per_bu"]
    isu_production_cost = sum(r["cost_per_acre"] for r in rows)  # unmodified
    isu_total_cost = isu_production_cost + bench["rental_rate"]
    isu_net_margin = isu_gross - isu_total_cost

    return MarginResult(
        crop=crop,
        acres=acres,
        yield_bu=yield_bu,
        price_per_bu=price_per_bu,
        rental_rate=rental_rate,
        gross_revenue_per_acre=round(gross_revenue_per_acre, 2),
        costs_by_category={k: round(v, 2) for k, v in costs_by_category.items()},
        farmer_cost_overrides=farmer_cost_overrides,
        production_cost_per_acre=round(production_cost_per_acre, 2),
        total_cost_per_acre=round(total_cost_per_acre, 2),
        net_margin_per_acre=round(net_margin_per_acre, 2),
        net_margin_total=round(net_margin_per_acre * acres, 2),
        isu_gross_revenue_per_acre=round(isu_gross, 2),
        isu_total_cost_per_acre=round(isu_total_cost, 2),
        isu_net_margin_per_acre=round(isu_net_margin, 2),
        margin_vs_benchmark=round(net_margin_per_acre - isu_net_margin, 2),
        data_year=data_year,
        source=source,
    )
