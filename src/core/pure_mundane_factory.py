import os
import sys
import pandas as pd
import numpy as np
import time
from datetime import datetime

sys.path.append(r"C:\Users\patel\Desktop\Python\Learn")

from planetary_dignity import extract_dignity_features
from parashari_aspects import extract_aspect_features
from shadbala_engine import extract_shadbala_features
from build_stock_matrix import compute_panchang_features, KEY_TO_FULL

print("="*70)
print(" GENESIS PHASE 9: PURE MUNDANE FACTORY (NON-BIRTHDAY)")
print("="*70)

# Paths
BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
ASTRO_PATH = os.path.join(BASE_DIR, "AstroData_2004_2027.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")

# 1. Load Data
print("\n[1/3] Loading Master Ephemeris...")
astro = pd.read_csv(ASTRO_PATH)
astro["Date"] = pd.to_datetime(astro["Time"].astype(str), format="%Y%m%d")
astro = astro.set_index("Date").sort_index()
astro = astro[astro.index.dayofweek < 5] # Weekdays only
dates = astro.index.tolist()
print(f" Loaded {len(dates)} continuous trading days.")

def build_pure_mundane(transit_df, dates):
    all_rows = []
    default_speeds = {"Sun": 1.0, "Moon": 13.0, "Mars": 0.5, "Mercury": 1.3,
                      "Jupiter": 0.08, "Venus": 1.1, "Saturn": 0.03}
    
    for dt in dates:
        if dt not in transit_df.index:
            continue
            
        row = transit_df.loc[dt]
        feats = {"Date": dt, "Ticker": "MUNDANE"}
        
        # 1. Transit planet longitudes
        transit_longs = {}
        for k, full_name in KEY_TO_FULL.items():
            if k in row.index:
                transit_longs[full_name] = float(row[k])
        transit_longs["Ketu"] = (transit_longs.get("Rahu", 0) + 180) % 360
        
        # 2. Panchang features
        sun_lon = transit_longs.get("Sun", 0)
        moon_lon = transit_longs.get("Moon", 0)
        panchang = compute_panchang_features(sun_lon, moon_lon, dt.weekday())
        feats.update(panchang)
        
        # 3. Transit Dignity
        transit_dignity = extract_dignity_features(transit_longs)
        for k, v in transit_dignity.items():
            if isinstance(v, (int, float)):
                feats[f"T_{k}"] = v
                
        # 4. Transit Aspects
        transit_aspects = extract_aspect_features(transit_longs)
        for k, v in transit_aspects.items():
            if isinstance(v, (int, float)):
                feats[f"T_{k}"] = v
                
        # 5. Transit Shadbala
        transit_shadbala = extract_shadbala_features(transit_longs, default_speeds, 0.0)
        for k, v in transit_shadbala.items():
            if isinstance(v, (int, float)):
                feats[f"T_{k}"] = v
                
        # 6. Pushkar Navamsha/Bhaga (transit-based)
        try:
            from pushkar_detector import PUSHKAR_RANGES, PUSHKAR_BHAGA_DEG, SIGN_ELEMENTS
            pushkar_count = 0
            pushkar_bhaga_count = 0
            SIGNS_LIST = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
            for p_name, t_lon in transit_longs.items():
                deg_in_sign = t_lon % 30.0
                sign_idx = int(t_lon / 30.0) % 12
                sign_name = SIGNS_LIST[sign_idx]
                element = SIGN_ELEMENTS.get(sign_name, "")
                if element in PUSHKAR_RANGES:
                    for r_start, r_end in PUSHKAR_RANGES[element]:
                        if r_start <= deg_in_sign < r_end:
                            pushkar_count += 1
                            feats[f"Pushkar_Nav_{p_name[:3]}"] = 1
                            break
                if sign_name in PUSHKAR_BHAGA_DEG:
                    pb_deg = PUSHKAR_BHAGA_DEG[sign_name]
                    if isinstance(pb_deg, (int, float)):
                        if abs(deg_in_sign - pb_deg) < 1.0:
                            pushkar_bhaga_count += 1
                            feats[f"Pushkar_Bhaga_{p_name[:3]}"] = 1
                    elif isinstance(pb_deg, (list, tuple)):
                        for d in pb_deg:
                            if abs(deg_in_sign - d) < 1.0:
                                pushkar_bhaga_count += 1
                                feats[f"Pushkar_Bhaga_{p_name[:3]}"] = 1
                                break
            feats["Pushkar_Nav_Count"] = pushkar_count
            feats["Pushkar_Bhaga_Count"] = pushkar_bhaga_count
        except Exception:
            pass
            
        all_rows.append(feats)
        
    return pd.DataFrame(all_rows)

def expand_features(df):
    new_features = {}
    base_cols = [c for c in df.columns if c not in ['Date', 'Ticker']]
    
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    for c in base_cols:
        series = df[c]
        new_features[f"{c}_lag1"] = series.shift(1)
        new_features[f"{c}_lag3"] = series.shift(3)
        new_features[f"{c}_lag5"] = series.shift(5)
        new_features[f"{c}_lag10"] = series.shift(10)
        new_features[f"{c}_lag20"] = series.shift(20)
        
        new_features[f"{c}_diff3"] = series.diff(3)
        new_features[f"{c}_diff10"] = series.diff(10)
        
    expanded_df = pd.DataFrame(new_features, index=df.index)
    df = pd.concat([df, expanded_df], axis=1)
    df.fillna(0, inplace=True)
    df = df[df['Date'] >= pd.to_datetime('2005-01-01')]
    return df

print("\n[2/3] Building Pure Mundane Base Matrix...")
t0 = time.time()
base_df = build_pure_mundane(astro, dates)
print(f"  Generated {len(base_df.columns)} base features in {time.time()-t0:.1f}s")

print("\n[3/3] Expanding Lags & Velocities...")
t1 = time.time()
final_df = expand_features(base_df)
float_cols = final_df.select_dtypes(include=['float64']).columns
final_df[float_cols] = final_df[float_cols].astype('float32')

final_df.to_parquet(OUTPUT_FILE)
print(f"  SUCCESS! Saved {len(final_df.columns)} features to genesis_9000_MUNDANE.parquet")
print(f"  Total Expansion Time: {time.time()-t1:.1f}s")
