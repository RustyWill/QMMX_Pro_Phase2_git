# diagnostic_engine.py

import time
from datetime import datetime, timedelta
from level_loader import load_levels
from price_feed import get_latest_price
from diagnostic_state import diagnostic_monitor
import sqlite3

def run_diagnostics():
    try:
        # Check 1: Levels available
        levels = load_levels()
        if not levels or len(levels) < 3:
            diagnostic_monitor.report_error("pattern_recognizer", "Insufficient level data")
        else:
            diagnostic_monitor.ping("pattern_recognizer")

        # Check 2: Price feed working
        price = get_latest_price("SPY")
        if not price or price <= 0:
            diagnostic_monitor.report_error("data_provider", "Live price unavailable or invalid")
        else:
            diagnostic_monitor.ping("data_provider")

        # Check 3: Last trade within past 5 minutes
        conn = sqlite3.connect("qmmx.db")
        cursor = conn.cursor()
        cursor.execute("SELECT entry_time FROM trades ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            last_trade_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_trade_time > timedelta(minutes=5):
                diagnostic_monitor.report_error("portfolio_tracker", "No recent trades (5+ min)")
            else:
                diagnostic_monitor.ping("portfolio_tracker")
        else:
            diagnostic_monitor.report_error("portfolio_tracker", "No trades found")

    except Exception as e:
        diagnostic_monitor.report_error("diagnostic_engine", f"Failure in diagnostics: {str(e)}")
