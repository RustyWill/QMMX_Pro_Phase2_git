import sqlite3
from datetime import datetime, timedelta

DB = "qmmx.db"

def get_connection():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def record_resilience(pattern_id, outcome, volatility_score, duration_minutes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pattern_resilience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id TEXT,
            timestamp TEXT,
            outcome TEXT,
            volatility_score REAL,
            duration_minutes INTEGER
        )
    """)
    cursor.execute("""
        INSERT INTO pattern_resilience (pattern_id, timestamp, outcome, volatility_score, duration_minutes)
        VALUES (?, ?, ?, ?, ?)
    """, (pattern_id, datetime.utcnow().isoformat(), outcome, volatility_score, duration_minutes))
    conn.commit()
    conn.close()

def get_resilience_score(pattern_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT outcome, volatility_score, duration_minutes
        FROM pattern_resilience
        WHERE pattern_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (pattern_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0.0

    score = 0
    weight_total = 0

    for outcome, vol_score, duration in rows:
        weight = max(1, duration / 15)
        direction = 1 if outcome == 'win' else -1
        score += direction * vol_score * weight
        weight_total += weight

    return round(score / weight_total, 3) if weight_total else 0.0

def purge_old_resilience_data(days_old=30):
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM pattern_resilience
        WHERE timestamp < ?
    """, (cutoff.isoformat(),))
    conn.commit()
    conn.close()

def get_all_resilience_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pattern_resilience ORDER BY timestamp DESC")
    results = cursor.fetchall()
    conn.close()
    return results
