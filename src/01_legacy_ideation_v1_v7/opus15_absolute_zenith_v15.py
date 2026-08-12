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
NO_TRADE_BAND = 0.005         # 0.5% weight deviation required to trade

SMA_WINDOWS = [50, 100, 150, 200, 250]
LOOKBACK = 60 # ERC covariance lookback

def load_v15_matrices():
    print(f"Loading matrices from {DATA_DIR}...")
    frozen_df = pd.read_parquet(os.path.join(DATA_DIR, "frozen_universe_data.parquet"))
    rates_df = pd.read_parquet(os.path.join(DATA_DIR, "frozen_rates_data.parquet"))
    
    dates = frozen_df.index.get_level_values('Date').unique().sort_values()
    # Align rates to dates
    rates_df = rates_df.reindex(dates).ffill().fillna(0)
    rf_daily = rates_df['rf_daily'].values
    
    T = len(dates)
    N = len(ASSETS)
    
    returns_matrix = np.full((N, T), np.nan)
    prices_matrix = np.full((N, T), np.nan)
    
    for i, asset in enumerate(ASSETS):
        try:
            asset_df = frozen_df.xs(asset, level='Ticker')
            asset_df = asset_df.reindex(dates)
            prices_matrix[i, :] = asset_df['Adj Close'].values  # Using Adj Close for signals too! (V14-S4)
            returns_matrix[i, :] = asset_df['Adj Close'].pct_change().values
        except KeyError:
            pass

    return returns_matrix, prices_matrix, rf_daily, dates

def get_multi_horizon_vol(returns_array):
    """V14-S2: Multi-Horizon Volatility Estimator (40% 20d, 40% 60d, 20% 120d)"""
    df = pd.Series(returns_array)
    vol_20 = df.rolling(20).std().shift(1).values * np.sqrt(252)
    vol_60 = df.rolling(60).std().shift(1).values * np.sqrt(252)
    vol_120 = df.rolling(120).std().shift(1).values * np.sqrt(252)
    
    blended_vol = 0.4 * np.nan_to_num(vol_20, nan=0.15) + \
                  0.4 * np.nan_to_num(vol_60, nan=0.15) + \
                  0.2 * np.nan_to_num(vol_120, nan=0.15)
    return blended_vol

