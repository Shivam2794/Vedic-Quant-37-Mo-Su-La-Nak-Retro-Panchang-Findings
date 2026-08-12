
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Helper to create a row
def make_row(col_name, desc, data_type, tv='0'):
    return {
        'column_name': col_name,
        'category_code': '1A',
        'category_name': 'Natal D1 Core Matrix',
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []

# 4a. Shadbala
P_7 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
balas = ['Sthana', 'Dig', 'Kala', 'Cheshta', 'Naisargika', 'Drig']

for p in P_7:
    for b in balas:
        new_rows.append(make_row(
            f"Natal_{p}_{b}_Bala",
            f"Natal {p} {b} component of Shadbala",
            "FLOAT"
        ))
    new_rows.append(make_row(
        f"Natal_{p}_Total_Shadbala",
        f"Natal {p} Total Shadbala Score",
        "FLOAT"
    ))
    new_rows.append(make_row(
        f"Natal_{p}_Shadbala_Ratio",
        f"Natal {p} Shadbala requirement ratio",
        "FLOAT"
    ))

# 4b. Arudha Padas
for i in range(1, 13):
    new_rows.append(make_row(
        f"Natal_Arudha_Pada_{i}",
        f"Sign index of Arudha Pada for House {i}",
        "INTEGER"
    ))

# 4c. House Lords
for i in range(1, 13):
    new_rows.append(make_row(
        f"Natal_House_{i}_Lord",
        f"Planet ruling natal house {i} cusp sign",
        "TEXT"
    ))
new_rows.append(make_row("Natal_Lagna_Lord", "Planet ruling Ascendant sign", "TEXT"))
new_rows.append(make_row("Natal_Lagna_Lord_House", "House placement of Lagna lord", "INTEGER"))

# 4d. Bhava Chalit
P_9 = P_7 + ['Rahu', 'Ketu']
for p in P_9:
    new_rows.append(make_row(
        f"Natal_{p}_Bhava_Chalit_House",
        f"House placement of {p} in Bhava Chalit (midpoint method)",
        "INTEGER"
    ))
for i in range(1, 13):
    new_rows.append(make_row(
        f"Natal_Bhava_Chalit_Cusp_{i}",
        f"Longitude of Bhava Chalit house {i} cusp",
        "FLOAT"
    ))

# 4e. Upagrahas
upagrahas = ['Dhuma', 'Vyatipata', 'Parivesha', 'Indrachapa', 'Upaketu']
for u in upagrahas:
    new_rows.append(make_row(
        f"Natal_{u}_Lon",
        f"Longitude of Upagraha {u}",
        "FLOAT"
    ))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 4 (1A).")
