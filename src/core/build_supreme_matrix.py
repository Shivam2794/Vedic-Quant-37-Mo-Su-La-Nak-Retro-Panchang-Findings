"""
TRUE JYOTISH ENGINE: Phase 2 & 3 — Ashtakvarga & Supreme Matrix
===============================================================
1. Calculates precise NYSE Natal Chart using Swiss Ephemeris.
2. Computes the 8x12 Ashtakvarga Bindu tables based on classical rules.
3. Computes EXACT Mahadasha, Antardasha, and Pratyantardasha periods from birth Moon.
4. Derives True Combustion, Graha Yuddha, and Nakshatra features.
5. Merges this supreme data with the original genesis matrix.
"""

import os
import pandas as pd
import numpy as np
import swisseph as swe
from datetime import datetime, date

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
RAW_EPHEMERIS = os.path.join(BASE_DIR, "raw_ephemeris_2005_2026.parquet")
GENESIS_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
SUPREME_OUTPUT = os.path.join(BASE_DIR, "supreme_genesis_matrix.parquet")

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ── 1. NYSE NATAL CHART CALCULATION ───────────────────────────────────────
# May 17, 1792. 08:00 AM New York City
# New York in 1792 was Local Mean Time, approx UTC-4:56.
# We will use UTC 13:00 for standardization.
NATAL_JD = swe.julday(1792, 5, 17, 13.0)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN
}

print("Calculating exact NYSE Natal Chart...")
natal_positions = {}
natal_signs = {}
flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
for p_name, p_id in PLANET_IDS.items():
    pos = swe.calc_ut(NATAL_JD, p_id, flags)[0][0]
    natal_positions[p_name] = pos
    natal_signs[p_name] = int(pos / 30) % 12

# Ascendant (Lagna) for 40.7128 N, 74.0060 W at 13:00 UTC
# Using swisseph houses calculation
houses, ascmc = swe.houses_ex(NATAL_JD, 40.7128, -74.0060, b'W', flags)
asc_lon = ascmc[0]  # Ascendant
natal_positions["Ascendant"] = asc_lon
natal_signs["Ascendant"] = int(asc_lon / 30) % 12

print("NYSE Natal Signs:")
for p, s in natal_signs.items():
    print(f"  {p:<10}: Sign {s} (Degree: {natal_positions[p]:.2f}°)")


# ── 2. ASHTAKVARGA BINDU ENGINE ──────────────────────────────────────────
# Classical Jyotish rules for Ashtakvarga:
# A planet grants a bindu (1) to specific signs counted from itself, from other planets, and from Ascendant.
# We map relative positions (1-indexed: 1 means the same sign, 2 means next sign, etc.)

ASHTAKVARGA_RULES = {
    "Sun": {
        "Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11],
        "Mercury": [3,5,6,9,10,11,12], "Jupiter": [5,6,9,11], "Venus": [6,7,12],
        "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [3,4,6,10,11,12]
    },
    "Moon": {
        "Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11],
        "Mercury": [1,3,4,5,7,8,10,11], "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11],
        "Saturn": [3,5,6,11], "Ascendant": [3,6,10,11]
    },
    "Mars": {
        "Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,9,10,11],
        "Mercury": [3,5,6,11], "Jupiter": [6,10,11,12], "Venus": [6,8,11,12],
        "Saturn": [1,4,7,8,9,10,11], "Ascendant": [1,3,6,10,11]
    },
    "Mercury": {
        "Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11], "Mars": [1,2,4,7,8,9,10,11],
        "Mercury": [1,3,5,6,9,10,11,12], "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11],
        "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [1,2,4,6,8,10,11]
    },
    "Jupiter": {
        "Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,7,9,11], "Mars": [1,2,4,7,8,10,11],
        "Mercury": [1,2,4,5,6,9,10,11], "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11],
        "Saturn": [3,5,6,12], "Ascendant": [1,2,4,5,6,9,10,11]
    },
    "Venus": {
        "Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12], "Mars": [3,5,6,9,11,12],
        "Mercury": [3,5,6,9,11], "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11],
        "Saturn": [3,4,5,8,9,10,11], "Ascendant": [1,2,3,4,5,8,9,11]
    },
    "Saturn": {
        "Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11], "Mars": [3,5,6,10,11,12],
        "Mercury": [6,8,9,10,11,12], "Jupiter": [5,6,11,12], "Venus": [6,11,12],
        "Saturn": [3,5,6,11], "Ascendant": [1,3,4,6,10,11]
    }
}

