
import csv
from itertools import combinations

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
outer_planets = ["Uranus", "Neptune", "Pluto"]
all_bodies = planets + outer_planets + ["Ascendant"]
higher_vargas = ["D10", "D16", "D20", "D24", "D30", "D40", "D45", "D60"]
sahams = ["Punya", "Karma", "Raja", "Vida"]

# --- NATAL CORE (tv=0) ---
# 1. Natal Distances
for p1, p2 in combinations(all_bodies, 2):
    new_rows.append(make_row(f"Natal_{p1}_Distance_To_Natal_{p2}", "1", "Astrology: Core D1", f"Angular distance between Natal {p1} and {p2}", "FLOAT", "0"))

# 2. Natal SAV Scores
for i in range(1, 13):
    new_rows.append(make_row(f"Natal_SAV_Score_House_{i}", "1C", "Astrology: Esoterics & Yogas", f"Total Sarvashtakvarga score for Natal House {i}", "INTEGER", "0"))

# 3. Dignity, OOB, Vargottama, Dispositors
for p in all_bodies:
    if p != "Ascendant":
        new_rows.append(make_row(f"Natal_{p}_Out_Of_Bounds_Flag", "1", "Astrology: Core D1", f"1 if Natal {p} exceeds 23.45 deg declination", "INTEGER", "0"))
    if p in planets:
        new_rows.append(make_row(f"Natal_{p}_Dignity_Score", "1C", "Astrology: Esoterics & Yogas", f"Panchdha Maitri dignity ordinal (-2 to 2) for {p}", "INTEGER", "0"))
        new_rows.append(make_row(f"Natal_{p}_Vargottama_Flag", "1C", "Astrology: Esoterics & Yogas", f"1 if {p} is in same sign in D1 and D9", "INTEGER", "0"))
        new_rows.append(make_row(f"Natal_{p}_Dispositor_Sign", "1", "Astrology: Core D1", f"Sign ID of the planet ruling {p}'s sign", "INTEGER", "0"))
        new_rows.append(make_row(f"Natal_{p}_Dispositor_Dignity", "1C", "Astrology: Esoterics & Yogas", f"Dignity score of {p}'s dispositor", "INTEGER", "0"))

# 4. Varga Deities
for v in higher_vargas:
    for p in planets:
        new_rows.append(make_row(f"Natal_{v}_{p}_Deity", "1B", "Astrology: Vargas", f"Amsa Deity name for {p} in {v}", "TEXT", "0"))

# 5. Temporal
new_rows.append(make_row("Natal_Days_To_Nearest_Solar_Eclipse", "1D", "Astrology: Panchang", "Float days to nearest solar eclipse", "FLOAT", "0"))
new_rows.append(make_row("Natal_Days_To_Nearest_Lunar_Eclipse", "1D", "Astrology: Panchang", "Float days to nearest lunar eclipse", "FLOAT", "0"))
new_rows.append(make_row("Natal_Ishta_Kaal", "1D", "Astrology: Panchang", "Minutes elapsed since natal sunrise", "FLOAT", "0"))
new_rows.append(make_row("Natal_Tithi_Completion_Percent", "1D", "Astrology: Panchang", "Percent completion of the natal Tithi phase", "FLOAT", "0"))

# --- DYNAMIC CORE (tv=1) ---
# 1. Stationary Flags
for p in planets + outer_planets:
    if p not in ["Sun", "Moon", "Rahu", "Ketu"]: # Only these station
        new_rows.append(make_row(f"Transit_{p}_Stationary_Flag", "2A", "Transits", f"1 if {p} velocity is near 0", "INTEGER", "1"))

# 2. Dasha Bridges
new_rows.append(make_row("Vimshottari_MD_Lord_Natal_Dignity", "3A", "Astrology: Dashas", "Natal dignity ordinal of the current MD lord", "INTEGER", "1"))
new_rows.append(make_row("Vimshottari_AD_Lord_Natal_Dignity", "3A", "Astrology: Dashas", "Natal dignity ordinal of the current AD lord", "INTEGER", "1"))
new_rows.append(make_row("Vimshottari_Chidra_Dasha_Flag", "3A", "Astrology: Dashas", "1 if this is the final destructive AD of the MD", "INTEGER", "1"))

# 3. Varshaphala
for p in planets:
    new_rows.append(make_row(f"Varshaphala_{p}_Combust_Flag", "4", "Varshaphala Annual Return", f"1 if {p} is combust in annual chart", "INTEGER", "1"))
    if p not in ["Sun", "Moon"]:
        new_rows.append(make_row(f"Varshaphala_{p}_Retrograde_Flag", "4", "Varshaphala Annual Return", f"1 if {p} is retrograde in annual chart", "INTEGER", "1"))

new_rows.append(make_row("Varshaphala_Mudda_MD_Elapsed_Pct", "4", "Varshaphala Annual Return", "Completion pct of current Mudda Dasha", "FLOAT", "1"))

for p in planets:
    for s in sahams:
        new_rows.append(make_row(f"Distance_Transit_{p}_To_Varshaphala_{s}", "4", "Varshaphala Annual Return", f"Angular dist from Transit {p} to Varshaphala {s} Saham", "FLOAT", "1"))

# 4. Final Macro Indicators
new_rows.append(make_row("Market_Closed_Days_Since_Last_Tick", "MKT_CONTEXT", "Market Data Context", "Number of calendar days elapsed since previous trading day", "INTEGER", "1"))
new_rows.append(make_row("Transit_Kala_Sarpa_Active_Flag", "2A", "Transits", "1 if all visible planets are bound between Rahu and Ketu", "INTEGER", "1"))
new_rows.append(make_row("Transit_Lunar_Phase_Percent", "2A", "Transits", "0.0 to 1.0 phase of the moon", "FLOAT", "1"))
new_rows.append(make_row("Transit_Distance_To_Nearest_New_Moon", "2A", "Transits", "Float days to exact new moon", "FLOAT", "1"))


# Deduplicate just in case
existing_cols = set(r['column_name'] for r in rows)
clean_new_rows = [r for r in new_rows if r['column_name'] not in existing_cols]

rows.extend(clean_new_rows)

with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Injected {len(clean_new_rows)} new variables. Total columns now: {len(rows)}")
