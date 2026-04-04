---
name: weather-forecast
description: >
  Fetches historical weather and 16-day forecast for any Iowa county using
  Open-Meteo (no API key required). Use for: (1) explaining weather conditions
  behind a crop disease diagnosis, (2) answering farmer questions about how
  upcoming weather will affect crops, (3) proactive alerts via heartbeat for
  frost, heat stress, heavy rain, high wind, drought, or disease pressure.
  Trigger phrases: "what's the weather been like", "will this rain affect my
  corn", "is frost coming", "has it been wet enough for disease", "what should
  I watch out for this week".
---

# Weather Forecast Skill

## When to use this skill

**Automatically after a disease diagnosis:**
Always run `--mode history --days 14` after diagnosing a corn disease.
Connect the weather to the diagnosis without being asked.

**When a farmer asks about crop impact from weather:**
Run `--mode forecast` and map the results to their crop and growth stage.

**When a farmer asks about recent conditions:**
Run `--mode history` with an appropriate window (default 14 days, up to 30
for slower-developing issues like grey leaf spot).

**Heartbeat — daily proactive alerts:**
Run `--mode alerts` for every farmer with a known county. If alert_count > 0,
send a message. See Heartbeat section below.

## Running the skill

```bash
python3 scripts/run_weather.py --mode history  --county "COUNTY" --days N
python3 scripts/run_weather.py --mode forecast --county "COUNTY"
python3 scripts/run_weather.py --mode alerts   --county "COUNTY"
```

County can be bare ("Story") or with suffix ("Story County") — both work.

## What each mode returns

**history** — per-day: high/low temp °F, precipitation inches, max humidity %,
max wind mph. Plus summary: total precip, avg high, avg low, avg humidity,
avg wind, frost days count, disease_pressure_days count.

**forecast** — 16 days of: high/low °F, precip inches, precip probability %,
max humidity %, max wind mph, weathercode.

**alerts** — list of triggered thresholds with type, date, detail, severity.
Types: frost_risk, hard_frost_planting, heat_stress, heavy_rain, high_wind,
drought_watch, disease_pressure.

## How to present results

### After disease diagnosis (history mode)

Do not dump the table. Pull the numbers that explain the disease and say it
plainly. Lead with what the weather did, then connect it to what ABE found.

Example — after diagnosing blight:
> "Looking at the last two weeks in Palo Alto County: you had 6 days where
> humidity was above 80% and temps were in the upper 60s and 70s. That's
> exactly the window blight needs to move fast. The rain on April 2nd —
> nearly an inch — would have spread spores across the field if the canopy
> was wet for more than 6 hours."

Always name specific dates or conditions from the data. "Wet conditions"
is too vague. "Six days above 80% humidity between March 28 and April 3"
is useful.

### Crop impact from forecast (forecast mode)

Map the forecast to what the farmer actually grows. Use growth stage if
known (from memory file). If not known, estimate from planting date or
use Iowa average (corn: plant ~May 5, soybean: ~May 15).

Key mappings:

| Condition | Corn impact | Soybean impact |
|-----------|-------------|----------------|
| >95°F during pollination (July) | 3–8% yield loss per day | Pod fill stress |
| <32°F after emergence | Kill emerged seedlings | Same |
| >2" rain in 48h | Nitrogen leaching, flooding risk | Flooding, disease |
| 10+ dry days in July | Stress during grain fill | Pod abortion |
| Wind >35mph | Lodging risk after V6 | Lodging, pod shatter |

Present 3–5 days in plain English, not a table. Name the risk, connect it
to the farmer's crop, suggest one action if warranted.

Example:
> "Looking ahead — you've got a frost coming Monday night, low of 28°F.
> If you have corn in the ground already, that's cold enough to set back
> emerged seedlings. Worth keeping an eye on Tuesday morning to see if
> anything came through."

### Proactive alerts (heartbeat / alerts mode)

One message per alert. Do not dump the full list.
Lead with the most severe alert first (high before medium).
Keep it short — the farmer is getting this unprompted.

Example frost alert:
> "Heads up — frost forecast for [county] Monday night, low of 28°F.
> If you have emerged corn, worth watching."

Example disease pressure:
> "Conditions in [county] over the past two weeks have been favorable
> for fungal disease — 7 days of high humidity and temps in the 70s.
> If you haven't scouted recently, now's a good time."

Do not send an alert message if alert_count is 0.

## Connecting weather to programs and decisions

After presenting weather, offer one relevant connection if it applies:

- Heavy rain + high rent operation → "Want me to check if your margin
  still works if yield comes in 10% below average?"
- Drought watch → "USDA NASS has drought monitor data for Iowa — if this
  continues through July, ARC-CO payments could trigger. Want me to look
  at what that might mean for your county?"
- Frost during planting → "If you need to replant, that changes your
  break-even date. Want me to run the margin with a late-plant yield
  adjustment?"

## Hard limits

- Never make yield predictions from weather data alone. Frame as risk, not outcome.
- Never recommend specific fungicide products or application rates.
- If county is unknown, ask for it before running — do not default to a
  neighboring county.
- Data is from Open-Meteo (ERA5 reanalysis + ECMWF forecast). Cite as
  "Open-Meteo weather data" — do not claim NOAA or NWS as the source.