bindu_tables = {p: [0]*12 for p in PLANETS}

for transiting_planet, rules in ASHTAKVARGA_RULES.items():
    for contributing_body, relative_signs in rules.items():
        natal_sign = natal_signs[contributing_body]
        for rel_sign in relative_signs:
            # -1 because rel_sign is 1-indexed (1=same sign)
            target_sign = (natal_sign + rel_sign - 1) % 12
            bindu_tables[transiting_planet][target_sign] += 1

print("\nNYSE Ashtakvarga Bindu Tables (0-8 per sign):")
total_bindus = 0
for p, table in bindu_tables.items():
    print(f"  {p:<10}: {table} (Sum: {sum(table)})")
    total_bindus += sum(table)
print(f"  Sarvashtakavarga Total: {total_bindus} (Must equal 337 for mathematical correctness)")
if total_bindus != 337:
    raise ValueError("Ashtakvarga math failed! Aborting.")


# ── 3. EXACT DASHA CALCULATOR ─────────────────────────────────────────────
# Moon Nakshatra spans 13.333°. 
# NYSE Natal Moon = 2.05° (Ashwini nakshatra, ruled by Ketu)
# Exact remaining fraction = (13.333 - 2.05) / 13.333
moon_lon = natal_positions["Moon"]
nakshatra_size = 360.0 / 27.0
natal_nakshatra_idx = int(moon_lon / nakshatra_size)
natal_nakshatra_pos = moon_lon % nakshatra_size
fraction_remaining = (nakshatra_size - natal_nakshatra_pos) / nakshatra_size

DASHA_RULERS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120.0

start_idx = natal_nakshatra_idx % 9
first_dasha_remaining = DASHA_YEARS[start_idx] * fraction_remaining

def get_exact_dasha(dt):
    # Days elapsed from May 17, 1792
    days_elapsed = (dt.date() - date(1792, 5, 17)).days
    years_elapsed = days_elapsed / 365.25636042  # accurate tropical year

    # Find Maha Dasha
    elapsed_maha = 0.0
    idx = start_idx
    first = True
    while True:
        period = first_dasha_remaining if first else DASHA_YEARS[idx]
        if elapsed_maha + period > years_elapsed:
            break
        elapsed_maha += period
        idx = (idx + 1) % 9
        first = False
    
    maha_idx = idx
    maha_lord = DASHA_RULERS[maha_idx]
    maha_period_total = first_dasha_remaining if first else DASHA_YEARS[maha_idx]
    maha_progress = (years_elapsed - elapsed_maha) / maha_period_total
    maha_elapsed_years = years_elapsed - elapsed_maha

    # Find Antar Dasha
    antar_idx = maha_idx
    elapsed_antar = 0.0
    for _ in range(9):
        # absolute years of antardasha = (maha_total_years * antar_total_years) / 120
        # If we are in the 'first' truncated dasha, proportional rules still apply to the elapsed portion
        if first:
             antar_years = (first_dasha_remaining * DASHA_YEARS[antar_idx]) / DASHA_YEARS[maha_idx]
        else:
             antar_years = (DASHA_YEARS[maha_idx] * DASHA_YEARS[antar_idx]) / TOTAL_YEARS
             
        if elapsed_antar + antar_years > maha_elapsed_years:
            break
        elapsed_antar += antar_years
        antar_idx = (antar_idx + 1) % 9
        
    antar_lord = DASHA_RULERS[antar_idx]
    antar_elapsed_years = maha_elapsed_years - elapsed_antar

    # Find Pratyantar Dasha
    prat_idx = antar_idx
    elapsed_prat = 0.0
    if first:
        actual_antar = (first_dasha_remaining * DASHA_YEARS[antar_idx]) / DASHA_YEARS[maha_idx]
    else:
        actual_antar = (DASHA_YEARS[maha_idx] * DASHA_YEARS[antar_idx]) / TOTAL_YEARS

    for _ in range(9):
        prat_years = (actual_antar * DASHA_YEARS[prat_idx]) / TOTAL_YEARS
        if elapsed_prat + prat_years > antar_elapsed_years:
            break
        elapsed_prat += prat_years
        prat_idx = (prat_idx + 1) % 9
        
    prat_lord = DASHA_RULERS[prat_idx]
    
    return maha_lord, antar_lord, prat_lord


