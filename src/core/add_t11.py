
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

P_9 = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

# 11a: Progressions (Cat 5)
for p in P_9:
    new_rows.append(make_row(f"Progressed_{p}_Sign", "5", "Progressions & Symbolic Time", f"Progressed {p} Sign", "INTEGER"))
    new_rows.append(make_row(f"Solar_Arc_Progressed_{p}_Sign", "5", "Progressions & Symbolic Time", f"Solar Arc Progressed {p} Sign", "INTEGER"))

new_rows.extend([
    make_row("Tertiary_Progressed_Sun_Lon", "5", "Progressions & Symbolic Time", "Tertiary Progressed Sun Lon", "FLOAT"),
    make_row("Tertiary_Progressed_Moon_Lon", "5", "Progressions & Symbolic Time", "Tertiary Progressed Moon Lon", "FLOAT"),
    make_row("Minor_Progressed_Sun_Lon", "5", "Progressions & Symbolic Time", "Minor Progressed Sun Lon", "FLOAT"),
    make_row("Minor_Progressed_Moon_Lon", "5", "Progressions & Symbolic Time", "Minor Progressed Moon Lon", "FLOAT"),
    make_row("Dwadashamsha_Progressed_Sun_Lon", "5", "Progressions & Symbolic Time", "Dwadashamsha Progressed Sun Lon", "FLOAT"),
    make_row("Dwadashamsha_Progressed_Moon_Lon", "5", "Progressions & Symbolic Time", "Dwadashamsha Progressed Moon Lon", "FLOAT"),
])

# 11b: KP Significators (Cat 6)
for h in range(1, 13):
    new_rows.append(make_row(f"KP_House_{h}_Significators", "6", "KP System", f"KP Significators for House {h}", "TEXT", "0"))

new_rows.extend([
    make_row("KP_RP_Vara_Lord", "6", "KP System", "KP Ruling Planet: Vara Lord", "TEXT"),
    make_row("KP_RP_Nakshatra_Lord", "6", "KP System", "KP Ruling Planet: Nakshatra Lord", "TEXT"),
    make_row("KP_RP_Sub_Lord", "6", "KP System", "KP Ruling Planet: Sub Lord", "TEXT"),
    make_row("KP_RP_Ascendant_Lord", "6", "KP System", "KP Ruling Planet: Ascendant Lord", "TEXT"),
])

# 11c: SBC Vedha (Cat 7)
for p in P_9:
    new_rows.append(make_row(f"SBC_{p}_Rasi_Vedha_Flag", "7", "Advanced Chakras", f"SBC {p} Rasi Vedha Flag", "INTEGER"))
    new_rows.append(make_row(f"SBC_{p}_Tithi_Vedha_Flag", "7", "Advanced Chakras", f"SBC {p} Tithi Vedha Flag", "INTEGER"))
    new_rows.append(make_row(f"SBC_{p}_Swara_Vedha_Flag", "7", "Advanced Chakras", f"SBC {p} Swara Vedha Flag", "INTEGER"))

new_rows.extend([
    make_row("Kota_Chakra_Stambha_Flag", "7", "Advanced Chakras", "Kota Chakra Stambha Flag (dist=0)", "INTEGER"),
    make_row("Sanghatta_Chakra_Nakshatra_Resonance_Flag", "7", "Advanced Chakras", "Sanghatta Chakra Nakshatra Resonance Flag", "INTEGER"),
    make_row("Sanghatta_Chakra_Active_Nakshatras_Count", "7", "Advanced Chakras", "Sanghatta Chakra Active Nakshatras Count", "INTEGER"),
])

# 11d: Muhurtha (Cat 8)
new_rows.extend([
    make_row("Muhurtha_Panchapakshi_Activity_Score", "8", "Intraday Muhurtha Micro-Time", "Panchapakshi Activity Score (0-4)", "INTEGER"),
    make_row("Muhurtha_Hora_Number", "8", "Intraday Muhurtha Micro-Time", "Hora Number (1-24)", "INTEGER"),
    make_row("Muhurtha_Choghadiya_Score", "8", "Intraday Muhurtha Micro-Time", "Choghadiya Score (0-5)", "INTEGER"),
    make_row("Muhurtha_Abhijit_Active", "8", "Intraday Muhurtha Micro-Time", "Abhijit Muhurtha Active", "INTEGER"),
    make_row("Muhurtha_Brahma_Active", "8", "Intraday Muhurtha Micro-Time", "Brahma Muhurtha Active", "INTEGER"),
    make_row("Muhurtha_Rahu_Kaal_Active", "8", "Intraday Muhurtha Micro-Time", "Rahu Kaal Active", "INTEGER"),
    make_row("Muhurtha_Gulika_Kaal_Active", "8", "Intraday Muhurtha Micro-Time", "Gulika Kaal Active", "INTEGER"),
    make_row("Muhurtha_Yama_Ghantam_Active", "8", "Intraday Muhurtha Micro-Time", "Yama Ghantam Active", "INTEGER"),
    make_row("Muhurtha_Amrit_Kaal_Active", "8", "Intraday Muhurtha Micro-Time", "Amrit Kaal Active", "INTEGER"),
    make_row("Muhurtha_Pushkara_Navamsa_Active", "8", "Intraday Muhurtha Micro-Time", "Pushkara Navamsa Active", "INTEGER"),
    make_row("Muhurtha_Pushkara_Bhaga_Active", "8", "Intraday Muhurtha Micro-Time", "Pushkara Bhaga Active", "INTEGER"),
    make_row("Muhurtha_Market_Open_Hora_Lord", "8", "Intraday Muhurtha Micro-Time", "Market Open Hora Lord", "TEXT"),
    make_row("Muhurtha_Panchapakshi_Enemy_Bird_Flag", "8", "Intraday Muhurtha Micro-Time", "Panchapakshi Enemy Bird Flag", "INTEGER"),
    make_row("Muhurtha_Vela_Current", "8", "Intraday Muhurtha Micro-Time", "Current Vela", "TEXT"),
    make_row("Muhurtha_Kalam_Current", "8", "Intraday Muhurtha Micro-Time", "Current Kalam", "TEXT"),
])

# 11e: Mundane (Cat 9)
for p_t in P_9:
    for p_n in P_9:
        new_rows.append(make_row(
            f"Transit_{p_t}_Over_India_Natal_{p_n}_Angle", "9", "Mundane Astrology",
            f"Transit {p_t} Angle to India Natal {p_n}", "FLOAT"
        ))
        new_rows.append(make_row(
            f"Transit_{p_t}_Over_USD_Natal_{p_n}_Angle", "9", "Mundane Astrology",
            f"Transit {p_t} Angle to USD Bretton Woods Natal {p_n}", "FLOAT"
        ))

new_rows.append(make_row("Days_Since_Rahu_Nodal_Axis_Shift", "9", "Mundane Astrology", "Days since last Rahu Nodal Axis Shift", "FLOAT"))

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 11 (5-9).")
