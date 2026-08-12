"""
Feature Matrix Generator (Phase 0.7) - Batch Optimized
======================================================
Generates the master feature matrix containing the universal sky state, 
per-stock natal/dasha states, and the evaluated boolean logic for 611 rules.

Optimized to process one Ticker at a time to prevent OOM errors, 
reading the specific trading dates from the market_data/ parquet files,
and writing out to partitioned pyarrow datasets.
"""
import sqlite3
import json
import time
import os
from datetime import datetime, timezone
import pytz
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from ephemeris_engine import compute_all_features
from transit_engine import StockAstroEngine

import sys
sys.path.append(r"E:\Python\Learn")
from institution_backtest_analysis import (extract_all_features, compute_natal_blueprint,
                                           extract_natal_transit_crossref, extract_vedha_topic23)
import swisseph as swe

MARKET_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"
OUTPUT_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
COMPILED_RULES_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\compiled_rules.json"

def load_compiled_rules():
    with open(COMPILED_RULES_PATH, "r") as f:
        rules_dict = json.load(f)
        
    funcs = {}
    for name, expr in rules_dict.items():
        try:
            code = compile(expr, "<string>", "eval")
            funcs[name] = code
        except Exception as e:
            print(f"Error compiling {name}: {e}")
    return funcs

def process_ticker(ticker, engine, rule_funcs, sky_cache):
    """Processes a single ticker by iterating through its exact trading history."""
    # Load market data to get exact trading dates
    md_path = os.path.join(MARKET_DATA_DIR, f"{ticker}_ohlcv.parquet")
    if not os.path.exists(md_path):
        print(f"  [{ticker}] No market data found. Skipping.")
        return None
        
    md_df = pd.read_parquet(md_path)
    
    # Optional: Filter to last 20 years to save time during this build
    # For institutional backtest, we will use all available dates.
    dates = md_df['Date'].tolist()
    
    all_rows = []
    
    # Pre-compute Natal Blueprint + Load Pre-computed Tables
    try:
        n_lons = {}
        if "planets" in engine.natal_cache[ticker]["natal"]:
            for p, data in engine.natal_cache[ticker]["natal"]["planets"].items():
                n_lons[p] = data.get("longitude", 0.0)
        
        # We need _asc and _moon_nak_i, and _jd for Panchang
        ipo_str = engine.natal_cache[ticker]["ipo_date"]
        dt_ipo = datetime.strptime(ipo_str, "%Y-%m-%d")
        dt_ipo_et = pytz.timezone("US/Eastern").localize(dt_ipo.replace(hour=9, minute=30))
        dt_ipo_utc = dt_ipo_et.astimezone(timezone.utc)
        n_lons['_jd'] = swe.julday(dt_ipo_utc.year, dt_ipo_utc.month, dt_ipo_utc.day, dt_ipo_utc.hour + dt_ipo_utc.minute/60.0)
        sector = "Unknown"
        c = engine.conn.cursor()
        c.execute("SELECT ascendant_degree, lagna_sign, moon_nakshatra FROM stocks WHERE ticker=?", (ticker,))
        res = c.fetchone()
        n_lons['_asc'] = res[0] if res else 0.0
        n_lons['_moon_nak_i'] = engine.natal_cache[ticker]["moon_nak"]
        
        # Inject BAV/SAV for Vedha system (Fix #2 + #3)
        try:
            sav_row = c.execute("SELECT sign_0,sign_1,sign_2,sign_3,sign_4,sign_5,sign_6,sign_7,sign_8,sign_9,sign_10,sign_11 FROM natal_sav WHERE ticker=?", (ticker,)).fetchone()
            if sav_row:
                n_lons['_sav'] = list(sav_row)
                bav_dict = {}
                for bav_row in c.execute("SELECT planet,sign_0,sign_1,sign_2,sign_3,sign_4,sign_5,sign_6,sign_7,sign_8,sign_9,sign_10,sign_11 FROM natal_bav WHERE ticker=?", (ticker,)).fetchall():
                    bav_dict[bav_row[0]] = list(bav_row[1:])
                n_lons['_bav'] = bav_dict
                n_lons['_moon_sign_idx'] = int(n_lons.get('Moon', 0) / 30)
                asc_sign = res[1] if res and res[1] is not None else int(n_lons['_asc'] / 30)
                n_lons['_asc_sign_idx'] = asc_sign
        except Exception:
            pass  # Vedha will produce empty features if BAV/SAV not available
        
        # Load pre-computed Shadbala, Karakas, Ghatak (per-stock constants)
        shadbala_feats = {}
        try:
            for sb_row in c.execute("SELECT planet, sthana_bala, dig_bala, chesta_bala, total_shadbala FROM natal_shadbala WHERE ticker=?", (ticker,)).fetchall():
                p = sb_row[0]
                shadbala_feats[f'SB_{p}_sthana'] = sb_row[1]
                shadbala_feats[f'SB_{p}_dig'] = sb_row[2]
                shadbala_feats[f'SB_{p}_chesta'] = sb_row[3]
                shadbala_feats[f'SB_{p}_total'] = sb_row[4]
        except Exception:
            pass
        
        karaka_feats = {}
        try:
            for kk_row in c.execute("SELECT karaka, planet FROM natal_karakas WHERE ticker=?", (ticker,)).fetchall():
                karaka_feats[f'natal_karaka_{kk_row[0]}'] = kk_row[1]
        except Exception:
            pass
        
        ghatak_feats = {}
        try:
            gh_row = c.execute("SELECT bad_day, bad_nakshatra, bad_rashi, bad_tithi_json, bad_lagna FROM natal_ghatak WHERE ticker=?", (ticker,)).fetchone()
            if gh_row:
                ghatak_feats['_ghatak_bad_day'] = gh_row[0]
                ghatak_feats['_ghatak_bad_nak'] = gh_row[1]
                ghatak_feats['_ghatak_bad_rashi'] = gh_row[2]
                ghatak_feats['_ghatak_bad_tithi'] = json.loads(gh_row[3]) if gh_row[3] else []
                ghatak_feats['_ghatak_bad_lagna'] = gh_row[4]
        except Exception:
            pass
        
        c.execute("SELECT sector FROM sector_tags WHERE ticker=?", (ticker,))
        res2 = c.fetchone()
        sector = res2[0] if res2 else "Unknown"
        
        bp = compute_natal_blueprint(n_lons)
    except Exception as e:
        print(f"  [{ticker}] Error computing natal blueprint: {e}")
        return None
        
    for dt in dates:
        # 1. Sky State (Universal) - Use cache to avoid recomputing the same day across tickers
        # Convert pandas timestamp (midnight local) to US/Eastern 9:30 AM, then to UTC
        local_dt = pytz.timezone("US/Eastern").localize(datetime(dt.year, dt.month, dt.day, 9, 30))
        dt_utc = local_dt.astimezone(timezone.utc)
        date_str = dt_utc.strftime("%Y-%m-%d %H:%M") # use H:M for cache key to prevent collision if time changes

        
        if date_str not in sky_cache:
            sky_cache[date_str] = compute_all_features(dt_utc)
            
        sky = sky_cache[date_str]
        
        # 2. Stock Features (Transit/Dasha)
        stock_features = engine.compute_stock_features(dt_utc, ticker, sky)
        
        # 3. ML Features (The 740+ Rules)
        try:
            feats, tlons = extract_all_features(n_lons, ipo_str, dt_utc, sector)
            cx = extract_natal_transit_crossref(bp, feats, tlons)
            ml_features = {**feats, **bp, **cx}
            # Remove non-numeric raw keys
            ml_features.pop('_panchang_raw', None)
        except Exception as e:
            ml_features = {}
        
        # 3b. Vedha + Ashtakavarga features (Fix #3)
        try:
            vedha_feats = extract_vedha_topic23(n_lons, date_str)
            if vedha_feats:
                ml_features.update(vedha_feats)
        except Exception:
            pass
        
        # 3c. Shadbala per-stock constants (Fix #4)
        ml_features.update(shadbala_feats)
        
        # 3d. Ghatak danger-day check (Fix #6)
        if ghatak_feats:
            # Check if today is a Ghatak bad day for this stock
            day_of_week = dt_utc.weekday()  # 0=Mon ... 6=Sun
            # Convert to Vedic weekday: 0=Sun, 1=Mon ... 6=Sat
            vedic_day = (day_of_week + 1) % 7
            ml_features['ghatak_bad_day'] = 1 if vedic_day == ghatak_feats.get('_ghatak_bad_day', -1) else 0
            # Check if transit Moon nakshatra matches Ghatak bad nakshatra
            transit_moon_nak = sky.get('Moon_nakshatra', -1)
            if isinstance(transit_moon_nak, (int, float)):
                ml_features['ghatak_bad_nak'] = 1 if int(transit_moon_nak) == ghatak_feats.get('_ghatak_bad_nak', -1) else 0
            # Check if transit Moon sign matches Ghatak bad rashi
            transit_moon_sign = sky.get('Moon_sign', -1)
            if isinstance(transit_moon_sign, (int, float)):
                ml_features['ghatak_bad_rashi'] = 1 if int(transit_moon_sign) == ghatak_feats.get('_ghatak_bad_rashi', -1) else 0
            # Composite Ghatak score (0-3)
            ml_features['ghatak_score'] = ml_features.get('ghatak_bad_day', 0) + ml_features.get('ghatak_bad_nak', 0) + ml_features.get('ghatak_bad_rashi', 0)
            
        combined = {**sky, **stock_features, **ml_features}
        
        # 4. Rules Evaluation
        rule_evals = {}
        local_vars = {"features": combined}
        for rule_name, code_obj in rule_funcs.items():
            try:
                rule_evals[f"rule_{rule_name}"] = 1.0 if eval(code_obj, {"__builtins__": None}, local_vars) else 0.0
            except Exception:
                rule_evals[f"rule_{rule_name}"] = 0.0
                
        # Combine
        row = {"date": dt_utc, "ticker": ticker, **combined, **rule_evals}
        all_rows.append(row)
        
    df = pd.DataFrame(all_rows)
    
    df = pd.DataFrame(all_rows)
    
    # 5. Stationarity Prep: sine/cosine of longitudes
    lon_cols = [c for c in df.columns if "longitude" in c]
    for col in lon_cols:
        rad = np.radians(df[col])
        df[f"{col}_sin"] = np.sin(rad)
        df[f"{col}_cos"] = np.cos(rad)
        
    df['year'] = df['date'].dt.year
    
    # 6. Write to partitioned dataset immediately to free memory
    table = pa.Table.from_pandas(df)
    pq.write_to_dataset(table, root_path=OUTPUT_DIR, partition_cols=['ticker', 'year'])
    
    # Merge returns into a separate table or save as part of the pipeline later.
    return len(df)

