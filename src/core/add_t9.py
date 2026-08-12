
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, desc, data_type, tv='1'):
    return {
        'column_name': col_name,
        'category_code': '3A',
        'category_name': 'Dasha Systems',
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []

# 9a: Ashtottari Dasha
new_rows.extend([
    make_row("Ashtottari_MD_Lord", "Ashtottari Mahadasha lord", "TEXT"),
    make_row("Ashtottari_MD_Start", "Ashtottari MD start time", "DATETIME"),
    make_row("Ashtottari_MD_End", "Ashtottari MD end time", "DATETIME"),
    make_row("Ashtottari_MD_Elapsed_Pct", "Percent elapsed in Ashtottari MD", "FLOAT"),
    make_row("Ashtottari_AD_Lord", "Ashtottari Antardasha lord", "TEXT"),
    make_row("Ashtottari_AD_Start", "Ashtottari AD start time", "DATETIME"),
    make_row("Ashtottari_AD_End", "Ashtottari AD end time", "DATETIME"),
    make_row("Ashtottari_AD_Elapsed_Pct", "Percent elapsed in Ashtottari AD", "FLOAT"),
])

# 9b: Yogini Dasha
new_rows.extend([
    make_row("Yogini_MD_Start", "Yogini MD start time", "DATETIME"),
    make_row("Yogini_MD_End", "Yogini MD end time", "DATETIME"),
    make_row("Yogini_MD_Elapsed_Pct", "Percent elapsed in Yogini MD", "FLOAT"),
    make_row("Yogini_AD_Start", "Yogini AD start time", "DATETIME"),
    make_row("Yogini_AD_End", "Yogini AD end time", "DATETIME"),
    make_row("Yogini_AD_Elapsed_Pct", "Percent elapsed in Yogini AD", "FLOAT"),
])

# 9c: Kalachakra Dasha
new_rows.extend([
    make_row("Kalachakra_MD_Start", "Kalachakra MD start time", "DATETIME"),
    make_row("Kalachakra_MD_End", "Kalachakra MD end time", "DATETIME"),
    make_row("Kalachakra_AD_Start", "Kalachakra AD start time", "DATETIME"),
    make_row("Kalachakra_AD_End", "Kalachakra AD end time", "DATETIME"),
])

# 9d: Vimshottari Sookshma/Prana
new_rows.extend([
    make_row("Vimshottari_Sookshma_Start", "Vimshottari Sookshma start time", "DATETIME"),
    make_row("Vimshottari_Sookshma_End", "Vimshottari Sookshma end time", "DATETIME"),
    make_row("Vimshottari_Prana_Start", "Vimshottari Prana start time", "DATETIME"),
    make_row("Vimshottari_Prana_End", "Vimshottari Prana end time", "DATETIME"),
])

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 9 (3A).")
