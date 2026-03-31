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

Walk the farmer through the comparison step by step. Do not just report
high/low/fair. Explain where the benchmark comes from and let them see
the full picture before you give a verdict.

No bullet points. No bold headers. Sentences, in plain English.

Follow this sequence:

**Step 1 — Name the benchmark and its source.**
State what ISU Extension found for their county and quality tier,
including the full range and the average. Name the source:
"ISU Extension surveyed cash rents across Iowa for 2025. For
[quality]-quality ground in [county], they found rents running from
[low] to [high] an acre, with most ground changing hands around [avg]."

**Step 2 — Compare their number to the range.**
If they gave you a quoted rate, place it in the range explicitly.
Do not just say "above average" — say where in the range it lands
and by how much: "At [their rate], you are [X] above the county
average and [Y] below the top of the range" or "You are paying about
[X] more than most people in your county for that quality of ground."

If their rate is below average, note that too. A below-average rate
is not automatically good news — it may reflect ground quality or
a long-term lease that could be repriced.

**Step 3 — Ask whether that matches what they expected.**
Before offering a next step, give the farmer a chance to confirm or
correct the picture: "Does that match what you were expecting, or is
there something about this ground that might put it in a different
category?"

**Step 4 — Offer a natural next step.**
- If rate is above average or high: "Want me to run the margin to see
  if it still pencils out at that rent?"
- If rate is fair or below: "Want me to run the full margin to see
  where you stand overall?"

Always cite the source at the end: ISU Extension AgDM C2-10, 2025 survey.
