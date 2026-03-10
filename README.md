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

ABE has three core skills at MVP:

### 1. Rental Rate Check
A farmer tells ABE the county, land quality, and rate they're being quoted. ABE compares it against ISU Extension's annual county cash rent survey (C2-10), the statewide average, and the high/medium/low range for that county. It gives a plain-English verdict: is this rate fair, high, or low for this ground?

### 2. Crop Margin Simulator
A farmer inputs their acres, expected yield, current price, and rental rate. ABE calculates gross revenue, total cost of production broken down by category, and net margin per acre — all benchmarked against ISU Extension's A1-20 cost-of-production data for corn and soybeans. It answers the core question: *does this operation make money at these numbers?*

### 3. Program Eligibility Screener
A farmer describes their situation — age, years of experience, net worth, county, operation size. ABE runs a rule-based pre-filter against eligibility criteria, then queries its knowledge base of government program documents to return a ranked list of programs the farmer likely qualifies for, with recommended next steps. Programs covered: FSA Beginning Farmer loans, EQIP, Iowa Beginning Farmer Tax Credit, and ARC/PLC.

### How ABE Responds

ABE is not a generic chatbot. Every financial answer cites its source document. If a number isn't in the knowledge base, ABE says so rather than estimating. All financial outputs use temperature = 0. ABE always recommends professional consultation for major decisions. It is an educational tool, not a substitute for legal or financial advice.

---

## Architecture

ABE runs on [OpenClaw](https://openclaw.bot), a self-hosted AI agent runtime, deployed on an Oracle Cloud Always Free ARM instance. Farmers interact with ABE through a Telegram bot.

```
Farmer (Telegram)
       │
       ▼
  OpenClaw Gateway  (Oracle Cloud ARM VPS — Ubuntu 22.04, 4 OCPUs, 24GB RAM)
       │
       ├── SOUL.md          ← ABE's persona, routing logic, guardrails
       ├── HEARTBEAT.md     ← Proactive daily price alerts (optional)
       │
       ├── Skill: knowledge + iyeque-pdf-reader   ← RAG over ISU/USDA PDFs
       ├── Skill: crop-margin                     ← Python calc + SQLite
       ├── Skill: rental-rate-check               ← Python calc + SQLite + NASS API
       └── Skill: program-eligibility             ← Rule filter + RAG
              │
              ├── SQLite DB
              │     ├── crop_costs     (parsed from ISU A1-20 Excel)
              │     └── rental_rates   (parsed from ISU C2-10 PDF)
              │
              └── USDA NASS QuickStats API  (live Iowa grain prices)
```

**LLM:** GPT-4o-mini via OpenAI API  
**Hosting:** Oracle Cloud Always Free (permanent, $0/month)  
**Interface:** Telegram bot (`@ABE_Iowa_bot`)  
**Total cost:** ~$15–30/month (OpenAI API only)

---

## Knowledge Base

ABE's RAG knowledge base is built from authoritative Iowa agricultural data sources, all publicly available and free:

| Category | Documents |
|---|---|
| Rental Rates | ISU Extension C2-10, C2-11, C2-20, C2-21 |
| Crop Economics | ISU Extension A1-85, A1-86, A1-21, A2-11 |
| Cost of Production | ISU Extension A1-20 (16 Excel files, corn & soybeans) |
| Financial Guidance | ISU Extension C3-15, C3-20, C3-25, C3-55, C3-56, C3-64 |
| Government Programs | FSA Beginning Farmer loan guide, FSA Operating Loan guide, EQIP criteria, Iowa Beginning Farmer Tax Credit, ARC/PLC overview |
| Live Data | USDA NASS QuickStats API (Iowa corn/soybean prices and yields) |

Structured financial data (cost benchmarks, county rental rates) is stored in SQLite for direct calculation. Narrative and policy documents are embedded in the OpenClaw RAG knowledge base for retrieval.

---

## Repository Structure

```
/
├── README.md
├── .env.example              ← API key template (never commit real keys)
├── SOUL.md                   ← ABE's agent persona and routing instructions
├── HEARTBEAT.md              ← Proactive price alert schedule (optional)
│
├── skills/
│   ├── crop-margin/
│   │   ├── SKILL.md          ← Trigger conditions and output format
│   │   └── calculate_margin.py
│   ├── rental-rate-check/
│   │   ├── SKILL.md
│   │   └── check_rental_rate.py
│   └── program-eligibility/
│       ├── SKILL.md
│       └── check_eligibility.py
│
├── scripts/
│   ├── build_sqlite.py       ← Parses ISU A1-20 Excel + C2-10 → SQLite
│   ├── nass_api.py           ← USDA NASS QuickStats API wrapper
│   └── ingest_docs.sh        ← Ingests all PDFs into OpenClaw knowledge base
│
├── data/
│   ├── raw/                  ← Downloaded ISU Extension PDFs and Excel files
│   └── db/
│       └── farm_data.db      ← SQLite database (crop_costs + rental_rates)
│
└── docs/
    ├── data_sources.md       ← All source documents with URLs and ingestion status
    ├── test_log.md           ← Skill test results and failure log
    ├── evaluation_report.md  ← 20-question accuracy test results
    └── ethical_review.md     ← Uncertainty, privacy, equity, disclaimers
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

### 3. Set up API keys

Copy `.env.example` to `.env` and fill in your keys:

```
OPENAI_API_KEY=sk-...
USDA_NASS_API_KEY=...
```

> **Never commit your `.env` file.** Set a $40/month hard spending limit in your OpenAI dashboard before anything else.

### 4. Create the Telegram bot

Message `@BotFather` on Telegram → `/newbot` → name it **ABE Iowa Farm Advisor** → copy the token into OpenClaw's channels config.

### 5. Install knowledge base skills

```bash
npx playbooks add skill openclaw/skills --skill knowledge
npx playbooks add skill openclaw/skills --skill iyeque-pdf-reader
```

### 6. Download source documents and build the database

```bash
# Download ISU Extension and USDA documents to data/raw/
# (See docs/data_sources.md for full URL list)

# Build SQLite tables from ISU A1-20 Excel and C2-10 PDF
python scripts/build_sqlite.py

# Ingest all PDFs into the OpenClaw knowledge base
bash scripts/ingest_docs.sh
```

### 7. Enable auto-restart

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
- Real-time price feeds (cached NASS API data is used instead)
- User accounts or authentication
- Web or mobile frontend
- Comprehensive Farm Bill analysis

---

## Ethical Considerations

**ABE is an educational tool, not a licensed financial or legal advisor.** Every response that touches financial decisions includes a recommendation to consult a professional before acting.

- **Hallucination prevention:** All financial outputs are grounded in retrieved ISU Extension or USDA documents. ABE is instructed to decline to answer rather than estimate when data is unavailable. Temperature is set to 0 for all financial tool calls.
- **Privacy:** No personal farmer data is stored beyond the current conversation session. ABE does not log names, farm details, or financial information.
- **Equity:** ABE is tested across small and large operations and multiple Iowa counties to avoid systematic bias toward any farm type or geography.
- **Transparency:** Every answer that draws on the knowledge base cites the source document and year.

---

## Future Work

The team's prior competition project produced a crop disease detection model trained on the PlantVillage dataset. A future ABE skill could integrate this model, allowing farmers to photograph a crop and receive both a disease diagnosis and the associated economic impact on their margin — all within the same conversation. This extension is explicitly out of scope for the April 2026 competition MVP.

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