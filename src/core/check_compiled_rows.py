import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM entities WHERE compiled_code IS NOT NULL AND compiled_code != ''")
cnt = c.fetchone()[0]
print(f"Total entities with non-empty compiled_code: {cnt}")

if cnt > 0:
    print("\nSample compiled codes:")
    c.execute("SELECT entity_name, category, compiled_code FROM entities WHERE compiled_code IS NOT NULL AND compiled_code != '' LIMIT 10")
    for name, cat, code in c.fetchall():
        print(f"  - {name:<30} | Cat: {cat:<12} | Code: {code}")
        
conn.close()
