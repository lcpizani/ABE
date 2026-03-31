"""
nass_api.py  —  ABE: Agricultural Business Expert
Dual-source Iowa market data client:
  • USDA NASS QuickStats — annual Iowa corn/soybean prices and corn yield
  • USDA AMS MyMarketNews (MARS) — daily Iowa cash grain bids (today's price)

How it works:
  1. Tries to fetch live data from each API.
  2. If an API is down or the key is missing, falls back to the saved CSV.
  3. Always saves a fresh CSV whenever a live fetch succeeds.

Usage:
  python nass_api.py                       # prints a full summary to the terminal
  from nass_api import get_iowa_data       # annual NASS benchmark data
  from nass_api import get_iowa_cash_prices  # today's AMS cash prices
"""

import os
import csv
import json
import base64
import urllib.request
import urllib.parse
from datetime import datetime

# ── Built-in .env loader (no external libraries required) ─────────────────────
# Reads a .env file in the same folder as this script and loads every
# NAME=value line into the environment so os.getenv() can find them.
# Lines that start with # are treated as comments and ignored.

def _load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

_load_env_file()

# ── Configuration ─────────────────────────────────────────────────────────────
# Both API keys are read from the .env file sitting next to this script.
# Your .env file should contain two lines:
#   NASS_API_KEY=your_nass_key_here     → get free at https://api.data.gov/signup/
#   MARS_API_KEY=your_mars_key_here     → get free at https://mymarketnews.ams.usda.gov/

API_KEY           = os.getenv("NASS_API_KEY", "YOUR_NASS_API_KEY_HERE")
BASE_URL          = "https://quickstats.nass.usda.gov/api/api_GET/"
FALLBACK_CSV      = "nass_fallback.csv"

MARS_API_KEY      = os.getenv("MARS_API_KEY", "YOUR_MARS_API_KEY_HERE")
MARS_BASE_URL     = "https://marsapi.ams.usda.gov/services/v1.2/reports/"
MARS_REPORT_ID    = "2850"                # Iowa Daily Cash Grain Bids
MARS_FALLBACK_CSV = "mars_fallback.csv"

# ── What we want to fetch ──────────────────────────────────────────────────────
#
# Three separate API queries, one per data point:
#
#   1. Iowa corn price received  → "How much are Iowa farmers getting per bushel?"
#   2. Iowa soybean price received
#   3. Iowa corn yield per acre  → "How many bushels does an acre produce on average?"
#
# Each query is a dictionary of filter parameters that map directly to the
# QuickStats column names described in the API documentation.

QUERIES = [
    {
        "label": "corn_price_iowa",
        "description": "Iowa Corn — Price Received ($ / BU)",
        "params": {
            "commodity_desc":    "CORN",
            "statisticcat_desc": "PRICE RECEIVED",
            "unit_desc":         "$ / BU",
            "state_alpha":       "IA",
            "freq_desc":         "ANNUAL",
            "source_desc":       "SURVEY",
            "domain_desc":       "TOTAL",
            "agg_level_desc":    "STATE",
        },
    },
    {
        "label": "soybean_price_iowa",
        "description": "Iowa Soybeans — Price Received ($ / BU)",
        "params": {
            "commodity_desc":    "SOYBEANS",
            "statisticcat_desc": "PRICE RECEIVED",
            "unit_desc":         "$ / BU",
            "state_alpha":       "IA",
            "freq_desc":         "ANNUAL",
            "source_desc":       "SURVEY",
            "domain_desc":       "TOTAL",
            "agg_level_desc":    "STATE",
        },
    },
    {
        "label": "corn_yield_iowa",
        "description": "Iowa Corn — Yield (BU / ACRE)",
        "params": {
            "commodity_desc":    "CORN",
            "statisticcat_desc": "YIELD",
            "unit_desc":         "BU / ACRE",
            "state_alpha":       "IA",
            "freq_desc":         "ANNUAL",
            "source_desc":       "SURVEY",
            "domain_desc":       "TOTAL",
            "agg_level_desc":    "STATE",
        },
    },
]

# ── Core API function ──────────────────────────────────────────────────────────

