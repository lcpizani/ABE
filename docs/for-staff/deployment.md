# Deployment

This page covers how to set up ABE on a new machine or VPS from scratch.

---

## Prerequisites

Before you begin, you need:

- Python 3.10 or later
- `pip` and `venv`
- [OpenClaw](https://openclaw.bot) installed and configured — see the [OpenClaw docs](https://docs.openclaw.ai/) for runtime setup
- [gno](https://github.com/gmickel/gno) 0.30.0 or later — used for the local knowledge base
- A Telegram bot token — create one with [@BotFather](https://t.me/BotFather)
- API keys for Anthropic, USDA NASS, and USDA MARS (see [Environment Variables](../reference/environment-variables.md))

---

## Step 1 — Clone the repository

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

All scripts in this project use `.venv/bin/python` directly. Do not use the system `python3`.

---

## Step 3 — Configure environment variables

Copy the example and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual values. See [Environment Variables](../reference/environment-variables.md) for the full list and descriptions.

---

## Step 4 — Initialize the database

```bash
.venv/bin/python data/seed_db.py
.venv/bin/python scripts/seed_cash_rent.py
.venv/bin/python scripts/seed_costs.py
.venv/bin/python scripts/update_data.py
```

These scripts create all SQLite tables and populate them with ISU Extension benchmark data from the files in `knowledge/`.

Verify the database was created:

```bash
sqlite3 data/abe.db ".tables"
```

You should see: `cash_rent`, `crop_production_costs`, `a1_20_costs`, `crop_costs`.

---

## Step 5 — Start the knowledge base daemon

```bash
bash scripts/gno-daemon.sh start
```

The daemon watches the `knowledge/` folder and indexes documents automatically. On first start, it will index all existing documents. This takes a few minutes depending on the number of files.

Check the status:

```bash
bash scripts/gno-daemon.sh status
```

Check the logs:

```bash
bash scripts/gno-daemon.sh logs
```

---

## Step 6 — Register cron jobs with OpenClaw

Run each of the following commands to register ABE's five heartbeat tasks:

```bash
# Daily price check — weekdays at 8:00 AM CT
openclaw cron add --agent abe --name "daily-price-check" \
  --cron "0 8 * * 1-5" --tz "America/Chicago" \
  --message "Run your daily price check heartbeat task." \
  --timeout-seconds 120

# Daily calendar reminders — every day at 7:00 AM CT
openclaw cron add --agent abe --name "daily-calendar-reminders" \
  --cron "0 7 * * *" --tz "America/Chicago" \
  --message "Run your daily calendar reminders heartbeat task." \
  --timeout-seconds 120

# Daily weather alerts — every day at 6:30 AM CT (growing season only)
openclaw cron add --agent abe --name "daily-weather-alerts" \
  --cron "30 6 * * *" --tz "America/Chicago" \
  --message "Run your daily weather alerts heartbeat task." \
  --timeout-seconds 180

# Weekly margin refresh — Mondays at 9:00 AM CT
openclaw cron add --agent abe --name "weekly-margin-refresh" \
  --cron "0 9 * * 1" --tz "America/Chicago" \
  --message "Run your weekly margin refresh heartbeat task." \
  --timeout-seconds 180

# Weekly crop progress — Mondays at 10:00 AM CT
openclaw cron add --agent abe --name "weekly-crop-progress" \
  --cron "0 10 * * 1" --tz "America/Chicago" \
  --message "Run your weekly crop progress heartbeat task." \
  --timeout-seconds 120
```

Verify all jobs are registered:

```bash
openclaw cron list
```

---

## Step 7 — Start the OpenClaw agent

Follow OpenClaw's documentation to connect the agent to your Telegram bot and start it. ABE's persona, behavior, and skill routing are defined in `SOUL.md`, `AGENTS.md`, and `HEARTBEAT.md` in the project root.

---

## Updating ABE

To update to a new version:

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

If the database schema changed, re-run the relevant seed scripts. If new documents were added to `knowledge/`, the daemon will detect and index them automatically.

---

## Verifying the installation

Run a quick smoke test on the core skills:

```bash
# Rental rate check
.venv/bin/python scripts/run_rental.py --county "Story" --quality medium

# Crop margin simulator
.venv/bin/python scripts/run_margin.py --crop corn --acres 200 --county "Linn County"

# Weather forecast
.venv/bin/python scripts/run_weather.py --mode forecast --county "Polk"

# Knowledge base query
gno query "FSA beginning farmer loan" -c abe-knowledge -n 3
```

Each command should return valid JSON with a data source cited.
