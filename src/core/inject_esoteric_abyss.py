
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, cat_code, cat_name, desc, data_type, tv='0'):
    return {
        'column_name': col_name,
        'category_code': cat_code,
        'category_name': cat_name,
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []
planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
retro_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Uranus", "Neptune", "Pluto"]

# 1. Sudarshana
new_rows.append(make_row("Sudarshana_MD_Lord", "3A", "Astrology: Dashas", "Current MD Lord of Sudarshana Dasha", "INTEGER", "1"))
new_rows.append(make_row("Sudarshana_AD_Lord", "3A", "Astrology: Dashas", "Current AD Lord of Sudarshana Dasha", "INTEGER", "1"))

# 2. Tri Pataki
new_rows.append(make_row("Varshaphala_Tri_Pataki_Moon_Vedha_Count", "4", "Varshaphala Annual Return", "Number of malefic vedhas on Moon in Tri Pataki Chakra", "INTEGER", "1"))
new_rows.append(make_row("Varshaphala_Tri_Pataki_Lagna_Vedha_Count", "4", "Varshaphala Annual Return", "Number of malefic vedhas on Lagna in Tri Pataki Chakra", "INTEGER", "1"))

# 3. Nadi
new_rows.append(make_row("Nadi_Macro_Progr_Jupiter_Sign_ID", "5", "Progressions & Symbolic Time", "Sign ID of 12-year Nadi Progressed Jupiter", "INTEGER", "1"))
new_rows.append(make_row("Nadi_Macro_Progr_Saturn_Sign_ID", "5", "Progressions & Symbolic Time", "Sign ID of 30-year Nadi Progressed Saturn", "INTEGER", "1"))

# 4. Karakamsha
for p in planets + ["Ascendant"]:
    new_rows.append(make_row(f"Natal_House_From_Karakamsha_{p}", "1A", "Astrology: Core D1", f"House position of {p} treating Atmakaraka Navamsa sign as House 1", "INTEGER", "0"))

# 5. KP Nodes
new_rows.append(make_row("Natal_KP_Rahu_Acts_As_Planet_ID", "1C", "Astrology: Esoterics & Yogas", "Planet ID whose results Natal Rahu hijacks per KP tenant rules", "INTEGER", "0"))
new_rows.append(make_row("Natal_KP_Ketu_Acts_As_Planet_ID", "1C", "Astrology: Esoterics & Yogas", "Planet ID whose results Natal Ketu hijacks per KP tenant rules", "INTEGER", "0"))
new_rows.append(make_row("Transit_KP_Rahu_Acts_As_Planet_ID", "6", "KP & Nadi Astrology", "Planet ID whose results Transit Rahu hijacks per KP tenant rules", "INTEGER", "1"))
new_rows.append(make_row("Transit_KP_Ketu_Acts_As_Planet_ID", "6", "KP & Nadi Astrology", "Planet ID whose results Transit Ketu hijacks per KP tenant rules", "INTEGER", "1"))

# 6. Geometric Boundaries
for p in planets:
    new_rows.append(make_row(f"Natal_{p}_In_Sarpa_Drekkana_Flag", "1B", "Astrology: Vargas", f"1 if Natal {p} is in a toxic Sarpa Drekkana", "INTEGER", "0"))
    new_rows.append(make_row(f"Natal_{p}_In_Pasha_Drekkana_Flag", "1B", "Astrology: Vargas", f"1 if Natal {p} is in a toxic Pasha Drekkana", "INTEGER", "0"))

for p in retro_planets:
    new_rows.append(make_row(f"Transit_{p}_Retrograde_Crosses_Sign_Boundary_Flag", "2A", "Transits", f"1 if {p} crosses backward into previous sign during current retrogression sweep", "INTEGER", "1"))

existing_cols = set(r['column_name'] for r in rows)
clean_new_rows = [r for r in new_rows if r['column_name'] not in existing_cols]

rows.extend(clean_new_rows)

with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Injected {len(clean_new_rows)} esoteric variables. Total columns now: {len(rows)}")
