# migrate.py — Idempotent DB migrations for QMMX
import sqlite3, os, datetime

DB_PATH = os.environ.get("QMMX_DB_PATH", "qmmx.db")

SCHEMA = [
    # price levels entered by user or mobile
    """CREATE TABLE IF NOT EXISTS price_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        price REAL NOT NULL,
        color TEXT NOT NULL,          -- blue|orange|black|teal
        style TEXT NOT NULL,          -- solid|dashed
        idx   INTEGER DEFAULT 1,
        active INTEGER DEFAULT 1,
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""",

    # level contacts detected by engine
    """CREATE TABLE IF NOT EXISTS level_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        symbol TEXT NOT NULL,
        level_id INTEGER,
        direction TEXT,               -- up|down
        reaction TEXT,                -- reject|break|retest|pass
        distance REAL,
        volume_state TEXT,
        FOREIGN KEY(level_id) REFERENCES price_levels(id)
    )""",

    # detected patterns
    """CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        symbol TEXT NOT NULL,
        kind TEXT NOT NULL,           -- e.g., break_retest, rejection
        confidence REAL DEFAULT 0.0,
        reviewed INTEGER DEFAULT 0,   -- 0=no,1=yes
        status TEXT DEFAULT 'open',   -- open|approved|rejected|review
        note TEXT
    )""",

    # portfolio positions
    """CREATE TABLE IF NOT EXISTS portfolio_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opened_at TEXT NOT NULL,
        closed_at TEXT,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,           -- long|short
        qty REAL DEFAULT 0,
        entry REAL,
        stop REAL,
        target REAL,
        exit_price REAL,
        pnl REAL
    )""",

    # module status heartbeats
    """CREATE TABLE IF NOT EXISTS module_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT NOT NULL,
        ts TEXT NOT NULL,
        status TEXT NOT NULL,         -- OK|ALERT
        detail TEXT
    )""",

    # predictions scaffold
    """CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        symbol TEXT NOT NULL,
        horizon TEXT NOT NULL,        -- 5m|15m|60m
        target TEXT NOT NULL,         -- one_r|level_hold|level_break
        prob REAL,
        expected_return REAL,
        features_json TEXT,
        model_version TEXT
    )""",

    # upgrade monitor snapshots (hardened version expects 'notes')
    """CREATE TABLE IF NOT EXISTS upgrade_score (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        pattern_count INTEGER,
        avg_confidence REAL,
        reviewed_patterns INTEGER,
        review_loop_score REAL,
        score INTEGER,
        notes TEXT
    )"""
]

# --- Add this to migrate.py (keep your existing code) ---
import sqlite3

REQUIRED_TABLES = {
    "trades": {
        "symbol":"TEXT","direction":"TEXT","entry_price":"REAL","entry_time":"TEXT",
        "confidence":"REAL","pattern_id":"TEXT","pattern":"TEXT","contact_event":"TEXT",
        "status":"TEXT","exit_price":"REAL","exit_time":"TEXT","pnl":"REAL","exit_reason":"TEXT","mode":"TEXT"
    },
    "trade_recommendations": {
        "timestamp":"TEXT","symbol":"TEXT","direction":"TEXT",
        "level_type":"TEXT","reaction_type":"TEXT","approach_direction":"TEXT",
        "macro_position":"TEXT","mode":"TEXT"
    }
}

def ensure_schema(db_path="qmmx.db"):
    con = sqlite3.connect(db_path); cur = con.cursor()
    # ensure base tables exist
    cur.execute("""CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY AUTOINCREMENT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS trade_recommendations(
        id INTEGER PRIMARY KEY AUTOINCREMENT
    )""")
    # add any missing columns
    for table, cols in REQUIRED_TABLES.items():
        cur.execute(f"PRAGMA table_info({table})")
        have = {r[1] for r in cur.fetchall()}
        for col, typ in cols.items():
            if col not in have:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    con.commit(); con.close()

def migrate(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for stmt in SCHEMA:
        cur.execute(stmt)
    conn.commit()
    conn.close()
    return {"ok": True, "db": db_path, "migrated_at": datetime.datetime.utcnow().isoformat()}

if __name__ == "__main__":
    print(migrate())
