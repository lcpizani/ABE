---
name: margin-calculator
description: Calculates gross revenue, production costs by category, and net margin per acre for corn or soybeans, then compares to ISU Extension benchmarks. Use when a farmer asks about profitability, net income, whether a crop is worth planting, break-even price, cash rent impact, or corn vs. soybean comparison.
---

# SKILL.md — Margin Calculator

## What This Skill Does

Calculates per-acre gross revenue, production costs broken down by category,
total costs including cash rent, and net margin — then compares the farmer's
numbers to the ISU Extension benchmark for that crop and year.

All cost figures come from `data/crop_costs.db`, which is seeded from ISU
Extension "Estimated Costs of Crop Production in Iowa." ABE never invents
a cost figure.

---

## When to Trigger

Trigger `calculate_margin()` any time the farmer asks about:

- Whether a crop is profitable or "worth planting"
- What their net income, net margin, or profit would look like
- How their operation compares to other Iowa farmers
- Whether their cash rent is eating into their margin
- What price they need to break even
- Corn vs. soybean profitability comparison
- Whether they can make money at a given yield or price

**Trigger phrases (not exhaustive):**

> "Is corn worth planting this year?"
> "What would my net be on 200 acres of beans?"
> "I'm paying $260 rent — can I still make money on corn?"
> "What's a good price to lock in for soybeans?"
> "How do I know if my operation is profitable?"
> "Will I break even?"
> "What's my margin look like?"

---

## Required Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `crop` | str | `"corn"` or `"soybeans"` |
| `acres` | float | Total acres for this crop |
| `yield_bu` | float | Expected or historical yield (bu/acre) |
| `price_per_bu` | float | Expected or contracted price ($/bu) |
| `rental_rate` | float | Cash rent per acre being paid |

**Collect inputs one at a time. Never ask more than one question per message.**

Use this order and these exact conversational prompts:

1. If crop is unknown: "What crop are you thinking about, corn or beans?"
2. If acres unknown: "How many acres are you looking at?"
3. If yield unknown: "What kind of yield do you usually pull on that ground?"
4. If price unknown: "What price are you working with? Got anything locked in or just going off the board?"
5. If rental rate unknown: "And what are you paying per acre in rent?"

If the farmer already gave some of this in their opening message, skip those
questions. Only ask what is still missing. Do not recap what they said before
asking the next question.

---

## What to Do With the Result

Use `MarginResult` fields to build a plain-language response:

1. **Lead with net margin per acre** and total margin across all acres.
2. **Show the cost breakdown** — seed, fertilizer, pesticide, machinery, labor,
   and other categories from `costs_by_category`.
3. **Compare to ISU benchmark** using `margin_vs_benchmark`. Call out whether
   the farmer is above or below benchmark and by how much.
4. **Name the source and year** — always cite `source` and `data_year` from the
   result.
5. If `net_margin_per_acre` is negative, say so plainly. Do not soften it.
6. Close any response where margin is negative or thin (< $30/acre) with a
   referral to an ISU Extension farm management specialist or FSA office.

---

## Example Response Shape

Write like you are talking, not reporting. No bold, no dashes, no headers.

> At 185 bushels and $4.25 a bushel, you are looking at $786.25 an acre in
> gross revenue. ISU puts production costs at $598 an acre for corn this year,
> and with your $250 rent on top of that, you are spending $848 to grow it.
> That is a loss of $61.75 an acre, or about $12,350 across your 200 acres.
>
> For context, ISU's benchmark margin on corn right now is around $70 an acre.
> You are running about $132 below that, mostly because of your rent and where
> prices are sitting.
>
> That is a tough number. Before you sign anything on that ground, it would be
> worth a call to your local ISU Extension office or FSA to see if ARC-CO or
> PLC changes the picture at all.
>
> Numbers from ISU Extension, Estimated Costs of Crop Production in Iowa, 2024.

---

## Skill Location

`skills/margin_calculator/calculator.py` — function `calculate_margin()`
