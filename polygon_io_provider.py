# polygon_io_provider.py
import requests
from settings_manager import load_settings
from diagnostic_monitor import diagnostic_monitor

def get_live_price_and_volume(symbol):
    """
    Returns a tuple: (price, volume)
    """
    settings = load_settings()
    api_key = settings.get("polygon_api_key", "")
    if not api_key:
        diagnostic_monitor.report_error("data_provider", "Polygon API key missing")
        return None, None

    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey={api_key}"
        resp = requests.get(url)
        resp.raise_for_status()
        obj = resp.json()["results"][0]
        price = obj["c"]  # close price
        volume = obj["v"]  # volume
        diagnostic_monitor.ping("data_provider")
        return price, volume
    except Exception as e:
        diagnostic_monitor.report_error("data_provider", str(e))
        return None, None

def get_live_stock_price(symbol):
    """
    Fetch the latest stock price for `symbol` from Polygon.IO.
    Returns a float or None on error.
    """
    settings = load_settings()
    api_key = settings.get("polygon_api_key", "")
    if not api_key:
        diagnostic_monitor.report_error("data_provider", "Polygon API key missing")
        return None

    try:
        url = f"https://api.polygon.io/v1/last/stocks/{symbol}?apiKey={api_key}"
        resp = requests.get(url)
        resp.raise_for_status()
        obj = resp.json()
        price = obj["last"]["price"]
        diagnostic_monitor.ping("data_provider")
        return price
    except Exception as e:
        diagnostic_monitor.report_error("data_provider", str(e))
        return None

def get_option_chain(symbol, exp_date, limit=50):
    """
    Fetch up to `limit` option contracts for `symbol` expiring on `exp_date`.
    Returns a list of contract dicts or empty list on error.
    """
    settings = load_settings()
    api_key = settings.get("polygon_api_key", "")
    if not api_key:
        diagnostic_monitor.report_error("data_provider", "Polygon API key missing")
        return []

    try:
        url = (
            f"https://api.polygon.io/v3/reference/options/contracts"
            f"?underlying_ticker={symbol}"
            f"&expiration_date={exp_date}"
            f"&limit={limit}"
            f"&apiKey={api_key}"
        )
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json().get("results", [])
        diagnostic_monitor.ping("data_provider")
        return data
    except Exception as e:
        diagnostic_monitor.report_error("data_provider", str(e))
        return []

def get_live_option_price(symbol, strike, exp_date, option_type):
    """
    Fetch the last quote for a single option via its constructed symbol.
    """
    settings = load_settings()
    api_key = settings.get("polygon_api_key", "")
    if not api_key:
        diagnostic_monitor.report_error("data_provider", "Polygon API key missing")
        return None

    try:
        option_symbol = build_option_symbol(symbol, exp_date, strike, option_type)
        url = f"https://api.polygon.io/v3/snapshot/options/{symbol}/{option_symbol}?apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data["results"]["lastQuote"]["askPrice"]
        diagnostic_monitor.ping("data_provider")
        return price
    except Exception as e:
        diagnostic_monitor.report_error("data_provider", str(e))
        return None

def build_option_symbol(symbol, exp_date, strike, option_type):
    """
    Convert SPY, 2025-08-02, 450, 'call'
    → 'SPY250802C00450000'
    """
    exp = exp_date.replace("-", "")[2:]  # e.g. '250802'
    typ = "C" if option_type.lower() == "call" else "P"
    strike_formatted = f"{float(strike):08.3f}".replace(".", "")  # '00450000'
    return f"{symbol.upper()}{exp}{typ}{strike_formatted}"
