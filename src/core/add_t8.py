
import csv
from itertools import combinations

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

# 8a: Sade Sati (2E)
new_rows.append(make_row("Transit_Sade_Sati_Active_Flag", "2E", "Transit Daily Panchang", "Sade Sati period active", "INTEGER"))
new_rows.append(make_row("Transit_Sade_Sati_Phase", "2E", "Transit Daily Panchang", "Rising/Peak/Setting phase of Sade Sati", "TEXT"))
new_rows.append(make_row("Transit_Sade_Sati_Year_Count", "2E", "Transit Daily Panchang", "Years into the 7.5 year cycle", "FLOAT"))

# 8b: Chandrashtama (2E)
new_rows.append(make_row("Transit_Chandrashtama_Active_Flag", "2E", "Transit Daily Panchang", "Chandrashtama period active", "INTEGER"))

# 8c: Outer Planet Kinematics (2A)
OUTER = ['Uranus', 'Neptune', 'Pluto']
for p in OUTER:
    new_rows.append(make_row(f"Transit_{p}_Lon_0_360", "2A", "Transit Kinematic Physics", f"{p} ecliptic longitude", "FLOAT"))
    new_rows.append(make_row(f"Transit_{p}_Velocity_DegPerDay", "2A", "Transit Kinematic Physics", f"{p} speed", "FLOAT"))
    new_rows.append(make_row(f"Transit_{p}_Sign_ID", "2A", "Transit Kinematic Physics", f"{p} sign 0-11", "INTEGER"))
    new_rows.append(make_row(f"Transit_{p}_Retrograde_Flag", "2A", "Transit Kinematic Physics", f"{p} retrograde status", "INTEGER"))

# 8d: Graha Yuddha (2B)
YUDDHA = ['Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
for p1, p2 in combinations(YUDDHA, 2):
    new_rows.append(make_row(f"Transit_{p1}_{p2}_War_Flag", "2B", "Transit D1 Sky Matrix", f"{p1}-{p2} Planetary War", "INTEGER"))
    new_rows.append(make_row(f"Transit_{p1}_{p2}_War_Winner", "2B", "Transit D1 Sky Matrix", f"Winner of {p1}-{p2} Planetary War", "TEXT"))

# 8e: Gochara Flags (2B)
P_9 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
for p_t in P_9:
    for p_n in P_9:
        new_rows.append(make_row(
            f"Transit_{p_t}_Conjunct_Natal_{p_n}_Flag", "2B", "Transit D1 Sky Matrix",
            f"Transit {p_t} conjunct Natal {p_n}", "INTEGER"
        ))
        new_rows.append(make_row(
            f"Transit_{p_t}_Conjunct_Natal_{p_n}_Orb", "2B", "Transit D1 Sky Matrix",
            f"Orb of Transit {p_t} to Natal {p_n}", "FLOAT"
        ))

# Transit to Natal House Ingress Counters (2B)
for p in P_9:
    new_rows.append(make_row(
        f"Days_Transit_{p}_In_Current_Natal_House", "2B", "Transit D1 Sky Matrix",
        f"Days {p} has been in its current transit house relative to natal", "FLOAT"
    ))

# 8f: Moorti Ingress Counters (2D)
for p in ['Jupiter', 'Saturn', 'Rahu']:
    new_rows.append(make_row(f"Days_Since_{p}_Sign_Ingress", "2D", "Moorti Nirnaya & Macro", f"Days since {p} entered current sign", "FLOAT"))
    new_rows.append(make_row(f"Days_Until_{p}_Next_Sign_Ingress", "2D", "Moorti Nirnaya & Macro", f"Days until {p} enters next sign", "FLOAT"))

# Missing Moorti Columns (4 types x 4 planets)
for p in ['Jupiter', 'Saturn', 'Rahu', 'Ketu']:
    for m in ['Metal', 'Stone', 'Fire', 'Water']:
        new_rows.append(make_row(f"Transit_{p}_Moorti_{m}", "2D", "Moorti Nirnaya & Macro", f"{p} {m} Moorti flag", "INTEGER"))

# 8g: Chara Lagnas (2A)
LAGNAS = ['Hora', 'Ghati', 'Varnada', 'Sree']
for l in LAGNAS:
    new_rows.append(make_row(f"Transit_{l}_Lagna_Lon", "2A", "Transit Kinematic Physics", f"{l} Lagna longitude", "FLOAT"))
    new_rows.append(make_row(f"Transit_{l}_Lagna_Sign", "2A", "Transit Kinematic Physics", f"{l} Lagna sign", "INTEGER"))

# 8h: SAV Transit Scores (2F)
for h in range(1, 13):
    new_rows.append(make_row(f"Transit_SAV_Score_House_{h}", "2F", "Transit AV Kakshyas", f"SAV score of transit house {h}", "INTEGER"))

P_7 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
for p in P_7:
    new_rows.append(make_row(f"Transit_{p}_Bindus_In_Current_Sign", "2F", "Transit AV Kakshyas", f"Bindus for {p} in its current transit sign", "INTEGER"))

# 8i: Daily Panchang remaining (2E)
new_rows.append(make_row("Transit_Nakshatra_Completion_Percent", "2E", "Transit Daily Panchang", "Percent complete of current Nakshatra", "FLOAT"))
new_rows.append(make_row("Transit_Yoga_Completion_Percent", "2E", "Transit Daily Panchang", "Percent complete of current Yoga", "FLOAT"))
new_rows.append(make_row("Transit_Sunrise_UTC", "2E", "Transit Daily Panchang", "UTC time of today's sunrise", "DATETIME"))
new_rows.append(make_row("Transit_Sunset_UTC", "2E", "Transit Daily Panchang", "UTC time of today's sunset", "DATETIME"))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 8 (2A-2F).")
