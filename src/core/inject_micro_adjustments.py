
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, cat_code, cat_name, desc, data_type, tv='1'):
    return {
        'column_name': col_name,
        'category_code': cat_code,
        'category_name': cat_name,
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []

# 1. Days_Since_Solar_Return
new_rows.append(make_row(
    "Days_Since_Solar_Return", "4", "Varshaphala Annual Return", 
    "Days elapsed since the most recent solar return", "FLOAT", "1"
))

# 2. Progressed Aspect Orbs
# Find all existing Progressed Aspect Flags
progressed_flags = [r['column_name'] for r in rows if r['column_name'].startswith('Progressed_') and r['column_name'].endswith('_Flag')]

for flag_col in progressed_flags:
    orb_col = flag_col.replace('_Flag', '_Orb')
    new_rows.append(make_row(
        orb_col, "5", "Progressions & Symbolic Time", 
        f"Orb distance for {flag_col.replace('_Flag', '')}", "FLOAT", "1"
    ))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} micro-adjustment columns.")
