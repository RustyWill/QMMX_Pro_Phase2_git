# price_feed.py
import requests  # ✅ Added
from polygon_io_provider import get_live_stock_price

def get_latest_price(symbol):
    """
    Proxy to live Polygon stock price.
    """
    try:
        # ✅ Ping Visible Pulse Panel
        requests.post("http://127.0.0.1:5000/ping", json={"module": "price_feed"})
    except:
        pass

    return get_live_stock_price(symbol)
