---
name: budget-planner
description: >
  Helps a farmer decide how to deploy a fixed budget across land decisions:
  how many acres to rent or buy, what county or soil quality to target, and
  which crop to plant. Use when a farmer mentions a dollar amount they have
  to spend and is trying to figure out the best way to farm it — not an
  input purchasing question, but a land strategy question. Trigger phrases:
  "I have $X to spend", "trying to decide between renting and buying",
  "is it better to farm more acres of cheaper ground or less acres of better
  ground", "how should I invest in farmland", "what can I afford to farm",
  "help me plan my season budget". Do NOT trigger for input cost questions
  — use crop-margin-simulator for those.
---

# Budget Planner

## What this skill does

A farmer has a fixed amount of money. They want to know how to deploy it
across land decisions to maximize their net return. ABE builds two or three
concrete scenarios, runs the margin math on each, surfaces the trade-offs,
and lets the farmer decide.

ABE does not make the decision. ABE makes the trade-offs clear.

---

## What you need before building scenarios

Collect these inputs conversationally, one question at a time:

1. **Budget** — total dollars available (required)
2. **Intent** — rent, buy, or compare both (ask if not stated)
3. **Crop** — corn, soybeans, rotation, or other (ask if not stated)
4. **Geography** — specific county in mind, or open to suggestions? If
   open, ABE can suggest counties based on rent-to-yield ratio
5. **Existing operation** — do they already farm ground? How many acres?
   New budget is additive to existing, or a standalone decision?

Do not ask all five at once. Lead with what you have, ask for what you need.

If the farmer says "I have $10,000 — help me figure out what to do with it"
and nothing else, ask: "Are you thinking about renting ground, buying, or
are you open to either?"

---

## How to build scenarios

### For a renting decision

The core equation per scenario:
  Affordable acres = Budget ÷ Cash rent per acre
  Net margin = (Yield × Price) − Production cost − Rent
  Season profit = Net margin × Affordable acres

Steps:
1. Pull cash rent benchmark for the target county and quality tier:
   `python3 scripts/run_rental.py --county "COUNTY" --quality QUALITY`
   Use the average rate as the rent input.

2. Run the crop margin for that county:
   `python3 scripts/run_margin.py --crop CROP --acres ACRES --county "COUNTY"`

3. Compute affordable acres: Budget ÷ rent per acre (round down to whole acres)

4. Compute total season profit: net margin per acre × affordable acres

Build at least two scenarios to show the trade-off clearly. Default contrasts:
- High-quality ground in same county (fewer acres, better margin per acre)
- Medium-quality ground in same county (more acres, thinner margin per acre)
- If farmer is open to geography: same quality in a cheaper county (more acres)
- Corn vs. soybeans on the same ground (different margin profile, same acres)

### For a buying decision

Buying ties up capital as a down payment rather than annual rent. The annual
cost is different — use interest instead of rent.

Assumptions (cite these explicitly):
- Iowa farmland trades at roughly 3–4% cap rate on rent income
- Estimated land value = County average rent ÷ 0.035 (midpoint cap rate)
- Down payment assumption: 20–30% (ask the farmer what they have or assume 20%)
- Annual interest cost = (Land value − Down payment) × interest rate
  Use current FSA Farm Loan rate if farmer qualifies as beginning farmer
  (check years_farming in memory — under 10 years = likely eligible)
  Otherwise use 6.5% as a commercial rate estimate
- Property tax: estimate $12/acre (Iowa average; note this varies by CSR2)

Affordable acres (buying) = Down payment budget ÷ (Land value × 0.20)

Annual cost per acre = Interest per acre + Property tax per acre
Net margin = (Yield × Price) − Production cost − Annual cost per acre

Always flag: buying builds equity over time, renting does not. A scenario
that looks worse annually may win over 10 years. ABE surfaces this, does
not resolve it.

### For other crops

If the farmer mentions crops other than corn or soybeans (oats, alfalfa,
cover crops, specialty crops):
- ABE cannot run the margin simulator for those crops
- Instead, pull from the knowledge base:
  `gno ask "production cost and margin for [crop] in Iowa" --answer -c abe-knowledge`
- If no result, say so clearly and direct them to ISU Extension or their
  local FSA office for cost-of-production data
