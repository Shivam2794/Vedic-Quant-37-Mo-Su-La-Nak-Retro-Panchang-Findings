import os
import sys
import warnings
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

BASE_DIR = r"C:\Users\patel\Desktop\Python\Learn"
MATRIX_FILE = os.path.join(BASE_DIR, "genesis_9000_MUNDANE.parquet")
MODELS_DIR = os.path.join(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch", "models")

BARRIER_BARS = 6

PAIRS = {
    'GLD': ('GLD', 'SPY'), 'SLV': ('SLV', 'SPY'), 'COPX': ('COPX', 'SPY'),
    'CPER': ('CPER', 'SPY'), 'GDX': ('GDX', 'SPY'), 'URA': ('URA', 'SPY'),
    'NLR': ('NLR', 'SPY'), 'XLE': ('XLE', 'SPY'), 'XLF': ('XLF', 'SPY'),
    'XLV': ('XLV', 'SPY'), 'XLI': ('XLI', 'SPY'), 'XLB': ('XLB', 'SPY'),
    'XLY': ('XLY', 'SPY'), 'XLP': ('XLP', 'SPY'), 'XLU': ('XLU', 'SPY'),
    'XLRE': ('XLRE', 'SPY'), 'XLC': ('XLC', 'SPY'), 'XLK': ('XLK', 'SPY'),
    'SMH': ('SMH', 'SPY'), 'XOP': ('XOP', 'SPY'), 'KRE': ('KRE', 'SPY'),
    'ITB': ('ITB', 'SPY'), 'XBI': ('XBI', 'SPY'), 'JETS': ('JETS', 'SPY'),
    'HACK': ('HACK', 'SPY'), 'TAN': ('TAN', 'SPY'), 'PAVE': ('PAVE', 'SPY'),
    'XME': ('XME', 'SPY')
}

def fetch_pair_data(asset, benchmark):
    df_asset = yf.download(asset, period="730d", interval="1h", progress=False, auto_adjust=False)
    df_bench = yf.download(benchmark, period="730d", interval="1h", progress=False, auto_adjust=False)
    
    if df_asset.empty or df_bench.empty: return None
    
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

def apply_labels_and_excursions(df):
    closes = df['Close'].values
    n = len(closes)
    labels = np.zeros(n, dtype=np.int8)
    max_ups = np.zeros(n, dtype=np.float32)
    max_downs = np.zeros(n, dtype=np.float32)
    
    for i in range(n - BARRIER_BARS):
        if closes[i + BARRIER_BARS] > closes[i]: labels[i] = 1
        else: labels[i] = 0
        
        entry = closes[i]
        window = closes[i+1 : i+1+BARRIER_BARS]
        max_ups[i] = (np.max(window) / entry) - 1.0
        max_downs[i] = 1.0 - (np.min(window) / entry)
        
    df['label'] = labels
    df['max_up'] = max_ups
    df['max_down'] = max_downs
    return df

def train_asset(asset_name, asset_ticker, bench_ticker, df_astro):
    print(f"--- Training {asset_name} ---")
    df_price = fetch_pair_data(asset_ticker, bench_ticker)
    if df_price is None or len(df_price) < 1000:
        print(f"Skipping {asset_name} due to missing data.")
        return
        
    df_price['Date'] = pd.to_datetime(df_price['dt']).dt.tz_localize(None).astype('datetime64[us]')
    max_astro_date = df_astro['Date'].max()
    df_price = df_price[df_price['Date'] <= max_astro_date]
    df_price.sort_values('Date', inplace=True)
    
    df_fused = pd.merge_asof(df_price, df_astro, on='Date', direction='backward')
    df_fused = df_fused.dropna(subset=['Tithi_Num'])
    
    df2 = apply_labels_and_excursions(df_fused).iloc[:-BARRIER_BARS].reset_index(drop=True)
    n = len(df2)
    
    exclude_cols = ['Close', 'Volume', 'dt', 'label', 'max_up', 'max_down', 'Date', 'index', 'Year', 'Quarter']
    primary_cols = [c for c in df2.columns if c not in exclude_cols and df2[c].dtype in [np.float32, np.float64, np.int64, np.int32, int, float]]
    
    X = df2[primary_cols].fillna(0).values.astype(np.float32)
    y = df2['label'].values
    y_up = df2['max_up'].values
    y_down = df2['max_down'].values
    meta_raw = df2['Volume'].values.reshape(-1, 1)
    
    # 1. Primary Model
    xgb_clf = dict(n_estimators=30, max_depth=3, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.5, reg_lambda=1.5)
    prim = xgb.XGBClassifier(**xgb_clf)
    prim.fit(X, y, verbose=False)
    prim.save_model(os.path.join(MODELS_DIR, f"{asset_name}_primary.json"))
    
    # 2. Meta Model (OOS Predictions)
    tscv = TimeSeriesSplit(n_splits=5)
    y_pred_oos = np.zeros(n)
    valid_mask = np.zeros(n, dtype=bool)
    
    for tr_in, val_in in tscv.split(X):
        if len(tr_in) <= BARRIER_BARS: continue
        clean_tr_in = tr_in[:-BARRIER_BARS]
        m = xgb.XGBClassifier(**xgb_clf)
        if len(np.unique(y[clean_tr_in])) > 1:
            m.fit(X[clean_tr_in], y[clean_tr_in], verbose=False)
            y_pred_oos[val_in] = m.predict(X[val_in])
            valid_mask[val_in] = True
            
    meta_targ = (y_pred_oos[valid_mask] == y[valid_mask]).astype(int)
    meta_feat = np.column_stack([y_pred_oos[valid_mask], meta_raw[valid_mask]])
    
    meta_m = xgb.XGBClassifier(n_estimators=20, max_depth=2, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.5, reg_lambda=1.5)
    meta_m.fit(meta_feat, meta_targ, verbose=False)
    meta_m.save_model(os.path.join(MODELS_DIR, f"{asset_name}_meta.json"))
    
    # 3. Dynamic Excursion Models
    # NOTE: No early stopping here. Early stopping on a 10% holdout caused degenerate
    # 11-tree models for low-spread assets (XLC, XLF, XLI, XLK, PAVE) that predict
    # the same constant value for every bar regardless of planet positions.
    # Fix: Fixed conservative tree count + strong regularization prevents overfitting
    # without the risk of degenerate underfitting from premature stopping.
    xgb_reg = dict(
        n_estimators=30,           # Conservative, matches primary model
        max_depth=3,               # Shallow trees prevent high-variance fits
        learning_rate=0.05,
        tree_method='hist',
        random_state=42,
        reg_alpha=2.0,             # Doubled L1 vs classifier
        reg_lambda=2.0,            # Doubled L2 vs classifier
        min_child_weight=5,        # Require at least 5 samples per leaf
        subsample=0.8,             # Row subsampling
        colsample_bytree=0.6       # Feature subsampling
    )
    
    reg_up = xgb.XGBRegressor(**xgb_reg)
    reg_up.fit(X, y_up, verbose=False)
    reg_up.save_model(os.path.join(MODELS_DIR, f"{asset_name}_max_up.json"))
    
    reg_down = xgb.XGBRegressor(**xgb_reg)
    reg_down.fit(X, y_down, verbose=False)
    reg_down.save_model(os.path.join(MODELS_DIR, f"{asset_name}_max_down.json"))
    
    print(f"   [+] Saved 4 Models for {asset_name}")
    return primary_cols

def train_all():
    print("Loading Mundane Matrix...")
    df_astro = pd.read_parquet(MATRIX_FILE)
    df_astro['Date'] = pd.to_datetime(df_astro['Date']).dt.tz_localize(None).astype('datetime64[us]')
    if 'Close' in df_astro.columns: df_astro.drop(columns=['Close'], inplace=True)
    if 'Volume' in df_astro.columns: df_astro.drop(columns=['Volume'], inplace=True)
    
    prim_cols = None
    for asset_name, (ticker, bench) in PAIRS.items():
        cols = train_asset(asset_name, ticker, bench, df_astro)
        if cols and not prim_cols:
            prim_cols = cols
            
    # Save feature names once (they are identical for all assets)
    with open(os.path.join(MODELS_DIR, "universal_feature_names.txt"), "w") as f:
        for col in prim_cols:
            f.write(col + "\n")
            
    print("All 112 Universal Models Trained!")

if __name__ == "__main__":
    train_all()
