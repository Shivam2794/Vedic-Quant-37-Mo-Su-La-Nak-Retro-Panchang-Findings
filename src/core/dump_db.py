import sqlite3
import json

db_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\god_memory.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT * FROM memories WHERE content LIKE '%Advance Auto Research Astro%'")
rows = cur.fetchall()

with open(r"F:\Fleet_Master_Archive\Bot_5_Advance_Auto_Research_Astro\god_memory_dump.txt", "w", encoding="utf-8") as f:
    for row in rows:
        f.write(str(row) + "\n")

conn.close()