# ── 4. MERGE & CALCULATE SUPREME FEATURES ─────────────────────────────────
print("\nLoading raw ephemeris and genesis matrix...")
df_raw = pd.read_parquet(RAW_EPHEMERIS)
df_gen = pd.read_parquet(GENESIS_FILE)
df_gen["Date"] = pd.to_datetime(df_gen["Date"]).dt.normalize()
df_raw["Date"] = pd.to_datetime(df_raw["Date"]).dt.normalize()

df = pd.merge(df_gen, df_raw, on="Date", how="inner")
print(f"Merged matrix shape: {df.shape}")

print("Deriving exact planetary intelligence...")
# 1. Exact Ashtakvarga
for p in PLANETS:
    lon_col = f"{p}_lon"
    sign_col = f"{p}_sign"
    df[f"{p}_bindus"] = df[sign_col].apply(lambda x: bindu_tables[p][x])
    df[f"{p}_bindu_strong"] = (df[f"{p}_bindus"] >= 5).astype(np.int8)
    df[f"{p}_bindu_weak"] = (df[f"{p}_bindus"] <= 3).astype(np.int8)

# Sarvashtakavarga
df["Sarvashtakavarga"] = df[[f"{p}_bindus" for p in PLANETS]].sum(axis=1)

# 2. Exact Dasha
dasha_res = df["Date"].apply(get_exact_dasha)
df["MahaDasha"] = [x[0] for x in dasha_res]
df["AntarDasha"] = [x[1] for x in dasha_res]
df["PratDasha"] = [x[2] for x in dasha_res]

# Dasha Categorical -> One Hot
for lord in DASHA_RULERS:
    df[f"Maha_{lord}"] = (df["MahaDasha"] == lord).astype(np.int8)
    df[f"Antar_{lord}"] = (df["AntarDasha"] == lord).astype(np.int8)
    df[f"Prat_{lord}"] = (df["PratDasha"] == lord).astype(np.int8)

