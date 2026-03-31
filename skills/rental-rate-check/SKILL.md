---
name: rental-rate-check
description: >
  Checks whether a cash rent quote is fair, high, or low for a specific
  Iowa county and land quality tier using ISU Extension AgDM C2-10 2025
  survey data. Use when a farmer asks if their rent is fair, too high,
  too low, what typical rents are in their county, or whether they should
  negotiate. Trigger phrases: "is this rent fair", "what's typical rent
  in", "am I paying too much", "what should I be paying", "is $X an acre
  good for [county]". Do NOT trigger for general profitability questions
  — use crop-margin-simulator for those.
---

# Rental Rate Check

## What to do

When a farmer asks about rent, you need three things:
1. County — ask if missing
2. Land quality — high, medium, or low. If they say "good ground" that
   is high. "Average" is medium. "Poor" or "rough" is low. Ask if unclear.
3. Their quoted rate (optional — if they have one to compare)

Then run to test:
```bash
python3 ~/abe/scripts/run_rental.py --county "COUNTY" --quality QUALITY
```

Where QUALITY is: high, medium, or low.

If they gave you a quoted rate, add: --quoted RATE

## How to present the result

The script returns JSON. Use it to give a plain-language verdict.

Always state:
- The ISU benchmark for their county and quality tier (low/avg/high range)
- Whether their quoted rate is below, at, or above average
- The source: "ISU Extension AgDM C2-10, 2025 survey"

If their rate is above the high end of the range, say so plainly.
If their rate is below average, note that too — do not assume cheap is
always good (may signal lower quality ground).

After the verdict, offer one natural next step:
- If rate is high → "Want me to run the margin to see if it still
  pencils out at that rent?"
- If rate is fair → "Want me to run the full margin to see where you
  stand overall?"

## Example response shape

Write like you are talking, not reporting:

> ISU puts typical rent for high-quality ground in Linn County at
> $286–$360 an acre this year, with an average of $323. At $340,
> you are on the high end but still within the normal range.
>
> Want me to run your margin to see if that rent still works at
> current corn prices?
>
> Source: ISU Extension AgDM C2-10, 2025 survey.
