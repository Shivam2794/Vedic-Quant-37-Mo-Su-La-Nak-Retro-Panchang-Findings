import sys, warnings, time
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

PAIRS = {
    # Metals Matrix
    'GLD_SPY': ('GLD', 'SPY', 'US'),
    'SLV_SPY': ('SLV', 'SPY', 'US'),
    'COPX_SPY': ('COPX', 'SPY', 'US'),
    'CPER_SPY': ('CPER', 'SPY', 'US'),
    'GDX_SPY': ('GDX', 'SPY', 'US'),
    'URA_SPY': ('URA', 'SPY', 'US'),
    'NLR_SPY': ('NLR', 'SPY', 'US'),
    # The 11 SPDR Sectors
    'XLE_SPY': ('XLE', 'SPY', 'US'),   # Energy
    'XLF_SPY': ('XLF', 'SPY', 'US'),   # Financials
    'XLV_SPY': ('XLV', 'SPY', 'US'),   # Healthcare
    'XLI_SPY': ('XLI', 'SPY', 'US'),   # Industrials
    'XLB_SPY': ('XLB', 'SPY', 'US'),   # Materials
    'XLY_SPY': ('XLY', 'SPY', 'US'),   # Consumer Discretionary
    'XLP_SPY': ('XLP', 'SPY', 'US'),   # Consumer Staples
    'XLU_SPY': ('XLU', 'SPY', 'US'),   # Utilities
    'XLRE_SPY': ('XLRE', 'SPY', 'US'), # Real Estate
    'XLC_SPY': ('XLC', 'SPY', 'US'),   # Communication
    'XLK_SPY': ('XLK', 'SPY', 'US'),   # Tech
    # Subsectors
    'SMH_SPY': ('SMH', 'SPY', 'US'),   # Semiconductors
    'XOP_SPY': ('XOP', 'SPY', 'US'),   # Oil & Gas
    'KRE_SPY': ('KRE', 'SPY', 'US'),   # Regional Banks
    'ITB_SPY': ('ITB', 'SPY', 'US'),   # Homebuilders
    'XBI_SPY': ('XBI', 'SPY', 'US'),   # Biotech
    'JETS_SPY': ('JETS', 'SPY', 'US'), # Airlines
    'HACK_SPY': ('HACK', 'SPY', 'US'), # Cybersecurity
    'TAN_SPY': ('TAN', 'SPY', 'US'),   # Solar
    'PAVE_SPY': ('PAVE', 'SPY', 'US'), # Infrastructure
    'XME_SPY': ('XME', 'SPY', 'US')    # Metals & Mining
}

BARRIER_BARS = 6  # 6 Hours Hold

def fetch_pair_data(asset, benchmark, market):
    print(f"\n[1] Fetching 2 YEARS (1h) data for {asset}/{benchmark} spread...")
    df_asset = yf.download(asset, period="730d", interval="1h", progress=False, auto_adjust=False)
    df_bench = yf.download(benchmark, period="730d", interval="1h", progress=False, auto_adjust=False)
    
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
    
    if market == 'US': mask = (syn.index.hour >= 9) & (syn.index.hour <= 15)
    else: mask = syn.index == syn.index
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

