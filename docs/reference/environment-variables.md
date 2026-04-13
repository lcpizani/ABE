# Environment Variables

All secrets and API keys are stored in `.env` in the project root. This file is never committed to the repository.

---

## Required variables

| Variable | Description | Where to get it |
|---|---|---|
| `CLAUDE_TOKEN` | Anthropic API key for Claude | [console.anthropic.com](https://console.anthropic.com/) |
| `NASS_API_KEY` | USDA NASS QuickStats API key | [quickstats.nass.usda.gov/api](https://quickstats.nass.usda.gov/api) |
| `MARS_API_KEY` | USDA AMS MyMarketNews API key | [mymarketnews.ams.usda.gov](https://mymarketnews.ams.usda.gov/) |

---

## Example `.env` file

```dotenv
# Anthropic Claude API key
CLAUDE_TOKEN=sk-ant-api03-...

# USDA NASS QuickStats — used for annual crop prices/yields and weekly crop progress
NASS_API_KEY=2AF8EF4B-AC8F-328B-9831-F5991F2EE2E7

# USDA AMS MyMarketNews (MARS) — used for daily Iowa cash prices
# Auth: Basic auth with API key as username, empty password
MARS_API_KEY=oK/SXE39wQhfeQg7fsBmS4ZrITNQhmzw
```

---

## Variables not required

| Variable | Reason not needed |
|---|---|
| Open-Meteo key | Open-Meteo is a free, open API requiring no authentication |
| Telegram bot token | Managed by OpenClaw's configuration, not by ABE's `.env` |

---

## Loading environment variables

ABE uses [`python-dotenv`](https://pypi.org/project/python-dotenv/) to load `.env` at startup. In any script that needs API keys:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("NASS_API_KEY")
```

---

## Security notes

- Never commit `.env` to the repository. It is listed in `.gitignore`.
- Rotate API keys if they are ever exposed in logs or committed accidentally.
- The MARS API key is used as an HTTP Basic Auth username (with an empty password). Treat it with the same sensitivity as a password.
