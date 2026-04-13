# ABE Documentation

ABE (Agricultural Business Expert) is a conversational AI assistant for Iowa beginning farmers, built by SAU Hive Mind. Farmers reach ABE through Telegram and get plain-language answers grounded in real Iowa data — rental benchmarks, crop margins, government programs, weather, and disease management.

---

## About this documentation

This documentation is written for three audiences:

- **Pi515 and evaluators** — understand what ABE does, why it was built, and how it works at a high level. Start with [What ABE Covers](for-partners/what-abe-covers.md) and [Knowledge Sources](for-partners/knowledge-sources.md).
- **Agricultural partners** — FSA staff, NRCS offices, ISU Extension educators, and anyone who wants to understand ABE's scope, data sources, and limits. See the [For Partners](for-partners/README.md) section.
- **Developers and contributors** — engineers setting up, extending, or maintaining ABE. See the [For Developers](for-developers/README.md) section.

---

## The problem ABE solves

Iowa has over 85,000 farms. The average farmer is 57 years old. Beginning farmers — those in their first ten years — face a steep learning curve: navigating FSA loan programs, understanding whether a quoted rent is fair, figuring out if a corn operation will pencil out, identifying when a crop disease is spreading.

The guidance that could help is scattered across ISU Extension publications, USDA program offices, and county-level data that most beginning farmers never find.

ABE puts that guidance in one place, in plain language, through a channel farmers already use.

---

## What ABE is

ABE is a Telegram bot powered by an OpenClaw agent backed by Claude. When a farmer asks a question, ABE:

1. Identifies what the farmer needs
2. Runs the appropriate skill (calculation, database lookup, photo analysis, document search)
3. Returns a sourced, specific answer — not generic advice
4. Notices what else might matter and offers one follow-up

ABE does not make decisions for farmers. It surfaces real numbers with real sources and lets the farmer decide.

---

## Quick reference

| | |
|---|---|
| Interface | Telegram |
| Agent runtime | OpenClaw + Claude |
| Crops covered | Corn, soybeans (Iowa) |
| Skills | 8 |
| Knowledge documents | ~41 indexed files |
| Database | SQLite (`data/abe.db`) |
| Heartbeat tasks | 5 automated cron jobs |
| Language | Python 3 |

---

## Table of contents

**For Partners and Evaluators**
- [For Partners — Overview](for-partners/README.md)
- [What ABE Covers](for-partners/what-abe-covers.md)
- [Knowledge Sources](for-partners/knowledge-sources.md)
- [Accuracy and Limits](for-partners/accuracy-and-limits.md)

**For Staff**
- [For Staff — Overview](for-staff/README.md)
- [Deployment](for-staff/deployment.md)
- [Managing the Knowledge Base](for-staff/knowledge-base.md)
- [Monitoring and Heartbeat](for-staff/monitoring.md)
- [Farmer Data and Privacy](for-staff/farmer-data.md)

**For Developers**
- [For Developers — Overview](for-developers/README.md)
- [Setup](for-developers/setup.md)
- [Architecture](for-developers/architecture.md)
- [Skills](for-developers/skills.md)
- [Database](for-developers/database.md)
- [External APIs](for-developers/apis.md)
- [Heartbeat Tasks](for-developers/heartbeat.md)
- [Adding a Skill](for-developers/adding-a-skill.md)

**Reference**
- [Environment Variables](reference/environment-variables.md)
- [CLI Commands](reference/cli-commands.md)
- [Knowledge Documents](reference/knowledge-documents.md)