def main():
    returns_matrix, prices_matrix, rf_daily, dates = load_v15_matrices()
    if returns_matrix is None: return
    
    N, T = returns_matrix.shape
    
    # Assertions for Data Integrity
    first_valid = np.array([np.argmax(np.isfinite(returns_matrix[i])) for i in range(N)])
    print(f"First valid indices: {first_valid}")
    global_start = max(first_valid) + max(SMA_WINDOWS) + max(LOOKBACK, 252) # 252 needed for Absolute Momentum
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
    spy_price = pd.Series(prices_matrix[spy_idx])
    
    signals = []
    for w in SMA_WINDOWS:
        sma = spy_price.rolling(w).mean()
        signals.append((spy_price > sma).astype(float))
        
    pct_ro = sum(signals) / len(SMA_WINDOWS)
    pct_ro = pct_ro.values
    
    # Shift signal by 1 day
    pct_ro_shifted = np.zeros(T)
    pct_ro_shifted[1:] = pct_ro[:-1]
    pct_ro_shifted[:global_start] = 0.0 
    pct_roff_shifted = 1.0 - pct_ro_shifted
    
    # 3. ABSOLUTE MOMENTUM GATE (Loss #2)
    # Any defensive asset failing its own 12-month absolute momentum test gets its weight reallocated to CASH.
    print("Applying Absolute Momentum Gates...")
    rf_cum_252 = pd.Series(rf_daily).rolling(252).sum().shift(1).values
    
    w_roff_gated = w_roff.copy()
    for i, a_idx in enumerate(idx_roff):
        asset_mom_252 = pd.Series(prices_matrix[a_idx]).pct_change(252).shift(1).values
        # If momentum < rf_cum, gate to 0
        gate = (asset_mom_252 > rf_cum_252).astype(float)
        w_roff_gated[i, :] = w_roff[i, :] * np.nan_to_num(gate, nan=1.0)
    
    # 4. Blend Target Weights
    W_target = np.zeros((N, T))
    for i, a_idx in enumerate(idx_ro):
        W_target[a_idx, :] += pct_ro_shifted * w_ro[i, :]
    for i, a_idx in enumerate(idx_roff):
        W_target[a_idx, :] += pct_roff_shifted * w_roff_gated[i, :]
        
    # 5. Volatility Targeting & Costs
    R = np.where(np.isfinite(returns_matrix), returns_matrix, 0.0)
    
    # Pool Vols (V14-S2 Multi-Horizon)
    r_ro = np.einsum('it,it->t', w_ro, R)
    vol_ro = get_multi_horizon_vol(r_ro)
    
    r_roff_gated = np.einsum('it,it->t', w_roff_gated, R)
    vol_roff = get_multi_horizon_vol(r_roff_gated)
    
    # Quadratic Volatility Blending (V14-S5)
    # Compute rolling correlation between RO and ROFF pools
    cov_ro_roff = pd.Series(r_ro).rolling(60).cov(pd.Series(r_roff_gated)).shift(1).values * 252
    var_ro = vol_ro**2
    var_roff = vol_roff**2
    
    a = pct_ro_shifted
    b = pct_roff_shifted
    
    var_blend = (a**2)*var_ro + (b**2)*var_roff + 2*a*b*np.nan_to_num(cov_ro_roff, nan=0.0)
    sig = np.sqrt(np.maximum(var_blend, 0.0001))
    sig = np.where(sig > 0, sig, TARGET_VOL)
    
    # Compute Leverage
    lev = np.clip(TARGET_VOL / sig, 0.0, MAX_LEV)
    
    # True Levered Target Weights
    L_target = W_target * lev
    
    # No-Trade Bands (V14-S3)
    L_held = np.zeros((N, T))
    current_held = np.zeros(N)
    for t in range(global_start, T):
        target = L_target[:, t]
        # Only update if deviation > NO_TRADE_BAND
        diff = np.abs(target - current_held)
        update_mask = diff > NO_TRADE_BAND
        current_held = np.where(update_mask, target, current_held)
        L_held[:, t] = current_held
        
    # Gross Return of the actually held portfolio
    r_gross = np.einsum('it,it->t', L_held, R)
    
    # Transaction Costs on Levered Notional
    cost_bps = np.array([BPS_COSTS[a] for a in ASSETS])
    L_diff = np.abs(np.diff(L_held, axis=1, prepend=0))
    turnover_costs = (L_diff * (cost_bps[:, None] / 10000.0)).sum(axis=0)
    
    # Total Leverage held
    lev_held = L_held.sum(axis=0)
    
    # Financing & Cash Yield (V14-S1 Real Rates)
    financing_costs = np.maximum(lev_held - 1.0, 0.0) * (rf_daily + FINANCING_SPREAD)
    cash_yield = np.maximum(1.0 - lev_held, 0.0) * rf_daily
    
    # Net Portfolio Return
    r_net = r_gross + cash_yield - financing_costs - turnover_costs
    
    # 6. Evaluate Performance
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
    
    print("\n=== V15 ABSOLUTE ZENITH RESULTS ===")
    print(f"Eval Window: {eval_dates[0].date()} to {eval_dates[-1].date()} ({len(eval_ret)} days)")
    print(f"CAGR:   {cagr:.2%} (SPY: {spy_cagr:.2%})")
    print(f"Sharpe: {sharpe:.2f} (SPY: {spy_sharpe:.2f})")
    print(f"MDD:    {mdd:.2%} (SPY: {spy_mdd:.2%})")
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(eval_dates, equity, label=f'V15 Zenith (SR: {sharpe:.2f})')
    plt.plot(eval_dates, spy_eq, label=f'SPY (SR: {spy_sharpe:.2f})', alpha=0.7)
    plt.yscale('log')
    plt.title('V15 Absolute Zenith vs SPY (Log Scale)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(DATA_DIR, "opus15_v15_equity.png"))
    print(f"Saved plot to {DATA_DIR}/opus15_v15_equity.png")

if __name__ == "__main__":
    main()
