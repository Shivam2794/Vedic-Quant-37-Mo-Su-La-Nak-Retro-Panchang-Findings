import os
import numpy as np
import pandas as pd
import itertools
from opus10_erc_optimizer_v10 import calculate_dynamic_erc_weights
from opus10_gridsearch_v10 import load_v9_matrices

def calculate_drawdown(cum_returns):
    rolling_max = np.maximum.accumulate(cum_returns)
    drawdowns = (cum_returns - rolling_max) / rolling_max
    return np.min(drawdowns)

def optimize_and_sweep():
    data_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
    dates, returns_matrix, assets = load_v9_matrices(data_dir)
    
    frozen_df = pd.read_parquet(os.path.join(data_dir, 'frozen_universe_data.parquet'))
    spy_df = frozen_df.xs('SPY', level='Ticker').reindex(dates)
    spy_close = spy_df['Adj Close'].values
    
    # 1. Precalculate Regimes
    sma_windows = [50, 100, 150, 200, 250, 300]
    regimes = {}
    for w in sma_windows:
        sma = pd.Series(spy_close).rolling(window=w).mean().values
        regime = (spy_close > sma).astype(int)
        regimes[w] = regime

    # 2. Define Asset Pools
    risk_on_pools = [
        ['TQQQ', 'UPRO'],
        ['QQQ', 'SPY'],
        ['QQQ', 'SPY', 'TQQQ'],
        ['UPRO', 'QQQ']
    ]
    
    risk_off_pools = [
        ['GLD', 'TLT'],
        ['GLD'],
        ['TLT'],
        ['BTC-USD', 'TLT'],
        ['BTC-USD', 'GLD', 'TLT']
    ]
    
    lookbacks = [20, 40, 60, 90, 120]
    
    # We will compute the ERC weights for each pool + lookback combo independently to save time
    # rather than dynamically computing it inside the massive loop.
    N, T = returns_matrix.shape
    
    def get_pool_weights(pool, lookback):
        positions = np.zeros((N, T))
        for asset in pool:
            positions[assets.index(asset), :] = 1
        return calculate_dynamic_erc_weights(returns_matrix, positions, lookback=lookback)
        
    print("Precalculating ERC Weights for Risk-On Pools...")
    risk_on_weights_cache = {}
    for pool in risk_on_pools:
        for lb in lookbacks:
            risk_on_weights_cache[(tuple(pool), lb)] = get_pool_weights(pool, lb)
            
    print("Precalculating ERC Weights for Risk-Off Pools...")
    risk_off_weights_cache = {}
    for pool in risk_off_pools:
        for lb in lookbacks:
            risk_off_weights_cache[(tuple(pool), lb)] = get_pool_weights(pool, lb)
            
    # 3. Sweep Combos
    best_sharpe = 0
    best_params = None
    best_cum_ret = None
    
    results = []
    
    combinations = list(itertools.product(sma_windows, lookbacks, risk_on_pools, risk_off_pools))
    print(f"Sweeping {len(combinations)} combinations...")
    
    for sma_w, lb, ro_pool, roff_pool in combinations:
        ro_w = risk_on_weights_cache[(tuple(ro_pool), lb)]
        roff_w = risk_off_weights_cache[(tuple(roff_pool), lb)]
        regime = regimes[sma_w]
        
        # Shift regime by 1 to prevent lookahead
        # regime[t-1] applies to day t's weights
        regime_shifted = np.roll(regime, 1)
        regime_shifted[0] = 0
        
        # Final weights at time t
        # (N, T)
        final_weights = np.zeros_like(ro_w)
        for i in range(N):
            final_weights[i, :] = np.where(regime_shifted == 1, ro_w[i, :], roff_w[i, :])
            
        # Shift weights to apply to next day's returns
        # port_returns[t] = sum(weights[t-1] * ret[t])
        weights_shifted = np.roll(final_weights, 1, axis=1)
        weights_shifted[:, 0] = 0
        
        port_returns = np.sum(weights_shifted * returns_matrix, axis=0)
        
        # Calculate stats (burn-in period = max(sma_w, lb))
        start_idx = max(sma_w, lb)
        valid_returns = port_returns[start_idx:]
        
        if len(valid_returns) == 0:
            continue
            
        cum_ret = np.exp(np.cumsum(valid_returns))
        total_ret = cum_ret[-1]
        cagr = total_ret ** (252 / len(valid_returns)) - 1
        daily_vol = np.std(valid_returns)
        ann_vol = daily_vol * np.sqrt(252)
        sharpe = cagr / ann_vol if ann_vol > 0 else 0
        mdd = calculate_drawdown(cum_ret)
        
        results.append({
            'sma': sma_w,
            'lookback': lb,
            'risk_on': tuple(ro_pool),
            'risk_off': tuple(roff_pool),
            'cagr': cagr,
            'sharpe': sharpe,
            'mdd': mdd
        })
        
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = results[-1]
            best_cum_ret = cum_ret
            
    # Output best
    df = pd.DataFrame(results).sort_values('sharpe', ascending=False)
    df.to_csv("opus11_gridsearch_results.csv", index=False)
    
    print("\n--- BEST STRATEGY FOUND ---")
    print(df.head(5))
    
if __name__ == "__main__":
    optimize_and_sweep()
