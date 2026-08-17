import pandas as pd
import yfinance as yf
import numpy as np
import time
from datetime import timedelta
import math
from vedic_astrology_engine import UltimateVedicEngine

def calc_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(period).mean()
    # Return ATR as a percentage of the close price
    return atr / df['Close']

def generate_dataset():
    print("Fetching SPY data...")
    df = yf.download("SPY", start="2000-01-01", end="2026-01-01", progress=False, auto_adjust=False)
    # yf download for a single ticker returns MultiIndex columns in recent versions, flatten it:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df.index = df.index.tz_localize(None)
    
    print("Calculating ATR...")
    df['ATR_pct'] = calc_atr(df)
    
    print("Applying Triple Barrier Labeling...")
    # Parameters
    pt_mult = 1.5  # Profit Take multiplier
    sl_mult = 1.0  # Stop Loss multiplier
    t_barrier = 10 # Days
    
    labels = []
    
    for i in range(len(df)):
        if i + t_barrier >= len(df) or pd.isna(df['ATR_pct'].iloc[i]):
            labels.append(np.nan)
            continue
            
        current_price = df['Close'].iloc[i]
        current_atr = df['ATR_pct'].iloc[i]
        
        upper_bound = current_price * (1 + (pt_mult * current_atr))
        lower_bound = current_price * (1 - (sl_mult * current_atr))
        
        # Look forward
        hit = 0 # 0 = expired sideways
        for j in range(1, t_barrier + 1):
            future_high = df['High'].iloc[i + j]
            future_low = df['Low'].iloc[i + j]
            
            # Check Stop Loss first (conservative)
            if future_low <= lower_bound:
                hit = -1
                break
            # Check Profit Take
            elif future_high >= upper_bound:
                hit = 1
                break
                
        labels.append(hit)
        
    df['Target_Label'] = labels
    df = df.dropna(subset=['Target_Label'])
    
    print(f"Generated {len(df)} labeled trading days.")
    
    # Initialize Astrological Engine
    engine = UltimateVedicEngine()
    print("Calculating SPY Natal Chart...")
    birth_jd, _ = engine.get_jd("1993-01-29 09:30:00")
    natal_planets = engine.calculate_d1(birth_jd)
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    features = []
    
    print("Calculating Daily Transits (Cyclical & Vedha)...")
    start_t = time.time()
    
    for date in df.index:
        date_str = date.strftime("%Y-%m-%d 09:30:00")
        jd, dt_utc = engine.get_jd(date_str)
        transit_planets = engine.calculate_d1(jd)
        
        # 1. Vedhas
        from vedha_engine import get_vedha_pairs
        vedhas = get_vedha_pairs(natal_planets, transit_planets)
        
        row_feat = {"Date": date}
        
        # Count Vedhas
        vedha_counts = {f"Transit_Vedha_Blocked_{p}": 0 for p in planets}
        for v in vedhas:
            blocked = v.get("planet_b")
            if blocked in vedha_counts:
                vedha_counts[f"Transit_Vedha_Blocked_{blocked}"] += 1
        row_feat.update(vedha_counts)
        
        # 2. D1 Cyclical Degrees and Deltas
        for p in planets:
            if p not in transit_planets or p not in natal_planets: continue
            
            t_lon = transit_planets[p]["longitude"]
            n_lon = natal_planets[p]["longitude"]
            
            row_feat[f"{p}_Transit_Sin"] = math.sin(math.radians(t_lon))
            row_feat[f"{p}_Transit_Cos"] = math.cos(math.radians(t_lon))
            
            delta = (t_lon - n_lon) % 360
            row_feat[f"{p}_Delta_Sin"] = math.sin(math.radians(delta))
            row_feat[f"{p}_Delta_Cos"] = math.cos(math.radians(delta))
            
        # 3. Transit D9 and D10
        divs = engine.calculate_divisional(transit_planets)
        for p, sign in divs["D9_navamsa"].items():
            row_feat[f"Transit_D9_{p}"] = sign
        for p, sign in divs["D10_dasamsa"].items():
            row_feat[f"Transit_D10_{p}"] = sign
            
        # 4. Transit SAV
        ashtak = engine.calculate_bav_sav(transit_planets)
        for sign, pts in ashtak["sarvashtakvarga"].items():
            row_feat[f"Transit_SAV_{sign}"] = pts
            
        # 5. Transit Shadbala
        from shadbala_core import calc_shadbala
        asc_lon = transit_planets.get("Ascendant", {}).get("longitude", 0)
        sun_lon = transit_planets.get("Sun", {}).get("longitude", 0)
        moon_lon = transit_planets.get("Moon", {}).get("longitude", 0)
        mc_lon = transit_planets.get("MC", {}).get("longitude", 0)
        t_shadbala = calc_shadbala(transit_planets, asc_lon, sun_lon, moon_lon, jd, mc_lon)
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if p in t_shadbala:
                row_feat[f"Transit_Shadbala_{p}"] = t_shadbala[p]["total_rupas"]
                
        # 6. Transit Panchang
        from compute_full_features import calc_panchang
        panchang = calc_panchang(jd, dt_utc)
        row_feat["Transit_Tithi"] = panchang.get("tithi", "").split("(")[0].strip()
        row_feat["Transit_Karana"] = panchang.get("karana", "")
        row_feat["Transit_Yoga"] = panchang.get("yoga", "")
        
        features.append(row_feat)
        
        if len(features) % 500 == 0:
            print(f"Processed {len(features)} dates...")
            
    print(f"Astrology engine took {time.time() - start_t:.2f} seconds.")
    
    feat_df = pd.DataFrame(features)
    feat_df.set_index("Date", inplace=True)
    
    # Merge with target labels
    final_df = df[['Target_Label', 'Close', 'ATR_pct']].join(feat_df, how='inner')
    
    # Categorical columns to encode
    cat_cols = [c for c in final_df.columns if final_df[c].dtype == 'object']
    final_df = pd.get_dummies(final_df, columns=cat_cols, drop_first=False)
    
    # Save to CSV
    final_df.to_csv("advanced_ml_dataset.csv")
    print(f"Saved advanced_ml_dataset.csv with shape {final_df.shape}")
    print(final_df['Target_Label'].value_counts())

if __name__ == "__main__":
    generate_dataset()
