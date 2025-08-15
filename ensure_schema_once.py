# ensure_schema_once.py — add any missing columns safely (idempotent)
import sqlite3

DB = "qmmx.db"

REQ = {
    "trades": {
        "symbol":"TEXT","direction":"TEXT","entry_price":"REAL","entry_time":"TEXT",
        "confidence":"REAL","pattern_id":"TEXT","pattern":"TEXT","contact_event":"TEXT",
        "status":"TEXT","exit_price":"REAL","exit_time":"TEXT","pnl":"REAL",
        "exit_reason":"TEXT","mode":"TEXT"
    },
    "trade_recommendations": {
        "timestamp":"TEXT","symbol":"TEXT","direction":"TEXT",
        "level_type":"TEXT","reaction_type":"TEXT","approach_direction":"TEXT",
        "macro_position":"TEXT","mode":"TEXT"
    }
}

con = sqlite3.connect(DB)
cur = con.cursor()

# Ensure base tables exist (no-op if already there)
cur.execute("CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT)")
cur.execute("CREATE TABLE IF NOT EXISTS trade_recommendations(id INTEGER PRIMARY KEY AUTOINCREMENT)")

def add_missing(table, cols):
    cur.execute(f"PRAGMA table_info({table})")
    have = {r[1] for r in cur.fetchall()}
    added = []
    for col, typ in cols.items():
        if col not in have:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
            added.append(col)
    return added

added_trades = add_missing("trades", REQ["trades"])
added_recs   = add_missing("trade_recommendations", REQ["trade_recommendations"])

con.commit(); con.close()

print("Added to trades:", added_trades)
print("Added to trade_recommendations:", added_recs)
