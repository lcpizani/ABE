"""
seed_db.py — Populate crop_costs.db with ISU Extension benchmark data.

Source: ISU Extension "Estimated Costs of Crop Production in Iowa" (2024)
https://www.extension.iastate.edu/agdm/crops/html/a1-20.html

Run once before starting ABE:
    python data/seed_db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "abe.db"

SOURCE = "ISU Extension — Estimated Costs of Crop Production in Iowa"
YEAR = 2026

# ISU 2026 production cost estimates (excludes land rent — added at query time).
# Source: ISU AgDM A1-20, January 2026.
# Corn = Corn Following Soybeans, 211 bu/acre (middle tier).
# Soybeans = Herbicide-Tolerant Soybeans Following Corn, 61 bu/acre (middle tier).
# Fertilizer combines N + P + K + lime. Machinery excludes drying (separate line).
# Miscellaneous includes the A1-20 "interest on preharvest variable costs" line.
# All figures are dollars per acre.
CROP_COSTS = [
    # --- Corn Following Soybeans, 211 bu/acre ---
    ("corn", "seed",           113.70),   # 30,000 kernels @ $3.79/1,000
    ("corn", "fertilizer",     169.44),   # N $84.27 + P $56.88 + K $24.57 + lime $3.72
    ("corn", "pesticide",       56.00),   # herbicide only (no insecticide in CFS budget)
    ("corn", "machinery",      146.83),   # preharvest $59.40 + harvest (excl. dry) $87.43
    ("corn", "drying",          49.54),   # LP gas @ $1.54/gal; fixed $10.55 + var $38.99
    ("corn", "labor",           52.02),   # 2.55 hrs @ $20.40/hr
    ("corn", "crop_insurance",  17.10),   # 80% RP coverage, Central Iowa
    ("corn", "miscellaneous",   33.35),   # $13.70 misc + $19.65 preharvest interest
    # --- Herbicide-Tolerant Soybeans Following Corn, 61 bu/acre ---
    ("soybeans", "seed",           63.10),   # 140,000 kernels @ $63.10/140k
    ("soybeans", "fertilizer",     74.88),   # P $35.28 + K $35.88 + lime $3.72 (no N)
    ("soybeans", "pesticide",      75.00),   # herbicide (no insecticide/fungicide in budget)
    ("soybeans", "machinery",     111.39),   # preharvest $64.20 + harvest $47.19
    ("soybeans", "labor",          44.88),   # 2.20 hrs @ $20.40/hr
    ("soybeans", "crop_insurance",  9.10),   # 80% RP coverage, Central Iowa
    ("soybeans", "miscellaneous",  26.77),   # $13.70 misc + $13.07 preharvest interest
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
