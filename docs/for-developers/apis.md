# External APIs

ABE integrates three external data sources. All API access is centralized in `scripts/nass_api.py` (USDA) and `skills/weather-forecast/scripts/weather.py` (Open-Meteo). Each has a fallback CSV for when the live API is unavailable.

---

## USDA NASS QuickStats

**Purpose:** Annual Iowa crop prices and yields; weekly crop progress reports.

**Base URL:** `https://quickstats.nass.usda.gov/api/`

**Auth:** API key passed in the `key` query parameter. Register at [https://quickstats.nass.usda.gov/api](https://quickstats.nass.usda.gov/api).

**Environment variable:** `NASS_API_KEY`

### What ABE fetches

| Data | NASS parameters | Used for |
|---|---|---|
| Annual corn price (Iowa) | `commodity_desc=CORN`, `statisticcat_desc=PRICE RECEIVED`, `state_name=IOWA` | Yield-normalized price benchmark |
| Annual soybean price (Iowa) | `commodity_desc=SOYBEANS`, `statisticcat_desc=PRICE RECEIVED`, `state_name=IOWA` | Yield-normalized price benchmark |
| Annual corn yield (Iowa) | `commodity_desc=CORN`, `statisticcat_desc=YIELD`, `state_name=IOWA` | Yield assumption for margin calculations |
| Weekly crop progress | `sector_desc=CROPS`, `statisticcat_desc=PROGRESS`, `state_name=IOWA` | Weekly progress messages to farmers |

### Fallback

If NASS is unreachable, the client loads `data/nass_fallback.csv`, which contains the most recently successful annual response.

### Key function

```python
# scripts/nass_api.py
get_iowa_data()           # Returns annual prices and yield
get_iowa_crop_progress()  # Returns weekly progress report
```

---

## USDA AMS MyMarketNews (MARS)

**Purpose:** Daily Iowa cash prices for corn and soybeans.

**Base URL:** `https://marsapi.ams.usda.gov/services/v1.2/`

**Auth:** HTTP Basic Auth. API key is the username; password is empty. Register at [https://mymarketnews.ams.usda.gov/](https://mymarketnews.ams.usda.gov/).

**Environment variable:** `MARS_API_KEY`

### What ABE fetches

ABE requests the most recent daily Iowa cash grain price report from MARS. Prices are parsed from the `report_narrative` field in the API response.

| Data | Used for |
|---|---|
| Iowa corn cash price ($/bu) | Daily price check, margin calculations |
| Iowa soybean cash price ($/bu) | Daily price check, margin calculations |

### Fallback

If MARS is unreachable, the client loads `data/mars_fallback.csv`.

### Key function

```python
# scripts/nass_api.py
get_iowa_cash_prices()  # Returns today's corn and soybean cash prices
```

---

## Open-Meteo

**Purpose:** Real-time weather history, 16-day forecast, and growing-season alert evaluation for any Iowa county.

**Base URL:** `https://api.open-meteo.com/v1/`

**Auth:** None required. Open-Meteo is a free, open-source weather API. See [https://open-meteo.com/](https://open-meteo.com/).

**Environment variable:** None.

### County coordinates

County names are resolved to latitude/longitude using `data/iowa_counties.json`, which contains coordinates for all 99 Iowa counties.

### What ABE fetches

| Mode | Endpoint | Data returned |
|---|---|---|
| `history` | `/archive` | Past N days of temperature, precipitation, humidity, wind |
| `forecast` | `/forecast` | 16-day daily forecast with precipitation probability |
| `alerts` | `/forecast` | Same as forecast; ABE evaluates alert thresholds client-side |

### Alert thresholds

Alert evaluation happens in `weather.py`, not on the API side. Open-Meteo returns raw weather data; the script applies these thresholds:

| Alert | Condition |
|---|---|
| `frost_risk` | Forecast low < 36°F during growing season |
| `hard_frost_planting` | Forecast low < 28°F near planting dates |
| `heat_stress` | Forecast high > 95°F |
| `heavy_rain` | Precipitation > 2 inches in 24 hours |
| `high_wind` | Wind > 35 mph |
| `drought_watch` | < 0.1 inch rain in the past 14 days |
| `disease_pressure` | Humidity > 80% AND temp between 65–85°F for 3+ consecutive days |

### Key function

```python
# skills/weather-forecast/scripts/weather.py
# Called via: .venv/bin/python scripts/run_weather.py --mode [history|forecast|alerts] --county "COUNTY"
```

---

## Error handling and fallbacks

All three API clients follow the same pattern:

1. Attempt the live API call.
2. On any network error or non-200 response, log the error.
3. Load the corresponding fallback CSV from `data/`.
4. Return the fallback data with a flag indicating it is cached.

ABE reports to the farmer when it is using cached data and when the cache was last updated, rather than presenting stale data as current.
