"""
run_weather.py — CLI wrapper for ABE's weather skill.

Usage:
  python3 run_weather.py --mode history  --county "Story County" --days 14
  python3 run_weather.py --mode forecast --county "Linn County"
  python3 run_weather.py --mode alerts   --county "Palo Alto County"
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "weather-forecast" / "scripts"))
from weather import run_history, run_forecast, run_alerts
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",   required=True, choices=["history", "forecast", "alerts"])
    parser.add_argument("--county", required=True)
    parser.add_argument("--days",   type=int, default=14)
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
