# Setup

This page covers setting up a full development environment for ABE.

---

## Prerequisites

- Python 3.10 or later
- [OpenClaw](https://openclaw.bot) installed and configured — see [OpenClaw docs](https://docs.openclaw.ai/)
- [gno](https://github.com/gmickel/gno) 0.30.0 or later installed
- SQLite 3
- A Telegram bot token — create one with [@BotFather](https://t.me/BotFather)
- API keys for:
  - [Anthropic](https://console.anthropic.com/) (Claude)
  - [USDA NASS QuickStats](https://quickstats.nass.usda.gov/api)
  - [USDA AMS MyMarketNews (MARS)](https://mymarketnews.ams.usda.gov/)

---

## Step 1 — Clone and enter the repo

```bash
git clone <repo-url>
cd ABE
```

---

## Step 2 — Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Verify the key packages are installed:

```bash
.venv/bin/python -c "import anthropic, torch, openpyxl; print('OK')"
```

---

## Step 3 — Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env` with your actual keys. See [Environment Variables](../reference/environment-variables.md) for the full reference.

---

## Step 4 — Initialize the database

Run the seed scripts in order:

```bash
.venv/bin/python data/seed_db.py          # Creates all tables
.venv/bin/python scripts/seed_cash_rent.py # Populates cash_rent from ISU C2-10
.venv/bin/python scripts/seed_costs.py    # Populates cost tables
.venv/bin/python scripts/update_data.py   # Parses a1-20.xlsx into DB
```

Verify:

```bash
sqlite3 data/abe.db ".tables"
# Expected: a1_20_costs  cash_rent  crop_costs  crop_production_costs
```

---

## Step 5 — Start the knowledge base daemon

```bash
bash scripts/gno-daemon.sh start
bash scripts/gno-daemon.sh status
```

The first start indexes all documents in `knowledge/`. This may take a few minutes. Monitor progress:

```bash
bash scripts/gno-daemon.sh logs
```

---

## Step 6 — Verify individual skills

Run each skill script to confirm everything is wired up:

```bash
# Rental rate check
.venv/bin/python scripts/run_rental.py --county "Story" --quality medium

# Crop margin
.venv/bin/python scripts/run_margin.py --crop corn --acres 200 --county "Linn County"

# Cost of production
.venv/bin/python scripts/run_cost_production.py --crop corn --acres 200

# Weather
.venv/bin/python scripts/run_weather.py --mode forecast --county "Polk"

# Price check
.venv/bin/python scripts/run_prices.py

# Knowledge base query
gno query "FSA beginning farmer loan" -c abe-knowledge -n 3
```

Each should return valid JSON.

---

## Step 7 — Register cron jobs

See [Deployment](../for-staff/deployment.md#step-6--register-cron-jobs-with-openclaw) for the full list of `openclaw cron add` commands.

---

## Step 8 — Start the agent

Follow the [OpenClaw documentation](https://docs.openclaw.ai/) to connect ABE to your Telegram bot and start the agent. ABE's identity and behavior are defined in:

- `SOUL.md` — persona and hard limits
- `AGENTS.md` — response rules, skill routing, memory protocol
- `HEARTBEAT.md` — autonomous task definitions

---

## Development tips

### Resetting the database

If you need a clean slate:

```bash
rm data/abe.db
.venv/bin/python data/seed_db.py
.venv/bin/python scripts/seed_cash_rent.py
.venv/bin/python scripts/seed_costs.py
.venv/bin/python scripts/update_data.py
```

### Testing a heartbeat script manually

Run any heartbeat script directly to see its output without waiting for cron:

```bash
.venv/bin/python scripts/run_prices.py
.venv/bin/python scripts/run_calendar.py
.venv/bin/python scripts/run_margin_check.py
.venv/bin/python scripts/run_crop_progress.py
```

### Restarting the daemon after adding documents

```bash
bash scripts/gno-daemon.sh restart
```

Or let it detect the new files automatically (it watches `knowledge/` on each sync cycle).
