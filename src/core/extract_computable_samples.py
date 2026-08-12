import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get column names for entities
c.execute("PRAGMA table_info(entities)")
cols = c.fetchall()
print("Entities Columns:")
for col in cols:
    print(f"  - {col[1]} ({col[2]})")

# Count by category for computable entities
print("\nComputable entities by category:")
c.execute("""
    SELECT category, COUNT(*) 
    FROM entities 
    WHERE is_computable = 1 
    GROUP BY category 
    ORDER BY COUNT(*) DESC
""")
for cat, cnt in c.fetchall():
    print(f"  - {cat:<25} : {cnt}")

# Show 30 samples of computable entities with wealth/financial descriptions
print("\nSample Financial/Wealth computable entities:")
c.execute("""
    SELECT entity_name, category, description 
    FROM entities 
    WHERE is_computable = 1 AND (
        description LIKE '%wealth%' OR 
        description LIKE '%money%' OR 
        description LIKE '%profession%' OR 
        description LIKE '%gain%' OR 
        description LIKE '%income%' OR 
        description LIKE '%loss%' OR
        description LIKE '%finance%'
    )
    LIMIT 30
""")
for name, cat, desc in c.fetchall():
    print(f"  - {name:<30} | Cat: {cat:<15} | Desc: {desc[:100]}")
    
conn.close()
