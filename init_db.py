import sqlite3

conn = sqlite3.connect("qmmx.db")
cur = conn.cursor()
cur.execute("""
  CREATE TABLE IF NOT EXISTS price_levels (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    color         TEXT    NOT NULL,
    level_type    TEXT    NOT NULL,
    level_index   INTEGER NOT NULL,
    price         REAL    NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
""")
conn.commit()
conn.close()
print("✅ price_levels table created")
