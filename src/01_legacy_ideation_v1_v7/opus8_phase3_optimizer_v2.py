import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import yfinance as yf

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
RETURNS_FILE = os.path.join(IN_DIR, 'opus8_portfolio_returns.csv')
OUT_IMG = os.path.join(IN_DIR, 'opus8_equity_curve_v5.png')

TICKERS = ['SPY', 'QQQ', 'TQQQ', 'UPRO', 'TLT', 'GLD', 'BTC-USD']

def calc_metrics(returns):
    cum_ret = np.exp(np.log1p(returns).cumsum())
    total_ret = cum_ret.iloc[-1] - 1
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    
    years = len(returns) / 252.0
    cagr = (cum_ret.iloc[-1]) ** (1.0 / years) - 1.0 if years > 0 else 0.0
    
    ann_ret = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0
    
    win_rate = (returns > 0).sum() / (returns != 0).sum()
    
    return total_ret, max_dd, sharpe, win_rate, cum_ret, cagr

def risk_parity_objective(weights, cov_matrix):
    port_var = np.dot(weights.T, np.dot(cov_matrix, weights))
    port_vol = np.sqrt(port_var)
    if port_vol == 0: return 1e9
    
    marginal_contrib = np.dot(cov_matrix, weights) / port_vol
    risk_contrib = weights * marginal_contrib
    
    target_risk = port_vol / len(weights)
    # Normalize by port_vol^2 as suggested by Opus 5 to fix SLSQP convergence
    return np.sum(np.square(risk_contrib - target_risk)) / (port_var + 1e-8)

def optimize_weights_erc(cov_matrix):
    n_assets = len(cov_matrix)
    
    # FATAL FLAW #3 (F4) FIXED: Inject tiny epsilon to variance to prevent cash explosion
    epsilon = np.eye(n_assets) * 1e-6
    cov_matrix = cov_matrix + epsilon
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    # If n_assets < 3, a 0.40 max bound means they can't sum to 1.0! 
    # Relax bound dynamically.
    max_bound = max(0.40, 1.0 / n_assets + 0.01)
    bounds = tuple((0.01, max_bound) for _ in range(n_assets))
    init_guess = [1.0 / n_assets] * n_assets
    
    result = minimize(risk_parity_objective, init_guess, args=(cov_matrix,), method='SLSQP', bounds=bounds, constraints=constraints, tol=1e-8)
    if not result.success:
        return np.array(init_guess)
    return result.x

def walk_forward_optimizer(df, tc_bps=0.0005, lookback=252, rebalance_freq=21):
    portfolio_returns = np.zeros(len(df))
    current_weights = np.zeros(len(TICKERS))
    
    for i in range(len(df)):
        ret_today = df.iloc[i].values
        valid_today = ~np.isnan(ret_today)
        safe_ret_today = np.where(valid_today, ret_today, 0.0)
        
        port_ret_today = np.dot(safe_ret_today, current_weights)
        portfolio_returns[i] = port_ret_today
        
        if i >= lookback and i % rebalance_freq == 0:
            window = df.iloc[i-lookback:i]
            
            # Using min_periods=lookback//2 to avoid NaNing an entire year for 1 missing day
            valid_assets_mask = (window.notna().sum() >= lookback * 0.9).values
            n_valid = np.sum(valid_assets_mask)
            
            target_weights = np.zeros(len(TICKERS))
            
            if n_valid > 0:
                valid_window = window.iloc[:, valid_assets_mask]
                cov_matrix = valid_window.cov().values * 252
                valid_target_weights = optimize_weights_erc(cov_matrix)
                target_weights[valid_assets_mask] = valid_target_weights
            
            drifted_weights = current_weights.copy()
            if (1 + port_ret_today) > 0:
                drifted_weights = current_weights * (1 + safe_ret_today) / (1 + port_ret_today)
            
            turnover = np.sum(np.abs(target_weights - drifted_weights))
            cost = turnover * tc_bps
            
            portfolio_returns[i] -= cost
            current_weights = target_weights
        else:
            if (1 + port_ret_today) > 0:
                current_weights = current_weights * (1 + safe_ret_today) / (1 + port_ret_today)
                
    return portfolio_returns, current_weights

