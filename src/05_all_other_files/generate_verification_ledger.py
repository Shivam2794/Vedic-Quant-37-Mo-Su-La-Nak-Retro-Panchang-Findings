import json
import swisseph as swe
from datetime import datetime
import pandas as pd

# Load inception dates
with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\asset_birth_database.json", "r") as f:
    birth_db = json.load(f)

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN
}

ASHTAKVARGA_RULES = {
    "Sun": {"Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11],
            "Mercury": [3,5,6,9,10,11,12], "Jupiter": [5,6,9,11], "Venus": [6,7,12],
            "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [3,4,6,10,11,12]},
    "Moon": {"Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11],
             "Mercury": [1,3,4,5,7,8,10,11], "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11],
             "Saturn": [3,5,6,11], "Ascendant": [3,6,10,11]},
    # We will just output Moon and Sun bindus for verification to keep the CSV readable
}

DASHA_RULERS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120.0

verification_data = []

# Target date for transit verification
target_dt = datetime(2026, 6, 3, 13, 0) # June 3, 2026

for ticker, inception in list(birth_db.items())[:30]: # First 30 assets
    # 1. Natal Chart
    dt = pd.to_datetime(inception)
    natal_jd = swe.julday(dt.year, dt.month, dt.day, 13.0) # 08:00 AM NY time
    
    natal_positions = {}
    natal_signs = {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    for p_name, p_id in PLANET_IDS.items():
        pos = swe.calc_ut(natal_jd, p_id, flags)[0][0]
        natal_positions[p_name] = pos
        natal_signs[p_name] = int(pos / 30) % 12
        
    houses, ascmc = swe.houses_ex(natal_jd, 40.7128, -74.0060, b'W', flags)
    natal_positions["Ascendant"] = ascmc[0]
    natal_signs["Ascendant"] = int(ascmc[0] / 30) % 12
    
    # 2. Ashtakvarga (Sun and Moon specifically for sheet)
    bindu_tables = {p: [0]*12 for p in ["Sun", "Moon"]}
    for transiting_planet, rules in ASHTAKVARGA_RULES.items():
        for contributing_body, relative_signs in rules.items():
            natal_sign = natal_signs[contributing_body]
            for rel_sign in relative_signs:
                target_sign = (natal_sign + rel_sign - 1) % 12
                bindu_tables[transiting_planet][target_sign] += 1
                
    # 3. Dasha on June 3, 2026
    moon_lon = natal_positions["Moon"]
    nakshatra_size = 360.0 / 27.0
    natal_nakshatra_idx = int(moon_lon / nakshatra_size)
    natal_nakshatra_pos = moon_lon % nakshatra_size
    fraction_remaining = (nakshatra_size - natal_nakshatra_pos) / nakshatra_size

    start_idx = natal_nakshatra_idx % 9
    first_dasha_remaining = DASHA_YEARS[start_idx] * fraction_remaining

    days_elapsed = (target_dt.date() - dt.date()).days
    years_elapsed = days_elapsed / 365.25636042

    elapsed_maha = 0.0
    idx = start_idx
    first = True
    while True:
        period = first_dasha_remaining if first else DASHA_YEARS[idx]
        if elapsed_maha + period > years_elapsed: break
        elapsed_maha += period
        idx = (idx + 1) % 9
        first = False
    
    maha_idx = idx
    maha_lord = DASHA_RULERS[maha_idx]
    maha_elapsed_years = years_elapsed - elapsed_maha

    antar_idx = maha_idx
    elapsed_antar = 0.0
    for _ in range(9):
        antar_years = (first_dasha_remaining * DASHA_YEARS[antar_idx]) / DASHA_YEARS[maha_idx] if first else (DASHA_YEARS[maha_idx] * DASHA_YEARS[antar_idx]) / TOTAL_YEARS
        if elapsed_antar + antar_years > maha_elapsed_years: break
        elapsed_antar += antar_years
        antar_idx = (antar_idx + 1) % 9
        
    antar_lord = DASHA_RULERS[antar_idx]

    verification_data.append({
        "Ticker": ticker,
        "Birth_Date": inception,
        "Natal_Moon_Degree": f"{natal_positions['Moon']:.4f}",
        "Natal_Moon_Sign": natal_signs['Moon'],
        "Natal_Sun_Degree": f"{natal_positions['Sun']:.4f}",
        "Ashtakvarga_Sun_Bindus_in_Aries": bindu_tables["Sun"][0],
        "Ashtakvarga_Sun_Bindus_in_Taurus": bindu_tables["Sun"][1],
        "Ashtakvarga_Moon_Bindus_in_Aries": bindu_tables["Moon"][0],
        "Transit_Date": "2026-06-03",
        "Active_Maha_Dasha": maha_lord,
        "Active_Antar_Dasha": antar_lord
    })

df = pd.DataFrame(verification_data)
out_file = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\external_audit_sheet.csv"
df.to_csv(out_file, index=False)
print(f"Verification Ledger generated: {out_file}")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
