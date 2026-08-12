
import csv
from collections import defaultdict

with open('master_feature_columns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Identify every assumption or ambiguity I need user input on
# before I can write correct code

# 1. Check what data types actually exist
from collections import Counter
type_counts = Counter(r['data_type'] for r in rows)
print("=== CURRENT DATA TYPES ===")
for t, c in type_counts.most_common():
    print(f"  {t}: {c}")

# 2. is_time_varying breakdown
tv_counts = Counter(r['is_time_varying'] for r in rows)
print("\n=== CURRENT is_time_varying ===")
for v, c in tv_counts.most_common():
    print(f"  '{v}': {c}")

# 3. Show the 9 flagged is_time_varying=0 in dynamic cats
print("\n=== 9 WRONGLY-STATIC DYNAMIC COLS ===")
DYNAMIC_CATS = {'3A','4','5','6','7','8','9','10',
                '2A','2B','2C','2D','2E','2F'}
for r in rows:
    if r['category_code'] in DYNAMIC_CATS and r['is_time_varying'] == '0':
        print(f"  [{r['category_code']}] {r['column_name']} | {r['description'][:60]}")

# 4. List all category codes that exist
print("\n=== CATEGORY CODES PRESENT ===")
cats = defaultdict(list)
for r in rows:
    cats[r['category_code']].append(r)
for c in sorted(cats.keys()):
    print(f"  {c}: {len(cats[c])} cols")

# 5. Show full 1D panchang columns to see exactly what exists
print("\n=== ALL CAT 1D COLUMNS ===")
for r in cats['1D']:
    print(f"  {r['column_name']} | {r['data_type']} | {r['description'][:60]}")

# 6. Show full 3A dasha columns
print("\n=== ALL CAT 3A COLUMNS ===")
for r in cats['3A']:
    print(f"  {r['column_name']} | {r['data_type']} | {r['is_time_varying']} | {r['description'][:60]}")

# 7. Show full Cat 8 muhurtha
print("\n=== ALL CAT 8 COLUMNS ===")
for r in cats['8']:
    print(f"  {r['column_name']} | {r['data_type']} | {r['description'][:60]}")

# 8. Show MKT_TARGET
print("\n=== ALL MKT_TARGET COLUMNS ===")
for r in cats['MKT_TARGET']:
    print(f"  {r['column_name']} | {r['data_type']}")

# 9. Show MKT_CONTEXT
print("\n=== ALL MKT_CONTEXT COLUMNS ===")
for r in cats['MKT_CONTEXT']:
    print(f"  {r['column_name']} | {r['data_type']}")
