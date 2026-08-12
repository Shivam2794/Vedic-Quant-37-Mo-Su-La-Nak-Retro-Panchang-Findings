import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from opus12_erc_optimizer_v12 import calculate_dynamic_erc_weights

# --- CONFIGURATION ---
DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
ASSETS = ['SPY', 'QQQ', 'TLT', 'GLD']
BPS_COSTS = {'SPY': 1.0, 'QQQ': 1.0, 'TLT': 1.0, 'GLD': 1.0}

TARGET_VOL = 0.15
MAX_LEV = 2.0
FINANCING_SPREAD = 0.01 / 252 # 1% annualized spread over RF for borrowing
RF_RATE = 0.02 / 252          # 2% annualized RF (simplified)

SMA_WINDOWS = [50, 100, 150, 200, 250]
LOOKBACK = 60 # ERC covariance lookback

def load_v14_matrices():
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

    rf_daily = np.full(T, RF_RATE)
    return returns_matrix, closes_matrix, rf_daily, dates

def main():
    returns_matrix, closes_matrix, rf_daily, dates = load_v14_matrices()
    if returns_matrix is None: return
    
    N, T = returns_matrix.shape
    
    # Assertions for Data Integrity (Opus 5 D5)
    first_valid = np.array([np.argmax(np.isfinite(returns_matrix[i])) for i in range(N)])
    print(f"First valid indices: {first_valid}")
    global_start = max(first_valid) + max(SMA_WINDOWS) + LOOKBACK
    print(f"Global Start Index: {global_start} ({dates[global_start].date()})")
    
    # 1. Precalculate ERC Weights
    print("Precalculating ERC Weights...")
    pool_ro = ['SPY', 'QQQ']
    pool_roff = ['GLD', 'TLT']
    
    idx_ro = [ASSETS.index(a) for a in pool_ro]
    idx_roff = [ASSETS.index(a) for a in pool_roff]
    
    w_ro = calculate_dynamic_erc_weights(returns_matrix, idx_ro, lookback=LOOKBACK)
    w_roff = calculate_dynamic_erc_weights(returns_matrix, idx_roff, lookback=LOOKBACK)
    
    # 2. Ensemble SMA Signal
    print("Ensembling SMAs...")
    spy_idx = ASSETS.index('SPY')
    spy_close = pd.Series(closes_matrix[spy_idx])
    
    signals = []
    for w in SMA_WINDOWS:
        sma = spy_close.rolling(w).mean()
        # 1 if SPY > SMA, else 0
        signals.append((spy_close > sma).astype(float))
        
    # sum of signals gives a score 0-5. 
    # pct_ro is the blend ratio: 5/5 = 100% RO, 0/5 = 0% RO
    pct_ro = sum(signals) / len(SMA_WINDOWS)
    pct_ro = pct_ro.values
    
    # Shift signal by 1 day (Opus 5 D1)
    pct_ro_shifted = np.zeros(T)
    pct_ro_shifted[1:] = pct_ro[:-1]
    pct_ro_shifted[:global_start] = 0.0 # burn-in
    
    # 3. Blend Target Weights
    W_target = np.zeros((N, T))
    for i, a_idx in enumerate(idx_ro):
        W_target[a_idx, :] += pct_ro_shifted * w_ro[i, :]
    for i, a_idx in enumerate(idx_roff):
        W_target[a_idx, :] += (1.0 - pct_ro_shifted) * w_roff[i, :]
        
    # 4. Apply Volatility Targeting & Costs
    R = np.where(np.isfinite(returns_matrix), returns_matrix, 0.0)
    
    # We need trailing vol of the pools to target correctly (Opus 5 D6)
    # Vol of RO pool
    r_ro = np.einsum('it,it->t', w_ro, R)
    vol_ro = pd.Series(r_ro).rolling(20).std().shift(1).values * np.sqrt(252)
    # Vol of ROFF pool
    r_roff = np.einsum('it,it->t', w_roff, R)
    vol_roff = pd.Series(r_roff).rolling(20).std().shift(1).values * np.sqrt(252)
    
    # Blend the trailing vols (approximation of forward vol)
    sig = pct_ro_shifted * np.nan_to_num(vol_ro, nan=0.15) + (1.0 - pct_ro_shifted) * np.nan_to_num(vol_roff, nan=0.10)
    sig = np.where(sig > 0, sig, TARGET_VOL)
    
    # Compute Leverage
    lev = np.clip(TARGET_VOL / sig, 0.0, MAX_LEV)
    
    # True Levered Weights
    L_target = W_target * lev
    
    # Calculate Gross Return of the unlevered portfolio
    r_gross = np.einsum('it,it->t', W_target, R)
    
    # Transaction Costs on Levered Notional (Opus 5 D3)
    cost_bps = np.array([BPS_COSTS[a] for a in ASSETS])
    L_diff = np.abs(np.diff(L_target, axis=1, prepend=0))
    turnover_costs = (L_diff * (cost_bps[:, None] / 10000.0)).sum(axis=0)
    
    # Financing & Cash Yield (Opus 5 D2)
    financing_costs = np.maximum(lev - 1.0, 0.0) * (rf_daily + FINANCING_SPREAD)
    cash_yield = np.maximum(1.0 - lev, 0.0) * rf_daily
    
    # Net Portfolio Return
    r_net = lev * r_gross + cash_yield - financing_costs - turnover_costs
    
    # 5. Evaluate Performance
    eval_ret = r_net[global_start:]
    eval_dates = dates[global_start:]
    eval_rf = rf_daily[global_start:]
    
    equity = np.cumprod(1.0 + eval_ret)
    cagr = equity[-1] ** (252 / len(eval_ret)) - 1.0
    
    ex_ret = eval_ret - eval_rf
    ann_vol = np.std(ex_ret, ddof=1) * np.sqrt(252)
    sharpe = np.mean(ex_ret) * 252 / ann_vol
    
    dd = equity / np.maximum.accumulate(equity) - 1.0
    mdd = dd.min()
    
    # Benchmark SPY
    spy_ret = R[spy_idx, global_start:]
    spy_eq = np.cumprod(1.0 + spy_ret)
    spy_cagr = spy_eq[-1] ** (252 / len(spy_ret)) - 1.0
    spy_ex = spy_ret - eval_rf
    spy_vol = np.std(spy_ex, ddof=1) * np.sqrt(252)
    spy_sharpe = np.mean(spy_ex) * 252 / spy_vol
    spy_mdd = (spy_eq / np.maximum.accumulate(spy_eq) - 1.0).min()
    
    print("\n=== FINAL V14 RESULTS ===")
    print(f"Eval Window: {eval_dates[0].date()} to {eval_dates[-1].date()} ({len(eval_ret)} days)")
    print(f"CAGR:   {cagr:.2%} (SPY: {spy_cagr:.2%})")
    print(f"Sharpe: {sharpe:.2f} (SPY: {spy_sharpe:.2f})")
    print(f"MDD:    {mdd:.2%} (SPY: {spy_mdd:.2%})")
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(eval_dates, equity, label=f'V14 Ensemble (SR: {sharpe:.2f})')
    plt.plot(eval_dates, spy_eq, label=f'SPY (SR: {spy_sharpe:.2f})', alpha=0.7)
    plt.yscale('log')
    plt.title('V14 Master Ensemble vs SPY (Log Scale)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(DATA_DIR, "opus14_v14_equity.png"))
    print(f"Saved plot to {DATA_DIR}/opus14_v14_equity.png")

if __name__ == "__main__":
    main()