# 3. Exact True Combustion & Cazimi
COMBUSTION_ORBS = {"Moon": 12.0, "Mars": 17.0, "Mercury": 14.0, "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0}
sun_lon = df["Sun_lon"]
for p, orb in COMBUSTION_ORBS.items():
    diff = (df[f"{p}_lon"] - sun_lon + 180) % 360 - 180
    diff_abs = diff.abs()
    df[f"{p}_true_combust"] = (diff_abs < orb).astype(np.int8)
    df[f"{p}_true_cazimi"] = (diff_abs < 0.5).astype(np.int8)

# 4. Exact Graha Yuddha (Planetary War within 1 degree)
WAR_PAIRS = [("Mercury","Venus"), ("Mercury","Mars"), ("Mercury","Jupiter"), ("Mercury","Saturn"),
             ("Venus","Mars"), ("Venus","Jupiter"), ("Venus","Saturn"),
             ("Mars","Jupiter"), ("Mars","Saturn"), ("Jupiter","Saturn")]
for p1, p2 in WAR_PAIRS:
    diff = ((df[f"{p1}_lon"] - df[f"{p2}_lon"] + 180) % 360 - 180).abs()
    df[f"{p1}_{p2}_true_war"] = (diff < 1.0).astype(np.int8)
    # The one with the lower latitude (closer to ecliptic) wins the war mathematically
    # We define victor if in war
    in_war = (diff < 1.0)
    p1_wins = in_war & (df[f"{p1}_lat"].abs() < df[f"{p2}_lat"].abs())
    p2_wins = in_war & (df[f"{p2}_lat"].abs() < df[f"{p1}_lat"].abs())
    df[f"{p1}_{p2}_war_{p1}_wins"] = p1_wins.astype(np.int8)
    df[f"{p1}_{p2}_war_{p2}_wins"] = p2_wins.astype(np.int8)

# 5. True Retrograde / Station Events
for p in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
    retro = df[f"{p}_retro"]
    prev_retro = retro.shift(1).fillna(0)
    df[f"{p}_true_station_R"] = ((prev_retro == 0) & (retro == 1)).astype(np.int8)
    df[f"{p}_true_station_D"] = ((prev_retro == 1) & (retro == 0)).astype(np.int8)

# 6. Dasha Lord Geometric Distances (Axes)
print("Deriving Dasha Lord Geometry and Gochara Vedha...")
def get_dasha_lon(row, level):
    lord = row[level]
    if lord in ["Rahu", "Ketu"]:
        return row[f"{lord}_lon"]
    return row[f"{lord}_lon"]

df["Maha_lon"] = df.apply(lambda r: get_dasha_lon(r, "MahaDasha"), axis=1)
df["Antar_lon"] = df.apply(lambda r: get_dasha_lon(r, "AntarDasha"), axis=1)
df["Prat_lon"] = df.apply(lambda r: get_dasha_lon(r, "PratDasha"), axis=1)

def calc_axis(lon1, lon2):
    diff = abs((lon1 - lon2 + 180) % 360 - 180)
    # Categorize into 6/8 (150 deg), 2/12 (30), 5/9 (120), Kendra (90,180)
    if 140 <= diff <= 160: return "6_8"
    if 20 <= diff <= 40: return "2_12"
    if 110 <= diff <= 130: return "5_9"
    if diff <= 10 or (80 <= diff <= 100) or (170 <= diff <= 180): return "Kendra"
    return "Neutral"

df["Maha_Antar_Axis"] = df.apply(lambda r: calc_axis(r["Maha_lon"], r["Antar_lon"]), axis=1)
df["Maha_Prat_Axis"] = df.apply(lambda r: calc_axis(r["Maha_lon"], r["Prat_lon"]), axis=1)
df["Antar_Prat_Axis"] = df.apply(lambda r: calc_axis(r["Antar_lon"], r["Prat_lon"]), axis=1)

for axis in ["6_8", "2_12", "5_9", "Kendra"]:
    df[f"Maha_Antar_{axis}"] = (df["Maha_Antar_Axis"] == axis).astype(np.int8)
    df[f"Maha_Prat_{axis}"] = (df["Maha_Prat_Axis"] == axis).astype(np.int8)
    df[f"Antar_Prat_{axis}"] = (df["Antar_Prat_Axis"] == axis).astype(np.int8)

# 7. Gochara Vedha (Transit Obstruction)
# Auspicious house -> Vedha (obstructing) house
VEDHA_PAIRS = {
    "Sun": {3:9, 6:12, 10:4, 11:5},
    "Moon": {1:5, 3:9, 6:12, 7:2, 10:4, 11:8},
    "Mars": {3:12, 6:9, 11:5},
    "Mercury": {2:5, 4:3, 6:9, 8:1, 10:7, 11:12},
    "Jupiter": {2:12, 5:4, 7:3, 9:10, 11:8},
    "Venus": {1:8, 2:7, 3:1, 4:10, 5:9, 8:5, 9:11, 11:6, 12:3},
    "Saturn": {3:12, 6:9, 11:5}
}
natal_moon_sign = natal_signs["Moon"] # 11 (Pisces)

# Calculate house from natal moon for all planets
for p in PLANETS:
    df[f"{p}_house_from_moon"] = ((df[f"{p}_sign"] - natal_moon_sign) % 12) + 1

for p, pairs in VEDHA_PAIRS.items():
    df[f"{p}_Vedha_Blocked"] = 0
    for good_house, block_house in pairs.items():
        is_in_good = (df[f"{p}_house_from_moon"] == good_house)
        # Check if ANY other planet (except Moon) is in the block_house
        is_blocked = pd.Series([False]*len(df))
        for other_p in PLANETS:
            if other_p in [p, "Moon"]: continue
            is_blocked = is_blocked | (df[f"{other_p}_house_from_moon"] == block_house)
        
        df.loc[is_in_good & is_blocked, f"{p}_Vedha_Blocked"] = 1
    df[f"{p}_Vedha_Blocked"] = df[f"{p}_Vedha_Blocked"].astype(np.int8)

# 8. Drop categorical text columns to prepare for XGBoost
df.drop(columns=[
    "MahaDasha", "AntarDasha", "PratDasha", 
    "Maha_lon", "Antar_lon", "Prat_lon",
    "Maha_Antar_Axis", "Maha_Prat_Axis", "Antar_Prat_Axis"
], inplace=True)


df.to_parquet(SUPREME_OUTPUT, index=False)
print(f"\n[SUCCESS] Supreme Matrix built with exactly {len(df.columns)} features.")
print(f"Saved to: {SUPREME_OUTPUT}")
