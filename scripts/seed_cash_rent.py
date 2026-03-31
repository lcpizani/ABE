"""
scripts/seed_cash_rent.py — Seed data/abe.db with ISU AgDM C2-10 2025 cash rent data.

Source: ISU Extension AgDM File C2-10
        "Cash Rental Rates for Iowa 2025 Survey"
        FM 1851 Revised May 2025

Run from the project root:
    python3 scripts/seed_cash_rent.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "abe.db"

# fmt: off
# (county, district, csr2_index, avg_rent, high_rent, med_rent, low_rent,
#  corn_yield_avg, soy_yield_avg, rent_per_csr2)
ROWS = [
    # ── District 1 ─────────────────────────────────────────────────────────────
    ("Buena Vista",   1, 86, 289, 340, 293, 236, 199, 61, 3.36),
    ("Cherokee",      1, 90, 317, 373, 308, 270, 201, 61, 3.52),
    ("Clay",          1, 86, 267, 319, 257, 225, 189, 56, 3.10),
    ("Dickinson",     1, 87, 247, 282, 255, 204, 185, 55, 2.84),
    ("Emmet",         1, 81, 244, 286, 236, 211, 194, 59, 3.01),
    ("Lyon",          1, 80, 310, 363, 306, 261, 201, 62, 3.88),
    ("O'Brien",       1, 94, 305, 334, 311, 271, 205, 62, 3.24),
    ("Osceola",       1, 86, 295, 343, 291, 251, 199, 60, 3.43),
    ("Palo Alto",     1, 82, 271, 310, 271, 232, 196, 57, 3.30),
    ("Plymouth",      1, 82, 287, 324, 286, 252, 192, 58, 3.50),
    ("Pocahontas",    1, 82, 288, 323, 292, 250, 191, 54, 3.51),
    ("Sioux",         1, 88, 339, 401, 327, 288, 199, 57, 3.85),
    # ── District 2 ─────────────────────────────────────────────────────────────
    ("Butler",        2, 80, 282, 333, 277, 235, 201, 57, 3.53),
    ("Cerro Gordo",   2, 79, 262, 290, 269, 227, 200, 61, 3.32),
    ("Floyd",         2, 83, 247, 279, 244, 218, 200, 56, 2.98),
    ("Franklin",      2, 81, 293, 325, 294, 260, 203, 59, 3.62),
    ("Hancock",       2, 76, 273, 326, 277, 217, 206, 61, 3.59),
    ("Humboldt",      2, 81, 285, 325, 286, 245, 200, 58, 3.52),
    ("Kossuth",       2, 79, 282, 336, 276, 235, 193, 59, 3.57),
    ("Mitchell",      2, 83, 287, 346, 282, 233, 202, 59, 3.46),
    ("Winnebago",     2, 74, 283, 324, 286, 240, 203, 58, 3.82),
    ("Worth",         2, 77, 250, 288, 255, 208, 195, 54, 3.25),
    ("Wright",        2, 79, 272, 323, 272, 221, 204, 58, 3.44),
    # ── District 3 ─────────────────────────────────────────────────────────────
    ("Allamakee",     3, 77, 281, 325, 289, 230, 203, 60, 3.65),
    ("Winneshiek",    3, 77, 281, 325, 289, 230, 203, 60, 3.65),
    ("Black Hawk",    3, 86, 289, 343, 286, 238, 193, 57, 3.36),
    ("Bremer",        3, 84, 317, 360, 319, 274, 201, 60, 3.77),
    ("Buchanan",      3, 83, 269, 316, 269, 221, 204, 59, 3.24),
    ("Chickasaw",     3, 83, 299, 346, 296, 256, 203, 57, 3.60),
    ("Clayton",       3, 68, 277, 343, 272, 216, 205, 59, 4.07),
    ("Delaware",      3, 77, 300, 358, 295, 248, 212, 62, 3.90),
    ("Dubuque",       3, 69, 330, 409, 345, 238, 212, 65, 4.78),
    ("Fayette",       3, 81, 270, 321, 265, 224, 201, 59, 3.33),
    ("Howard",        3, 83, 271, 319, 264, 230, 202, 56, 3.27),
    # ── District 4 ─────────────────────────────────────────────────────────────
    ("Audubon",       4, 77, 283, 326, 284, 238, 201, 58, 3.68),
    ("Calhoun",       4, 84, 275, 311, 275, 241, 202, 58, 3.27),
    ("Carroll",       4, 80, 299, 355, 298, 243, 200, 61, 3.74),
    ("Crawford",      4, 73, 316, 357, 309, 282, 204, 59, 4.33),
    ("Greene",        4, 82, 279, 323, 283, 232, 201, 59, 3.40),
    ("Guthrie",       4, 83, 255, 301, 249, 215, 188, 52, 3.07),
    ("Harrison",      4, 73, 294, 344, 292, 244, 181, 53, 4.03),
    ("Ida",           4, 81, 323, 373, 327, 271, 211, 61, 3.99),
    ("Monona",        4, 71, 333, 381, 330, 287, 180, 55, 4.69),
    ("Sac",           4, 86, 304, 346, 304, 263, 162, 49, 3.53),
    ("Shelby",        4, 72, 282, 325, 280, 240, 210, 67, 3.92),
    ("Woodbury",      4, 73, 300, 339, 307, 253, 199, 58, 4.11),
    # ── District 5 ─────────────────────────────────────────────────────────────
    ("Boone",         5, 85, 290, 335, 282, 251, 203, 62, 3.41),
    ("Dallas",        5, 88, 306, 355, 309, 255, 187, 59, 3.48),
    ("Grundy",        5, 88, 303, 346, 300, 262, 203, 64, 3.44),
    ("Hamilton",      5, 80, 270, 308, 275, 229, 201, 59, 3.38),
    ("Hardin",        5, 84, 281, 335, 273, 236, 194, 61, 3.35),
    ("Jasper",        5, 80, 275, 314, 282, 230, 214, 64, 3.44),
    ("Marshall",      5, 82, 288, 337, 289, 237, 216, 65, 3.51),
    ("Polk",          5, 89, 267, 314, 268, 219, 204, 59, 3.00),
    ("Poweshiek",     5, 79, 266, 313, 264, 222, 197, 56, 3.37),
    ("Story",         5, 86, 289, 334, 284, 250, 208, 67, 3.36),
    ("Tama",          5, 85, 302, 358, 301, 249, 197, 61, 3.55),
    ("Webster",       5, 78, 296, 325, 303, 262, 178, 53, 3.79),
    # ── District 6 ─────────────────────────────────────────────────────────────
    ("Benton",        6, 86, 283, 326, 284, 239, 203, 61, 3.29),
    ("Cedar",         6, 86, 276, 320, 269, 238, 205, 63, 3.21),
    ("Clinton",       6, 74, 275, 323, 270, 233, 209, 62, 3.72),
    ("Iowa",          6, 79, 271, 327, 275, 213, 197, 58, 3.43),
    ("Jackson",       6, 67, 255, 310, 252, 204, 203, 58, 3.81),
    ("Johnson",       6, 85, 282, 336, 283, 226, 198, 58, 3.32),
    ("Jones",         6, 77, 287, 326, 296, 240, 203, 60, 3.73),
    ("Linn",          6, 87, 323, 360, 324, 286, 197, 56, 3.71),
    ("Muscatine",     6, 83, 257, 318, 253, 201, 205, 62, 3.10),
    ("Scott",         6, 89, 284, 336, 290, 228, 207, 58, 3.19),
    # ── District 7 ─────────────────────────────────────────────────────────────
    ("Adair",         7, 79, 230, 264, 228, 197, 181, 52, 2.91),
    ("Adams",         7, 79, 254, 297, 262, 204, 187, 55, 3.22),
    ("Cass",          7, 79, 254, 297, 256, 208, 197, 56, 3.22),
    ("Fremont",       7, 81, 254, 295, 258, 209, 207, 57, 3.14),
    ("Mills",         7, 82, 276, 321, 276, 231, 200, 54, 3.37),
    ("Montgomery",    7, 79, 255, 304, 251, 211, 200, 57, 3.23),
    ("Page",          7, 80, 237, 285, 241, 185, 187, 57, 2.96),
    ("Pottawattamie", 7, 79, 283, 324, 286, 239, 196, 58, 3.58),
    ("Taylor",        7, 81, 253, 286, 252, 222, 187, 60, 3.12),
    # ── District 8 ─────────────────────────────────────────────────────────────
    ("Appanoose",     8, 76, 188, 219, 183, 163, 161, 48, 2.47),
    ("Monroe",        8, 76, 188, 219, 183, 163, 161, 48, 2.47),
    ("Clarke",        8, 77, 209, 270, 224, 135, 170, 48, 2.71),
    ("Decatur",       8, 75, 187, 221, 186, 153, 171, 48, 2.49),
    ("Lucas",         8, 73, 169, 207, 171, 130, 157, 48, 2.32),
    ("Madison",       8, 86, 228, 266, 231, 188, 184, 57, 2.65),
    ("Marion",        8, 80, 251, 304, 252, 195, 199, 60, 3.14),
    ("Ringgold",      8, 76, 237, 284, 248, 179, 192, 59, 3.12),
    ("Union",         8, 85, 235, 270, 238, 197, 183, 56, 2.76),
    ("Warren",        8, 85, 266, 308, 263, 227, 181, 57, 3.13),
    ("Wayne",         8, 66, 177, 207, 179, 144, 186, 57, 2.68),
    # ── District 9 ─────────────────────────────────────────────────────────────
    ("Davis",         9, 72, 234, 284, 232, 184, 169, 51, 3.25),
    ("Wapello",       9, 72, 234, 284, 232, 184, 169, 51, 3.25),
    ("Des Moines",    9, 84, 254, 316, 258, 190, 204, 64, 3.02),
    ("Henry",         9, 81, 281, 326, 284, 231, 183, 61, 3.47),
    ("Jefferson",     9, 79, 251, 301, 240, 211, 181, 55, 3.18),
    ("Keokuk",        9, 80, 242, 302, 231, 193, 181, 57, 3.03),
    ("Lee",           9, 75, 288, 333, 288, 242, 188, 60, 3.84),
    ("Louisa",        9, 80, 253, 311, 252, 197, 195, 60, 3.16),
    ("Mahaska",       9, 81, 228, 268, 232, 185, 201, 63, 2.81),
    ("Van Buren",     9, 73, 208, 266, 199, 158, 183, 54, 2.85),
    ("Washington",    9, 82, 297, 351, 287, 254, 175, 53, 3.62),
]
# fmt: on

# All 99 official Iowa counties — used to detect missing rows
IOWA_COUNTIES = {
    "Adair", "Adams", "Allamakee", "Appanoose", "Audubon", "Benton",
    "Black Hawk", "Boone", "Bremer", "Buchanan", "Buena Vista", "Butler",
    "Calhoun", "Carroll", "Cass", "Cedar", "Cerro Gordo", "Cherokee",
    "Chickasaw", "Clarke", "Clay", "Clayton", "Clinton", "Crawford",
    "Dallas", "Davis", "Decatur", "Delaware", "Des Moines", "Dickinson",
    "Dubuque", "Emmet", "Fayette", "Floyd", "Franklin", "Fremont",
    "Greene", "Grundy", "Guthrie", "Hamilton", "Hancock", "Hardin",
    "Harrison", "Henry", "Howard", "Humboldt", "Ida", "Iowa",
    "Jackson", "Jasper", "Jefferson", "Johnson", "Jones", "Keokuk",
    "Kossuth", "Lee", "Linn", "Louisa", "Lucas", "Lyon",
    "Madison", "Mahaska", "Marion", "Marshall", "Mills", "Mitchell",
    "Monona", "Monroe", "Montgomery", "Muscatine", "O'Brien", "Osceola",
    "Page", "Palo Alto", "Plymouth", "Pocahontas", "Polk", "Pottawattamie",
    "Poweshiek", "Ringgold", "Sac", "Scott", "Shelby", "Sioux",
    "Story", "Tama", "Taylor", "Union", "Van Buren", "Wapello",
    "Warren", "Washington", "Wayne", "Webster", "Winnebago", "Winneshiek",
    "Woodbury", "Worth", "Wright",
}


def seed() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cash_rent (
                county          TEXT    NOT NULL,
                district        INTEGER NOT NULL,
                csr2_index      REAL,
                avg_rent        REAL,
                high_rent       REAL,
                med_rent        REAL,
                low_rent        REAL,
                corn_yield_avg  REAL,
                soy_yield_avg   REAL,
                rent_per_csr2   REAL,
                source          TEXT    DEFAULT 'ISU AgDM C2-10 2025',
                year            INTEGER DEFAULT 2025,
                PRIMARY KEY (county, year)
            )
            """
        )

        conn.executemany(
            """
            INSERT OR REPLACE INTO cash_rent
                (county, district, csr2_index, avg_rent, high_rent, med_rent,
                 low_rent, corn_yield_avg, soy_yield_avg, rent_per_csr2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ROWS,
        )

        count = conn.execute("SELECT COUNT(*) FROM cash_rent WHERE year = 2025").fetchone()[0]
        print(f"Rows in cash_rent (year=2025): {count}")

        if count != 99:
            seeded = {r[0] for r in conn.execute("SELECT county FROM cash_rent WHERE year = 2025")}
            missing = IOWA_COUNTIES - seeded
            print(f"\nMissing counties ({len(missing)}):")
            for c in sorted(missing):
                print(f"  {c}")
        else:
            print("Row count correct: 99 ✓")

        print("\nSpot check — Linn, Polk, Sioux, Wayne:")
        print(f"  {'County':<16} {'Dist':>4} {'Avg':>6} {'High':>6} {'Low':>6} {'CSR2':>6}")
        print(f"  {'-'*16} {'-'*4} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
        rows = conn.execute(
            """
            SELECT county, district, avg_rent, high_rent, low_rent, csr2_index
            FROM cash_rent
            WHERE county IN ('Linn', 'Polk', 'Sioux', 'Wayne')
            ORDER BY county
            """
        ).fetchall()
        for r in rows:
            print(f"  {r[0]:<16} {r[1]:>4} {r[2]:>6.0f} {r[3]:>6.0f} {r[4]:>6.0f} {r[5]:>6.0f}")


if __name__ == "__main__":
    seed()
