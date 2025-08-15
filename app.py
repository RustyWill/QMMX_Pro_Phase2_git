from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import time
import os
import requests

import migrate; migrate.migrate()
from backend.pattern_resilience import record_resilience
from exit_strategy import ExitStrategy
from trade_recommender import TradeRecommender
from diagnostic_state import diagnostic_monitor
from pattern_memory_engine import get_current_pattern, mark_pattern_decision
from alerts import get_current_alerts
from qmms_pattern_discovery import PatternDiscoveryEngine
from price_feed import get_latest_price as get_live_price
from settings_store import save_settings
from portfolio_tracker import PortfolioTracker
from threading import Thread
from candlestick_chart_provider import get_candlestick_chart_payload

app = Flask(__name__)
CORS(app)

from routes_patch import bp as patch_bp
app.register_blueprint(patch_bp)

exit_strategy = ExitStrategy()
disc_engine = PatternDiscoveryEngine()
portfolio_tracker = PortfolioTracker()
recommender = TradeRecommender()

DB_PATH = os.getenv("QMMX_DB", "qmmx.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT,
            level_type TEXT,
            level_index INTEGER,
            price REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            direction TEXT,
            entry_price REAL,
            exit_price REAL,
            entry_time TEXT,
            exit_time TEXT,
            confidence REAL,
            status TEXT,
            pattern_id TEXT,
            contact_event TEXT,
            exit_reason TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patterns_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_signature TEXT,
            direction TEXT,
            success_rate REAL,
            total_trades INTEGER,
            successful_trades INTEGER
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/module_status")
def module_status():
    try:
        status = diagnostic_monitor.get_status()
        return jsonify(success=True, status=status)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 200

@app.route("/view_memory/false_missed_analysis", methods=["GET"])
def view_false_missed_analysis():
    try:
        conn = sqlite3.connect("qmmx.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM false_missed_analysis ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/price")
def price():
    symbol = request.args.get("symbol", "SPY")
    try:
        p = get_live_price(symbol)
        return jsonify(success=True, price=p)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 200

@app.route("/get_recommendations")
def get_recs():
    rec = recommender.get_latest_recommendation()  # single or None
    # Return an array so the frontend's .length works
    return jsonify(success=True, recommendations=([rec] if rec else []))

@app.route("/get_alerts")
def get_alerts():
    alerts = get_current_alerts()
    return jsonify(success=True, alerts=alerts)

@app.route("/view_memory/<table_name>", methods=["GET"])
def view_memory_table(table_name):
    import sqlite3
    import os
    db_path = os.path.join(os.getcwd(), "qmmx.db")

    # Supported tables for dropdown viewing
    allowed_tables = [
        "trades_history",
        "patterns_memory",
        "contact_events",
        "user_feedback",
        "volume_profile",
        "portfolio_ledger",
        "module_diagnostics",
        "pattern_evolution",
        "false_missed_analysis",
        "pattern_evolution"
    ]

    table_map = {
    "level_contacts": "contact_events",
    "patterns_memory": "patterns_memory",
    "trades_history": "trades_history",
    "user_feedback": "user_feedback",
    "volume_profile": "volume_profile",
    "portfolio_ledger": "portfolio_ledger",
    "module_diagnostics": "module_diagnostics",
    "pattern_evolution": "pattern_evolution",
    "false_missed_analysis": "false_missed_analysis",
    "pattern_evolution": "pattern_evolution"
}

    # Handle alias
    if table_name == "level_contacts":
        table_name = "contact_events"

    if table_name not in allowed_tables:
        return jsonify({"success": False, "error": f"Table '{table_name}' is not accessible."}), 400

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 500;")
        rows = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "rows": rows})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


#@app.route("/view_memory/<table_name>")
#def view_memory(table_name):
#    conn = sqlite3.connect(DB_PATH)
#    conn.row_factory = sqlite3.Row
#    cur = conn.cursor()
#    try:
#        cur.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 100")
#        rows = [dict(r) for r in cur.fetchall()]
#        return jsonify(success=True, rows=rows)
#    except sqlite3.OperationalError as e:
#        return jsonify(success=False, error=str(e)), 200
#    finally:
#        conn.close()

