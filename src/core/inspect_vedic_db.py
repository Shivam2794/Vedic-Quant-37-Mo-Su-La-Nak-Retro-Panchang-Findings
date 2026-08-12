import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db")
print(f"Reading database: {db_path}")

if not db_path.exists():
    print("Database file not found.")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Get list of tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    print("Tables in database:")
    for t in tables:
        print(f"  - {t[0]}")
        # Get row count
        c.execute(f"SELECT COUNT(*) FROM {t[0]}")
        row_count = c.fetchone()[0]
        print(f"    Rows: {row_count}")
        
    # 2. Inspect table structures and sample data
    for t in tables:
        t_name = t[0]
        print(f"\nSchema of {t_name}:")
        c.execute(f"PRAGMA table_info({t_name})")
        info = c.fetchall()
        for col in info:
            print(f"  - {col[1]} ({col[2]})")
            
        print(f"\nSample data from {t_name} (first 5 rows):")
        c.execute(f"SELECT * FROM {t_name} LIMIT 5")
        rows = c.fetchall()
        for r in rows:
            print(f"  {r}")
            
    conn.close()