def _is_numeric(s: str) -> bool:
    """Return True if string s can be read as a float (handles commas)."""
    try:
        float(s.replace(",", ""))
        return True
    except (ValueError, AttributeError):
        return False


def fetch_latest(params: dict):
    """
    Send one GET request to the NASS QuickStats API and return the most
    recent record (highest year) that has a non-empty Value field.

    Args:
        params: A dict of query parameters to filter the API request, e.g.:
            {
                "commodity_desc":    "CORN",
                "statisticcat_desc": "PRICE RECEIVED",
                "unit_desc":         "$ / BU",
                "state_alpha":       "IA",
                "freq_desc":         "ANNUAL",
                "source_desc":       "SURVEY",
                "domain_desc":       "TOTAL",
                "agg_level_desc":    "STATE",
            }

    Returns a dict with the record fields, or None if nothing was found.
    """
    query = {"key": API_KEY, "format": "json"}
    query.update(params)

    url = BASE_URL + "?" + urllib.parse.urlencode(query)

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        print(f"  [API ERROR] Could not reach NASS API: {e}")
        return None

    records = data.get("data", [])

    if not records:
        print("  [API WARNING] API responded but returned zero records.")
        print("  Check your parameters — they may not match any data.")
        return None

    valid = [r for r in records if _is_numeric(r.get("Value", ""))]

    if not valid:
        print("  [API WARNING] All returned values were suppressed or non-numeric.")
        return None

    latest = max(valid, key=lambda r: int(r.get("year", 0)))
    return latest


# ── Fallback CSV helpers ───────────────────────────────────────────────────────

