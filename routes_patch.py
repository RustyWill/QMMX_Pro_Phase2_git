# routes_patch.py — drop-in Blueprint for QMMX API additions
from flask import Blueprint, jsonify, request
import sqlite3, os
from upgrade_monitor import track_module_impact, get_upgrade_status

DB_PATH = os.environ.get("QMMX_DB_PATH", "qmmx.db")
bp = Blueprint('qmmx_patch', __name__)

def _db():
    return sqlite3.connect(DB_PATH)

@bp.route('/health')
def health():
    return jsonify({"ok": True})

@bp.route('/upgrade/status')
def upgrade_status():
    return jsonify(get_upgrade_status())

@bp.route('/predictions/current')
def predictions_current():
    symbol = request.args.get('symbol','SPY')
    conn=_db(); cur=conn.cursor()
    cur.execute("""SELECT ts,horizon,target,prob,expected_return,model_version
                  FROM predictions WHERE symbol=? ORDER BY id DESC LIMIT 10""", (symbol,))
    rows=[{"ts":ts,"horizon":h,"target":t,"prob":p,"expected_return":er,"model":mv} for ts,h,t,p,er,mv in cur.fetchall()]
    conn.close()
    return jsonify({"ok": True, "symbol": symbol, "predictions": rows, "status": "warming_up" if not rows else "live"})
