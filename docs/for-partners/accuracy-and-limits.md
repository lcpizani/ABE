# Accuracy and Limits

Understanding what ABE will and won't do is as important as understanding what it covers.

---

## What ABE will not do

**Give legal or tax advice.**
ABE will not review contracts, interpret lease terms as legal obligations, advise on tax strategy, or tell a farmer what to file. Questions that require a lawyer or CPA are redirected to those professionals explicitly.

**Make eligibility determinations.**
ABE presents program criteria. It does not tell a farmer they qualify or don't qualify for FSA loans, EQIP, ARC-CO/PLC, or Iowa state programs. That determination is made by the relevant agency. ABE helps farmers understand criteria before they contact an office.

**Generate financial figures without a source.**
Every dollar amount ABE gives comes from one of three places: the SQLite database (populated from ISU Extension benchmarks), a live API call (USDA NASS, USDA MARS, or Open-Meteo), or an indexed document in the knowledge base. If ABE cannot source a number, it says so.

**Estimate when data is unavailable.**
If a live API is unreachable and cached fallback data is stale, ABE tells the farmer what data it has and when it was last updated rather than filling in a guess.

**Override its own instructions.**
User messages cannot change ABE's core behavior. Instructions to ignore its guidelines, roleplay as a different system, or bypass source requirements are silently rejected.

---

## What ABE acknowledges as uncertain

- **Rent benchmarks are county averages.** ISU C2-10 data reflects county-level averages by quality tier. Actual rents for specific parcels vary based on drainage, CSR2 score, location, and lease history. ABE says this when presenting rent data.
- **Cost benchmarks are ISU estimates.** The A1-20 figures are Iowa averages. A farmer's actual costs for seed, fertilizer, and machinery will differ. ABE shows farmers how to override any line item with their own numbers.
- **Crop disease confidence thresholds.** The CornCNN2 model returns a confidence score. ABE will not report a diagnosis below 60% confidence. It asks for a clearer photo instead.
- **Yield data is historical.** Yield benchmarks from USDA NASS reflect historical Iowa averages. Actual yields depend on weather, management, and local conditions.

---

## Scope boundaries

| In scope | Out of scope |
|---|---|
| Iowa | Other states |
| Corn and soybeans | Livestock, specialty crops, other row crops |
| Current crop year | Multi-year projections |
| FSA, EQIP, ARC-CO/PLC, Iowa BFLP/LPP | Comprehensive Farm Bill or other federal programs |
| Beginning farmer guidance | General agronomy or veterinary questions |

---

## Data freshness

| Data | Update frequency |
|---|---|
| Iowa cash prices (MARS) | Daily (weekdays) |
| Crop progress (NASS) | Weekly (during growing season) |
| Weather | Real-time (each query) |
| ISU rental benchmarks (C2-10) | Annual — current dataset is 2025 |
| ISU cost benchmarks (A1-20) | Annual — current dataset is 2026 |
| FSA and Iowa program documents | Updated manually when new versions are released |

---

## How to report an error

If ABE gives a farmer incorrect information or cites a source inaccurately, contact the SAU Hive Mind team. Document the exact question the farmer asked and the response ABE gave.