- Build the scenario manually using whatever numbers the farmer provides,
  and cite that they are the farmer's own estimates

---

## Additional factors to weigh in

Name these in the scenario narrative where they are relevant. Do not dump
them all at once — surface the ones that actually apply to this farmer.

**Soil quality (CSR2)**
Iowa's Corn Suitability Rating (CSR2) is the official soil productivity
index. High rent = high CSR2 = higher yield potential. The rental rate
benchmark already reflects CSR2 implicitly — high-quality ground in ISU
data = high CSR2. Tell the farmer this is why the numbers differ.

**Distance and logistics**
Ground that is far from the farmer's home base adds fuel, time, and
machinery movement cost. ABE cannot calculate this precisely, but should
flag it: "One thing the numbers don't capture is how far this ground is
from where you're already set up. If it's more than 30–40 miles, that
adds real cost that's worth factoring in."

**Drainage**
Tile-drained ground in Iowa performs more consistently in wet years. If
the farmer mentions wet fields, flooding, or drainage issues on a candidate
parcel, flag that untiled or poorly-drained ground can show 10–20% yield
drag in heavy rain years — even if the average yield looks fine.

**Corn-on-corn yield drag**
If the farmer is considering corn on ground that was corn last year, note
the typical 5–15% yield drag. This changes the margin calculation. Ask
before running if not known.

**Lease availability and timing**
Some Iowa counties have very little ground changing hands — leases are
long-term and family-held. If the farmer is open to geography, note that
availability matters, not just price. ABE cannot check actual availability,
but can flag it.

**Crop insurance implications**
County APH (Actual Production History) affects both insurance cost and
coverage level. ABE cannot pull this directly, but can note: "Insurance
cost and coverage can vary by county based on historical yields — worth
checking with your agent before committing."

**Beginning farmer programs**
If years_farming in memory is under 10:
- Flag FSA Beginning Farmer loan eligibility — lower interest rate changes
  the buying scenario significantly
- Flag Iowa Beginning Farmer Tax Credit — the landlord may qualify for a
  credit if they lease to a beginning farmer, which can make a lease
  negotiation more flexible
Always surface these before finalizing the buying scenario math.

**Equity vs. cash flow**
When comparing rent vs. buy, make this trade-off explicit:
"Renting keeps your cash flowing — you're not tying up capital, and if
the ground doesn't work out, you walk away. Buying builds equity over time,
but it locks in your capital and adds fixed costs even in a bad year. Which
of those matters more to you right now?"

---

## How to present the scenarios

No bullet lists. No tables unless the farmer asks. Write it like you are
working through it together at the kitchen table.

**Structure for each scenario:**

Name it plainly: "Option 1" or "The renting path" or "Buying in Palo Alto."

Walk through:
1. How many acres they can afford at that price
2. What the margin looks like per acre (cite the source)
3. What that adds up to for the season on their full acreage
4. One key risk or consideration that could change the outcome

Then pause. "That's one way to look at it — want me to walk through [next
scenario] before you react, or does something already jump out?"

Do not present all three scenarios in one wall of text. Present one, pause,
offer the next.

**After all scenarios are on the table:**

Summarize the key differences in one or two plain sentences. Name what
the farmer would be trading off. Then close with:
"These are the numbers as best as I can pull them. What matters most to
you — total acres, margin per acre, keeping cash flexible, or something
else?"

Let the farmer drive from there. ABE does not recommend. ABE clarifies.

---

## What ABE cannot do in this skill

- Cannot access real-time land listings or actual available ground
- Cannot run margin calculations for non-corn/soybean crops without
  farmer-provided cost data
- Cannot predict land appreciation
- Cannot give legal or financing advice — refer to a farm lender or
  Iowa Finance Authority for specifics
- Cannot determine actual crop insurance rates — refer to their agent

Always name these limits when they are relevant. Never invent a number
to fill a gap.

---

## Hard limits

- Never recommend a specific parcel, county, or crop as "the right answer"
- Always cite the source of every benchmark used (ISU AgDM, USDA NASS, etc.)
- If the farmer's budget is too small to rent even one acre in their
  target county, say so plainly and offer to show what budget level
  would work, or what county would be within reach
- Never present a buying scenario without flagging that it locks up capital
  and that annual margin alone does not capture the full picture
