# ABE — Agricultural Business Expert

**An AI-powered business advisor for Iowa's beginning farmers.**  
Built by **SAU Hive Mind** · Pi515 AI Challenge 2026 · Track 1: Sustainable Agriculture · Track 2: Fair Financial Futures

---

## The problem

Iowa has approximately 85,000 farms and the average farmer is over 57 years old. Beginning farmers face a steep knowledge gap: county extension agents serve hundreds of farms each, private consultants charge $150–$300/hour, and generic financial tools carry no Iowa-specific data.

The result is that too many beginning farmers make expensive decisions without the information they need.

ABE is built to change that — not by replacing professional advice, but by making a knowledgeable first conversation available to every Iowa farmer, any time they need it.

---

## What ABE does

ABE is a Telegram-based AI assistant powered by [OpenClaw](https://openclaw.bot) and Claude. A farmer sends a message. ABE identifies what they need, runs the appropriate skill, and returns a specific, sourced answer. Every dollar figure cites its source — an ISU Extension publication, a USDA dataset, or a live market API.

**Eight skills:**
1. **Rental rate check** — compares a quoted rate to ISU Extension county benchmarks
2. **Crop margin simulator** — calculates net margin per acre for corn and soybeans
3. **Cost of production** — line-item ISU A1-20 cost breakdown with farmer overrides
4. **Program screener** — FSA loans, EQIP, ARC-CO/PLC, Iowa BFLP/LPP
5. **Weather forecast** — 14-day history, 16-day forecast, and growing-season alerts for any Iowa county
6. **Corn disease detector** — photo → CornCNN2 diagnosis → management guidance
7. **Budget planner** — rent vs. buy scenarios given a stated budget
8. **Knowledge base** — hybrid BM25 + vector search over ~41 authoritative documents

ABE also runs **five automated heartbeat tasks** — daily price alerts, weekly margin checks, daily calendar reminders, daily weather alerts, and weekly crop progress updates — without the farmer needing to ask.

---

## Tech stack

| | |
|---|---|
| Agent runtime | [OpenClaw](https://openclaw.bot) |
| LLM | Anthropic Claude |
| Interface | Telegram |
| Knowledge search | [gno](https://github.com/gmickel/gno) (BM25 + vector hybrid) |
| Database | SQLite (ISU Extension benchmarks) |
| Market data | USDA NASS + USDA MARS APIs |
| Weather | Open-Meteo (no key required) |
| Disease detection | PyTorch (CornCNN2) |

---

## Documentation

Full documentation is in [`docs/`](docs/README.md):

- **[For Evaluators and Partners](docs/for-partners/README.md)** — what ABE covers, data sources, accuracy and limits
- **[Competition Submission](docs/submission/README.md)** — problem statement, model development, evaluation, impact and feasibility
- **[For Staff](docs/for-staff/README.md)** — deployment, knowledge base management, monitoring
- **[For Developers](docs/for-developers/README.md)** — setup, architecture, skills reference, adding a skill
- **[Reference](docs/reference/)** — environment variables, CLI commands, knowledge document index

---

## Quick setup

```bash
git clone <repo-url> && cd ABE
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in CLAUDE_TOKEN, NASS_API_KEY, MARS_API_KEY
.venv/bin/python data/seed_db.py
bash scripts/gno-daemon.sh start
```

See [Deployment](docs/for-staff/deployment.md) for the full setup guide including database seeding, cron job registration, and Telegram bot configuration.

---

## Scope

ABE is scoped to Iowa corn and soybean row crop operations. Out of scope for the current version: livestock, multi-year projections, comprehensive Farm Bill analysis, and other states.

---

## Future work

ABE is a single-agent MVP. The long-term vision is significantly larger.

**Multi-agent farm advisory team** — Move from one generalist agent to a coordinated team of specialized agents: an agronomist, a finance agent, a legal agent, a market analyst. Each expert in their domain; the farmer still has one conversation.

**More proactive intelligence** — Expand the heartbeat system to include USDA report release dates and local basis impact, county-level pest and disease pressure from ISU's Pest Management Network, and lease renewal timing relative to program enrollment calendars. The goal is an agent that surfaces the right information before the farmer thinks to ask.

**Disease detection expansion** — The current model covers six corn disease classes. Soybean disease detection (SCN, sudden death syndrome, white mold) is a natural addition given that soybeans represent half of Iowa's planted acres.

**More access points** — Telegram works, but WhatsApp has broader rural adoption in some regions. A phone number farmers can text directly — no app install required — would lower the barrier further.

**Scale and infrastructure** — ABE is currently self-hosted on a single machine. The architecture is already designed for multi-tenant deployment; the main work is operational.

---

## Ethical principles

ABE never generates a financial figure without a named source. If data is unavailable, it says so. It surfaces program eligibility criteria but never tells a farmer they qualify — that determination is made by the relevant agency. Legal and tax questions are always referred to professionals.

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

