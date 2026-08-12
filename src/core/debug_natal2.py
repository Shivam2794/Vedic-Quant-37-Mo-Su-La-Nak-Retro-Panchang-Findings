import sqlite3
conn = sqlite3.connect(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db")
tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)
for t in tables:
    tickers = [r[0] for r in conn.execute(f"SELECT DISTINCT ticker FROM [{t}]").fetchall()]
    print(f"  {t}: {len(tickers)} unique tickers")
    if len(tickers) < 150:
        print(f"    {sorted(tickers)}")
conn.close()
