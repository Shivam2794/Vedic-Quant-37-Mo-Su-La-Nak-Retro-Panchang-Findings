import numpy as np
import pandas as pd
import os
import itertools
from opus12_erc_optimizer_v12 import calculate_dynamic_erc_weights

# --- CONFIGURATION ---
DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
ASSETS = ['SPY', 'QQQ', 'TQQQ', 'UPRO', 'TLT', 'GLD']
BPS_COSTS = {
    'SPY': 1.0, 'QQQ': 1.0, 'TQQQ': 2.0, 'UPRO': 3.0, 
    'TLT': 1.0, 'GLD': 1.0
}
TARGET_VOL = 0.15
MAX_LEV_RO = 1.0
MAX_LEV_ROFF = 1.5

LOOKBACKS = [20, 60, 120]
SMA_WINDOWS = [150, 200, 250]
BUFFERS = [0.01, 0.02, 0.03]  # 1%, 2%, 3% hysteresis buffer
MOM_WINDOWS = [126, 252]      # 6 month, 12 month momentum

def load_v9_matrices():
    print(f"Loading matrices from {DATA_DIR}...")
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

def get_buffered_regime(price, sma, buffer):
    T = len(price)
    regime = np.full(T, -1)
    
    # Need at least valid SMA
    valid = np.isfinite(sma) & np.isfinite(price)
    
    current_state = 0 # default to risk-off initially
    for t in range(T):
        if not valid[t]:
            continue
            
        p = price[t]
        s = sma[t]
        
        upper_band = s * (1.0 + buffer)
        lower_band = s * (1.0 - buffer)
        
        if current_state == 0 and p > upper_band:
            current_state = 1
        elif current_state == 1 and p < lower_band:
            current_state = 0
            
        regime[t] = current_state
        
    return regime

def main():
    returns_matrix, closes_matrix, rf_daily, dates = load_v9_matrices()
    if returns_matrix is None: return
    
    N, T = returns_matrix.shape
    first_valid = np.array([np.argmax(np.isfinite(returns_matrix[i])) for i in range(N)])
    
    # Pre-cache weights
    print("Precalculating ERC Weights...")
    
    # The 3 core pools we use
    pool_qqq = ['QQQ', 'TQQQ']
    pool_spy = ['SPY', 'UPRO']
    pool_roff = ['GLD', 'TLT']
    
    weights_cache = {}
    for pool in [pool_qqq, pool_spy, pool_roff]:
        indices = [ASSETS.index(a) for a in pool]
        for lb in LOOKBACKS:
            w = calculate_dynamic_erc_weights(returns_matrix, indices, lookback=lb)
            weights_cache[(tuple(pool), lb)] = w

    combinations = list(itertools.product(SMA_WINDOWS, LOOKBACKS, BUFFERS, MOM_WINDOWS))
    print(f"Sweeping {len(combinations)} combinations...")
    
    spy_idx = ASSETS.index('SPY')
    qqq_idx = ASSETS.index('QQQ')
    spy_close = closes_matrix[spy_idx]
    
    cost_bps = np.array([BPS_COSTS[a] for a in ASSETS])
    global_start = max(first_valid) + max(LOOKBACKS) + max(SMA_WINDOWS) + max(MOM_WINDOWS)
    
    results = []
    
    for sma_w, lb, buffer, mom_w in combinations:
        # Regime Calculation with Hysteresis
        sma = pd.Series(spy_close).rolling(window=sma_w).mean().values
        regime = get_buffered_regime(spy_close, sma, buffer)
        
        # Relative Momentum
        spy_mom = pd.Series(closes_matrix[spy_idx]).pct_change(mom_w).values
        qqq_mom = pd.Series(closes_matrix[qqq_idx]).pct_change(mom_w).values
        
        # Shift signals 1 day: computed at close[t], applied to day t+1 returns
        regime_shifted = np.full(T, -1)
        regime_shifted[1:] = regime[:-1]
        
        spy_mom_shifted = np.full(T, np.nan)
        spy_mom_shifted[1:] = spy_mom[:-1]
        
        qqq_mom_shifted = np.full(T, np.nan)
        qqq_mom_shifted[1:] = qqq_mom[:-1]
        
        # Determine target weights for day t+1
        W_decided = np.zeros((N, T))
        
        # Boolean masks
        mask_ro = (regime_shifted == 1)
        mask_roff = (regime_shifted == 0)
        
        # Among risk on, pick QQQ if QQQ > SPY, else SPY
        # Handling NaNs in momentum by falling back to QQQ safely
        qqq_wins = mask_ro & (np.nan_to_num(qqq_mom_shifted, 0.0) >= np.nan_to_num(spy_mom_shifted, 0.0))
        spy_wins = mask_ro & (~qqq_wins)
        
        W_decided[:, qqq_wins] = weights_cache[(tuple(pool_qqq), lb)][:, qqq_wins]
        W_decided[:, spy_wins] = weights_cache[(tuple(pool_spy), lb)][:, spy_wins]
        W_decided[:, mask_roff] = weights_cache[(tuple(pool_roff), lb)][:, mask_roff]
        
        # Calculate gross returns
        R = np.where(np.isfinite(returns_matrix), returns_matrix, 0.0)
        port_gross = np.einsum('it,it->t', W_decided, R)
        
        # Apply Turnover Costs
        W_diff = np.abs(np.diff(W_decided, axis=1, prepend=0))
        cost = (W_diff * (cost_bps[:, None] / 10000.0)).sum(axis=0)
        
        port_net = port_gross - cost
        
        # Apply Volatility Targeting (20-day trailing)
        sig = pd.Series(port_gross).rolling(20).std().shift(1).values * np.sqrt(252)
        sig = np.where(np.isfinite(sig) & (sig > 0), sig, TARGET_VOL)
        
        # Dual max leverage caps
        lev = np.zeros(T)
        
        # In Risk-On, limit to 1.0
        lev[mask_ro] = np.clip(TARGET_VOL / sig[mask_ro], 0.0, MAX_LEV_RO)
        # In Risk-Off, limit to 1.5
        lev[mask_roff] = np.clip(TARGET_VOL / sig[mask_roff], 0.0, MAX_LEV_ROFF)
        
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
            'buffer': buffer,
            'mom_w': mom_w,
            'cagr': cagr,
            'sharpe': sharpe,
            'mdd': mdd
        })
        
    df = pd.DataFrame(results)
    df = df.sort_values('sharpe', ascending=False)
    
    print("\n--- BEST STRATEGIES (V13 DUAL MOMENTUM) ---")
    print(df.head(10).to_string())
    df.to_csv(os.path.join(DATA_DIR, "opus13_gridsearch_results.csv"), index=False)
    
if __name__ == "__main__":
    main()
