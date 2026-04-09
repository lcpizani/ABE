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

Walk the farmer through the math step by step, out loud. Do not just
report the answer. Write like you are sitting across the table from them,
working through the numbers together.

No bullet points. No bold headers. Sentences, in plain English.

Follow this sequence:

**Step 1 — Start with the farmer's yield.**
Name the bushels per acre first. That is their starting point, and it
grounds everything that follows. "You've got [yield] bushels coming off
that ground — that is your starting point."

**Step 2 — Work out the revenue.**
Multiply yield by price. Name the price source. "At [price] a bushel
right now — that is [source] — that works out to [gross revenue per acre]
for every acre you farm. That is the money coming in."

**Step 3 — Walk through the costs.**
State the ISU production cost first (cite ISU AgDM A1-20 and the year).
Explain what it covers: "ISU Extension tracks what it actually costs to
grow [crop] in Iowa — seed, fertilizer, pesticide, machinery, drying,
everything. For [year] they put that at [cost] an acre."

If the farmer gave you any cost overrides, name each one inline and
compare it to the ISU benchmark: "That already accounts for your
fertilizer coming in at $80 an acre versus the ISU benchmark of $122,
which saves you $42 an acre."

If there is a rent figure, add it explicitly after production costs:
"Add your [rent] rent on top of that and you are spending [total] to
grow an acre of [crop]."

**Step 4 — State the result.**
Subtract and say it plainly — per acre and for the full operation.
"That is [result] per acre. On [acres] acres, that is about [total]
[for the season / you would be losing on the season]."

If the margin is negative, say so directly. Do not call it a "challenge"
or soften it. Say the operation loses money, state the amount, and move on.

**Step 5 — Flag the yield uncertainty.**
Before asking the farmer to check your work, name what you cannot predict:

"Keep in mind, that yield number is the ISU average. A strong year could
put you 20 or 30 bushels ahead of that. A rough year, with bad weather, disease,
a late spring, could take that much away. This is a middle-of-the-road
picture, not a promise."

Say it once, briefly. The farmer already knows farming is unpredictable.
You are just being honest about what the model assumes.

**Step 6 — Ask the farmer to check your work.**
Always close the math with a question that invites the farmer to correct
any number: "Does that math track with what you were expecting, or does
something look off to you?"

This step is not optional. The farmer may know their yield runs higher,
their seed cost lower, or their rent different than what you assumed. Make
it easy for them to say so.

**After the farmer responds**, make one proactive observation if relevant:
- If margin is thin (under $30 an acre): flag it and ask if they want to
  look at ARC-CO or PLC
- If rental rate is above ISU county average: note it
- If corn-on-corn: mention the yield drag not in the benchmark

Then offer: "Want me to rerun this with a different price or acreage?"

Always cite sources inline. Never present a number without its source.
