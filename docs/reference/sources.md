# Sources

All sources used in ABE's research, knowledge base, data, and development.

---

## Background research

Sources used to establish the problem statement and scope.

| Claim | Source |
|---|---|
| Iowa has approximately 85,000 farms | USDA National Agricultural Statistics Service (NASS) — 2022 Census of Agriculture |
| Average Iowa farmer age is 57+ years | USDA NASS — 2022 Census of Agriculture |
| Beginning farmers represent ~17% of Iowa operators | USDA NASS — 2022 Census of Agriculture |
| Iowa ranks first in total agricultural output value | USDA Economic Research Service (ERS) |
| Iowa plants roughly 23 million acres of corn and soybeans annually | USDA NASS — annual crop acreage reports |
| Farm management consultants charge $150–$300/hour | Iowa State University Extension industry references |
| ISU Extension agents serve hundreds of operations per county | Iowa State University Extension and Outreach staffing data |

---

## ISU Extension AgDM publications

Iowa State University Extension and Outreach's Ag Decision Maker series. These are the authoritative sources for Iowa-specific farm financial benchmarks.

| Publication | File in `knowledge/` | What ABE uses it for |
|---|---|---|
| C2-10 — Cash Rental Rates for Iowa Survey | *(data parsed into `abe.db`)* | County-level rental benchmarks by quality tier for all 99 Iowa counties |
| A1-20 — Estimated Costs of Crop Production in Iowa (2026) | `a1-20.pdf` | Line-item cost benchmarks for corn and soybeans: seed, fertilizer, pesticide, machinery, labor, drying, insurance |
| A1-32 — ARC-CO and PLC Safety Net Programs | `a1-32-arc-plc-safety-net.pdf`, `a1-32-arc-plc-explainer-web.txt` | ARC vs. PLC comparison, decision logic, historical payments, plain-language explainer |
| A1-33 — ARC-CO and PLC Data and Methods | `a1-33-arc-plc-data-methods.txt` | Methodology for ARC-CO and PLC calculations |
| A1-39 — EQIP and CSP Conservation Programs | `a1-39-eqip-csp-conservation.pdf` | EQIP and CSP overview, payment rates, priority practices |
| C2-01 — Improving the Farm Lease Arrangement | `c2-01-improving-farm-lease.pdf` | What to include in a written lease, negotiation guidance |
| C2-03 — Do I Need a Written Lease? | `c2-03-do-i-need-written-lease.pdf` | Written vs. oral lease comparison and recommendations |
| C2-05 — Leasing Land: Ownership Terms | `c2-05-leasing-land-ownership-terms.pdf` | Terms and definitions for land leases |
| C2-13 — Building a Farm Resume | `c2-13-building-farm-resume.pdf` | How to approach a landlord and build a farm resume |
| C2-20 — Computing a Cash Rental Rate | `c2-20-computing-cash-rental-rate.pdf` | Methods for calculating a fair cash rent based on productivity, returns, and comparable sales |
| C2-21 — Flexible Cash Rent Lease Agreements | `c2-21-flexible-lease-agreements.pdf` | Flexible lease structure, trigger mechanisms, and examples |
| C3-70 — Farmland Financing Options for Beginning Farmers | `c3-70-farmland-financing-beginning-farmers.txt` | Financing pathways for beginning farmers purchasing land |

---

## USDA program documents

Federal sources covering FSA farm loans, EQIP conservation programs, and market data.

| Document | File in `knowledge/` | What ABE uses it for |
|---|---|---|
| FSA Beginning Farmer and Rancher Loans (fact sheet) | `fsa-beginning-farmer-loans.pdf` | Eligibility criteria, loan types, and rates for FSA farm ownership, operating, and microloans |
| FSA Farm Loan Programs Overview (2025) | `fsa-farm-loan-overview-2025.pdf` | Overview of all FSA farm loan programs and application guidance |
| FSA Beginning Farmer Loans (web) | `fsa-beginning-farmer-loans-web.txt` | Web text version of beginning farmer loan fact sheet |
| FSA Operating Loans (web) | `fsa-operating-loans-web.txt` | FSA operating loan program details |
| EQIP Advance Payment for Beginning Farmers | `eqip-advance-payment-beginning-farmers.txt` | 50% advance payment eligibility and process for beginning farmers |
| EQIP Iowa Program Page | `eqip-iowa-web.txt` | Iowa-specific EQIP practices and payment schedules |

---

## Iowa state program documents

Sources from Iowa Finance Authority (IFA) and the Iowa Agricultural Development Division (IADD) covering state-level beginning farmer financing programs.

