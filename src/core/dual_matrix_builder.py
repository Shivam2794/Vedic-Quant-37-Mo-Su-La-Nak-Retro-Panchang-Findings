import os
import json
import pandas as pd
import numpy as np
import swisseph as swe
from datetime import datetime
import pytz
import warnings
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE # Ketu is +180 deg
}

ASHTAKVARGA_RULES = {
    "Sun": {"Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11],
            "Mercury": [3,5,6,9,10,11,12], "Jupiter": [5,6,9,11], "Venus": [6,7,12],
            "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [3,4,6,10,11,12]},
    "Moon": {"Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11],
             "Mercury": [1,3,4,5,7,8,10,11], "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11],
             "Saturn": [3,5,6,11], "Ascendant": [3,6,10,11]},
    "Mars": {"Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,10,11],
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
    "Saturn": {"Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11], "Mars": [3,5,6,10,11],
               "Mercury": [6,8,9,10,11,12], "Jupiter": [5,6,11,12], "Venus": [6,11,12],
               "Saturn": [3,5,6,11], "Ascendant": [1,3,4,6,10,11]}
}

VEDHA_RULES = {
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

def calc_astrology(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_ny = ny_tz.localize(dt_naive)
    dt_utc = dt_ny.astimezone(pytz.utc)
    utc_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    
    pos, signs, d9, d10 = {}, {}, {}, {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    for p_name, p_id in PLANET_IDS.items():
        if p_name == "Ketu":
            val = (pos["Rahu"] + 180.0) % 360.0
        else:
            val = swe.calc_ut(jd, p_id, flags)[0][0]
        pos[p_name] = val
        signs[p_name] = int(val / 30) % 12
        d9[p_name] = int(val / (10.0 / 3.0)) % 12
        
        sign_idx = int(val / 30)
        part_idx = int((val % 30) / 3.0)
        if sign_idx % 2 == 0:
            d10[p_name] = (sign_idx + part_idx) % 12
        else:
            d10[p_name] = (sign_idx + 8 + part_idx) % 12
            
    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    pos["Ascendant"] = ascmc[0]
    signs["Ascendant"] = int(ascmc[0] / 30) % 12
    d9["Ascendant"] = int(ascmc[0] / (10.0 / 3.0)) % 12
    sign_idx = int(ascmc[0] / 30)
    part_idx = int((ascmc[0] % 30) / 3.0)
    d10["Ascendant"] = (sign_idx + part_idx) % 12 if sign_idx % 2 == 0 else (sign_idx + 8 + part_idx) % 12
    
    # Ashtakvarga
    bindus = {p: [0]*12 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    for transiting, rules in ASHTAKVARGA_RULES.items():
        for contrib, rel_signs in rules.items():
            s = signs[contrib]
            for r in rel_signs:
                bindus[transiting][(s + r - 1) % 12] += 1
                
    # Dasha Setup
    moon_lon = pos["Moon"]
    n_size = 360.0 / 27.0
    n_idx = int(moon_lon / n_size)
    n_pos = moon_lon % n_size
    frac = (n_size - n_pos) / n_size
    start_idx = n_idx % 9
    first_rem = DASHA_YEARS[start_idx] * frac
    
    return {
        "dt_naive": dt_naive,
        "signs": signs,
        "d9": d9,
        "d10": d10,
        "bindus": bindus,
        "start_idx": start_idx,
        "first_rem": first_rem
    }

def get_dasha(row_dt, astro_data):
    days_elapsed = (row_dt.date() - astro_data["dt_naive"].date()).days
    if days_elapsed < 0: return "None", "None", "None"
    y_el = days_elapsed / 365.25636042
    
    el_maha = 0.0
    idx = astro_data["start_idx"]
    first = True
    while True:
        period = astro_data["first_rem"] if first else DASHA_YEARS[idx]
        if el_maha + period > y_el: break
        el_maha += period
        idx = (idx + 1) % 9
        first = False
    maha_lord = DASHA_RULERS[idx]
    maha_el = y_el - el_maha
    
    a_idx = idx
    el_a = 0.0
    first_a = True
    for _ in range(9):
        a_years = (astro_data["first_rem"] * DASHA_YEARS[a_idx]) / DASHA_YEARS[idx] if first_a else (DASHA_YEARS[idx] * DASHA_YEARS[a_idx]) / TOTAL_YEARS
        if el_a + a_years > maha_el: break
        el_a += a_years
        a_idx = (a_idx + 1) % 9
        first_a = False
    antar_lord = DASHA_RULERS[a_idx]
    
    p_idx = a_idx
    el_p = 0.0
    a_y_full = (DASHA_YEARS[idx] * DASHA_YEARS[a_idx]) / TOTAL_YEARS
    a_rem = a_y_full - el_a
    for _ in range(9):
        p_years = (DASHA_YEARS[p_idx] / TOTAL_YEARS) * a_y_full
        if el_p + p_years > a_rem: break
        el_p += p_years
        p_idx = (p_idx + 1) % 9
    prat_lord = DASHA_RULERS[p_idx]
    
    return maha_lord, antar_lord, prat_lord

def build_dual_matrix(ticker, inception_dates, df_base):
    print(f"Building dual matrix for {ticker}...")
    df = df_base.copy()
    
    conception = calc_astrology(inception_dates["conception"])
    trading = calc_astrology(inception_dates["trading"])
    
    for prefix, data in [("Conceptional", conception), ("Trading", trading)]:
        dasha_maha, dasha_antar, dasha_prat = zip(*[get_dasha(pd.to_datetime(dt), data) for dt in df["Date"]])
        df[f"{prefix}_Maha_Dasha"] = dasha_maha
        df[f"{prefix}_Antar_Dasha"] = dasha_antar
        df[f"{prefix}_Pratyantar_Dasha"] = dasha_prat
        
        for p in PLANETS:
            df[f"{prefix}_{p}_Maha"] = (df[f"{prefix}_Maha_Dasha"] == p).astype(np.int8)
            df[f"{prefix}_{p}_Antar"] = (df[f"{prefix}_Antar_Dasha"] == p).astype(np.int8)
            df[f"{prefix}_{p}_Prat"] = (df[f"{prefix}_Pratyantar_Dasha"] == p).astype(np.int8)
            
            df[f"{prefix}_{p}_Natal_D9"] = data["d9"][p]
            df[f"{prefix}_{p}_Natal_D10"] = data["d10"][p]
            df[f"{prefix}_{p}_Natal_Sign"] = data["signs"][p]
            
        # Calculate transiting signs on the fly
        def get_transiting_sign(row_dt, p_id):
            utc_hour = 12.0 # Noon UTC
            jd = swe.julday(row_dt.year, row_dt.month, row_dt.day, utc_hour)
            flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
            lon = swe.calc_ut(jd, p_id, flags)[0][0]
            return int(lon / 30) % 12
            
        transiting_signs_cache = {}
        for t_p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            transiting_signs_cache[t_p] = df["Date"].apply(lambda d: get_transiting_sign(pd.to_datetime(d), PLANET_IDS[t_p]))
            df[f"{prefix}_{t_p}_Transiting_Sign"] = transiting_signs_cache[t_p]
            
            def get_bindus(x):
                try: return data["bindus"][t_p][int(x)]
                except: return 0
            df[f"{prefix}_{t_p}_Transit_Bindus"] = df[f"{prefix}_{t_p}_Transiting_Sign"].apply(get_bindus)
            
        natal_moon = data["signs"]["Moon"]
        for transiting in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            df[f"{prefix}_{transiting}_From_Moon"] = (df[f"{prefix}_{transiting}_Transiting_Sign"] - natal_moon + 12) % 12 + 1
            
        for transiting in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if transiting in VEDHA_RULES:
                def is_vedha(row, transiting=transiting):
                    from_moon = row[f"{prefix}_{transiting}_From_Moon"]
                    if from_moon in VEDHA_RULES[transiting]:
                        obs = VEDHA_RULES[transiting][from_moon]
                        for op in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                            if op == transiting: continue
                            if row[f"{prefix}_{op}_From_Moon"] == obs:
                                return 1
                    return 0
                df[f"{prefix}_{transiting}_Vedha_Active"] = df.apply(is_vedha, axis=1)
                
    cols_to_drop = [c for c in df.columns if c.endswith(("_Maha_Dasha", "_Antar_Dasha", "_Pratyantar_Dasha", "_Transiting_Sign", "_From_Moon"))]
    df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
    
    out_dir = r"C:\Users\patel\Desktop\Python\Learn\asset_matrices_dual"
    os.makedirs(out_dir, exist_ok=True)
    df.to_parquet(os.path.join(out_dir, f"{ticker}_matrix.parquet"))
    print(f"✅ Built {ticker} dual matrix: {df.shape[1]} features.")

if __name__ == "__main__":
    db_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\asset_birth_database.json"
    with open(db_path, "r") as f:
        birth_db = json.load(f)
        
    base_path = r"C:\Users\patel\Desktop\Python\Learn\supreme_genesis_matrix.parquet"
    print("Loading base universal matrix...")
    df_base = pd.read_parquet(base_path)
    
    for ticker, dates in birth_db.items():
        try:
            build_dual_matrix(ticker, dates, df_base)
        except Exception as e:
            print(f"Error on {ticker}: {e}")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
