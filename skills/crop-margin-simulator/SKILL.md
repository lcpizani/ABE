---
name: crop-margin-simulator
description: >
  Estimates net margin per acre and total profit or loss for an Iowa corn
  or soybean operation using ISU Extension cost-of-production data and
  live USDA NASS pricing. Use when a farmer explicitly asks about
  profitability, whether a crop will pencil out, what they can expect to
  make, break-even price, or whether their rent is too high relative to
  returns. Trigger phrases: "will corn pencil out", "what's my margin",
  "can I make money at this rent", "run my numbers", "what will I clear
  per acre", "what price do I need to break even". Do NOT trigger when
  a farmer is simply describing their operation. Do NOT trigger for rent
  comparison questions — use rental-rate-check for those.
---

# Crop Margin Simulator

## When to run this skill

Only run this skill when:
- The farmer has explicitly asked for a margin calculation, OR
- You offered to run the numbers and the farmer said yes

Never run this skill because the farmer mentioned acres or a price.
Mentioning numbers is not a request for analysis.

## What you need

1. Crop — corn or soybeans. Ask if missing.
2. Acres — ask if missing.
3. County — ask if missing. Used to pull county-specific rent benchmark.
4. Price per bushel — optional. If not given, live USDA data is used.

Collect missing inputs one question at a time. Never ask more than one
question per message.

## Running the calculation
```bash
python3 ~/abe/scripts/run_margin.py --crop CROP --acres ACRES --county "COUNTY"
```

If farmer provided a price:
```bash
python3 ~/abe/scripts/run_margin.py --crop CROP --acres ACRES --county "COUNTY" --price PRICE
```

## How to present the result

The script returns JSON. Build a plain-language response from it.

Write like you are talking to someone who works that ground, not like
you are filing a report. No bullet points. No bold headers. Sentences.

State in order:
1. Price per bushel and its source
2. Gross revenue for the whole operation
3. Total cost (cite ISU AgDM A1-20 and year)
4. Net margin — total and per acre

If net margin is negative, say so plainly. Do not call it a "challenge."
Say the operation loses money, state the amount, move on.

After the result, make one proactive observation if relevant:
- If margin is thin (under $30/acre): flag it and ask if they want to
  look at ARC-CO or PLC
- If rental rate is above ISU county average: note it
- If corn-on-corn: mention the yield drag not in the benchmark

Close with: "Want me to rerun this with a different price or acreage?"

Always cite sources inline. Never present a number without its source.