| Document | File in `knowledge/` | What ABE uses it for |
|---|---|---|
| IFA / IADD Beginning Farmer Programs 2026 | `2026-IFA-IADD_Beginning-Farmers-Program.pdf` | Iowa beginning farmer program overview for 2026 |
| IFA / IADD Beginning Farmer Programs (detailed guide) | `fa-iadd-beginning-farmer-programs-2026.pdf` | Detailed 2026 program eligibility, rates, and structure |
| BFLP Summary | `bflp-summary.pdf` | Iowa Beginning Farmer Loan Program: loan amounts, interest rates, eligibility |
| BFLP FAQ | `bflp-faq.pdf` | Common questions about the Iowa Beginning Farmer Loan Program |
| BFLP Aggie Bond Pricing | `bflp-aggie-bond-pricing.pdf` | Tax-exempt Aggie Bond interest rates for BFLP |
| LPP Summary | `lpp-summary.pdf` | Iowa Loan Participation Program: structure and eligibility |
| LPP FAQ | `lpp-faq.pdf` | Common questions about the Iowa Loan Participation Program |
| BFLP/LPP — Financing a Facility | `iadd-bflp-lpp-financing-a-facility.pdf` | Using BFLP and LPP together for facility financing |
| Beginning Farmer Contract Sale Program | `beginning-farmer-contract-sale-program.pdf` | Contract sale structure and eligibility for beginning farmers |

---

## Corn disease management

Extension publications and research used to support the corn disease knowledge base and inform CornCNN2 diagnoses.

| Document | Source | File in `knowledge/` | What ABE uses it for |
|---|---|---|---|
| Northern Corn Leaf Blight (BP-84-W) | Purdue University Extension | `corn-blight-northern-purdue-bp84w.pdf` | Identification, management, and fungicide guidance |
| Northern Corn Leaf Blight (fact sheet) | Crop Protection Network (CPN) | `corn-blight-northern-cpn.txt` | Management recommendations |
| Southern Corn Leaf Blight (fact sheet) | Crop Protection Network (CPN) | `corn-blight-southern-cpn.txt` | Management recommendations |
| Common Rust | University of Minnesota Extension | `corn-common-rust-umn.txt` | Identification and management |
| Common Rust | University of Illinois Extension | `corn-common-rust-illinois.txt` | Supplemental identification guidance |
| Common Rust | University of Nebraska-Lincoln Extension | `corn-common-rust-unl.txt` | Regional management guidance |
| Grey Leaf Spot | ISU Extension | `corn-grey-leaf-spot-isu.txt` | Iowa-specific identification and management |
| Grey Leaf Spot | University of Minnesota Extension | `corn-grey-leaf-spot-umn.txt` | Supplemental guidance |
| Corn Lethal Necrosis | CIMMYT | `corn-lethal-necrosis-cimmyt.pdf` | Identification and management (threat awareness for U.S. corn production) |
| Corn Streak Virus | CIMMYT | `corn-streak-virus-cimmyt.pdf` | Identification and management |

---

## Live data APIs

Real-time and regularly updated data sources that ABE queries during each conversation.

| Source | Provider | What ABE uses it for | Update frequency |
|---|---|---|---|
| AMS MyMarketNews (MARS) | USDA Agricultural Marketing Service | Daily Iowa cash prices for corn and soybeans | Daily (weekdays) |
| QuickStats | USDA National Agricultural Statistics Service (NASS) | Annual Iowa corn and soybean prices and yield benchmarks; weekly crop progress reports | Annual / weekly in-season |
| Open-Meteo | Open-Meteo | Real-time weather history (14 days), 16-day forecast, and growing-season alerts for any Iowa county | Real-time, each query |

ABE caches the previous day's prices and prior week's margins. If a live API is unavailable, ABE falls back to the most recent cached CSV rather than estimating.

---

## Machine learning — CornCNN2

The corn disease detector used by ABE was developed by a prior SAU research team and integrated into ABE with their permission. Training data and tooling sources are listed here.

| Source | What it was used for |
|---|---|
| Corn leaf disease dataset(s) — Hugging Face | Labeled corn leaf photographs used for training and validation of the CornCNN2 model |
| Corn disease dataset(s) — Nelson Mandela Research Institute (×2) | Two additional labeled corn leaf disease datasets from the Nelson Mandela Research Institute used to supplement training data |
| PyTorch | Model architecture, training, and inference |
| torchvision | Image preprocessing, normalization, and augmentation |
| Pillow (PIL) | Image loading and format handling |

---

## Tools and software

Tools used to build and run ABE, not directly cited in responses but part of the system's foundation.

| Tool | Purpose |
|---|---|
| [Anthropic Claude Sonnet](https://anthropic.com) | Core LLM for conversation, routing, and response generation |
| [OpenClaw](https://openclaw.bot) | Agent runtime: Telegram integration, tool invocation, cron scheduling, memory file access |
| [gno](https://github.com/gmickel/gno) v0.30.0 | Document indexing and hybrid search (BM25 + vector) over the knowledge base |
| Qwen3-Embedding-0.6B-Q8_0 | Local embedding model used by gno for vector search |
| SQLite | Structured storage for ISU rental and cost benchmarks |
| Python 3 | Skill scripts, API clients, data processing |
| Open-Meteo | Weather API (no key required) |

---

## How ABE cites sources in conversation

ABE cites sources inline — not in footnotes — so the farmer always knows where a number came from before acting on it.

Examples:

> "According to ISU Extension C2-10, medium-quality ground in Story County rented for an average of $242/acre in 2025."

> "The ISU A1-20 (2026) puts total variable costs for corn at around $485/acre at mid-yield."

> "USDA NASS has the current Iowa corn price at $4.62/bushel."

If ABE cannot source a figure from the database, an API, or the knowledge base, it says so and refers the farmer to ISU Extension or the local FSA office. ABE does not estimate.
