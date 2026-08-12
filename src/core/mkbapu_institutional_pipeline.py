"""
MK Bapu Absolute Purity Engine
==============================
730-Day History (1-Hour Granularity)
Market-Neutral (Asset / SPY Close-Only Ratio)
Zero Phantom Wicks (Close-to-Close Simulation)
Zero Look-Ahead Bias (6-Bar Purge Window in WFO)
"""
import sys, warnings, time
import numpy as np
import pandas as pd
import swisseph as swe
import yfinance as yf
from datetime import datetime, timezone
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

PAIRS = {
    'SMH_SPY': ('SMH', 'SPY', 'US', 40.7128, -74.0060),    # Semiconductors
    'XLK_SPY': ('XLK', 'SPY', 'US', 40.7128, -74.0060),    # Tech Sector
    'GLD_SPY': ('GLD', 'SPY', 'US', 40.7128, -74.0060),    # Physical Gold
    'SLV_SPY': ('SLV', 'SPY', 'US', 40.7128, -74.0060),    # Physical Silver
    'GDX_SPY': ('GDX', 'SPY', 'US', 40.7128, -74.0060),    # Gold Miners
    'URA_SPY': ('URA', 'SPY', 'US', 40.7128, -74.0060)     # Uranium
}

BARRIER_BARS = 6  # 6 Hours

# ═══════════════════════════════════════════════════════════════════════
# DATA & EPHEMERIS
# ═══════════════════════════════════════════════════════════════════════
def fetch_pair_data(asset, benchmark, market):
    print(f"\n[1] Fetching 2 YEARS (1h) data for {asset}/{benchmark} spread...")
    df_asset = yf.download(asset, period="730d", interval="1h", progress=False)
    df_bench = yf.download(benchmark, period="730d", interval="1h", progress=False)
    
    if df_asset.empty or df_bench.empty: raise ValueError("No data returned")
    
    if isinstance(df_asset.columns, pd.MultiIndex): df_asset.columns = df_asset.columns.get_level_values(0)
    if isinstance(df_bench.columns, pd.MultiIndex): df_bench.columns = df_bench.columns.get_level_values(0)
        
    df_asset = df_asset[['Close', 'Volume']].dropna()
    df_bench = df_bench[['Close']].dropna()
    
    # Align dates
    df, bench = df_asset.align(df_bench, join='inner', axis=0)
    
    # Create Synthetic Ratio Spread (CLOSE ONLY - NO PHANTOM WICKS)
    syn = pd.DataFrame()
    syn['Close'] = df['Close'] / bench['Close']
    syn['Volume'] = df['Volume']
    syn['dt'] = syn.index
    
    if market == 'US': mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    else: mask = syn.index == syn.index
    syn = syn[mask].reset_index(drop=True)
    return syn

def compute_ephemeris(df, lat, lon):
    swe.set_ephe_path('')
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    rows = []
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    for i, row in df.iterrows():
        dt_utc = row['dt'].to_pydatetime()
        if dt_utc.tzinfo is not None: dt_utc = dt_utc.astimezone(timezone.utc).replace(tzinfo=None)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
        feats = {}
        for pid, name in [(swe.SUN,"Sun"),(swe.MOON,"Moon"),(swe.MERCURY,"Mercury"),
                          (swe.VENUS,"Venus"),(swe.MARS,"Mars"),(swe.JUPITER,"Jupiter"),
                          (swe.SATURN,"Saturn"),(swe.URANUS,"Uranus"),(swe.NEPTUNE,"Neptune"),
                          (swe.PLUTO,"Pluto"),(swe.TRUE_NODE,"Rahu")]:
            r = swe.calc_ut(jd, pid, flags)
            lon2 = r[0][0]
            feats[f"{name}_lon_cos"] = np.cos(np.radians(lon2))
            feats[f"{name}_lon_sin"] = np.sin(np.radians(lon2))
            feats[f"{name}_sign"] = int(lon2 / 30)
        try:
            cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            asc = ascmc[0]
            feats["house_placidus_1_cusp"] = asc
            feats["asc_lon_cos"] = np.cos(np.radians(asc))
            feats["asc_lon_sin"] = np.sin(np.radians(asc))
            feats["asc_sign"] = int(asc/30) % 12
            feats["asc_deg"] = asc % 30
            feats["asc_d60_sign"] = (int(asc/30)*60 + int((asc%30)*60/30)) % 12
        except:
            for k in ["house_placidus_1_cusp","asc_lon_cos","asc_lon_sin","asc_sign","asc_deg","asc_d60_sign"]: feats[k] = 0.0
        rows.append(feats)
    return pd.DataFrame(rows)

def apply_labels(df):
    closes = df['Close'].values
    n = len(closes)
    labels = np.zeros(n, dtype=np.int8)
    # Simple binary label: 1 if Close goes UP after 6 bars, 0 if it goes DOWN.
    for i in range(n - BARRIER_BARS):
        if closes[i + BARRIER_BARS] > closes[i]:
            labels[i] = 1
        else:
            labels[i] = 0
    df['label'] = labels
    return df

