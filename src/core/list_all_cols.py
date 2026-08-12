
import csv
from collections import defaultdict

with open('master_feature_columns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

cats = defaultdict(list)
for r in rows:
    cats[r['category_code']].append(r)

# Print ALL column names per category for full audit
for code in ['1A','1B','1C','1D','2A','2B','2C','2D','2E','2F','3A','4','5','6','7','8','9','10',
             'MKT_PRICE','MKT_TECH','MKT_CAL','MKT_CONTEXT','MKT_TARGET']:
    g = cats.get(code,[])
    print(f"\n=== [{code}] {g[0]['category_name'] if g else ''} ({len(g)} cols) ===")
    for r in g:
        print(f"  {r['column_name']} | {r['data_type']} | tv={r['is_time_varying']}")
