
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, desc, data_type, tv='0'):
    return {
        'column_name': col_name,
        'category_code': '1D',
        'category_name': 'Natal Panchang',
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = [
    make_row("Natal_Sunrise_UTC", "Exact UTC time of sunrise at birth", "DATETIME"),
    make_row("Natal_Sunset_UTC", "Exact UTC time of sunset at birth", "DATETIME"),
    make_row("Natal_Moon_Phase_Angle", "Sun-Moon angle in degrees", "FLOAT"),
    make_row("Natal_Ayanamsa_Value_Used", "Exact Lahiri ayanamsha value at birth", "FLOAT"),
    make_row("Natal_Tithi_Deity", "Presiding deity of the birth Tithi", "TEXT"),
    make_row("Natal_Nakshatra_Devata", "Presiding deity of the birth Nakshatra", "TEXT"),
    make_row("Natal_Nakshatra_Gana", "Deva/Manushya/Rakshasa classification", "TEXT"),
    make_row("Natal_Nakshatra_Nadi", "Adi/Madhya/Antya classification", "TEXT"),
    make_row("Natal_Nakshatra_Yoni", "Animal symbol of the Nakshatra", "TEXT"),
    make_row("Natal_Karana_Lord", "Lord of the birth Karana", "TEXT"),
    make_row("Natal_Hora_Lord", "Planetary lord of the birth hour", "TEXT"),
    make_row("Natal_Muhurtha_Name", "Which of 30 specific Muhurthas the birth fell in", "TEXT"),
    make_row("Natal_Rahu_Kaal_Active_Flag", "Rahu Kaal window active at birth", "INTEGER"),
    make_row("Natal_Gulika_Kaal_Active_Flag", "Gulika Kaal window active at birth", "INTEGER"),
    make_row("Natal_Abhijit_Muhurtha_Active_Flag", "Abhijit Muhurtha active at birth", "INTEGER"),
    make_row("Natal_Amrit_Kaal_Active_Flag", "Amrit Kaal active at birth", "INTEGER"),
    make_row("Natal_Brahma_Muhurtha_Active_Flag", "Brahma Muhurtha active at birth", "INTEGER")
]

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 7 (1D).")
