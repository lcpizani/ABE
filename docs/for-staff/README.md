# For Staff

This section is for team members responsible for deploying, operating, or expanding ABE.

---

## What you'll find here

- [Deployment](deployment.md) — how to set up ABE on a new machine or VPS
- [Managing the Knowledge Base](knowledge-base.md) — how to add, update, or remove documents
- [Monitoring and Heartbeat](monitoring.md) — how cron jobs work, what they send, and how to check logs
- [Farmer Data and Privacy](farmer-data.md) — how farmer profiles are stored and what is never logged

---

## System overview for operators

ABE runs as an OpenClaw agent connected to a Telegram bot. It uses:

- A **SQLite database** (`data/abe.db`) for rental benchmarks and cost-of-production data
- A **local knowledge index** (managed by the `gno` daemon) that auto-indexes documents in the `knowledge/` folder
- **Five cron jobs** (registered with OpenClaw) that run autonomous heartbeat tasks: daily price alerts, daily calendar reminders, weekly margin checks, weekly crop progress, and daily weather alerts during the growing season
- **Three external APIs**: USDA NASS, USDA MARS, and Open-Meteo (no key required)

The system runs on Python 3 inside a virtual environment at `.venv/`. All scripts must be called with `.venv/bin/python`.

---

## Who to contact for technical issues

For infrastructure issues, consult the developer documentation or reach the SAU Hive Mind development team directly.
