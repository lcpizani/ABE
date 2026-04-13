# Architecture

This page describes how ABE's components fit together and how data flows through the system.

---

## High-level overview

```
Farmer (Telegram)
       │
       ▼
  OpenClaw Agent  ◄──── SOUL.md / AGENTS.md / HEARTBEAT.md
       │
       ├──── Skill routing ────►  Python scripts (.venv/bin/python)
       │                              │
       │                        ┌─────┴─────────────────────────┐
       │                        │                               │
       │                    SQLite DB                      gno daemon
       │                   (data/abe.db)                (knowledge/ index)
       │                        │                               │
       │                   ISU benchmarks               ~41 documents
       │                   (C2-10, A1-20)             (ISU, FSA, NRCS, etc.)
       │
       ├──── External APIs ───► USDA NASS / MARS
       │                        Open-Meteo
       │
       └──── Farmer memory ──► memory/farmers/<telegram_id>.md
```

---

## Components

### OpenClaw agent

OpenClaw is the agent runtime. It manages:
- The Telegram bot connection
- LLM conversation context
- Tool/skill invocation
- Cron job scheduling and execution

ABE's behavior is defined in three Markdown files that OpenClaw loads at startup:
- `SOUL.md` — who ABE is, hard limits, what it will never do
- `AGENTS.md` — how ABE responds, skill routing logic, memory protocol, conversation rules
- `HEARTBEAT.md` — what each autonomous cron task does and how it messages farmers

### Skills

Each skill is a directory under `skills/` containing a `SKILL.md` (instructions for ABE) and optionally Python scripts. ABE reads the `SKILL.md` to know when to invoke the skill and how to present results. The actual computation happens in the Python scripts.

See [Skills](skills.md) for routing logic and a full skill reference.

### SQLite database (`data/abe.db`)

The database holds structured, queryable benchmark data:

- `cash_rent` — ISU C2-10 county rental benchmarks for all 99 Iowa counties
- `crop_production_costs` — ISU A1-20 line-item cost data for corn and soybeans
- `a1_20_costs` — aggregate ISU cost benchmarks by crop and region
- `crop_costs` — flat cost items by category

Scripts that query the database are called via CLI and return JSON to stdout.

See [Database](database.md) for full schema details.

### gno knowledge base

`gno` is a local document search tool. The daemon watches `knowledge/` and indexes documents using BM25 (keyword) + vector embeddings (semantic). ABE calls `gno query` or `gno ask` to retrieve relevant chunks from the indexed documents.

The collection name is `abe-knowledge`.

### External APIs

| API | Purpose | Auth |
|---|---|---|
| USDA NASS QuickStats | Annual Iowa corn/soybean prices and yields; weekly crop progress | API key in header |
| USDA AMS MARS | Daily Iowa cash prices for corn and soybeans | Basic auth (API key as username) |
| Open-Meteo | Weather history, 16-day forecast, growing-season alerts | No auth required |

All API access is handled in `scripts/nass_api.py` (NASS and MARS) and `skills/weather-forecast/scripts/weather.py` (Open-Meteo). Each has a fallback CSV in `data/` for when the live API is unavailable.

### Farmer memory

Each farmer has a Markdown file at `memory/farmers/<telegram_id>.md`. ABE reads this file at the start of each conversation and updates it when new information is shared. This is the only file ABE is permitted to write.

The `memory/farmers/` directory is gitignored.

---

## Data flow: a crop margin calculation

1. Farmer asks: "Will 400 acres of corn in Linn County pencil out at $4.20?"
2. OpenClaw routes to the crop-margin-simulator skill (per `AGENTS.md` routing rules).
3. ABE calls: `.venv/bin/python scripts/run_margin.py --crop corn --acres 400 --county "Linn County" --price 4.20`
4. `run_margin.py`:
   - Queries `abe.db` for Linn County rental rate and ISU A1-20 cost benchmarks
   - Calls `nass_api.get_iowa_data()` for yield benchmark
   - Calculates gross revenue, total cost, net margin
   - Returns JSON with all inputs, outputs, and sources
5. ABE parses the JSON and presents results in plain language, citing ISU A1-20 and ISU C2-10 inline.
6. ABE notices if the margin is thin (<$30/acre) and offers to check ARC-CO/PLC eligibility.

---

## Data flow: a knowledge base query

1. Farmer asks: "What do I need to qualify for an FSA beginning farmer loan?"
2. OpenClaw routes to the program-screener skill.
3. ABE calls: `gno ask "FSA beginning farmer loan eligibility requirements" --answer -c abe-knowledge`
4. gno searches the indexed documents, retrieves the most relevant chunks, and synthesizes an answer with citations.
5. ABE presents the result, citing the specific FSA document.

---

## Cron / heartbeat flow

1. OpenClaw fires a cron job at the scheduled time.
2. The cron message triggers ABE to run the corresponding heartbeat task from `HEARTBEAT.md`.
3. ABE runs the heartbeat script (e.g., `scripts/run_prices.py`).
4. ABE parses the JSON output and, if thresholds are met, sends Telegram messages to the relevant farmers.
5. Cache files in `data/` are updated for the next cycle.
