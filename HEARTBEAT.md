# HEARTBEAT.md — ABE Autonomous Tasks

ABE checks this file on each heartbeat cycle and runs any active tasks.
Tasks run once per day unless marked otherwise.

---

## Daily Weather Alerts

Every day during growing season (April through October), check the weather
for every farmer with a known county and send an alert if conditions warrant.

Steps:
1. Read all files in memory/farmers/ — collect every farmer with a non-empty county field
2. For each farmer, run:
   .venv/bin/python scripts/run_weather.py --mode alerts --county "COUNTY"
3. If alert_count > 0, send the farmer a Telegram message with the alerts
4. Lead with the most severe alert (high before medium)
5. Keep it short — one or two sentences per alert, unprompted tone
6. Do not message the farmer if alert_count is 0

Outside growing season (November through March), skip this task.

Example message format:
  "Heads up — frost forecast for [county] Monday night, low of 28°F.
  If you have emerged corn, worth watching."

---

---

## Daily Price Check

Every weekday, check whether Iowa cash prices moved significantly and alert
farmers if so.

Steps:
1. Run: .venv/bin/python scripts/run_prices.py
2. Parse the JSON output
3. If any_significant == true, message every farmer whose crops field is non-empty
4. Report only the commodities that moved significantly
5. Keep it short — one sentence per commodity, include direction and amount

Example message format:
  "Corn cash dropped 12¢ today to $4.08/bu — worth keeping an eye on."
  "Soybeans up 8¢ to $10.88/bu at Iowa elevators today."

Do not message farmers if any_significant == false.
Do not send on weekends (Saturday/Sunday).

---

## Notes

- Run at a consistent daily time (e.g. 7:00 AM local time)
- Do not send duplicate alerts — if the same alert was sent yesterday
  for the same county and date, skip it
- Never send more than 3 alert messages per farmer per day
