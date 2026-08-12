
import csv
from collections import Counter

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

total_cols = len(rows)

# 1. Category Balances
cat_counts = Counter(r['category_name'] for r in rows)

# 2. Data Types
dtype_counts = Counter(r['data_type'] for r in rows)

# 3. Time-Varying Split
tv_counts = Counter(r['is_time_varying'] for r in rows)

# 4. Naming Conventions (Parquet compatibility)
illegal_chars = set()
for r in rows:
    for char in r['column_name']:
        if not (char.isalnum() or char == '_'):
            illegal_chars.add(char)

# 5. Duplicate Descriptions (Logical Collisions)
desc_map = {}
duplicate_descs = []
for r in rows:
    desc = r['description'].strip().lower()
    if desc in desc_map:
        duplicate_descs.append((r['column_name'], desc_map[desc]))
    else:
        desc_map[desc] = r['column_name']

# 6. ML Sparsity (Flags vs Continuous)
flag_count = sum(1 for r in rows if '_Flag' in r['column_name'] or '_Active' in r['column_name'])
float_count = sum(1 for r in rows if r['data_type'] == 'FLOAT')

print(f"Total Columns: {total_cols}")
print(f"Data Types: {dict(dtype_counts)}")
print(f"Time Varying (0=Natal, 1=Transit): {dict(tv_counts)}")
print(f"Categories: {dict(cat_counts.most_common(5))} ...")
print(f"Illegal Parquet Chars in Column Names: {illegal_chars}")
print(f"Duplicate Descriptions Count: {len(duplicate_descs)}")
print(f"Boolean Flags vs Floats: {flag_count} Flags, {float_count} Floats")

if duplicate_descs:
    print(f"Sample duplicate descs: {duplicate_descs[:5]}")
