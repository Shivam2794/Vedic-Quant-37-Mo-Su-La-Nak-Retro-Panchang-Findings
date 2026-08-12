
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, desc, data_type, tv='1'):
    return {
        'column_name': col_name,
        'category_code': '4',
        'category_name': 'Varshaphala Annual Return',
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = [
    make_row("Varshaphala_Muntha_Sign", "Muntha Sign index 0-11", "INTEGER"),
    make_row("Varshaphala_Muntha_Sign_Name", "Muntha Sign name", "TEXT"),
    make_row("Varshaphala_Muntha_House", "Muntha House in Natal chart", "INTEGER"),
    make_row("Varshaphala_Muntha_Lord", "Lord of the Muntha sign", "TEXT"),
    make_row("Varshaphala_Year_Lord", "Varshesh (strongest planet in Varshaphala chart)", "TEXT"),
    make_row("Varshaphala_Saham_Punya", "Punya Saham sign (Lot of Fortune)", "INTEGER"),
    make_row("Varshaphala_Saham_Vida", "Vida Saham sign (Lot of Wisdom)", "INTEGER"),
    make_row("Varshaphala_Saham_Raja", "Raja Saham sign (Lot of Power)", "INTEGER"),
    make_row("Varshaphala_Saham_Karma", "Karma Saham sign (Lot of Action)", "INTEGER"),
    make_row("Varshaphala_Tajika_Aspects_Active", "List of active Tajika aspects", "TEXT"),
    make_row("Varshaphala_Ithasala_Yogas", "Count of Ithasala Yogas (applying aspect)", "INTEGER"),
    make_row("Varshaphala_Ishrafa_Yogas", "Count of Ishrafa Yogas (separating aspect)", "INTEGER"),
    make_row("Varshaphala_Nakta_Yoga", "Presence of Nakta Yoga (translation of light)", "INTEGER"),
    make_row("Varshaphala_Yamaya_Yoga", "Presence of Yamaya Yoga (mutual reception)", "INTEGER"),
    make_row("Varshaphala_Manahila_Yoga", "Presence of Manahila Yoga (cutting aspect)", "INTEGER"),
    make_row("Varshaphala_Mudda_MD_Lord", "Mudda Dasha Mahadasha lord", "TEXT"),
    make_row("Varshaphala_Mudda_AD_Lord", "Mudda Dasha Antardasha lord", "TEXT"),
    make_row("Varshaphala_Dasha_Current_Lord", "Current lord of Varshaphala Dasha", "TEXT"),
]

P_7 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
for p in P_7:
    new_rows.append(make_row(
        f"Varshaphala_Pancha_Vargiya_Bala_{p}",
        f"Tajika 5-varga score for {p}",
        "FLOAT"
    ))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 10 (4).")
