# ABE — Agricultural Business Expert

**An AI-powered business advisor for Iowa's beginning farmers.**  
Built by **SAU Hive Mind** for the [Pi515 AI Challenge 2026](https://pi515.org) · Track 1: Sustainable Agriculture · Track 2: Fair Financial Futures

---

## The Problem

Iowa has approximately 85,000 farms, and the average Iowa farmer is over 57 years old. Every year, thousands of beginning and transitioning farmers enter the industry facing a critical knowledge gap: they lack access to affordable, personalized business guidance.

When a beginning farmer needs to know whether a cash rent rate is fair, whether their corn margin makes sense this year, or what government programs they might qualify for, their options are limited. County extension agents serve hundreds of farmers each. Private farm management consultants charge $150–$300 per hour. Generic financial tools carry no Iowa-specific data. The result is that too many beginning farmers make expensive decisions without the information they need; and the numbers bear that out: many farmers fail within their first years of operation because of negative revenue.

ABE is built to change that. Not by replacing professional advice, but by making a knowledgeable first conversation available to every Iowa farmer, any time they need it.

---

## What ABE Does

ABE is a conversational AI agent that connects to farmers through Telegram. It answers real business questions about Iowa farm operations, grounded in Iowa-specific data sources, such as Iowa State University Extension and Outreach and USDA sata, not national averages. ABE also runs four autonomous heartbeat tasks on a cron schedule — daily price alerts, weekly margin checks, seasonal milestone reminders, and weekly crop progress updates — without the farmer needing to ask. For now, ABE has seven skills, but we plan on expanding that

### 1. Rental Rate Check

A farmer tells ABE the county, land quality, and rate they're being quoted. ABE compares it against ISU Extension's annual county cash rent survey data, the statewide average, and the high/medium/low range for that county. It gives a plain-English verdict: is this rate fair, high, or low for this ground?

### 2. Crop Margin Simulator

A farmer inputs their acres, expected yield, current price, and rental rate. ABE calculates gross revenue, total cost of production broken down by category, and net margin per acre, all benchmarked against Iowa State University Extension and Outreach's A1-20 cost-of-production data for corn and soybeans. It answers the core question: *does this operation make money at these numbers?*

### 3. Cost of Production

A farmer asks for a detailed line-item breakdown of what it costs to raise corn or soybeans. ABE pulls from ISU AgDM A1-20 2026 (file that estimates costs of production) benchmarks, separates fixed from variable costs, and computes cost per bushel. Farmers can override any individual input with their own numbers; ISU benchmarks fill in the rest. Designed for farmers who want to understand where their money goes, not just whether the bottom line is positive.

### 4. Program Eligibility Screener

A farmer describes their situation (or the agent already has ) age, years of experience, net worth, county, operation size. ABE runs a rule-based pre-filter against eligibility criteria, then queries its knowledge base of government program documents to return a ranked list of programs the farmer likely qualifies for, with recommended next steps. Programs covered: FSA Beginning Farmer loans, EQIP, Iowa Beginning Farmer Tax Credit, and ARC/PLC.

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

ABE runs on [OpenClaw](https://openclaw.bot), a self-hosted AI agent runtime. Te agent can be deployed on an VPS or on a local machine (for the sakes of the competition, it is deployed in one of our machines). Farmers interact with ABE through a Telegram bot. The knowledge base is powered by gno, a search indexer that combines keyword matching (BM25) and semantic similarity (vector search) to find relevant documents even when the farmer's words don't exactly match the source text. It runs as a background daemon and automatically re-indexes any file added to the `knowledge/` directory. We automated the daemon using a LaunchAgent (macOS) and a systemd service (Ubuntu VPS), controlled via `scripts/gno-daemon.sh`.

```
Farmer (Telegram)
       │
       ▼
  OpenClaw Gateway  (VPS / Local Machine)
       │
       ├── SOUL.md          ← ABE's persona, hard limits, voice
       ├── AGENTS.md        ← Routing logic, memory protocol, skill commands
       ├── HEARTBEAT.md     ← Proactive cron tasks: price alerts, margin checks, calendar reminders, crop progress
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

**LLM:** Claude Sonnet (Anthropic API)  
**Knowledge search:** gno (hybrid BM25 + vector, local)  
**Hosting:** VPS / Local Machine 
**Interface:** Telegram bot (`@ABE_Iowa_bot`)  
**Total cost:** ~$5–15/month per user (Anthropic API only)

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

## API Keys Needed

| Key | What it does | Where to get it |
|---|---|---|
| `CLAUDE_TOKEN` | Powers ABE's conversations (OpenClaw supports any LLM — we use Claude) | [console.anthropic.com](https://console.anthropic.com) |
| `NASS_API_KEY` | Fetches live Iowa corn and soybean cash prices from USDA NASS QuickStats | [quickstats.nass.usda.gov](https://quickstats.nass.usda.gov/api) |
| `MARS_API_KEY` | Fetches Iowa crop yield data from USDA MARS (used as fallback when NASS data is unavailable) | [glam.gsfc.nasa.gov](https://glam.gsfc.nasa.gov) |

## Repository Structure

```
/
├── README.md
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
│   ├── run_calendar.py           ← Heartbeat: daily ag calendar reminders (milestones + FSA deadlines)
│   ├── run_crop_progress.py      ← Heartbeat: weekly USDA Iowa crop progress report
│   ├── run_margin_check.py       ← Heartbeat: weekly margin refresh + profitability flip detection
│   ├── run_prices.py             ← Heartbeat: daily cash price check + delta alerts
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
│   ├── ag_calendar.json          ← Seasonal milestones + FSA deadlines (verified ISU/USDA sources)
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

Create `.env` and fill in your keys:

```
CLAUDE_TOKEN=sk-ant-...       # Anthropic API key — powers ABE's conversations
NASS_API_KEY=...              # USDA NASS QuickStats — live Iowa grain prices
MARS_API_KEY=...              # USDA MARS — Iowa crop yield data (fallback)
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

### 8. Register the heartbeat cron jobs

```bash
# Daily cash price alerts — weekdays at 8am CT
openclaw cron add --agent abe --name "daily-price-check" \
  --cron "0 8 * * 1-5" --tz "America/Chicago" \
  --message "Run your daily price check heartbeat task." \
  --timeout-seconds 120

# Daily calendar reminders — every day at 7am CT
openclaw cron add --agent abe --name "daily-calendar-reminders" \
  --cron "0 7 * * *" --tz "America/Chicago" \
  --message "Run your daily calendar reminders heartbeat task." \
  --timeout-seconds 120

# Weekly margin refresh — Mondays at 9am CT
openclaw cron add --agent abe --name "weekly-margin-refresh" \
  --cron "0 9 * * 1" --tz "America/Chicago" \
  --message "Run your weekly margin refresh heartbeat task." \
  --timeout-seconds 180

# Weekly crop progress — Mondays at 10am CT
openclaw cron add --agent abe --name "weekly-crop-progress" \
  --cron "0 10 * * 1" --tz "America/Chicago" \
  --message "Run your weekly crop progress heartbeat task." \
  --timeout-seconds 120
```

Verify with `openclaw cron list`.

### 9. Enable auto-restart

```bash
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

ABE is now live. Message `@ABE_Iowa_bot` on Telegram to test it.

---

## MVP Scope

ABE is scoped to corn and soybean row crop operations, which is Iowa's dominant farm type. The following are explicitly out of scope for the competition MVP:

- Livestock enterprise support
- Multi-year financial projections
- User accounts or authentication
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

ABE is a single-agent MVP. The long-term vision is significantly larger.

### Multi-agent farm advisory team

The natural next step is moving from one generalist agent to a team of specialized agents working together on behalf of the farmer. An agronomist agent focused on crop health and scouting. A finance agent handling margins, loans, and cash flow. A legal agent navigating lease terms and program compliance. A market analyst watching price trends and basis levels. Each expert in their domain, coordinating behind the scenes so the farmer still has one conversation. This model could support a subscription tier for farmers who want deeper, ongoing advisory coverage.

### More proactive intelligence

ABE now runs four autonomous heartbeat tasks on a cron schedule: daily Iowa cash price alerts (corn and soybeans), weekly margin checks that flag when a farmer's operation crosses the profitable/unprofitable line, daily calendar reminders tied to verified ISU Extension and USDA deadlines (crop insurance sales closing, ARC/PLC enrollment, EQIP cutoffs, Iowa Beginning Farmer Tax Credit), and weekly USDA crop progress reports during growing season.

Further expansions could include: USDA report release dates and their impact on local basis, county-level pest and disease pressure reports from ISU's Pest Management Network, and lease renewal timing relative to program enrollment calendars. The goal is an agent that surfaces the right information before the farmer thinks to ask.

### Scale and infrastructure

ABE is currently self-hosted on a single machine. Serving more farmers means moving to a proper VPS (or multiple), adding usage monitoring, and securing funding to cover API and hosting costs at scale. The architecture is already designed for it — the main work is operational, not technical.

### Reach farmers where they already are

Telegram works, but it is not where every farmer is. WhatsApp has broader rural adoption in some regions. A phone number farmers can text directly, without installing anything, would lower the barrier further. The same agent, more access points.

### Disease detection expansion

The current corn disease model covers six classes. Soybean disease detection (SCN, sudden death syndrome, white mold) requires new training data but is a natural addition given that soybeans are half of Iowa's planted acres. Integrating active field scouting reports from ISU's Pest Management Network would let ABE correlate a farmer's photo with what is actually moving across the county right now.

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
