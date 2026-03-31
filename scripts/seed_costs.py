"""
scripts/seed_costs.py — Seed data/abe.db with ISU A1-20 aggregate cost data.

Source: ISU Extension AgDM A1-20 "Estimated Costs of Crop Production in Iowa" (2024)
https://www.extension.iastate.edu/agdm/crops/html/a1-20.html

All ABE data lives in data/abe.db. This script manages the a1_20_costs table
(ISU A1-20 aggregate totals). The per-category crop_costs table is seeded by
data/seed_db.py.

Run from the project root:
    python3 scripts/seed_costs.py
"""

import sqlite3
from pathlib import Path

# Two levels up from scripts/ → project root → data/abe.db
DB_PATH = Path(__file__).parent.parent / "data" / "abe.db"

ROWS = [
    {
        "crop":                    "corn",
        "region":                  "iowa_statewide",
        "variable_cost_per_acre":  478.00,
        "fixed_cost_per_acre":     287.00,
        "expected_yield_bu":       202.0,
        "price_source":            "ISU AgDM A1-20 2024",
        "year":                    2024,
    },
    {
        "crop":                    "soybeans",
        "region":                  "iowa_statewide",
        "variable_cost_per_acre":  294.00,
        "fixed_cost_per_acre":     247.00,
        "expected_yield_bu":       54.0,
        "price_source":            "ISU AgDM A1-20 2024",
        "year":                    2024,
    },
]


def seed() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS a1_20_costs (
                crop                   TEXT    NOT NULL,
                region                 TEXT    NOT NULL,
                variable_cost_per_acre REAL    NOT NULL,
                fixed_cost_per_acre    REAL    NOT NULL,
                expected_yield_bu      REAL    NOT NULL,
                price_source           TEXT    NOT NULL,
                year                   INTEGER NOT NULL,
                PRIMARY KEY (crop, region, year)
            )
            """
        )
        conn.executemany(
            """
            INSERT OR REPLACE INTO a1_20_costs
                (crop, region, variable_cost_per_acre, fixed_cost_per_acre,
                 expected_yield_bu, price_source, year)
            VALUES
                (:crop, :region, :variable_cost_per_acre, :fixed_cost_per_acre,
                 :expected_yield_bu, :price_source, :year)
            """,
            ROWS,
        )
        count = conn.execute("SELECT COUNT(*) FROM a1_20_costs").fetchone()[0]

    print(f"a1_20_costs rows in {DB_PATH}: {count}")


if __name__ == "__main__":
    seed()