import concurrent.futures

def generate_matrix():
    print("Initializing Generator Engine...")
    engine = StockAstroEngine()
    rule_funcs = load_compiled_rules()
    
    target_tickers = ['AAPL'] # Only generate AAPL for the audit testing
    print(f"Targeting {len(target_tickers)} pristine tickers.")
    
    sky_cache = {}
    
    t_start = time.perf_counter()
    total_rows = 0
    
    # Optional: exclude the new ETFs if we don't want to re-run them
    # NEW_TICKERS = ['SPY','QQQ','IWM','DIA','GLD','SLV','USO','TLT','XLE','VIXY']
    # target_tickers = [t for t in target_tickers if t not in NEW_TICKERS]
    
    print(f"Processing {len(target_tickers)} tickers synchronously...")
    for i, tk in enumerate(target_tickers):
        try:
            rows_processed = process_ticker(tk, engine, rule_funcs, sky_cache)
            if rows_processed:
                total_rows += rows_processed
            print(f"[{i+1}/{len(target_tickers)}] {tk} completed -> {rows_processed or 0} rows")
        except Exception as exc:
            print(f"[{i+1}/{len(target_tickers)}] {tk} generated an exception: {exc}")
                
    elapsed = time.perf_counter() - t_start
    print("="*50)
    print("MATRIX GENERATION COMPLETE")
    print("="*50)
    print(f"Total Rows Generated: {total_rows}")
    print(f"Total Time: {elapsed/60:.2f} mins")
    print(f"Dataset Path: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_matrix()
