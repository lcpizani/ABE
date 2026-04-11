---
name: cost-of-production
description: >
  Calculates a detailed, line-by-line cost-of-production breakdown for an
  Iowa corn or soybean operation using ISU AgDM A1-20 2026 benchmarks.
  Separates fixed vs. variable costs, shows per-acre and per-bushel totals,
  and shows each category as a % of total. The farmer can provide their own
  numbers for any input; ISU benchmarks fill in the rest. Use when a farmer
  wants to understand what they are spending, break down fixed vs. variable
  costs, or know their cost per bushel. Trigger phrases: "what does it cost
  to raise corn", "break down my production costs", "how much am I spending
  per acre", "what's my cost per bushel", "how do my costs compare to
  average". For profitability / margin questions, use crop-margin-simulator.
---

# Cost-of-Production Skill

## When to run this skill

Run this skill when:
- The farmer wants a detailed cost breakdown, NOT just a quick margin number
- The farmer asks about cost per bushel or per acre
- The farmer wants to compare their costs to the ISU benchmark
- The farmer wants to see fixed vs. variable split

Do NOT run this for simple "will it pencil out" questions — that is crop-margin-simulator.

## What you need

1. **Crop** — corn or soybeans. Ask if missing.
2. **Acres** — ask if missing.
3. **Rotation** — for corn: following soybeans (most common), following corn, or silage.
   For soybeans: always following corn. Ask if missing for corn.
4. **Yield tier** — low / mid / high (ISU statewide tiers). Default to mid.
   Ask only if the farmer mentions their yields are notably above or below average.

Optional but valuable:
- Any input costs the farmer already knows (seed, fertilizer, rent, etc.)
- Expected price per bushel (to show net return at the end)

Collect missing required inputs one question at a time.

## How to ask about costs — section by section

Walk through these sections in order. For each one, ask if the farmer knows
what they pay. If they do, capture it. If they say they don't know or want
the ISU default, note it and move on.

Keep it conversational. Do not read out a list of questions. One thing at a time.

### Section 1 — Pre-harvest Machinery
> "Do you know roughly what you're spending on pre-harvest machinery — 
> that's your tillage, planting equipment, field operations — on a per-acre basis?
> ISU's benchmark is about $59 an acre for corn [mid tier]."

If they don't know → use ISU default, note it.

### Section 2 — Seed & Inputs
This is the biggest variable section. Ask by input:

**Seed:**
> "How much are you paying for seed? ISU has corn seed at about $114 an acre
> [30,000 kernels at $3.79 per 1,000] for the mid tier."

**Fertilizer (corn only — ask each if they know it):**
> "What about nitrogen? ISU has 159 pounds at $0.53 per pound — $84 an acre."
> "Phosphate? ISU has 79 pounds at $0.72 per pound — about $57 an acre."
> "Potash? ISU has 63 pounds at $0.39 per pound — $25 an acre."

For soybeans, skip nitrogen. Soy benchmark: P $35, K $36, lime $4.

**Herbicide:**
> "What are you spending on herbicide? ISU has $56 an acre for corn herbicide."

**Crop insurance:**
> "Do you carry crop insurance? ISU uses $17 an acre for 80% RP in Central Iowa."

If they don't know any of these → use ISU defaults, note each one.

### Section 3 — Harvest Machinery
> "What does harvest run you — combine, grain cart, hauling, drying if you dry on-farm?
> ISU has total harvest machinery at about $137 an acre for corn [mid tier]."

If they dry commercially or don't dry, ask whether to include or remove the drying line.

### Section 4 — Labor
> "How many hours does it take you to farm an acre, and what do you pay yourself or
> hired help? ISU uses 2.55 hours at $20.40 per hour — $52 an acre."

### Section 5 — Land
> "What are you paying in cash rent? ISU's 2026 benchmark is $274 an acre statewide."

If they own the ground:
> "Do you want to use your ownership cost (taxes, insurance, opportunity cost),
> or should I use the ISU cash-rent equivalent of $274 an acre for comparison?"

