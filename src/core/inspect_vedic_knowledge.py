import sqlite3

db_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print("Tables in vedic_knowledge.db:", tables)

# Search for any entities that look like stock tickers or names
c.execute("SELECT entity_name, category, description FROM entities WHERE entity_name LIKE '%reliance%' OR entity_name LIKE '%tcs%' OR entity_name LIKE '%nifty%' LIMIT 20")
rows = c.fetchall()
print("Vedic entities matching Reliance/TCS/Nifty:", len(rows))
for r in rows:
    print(r)

# Search relations
c.execute("SELECT * FROM relations WHERE entity_a LIKE '%reliance%' OR entity_b LIKE '%reliance%' LIMIT 20")
rel_rows = c.fetchall()
print("\nRelations matching Reliance:", len(rel_rows))
for r in rel_rows:
    print(r)

conn.close()
