import os
import sys
import warnings
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import xgboost as xgb

warnings.filterwarnings("ignore")

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
PRIMARY_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_primary.json")
META_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_meta.json")
FEATURE_NAMES_FILE = os.path.join(BASE_DIR, "copper_feature_names.txt")

MAX_UP_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_max_up.json")
MAX_DOWN_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_max_down.json")

def fetch_latest_data():
    df_asset = yf.download("COPX", period="5d", interval="1h", progress=False, auto_adjust=False)
    df_bench = yf.download("SPY", period="5d", interval="1h", progress=False, auto_adjust=False)
    
    if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_bench.columns, pd.MultiIndex): df_bench.columns = df_bench.columns.get_level_values(0)
        
    df_asset = df_asset[['Close', 'Volume']].dropna()
    df_bench = df_bench[['Close']].dropna()
    
    df, bench = df_asset.align(df_bench, join='inner', axis=0)
    
    syn = pd.DataFrame()
    syn['Close'] = df['Close'] / bench['Close']
    syn['Volume'] = df['Volume']
    syn['dt'] = syn.index
    
    return syn.iloc[-1:], df_asset.iloc[-1]['Close'], df_bench.iloc[-1]['Close']

def get_latest_astro_features(price_date):
    df_astro = pd.read_parquet(MATRIX_FILE)
    df_astro['Date'] = pd.to_datetime(df_astro['Date']).dt.tz_localize(None).astype('datetime64[us]')
    df_astro = df_astro[df_astro['Date'] <= price_date.tz_localize(None)]
    return df_astro.iloc[-1:]

def run_bot():
    print("="*60)
    print(" GENESIS LIVE EXECUTION DAEMON: COPX/SPY PAIRS TRADE")
    print("="*60)
    
    # 1. Fetch Models
    prim = xgb.XGBClassifier()
    prim.load_model(PRIMARY_MODEL_FILE)
    meta = xgb.XGBClassifier()
    meta.load_model(META_MODEL_FILE)
    
    reg_up = xgb.XGBRegressor()
    reg_up.load_model(MAX_UP_MODEL_FILE)
    reg_down = xgb.XGBRegressor()
    reg_down.load_model(MAX_DOWN_MODEL_FILE)
    
    with open(FEATURE_NAMES_FILE, "r") as f:
        primary_cols = [line.strip() for line in f.readlines()]
        
    # 2. Fetch Live Market Data
    print("\n[1] Fetching live market data...")
    live_df, current_copx_price, current_spy_price = fetch_latest_data()
    dt = live_df['dt'].iloc[0]
    volume = live_df['Volume'].iloc[0]
    print(f"    Timestamp: {dt}")
    print(f"    COPX Live Price: ${current_copx_price:.2f}")
    print(f"    SPY Live Price:  ${current_spy_price:.2f}")
    
    # 3. Fetch Planetary Coordinates
    print("[2] Synchronizing Mundane Astrological Ephemeris...")
    astro_row = get_latest_astro_features(dt)
    
    # 4. Feature Construction
    live_df['Date'] = pd.to_datetime(live_df['dt']).dt.tz_localize(None).astype('datetime64[us]')
    fused = pd.merge_asof(live_df, astro_row, on='Date', direction='backward')
    
    X = fused[primary_cols].fillna(0).values.astype(np.float32)
    meta_raw = np.array([[volume]])
    
    # 5. Prediction Engine
    print("[3] Genesis Engine evaluating...")
    pred = prim.predict(X)[0]
    meta_feat = np.column_stack([np.array([pred]), meta_raw])
    meta_prob = meta.predict_proba(meta_feat)[0, 1]
    
    max_up_pred = reg_up.predict(X)[0]
    max_down_pred = reg_down.predict(X)[0]
    
    direction = "LONG" if pred == 1 else "SHORT"
    
    # Dynamic Assignment
    if direction == "LONG":
        mfe_pred = max_up_pred
        mae_pred = max_down_pred
    else:
        mfe_pred = max_down_pred
        mae_pred = max_up_pred
        
    mae_pred = max(mae_pred, 0.002)
    
    dynamic_stop_loss = mae_pred * 1.5
    dynamic_limit_offset = mae_pred * 0.05
    
    # 6. Execution Logic
    print("\n" + "="*60)
    print(" EXCURSION FORECAST (PAIRS SPREAD)")
    print("="*60)
    print(f" Predicted Max Favorable Excursion (MFE): +{mfe_pred*100:.2f}%")
    print(f" Predicted Max Adverse Excursion (MAE):   -{mae_pred*100:.2f}%")
    print(f" Derived Astrological Stop-Loss:          {dynamic_stop_loss*100:.2f}%")
    
    print("\n" + "="*60)
    print(" EXECUTION DIRECTIVE")
    print("="*60)
    
    if meta_prob <= 0.52:
        print(f" [VETO] Meta-Model Confidence: {meta_prob*100:.1f}%")
        print(" [ACTION] DO NOT TRADE. Purged Gap detected. Maintain Cash.")
    else:
        print(f" [APPROVED] Primary Direction: {direction}")
        print(f" [CONFIDENCE] Meta-Model Score: {meta_prob*100:.1f}%")
        
        print("\n [DOLLAR-NEUTRAL PAIRS TRADE TICKET]")
        if direction == "LONG":
            print(f" 1. BUY  $10,000 of COPX at ${current_copx_price:.2f} (approx {int(10000/current_copx_price)} shares)")
            print(f" 2. SELL $10,000 of SPY  at ${current_spy_price:.2f} (approx {int(10000/current_spy_price)} shares)")
        else:
            print(f" 1. SELL $10,000 of COPX at ${current_copx_price:.2f} (approx {int(10000/current_copx_price)} shares)")
            print(f" 2. BUY  $10,000 of SPY  at ${current_spy_price:.2f} (approx {int(10000/current_spy_price)} shares)")
            
        print(f" 3. Limit Order Spread Tolerance: {dynamic_limit_offset*100:.3f}% (15 Min Cancel)")
        print(f" 4. Hard Stop-Loss: -${10000 * dynamic_stop_loss:.2f} Portfolio Drawdown")
        print(f" 5. Take-Profit Limit: +${10000 * mfe_pred:.2f} Portfolio Gain")
        print(f" 6. Time Exit: If targets not hit, close strictly after 6 Hours.")
        print("="*60)

if __name__ == "__main__":
    run_bot()
