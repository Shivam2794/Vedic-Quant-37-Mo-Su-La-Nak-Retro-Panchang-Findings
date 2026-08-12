import numpy as np
import pandas as pd
import os
import itertools
from opus12_erc_optimizer_v12 import calculate_dynamic_erc_weights

# --- CONFIGURATION ---
DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
ASSETS = ['SPY', 'QQQ', 'TQQQ', 'UPRO', 'TLT', 'GLD', 'BTC-USD']
BPS_COSTS = {
    'SPY': 1.0, 'QQQ': 1.0, 'TQQQ': 2.0, 'UPRO': 3.0, 
    'TLT': 1.0, 'GLD': 1.0, 'BTC-USD': 15.0
}
TARGET_VOL = 0.15
MAX_LEV = 1.0

# Define Pools
RISK_ON_POOLS = [
    ['QQQ', 'SPY', 'TQQQ'],
    ['TQQQ', 'UPRO'],
    ['QQQ', 'TQQQ'],
    ['SPY', 'UPRO']
]

RISK_OFF_POOLS = [
    ['GLD', 'TLT'],
    ['TLT'],
    ['GLD'],
]

LOOKBACKS = [20, 40, 60, 90, 120]
SMA_WINDOWS = [50, 100, 150, 200, 250]

def load_v9_matrices():
    print(f"Loading V9 matrices from {DATA_DIR}...")
    try:
        frozen_df = pd.read_parquet(os.path.join(DATA_DIR, "frozen_universe_data.parquet"))
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None

    dates = frozen_df.index.get_level_values('Date').unique().sort_values()
    T = len(dates)
    N = len(ASSETS)
    
    returns_matrix = np.full((N, T), np.nan)
    closes_matrix = np.full((N, T), np.nan)
    
    for i, asset in enumerate(ASSETS):
        try:
            asset_df = frozen_df.xs(asset, level='Ticker')
            asset_df = asset_df.reindex(dates)
            returns_matrix[i, :] = asset_df['Adj Close'].pct_change().values
            closes_matrix[i, :] = asset_df['Close'].values
        except KeyError:
            pass

    rf_daily = np.full(T, 0.02 / 252) # 2% annualized RF
    
    return returns_matrix, closes_matrix, rf_daily, dates

