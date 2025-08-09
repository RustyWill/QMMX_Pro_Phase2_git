import sqlite3

conn = sqlite3.connect("qmmx.db")
cursor = conn.cursor()

# Expected columns and types
expected_columns = {
    "level_price": "REAL",
    "level_type": "TEXT",
    "level_color": "TEXT",
    "date": "TEXT",
    "symbol": "TEXT",
    "source": "TEXT"
}

# Check existing columns
cursor.execute("PRAGMA table_info(levels)")
existing_columns = {col[1] for col in cursor.fetchall()}

# Add any missing columns
for column, datatype in expected_columns.items():
    if column not in existing_columns:
        cursor.execute(f"ALTER TABLE levels ADD COLUMN {column} {datatype}")
        print(f"✅ Added missing column: {column} ({datatype})")

conn.commit()
conn.close()
