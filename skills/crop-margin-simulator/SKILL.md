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
5. Cost adjustments — optional. If the farmer mentions that any input costs
   differ from market (e.g. "I make my own fertilizer", "a friend gives me
   seed"), capture those as `cost_adjustments` before running.

Collect missing inputs one question at a time. Never ask more than one
question per message.

## Before running — ask about input costs

Once you have crop, acres, and county, ask this before calling the tool:

> "Do any of your input costs run significantly different from average —
> seed, fertilizer, that kind of thing? Or should I just run it on ISU
> benchmarks?"

If the farmer says no or tells you to just run it — proceed with ISU defaults.
If they mention specific numbers, capture those as `farmer_costs` and run with them.
If they mention a cost difference without a number (e.g. "I make my own fertilizer"),
ask for the $/acre before running.

This is the one question you ask about costs. Do not follow up with a full
category-by-category breakdown.

## Running the calculation

This skill is invoked through the `crop_margin_simulator` tool, which calls
`run_crop_margin()` in `skills/crop-margin-simulator/scripts/crop_margin.py`.

Required inputs:
- `crop` — `"corn"` or `"soybeans"`
- `acres` — number
- `county` — Iowa county name (e.g. `"Story County"`)

Optional:
- `price_override` — $/bu. Omit to use live USDA data.
- `farmer_costs` — dict of `{category: actual_$/acre}` for any input the farmer
  knows what they pay. Pass the farmer's real number — the skill computes the
  delta vs. the ISU benchmark automatically.
  Corn: `seed`, `fertilizer`, `pesticide`, `machinery`, `labor`, `drying`,
  `crop_insurance`, `miscellaneous`.
  Soybeans: same except no `drying`.
  Unknown categories are ignored.

The function returns a dict with 12 keys:
`crop`, `county`, `acres`, `price_per_bu`, `price_source`,
`gross_revenue`, `total_cost`, `net_margin`, `cost_source`,
`yield_bu_per_acre`, `year`, `farmer_cost_overrides`.

`farmer_cost_overrides` is a dict of `{category: {farmer_cost, isu_cost, savings_per_acre}}`
— use it to tell the farmer how each override compared to the ISU benchmark.

## How to present the result

The tool returns a dict. Build a plain-language response from it.

Write like you are talking to someone who works that ground, not like
you are filing a report. No bullet points. No bold headers. Sentences.

State in order:
1. Price per bushel and its source
2. Gross revenue for the whole operation
3. Total cost (cite ISU AgDM A1-20 and year). If `farmer_cost_overrides`
   is non-empty, note each one inline using `savings_per_acre`
   (e.g. "That already accounts for your fertilizer coming in at $80/acre
   versus the ISU benchmark of $122 — saving you $42/acre").
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
