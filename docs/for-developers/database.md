# Database

ABE uses a single SQLite database at `data/abe.db`. It stores structured benchmark data that skills query for calculations. All data comes from ISU Extension publications or USDA sources.

---

## Tables

### `cash_rent`

ISU Extension C2-10 rental benchmarks for all 99 Iowa counties.

| Column | Type | Description |
|---|---|---|
| `county` | TEXT | Iowa county name |
| `district` | TEXT | Iowa crop reporting district (e.g., North Central, Southeast) |
| `csr2_index` | REAL | Average CSR2 soil productivity score for the county |
| `avg_rent` | REAL | Average cash rent per acre (all quality tiers) |
| `high_rent` | REAL | Average rent for high-quality ground |
| `med_rent` | REAL | Average rent for medium-quality ground |
| `low_rent` | REAL | Average rent for low-quality ground |
| `corn_yield_avg` | REAL | County average corn yield (bu/acre) |
| `soy_yield_avg` | REAL | County average soybean yield (bu/acre) |
| `rent_per_csr2` | REAL | Rent divided by CSR2 score (value per productivity point) |
| `source` | TEXT | `ISU AgDM C2-10 2025` |
| `year` | INTEGER | Data year |

Primary key: `(county, year)`

**Used by:** `rental-rate-check`, `crop-margin-simulator`, `budget-planner`

---

### `crop_production_costs`

Line-item cost data parsed from ISU A1-20 (2026). Stores every cost item for corn and soybeans across low, mid, and high yield tiers.

| Column | Type | Description |
|---|---|---|
| `year` | INTEGER | Budget year |
| `budget_type` | TEXT | `corn` or `soybean` |
| `sub_budget` | TEXT | Budget variant (e.g., continuous corn, corn after soybean) |
| `section` | TEXT | Cost section heading |
| `cost_item` | TEXT | Line item name (e.g., seed, nitrogen, machinery) |
| `cost_type` | TEXT | `fixed` or `variable` |
| `yield_tier` | TEXT | `low`, `mid`, or `high` |
| `yield_value` | REAL | Expected yield at this tier (bu/acre) |
| `yield_unit` | TEXT | `bu/acre` |
| `units_quantity` | REAL | Units used per acre |
| `cost_per_acre` | REAL | Cost in dollars per acre |

**Used by:** `cost-of-production`, `crop-margin-simulator`

---

### `a1_20_costs`

Aggregate ISU A1-20 benchmarks by crop, region, and year.

| Column | Type | Description |
|---|---|---|
| `crop` | TEXT | `corn` or `soybean` |
| `region` | TEXT | Iowa region |
| `variable_cost_per_acre` | REAL | Total variable cost per acre |
| `fixed_cost_per_acre` | REAL | Total fixed cost per acre |
| `expected_yield_bu` | REAL | Expected yield (bu/acre) |
| `price_source` | TEXT | Price data source |
| `year` | INTEGER | Budget year |

---

### `crop_costs`

Flat cost lookup by category, for quick queries where line-item detail is not needed.

| Column | Type | Description |
|---|---|---|
| `crop` | TEXT | `corn` or `soybean` |
| `category` | TEXT | Cost category (seed, fertilizer, pesticide, machinery, labor, etc.) |
| `cost_per_acre` | REAL | Benchmark cost per acre |
| `year` | INTEGER | Budget year |
| `source` | TEXT | Source publication |

---

## Seeding the database

Run these scripts in order on a fresh setup:

```bash
# 1. Create all tables
.venv/bin/python data/seed_db.py

# 2. Populate cash_rent with ISU C2-10 data
.venv/bin/python scripts/seed_cash_rent.py

# 3. Populate cost tables
.venv/bin/python scripts/seed_costs.py

# 4. Parse knowledge/a1-20.xlsx into crop_production_costs
.venv/bin/python scripts/update_data.py
```

---

## Querying the database directly

```bash
sqlite3 data/abe.db

# List tables
.tables

# Check rental benchmarks for a county
SELECT * FROM cash_rent WHERE county = 'Linn County';

# Check corn variable costs for mid-yield tier
SELECT cost_item, cost_per_acre FROM crop_production_costs
WHERE budget_type = 'corn' AND yield_tier = 'mid' AND cost_type = 'variable';
```

---

## Updating benchmark data

When new ISU publications are released:

1. Update the source file in `knowledge/` (e.g., replace `a1-20.xlsx` with the new edition).
2. Re-run the relevant seed scripts.
3. Verify row counts and spot-check key values.

```bash
sqlite3 data/abe.db "SELECT COUNT(*) FROM cash_rent;"
sqlite3 data/abe.db "SELECT COUNT(*) FROM crop_production_costs;"
```