# ═══════════════════════════════════════════════════════════════════════
# ABSOLUTE PURITY WFO PIPELINE
# ═══════════════════════════════════════════════════════════════════════
def execute_pure_pipeline(df, pair_name):
    df2 = apply_labels(df).iloc[:-BARRIER_BARS].reset_index(drop=True)
    n = len(df2)
    
    primary_cols = [c for c in df2.columns if c.endswith('_cos') or c.endswith('_sin') or c.endswith('_sign') or c.endswith('_deg')]
    X = df2[primary_cols].fillna(0).values.astype(np.float32)
    y = df2['label'].values
    meta_raw = df2['Volume'].values.reshape(-1, 1) # Only volume as meta-feature now since ATR is gone
    
    closes = df2['Close'].values
    dts = df2['dt'].values
    
    xgb_params = dict(n_estimators=50, max_depth=3, learning_rate=0.05, tree_method='hist', random_state=42)
    tscv = TimeSeriesSplit(n_splits=5)
    
    active_rets = []
    
    print(f"    [WFO] Rolling 5-Fold Strict Close-to-Close Test across {n} total bars...")
    
    for train_index, test_index in tscv.split(X):
        # --- THE PURGE ---
        # Eliminate the last 6 bars of the training set to mathematically destroy overlapping look-ahead bias
        if len(train_index) <= BARRIER_BARS: continue
        clean_train_index = train_index[:-BARRIER_BARS]
        
        X_tr, X_te = X[clean_train_index], X[test_index]
        y_tr, y_te = y[clean_train_index], y[test_index]
        m_raw_tr, m_raw_te = meta_raw[clean_train_index], meta_raw[test_index]
        
        # Primary Model
        prim = xgb.XGBClassifier(**xgb_params)
        if len(np.unique(y_tr)) > 1:
            prim.fit(X_tr, y_tr, verbose=False)
        else:
            prim.fit(np.vstack([X_tr, np.zeros_like(X_tr[0])]), np.append(y_tr, 1-y_tr[0]), verbose=False)
            
        # Meta Model Inner CV (Also Purged)
        meta_m = xgb.XGBClassifier(n_estimators=30, max_depth=2, learning_rate=0.05, random_state=42)
        inner_tscv = TimeSeriesSplit(n_splits=3)
        y_pred_oos = np.zeros(len(y_tr))
        
        for tr_in, val_in in inner_tscv.split(X_tr):
            if len(tr_in) <= BARRIER_BARS: continue
            clean_tr_in = tr_in[:-BARRIER_BARS]
            m = xgb.XGBClassifier(**xgb_params)
            if len(np.unique(y_tr[clean_tr_in])) > 1:
                m.fit(X_tr[clean_tr_in], y_tr[clean_tr_in], verbose=False)
                y_pred_oos[val_in] = m.predict(X_tr[val_in])
            else:
                y_pred_oos[val_in] = y_tr[clean_tr_in][0]
                
        meta_feat = np.column_stack([y_pred_oos, m_raw_tr])
        meta_targ = (y_pred_oos == y_tr).astype(int)
        start_idx = len(X_tr) - len(y_pred_oos[y_pred_oos != 0])
        if start_idx == len(X_tr) or start_idx < 0: start_idx = 0
        if len(np.unique(meta_targ[start_idx:])) > 1:
            meta_m.fit(meta_feat[start_idx:], meta_targ[start_idx:], verbose=False)
        else:
            meta_m.fit(np.vstack([meta_feat[start_idx:], np.zeros_like(meta_feat[0])]), np.append(meta_targ[start_idx:], 1-meta_targ[start_idx:][0]), verbose=False)

        # INFERENCE
        preds = prim.predict(X_te)
        meta_probs = meta_m.predict_proba(np.column_stack([preds, m_raw_te]))[:, 1]
        
        # EXACT CLOSE-TO-CLOSE EVALUATION
        for i, global_idx in enumerate(test_index):
            if global_idx >= len(closes) - BARRIER_BARS: continue
            
            # The Meta-Model sniper waits for 52% confidence
            if meta_probs[i] > 0.52:
                entry = closes[global_idx]
                exit_price = closes[global_idx + BARRIER_BARS]
                
                if preds[i] == 1:
                    trade_ret = (exit_price - entry) / entry
                else:
                    trade_ret = (entry - exit_price) / entry
                    
                active_rets.append(trade_ret)

    print(f"\n    === 730-DAY ABSOLUTE PURITY RESULTS: {pair_name} ===")
    if len(active_rets) == 0:
        print("    [RESULT] Meta-Model vetoed ALL trades. Capital preserved.")
        return
        
    active_rets = np.array(active_rets)
    cum_rets = (1 + active_rets).cumprod()
    tot_ret = cum_rets[-1] - 1
    
    roll_max = np.maximum.accumulate(cum_rets)
    drawdowns = (cum_rets - roll_max) / roll_max
    max_dd = drawdowns.min() if len(drawdowns) > 0 else 0.0
    
    years = max(float((dts[-1] - dts[test_index[0]]) / np.timedelta64(1, 's')) / (365.25636042*24*3600), 0.01)
    cagr = (1 + tot_ret)**(1/years) - 1
    
    wr = (active_rets > 0).mean()
    wins = active_rets[active_rets > 0]
    losses = active_rets[active_rets < 0]
    pf = abs(wins.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else np.inf
    
    print(f"    Trades Taken: {len(active_rets):3d}")
    print(f"    Win Rate:     {wr*100:.1f}%")
    print(f"    Profit Factor:{pf:.2f}")
    print(f"    Max Drawdown: {max_dd*100:.2f}%")
    print(f"    Total Return: {tot_ret*100:+.2f}%")
    print(f"    Ann. CAGR:    {cagr*100:+.1f}%")

def main():
    print("="*70)
    print(" ABSOLUTE PURITY ENGINE (Zero Phantom Wicks, Zero Overlap)")
    print("="*70)
    for pair_name, (asset, bench, market, lat, lon) in PAIRS.items():
        try:
            df = fetch_pair_data(asset, bench, market)
            feat_df = compute_ephemeris(df, lat, lon)
            df2 = pd.concat([df.reset_index(drop=True), feat_df.reset_index(drop=True)], axis=1)
            execute_pure_pipeline(df2, pair_name)
        except Exception as e:
            print(f"Error on {pair_name}: {e}")

if __name__ == "__main__":
    main()
