"""
margin_calculator — ABE skill

calculate_margin(crop, acres, yield_bu, price_per_bu, rental_rate)

Queries the crop_costs SQLite table for ISU Extension benchmark costs,
then returns gross revenue, costs broken down by category, net margin per
acre, and a comparison to the ISU benchmark margin.

All financial figures come from crop_costs.db (seeded from ISU Extension
"Estimated Costs of Crop Production in Iowa"). No arithmetic is invented
by the model.
"""

import sqlite3
from pathlib import Path
from dataclasses import dataclass, field

DB_PATH = Path(__file__).parent.parent.parent / "data" / "crop_costs.db"

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
    costs_by_category: dict = field(default_factory=dict)   # {category: $/acre}
    production_cost_per_acre: float = 0.0                   # excludes land rent
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
) -> MarginResult:
    """
    Calculate per-acre and total margin for a crop, comparing to ISU benchmarks.

    Args:
        crop:          Crop name — "corn" or "soybeans" (case-insensitive).
        acres:         Total acres planted.
        yield_bu:      Expected yield in bushels per acre.
        price_per_bu:  Expected price in dollars per bushel.
        rental_rate:   Cash rent paid per acre.

    Returns:
        MarginResult dataclass with gross revenue, costs by category,
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
            f"crop_costs.db not found at {DB_PATH}. Run data/seed_db.py first."
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
            f"No cost data found for '{crop}' in crop_costs.db. "
            "Check that seed_db.py ran successfully."
        )

    costs_by_category = {r["category"]: r["cost_per_acre"] for r in rows}
    data_year = rows[0]["year"]
    source = rows[0]["source"]

    production_cost_per_acre = sum(costs_by_category.values())
    total_cost_per_acre = production_cost_per_acre + rental_rate
    gross_revenue_per_acre = yield_bu * price_per_bu
    net_margin_per_acre = gross_revenue_per_acre - total_cost_per_acre

    # --- ISU benchmark comparison ---
    bench = ISU_BENCHMARK[crop]
    isu_gross = bench["yield_bu"] * bench["price_per_bu"]
    isu_total_cost = production_cost_per_acre + bench["rental_rate"]  # same production costs
    isu_net_margin = isu_gross - isu_total_cost

    return MarginResult(
        crop=crop,
        acres=acres,
        yield_bu=yield_bu,
        price_per_bu=price_per_bu,
        rental_rate=rental_rate,
        gross_revenue_per_acre=round(gross_revenue_per_acre, 2),
        costs_by_category={k: round(v, 2) for k, v in costs_by_category.items()},
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
