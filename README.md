# ABE — Agricultural Business Expert

**An AI-powered business advisor for Iowa's beginning farmers.**  
Built by **SAU Hive Mind** for the [Pi515 AI Challenge 2026](https://pi515.org) · Track 1: Sustainable Agriculture · Track 2: Fair Financial Futures

---

## The Problem

Iowa has approximately 85,000 farms, and the average Iowa farmer is over 57 years old. Every year, thousands of beginning and transitioning farmers enter the industry facing a critical knowledge gap: they lack access to affordable, personalized business guidance.

When a beginning farmer needs to know whether a cash rent rate is fair, whether their corn margin makes sense this year, or what government programs they might qualify for, their options are limited. County extension agents serve hundreds of farmers each. Private farm management consultants charge $150–$300 per hour. Generic financial tools carry no Iowa-specific data. The result is that too many beginning farmers make expensive decisions without the information they need — and the numbers bear that out: the five-year failure rate for beginning farmers is 48.1%.

ABE is built to change that. Not by replacing professional advice, but by making a knowledgeable first conversation available to every Iowa farmer, for free, any time they need it.

---

## What ABE Does

ABE is a conversational AI agent that connects to farmers through Telegram. It answers real business questions about Iowa farm operations, grounded in Iowa-specific data sources — not national averages.

### 1. Rental Rate Check

A farmer tells ABE the county, land quality, and rate they're being quoted. ABE compares it against ISU Extension's annual county cash rent survey data, the statewide average, and the high/medium/low range for that county. It gives a plain-English verdict: is this rate fair, high, or low for this ground?

### 2. Crop Margin Simulator

A farmer inputs their acres, expected yield, current price, and rental rate. ABE calculates gross revenue, total cost of production broken down by category, and net margin per acre — all benchmarked against ISU Extension's A1-20 cost-of-production data for corn and soybeans. It answers the core question: *does this operation make money at these numbers?*

### 3. Cost of Production

A farmer asks for a detailed line-item breakdown of what it costs to raise corn or soybeans. ABE pulls from ISU AgDM A1-20 2026 benchmarks, separates fixed from variable costs, and computes cost per bushel. Farmers can override any individual input with their own numbers; ISU benchmarks fill in the rest. Designed for farmers who want to understand where their money goes, not just whether the bottom line is positive.

### 4. Program Eligibility Screener

A farmer describes their situation — age, years of experience, net worth, county, operation size. ABE runs a rule-based pre-filter against eligibility criteria, then queries its knowledge base of government program documents to return a ranked list of programs the farmer likely qualifies for, with recommended next steps. Programs covered: FSA Beginning Farmer loans, EQIP, Iowa Beginning Farmer Tax Credit, and ARC/PLC.

### 5. Weather Forecast

ABE pulls 14-day historical weather and a 16-day forecast for any Iowa county from Open-Meteo (no API key required). Three modes: history (explaining conditions behind a disease finding), forecast (mapping upcoming weather to crop impact), and alerts (proactive daily messages during growing season if frost, heat stress, heavy rain, or disease pressure conditions are detected).

### 6. Corn Disease Detector

A farmer sends a close-up photo of a corn leaf. ABE runs the image through CornCNN2, a CNN trained on the PlantVillage dataset, and returns a diagnosis with confidence level. Supported classes: northern/southern blight, common rust, grey leaf spot, lethal necrosis, streak virus, and healthy. After any diagnosis, ABE automatically runs 14-day weather history for the farmer's county and connects the conditions to the finding.

### 7. Budget Planner

A farmer has a fixed amount of money and wants to know how to deploy it across land decisions: rent vs. buy, which county, how many acres, which crop. ABE builds two or three concrete scenarios using ISU cost benchmarks and county rental data, runs the margin math on each, and surfaces the trade-offs. ABE does not recommend — it makes the trade-offs clear.

### 8. Knowledge Base (RAG)

ABE's local knowledge base covers FSA loans, EQIP cost-share, ARC-CO vs PLC program selection, Iowa Beginning Farmer Tax Credit, farmland financing, cash rent calculation, flexible lease agreements, and corn disease management. Searches use hybrid BM25 + vector retrieval (gno). Every answer cites the source document.

### How ABE Responds

ABE is not a generic chatbot. Every financial answer cites its source document. If a number isn't in the knowledge base or database, ABE says so rather than estimating. All financial outputs use temperature = 0. ABE always recommends professional consultation for major decisions. It is an educational tool, not a substitute for legal or financial advice.

---

## Architecture

ABE runs on [OpenClaw](https://openclaw.bot), a self-hosted AI agent runtime, deployed on an Oracle Cloud Always Free ARM instance. Farmers interact with ABE through a Telegram bot. The knowledge base uses gno, OpenClaw's hybrid BM25 + vector search indexer, which auto-indexes all files in the `knowledge/` directory.

```
Farmer (Telegram)
       │
       ▼
  OpenClaw Gateway  (Oracle Cloud ARM VPS — Ubuntu 22.04, 4 OCPUs, 24GB RAM)
       │
       ├── SOUL.md          ← ABE's persona, hard limits, voice
       ├── AGENTS.md        ← Routing logic, memory protocol, skill commands
       ├── HEARTBEAT.md     ← Proactive daily price + weather alerts
       │
       ├── Skill: abe-knowledge        ← gno RAG over knowledge/ documents
       ├── Skill: rental-rate-check    ← SQLite query + ISU benchmark
       ├── Skill: crop-margin-simulator ← Python calc + ISU A1-20 data
       ├── Skill: cost-of-production   ← Line-item ISU benchmark breakdown
       ├── Skill: program-screener     ← Rule filter + RAG
       ├── Skill: weather-forecast     ← Open-Meteo (history/forecast/alerts)
       ├── Skill: corn-disease-detector ← CornCNN2 image inference
       └── Skill: budget-planner       ← Land strategy scenarios
              │
              ├── SQLite DB (data/abe.db)
              │     ├── cash_rent          (ISU C2-10 county benchmarks)
              │     └── crop_production_costs  (parsed from ISU A1-20 Excel)
              │
              ├── knowledge/             (gno auto-indexed)
              │     ├── ISU Extension PDFs and text files
              │     ├── FSA / EQIP / ARC-PLC program documents
              │     └── Corn disease management documents
              │
              └── USDA NASS + MARS APIs  (live Iowa grain prices and yields)
```

**LLM:** Claude (Anthropic API)  
**Knowledge search:** gno (hybrid BM25 + vector, local)  
**Hosting:** Oracle Cloud Always Free (permanent, $0/month)  
**Interface:** Telegram bot (`@ABE_Iowa_bot`)  
**Total cost:** ~$5–15/month (Anthropic API only)

---

## Knowledge Base

ABE's RAG knowledge base is built from authoritative Iowa agricultural data sources, all publicly available and free:

| Category | Documents |
|---|---|
| Rental Rates | ISU Extension C2-20, C2-21 (cash rent calculation, flexible leases) |
| Lease Guidance | ISU Extension C2-01, C2-03, C2-05, C2-13 |
| Cost of Production | ISU Extension A1-20 (Excel, corn & soybeans, 2026 benchmarks) |
| Farmland Financing | ISU Extension C3-70 |
| Government Programs | FSA Beginning Farmer loans, FSA Operating loans, EQIP Iowa, EQIP advance payment (beginning farmers), ARC/PLC explainer |
| Corn Disease | Northern blight (Purdue BP-84), southern blight, common rust (UMN, UNL, Illinois), grey leaf spot (ISU, UMN), lethal necrosis (CIMMYT), streak virus (CIMMYT) |
| Live Data | USDA NASS QuickStats API (Iowa corn/soybean prices), USDA MARS (yield data) |

Structured financial data (cost benchmarks, county rental rates) is stored in SQLite for direct calculation. Narrative and policy documents are indexed in the gno knowledge base for hybrid BM25 + vector retrieval.

---

## Repository Structure

```
/
├── README.md
├── .env.example              ← API key template (never commit .env)
├── requirements.txt          ← Python dependencies
├── SOUL.md                   ← ABE's persona, voice, hard limits
├── AGENTS.md                 ← Routing logic, memory protocol, skill commands
├── IDENTITY.md               ← ABE's name, vibe, avatar
├── HEARTBEAT.md              ← Proactive daily price + weather alerts
├── TOOLS.md                  ← Local setup notes (environment-specific)
├── USER.md                   ← Not used for farmer profiles — leave blank
│
├── skills/
│   ├── abe-knowledge/
│   │   └── SKILL.md          ← gno RAG search over knowledge/ documents
│   ├── budget-planner/
│   │   └── SKILL.md          ← Land/budget scenario planner
│   ├── corn-disease-detector/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── corn_disease.py   ← CornCNN2 inference entry point
│   │       ├── CornCNN.py        ← Model architecture
│   │       ├── parameters.pth    ← Trained model weights
│   │       └── meta_data.json    ← Class labels
│   ├── cost-of-production/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── cost_calculator.py  ← ISU A1-20 line-item cost report
│   ├── crop-margin-simulator/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   └── response_format.md
│   │   └── scripts/
│   │       ├── crop_margin.py
│   │       └── calculator.py
│   ├── program-screener/
│   │   └── SKILL.md
│   ├── rental-rate-check/
│   │   └── SKILL.md
│   └── weather-forecast/
│       ├── SKILL.md
│       └── scripts/
│           └── weather.py        ← Open-Meteo fetcher (history/forecast/alerts)
│
├── scripts/
│   ├── add_document.sh           ← Copy a file into knowledge/ for gno indexing
│   ├── gno-daemon.sh             ← Start/stop the gno index daemon
│   ├── nass_api.py               ← Fetch live USDA NASS prices
│   ├── run_budget.py             ← CLI wrapper: budget planner scenarios
│   ├── run_cost_production.py    ← CLI wrapper: cost-of-production skill
│   ├── run_margin.py             ← CLI wrapper: crop margin simulator
│   ├── run_prices.py             ← CLI wrapper: daily price check (heartbeat)
│   ├── run_rental.py             ← CLI wrapper: rental rate check
│   ├── run_weather.py            ← CLI wrapper: weather history/forecast/alerts
│   ├── seed_cash_rent.py         ← Seed abe.db cash_rent table from ISU C2-10
│   ├── seed_costs.py             ← Seed abe.db crop_production_costs table
│   └── update_data.py            ← Parse knowledge/a1-20.xlsx → abe.db
│
├── knowledge/                    ← gno auto-indexes all files here
│   ├── a1-20.xlsx                ← ISU A1-20 cost-of-production Excel
│   ├── <program docs>.pdf/.txt   ← FSA, EQIP, ARC/PLC, lease, financing
│   └── <disease docs>.pdf/.txt   ← Blight, rust, grey leaf spot, lethal necrosis, streak virus
│
├── data/
│   ├── abe.db                    ← SQLite: cash_rent + crop_production_costs tables
│   ├── iowa_counties.json        ← Lat/lon for all 99 Iowa counties
│   ├── nass_fallback.csv         ← USDA NASS price fallback (offline)
│   ├── mars_fallback.csv         ← USDA MARS yield fallback (offline)
│   ├── prices_cache.json         ← Cached price data
│   └── seed_db.py                ← Seed all abe.db tables
│
├── memory/
│   └── farmers/
│       ├── TEMPLATE.md           ← Farmer memory file format
│       └── <telegram_id>.md      ← One per farmer, created on first contact
│
└── logs/
    ├── gno-daemon.log
    └── gno-daemon-error.log
```

---

## Setup

### Prerequisites

- Oracle Cloud Always Free account (ARM instance, Ubuntu 22.04)
- Node.js ≥ 22
- Python ≥ 3.10
- A Telegram account

### 1. Clone the repo

```bash
git clone https://github.com/SAU-Hive-Mind/ABE.git
cd ABE
```

### 2. Install OpenClaw

```bash
curl -fsSL https://openclaw.bot/install.sh | bash
openclaw onboard --install-daemon
```

### 3. Set up the Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 4. Set up API keys

Copy `.env.example` to `.env` and fill in your keys:

```
CLAUDE_TOKEN=sk-ant-...
NASS_API_KEY=...
MARS_API_KEY=...
```

> **Never commit your `.env` file.** It is already in `.gitignore`. Set a spending limit in your Anthropic console before anything else.

### 5. Create the Telegram bot

Message `@BotFather` on Telegram → `/newbot` → name it **ABE Iowa Farm Advisor** → copy the token into OpenClaw's channels config.

### 6. Build the database

```bash
# Seed the SQLite database with ISU cash rent and cost-of-production data
.venv/bin/python data/seed_db.py

# Or seed tables individually:
.venv/bin/python scripts/seed_cash_rent.py
.venv/bin/python scripts/seed_costs.py
.venv/bin/python scripts/update_data.py  # Parse A1-20 Excel → abe.db
```

### 7. Start the gno knowledge base daemon

```bash
bash scripts/gno-daemon.sh start
```

gno will auto-index everything in `knowledge/`. To add a new document:

```bash
bash scripts/add_document.sh path/to/document.pdf
```

### 8. Enable auto-restart

```bash
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

ABE is now live. Message `@ABE_Iowa_bot` on Telegram to test it.

---

## Development Schedule

| Week | Dates | Focus |
|---|---|---|
| Pre-Kickoff | Before Mar 9 | Create GitHub repo, team setup |
| Week 1 | Mar 9–14 | VPS, OpenClaw, Telegram bot, knowledge base |
| Week 2 | Mar 15–21 | Build all three core skills |
| Week 3 | Mar 22–28 | Accuracy testing, citations, guardrails |
| Week 4 | Mar 28–31 | Phase 2 submission (due March 31) |
| Week 5 | Apr 1–7 | User testing, ISU benchmark validation |
| Week 6 | Apr 7–14 | Demo video, final polish, submission (due April 14) |

Full task breakdown with owner assignments is in `ABE_Project_Tracker_v2.xlsx`.

---

## MVP Scope

ABE is scoped to corn and soybean row crop operations — Iowa's dominant farm type. The following are explicitly out of scope for the competition MVP:

- Livestock enterprise support
- Multi-year financial projections
- Real-time price feeds (cached NASS/MARS API data is used instead)
- User accounts or authentication
- Web or mobile frontend
- Comprehensive Farm Bill analysis

---

## Ethical Considerations

**ABE is an educational tool, not a licensed financial or legal advisor.** Every response that touches financial decisions includes a recommendation to consult a professional before acting.

- **Hallucination prevention:** All financial outputs are grounded in retrieved ISU Extension or USDA documents. ABE is instructed to decline to answer rather than estimate when data is unavailable. Temperature is set to 0 for all financial tool calls.
- **Privacy:** No personal farmer data is stored beyond the farmer's own memory file (keyed by Telegram ID). ABE does not log names, farm details, or financial information in any shared store.
- **Equity:** ABE is tested across small and large operations and multiple Iowa counties to avoid systematic bias toward any farm type or geography.
- **Transparency:** Every answer that draws on the knowledge base cites the source document and year.

---

## Future Work

The corn disease detector built for this project uses a CNN trained on the PlantVillage dataset. A natural extension would be integrating real-time scouting data from Iowa State University's Pest Management Network, allowing ABE to correlate a farmer's photo diagnosis with active field reports across the county.

Other extensions under consideration:

- Soybean disease detection (requires training data for SCN, sudden death syndrome, white mold)
- Multi-year financial projection (requires persistent farm data beyond the current session model)
- Direct FSA office integration (pre-fill loan applications from the farmer's profile)

All of the above are explicitly out of scope for the April 2026 competition MVP.

---

## Team

**SAU Hive Mind**

| Member | School |
|---|---|
| Jayden P. Coetzer | St. Ambrose University |
| Elyse S. Habersetzer | St. Ambrose University |
| Lucas C. Pizani | St. Ambrose University |
| Felipe P. Rivoir | St. Ambrose University |
| Luke E. Sproule | St. Ambrose University |

---

## Competition

**Pi515 AI Challenge 2026**  

---

*ABE provides educational information only. It is not a substitute for professional financial, legal, or agronomic advice. Always consult a qualified professional before making major farm business decisions.*
