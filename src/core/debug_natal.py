import sqlite3
conn = sqlite3.connect(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db")
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", [t[0] for t in tables])
for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM [{t[0]}]").fetchone()[0]
    print(f"  {t[0]}: {count} rows")
    cols = conn.execute(f"PRAGMA table_info([{t[0]}])").fetchall()
    print(f"  Columns: {[c[1] for c in cols]}")
    sample = conn.execute(f"SELECT * FROM [{t[0]}] LIMIT 3").fetchall()
    for s in sample:
        print(f"    {s}")
conn.close()
