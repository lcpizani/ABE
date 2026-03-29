"""
seed_db.py — Populate crop_costs.db with ISU Extension benchmark data.

Source: ISU Extension "Estimated Costs of Crop Production in Iowa" (2024)
https://www.extension.iastate.edu/agdm/crops/html/a1-20.html

Run once before starting ABE:
    python data/seed_db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "crop_costs.db"

SOURCE = "ISU Extension — Estimated Costs of Crop Production in Iowa"
YEAR = 2024

# ISU 2024 production cost estimates (excludes land rent — added at query time).
# All figures are dollars per acre.
CROP_COSTS = [
    # --- Corn ---
    ("corn", "seed",          115.00),
    ("corn", "fertilizer",    185.00),
    ("corn", "pesticide",      55.00),
    ("corn", "machinery",     145.00),
    ("corn", "labor",          25.00),
    ("corn", "drying",         30.00),
    ("corn", "crop_insurance", 25.00),
    ("corn", "miscellaneous",  18.00),
    # --- Soybeans ---
    ("soybeans", "seed",           60.00),
    ("soybeans", "fertilizer",     60.00),
    ("soybeans", "pesticide",      35.00),
    ("soybeans", "machinery",     120.00),
    ("soybeans", "labor",          20.00),
    ("soybeans", "crop_insurance", 20.00),
    ("soybeans", "miscellaneous",  15.00),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS crop_costs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            crop         TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            cost_per_acre REAL   NOT NULL,
            year         INTEGER NOT NULL,
            source       TEXT    NOT NULL,
            UNIQUE(crop, category, year)
        )
        """
    )
    conn.executemany(
        """
        INSERT OR REPLACE INTO crop_costs (crop, category, cost_per_acre, year, source)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(crop, cat, cost, YEAR, SOURCE) for crop, cat, cost in CROP_COSTS],
    )
    conn.commit()
    conn.close()
    print(f"Seeded {len(CROP_COSTS)} rows into {DB_PATH}")


if __name__ == "__main__":
    seed()