@app.route("/chart_data")
def chart_data():
    from polygon_io_provider import get_live_price_and_volume
    from polygon_io_provider import load_settings
    symbol = request.args.get("symbol", "SPY")

    # Static memory cache
    if not hasattr(chart_data, "history") or len(chart_data.history) < 2:
        chart_data.history = []

        # ⬇️ Bootstrap with 30 previous 1-min bars
        try:
            settings = load_settings()
            api_key = settings.get("polygon_api_key", "")
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/now-30/minute/now?apiKey={api_key}&limit=30&adjusted=true&sort=asc"
            resp = requests.get(url)
            resp.raise_for_status()
            bars = resp.json().get("results", [])
            for b in bars:
                ts = time.strftime("%H:%M:%S", time.localtime(b["t"] / 1000))
                chart_data.history.append({
                    "time": ts,
                    "price": round(b["c"], 2),
                    "volume": b["v"]
                })
        except Exception as e:
            print("Polygon backfill error:", str(e))

    # Live update every hit
    price, volume = get_live_price_and_volume(symbol)
    if price is not None and volume is not None:
        chart_data.history.append({
            "time": time.strftime("%H:%M:%S"),
            "price": round(price, 2),
            "volume": volume
        })
        chart_data.history = chart_data.history[-60:]

    return jsonify(success=True, data=chart_data.history)

# in backend (Flask)
@app.route("/candlestick_chart_data", methods=["GET"])
def get_candlestick_chart_data():
    payload = {
        "success": True,              # ← add this
        "data": [
            {
                "x": ["2025-08-08","2025-08-08","2025-08-08"],
                "open":  [630, 635, 640],
                "high":  [640, 645, 650],
                "low":   [625, 630, 635],
                "close": [638, 642, 647],
                "type": "candlestick",
                "xaxis": "x",
                "yaxis": "y",
            }
        ],
        "layout": {
            "title": "SPY Candlestick Chart",
            "xaxis": {"rangeslider": {"visible": False}},
            "yaxis": {"autorange": True},
        }
    }
    return jsonify(payload)

@app.route("/get_current_pattern")
def fetch_pattern():
    pat = get_current_pattern()
    return jsonify(success=bool(pat), pattern=pat)

@app.route("/mark_pattern_decision", methods=["POST"])
def submit_pattern_decision():
    data = request.get_json() or {}
    ok = mark_pattern_decision(data.get("pattern_id"), data.get("decision"))
    return jsonify(success=ok)

@app.route("/submit_levels", methods=["POST"])
def submit_levels():
    data = request.get_json() or {}
    levels_by_color = data.get("levels_by_color", {})
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM price_levels")
    for color, groups in levels_by_color.items():
        for level_type in ("solid", "dashed"):
            for idx, price in enumerate(groups.get(level_type, [])):
                try:
                    p = float(price)
                except (TypeError, ValueError):
                    continue
                cur.execute("""INSERT INTO price_levels
                    (color, level_type, level_index, price)
                    VALUES (?, ?, ?, ?)""", (color, level_type, idx, p))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route("/get_portfolio")
def get_portfolio():
    state = portfolio_tracker.get_portfolio()
    for pos in state.get("open_positions", []):
        current = get_live_price("SPY")
        pos["current_price"] = current
        pos["profit"] = (current - pos["entry_price"]) * 1  # buying 1 share
    return jsonify(success=True, **state)

@app.route("/settings", methods=["POST"])
def settings():
    data = request.get_json() or {}
    api_key = data.get("polygon_api_key", "")
    phones = data.get("alert_phone_numbers", [])
    ok = save_settings(api_key, phones)
    return jsonify(success=ok)

@app.route("/analyze")
def analyze_patterns():
    pattern = disc_engine.discover(features={}, levels=[])
    return jsonify(patterns=pattern or [])

@app.route("/evolve_patterns")
def evolve_patterns():
    return jsonify(success=False, error="update_pattern_weights() not implemented")

@app.route("/exit_strategy", methods=["POST"])
def exit_strategy_route():
    params = request.get_json() or {}
    result = exit_strategy.evaluate(**params)
    return jsonify(success=True, **result)

@app.route("/record_resilience", methods=["POST"])
def resilience_route():
    data = request.get_json() or {}
    record_resilience(**data)
    return jsonify(success=True)

@app.route("/ping", methods=["POST"])
def ping_module():
    name = request.json.get("module")
    diagnostic_monitor.ping(name)
    return jsonify(success=True)

@app.route("/get_levels", methods=["GET"])
def get_levels():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT color, level_type, price FROM price_levels")
    rows = cur.fetchall()
    conn.close()

    grouped = {
        "blue": {"solid": [], "dashed": []},
        "orange": {"solid": [], "dashed": []},
        "black": {"solid": [], "dashed": []},
        "teal": {"solid": [], "dashed": []}
    }

    for color, level_type, price in rows:
        if color in grouped and level_type in grouped[color]:
            grouped[color][level_type].append(price)

    return jsonify(grouped)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