def optimize_portfolio():
    if not os.path.exists(RETURNS_FILE):
        print(f"Returns file not found at {RETURNS_FILE}")
        return
        
    df_algo = pd.read_csv(RETURNS_FILE, index_col=0, parse_dates=True)
    df_algo = df_algo[TICKERS]
    df_algo = df_algo.dropna(how='all')
    
    print(f"Optimizing ALGORITHMIC OVERLAY over {len(df_algo)} days...")
    algo_returns, algo_final_weights = walk_forward_optimizer(df_algo)
    
    # Now compute the TRUE STATIC ERC BENCHMARK (no signals, just buy and hold universe)
    print(f"Optimizing STATIC ERC BENCHMARK (No Signals) over {len(df_algo)} days...")
    
    df_dates = df_algo.index
    bnh_dict = {}
    for ticker in TICKERS:
        raw_df = yf.download([ticker], start='1999-01-01', progress=False, auto_adjust=True)
        if isinstance(raw_df.columns, pd.MultiIndex):
            orig_close = raw_df['Close'][ticker].reindex(df_dates).values.flatten()
        else:
            orig_close = raw_df['Close'].reindex(df_dates).values.flatten()
        close = pd.Series(orig_close).ffill().bfill().values
        rets = np.zeros(len(df_dates))
        rets[1:] = np.diff(close) / close[:-1]
        rets[np.isnan(orig_close)] = np.nan 
        bnh_dict[ticker] = rets
        
    df_bnh = pd.DataFrame(bnh_dict, index=df_dates)
    bnh_returns, bnh_final_weights = walk_forward_optimizer(df_bnh)
    
    # Calculate Equal Weight Benchmark as a 3rd comparison
    eq_returns = np.zeros(len(df_bnh))
    for i in range(len(df_bnh)):
        ret_today = df_bnh.iloc[i].values
        valid_today = ~np.isnan(ret_today)
        safe_ret_today = np.where(valid_today, ret_today, 0.0)
        n_valid = np.sum(valid_today)
        if n_valid > 0: eq_returns[i] = np.sum(safe_ret_today) / n_valid
            
    # Print Metrics
    port_series = pd.Series(algo_returns, index=df_algo.index)
    tot_ret, max_dd, sharpe, win_rate, cum_ret, cagr = calc_metrics(port_series)
    
    bnh_series = pd.Series(bnh_returns, index=df_bnh.index)
    bnh_tot, bnh_dd, bnh_sharpe, bnh_wr, bnh_cum, bnh_cagr = calc_metrics(bnh_series)
    
    eq_tot, eq_dd, eq_sharpe, eq_wr, eq_cum, eq_cagr = calc_metrics(pd.Series(eq_returns, index=df_bnh.index))

    print("\n=========================================")
    print("OPUS-8 ABSOLUTION v5: TRUE RISK PARITY WFO")
    print("=========================================")
    print(f"Final Algorithmic Weights:")
    for i, ticker in enumerate(TICKERS):
        print(f"{ticker:10s} : {algo_final_weights[i]*100:.2f}%")
        
    print("\n--- 1. ALGORITHMIC WFO OVERLAY ---")
    print(f"Total Return : {tot_ret*100:.2f}%")
    print(f"CAGR         : {cagr*100:.2f}%")
    print(f"Max Drawdown : {max_dd*100:.2f}%")
    print(f"Sharpe Ratio : {sharpe:.4f}")
    
    print("\n--- 2. STATIC ERC BENCHMARK (NULL HYPOTHESIS) ---")
    print(f"CAGR         : {bnh_cagr*100:.2f}%")
    print(f"Sharpe Ratio : {bnh_sharpe:.4f}")
    print(f"Max Drawdown : {bnh_dd*100:.2f}%")
    
    print("\n--- 3. EQUAL WEIGHT BENCHMARK ---")
    print(f"CAGR         : {eq_cagr*100:.2f}%")
    print(f"Sharpe Ratio : {eq_sharpe:.4f}")
    print(f"Max Drawdown : {eq_dd*100:.2f}%")
    
    plt.figure(figsize=(12, 6))
    plt.plot(cum_ret, label=f'Algorithmic WFO (Sharpe {sharpe:.2f})', color='green', linewidth=2)
    plt.plot(bnh_cum, label=f'Static ERC Benchmark (Sharpe {bnh_sharpe:.2f})', color='blue', linestyle='--')
    plt.plot(eq_cum, label=f'Equal Weight (Sharpe {eq_sharpe:.2f})', color='gray', linestyle=':')
    plt.yscale('log')
    plt.title('OPUS-8 Absolution v5: Algorithmic Overlay vs. True Static Benchmarks')
    plt.ylabel('Cumulative Return Multiplier')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_IMG, dpi=150)
    print(f"\nEquity curve saved to {OUT_IMG}")

if __name__ == '__main__':
    optimize_portfolio()
