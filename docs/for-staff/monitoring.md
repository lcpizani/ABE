# Monitoring and Heartbeat

ABE runs five automated tasks on a cron schedule. This page explains what each task does, when it runs, and how to verify it is working.

---

## Heartbeat tasks

### Daily price check
**Schedule:** Weekdays at 8:00 AM CT
**Script:** `scripts/run_prices.py`

Fetches today's Iowa cash prices for corn and soybeans from USDA AMS MARS. Compares them to yesterday's cached prices. If either commodity moved by $0.05/bu or more, ABE sends a message to all farmers who have listed crops in their profile.

Output is a JSON object with:
- `date` — today's date
- `corn` and `soybeans` — price, previous price, delta, and whether the move was significant
- `any_significant` — whether any commodity triggered the threshold

**Fallback:** If MARS API is unreachable, ABE loads `data/mars_fallback.csv` and reports based on the most recent cached data.

---

### Daily calendar reminders
**Schedule:** Every day at 7:00 AM CT
**Script:** `scripts/run_calendar.py`

Reads `data/ag_calendar.json`, which contains seasonal milestones and FSA deadlines with their dates and a lookahead window. An entry fires when today falls within the lookahead window for that entry. ABE filters by each farmer's crop profile so only relevant reminders are sent.

Examples of entries in the calendar:
- Planting window opening (corn and soybeans)
- FSA ARC-CO/PLC election deadlines
- EQIP application windows
- Fall harvest milestones

---

### Daily weather alerts
**Schedule:** Every day at 6:30 AM CT (growing season: April through October)
**Script:** `scripts/run_weather.py --mode alerts`

Loops through all farmers with a known county. For each farmer, fetches the next 16-day forecast from Open-Meteo and evaluates against growing-season thresholds. If any threshold is triggered, ABE sends a message describing the most severe alerts.

Alert types:
| Alert | Trigger condition |
|---|---|
| `frost_risk` | Forecast low below 36°F during growing season |
| `hard_frost_planting` | Forecast low below 28°F near planting dates |
| `heat_stress` | Forecast high above 95°F |
| `heavy_rain` | Forecast precipitation above 2 inches in 24 hours |
| `high_wind` | Forecast wind above 35 mph |
| `drought_watch` | Less than 0.1 inch of rain in the past 14 days |
| `disease_pressure` | High humidity (>80%) combined with warm temperatures (65–85°F) for multiple consecutive days |

ABE uses `data/alerts_sent_cache.json` to avoid sending the same alert twice for the same county and date.

---

### Weekly margin refresh
**Schedule:** Mondays at 9:00 AM CT
**Script:** `scripts/run_margin_check.py`

Loops through all farmer memory files at `memory/farmers/`. For farmers with crops, acres, and county populated, runs the crop margin simulator using current prices. Compares the result to the previous week's cached margin in `data/margins_cache.json`.

If a farmer's operation crossed the profitable/unprofitable line since last week, ABE sends a message naming the direction and the margin per acre.

Output saved to `data/margins_cache.json` for next week's comparison.

---

### Weekly crop progress
**Schedule:** Mondays at 10:00 AM CT (growing season: April through October)
**Script:** `scripts/run_crop_progress.py`

Fetches the USDA NASS weekly Iowa crop progress report. Sends one message per farmer covering only their crops. Messages are conversational (1–2 sentences):

> "Iowa corn is 62% planted as of this week — right at the 5-year average."

**Fallback:** If NASS API is unavailable, ABE loads `data/crop_progress_fallback.csv`.

---

## Checking logs

### gno daemon logs
```bash
bash scripts/gno-daemon.sh logs
```

Or view directly:
```bash
cat logs/gno-daemon.log
cat logs/gno-daemon-error.log
```

### OpenClaw cron logs
Use OpenClaw's interface or CLI to view execution history for each cron job:

```bash
openclaw cron list
```

---

## Restarting the daemon

If the knowledge base stops responding to queries:

```bash
bash scripts/gno-daemon.sh restart
```

---

## Verifying cron jobs

List all registered cron jobs:

```bash
openclaw cron list
```

You should see five entries: `daily-price-check`, `daily-calendar-reminders`, `daily-weather-alerts`, `weekly-margin-refresh`, and `weekly-crop-progress`.

---

## Cache files

ABE maintains several cache files in `data/`. These are auto-managed — do not edit them manually.

| File | Purpose |
|---|---|
| `prices_cache.json` | Yesterday's corn and soybean prices for delta comparison |
| `margins_cache.json` | Last week's net margins per farmer for flip detection |
| `alerts_sent_cache.json` | Deduplication log for weather alerts |
| `nass_fallback.csv` | Annual NASS data backup |
| `mars_fallback.csv` | Daily MARS cash price backup |
| `crop_progress_fallback.csv` | Weekly crop progress backup |
