
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Fix duplicates (keep first)
seen = set()
unique_rows = []
for r in rows:
    col = r['column_name']
    if col not in seen:
        seen.add(col)
        unique_rows.append(r)

# Fix INT -> INTEGER
for r in unique_rows:
    if r['data_type'] == 'INT':
        r['data_type'] = 'INTEGER'
    elif r['data_type'] == 'STRING':
        r['data_type'] = 'TEXT'

with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=unique_rows[0].keys())
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"Removed duplicates and fixed INT types. Total unique columns: {len(unique_rows)}")
