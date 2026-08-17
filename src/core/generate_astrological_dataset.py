import pandas as pd
import yfinance as yf
import numpy as np
import time
import math
from datetime import datetime
from vedic_astrology_engine import UltimateVedicEngine
from compute_full_features import calc_dasha, get_3level_dasha
from shadbala_core import calc_shadbala

def calc_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(period).mean()
    return atr / df['Close']

def generate_architected_dataset():
    print("Fetching SPY data...")
    df = yf.download("SPY", start="2000-01-01", end="2026-01-01", progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = df.index.tz_localize(None)
    
    df['ATR_pct'] = calc_atr(df)
    
    # Triple Barrier
    pt_mult, sl_mult, t_barrier = 1.5, 1.0, 10
    labels = []
    for i in range(len(df)):
        if i + t_barrier >= len(df) or pd.isna(df['ATR_pct'].iloc[i]):
            labels.append(np.nan)
            continue
        current_price = df['Close'].iloc[i]
        current_atr = df['ATR_pct'].iloc[i]
        upper_bound = current_price * (1 + (pt_mult * current_atr))
        lower_bound = current_price * (1 - (sl_mult * current_atr))
        hit = 0
        for j in range(1, t_barrier + 1):
            future_high, future_low = df['High'].iloc[i + j], df['Low'].iloc[i + j]
            if future_low <= lower_bound:
                hit = -1
                break
            elif future_high >= upper_bound:
                hit = 1
                break
        labels.append(hit)
    df['Target_Label'] = labels
    df = df.dropna(subset=['Target_Label'])
    
    print("Initialize Engine & Calculate NATAL Baseline...")
    engine = UltimateVedicEngine()
    birth_dt = datetime(1993, 1, 29, 9, 30, 0)
    birth_jd, _ = engine.get_jd(birth_dt.strftime("%Y-%m-%d %H:%M:%S"))
    natal_planets = engine.calculate_d1(birth_jd)
    natal_divs = engine.calculate_divisional(natal_planets)
    
    asc_lon = natal_planets.get("Ascendant", {}).get("longitude", 0)
    sun_lon = natal_planets.get("Sun", {}).get("longitude", 0)
    moon_lon = natal_planets.get("Moon", {}).get("longitude", 0)
    mc_lon = natal_planets.get("MC", {}).get("longitude", 0)
    natal_shadbala = calc_shadbala(natal_planets, asc_lon, sun_lon, moon_lon, birth_jd, mc_lon)
    
    # Calculate Dasha Sequence once
    dasha_sequence = calc_dasha(moon_lon, birth_dt)
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    features = []
    print("Generating Astrological Combinations (NATAL x TRANSIT x DASHA)...")
    start_t = time.time()
    
    from vedha_engine import get_vedha_pairs
    
    for date in df.index:
        date_str = date.strftime("%Y-%m-%d 09:30:00")
        jd, _ = engine.get_jd(date_str)
        transit_planets = engine.calculate_d1(jd)
        transit_divs = engine.calculate_divisional(transit_planets)
        
        row_feat = {"Date": date}
        
        # ==========================================
        # CATEGORY 2: TRANSIT (General Macro Sky)
        # ==========================================
        for p in planets:
            if p not in transit_planets: continue
            row_feat[f"TRANSIT_D1_Sign_{p}"] = transit_planets[p]["sign"]
            row_feat[f"TRANSIT_D9_Sign_{p}"] = transit_divs["D9_navamsa"].get(p, "")
            
        # ==========================================
        # CATEGORY 3: DASHA (Pre-Decided Triggers)
        # ==========================================
        current_dasha = get_3level_dasha(dasha_sequence, date)
        md_lord = current_dasha["mahadasha"]["lord"] if current_dasha else "Unknown"
        ad_lord = current_dasha["antardasha"]["lord"] if current_dasha else "Unknown"
        pad_lord = current_dasha["pratyantardasha"]["lord"] if current_dasha else "Unknown"
        
        row_feat["DASHA_MD"] = md_lord
        row_feat["DASHA_AD"] = ad_lord
        row_feat["DASHA_PAD"] = pad_lord
        
        # ==========================================
        # CROSS A: DASHA x NATAL
        # ==========================================
        # How strong is the current Dasha Lord in the NATAL chart?
        if md_lord in natal_shadbala:
            row_feat["DASHA_x_NATAL_MD_Strength"] = natal_shadbala[md_lord]["total_rupas"]
        if ad_lord in natal_shadbala:
            row_feat["DASHA_x_NATAL_AD_Strength"] = natal_shadbala[ad_lord]["total_rupas"]
            
        if md_lord in natal_planets:
            row_feat["DASHA_x_NATAL_MD_Sign"] = natal_planets[md_lord]["sign"]
        
        # ==========================================
        # CROSS B: TRANSIT x NATAL (Triggers)
        # ==========================================
        # Vedhas are inherently Transit x Natal
        vedhas = get_vedha_pairs(natal_planets, transit_planets)
        vedha_counts = {f"TRANSIT_x_NATAL_Vedha_Blocked_{p}": 0 for p in planets}
        for v in vedhas:
            blocked = v.get("planet_b")
            if blocked in vedha_counts:
                vedha_counts[f"TRANSIT_x_NATAL_Vedha_Blocked_{blocked}"] += 1
        row_feat.update(vedha_counts)
        
        # Classical Overlaps (Transit Planet exactly over Natal Planet Sign)
        for tp in planets:
            if tp not in transit_planets: continue
            t_sign = transit_planets[tp]["sign"]
            
            # Is Transit Planet in same sign as Natal Moon? (Sade Sati / Kantaka Sani concept)
            n_moon_sign = natal_planets["Moon"]["sign"]
            row_feat[f"TRANSIT_x_NATAL_{tp}_Over_Moon"] = 1 if t_sign == n_moon_sign else 0
            
            # Angular Deltas
            t_lon = transit_planets[tp]["longitude"]
            n_lon = natal_planets[tp]["longitude"]
            delta = (t_lon - n_lon) % 360
            row_feat[f"TRANSIT_x_NATAL_{tp}_Delta_Sin"] = math.sin(math.radians(delta))
            row_feat[f"TRANSIT_x_NATAL_{tp}_Delta_Cos"] = math.cos(math.radians(delta))
            
        # ==========================================
        # CROSS C: DASHA x TRANSIT
        # ==========================================
        # What is the Transit Sign of the CURRENT Dasha Lord today?
        if md_lord in transit_planets:
            row_feat["DASHA_x_TRANSIT_MD_Sign"] = transit_planets[md_lord]["sign"]
            row_feat["DASHA_x_TRANSIT_MD_D9_Sign"] = transit_divs["D9_navamsa"].get(md_lord, "")
        
        features.append(row_feat)
        
        if len(features) % 500 == 0:
            print(f"Processed {len(features)} dates...")
            
    print(f"Astrology engine took {time.time() - start_t:.2f} seconds.")
    
    feat_df = pd.DataFrame(features)
    feat_df.set_index("Date", inplace=True)
    
    final_df = df[['Target_Label', 'Close', 'ATR_pct']].join(feat_df, how='inner')
    
    cat_cols = [c for c in final_df.columns if final_df[c].dtype == 'object']
    final_df = pd.get_dummies(final_df, columns=cat_cols, drop_first=False)
    
    final_df.to_csv("architected_ml_dataset.csv")
    print(f"Saved architected_ml_dataset.csv with shape {final_df.shape}")

if __name__ == "__main__":
    generate_architected_dataset()
