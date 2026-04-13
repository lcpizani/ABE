# CLI Commands

All scripts use `.venv/bin/python`. Never use the system `python3`.

---

## Skill scripts

### Rental rate check

```bash
.venv/bin/python scripts/run_rental.py \
  --county "COUNTY NAME" \
  --quality high|medium|low \
  [--quoted RATE]
```

| Argument | Required | Description |
|---|---|---|
| `--county` | Yes | Iowa county name (e.g., "Linn County") |
| `--quality` | Yes | Land quality tier: `high`, `medium`, or `low` |
| `--quoted` | No | Quoted rent per acre to compare against benchmarks |

---

### Crop margin simulator

```bash
.venv/bin/python scripts/run_margin.py \
  --crop corn|soybean \
  --acres NUMBER \
  --county "COUNTY NAME" \
  [--price PRICE_PER_BU] \
  [--rent RENT_PER_ACRE] \
  [--farmer-cost KEY=VALUE ...]
```

| Argument | Required | Description |
|---|---|---|
| `--crop` | Yes | `corn` or `soybean` |
| `--acres` | Yes | Number of acres |
| `--county` | Yes | Iowa county name |
| `--price` | No | Price override per bushel (default: live MARS price) |
| `--rent` | No | Rent override per acre (default: ISU C2-10 benchmark) |
| `--farmer-cost` | No | Override individual cost items: `seed=120`, `fertilizer=90`, etc. |

Valid `--farmer-cost` keys: `seed`, `fertilizer`, `pesticide`, `machinery`, `labor`, `drying`, `crop_insurance`, `miscellaneous`

---

### Cost of production

```bash
.venv/bin/python scripts/run_cost_production.py \
  --crop corn|soybean \
  --acres NUMBER \
  [--rotation continuous|rotation] \
  [--tier low|mid|high] \
  [--price PRICE_PER_BU] \
  [--override KEY=VALUE ...]
```

---

### Budget planner

```bash
.venv/bin/python scripts/run_budget.py \
  --budget AMOUNT \
  --county "COUNTY NAME" \
  --crop corn|soybean \
  --intent rent|buy|both \
  --quality high|medium|low
```

---

### Weather

```bash
# 14-day history
.venv/bin/python scripts/run_weather.py \
  --mode history \
  --county "COUNTY NAME" \
  [--days 14]

# 16-day forecast
.venv/bin/python scripts/run_weather.py \
  --mode forecast \
  --county "COUNTY NAME"

# Growing-season alerts
.venv/bin/python scripts/run_weather.py \
  --mode alerts \
  --county "COUNTY NAME"
```

---

### Corn disease detector

```bash
.venv/bin/python skills/corn-disease-detector/scripts/corn_disease.py IMAGE_PATH
```

---

## Heartbeat scripts

```bash
# Daily price check
.venv/bin/python scripts/run_prices.py

# Daily calendar reminders
.venv/bin/python scripts/run_calendar.py

# Weekly margin check
.venv/bin/python scripts/run_margin_check.py

# Weekly crop progress
.venv/bin/python scripts/run_crop_progress.py
```

---

## Database scripts

```bash
# Initialize all tables
.venv/bin/python data/seed_db.py

# Populate cash_rent from ISU C2-10
.venv/bin/python scripts/seed_cash_rent.py

# Populate cost tables
.venv/bin/python scripts/seed_costs.py

# Parse knowledge/a1-20.xlsx into DB
.venv/bin/python scripts/update_data.py
```

---

## Knowledge base (gno)

```bash
# Query — returns top N relevant chunks as JSON
gno query "TOPIC" -c abe-knowledge -n 3 --json

# Ask — synthesizes an answer from indexed documents
gno ask "QUESTION" --answer -c abe-knowledge

# Re-index all documents manually
gno index

# Daemon control
bash scripts/gno-daemon.sh start
bash scripts/gno-daemon.sh stop
bash scripts/gno-daemon.sh restart
bash scripts/gno-daemon.sh status
bash scripts/gno-daemon.sh logs

# Add a document
bash scripts/add_document.sh /path/to/document.pdf
```

---

## OpenClaw cron

```bash
# List all registered cron jobs
openclaw cron list

# Add a cron job (see Deployment for full commands)
openclaw cron add --agent abe --name "JOB-NAME" \
  --cron "CRON_EXPRESSION" --tz "America/Chicago" \
  --message "MESSAGE TO TRIGGER TASK" \
  --timeout-seconds SECONDS

# Remove a cron job
openclaw cron remove --name "JOB-NAME"
```

---

## NASS API standalone

Run the NASS/MARS client directly to see what data is available:

```bash
.venv/bin/python scripts/nass_api.py
```

Prints current Iowa corn/soybean prices, yields, and crop progress summary.
