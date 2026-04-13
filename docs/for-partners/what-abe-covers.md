# What ABE Covers

ABE answers questions across eight skill areas. Each skill draws on a specific data source or algorithm — ABE does not give general advice from training data alone.

---

## Skills

### Rental rate check
ABE looks up ISU Extension C2-10 county rental benchmarks for all 99 Iowa counties and tells a farmer whether a quoted rate is above average, at average, or below average for their county and land quality tier (high, medium, low).

**Example:** "Is $290/acre high for Story County medium-quality ground?"
ABE returns the ISU benchmark range for that county and quality tier, names the source, and tells the farmer plainly where their quote lands.

---

### Crop margin simulator
ABE calculates net margin per acre and total profit or loss for a corn or soybean operation. Inputs include acres, county, crop, and optional overrides for price, rent, and individual cost line items. Outputs show gross revenue, total cost, net margin, and the source of every input.

Live Iowa corn and soybean prices come from USDA AMS MyMarketNews (MARS). Yield benchmarks come from USDA NASS Iowa data. Cost benchmarks come from ISU A1-20 (2026).

**Example:** "Will 400 acres of corn in Linn County pencil out this year at $4.20?"

---

### Cost of production
ABE produces a detailed line-item cost breakdown — fixed costs (land, machinery, overhead) and variable costs (seed, fertilizer, pesticide, drying, crop insurance, labor) — for corn and soybeans using ISU A1-20 2026 benchmarks. Farmers can override any line item with their own numbers.

---

### Program screener
ABE walks farmers through the most relevant government programs for their situation:

- FSA Beginning Farmer loans (farm ownership, operating, microloan)
- EQIP conservation cost-share (including 50% advance payment for beginning farmers)
- ARC-CO vs. PLC farm bill program selection
- Iowa Beginning Farmer Tax Credit (landlord-side credit)
- Iowa Beginning Farmer Loan Program (BFLP)
- Iowa Loan Participation Program (LPP)

ABE surfaces eligibility criteria and program details from official documents. It does not make eligibility determinations — it presents criteria and lets the farmer decide whether to apply.

---

### Weather forecast
ABE provides three weather modes for any Iowa county using the Open-Meteo API (no API key required):

- **History** — past 14 days of temperature, precipitation, humidity, and wind, plus a summary of frost days and disease-pressure days
- **Forecast** — 16-day outlook with precipitation probability
- **Alerts** — flags specific growing-season thresholds: frost risk, heat stress, heavy rain, high wind, drought watch, and disease pressure

---

### Corn disease detector
A farmer sends a photo of a corn leaf. ABE runs it through a trained convolutional neural network (CornCNN2) and identifies the disease or confirms the plant is healthy.

Supported diagnoses:
- Northern corn leaf blight
- Southern corn leaf blight
- Common rust
- Grey leaf spot
- Lethal necrosis
- Streak virus
- Healthy

If the model confidence is below 60%, ABE asks for a clearer photo rather than guessing. After diagnosis, ABE automatically retrieves management and treatment guidance from the knowledge base.

---

### Budget planner
ABE models land strategy scenarios — renting vs. buying, different counties, different acreages, different crops — given a stated budget. Output compares scenarios by estimated net margin and cash flow implications.

---

### Knowledge base (program questions)
ABE searches a local index of ~41 authoritative documents using hybrid BM25 + vector search. This skill handles questions about government programs, lease agreements, farmland financing, and disease management that require a sourced, specific answer from an official publication.

---

## What ABE does not cover

- Livestock operations
- Multi-year financial projections
- Comprehensive Farm Bill analysis beyond ARC-CO/PLC
- Tax advice or tax return preparation
- Legal advice or contract review
- Formal eligibility determinations for any program
- States other than Iowa
- Crops other than corn and soybeans

See [Accuracy and Limits](accuracy-and-limits.md) for more detail.
