import sqlite3
conn = sqlite3.connect(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\vedic_knowledge.db')
c = conn.cursor()
print('Sample Rules in Entities:')
for r in c.execute("SELECT entity_name FROM entities WHERE is_computable=1 AND category IN ('aspect', 'conjunction', 'dasha', 'yoga') ORDER BY RANDOM() LIMIT 20").fetchall():
    print(' ', r[0])
