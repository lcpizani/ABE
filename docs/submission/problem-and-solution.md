# Research and Problem Identification

## Problem Statement

Iowa's beginning farmers — those in their first ten years of operation — face a structural knowledge gap that costs them money, causes poor decisions, and drives many out of farming entirely.

The guidance they need exists. Iowa State University Extension publishes detailed cost-of-production benchmarks, county cash rent surveys, and program explainers. USDA runs loan programs specifically for beginning farmers. Iowa offers its own financing tools. But this information is scattered across dozens of publications, federal agency offices, and county extension staff who each serve hundreds of farms. The farmer trying to decide whether to sign a lease or apply for an FSA loan has no single place to go, no one who knows their specific situation, and no way to get a fast, grounded answer without either paying a consultant or waiting weeks.

This is not a niche problem. It is the normal experience of every beginning farmer in Iowa.

### The scale of the problem

| Indicator | Value |
|---|---|
| Iowa farms | ~85,000 |
| Average Iowa farmer age | 57+ years |
| Beginning farmers (under 10 years) | ~17% of Iowa operators |
| Average hourly rate for a farm management consultant | $150–$300 |
| ISU Extension agents per county | 1–2 (serving hundreds of operations) |

Beginning farmers are disproportionately likely to be renting ground, carrying debt, and operating on thin margins — the exact profile where a wrong rent decision, a missed program deadline, or a misidentified disease can determine whether the operation survives its first five years.

---

## Relevance to Iowa

Iowa is the most agriculturally productive state in the country by total output value, and corn and soybeans dominate its landscape — roughly 23 million acres planted annually. The economics of Iowa farming are specific: cash rent is the dominant tenure arrangement, ISU Extension's county-level benchmarks are the authoritative standard for rent and costs, and state-specific programs like the Iowa Beginning Farmer Loan Program and Loan Participation Program exist precisely because the federal system is not sufficient on its own.

Generic agricultural AI tools miss this entirely. A tool trained on national averages cannot tell a farmer in Linn County whether $290/acre is fair for medium-quality ground. It cannot retrieve the BFLP interest rate for this year. It cannot flag that a farmer with four years of experience may still qualify for the Iowa Beginning Farmer Tax Credit if their landlord doesn't know about it.

ABE is built specifically for Iowa. Every benchmark, every program document, every county lookup is Iowa-specific. That specificity is the product.

### Iowa-specific data ABE uses

- ISU Extension C2-10 cash rental benchmarks for all 99 Iowa counties
- ISU Extension A1-20 (2026) cost-of-production estimates for corn and soybeans
- Iowa Beginning Farmer Loan Program (BFLP) and Loan Participation Program (LPP) documents
- Iowa Finance Authority / IADD beginning farmer program materials
- USDA FSA Iowa-specific program documents
- USDA NASS Iowa annual crop prices and yields
- USDA AMS MARS daily Iowa cash grain prices
- Open-Meteo weather data resolved to Iowa county coordinates

---

## Proposed Solution Overview

ABE (Agricultural Business Expert) is a conversational AI agent that gives Iowa beginning farmers fast, sourced answers to the business questions that shape their operations — through Telegram, which farmers already use.

When a farmer asks ABE a question, ABE:

1. Identifies what the farmer needs
2. Routes to the appropriate skill (a calculation, a database lookup, a document search, or a photo analysis)
3. Returns a specific answer with the source named inline
4. Notices what the answer implies and offers one natural follow-up

ABE does not estimate. Every number it gives comes from a named source: an ISU Extension publication, a USDA dataset, or a live market API. If the data is unavailable, ABE says so.

### What makes this different from a chatbot

A generic chatbot answers from training data — which means it averages across all geographies, all years, and all contexts. ABE answers from a structured local database and a curated document index. The difference is the difference between "Iowa corn production costs are around $600–$700/acre nationally" and "ISU A1-20 (2026) puts total corn production costs at $X/acre for your yield tier in Iowa — here's the line-item breakdown."

### The tracks this addresses

ABE was built for two Pi515 competition tracks:

- **Sustainable Practices in Agriculture** — ABE connects beginning farmers to conservation cost-share programs (EQIP, CSP), helps them understand whether their operation is financially sustainable at current rent and price levels, and flags disease pressure before it spreads.
- **Fair and Resilient Finance** — ABE democratizes access to farm business guidance that currently requires either expensive consultants or knowing the right extension agent. It surfaces FSA loans, Iowa state financing programs, and fair-rent benchmarks for farmers who would otherwise not know these tools exist.

---

## Related documentation

- [What ABE Covers](for-partners/what-abe-covers.md) — full skill reference
- [Knowledge Sources](for-partners/knowledge-sources.md) — every data source ABE uses
- [Impact and Feasibility](impact-and-feasibility.md) — estimated impact and scale analysis
