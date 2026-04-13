# For Developers

This section is for engineers setting up, extending, or maintaining ABE.

---

## What you'll find here

- [Setup](setup.md) — full development environment setup from scratch
- [Architecture](architecture.md) — system design, data flow, and component relationships
- [Skills](skills.md) — how skills are structured, routed, and invoked
- [Database](database.md) — SQLite schema, table descriptions, and seeding
- [External APIs](apis.md) — USDA NASS, USDA MARS, and Open-Meteo integration details
- [Heartbeat Tasks](heartbeat.md) — autonomous cron jobs: what they do and how they are structured
- [Adding a Skill](adding-a-skill.md) — step-by-step guide to building and integrating a new skill

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent runtime | OpenClaw |
| LLM | Anthropic Claude |
| Interface | Telegram |
| Language | Python 3 |
| Database | SQLite (`data/abe.db`) |
| Knowledge search | gno (BM25 + vector hybrid) |
| Disease detection | PyTorch (CornCNN2) |
| Weather | Open-Meteo API |
| Market prices | USDA AMS MARS API |
| Crop data | USDA NASS QuickStats API |

---

## Key files

| File | Purpose |
|---|---|
| `SOUL.md` | ABE's persona, voice, hard limits — defines who ABE is |
| `AGENTS.md` | Operational behavior — how ABE responds, skill routing, memory protocol |
| `HEARTBEAT.md` | Autonomous task definitions — what each cron job does and sends |
| `TOOLS.md` | Environment-specific tool notes |
| `requirements.txt` | Python dependencies |
| `.env` | API keys and secrets (not committed) |

---

## Codebase layout

```
ABE/
├── skills/          # Skill definitions (SKILL.md) and their scripts
├── scripts/         # CLI wrappers and heartbeat scripts
├── data/            # SQLite database, JSON caches, reference data
├── knowledge/       # Documents indexed by the gno daemon
├── memory/          # Farmer profile files (gitignored)
├── logs/            # gno daemon logs
└── docs/            # This documentation
```

---

## Python environment

All scripts use the project's virtual environment. Never use the system `python3`.

```bash
# Correct
.venv/bin/python scripts/run_margin.py --crop corn ...

# Wrong — do not use
python3 scripts/run_margin.py
python scripts/run_margin.py
```

This applies to every script invocation everywhere in the project.
