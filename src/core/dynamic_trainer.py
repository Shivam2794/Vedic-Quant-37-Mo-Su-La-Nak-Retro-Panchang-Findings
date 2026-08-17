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
MAX_UP_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_max_up.json")
MAX_DOWN_MODEL_FILE = os.path.join(BASE_DIR, "genesis_copper_max_down.json")

BARRIER_BARS = 6

def fetch_pair_data():
    print("[1] Fetching 2 YEARS (1h) data for COPX/SPY spread...")
    df_asset = yf.download("COPX", period="730d", interval="1h", progress=False, auto_adjust=False)
    df_bench = yf.download("SPY", period="730d", interval="1h", progress=False, auto_adjust=False)
    
    if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_bench.columns, pd.MultiIndex): df_bench.columns = df_bench.columns.get_level_values(0)
        
    df_asset = df_asset[['Close', 'Volume']].dropna()
    df_bench = df_bench[['Close']].dropna()
    
    df, bench = df_asset.align(df_bench, join='inner', axis=0)
    
    syn = pd.DataFrame()
    syn['Close'] = df['Close'] / bench['Close']
    syn['dt'] = syn.index
    
    mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    syn = syn[mask].reset_index(drop=True)
    return syn

def apply_excursions(df):
    closes = df['Close'].values
    n = len(closes)
    max_ups = np.zeros(n, dtype=np.float32)
    max_downs = np.zeros(n, dtype=np.float32)
    
    for i in range(n - BARRIER_BARS):
        entry = closes[i]
        window = closes[i+1 : i+1+BARRIER_BARS]
        max_ups[i] = (np.max(window) / entry) - 1.0
        max_downs[i] = 1.0 - (np.min(window) / entry)
        
    df['max_up'] = max_ups
    df['max_down'] = max_downs
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
    
    print("[3] Fusing Data & Calculating Excursions...")
    df_fused = pd.merge_asof(df_price, df_astro, on='Date', direction='backward')
    df_fused = df_fused.dropna(subset=['Tithi_Num'])
    
    df2 = apply_excursions(df_fused).iloc[:-BARRIER_BARS].reset_index(drop=True)
    n = len(df2)
    
    exclude_cols = ['Close', 'Volume', 'dt', 'max_up', 'max_down', 'Date', 'index', 'Year', 'Quarter']
    primary_cols = [c for c in df2.columns if c not in exclude_cols and df2[c].dtype in [np.float32, np.float64, np.int64, np.int32, int, float]]
    
    X = df2[primary_cols].fillna(0).values.astype(np.float32)
    y_up = df2['max_up'].values
    y_down = df2['max_down'].values
    
    # Embargo KFold Implementation to stop Target Overlap
    class EmbargoKFold:
        def __init__(self, n_splits=5, embargo_bars=6):
            self.n_splits = n_splits
            self.embargo_bars = embargo_bars
            
        def split(self, X):
            n = len(X)
            fold_size = n // self.n_splits
            indices = np.arange(n)
            
            for i in range(self.n_splits):
                test_start = i * fold_size
                test_end = (i + 1) * fold_size if i < self.n_splits - 1 else n
                
                test_indices = indices[test_start:test_end]
                
                train_indices = []
                if test_start > self.embargo_bars:
                    train_indices.extend(indices[:test_start - self.embargo_bars])
                if test_end + self.embargo_bars < n:
                    train_indices.extend(indices[test_end + self.embargo_bars:])
                    
                yield np.array(train_indices), np.array(test_indices)
    
    # Regression Parameters
    xgb_params = dict(n_estimators=100, max_depth=3, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.0, reg_lambda=1.0)
    
    print(f"[4] Training Max_Up Excursion Regressor on {n} samples (Embargo KFold)...")
    kf = EmbargoKFold(n_splits=5, embargo_bars=BARRIER_BARS)
    
    best_up_model = None
    best_up_score = float('inf')
    
    for fold, (tr_idx, val_idx) in enumerate(kf.split(X)):
        X_tr, y_up_tr = X[tr_idx], y_up[tr_idx]
        X_val, y_up_val = X[val_idx], y_up[val_idx]
        
        reg_up = xgb.XGBRegressor(**xgb_params, early_stopping_rounds=10)
        reg_up.fit(X_tr, y_up_tr, eval_set=[(X_val, y_up_val)], verbose=False)
        
        # Keep track of the best model across folds
        score = reg_up.best_score
        if score < best_up_score:
            best_up_score = score
            best_up_model = reg_up

    best_up_model.save_model(MAX_UP_MODEL_FILE)
    print(f"    Saved -> {MAX_UP_MODEL_FILE}")
    
    print(f"[5] Training Max_Down Excursion Regressor on {n} samples (Embargo KFold)...")
    best_down_model = None
    best_down_score = float('inf')
    
    for fold, (tr_idx, val_idx) in enumerate(kf.split(X)):
        X_tr, y_down_tr = X[tr_idx], y_down[tr_idx]
        X_val, y_down_val = X[val_idx], y_down[val_idx]
        
        reg_down = xgb.XGBRegressor(**xgb_params, early_stopping_rounds=10)
        reg_down.fit(X_tr, y_down_tr, eval_set=[(X_val, y_down_val)], verbose=False)
        
        score = reg_down.best_score
        if score < best_down_score:
            best_down_score = score
            best_down_model = reg_down

    best_down_model.save_model(MAX_DOWN_MODEL_FILE)
    print(f"    Saved -> {MAX_DOWN_MODEL_FILE}")
    
    print("[6] Success! Dynamic ML Excursion models are ready.")

if __name__ == "__main__":
    train_and_save()
