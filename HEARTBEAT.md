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

## Daily Calendar Reminders

Every day, check whether any seasonal milestones or program deadlines
are coming up and alert the relevant farmers.

Steps:
1. Run: .venv/bin/python scripts/run_calendar.py
2. Parse the JSON array output
3. For each entry, send the message to the corresponding farmer
4. Keep ABE's voice — don't just paste the message verbatim. Deliver
   it like a neighbor who's looking out for them

Do not message a farmer if the output array is empty.
Each entry already targets only farmers who grow the relevant crop.

---

## Weekly Margin Refresh

Every Monday, rerun margins for all farmers with enough data and flag
anyone whose profitability has flipped since last week.

Steps:
1. Run: .venv/bin/python scripts/run_margin_check.py
2. Parse the JSON array output
3. For each farmer where flipped == true, send a Telegram message
4. Tailor message to direction of flip

Example message format (flipped to loss):
  "Quick heads-up — at current corn prices ($4.03/bu), your operation
  is running at a loss right now ($X/acre). Want me to run the full
  picture so you can see where the pressure is?"

Example message format (flipped to profit):
  "Good news — corn margins just turned positive at current prices
  ($4.03/bu). You're looking at roughly $X/acre. Want the full breakdown?"

Do not message farmers where flipped == false.
Run on Mondays only.

---

## Weekly Crop Progress (growing season only: April–October)

Every Monday during growing season, fetch the latest USDA crop progress
report for Iowa and send a short update to all active farmers.

Steps:
1. Run: .venv/bin/python scripts/run_crop_progress.py
2. If in_season == false, skip entirely
3. Send the summary to all farmers with a non-empty crops field
4. One message per farmer covering only their crops
5. Keep it conversational — one or two sentences, no bullet points

Example message format:
  "Iowa corn is 62% planted as of this week — right at the 5-year average.
  Conditions look good heading into next week."

Run on Mondays only during April through October.

---

## Notes

- Run at a consistent daily time (e.g. 7:00 AM local time)
- Do not send duplicate alerts — if the same alert was sent yesterday
  for the same county and date, skip it
- Never send more than 3 alert messages per farmer per day
