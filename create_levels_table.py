import sqlite3

conn = sqlite3.connect("qmmx.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    subtype TEXT,
    color TEXT,
    value REAL
)
""")

conn.commit()
conn.close()
print("✅ levels table created successfully.")