def execute_genesis_pipeline(df, pair_name):
    df2 = apply_labels(df).iloc[:-BARRIER_BARS].reset_index(drop=True)
    n = len(df2)
    
    # Exclude non-feature columns
    exclude_cols = ['Close', 'Volume', 'dt', 'label', 'Date', 'index', 'Year', 'Quarter']
    primary_cols = [c for c in df2.columns if c not in exclude_cols and df2[c].dtype in [np.float32, np.float64, np.int64, np.int32, int, float]]
    
    X = df2[primary_cols].fillna(0).values.astype(np.float32)
    y = df2['label'].values
    meta_raw = df2['Volume'].values.reshape(-1, 1) 
    
    closes = df2['Close'].values
    dts = df2['dt'].values
    
    xgb_params = dict(n_estimators=30, max_depth=3, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.5, reg_lambda=1.5)
    tscv = TimeSeriesSplit(n_splits=5)
    
    active_rets = []
    
    print(f"    [WFO] Rolling 5-Fold Genesis Purged Test across {n} total bars...")
    
    for train_index, test_index in tscv.split(X):
        if len(train_index) <= BARRIER_BARS: continue
        clean_train_index = train_index[:-BARRIER_BARS]
        
        X_tr, X_te = X[clean_train_index], X[test_index]
        y_tr, y_te = y[clean_train_index], y[test_index]
        m_raw_tr, m_raw_te = meta_raw[clean_train_index], meta_raw[test_index]
        
        prim = xgb.XGBClassifier(**xgb_params)
        if len(np.unique(y_tr)) > 1:
            prim.fit(X_tr, y_tr, verbose=False)
        else:
            continue
            
        meta_m = xgb.XGBClassifier(n_estimators=20, max_depth=2, learning_rate=0.05, tree_method='hist', random_state=42, reg_alpha=1.5, reg_lambda=1.5)
        inner_tscv = TimeSeriesSplit(n_splits=3)
        y_pred_oos = np.zeros(len(y_tr))
        valid_mask = np.zeros(len(y_tr), dtype=bool)
        
        for tr_in, val_in in inner_tscv.split(X_tr):
            if len(tr_in) <= BARRIER_BARS: continue
            clean_tr_in = tr_in[:-BARRIER_BARS]
            m = xgb.XGBClassifier(**xgb_params)
            if len(np.unique(y_tr[clean_tr_in])) > 1:
                m.fit(X_tr[clean_tr_in], y_tr[clean_tr_in], verbose=False)
                y_pred_oos[val_in] = m.predict(X_tr[val_in])
                valid_mask[val_in] = True
            else:
                y_pred_oos[val_in] = y_tr[clean_tr_in][0]
                valid_mask[val_in] = True
                
        meta_targ = (y_pred_oos[valid_mask] == y_tr[valid_mask]).astype(int)
        meta_feat = np.column_stack([y_pred_oos[valid_mask], m_raw_tr[valid_mask]])
        if len(np.unique(meta_targ)) > 1:
            meta_m.fit(meta_feat, meta_targ, verbose=False)
        else:
            continue

        preds = prim.predict(X_te)
        meta_probs = meta_m.predict_proba(np.column_stack([preds, m_raw_te]))[:, 1]
        
        # EXACT CLOSE-TO-CLOSE EVALUATION WITH `next_free_idx` FIX
        next_free_idx = 0
        for i, global_idx in enumerate(test_index):
            if global_idx >= len(closes) - BARRIER_BARS: continue
            
            # Mathematical Fix: Only trade if we don't currently have a position open
            if global_idx < next_free_idx:
                continue

            # Meta-Model Wait
            if meta_probs[i] > 0.52:
                entry = closes[global_idx]
                exit_price = closes[global_idx + BARRIER_BARS]
                
                SLIPPAGE = 0.0010 # 10 bps round trip
                
                if preds[i] == 1:
                    trade_ret = ((exit_price - entry) / entry) - SLIPPAGE
                else:
                    trade_ret = ((entry - exit_price) / entry) - SLIPPAGE
                    
                active_rets.append(trade_ret)
                
                # Lock the portfolio for the duration of the trade
                next_free_idx = global_idx + BARRIER_BARS

    print(f"\n    === 730-DAY GENESIS PURITY RESULTS: {pair_name} ===")
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
    MUNDANE_CAMP = {'GLD', 'SLV', 'COPX', 'CPER', 'GDX', 'URA', 'NLR', 'XLE', 'XLB', 'XOP', 'TAN', 'XME', 'XLU', 'XLP'}
    
    for pair_name, (asset, bench, market) in PAIRS.items():
        try:
            print(f"\n--- Processing {pair_name} ---")
            
            # 1. Null Hypothesis Override
            matrix_file = f'C:/Users/patel/Desktop/Python/Learn/genesis_9000_NOISE.parquet'
            print(f"Loading NOISE Matrix: {matrix_file}")
                
            df_astro = pd.read_parquet(matrix_file)
            df_astro['Date'] = pd.to_datetime(df_astro['Date']).dt.tz_localize(None).astype('datetime64[us]')
            if 'Close' in df_astro.columns: df_astro.drop(columns=['Close'], inplace=True)
            if 'Volume' in df_astro.columns: df_astro.drop(columns=['Volume'], inplace=True)
            max_astro_date = df_astro['Date'].max()
            
            # 2. Fetch Price
            df_price = fetch_pair_data(asset, bench, market)
            # Remove TZ and cast to [us] to match the parquet file
            df_price['Date'] = pd.to_datetime(df_price['dt']).dt.tz_localize(None).astype('datetime64[us]')
            df_price = df_price[df_price['Date'] <= max_astro_date]
            df_price.sort_values('Date', inplace=True)
            
            # Merge 9009 features forward onto the hourly price bars
            df_fused = pd.merge_asof(df_price, df_astro, on='Date', direction='backward')
            df_fused = df_fused.dropna(subset=['Tithi_Num']) # Drop rows before astro data starts
            
            execute_genesis_pipeline(df_fused, pair_name)
        except Exception as e:
            print(f"Error on {pair_name}: {e}")

if __name__ == "__main__":
    main()
