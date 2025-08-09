# candlestick_chart_provider.py

import json
from datetime import datetime, timedelta
import pandas as pd
import requests

from settings_manager import load_settings
from polygon_io_provider import get_live_price_and_volume

TICKER = "SPY"
DAYS_BACK = 30
LEVELS_FILE = "submitted_levels.json"

def fetch_daily_spy_data():
    """
    Pulls last 30 days of SPY OHLCV using Polygon aggregates REST API.
    """
    settings = load_settings()
    api_key = settings.get("polygon_api_key", "")
    if not api_key:
        return pd.DataFrame()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=DAYS_BACK)

    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/range/1/day/"
        f"{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={api_key}"
    )

    try:
        res = requests.get(url)
        res.raise_for_status()
        results = res.json().get("results", [])
        records = []

        for item in results:
            dt = datetime.fromtimestamp(item["t"] / 1000).strftime("%Y-%m-%d")
            records.append({
                "date": dt,
                "open": item["o"],
                "high": item["h"],
                "low": item["l"],
                "close": item["c"],
                "volume": item["v"]
            })

        return pd.DataFrame(records)
    except Exception as e:
        print(f"[!] Failed to fetch SPY data: {e}")
        return pd.DataFrame()

def load_price_levels(date_key):
    try:
        with open(LEVELS_FILE, "r") as f:
            all_levels = json.load(f)
        return all_levels.get(date_key, {})
    except Exception as e:
        print(f"[!] Error loading levels: {e}")
        return {}

def get_candlestick_chart_payload():
    df = fetch_daily_spy_data()
    if df.empty:
        return {"success": False, "error": "No data returned from Polygon"}

    last_date = df["date"].iloc[-1]
    levels = load_price_levels(last_date)

    return {
        "success": True,
        "candles": df.to_dict(orient="records"),
        "levels": levels
    }
