"""
DYNAMIC ASSET-SPECIFIC MATRIX BUILDER
=====================================
Calculates individualized Ashtakvarga, Dasha periods, and Vedha rules 
based on the exact inception date of each specific asset.
"""

import os
import json
import pandas as pd
import numpy as np
import swisseph as swe
from datetime import datetime, date
import pytz
import warnings
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
RAW_EPHEMERIS = os.path.join(BASE_DIR, "raw_ephemeris_2005_2026.parquet")
GENESIS_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
ASSET_DIR = os.path.join(BASE_DIR, "asset_matrices")

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
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
    "Mars": {"Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,9,10,11],
             "Mercury": [3,5,6,11], "Jupiter": [6,10,11,12], "Venus": [6,8,11,12],
             "Saturn": [1,4,7,8,9,10,11], "Ascendant": [1,3,6,10,11]},
    "Mercury": {"Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11], "Mars": [1,2,4,7,8,9,10,11],
                "Mercury": [1,3,5,6,9,10,11,12], "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11],
                "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [1,2,4,6,8,10,11]},
    "Jupiter": {"Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,7,9,11], "Mars": [1,2,4,7,8,10,11],
                "Mercury": [1,2,4,5,6,9,10,11], "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11],
                "Saturn": [3,5,6,12], "Ascendant": [1,2,4,5,6,9,10,11]},
    "Venus": {"Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12], "Mars": [3,5,6,9,11,12],
              "Mercury": [3,5,6,9,11], "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11],
              "Saturn": [3,4,5,8,9,10,11], "Ascendant": [1,2,3,4,5,8,9,11]},
    "Saturn": {"Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11], "Mars": [3,5,6,10,11,12],
               "Mercury": [6,8,9,10,11,12], "Jupiter": [5,6,11,12], "Venus": [6,11,12],
               "Saturn": [3,5,6,11], "Ascendant": [1,3,4,6,10,11]}
}

VEDHA_PAIRS = {
    "Sun": {3:9, 6:12, 10:4, 11:5},
    "Moon": {1:5, 3:9, 6:12, 7:2, 10:4, 11:8},
    "Mars": {3:12, 6:9, 11:5},
    "Mercury": {2:5, 4:3, 6:9, 8:1, 10:7, 11:12},
    "Jupiter": {2:12, 5:4, 7:3, 9:10, 11:8},
    "Venus": {1:8, 2:7, 3:1, 4:10, 5:9, 8:5, 9:11, 11:6, 12:3},
    "Saturn": {3:12, 6:9, 11:5}
}

DASHA_RULERS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120.0

