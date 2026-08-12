
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, desc, data_type, tv='0'):
    return {
        'column_name': col_name,
        'category_code': '1B',
        'category_name': 'Natal 16 Varga Matrices',
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []

# 5a, 5b: These were python code fixes in astro_core.py, not new columns.

# 5c: Varga Ascendants
VARGAS = ['D2','D3','D4','D7','D9','D10','D12','D16','D20','D24','D27','D30','D40','D45','D60']

for v in VARGAS:
    new_rows.append(make_row(f"Natal_{v}_Ascendant_Sign", f"{v} Varga Ascendant Sign (0-11)", "INTEGER"))
    new_rows.append(make_row(f"Natal_{v}_Ascendant_Sign_Name", f"{v} Varga Ascendant Sign Name", "TEXT"))
    new_rows.append(make_row(f"Natal_{v}_Ascendant_Lord", f"Lord of {v} Varga Ascendant", "TEXT"))
    new_rows.append(make_row(f"Natal_{v}_Ascendant_Lord_Sign", f"Sign placement of {v} Ascendant Lord in D1", "INTEGER"))
    new_rows.append(make_row(f"Natal_{v}_Ascendant_Lord_House", f"House placement of {v} Ascendant Lord in {v}", "INTEGER"))

# 5d: Vimshopaka Bala
P_7 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
for p in P_7:
    new_rows.append(make_row(
        f"Natal_{p}_Vimshopaka_Bala",
        f"{p} 20-point Vimshopaka Bala score across 16 Vargas",
        "FLOAT"
    ))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 5 (1B).")
