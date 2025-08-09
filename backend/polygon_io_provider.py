import requests
import os
from datetime import datetime
from diagnostic_monitor import diagnostic_monitor  # ✅ Added

class PolygonDataProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"

    def get_current_price(self, ticker="SPY"):
        url = f"{self.base_url}/v2/last/trade/{ticker}?apiKey={self.api_key}"
        try:
            resp = requests.get(url)
            data = resp.json()
            price = float(data["results"]["p"])
            diagnostic_monitor.ping("data_provider")  # ✅ Ping on success
            return price
        except Exception as e:
            print("Error getting current price:", e)
            diagnostic_monitor.report_error("data_provider", f"Price fetch error: {e}")  # ✅ Error on fail
            return None

    def get_current_volume(self, ticker="SPY"):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/minute/{date_str}/{date_str}?adjusted=true&sort=desc&limit=1&apiKey={self.api_key}"
        try:
            resp = requests.get(url)
            bars = resp.json().get("results", [])
            if bars:
                volume = bars[0].get("v", 0)
                diagnostic_monitor.ping("data_provider")  # ✅ Track volume ping
                return volume
            diagnostic_monitor.report_error("data_provider", "No volume data returned")
            return 0
        except Exception as e:
            print("Error getting volume:", e)
            diagnostic_monitor.report_error("data_provider", f"Volume fetch error: {e}")  # ✅ Error report
            return 0

    def get_option_chain(self, ticker="SPY"):
        url = f"{self.base_url}/v3/snapshot/options/{ticker}?apiKey={self.api_key}"
        try:
            resp = requests.get(url)
            options_data = resp.json().get("results", {}).get("options", [])
            chain = []
            for opt in options_data:
                chain.append({
                    "type": "call" if opt["details"]["contract_type"] == "call" else "put",
                    "strike": float(opt["details"]["strike_price"]),
                    "expiration": opt["details"]["expiration_date"],
                    "underlying_price": float(opt["underlying_asset"]["price"]),
                    "symbol": opt["details"]["symbol"]
                })
            diagnostic_monitor.ping("data_provider")  # ✅ Track successful options load
            return chain
        except Exception as e:
            print("Error fetching option chain:", e)
            diagnostic_monitor.report_error("data_provider", f"Option chain fetch error: {e}")  # ✅ Error report
            return []