def build_asset_matrix(ticker, inception_date, df_base):
    # Calculate Exact Natal Chart for 09:30:00 AM America/New_York
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(f"{inception_date} 09:30:00", "%Y-%m-%d %H:%M:%S")
    dt_ny = ny_tz.localize(dt_naive)
    dt_utc = dt_ny.astimezone(pytz.utc)
    
    # swe.julday expects year, month, day, hour (in decimal)
    utc_hour_decimal = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    natal_jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour_decimal)
    
    natal_positions = {}
    natal_signs = {}
    natal_d9_signs = {}
    natal_d10_signs = {}
    
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    for p_name, p_id in PLANET_IDS.items():
        pos = swe.calc_ut(natal_jd, p_id, flags)[0][0]
        natal_positions[p_name] = pos
        natal_signs[p_name] = int(pos / 30) % 12
        
        # D9 (Navamsha) calculation
        natal_d9_signs[p_name] = int(pos / (10.0 / 3.0)) % 12
        
        # D10 (Dashamsha) calculation
        sign_idx = int(pos / 30)
        part_idx = int((pos % 30) / 3.0)
        if sign_idx % 2 == 0:
            natal_d10_signs[p_name] = (sign_idx + part_idx) % 12
        else:
            natal_d10_signs[p_name] = (sign_idx + 8 + part_idx) % 12
        
    houses, ascmc = swe.houses_ex(natal_jd, 40.7128, -74.0060, b'W', flags)
    natal_positions["Ascendant"] = ascmc[0]
    natal_signs["Ascendant"] = int(ascmc[0] / 30) % 12
    
    # 1. Calculate Individualized Ashtakvarga
    bindu_tables = {p: [0]*12 for p in PLANETS}
    for transiting_planet, rules in ASHTAKVARGA_RULES.items():
        for contributing_body, relative_signs in rules.items():
            natal_sign = natal_signs[contributing_body]
            for rel_sign in relative_signs:
                target_sign = (natal_sign + rel_sign - 1) % 12
                bindu_tables[transiting_planet][target_sign] += 1
                
    # 2. Individualized Dasha Engine
    moon_lon = natal_positions["Moon"]
    nakshatra_size = 360.0 / 27.0
    natal_nakshatra_idx = int(moon_lon / nakshatra_size)
    natal_nakshatra_pos = moon_lon % nakshatra_size
    fraction_remaining = (nakshatra_size - natal_nakshatra_pos) / nakshatra_size

    start_idx = natal_nakshatra_idx % 9
    first_dasha_remaining = DASHA_YEARS[start_idx] * fraction_remaining

    def get_exact_dasha(row_dt):
        days_elapsed = (row_dt.date() - dt_naive.date()).days
        if days_elapsed < 0:
            return "None", "None", "None" # Backtest before inception is invalid anyway
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
        antar_elapsed_years = maha_elapsed_years - elapsed_antar

        prat_idx = antar_idx
        elapsed_prat = 0.0
        actual_antar = (first_dasha_remaining * DASHA_YEARS[antar_idx]) / DASHA_YEARS[maha_idx] if first else (DASHA_YEARS[maha_idx] * DASHA_YEARS[antar_idx]) / TOTAL_YEARS
        for _ in range(9):
            prat_years = (actual_antar * DASHA_YEARS[prat_idx]) / TOTAL_YEARS
            if elapsed_prat + prat_years > antar_elapsed_years: break
            elapsed_prat += prat_years
            prat_idx = (prat_idx + 1) % 9
            
        prat_lord = DASHA_RULERS[prat_idx]
        return maha_lord, antar_lord, prat_lord

    # 3. Apply to DataFrame
    df = df_base.copy()
    
    # Ashtakvarga
    for p in PLANETS:
        df[f"{p}_bindus"] = df[f"{p}_sign"].apply(lambda x: bindu_tables[p][x])
    df["Sarvashtakavarga"] = df[[f"{p}_bindus" for p in PLANETS]].sum(axis=1)
    
    # Dasha
    dasha_res = df["Date"].apply(get_exact_dasha)
    df["MahaDasha"] = [x[0] for x in dasha_res]
    df["AntarDasha"] = [x[1] for x in dasha_res]
    df["PratDasha"] = [x[2] for x in dasha_res]

    for lord in DASHA_RULERS:
        df[f"Maha_{lord}"] = (df["MahaDasha"] == lord).astype(np.int8)
        df[f"Antar_{lord}"] = (df["AntarDasha"] == lord).astype(np.int8)
        df[f"Prat_{lord}"] = (df["PratDasha"] == lord).astype(np.int8)
        
    # Dasha Geometry
    def get_dasha_lon(row, level):
        lord = row[level]
        if lord == "None": return 0.0
        if lord in ["Rahu", "Ketu"]: return row[f"{lord}_lon"]
        return row[f"{lord}_lon"]

    df["Maha_lon"] = df.apply(lambda r: get_dasha_lon(r, "MahaDasha"), axis=1)
    df["Antar_lon"] = df.apply(lambda r: get_dasha_lon(r, "AntarDasha"), axis=1)
    df["Prat_lon"] = df.apply(lambda r: get_dasha_lon(r, "PratDasha"), axis=1)

    def calc_axis(lon1, lon2):
        if lon1 == 0.0 or lon2 == 0.0: return "Neutral"
        diff = abs((lon1 - lon2 + 180) % 360 - 180)
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
        
    # D9 and D10 features (Natal)
    for p in PLANETS:
        df[f"{p}_Natal_D9_Sign"] = natal_d9_signs[p]
        df[f"{p}_Natal_D10_Sign"] = natal_d10_signs[p]
        
    # Vedha
    natal_moon_sign = natal_signs["Moon"]
    for p in PLANETS:
        df[f"{p}_house_from_moon"] = ((df[f"{p}_sign"] - natal_moon_sign) % 12) + 1

    for p, pairs in VEDHA_PAIRS.items():
        df[f"{p}_Vedha_Blocked"] = 0
        for good_house, block_house in pairs.items():
            is_in_good = (df[f"{p}_house_from_moon"] == good_house)
            is_blocked = pd.Series([False]*len(df))
            for other_p in PLANETS:
                if other_p in [p, "Moon"]: continue
                is_blocked = is_blocked | (df[f"{other_p}_house_from_moon"] == block_house)
            df.loc[is_in_good & is_blocked, f"{p}_Vedha_Blocked"] = 1
        df[f"{p}_Vedha_Blocked"] = df[f"{p}_Vedha_Blocked"].astype(np.int8)

    # Universal features (Combustion, Station, Graha Yuddha) are pre-calculated in the base matrix 
    # to save extreme processing time, since they are universal for Earth.
    
    # Cleanup
    df.drop(columns=[
        "MahaDasha", "AntarDasha", "PratDasha", 
        "Maha_lon", "Antar_lon", "Prat_lon",
        "Maha_Antar_Axis", "Maha_Prat_Axis", "Antar_Prat_Axis",
        *[f"{p}_house_from_moon" for p in PLANETS]
    ], inplace=True)
    
    out_path = os.path.join(ASSET_DIR, f"{ticker}_matrix.parquet")
    df.to_parquet(out_path, index=False)
    print(f"✅ Built {ticker} dynamic matrix: {len(df.columns)} features. Saved to {out_path}")

def generate_all():
    db_file = os.path.join(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch", "asset_birth_database.json")
    with open(db_file, "r") as f:
        birth_db = json.load(f)
        
    print("Loading base matrices...")
    # Base matrix already has the universal features (Cazimi, Yuddha, Station) which I computed globally
    # I will load the old genesis matrix which I previously added the universal true features to
    df_base = pd.read_parquet(os.path.join(BASE_DIR, "supreme_genesis_matrix.parquet"))
    
    # We must strip out the old NYSE-specific features before passing it as a base
    nyse_cols = [c for c in df_base.columns if any(tag in c for tag in [
        "_bindus", "Sarvashtakavarga", "Maha_", "Antar_", "Prat_", "_Vedha_Blocked"
    ])]
    df_base.drop(columns=nyse_cols, inplace=True, errors='ignore')
    
    print(f"Base Universal Matrix shape: {df_base.shape}")
    print(f"Generating personalized matrices for {len(birth_db)} assets...\n")
    
    for ticker, inception in birth_db.items():
        build_asset_matrix(ticker, inception, df_base)

if __name__ == "__main__":
    generate_all()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
