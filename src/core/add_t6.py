
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, desc, data_type, tv='0'):
    return {
        'column_name': col_name,
        'category_code': '1C',
        'category_name': 'Natal Extended Esoterics',
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []

# 6a. BAV per planet per house
P_7 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
for p in P_7:
    for h in range(1, 13):
        new_rows.append(make_row(
            f"Natal_{p}_BAV_{h}",
            f"{p} Bhinnashtakavarga score in House {h}",
            "INTEGER"
        ))

# 6b. Shodhya Pinda (Ensuring 12 houses are covered if they aren't - skipping for now, relying on Yogas)

# 6c. Yogas
YOGAS = [
    'Raj', 'Dhana', 'Viparita_Raj', 'Neechabhanga_Raj', 'Parivartana',
    'Gaja_Kesari', 'Budha_Aditya', 'Chandra_Mangal', 'Pancha_Mahapurusha',
    'Kemadruma', 'Voshi', 'Veshi', 'Obhayachari', 'Amala', 'Maha_Bhagya', 'Adhi'
]
for y in YOGAS:
    new_rows.append(make_row(
        f"Natal_{y}_Yoga_Flag",
        f"Presence of {y} Yoga in natal chart",
        "INTEGER"
    ))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 6 (1C).")
