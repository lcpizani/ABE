# Heartbeat Tasks

ABE runs five autonomous tasks on a cron schedule via OpenClaw. These tasks monitor prices, margins, weather, and seasonal deadlines and send proactive messages to farmers without requiring a farmer to ask.

---

## How heartbeat tasks work

1. OpenClaw fires the cron job at the scheduled time.
2. The cron message triggers ABE, which reads the task description from `HEARTBEAT.md`.
3. ABE runs the appropriate Python script and receives JSON output.
4. ABE evaluates the output against thresholds (e.g., price move ≥ $0.05/bu).
5. If the threshold is met, ABE sends a Telegram message to the relevant farmers.
6. Cache files in `data/` are updated for the next cycle.

Each task is defined in `HEARTBEAT.md`. The cron schedule is registered with OpenClaw using `openclaw cron add` (see [Deployment](../for-staff/deployment.md#step-6--register-cron-jobs-with-openclaw)).

---

## Task reference

### daily-price-check

**Schedule:** Weekdays at 8:00 AM CT (`0 8 * * 1-5`)
**Script:** `scripts/run_prices.py`
**Timeout:** 120 seconds

Fetches today's Iowa corn and soybean cash prices from USDA AMS MARS and compares them to yesterday's prices (cached in `data/prices_cache.json`).

**Threshold:** Sends a message if any commodity moved ≥ $0.05/bu.

**Message target:** All farmers with crops listed in their profile.

**Output schema:**
```json
{
  "date": "2026-04-13",
  "corn": { "price": 4.35, "prev": 4.28, "delta": 0.07, "significant": true },
  "soybeans": { "price": 10.12, "prev": 10.09, "delta": 0.03, "significant": false },
  "any_significant": true
}
```

---

### daily-calendar-reminders

**Schedule:** Every day at 7:00 AM CT (`0 7 * * *`)
**Script:** `scripts/run_calendar.py`
**Timeout:** 120 seconds

Reads `data/ag_calendar.json`, which contains seasonal milestones and FSA deadlines. An entry fires when today falls within its lookahead window (configured per entry). Entries are filtered by each farmer's crop profile.

**Message target:** Farmers whose crops match the entry's crop filter.

**Output schema:**
```json
[
  {
    "telegram_id": "000000001",
    "name": "Jake",
    "entry_id": "fsa-arc-plc-election",
    "program": "ARC-CO/PLC",
    "type": "deadline",
    "message": "FSA ARC-CO/PLC election deadline is coming up on March 15..."
  }
]
```

**Updating the calendar:** Edit `data/ag_calendar.json` to add, remove, or adjust entries and lookahead windows.

---

### daily-weather-alerts

**Schedule:** Every day at 6:30 AM CT (`30 6 * * *`)
**Script:** `scripts/run_weather.py --mode alerts`
**Timeout:** 180 seconds
**Active:** Growing season only (April through October; ABE checks the current month before sending)

Loops through all farmers with a known county. For each, fetches the 16-day Open-Meteo forecast and evaluates alert thresholds. Sends the most severe alerts first. Uses `data/alerts_sent_cache.json` to avoid duplicate alerts for the same county and date.

**Message target:** Farmers with a county in their profile (during growing season).

---

### weekly-margin-refresh

**Schedule:** Mondays at 9:00 AM CT (`0 9 * * 1`)
**Script:** `scripts/run_margin_check.py`
**Timeout:** 180 seconds

Loops through all farmer memory files in `memory/farmers/`. For farmers with crops, acres, and county populated, runs the crop margin simulator using current prices. Compares the result to the previous week's margin in `data/margins_cache.json`.

**Threshold:** Sends a message if the farmer's operation crossed the profitable/unprofitable line since last week.

**Message target:** Farmers whose margin status flipped.

**Output schema:**
```json
[
  {
    "telegram_id": "000000001",
    "name": "Jake",
    "crop": "corn",
    "county": "Linn County",
    "acres": 320,
    "net_margin": -12.40,
    "prev_net_margin": 18.20,
    "delta": -30.60,
    "was_profitable": true,
    "is_profitable": false,
    "flipped": true
  }
]
```

---

### weekly-crop-progress

**Schedule:** Mondays at 10:00 AM CT (`0 10 * * 1`)
**Script:** `scripts/run_crop_progress.py`
**Timeout:** 120 seconds
**Active:** Growing season only (April through October)

Fetches the USDA NASS weekly Iowa crop progress report. Sends one conversational message per farmer covering only their crops.

Example message:
> "Iowa corn is 62% planted as of this week — right at the 5-year average."

**Fallback:** Loads `data/crop_progress_fallback.csv` if NASS is unavailable.

---

## Adding a new heartbeat task

1. Write the Python script in `scripts/`. The script should return JSON to stdout.
2. Add the task description to `HEARTBEAT.md`. Define what the task does, what it sends, and under what conditions.
3. Register the cron job with OpenClaw:
   ```bash
   openclaw cron add --agent abe --name "my-new-task" \
     --cron "0 8 * * *" --tz "America/Chicago" \
     --message "Run your my-new-task heartbeat task." \
     --timeout-seconds 120
   ```
4. Test manually before relying on the schedule:
   ```bash
   .venv/bin/python scripts/my_new_task.py
   ```