## Running the calculation

Run this command via exec:

```
.venv/bin/python scripts/run_cost_production.py --crop CROP --acres N [--rotation R] [--tier low|mid|high] [--price P] [--override KEY=VALUE ...]
```

Do not read the script or inspect its source. Just run the command with the parameters collected from the farmer.

Required inputs:
- `crop` — `"corn"` or `"soybeans"`
- `acres` — number

Optional inputs:
- `rotation` — `"following_soybeans"` (default corn), `"following_corn"`, `"silage"`,
  or `"following_corn"` for soybeans
- `yield_tier` — `"low"` | `"mid"` (default) | `"high"`
- `price_per_bu` — $/bu for net-return calculation
- `farmer_overrides` — `{cost_category: actual_$/acre}` for any input the farmer gave.
  Keys: `seed`, `nitrogen`, `phosphate`, `potash`, `lime`, `herbicide`,
  `crop_insurance`, `miscellaneous`, `interest`, `labor`, `cash_rent`,
  `drying`, `haul`, `combine`, `grain_cart`, `handle`, `preharvest`.
  Unknown keys are ignored.

## How to present the result

Present the output as a structured cost report. Do NOT dump raw numbers.
Walk the farmer through it like you are reviewing it together.

No bullet points for the numbers. Use plain sentences. The table format below
is acceptable only if you set it up with a short narrative first.

### Structure of the report

**Open with the operation setup:**
"Alright — here is the breakdown for your [crop] operation.
I used ISU's [yield_tier]-tier assumptions for [year] — [yield] bushels an acre.
[Note which inputs you used ISU defaults for, and which the farmer provided.]"

**Section-by-section breakdown:**
Go through each section briefly. Name the total, name whether ISU or farmer-provided.
For any override, tell the farmer explicitly how their number compared to the benchmark.

Example:
"Pre-harvest machinery: $59.40 an acre — $34.80 fixed, $24.60 variable. That is the ISU number."
"Seed: you said $95 an acre versus the ISU benchmark of $114 — that saves you $19 an acre."
"Fertilizer: you told me $70 for nitrogen — ISU has it at $84. That's $14 an acre lower."

**Summary totals:**
Present in this order:
1. Total fixed costs per acre
2. Total variable costs per acre
3. Total cost per acre
4. Cost per bushel
5. (If price given) Gross revenue per acre
6. (If price given) Net return per acre and for the full operation

**Benchmark comparison:**
If any overrides were applied, sum up total savings per acre vs. ISU.
"Across all your adjustments, you're running about $XX an acre below the ISU
benchmark — that works out to $XX,XXX across the operation."

If no overrides:
"This uses ISU benchmarks throughout. If you know you're paying more or less
for any of these, we can adjust the numbers."

**Cost breakdown percentages:**
After the totals, briefly name the two or three biggest cost categories
and their share of total. Always mention land separately.

Example:
"The biggest pieces of that $912 an acre: seed, fertilizer, and chemicals together
are $390 (43%), land is $274 (30%), harvest machinery is $137 (15%)."

**If price was provided — net return:**
"At $4.50 a bushel and 211 bushels an acre, you're bringing in $950 an acre.
After $912 in total costs, that leaves $38 an acre — about $19,000 over the season."

If net return is negative, say so directly. Do not soften it.

**Close by inviting corrections:**
"Does any of that look off based on what you actually see in your bills?
If something is significantly higher or lower, tell me and I'll rerun it."

## After the farmer responds

If the margin is tight (under $30/acre) or negative:
- Flag it and offer to stress-test the numbers (what price is needed to break even?)
- Mention: "Want me to run the crop-margin simulator with this cost structure to see
  where the break-even price lands?"

If they want a profitability picture:
- Offer to pass these costs into the crop-margin skill for a quick margin read.

Always cite ISU AgDM A1-20 and the year for every benchmark you use.
