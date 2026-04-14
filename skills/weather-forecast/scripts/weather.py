"""
weather.py — Open-Meteo weather fetcher for ABE.

Three modes:
  history  — past N days of weather for disease context and planting history
  forecast — 16-day forecast for crop impact and planning questions
  alerts   — threshold checks for heartbeat proactive notifications

Usage:
  python3 weather.py --mode history  --county "Story County" --days 14
  python3 weather.py --mode forecast --county "Linn County"
  python3 weather.py --mode alerts   --county "Palo Alto County"
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
import urllib.request
import urllib.parse

COUNTIES_PATH    = Path(__file__).parent.parent.parent.parent / "data" / "iowa_counties.json"
ALERTS_CACHE_PATH = Path(__file__).parent.parent.parent.parent / "data" / "alerts_sent_cache.json"

ARCHIVE_URL  = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Disease pressure thresholds (fungal)
DISEASE_HUMIDITY_MIN = 80   # % relative humidity
DISEASE_TEMP_MIN_F   = 65
DISEASE_TEMP_MAX_F   = 85

# Alert thresholds
FROST_THRESHOLD_F  = 32
HEAT_STRESS_F      = 95
HEAVY_RAIN_INCHES  = 2.0    # per 48-hour window
DROUGHT_DAYS       = 14     # consecutive days with <0.1"
DROUGHT_RAIN_MIN   = 0.1    # inches/day
HIGH_WIND_MPH      = 35     # damaging wind threshold


def load_counties():
    with open(COUNTIES_PATH) as f:
        return json.load(f)


def normalize_county(raw: str) -> str:
    name = raw.strip()
    if name.lower().endswith(" county"):
        name = name[:-7].strip()
    return name


def get_coords(county_raw: str) -> tuple[float, float]:
    counties = load_counties()
    name = normalize_county(county_raw)
    if name in counties:
        c = counties[name]
        return c["lat"], c["lon"]
    for key, val in counties.items():
        if key.lower() == name.lower():
            return val["lat"], val["lon"]
    raise ValueError(f"County not found: '{county_raw}'. Check spelling.")


def fetch_json(url: str, params: dict) -> dict:
    full_url = url + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(full_url, timeout=15) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# MODE: history
# ---------------------------------------------------------------------------

def run_history(county: str, days: int) -> dict:
    lat, lon = get_coords(county)
    end   = date.today() - timedelta(days=1)   # archive lags ~1 day
    start = end - timedelta(days=days - 1)

    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": str(start),
        "end_date":   str(end),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "relative_humidity_2m_max",
            "wind_speed_10m_max",
            "et0_fao_evapotranspiration",
        ]),
        "timezone":           "America/Chicago",
        "temperature_unit":   "fahrenheit",
        "precipitation_unit": "inch",
        "wind_speed_unit":    "mph",
    }

    data  = fetch_json(ARCHIVE_URL, params)
    daily = data["daily"]

    days_data = []
    for i, dt in enumerate(daily["time"]):
        # Handle None values gracefully
        temp_high = daily["temperature_2m_max"][i]
        temp_low = daily["temperature_2m_min"][i]
        precip = daily["precipitation_sum"][i]
        humidity = daily["relative_humidity_2m_max"][i]
        wind = daily["wind_speed_10m_max"][i]
        
        days_data.append({
            "date":          dt,
            "temp_high_f":   round(temp_high, 1) if temp_high is not None else None,
            "temp_low_f":    round(temp_low, 1) if temp_low is not None else None,
            "precip_in":     round(precip, 2) if precip is not None else 0.0,
            "humidity_max":  round(humidity, 1) if humidity is not None else None,
            "wind_max_mph":  round(wind, 1) if wind is not None else None,
        })

    disease_days = sum(
        1 for d in days_data
        if d["humidity_max"] is not None and d["temp_high_f"] is not None
        and d["humidity_max"] >= DISEASE_HUMIDITY_MIN
        and DISEASE_TEMP_MIN_F <= d["temp_high_f"] <= DISEASE_TEMP_MAX_F
    )

    total_precip = round(sum(d["precip_in"] for d in days_data), 2)
    
    # Calculate averages, filtering out None values
    valid_highs = [d["temp_high_f"] for d in days_data if d["temp_high_f"] is not None]
    valid_lows = [d["temp_low_f"] for d in days_data if d["temp_low_f"] is not None]
    valid_humidity = [d["humidity_max"] for d in days_data if d["humidity_max"] is not None]
    valid_wind = [d["wind_max_mph"] for d in days_data if d["wind_max_mph"] is not None]
    
    avg_high     = round(sum(valid_highs) / len(valid_highs), 1) if valid_highs else None
    avg_low      = round(sum(valid_lows) / len(valid_lows), 1) if valid_lows else None
    avg_humidity = round(sum(valid_humidity) / len(valid_humidity), 1) if valid_humidity else None
    avg_wind     = round(sum(valid_wind) / len(valid_wind), 1) if valid_wind else None
    frost_days   = sum(1 for d in days_data if d["temp_low_f"] is not None and d["temp_low_f"] <= FROST_THRESHOLD_F)

    return {
        "mode":                  "history",
        "county":                normalize_county(county),
        "period_start":          str(start),
        "period_end":            str(end),
        "days":                  len(days_data),
        "total_precip_in":       total_precip,
        "avg_high_f":            avg_high,
        "avg_low_f":             avg_low,
        "avg_humidity":          avg_humidity,
        "avg_wind_mph":          avg_wind,
        "frost_days":            frost_days,
        "disease_pressure_days": disease_days,
        "daily":                 days_data,
    }


# ---------------------------------------------------------------------------
# MODE: forecast
# ---------------------------------------------------------------------------

def run_forecast(county: str) -> dict:
    lat, lon = get_coords(county)

    params = {
        "latitude":   lat,
        "longitude":  lon,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "relative_humidity_2m_max",
            "wind_speed_10m_max",
            "weathercode",
        ]),
        "forecast_days":      16,
        "timezone":           "America/Chicago",
        "temperature_unit":   "fahrenheit",
        "precipitation_unit": "inch",
        "wind_speed_unit":    "mph",
    }

    data  = fetch_json(FORECAST_URL, params)
    daily = data["daily"]

    days_data = []
    for i, dt in enumerate(daily["time"]):
        # Handle None values gracefully
        temp_high = daily["temperature_2m_max"][i]
        temp_low = daily["temperature_2m_min"][i]
        precip = daily["precipitation_sum"][i]
        humidity = daily["relative_humidity_2m_max"][i]
        wind = daily["wind_speed_10m_max"][i]
        
        days_data.append({
            "date":            dt,
            "temp_high_f":     round(temp_high, 1) if temp_high is not None else None,
            "temp_low_f":      round(temp_low, 1) if temp_low is not None else None,
            "precip_in":       round(precip, 2) if precip is not None else 0.0,
            "precip_prob_pct": daily["precipitation_probability_max"][i],
            "humidity_max":    round(humidity, 1) if humidity is not None else None,
            "wind_max_mph":    round(wind, 1) if wind is not None else None,
            "weathercode":     daily["weathercode"][i],
        })

    return {
        "mode":    "forecast",
        "county":  normalize_county(county),
        "from":    days_data[0]["date"]  if days_data else None,
        "through": days_data[-1]["date"] if days_data else None,
        "daily":   days_data,
    }


# ---------------------------------------------------------------------------
# MODE: alerts
# ---------------------------------------------------------------------------

def _load_alerts_cache() -> dict:
    if ALERTS_CACHE_PATH.exists():
        with open(ALERTS_CACHE_PATH) as f:
            return json.load(f)
    return {}


def _save_alerts_cache(cache: dict) -> None:
    ALERTS_CACHE_PATH.parent.mkdir(exist_ok=True)
    with open(ALERTS_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def run_alerts(county: str) -> dict:
    alerts  = []
    history  = run_history(county, days=14)
    forecast = run_forecast(county)

    # --- Frost risk (next 5 days) ---
    for day in forecast["daily"][:5]:
        if day["temp_low_f"] is not None and day["temp_low_f"] <= FROST_THRESHOLD_F:
            alerts.append({
                "type":     "frost_risk",
                "date":     day["date"],
                "detail":   f"Low of {day['temp_low_f']}°F forecast — potential frost.",
                "severity": "high",
            })

    # --- Heat stress (next 14 days, growing season May–Aug) ---
    if 5 <= date.today().month <= 8:
        for day in forecast["daily"][:14]:
            if day["temp_high_f"] is not None and day["temp_high_f"] >= HEAT_STRESS_F:
                alerts.append({
                    "type":     "heat_stress",
                    "date":     day["date"],
                    "detail":   f"High of {day['temp_high_f']}°F forecast — heat stress risk during growing season.",
                    "severity": "medium",
                })

    # --- Heavy rain (rolling 48h windows, next 7 days) ---
    fcast_days = forecast["daily"][:7]
    for i in range(len(fcast_days) - 1):
        window_rain = fcast_days[i]["precip_in"] + fcast_days[i + 1]["precip_in"]
        if window_rain >= HEAVY_RAIN_INCHES:
            alerts.append({
                "type":     "heavy_rain",
                "date":     fcast_days[i]["date"],
                "detail":   f"{round(window_rain, 2)}\" forecast over {fcast_days[i]['date']} and {fcast_days[i+1]['date']}.",
                "severity": "medium",
            })

    # --- High wind (next 3 days) ---
    for day in forecast["daily"][:3]:
        if day["wind_max_mph"] >= HIGH_WIND_MPH:
            alerts.append({
                "type":     "high_wind",
                "date":     day["date"],
                "detail":   f"Wind gusts up to {day['wind_max_mph']} mph forecast — risk of lodging or spray drift.",
                "severity": "medium",
            })

    # --- Drought watch (last 14 days) ---
    dry_days = sum(1 for d in history["daily"] if d["precip_in"] < DROUGHT_RAIN_MIN)
    if dry_days >= DROUGHT_DAYS:
        alerts.append({
            "type":     "drought_watch",
            "date":     str(date.today()),
            "detail":   f"{dry_days} of the last 14 days had less than 0.1\" of rain.",
            "severity": "medium",
        })

    # --- Disease pressure window (last 14 days) ---
    if history["disease_pressure_days"] >= 5:
        alerts.append({
            "type":     "disease_pressure",
            "date":     str(date.today()),
            "detail":   f"{history['disease_pressure_days']} days in the last 2 weeks had high humidity (≥80%) and temps 65–85°F — favorable for fungal disease.",
            "severity": "medium",
        })

    # --- Late frost risk for planting (Apr–May specific) ---
    if date.today().month in (4, 5):
        for day in forecast["daily"][:10]:
            if day["temp_low_f"] <= 28:
                alerts.append({
                    "type":     "hard_frost_planting",
                    "date":     day["date"],
                    "detail":   f"Hard frost ({day['temp_low_f']}°F) forecast during planting season — hold off on emerged fields.",
                    "severity": "high",
                })

    # --- Deduplicate: skip alerts already sent for the same county+type+date ---
    county_key = normalize_county(county)
    cache = _load_alerts_cache()
    new_alerts = []
    for alert in alerts:
        cache_key = f"{county_key}:{alert['type']}:{alert['date']}"
        if cache_key not in cache:
            new_alerts.append(alert)
            cache[cache_key] = str(date.today())

    _save_alerts_cache(cache)

    return {
        "mode":        "alerts",
        "county":      county_key,
        "date":        str(date.today()),
        "alerts":      new_alerts,
        "alert_count": len(new_alerts),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",   required=True, choices=["history", "forecast", "alerts"])
    parser.add_argument("--county", required=True, help="Iowa county name (e.g. 'Story County')")
    parser.add_argument("--days",   type=int, default=14, help="Days of history (mode=history only)")
    args = parser.parse_args()

    try:
        if args.mode == "history":
            result = run_history(args.county, args.days)
        elif args.mode == "forecast":
            result = run_forecast(args.county)
        elif args.mode == "alerts":
            result = run_alerts(args.county)

        print(json.dumps(result, indent=2))

    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Request failed: {str(e)}"}))
        sys.exit(1)
