import sqlite3

DB_PATH = "qmmx.db"

def ensure_patterns_and_trades_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create patterns table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        symbol TEXT,
        pattern_name TEXT,
        confidence REAL,
        entry_price REAL,
        exit_price REAL,
        result TEXT,
        evolution_version INTEGER,
        status TEXT DEFAULT 'pending'
    )
    """)

    # Create trades table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        symbol TEXT,
        pattern_name TEXT,
        option_contract TEXT,
        entry_price REAL,
        exit_price REAL,
        pnl REAL,
        exit_reason TEXT,
        confidence REAL
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Verified: 'patterns' and 'trades' tables exist with required schema.")

if __name__ == "__main__":
    ensure_patterns_and_trades_tables()
