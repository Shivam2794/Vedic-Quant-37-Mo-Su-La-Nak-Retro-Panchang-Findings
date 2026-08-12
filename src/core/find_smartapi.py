import sqlite3
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
db_path = r'C:\Users\Shivam Patel\.gemini\antigravity\brain\god_memory.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, facets_json, source FROM entities")
    rows = cursor.fetchall()
    print(f'Total entities checked: {len(rows)}')
    
    found = 0
    for r in rows:
        n, d, fj, s = r
        text = str(n) + str(d) + str(fj) + str(s)
        text_lower = text.lower()
        if 'mpin' in text_lower or 'totp' in text_lower or 'smartapi' in text_lower or 'smart api' in text_lower:
            found += 1
            print('--- FOUND ---')
            print(f'NAME: {n}')
            print(f'DESC: {d}')
            print(f'SOURCE: {s}')
            try:
                print(f'JSON: {json.dumps(json.loads(fj), indent=2)}')
            except:
                print(f'TEXT: {fj}')
    print(f'Total hits: {found}')
except Exception as e:
    print('Error:', e)
