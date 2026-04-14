# Data Collection, Preparation, and Knowledge Base

This page covers where ABE's data comes from, how it was collected and prepared, and how to manage the knowledge base going forward.

---

## Data sources overview

ABE draws on four categories of data. Each is described below with its source, type, scope, and how it was collected.

### Structured benchmark data (SQLite)

**ISU Extension C2-10 — Cash Rental Rates for Iowa**

Iowa State University Extension publishes C2-10 annually based on a statewide survey of farm operators, landowners, and farm managers. We extracted the county-level data and loaded it into the `cash_rent` table in `data/abe.db` using `scripts/seed_cash_rent.py`.

- Type: Structured tabular data
- Scope: All 99 Iowa counties — average rent, high/medium/low quality tier benchmarks, CSR2 soil productivity score, corn and soybean yield averages
- Size: 99 rows, 12 columns
- Published at: [extension.iastate.edu/agdm](https://www.extension.iastate.edu/agdm)

**ISU Extension A1-20 — Estimated Costs of Crop Production in Iowa (2026)**

ISU Extension publishes A1-20 annually as an Excel workbook. We parse it using `scripts/update_data.py` (openpyxl) and load it into `crop_production_costs` in `data/abe.db`.

- Type: Structured tabular data (Excel)
- Scope: Line-item production costs for corn and soybeans across low, medium, and high yield tiers — seed, fertilizer, pesticide, drying, crop insurance, labor, machinery, overhead
- Size: ~300 rows across cost categories, crops, and yield tiers
- File: `knowledge/a1-20.xlsx`
- Published at: [extension.iastate.edu/agdm](https://www.extension.iastate.edu/agdm)

---

### Live market and weather data (APIs)

| Source | Type | Scope | Update frequency | Fallback |
|---|---|---|---|---|
| [USDA AMS MARS](https://mymarketnews.ams.usda.gov) | JSON (API) | Daily Iowa corn and soybean cash prices | Weekday daily | `data/mars_fallback.csv` |
| [USDA NASS QuickStats](https://quickstats.nass.usda.gov) | JSON (API) | Annual Iowa prices and yields; weekly crop progress | Annual / weekly (Apr–Oct) | `data/nass_fallback.csv`, `data/crop_progress_fallback.csv` |
| [Open-Meteo](https://open-meteo.com) | JSON (API) | Weather history and 16-day forecast for any Iowa county | Real-time (each query) | None — always live |

County names are resolved to lat/lon using `data/iowa_counties.json` (all 99 Iowa counties, compiled from USDA and Census geographic data).

---

### Corn disease image data (CornCNN2)

The disease detector model was trained on labeled corn leaf disease images from three sources: Hugging Face and two datasets from the Nelson Mandela Research Institute.

- Type: Labeled images (JPEG/PNG)
- Scope: Corn leaf images across seven classes (six diseases + healthy)
- Classes: Northern Corn Leaf Blight, Southern Corn Leaf Blight, Common Rust, Grey Leaf Spot, Lethal Necrosis, Streak Virus, Healthy
- Model: CornCNN2 — a custom PyTorch CNN. Architecture in `skills/corn-disease-detector/scripts/CornCNN.py`, weights in `parameters.pth`
- Confidence threshold: ABE requires ≥60% confidence before reporting a diagnosis

---

### Policy and guidance documents (knowledge base)

~41 publicly available documents from USDA, ISU Extension, Iowa Finance Authority, and university extension programs. All documents are free to access. See [Knowledge Documents](../reference/knowledge-documents.md) for the full inventory.

- Type: PDF and plain text
- Scope: FSA loans, Iowa BFLP/LPP, EQIP/CSP, ARC-CO/PLC, lease agreements, farmland financing, corn disease management
- Size: ~41 files, approximately 300,000 words of indexed content
- Indexing: Hybrid BM25 + vector search via the `gno` daemon (Qwen3-Embedding-0.6B embeddings)

---

### Data sharing

All data used by ABE is publicly available. No proprietary data is used.

| Dataset | Link |
|---|---|
| ISU Extension AgDM publications (C2-10, A1-20, etc.) | [extension.iastate.edu/agdm](https://www.extension.iastate.edu/agdm) |
| USDA NASS QuickStats | [quickstats.nass.usda.gov](https://quickstats.nass.usda.gov) |
| USDA AMS MyMarketNews | [mymarketnews.ams.usda.gov](https://mymarketnews.ams.usda.gov) |
| Open-Meteo weather | [open-meteo.com](https://open-meteo.com) |
| Corn leaf disease images (training data) | Hugging Face + Nelson Mandela Research Institute (×2 datasets) |
| Iowa counties coordinates | Included in repo: `data/iowa_counties.json` |
| Agricultural calendar | Included in repo: `data/ag_calendar.json` |
| Processed SQLite database | Included in repo: `data/abe.db` |

---

## How the knowledge base works

Documents in the `knowledge/` folder are indexed by the `gno` daemon using a hybrid approach:
- **BM25** for keyword relevance
- **Vector embeddings** (Qwen3-Embedding-0.6B) for semantic similarity

Both methods are combined and re-ranked to surface the most relevant content for each query. ABE then cites the specific document in its response.

---

## Adding a document

To add a new document to the knowledge base:

1. Drop the file into the `knowledge/` folder. Supported formats: `.pdf`, `.txt`, `.md`.
2. The daemon detects the new file within its next sync cycle and indexes it automatically.
3. No manual steps required.

If you want to use the helper script:

```bash
bash scripts/add_document.sh /path/to/your-document.pdf
```

This copies the file into `knowledge/` and logs the addition.

If the daemon is not running, index manually:

```bash
gno index
```

---

## Verifying a document was indexed

Check the daemon log for confirmation:

```bash
bash scripts/gno-daemon.sh logs
```

Look for a line showing the document was added and embeddings were generated. For example:

```
[sync] documents: 1 added, 0 updated, 40 unchanged, 0 skipped
[embeddings] generated for: your-document.pdf
```

You can also run a test query to confirm the content is retrievable:

```bash
gno query "topic from your document" -c abe-knowledge -n 3
```

---

## Updating an existing document

Replace the file in `knowledge/` with the new version, using the same filename. The daemon detects the change and re-indexes automatically.

If the document has a new name (for example, a newer edition of an ISU publication), add the new file and optionally remove the old one.

---

## Removing a document

Delete the file from `knowledge/`. The daemon removes it from the index on its next sync cycle.

**Important:** If ABE's responses currently cite that document, removing it means ABE can no longer source those answers. Verify that equivalent content exists in another document before removing.

---

## What types of documents work well

The knowledge base works best with:
- Official program fact sheets and eligibility summaries (PDF or TXT)
- ISU Extension AgDM publications
- USDA program web pages saved as text
- Plain-language summaries and FAQs

Avoid:
- Scanned PDFs without OCR (text is not extractable)
- Large spreadsheets (use the database for structured data instead)
- Documents with heavily formatted tables where context is lost without the structure

---

## Current document inventory

See [Knowledge Documents](../reference/knowledge-documents.md) for a full list of all currently indexed documents organized by category.

---

## Keeping documents current

Key documents to update annually:

| Document | Typical update cycle | What changes |
|---|---|---|
| ISU A1-20 (cost of production) | Each fall for the following crop year | Cost benchmarks |
| ISU C2-10 (cash rental rates) | Each fall | County rental benchmarks |
| FSA program fact sheets | When USDA issues updates | Loan limits, interest rates |
| Iowa BFLP/LPP documents | When IFA/IADD issues updates | Program terms, rates |

When you update a document, re-seed the database if the document feeds structured data:

```bash
# After updating a1-20.xlsx:
.venv/bin/python scripts/update_data.py
.venv/bin/python scripts/seed_costs.py

# After updating C2-10 data:
.venv/bin/python scripts/seed_cash_rent.py
```
