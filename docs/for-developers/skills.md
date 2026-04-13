# Skills

A skill is a discrete capability ABE can invoke in response to a farmer's question. Each skill has a `SKILL.md` that tells ABE when to use it and how to present results, and most have one or more Python scripts that do the actual work.

---

## Skill structure

Every skill lives under `skills/<skill-name>/` and contains:

```
skills/
└── crop-margin-simulator/
    ├── SKILL.md          # When to use this skill; how to invoke it; how to present results
    └── scripts/
        ├── crop_margin.py    # Integration layer: price resolution, DB queries
        └── calculator.py     # Core calculation logic
```

The `SKILL.md` is the primary interface between ABE and the skill. ABE reads it to understand:
- When this skill applies (trigger conditions)
- What inputs it needs from the farmer
- The exact command to run
- How to interpret and present the JSON output

---

## Routing rules

ABE's `AGENTS.md` defines which skill to invoke for each type of question. ABE never runs a skill without being asked — it offers and waits for confirmation.

| Farmer says... | Skill invoked |
|---|---|
| "Is this rent fair?" / "Is $X/acre high?" | `rental-rate-check` |
| "Will this pencil out?" / "What's my margin?" | `crop-margin-simulator` |
| "What does it cost to grow corn?" | `cost-of-production` |
| "What programs can I qualify for?" / "Tell me about FSA loans" | `program-screener` + `abe-knowledge` |
| Sends a photo of a corn leaf | `corn-disease-detector` |
| "What's the weather going to be?" / "Will it freeze?" | `weather-forecast` |
| "How much land can I rent on my budget?" / "Should I rent or buy?" | `budget-planner` |
| Asks about leases, financing, or policy | `abe-knowledge` |

---

## Skill reference

### rental-rate-check

Looks up ISU C2-10 county rental benchmarks from `data/abe.db`.

```bash
.venv/bin/python scripts/run_rental.py \
  --county "Linn County" \
  --quality medium \
  [--quoted 290]
```

**Output fields:** `county`, `quality_tier`, `benchmark_avg`, `benchmark_high`, `benchmark_med`, `benchmark_low`, `tier_benchmark`, `verdict` (above_range / above_average / at_average / below_average), `source`

---

### crop-margin-simulator

Calculates net margin per acre and total profit or loss.

```bash
.venv/bin/python scripts/run_margin.py \
  --crop corn \
  --acres 400 \
  --county "Linn County" \
  [--price 4.20] \
  [--rent 290] \
  [--farmer-cost seed=120 fertilizer=90 ...]
```

**Output fields:** `crop`, `county`, `acres`, `price_per_bu`, `price_source`, `gross_revenue`, `total_cost`, `net_margin`, `cost_source`, `yield_bu_per_acre`, `year`, `rental_rate_used`, `farmer_cost_overrides`, `costs_by_category`

---

### cost-of-production

Produces a detailed line-item cost breakdown using ISU A1-20 (2026) benchmarks.

```bash
.venv/bin/python scripts/run_cost_production.py \
  --crop corn \
  --acres 200 \
  [--rotation continuous|rotation] \
  [--tier low|mid|high] \
  [--price 4.20] \
  [--override seed=120 fertilizer=90 ...]
```

**Output fields:** Itemized fixed costs, variable costs, total cost per acre, total cost per bushel, yield assumption, price, gross revenue, net margin.

---

### program-screener

Searches the knowledge base for program information and presents it one program at a time.

```bash
gno ask "QUESTION" --answer -c abe-knowledge
gno query "TOPIC" -c abe-knowledge -n 3 --json
```

Programs covered: FSA beginning farmer loans, EQIP, ARC-CO/PLC, Iowa Beginning Farmer Tax Credit, Iowa BFLP, Iowa LPP.

---

### corn-disease-detector

Classifies a corn leaf photo using the CornCNN2 PyTorch model.

```bash
.venv/bin/python skills/corn-disease-detector/scripts/corn_disease.py IMAGE_PATH
```

**Supported classes:** Blight (northern), Blight (southern), Common_Rust, Grey_Leaf_Spot, Healthy, Lethal_Necrosis, Streak_Virus

**Confidence threshold:** 60%. Below that, ABE asks for a clearer photo.

After diagnosis, ABE automatically runs weather history (14 days) for the farmer's county and connects conditions to disease risk.

---

### weather-forecast

Three modes via [Open-Meteo](https://open-meteo.com/).

```bash
# 14-day history
.venv/bin/python scripts/run_weather.py --mode history --county "Story" [--days 14]

# 16-day forecast
.venv/bin/python scripts/run_weather.py --mode forecast --county "Linn"

# Growing-season alerts
.venv/bin/python scripts/run_weather.py --mode alerts --county "Palo Alto"
```

County names are resolved to lat/lon using `data/iowa_counties.json`.

**Alert types:** frost_risk, hard_frost_planting, heat_stress, heavy_rain, high_wind, drought_watch, disease_pressure.

---

### budget-planner

Models land strategy scenarios given a dollar budget.

```bash
.venv/bin/python scripts/run_budget.py \
  --budget 500000 \
  --county "Story" \
  --crop corn \
  --intent rent|buy|both \
  --quality high|medium|low
```

**Output:** Scenario comparisons by estimated net margin and cash flow implications.

---

### abe-knowledge

Hybrid BM25 + vector search over ~41 indexed documents in `knowledge/`.

```bash
# Retrieve relevant chunks
gno query "TOPIC" -c abe-knowledge -n 3 --json

# Synthesize an answer with citations
gno ask "QUESTION" --answer -c abe-knowledge
```

Use `gno query` for targeted lookups. Use `gno ask` when the farmer's question requires synthesizing across multiple documents.

---

## How ABE presents skill results

- Walk the math like sitting at a kitchen table.
- Name the source inline (not in a footnote).
- Always ask the farmer to check the numbers against their own operation.
- If the result implies something worth noting (thin margin, above-average rent, disease pressure), offer it — once, as a question, then wait.
