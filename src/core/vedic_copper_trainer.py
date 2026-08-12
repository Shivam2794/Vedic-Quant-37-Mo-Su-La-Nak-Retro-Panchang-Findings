import os
import sys
import warnings
import time
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
PRIMARY_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_primary.json")
META_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_meta.json")

BARRIER_BARS = 6

def fetch_pair_data():
    print("[1] Fetching 2 YEARS (1h) data for COPX/SPY spread...")
    df_asset = yf.download("COPX", period="730d", interval="1h", progress=False)
    df_bench = yf.download("SPY", period="730d", interval="1h", progress=False)
    
    if df_asset.empty or df_bench.empty: raise ValueError("No data returned")
    
    if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_bench.columns, pd.MultiIndex): df_bench.columns = df_bench.columns.get_level_values(0)
        
    df_asset = df_asset[['Close', 'Volume']].dropna()
    df_bench = df_bench[['Close']].dropna()
    
    df, bench = df_asset.align(df_bench, join='inner', axis=0)
    
    syn = pd.DataFrame()
    syn['Close'] = df['Close'] / bench['Close']
    syn['Volume'] = df['Volume']
    syn['dt'] = syn.index
    
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn = syn[mask].reset_index(drop=True)
    return syn

def apply_labels(df):
    closes = df['Close'].values
    n = len(closes)
    labels = np.zeros(n, dtype=np.int8)
    for i in range(n - BARRIER_BARS):
        if closes[i + BARRIER_BARS] > closes[i]: labels[i] = 1
        else: labels[i] = 0
    df['label'] = labels
    return df

def train_and_save():
    print("[2] Loading Mundane Matrix...")
    df_astro = pd.read_parquet(MATRIX_FILE)
    df_astro['Date'] = pd.to_datetime(df_astro['Date']).dt.tz_localize(None).astype('datetime64[us]')
    if 'Close' in df_astro.columns: df_astro.drop(columns=['Close'], inplace=True)
    if 'Volume' in df_astro.columns: df_astro.drop(columns=['Volume'], inplace=True)
    max_astro_date = df_astro['Date'].max()
    
    df_price = fetch_pair_data()
    df_price['Date'] = pd.to_datetime(df_price['dt']).dt.tz_localize(None).astype('datetime64[us]')
    df_price = df_price[df_price['Date'] <= max_astro_date]
    df_price.sort_values('Date', inplace=True)
    
    print("[3] Fusing Data...")
    df_fused = pd.merge_asof(df_price, df_astro, on='Date', direction='backward')
    df_fused = df_fused.dropna(subset=['Tithi_Num'])
    
    df2 = apply_labels(df_fused).iloc[:-BARRIER_BARS].reset_index(drop=True)
    n = len(df2)
    
    exclude_cols = ['Close', 'Volume', 'dt', 'label', 'Date', 'index', 'Year', 'Quarter']
    primary_cols = [c for c in df2.columns if c not in exclude_cols and df2[c].dtype in [np.float32, np.float64, np.int64, np.int32, int, float]]
    
    X = df2[primary_cols].fillna(0).values.astype(np.float32)
    y = df2['label'].values
    meta_raw = df2['Volume'].values.reshape(-1, 1) 
    
    print(f"[4] Training Primary Model on {n} full samples...")
    xgb_params = dict(n_estimators=30, max_depth=3, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.5, reg_lambda=1.5)
    
    prim = xgb.XGBClassifier(**xgb_params)
    prim.fit(X, y, verbose=False)
    prim.save_model(PRIMARY_MODEL_FILE)
    print(f"    Saved -> {PRIMARY_MODEL_FILE}")
    
    print("[5] Generating Out-Of-Sample Predictions for Meta-Model...")
    # To train the meta-model, we need out-of-sample predictions for the entire dataset
    tscv = TimeSeriesSplit(n_splits=5)
    y_pred_oos = np.zeros(n)
    valid_mask = np.zeros(n, dtype=bool)
    
    for tr_in, val_in in tscv.split(X):
        if len(tr_in) <= BARRIER_BARS: continue
        clean_tr_in = tr_in[:-BARRIER_BARS]
        m = xgb.XGBClassifier(**xgb_params)
        if len(np.unique(y[clean_tr_in])) > 1:
            m.fit(X[clean_tr_in], y[clean_tr_in], verbose=False)
            y_pred_oos[val_in] = m.predict(X[val_in])
            valid_mask[val_in] = True
            
    print("[6] Training Meta-Model...")
    meta_targ = (y_pred_oos[valid_mask] == y[valid_mask]).astype(int)
    meta_feat = np.column_stack([y_pred_oos[valid_mask], meta_raw[valid_mask]])
    
    meta_m = xgb.XGBClassifier(n_estimators=20, max_depth=2, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.5, reg_lambda=1.5)
    meta_m.fit(meta_feat, meta_targ, verbose=False)
    meta_m.save_model(META_MODEL_FILE)
    print(f"    Saved -> {META_MODEL_FILE}")
    print("[7] Success! Models are ready for live deployment.")
    
    # Save feature names for the bot to ensure ordering
    with open(os.path.join(BASE_DIR, "copper_feature_names.txt"), "w") as f:
        for col in primary_cols:
            f.write(col + "\n")

if __name__ == "__main__":
    train_and_save()