def save_fallback(results: list) -> None:
    """
    Write the current results to a CSV file so we have a backup
    in case the API is unavailable on demo day.
    """
    fieldnames = ["label", "description", "year", "value", "unit", "fetched_at"]
    with open(FALLBACK_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n  [SAVED] Fallback CSV written to: {FALLBACK_CSV}")


def load_fallback() -> list:
    """
    Read the previously saved CSV and return its rows.
    Called automatically when the live API fetch fails.
    """
    if not os.path.exists(FALLBACK_CSV):
        print("  [FALLBACK ERROR] No fallback CSV found. Run the script once"
              " with a working API key to create it.")
        return []

    with open(FALLBACK_CSV, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"  [FALLBACK] Loaded {len(rows)} rows from {FALLBACK_CSV}")
    return rows


# ── Main public function ───────────────────────────────────────────────────────

def get_iowa_data(use_fallback_on_error: bool = True) -> list:
    """
    Fetch Iowa corn price, soybean price, and corn yield from NASS.

    Args:
    use_fallback_on_error: If True, loads the saved CSV fallback if the API
                           fetch fails. If False, returns an empty list on failure.

    Returns a list of dicts, one per data point:
        {
            "label":       "corn_price_iowa",
            "description": "Iowa Corn — Price Received ($ / BU)",
            "year":        "2024",
            "value":       "4.85",
            "unit":        "$ / BU",
            "fetched_at":  "2026-03-28 14:30:00",
        }

    If the API fails and use_fallback_on_error=True, loads the saved CSV instead.
    """
    results = []
    api_failed = False

    for query in QUERIES:
        print(f"\nFetching: {query['description']}")

        if API_KEY == "YOUR_NASS_API_KEY_HERE":
            print("  [SKIP] API key not set.")
            print("  Open nass_api.py and replace YOUR_API_KEY_HERE with your real key.")
            print("  Get one free at: https://api.data.gov/signup/")
            api_failed = True
            break

        record = fetch_latest(query["params"])

        if record is None:
            api_failed = True
            break

        results.append({
            "label":       query["label"],
            "description": query["description"],
            "year":        record.get("year", "N/A"),
            "value":       record.get("Value", "N/A").replace(",", ""),
            "unit":        record.get("unit_desc", "N/A"),
            "fetched_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        print(f"  ✅  {record.get('year')} → "
              f"{record.get('Value')} {record.get('unit_desc')}")

    if not api_failed and len(results) == len(QUERIES):
        save_fallback(results)
        return results

    if use_fallback_on_error:
        print("\n  [FALLBACK MODE] One or more API fetches failed. Loading saved CSV...")
        return load_fallback()

    return results


# ── Helper: format results for ABE responses ──────────────────────────────────

def format_for_abe(results: list) -> str:
    """
    Return a plain-English summary string that ABE can include in a response.

    Example output:
        Iowa Corn Price (2024): $4.85 / BU  [Source: USDA NASS QuickStats]
        Iowa Soybean Price (2024): $11.20 / BU  [Source: USDA NASS QuickStats]
        Iowa Corn Yield (2024): 202.0 BU / ACRE  [Source: USDA NASS QuickStats]

    If results is empty, returns a message indicating data is unavailable.

    Args:
        results: List of dicts as returned by get_iowa_data().
    
    Returns:
        A formatted multi-line string summarizing the data for ABE responses.
    """
    if not results:
        return ("Iowa market data is currently unavailable. "
                "Please check back shortly.")

    label_map = {
        "corn_price_iowa":    "Iowa Corn Price",
        "soybean_price_iowa": "Iowa Soybean Price",
        "corn_yield_iowa":    "Iowa Corn Yield",
    }

    lines = []
    for row in results:
        name       = label_map.get(row["label"], row["description"])
        year       = row.get("year", "N/A")
        value      = row.get("value", "N/A")
        unit       = row.get("unit", "")
        prefix     = "$" if "$" in unit else ""
        clean_unit = unit.replace("$", "").strip()
        lines.append(
            f"{name} ({year}): {prefix}{value} {clean_unit}"
            f"  [Source: USDA NASS QuickStats]"
        )

    return "\n".join(lines)


# ── USDA AMS MARS API (daily Iowa cash prices) ────────────────────────────────

def _mars_auth_header() -> str:
    """
    MARS uses Basic Auth — the API key is the username, password is empty.
    We base64-encode "api_key:" (note the colon) and put it in the header.
    """
    token = base64.b64encode(f"{MARS_API_KEY}:".encode()).decode()
    return f"Basic {token}"


def fetch_iowa_cash_prices() -> list:
    """
    Call the MARS API for today's Iowa corn and soybean cash prices.
    Report 2850 = Iowa Daily Cash Grain Bids.
    Returns a list of raw record dicts, or empty list on failure.
    """
    url = f"{MARS_BASE_URL}{MARS_REPORT_ID}?lastDays=7"

    if MARS_API_KEY == "YOUR_MARS_API_KEY_HERE":
        print("  [SKIP] MARS API key not set.")
        print("  Add MARS_API_KEY to your .env file.")
        print("  Register free at: https://mymarketnews.ams.usda.gov/")
        return []

    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", _mars_auth_header())
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        print(f"  [MARS API ERROR] Could not reach MARS API: {e}")
        return []

    # MARS wraps records in a "results" key
    records = data.get("results", [])
    if not records:
        print("  [MARS WARNING] API responded but returned zero records.")
        return []

    return records


def save_mars_fallback(results: list) -> None:
    """Save MARS cash price results to a CSV fallback file."""
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(MARS_FALLBACK_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n  [SAVED] MARS fallback CSV written to: {MARS_FALLBACK_CSV}")


def load_mars_fallback() -> list:
    """
    Load the saved MARS CSV fallback when the live API is unavailable.
    Returns a list of dicts representing the rows, or empty list if the file is missing.
     """
    if not os.path.exists(MARS_FALLBACK_CSV):
        print("  [MARS FALLBACK ERROR] No MARS fallback CSV found.")
        print("  Run the script once with a working MARS API key to create it.")
        return []
    with open(MARS_FALLBACK_CSV, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"  [MARS FALLBACK] Loaded {len(rows)} rows from {MARS_FALLBACK_CSV}")
    return rows


def get_iowa_cash_prices(use_fallback_on_error: bool = True) -> list:
    """
    Fetch today's Iowa corn and soybean cash prices from USDA AMS MARS API.

    The MARS report 2850 stores prices in a report_narrative text field, e.g.:
    "State Average Price: Corn -- $4.20 ... | Soybeans -- $10.81 ..."
    We parse that string with regex to extract the numbers.

    Returns a list of dicts shaped like:
        {
            "label":       "corn_cash_iowa",
            "description": "Iowa Corn — Daily Cash Price",
            "date":        "03/28/2026",
            "value":       "4.20",
            "unit":        "$ / BU",
            "fetched_at":  "2026-03-28 14:30:00",
        }
    """
    import re

    print("\nFetching: Iowa Daily Cash Grain Bids (USDA AMS MARS)")

    records = fetch_iowa_cash_prices()

    if not records:
        if use_fallback_on_error:
            print("  [MARS FALLBACK MODE] Loading saved CSV...")
            return load_mars_fallback()
        return []

    # Find the most recent record that contains a report_narrative
    narrative   = ""
    report_date = "N/A"
    for r in records:
        if r.get("report_narrative"):
            narrative   = r["report_narrative"]
            report_date = r.get("report_date", "N/A")
            break

    if not narrative:
        print("  [MARS WARNING] No report_narrative found in any record.")
        if use_fallback_on_error:
            print("  [MARS FALLBACK MODE] Loading saved CSV...")
            return load_mars_fallback()
        return []

    # Parse: "Corn -- $4.20" and "Soybeans -- $10.81" from the narrative
    corn_match    = re.search(r"Corn -- \$(\d+\.?\d*)", narrative)
    soybean_match = re.search(r"Soybeans -- \$(\d+\.?\d*)", narrative)

    if not corn_match or not soybean_match:
        print(f"  [MARS WARNING] Could not parse prices from narrative:")
        print(f"  {narrative}")
        if use_fallback_on_error:
            print("  [MARS FALLBACK MODE] Loading saved CSV...")
            return load_mars_fallback()
        return []

    corn_price    = corn_match.group(1)
    soybean_price = soybean_match.group(1)

    results = [
        {
            "label":       "corn_cash_iowa",
            "description": "Iowa Corn — Daily Cash Price",
            "date":        report_date,
            "value":       corn_price,
            "unit":        "$ / BU",
            "fetched_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "label":       "soybean_cash_iowa",
            "description": "Iowa Soybeans — Daily Cash Price",
            "date":        report_date,
            "value":       soybean_price,
            "unit":        "$ / BU",
            "fetched_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    ]

    print(f"  ✅  {report_date} → Corn: ${corn_price} / BU")
    print(f"  ✅  {report_date} → Soybeans: ${soybean_price} / BU")

    save_mars_fallback(results)
    return results


def format_cash_prices_for_abe(results: list) -> str:
    """
    Return a plain-English summary of today's Iowa cash prices for ABE responses.

    Example output:
        Iowa Corn Cash Price (03/28/2026): $4.20 / BU  [Source: USDA AMS MyMarketNews]
        Iowa Soybean Cash Price (03/28/2026): $10.81 / BU  [Source: USDA AMS MyMarketNews]
    """
    if not results:
        return "Today's Iowa cash prices are currently unavailable. Please check back shortly."

    label_map = {
        "corn_cash_iowa":     "Iowa Corn Cash Price",
        "soybean_cash_iowa":  "Iowa Soybean Cash Price",
    }

    lines = []
    for row in results:
        name  = label_map.get(row["label"], row["description"])
        date  = row.get("date", "N/A")
        value = row.get("value", "N/A")
        lines.append(f"{name} ({date}): ${value} / BU  [Source: USDA AMS MyMarketNews]")

    return "\n".join(lines)


# ── Run directly from terminal ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ABE — Iowa Market Data Fetch")
    print("=" * 60)

    print("\n>>> USDA NASS — Annual Benchmark Data")
    nass_data = get_iowa_data()

    print("\n>>> USDA AMS MARS — Today's Cash Prices")
    mars_data = get_iowa_cash_prices()

    print("\n" + "=" * 60)
    print("  SUMMARY FOR ABE")
    print("=" * 60)
    print("\n--- Annual Benchmark (USDA NASS) ---")
    print(format_for_abe(nass_data))
    print("\n--- Today's Cash Prices (USDA AMS) ---")
    print(format_cash_prices_for_abe(mars_data))
    print("=" * 60)