def main():
    returns_matrix, closes_matrix, rf_daily, dates = load_v9_matrices()
    if returns_matrix is None: return
    
    N, T = returns_matrix.shape
    
    # 1. Define Tradability / Inception Mask
    first_valid = np.array([np.argmax(np.isfinite(returns_matrix[i])) for i in range(N)])
    
    # Pre-cache weights
    print("Precalculating ERC Weights for Risk-On Pools...")
    risk_on_weights_cache = {}
    for pool in RISK_ON_POOLS:
        indices = [ASSETS.index(a) for a in pool]
        for lb in LOOKBACKS:
            w = calculate_dynamic_erc_weights(returns_matrix, indices, lookback=lb)
            risk_on_weights_cache[(tuple(pool), lb)] = w
            
    print("Precalculating ERC Weights for Risk-Off Pools...")
    risk_off_weights_cache = {}
    for pool in RISK_OFF_POOLS:
        indices = [ASSETS.index(a) for a in pool]
        for lb in LOOKBACKS:
            w = calculate_dynamic_erc_weights(returns_matrix, indices, lookback=lb)
            risk_off_weights_cache[(tuple(pool), lb)] = w

    combinations = list(itertools.product(SMA_WINDOWS, LOOKBACKS, RISK_ON_POOLS, RISK_OFF_POOLS))
    print(f"Sweeping {len(combinations)} combinations...")
    
    spy_idx = ASSETS.index('SPY')
    spy_close = closes_matrix[spy_idx]
    
    # Cost array
    cost_bps = np.array([BPS_COSTS[a] for a in ASSETS])
    
    # Determine GLOBAL START date to ensure fair comparison
    # TQQQ started in 2010.
    all_assets_used = set().union(*RISK_ON_POOLS, *RISK_OFF_POOLS)
    global_start = max(first_valid[ASSETS.index(a)] for a in all_assets_used) + max(LOOKBACKS) + max(SMA_WINDOWS)
    
    results = []
    
    for sma_w, lb, ro_pool, roff_pool in combinations:
        # Regime Calculation
        sma = pd.Series(spy_close).rolling(window=sma_w).mean().values
        
        # 3-state regime: 1 (Risk On), 0 (Risk Off), -1 (Unknown)
        regime = np.full(T, -1)
        valid_sma = np.isfinite(sma) & np.isfinite(spy_close)
        regime[valid_sma] = (spy_close[valid_sma] > sma[valid_sma]).astype(int)
        
        # Shift 1 day: signal computed at close[t], applied to day t+1 returns
        regime_shifted = np.full(T, -1)
        regime_shifted[1:] = regime[:-1]
        
        ro_w = risk_on_weights_cache[(tuple(ro_pool), lb)]
        roff_w = risk_off_weights_cache[(tuple(roff_pool), lb)]
        
        # Determine target weights for day t+1 based on regime at close t
        W_decided = np.zeros((N, T))
        mask_ro = (regime_shifted == 1)
        mask_roff = (regime_shifted == 0)
        
        W_decided[:, mask_ro] = ro_w[:, mask_ro]
        W_decided[:, mask_roff] = roff_w[:, mask_roff]
        
        # W_decided is what we hold during day t+1. 
        # Calculate gross returns
        R = np.where(np.isfinite(returns_matrix), returns_matrix, 0.0)
        port_gross = np.einsum('it,it->t', W_decided, R)
        
        # Apply Turnover Costs
        # Turnover happens when W_decided changes from t to t+1
        W_diff = np.abs(np.diff(W_decided, axis=1, prepend=0))
        cost = (W_diff * (cost_bps[:, None] / 10000.0)).sum(axis=0)
        
        port_net = port_gross - cost
        
        # Apply Volatility Targeting (Optional, max lev = 1.0)
        # Using a 20-day trailing realized volatility of the gross return
        sig = pd.Series(port_gross).rolling(20).std().shift(1).values * np.sqrt(252)
        sig = np.where(np.isfinite(sig) & (sig > 0), sig, TARGET_VOL)
        lev = np.clip(TARGET_VOL / sig, 0.0, MAX_LEV)
        
        port_net = port_net * lev
        
        # Evaluate from global_start
        if global_start >= T:
            continue
            
        eval_ret = port_net[global_start:]
        eval_rf = rf_daily[global_start:]
        
        if (eval_ret <= -1.0).any():
            continue # Ruin event
            
        equity = np.cumprod(1.0 + eval_ret)
        
        cagr = equity[-1] ** (252 / len(eval_ret)) - 1.0
        
        # Correct Sharpe Ratio
        ex_ret = eval_ret - eval_rf
        ann_vol = np.std(ex_ret, ddof=1) * np.sqrt(252)
        if ann_vol <= 0:
            sharpe = 0
        else:
            sharpe = np.mean(ex_ret) * 252 / ann_vol
            
        dd = equity / np.maximum.accumulate(equity) - 1.0
        mdd = dd.min()
        
        results.append({
            'sma': sma_w,
            'lookback': lb,
            'risk_on': tuple(ro_pool),
            'risk_off': tuple(roff_pool),
            'cagr': cagr,
            'sharpe': sharpe,
            'mdd': mdd
        })
        
    df = pd.DataFrame(results)
    df = df.sort_values('sharpe', ascending=False)
    
    print("\n--- BEST STRATEGIES (V12) ---")
    print(df.head(10).to_string())
    df.to_csv(os.path.join(DATA_DIR, "opus12_gridsearch_results.csv"), index=False)
    
if __name__ == "__main__":
    main()
