import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
RETURNS_FILE = os.path.join(IN_DIR, 'opus8_portfolio_returns.csv')
OUT_IMG = os.path.join(IN_DIR, 'opus8_equity_curve_v4.png')

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
    port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    if port_vol == 0: return 1e9
    
    marginal_contrib = np.dot(cov_matrix, weights) / port_vol
    risk_contrib = weights * marginal_contrib
    
    target_risk = port_vol / len(weights)
    return np.sum(np.square(risk_contrib - target_risk))

def optimize_weights_erc(cov_matrix):
    n_assets = len(cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    bounds = tuple((0.01, 0.40) for _ in range(n_assets))
    init_guess = [1.0 / n_assets] * n_assets
    
    result = minimize(risk_parity_objective, init_guess, args=(cov_matrix,), method='SLSQP', bounds=bounds, constraints=constraints)
    if not result.success:
        return np.array(init_guess)
    return result.x

def optimize_portfolio():
    if not os.path.exists(RETURNS_FILE):
        print(f"Returns file not found at {RETURNS_FILE}")
        return
        
    df = pd.read_csv(RETURNS_FILE, index_col=0, parse_dates=True)
    df = df[TICKERS]
    # Drop rows where ALL tickers are NaN (e.g. before backtest start)
    df = df.dropna(how='all')
    
    print(f"Optimizing over {len(df)} trading days (from {df.index[0].date()} to {df.index[-1].date()})")
    
    lookback = 252
    rebalance_freq = 21
    tc_bps = 0.0005 
    
    portfolio_returns = np.zeros(len(df))
    
    # We dynamically size weights over ALL 7 assets. If an asset is NaN, its weight is 0.
    current_weights = np.zeros(len(TICKERS))
    
    for i in range(len(df)):
        ret_today = df.iloc[i].values
        
        # Valid assets today
        valid_today = ~np.isnan(ret_today)
        
        # Zero out returns for NaN assets
        safe_ret_today = np.where(valid_today, ret_today, 0.0)
        
        # 1. Update Drifted Weights based on today's return
        port_ret_today = np.dot(safe_ret_today, current_weights)
        portfolio_returns[i] = port_ret_today
        
        # 2. Rebalance check at end of day
        if i >= lookback and i % rebalance_freq == 0:
            window = df.iloc[i-lookback:i]
            
            # Find assets that have valid data for the ENTIRE lookback window
            valid_assets_mask = window.notna().all().values
            n_valid = np.sum(valid_assets_mask)
            
            target_weights = np.zeros(len(TICKERS))
            
            if n_valid > 0:
                valid_window = window.iloc[:, valid_assets_mask]
                cov_matrix = valid_window.cov().values * 252
                valid_target_weights = optimize_weights_erc(cov_matrix)
                target_weights[valid_assets_mask] = valid_target_weights
            
            # Calculate turnover from drifted weights to target weights
            drifted_weights = current_weights.copy()
            if (1 + port_ret_today) > 0:
                drifted_weights = current_weights * (1 + safe_ret_today) / (1 + port_ret_today)
            
            turnover = np.sum(np.abs(target_weights - drifted_weights))
            cost = turnover * tc_bps
            
            # Subtract transaction cost from today's portfolio return
            portfolio_returns[i] -= cost
            
            # Update current weights to target
            current_weights = target_weights
        else:
            # Just drift the weights
            if (1 + port_ret_today) > 0:
                current_weights = current_weights * (1 + safe_ret_today) / (1 + port_ret_today)
                
    port_series = pd.Series(portfolio_returns, index=df.index)
    tot_ret, max_dd, sharpe, win_rate, cum_ret, cagr = calc_metrics(port_series)
    
    print("\n=========================================")
    print("OPUS-8 ABSOLUTION v4: DYNAMIC WFO TRUE RISK PARITY")
    print("=========================================")
    print(f"Final Weights:")
    for i, ticker in enumerate(TICKERS):
        print(f"{ticker:10s} : {current_weights[i]*100:.2f}%")
        
    print("\n--- COMPOSITE PORTFOLIO METRICS ---")
    print(f"Total Return : {tot_ret*100:.2f}%")
    print(f"CAGR         : {cagr*100:.2f}%")
    print(f"Max Drawdown : {max_dd*100:.2f}%")
    print(f"Sharpe Ratio : {sharpe:.4f}")
    print(f"Win Rate     : {win_rate*100:.2f}%")
    
    # Dynamic Equal Weight Benchmark (rebalances to valid assets)
    eq_returns = np.zeros(len(df))
    for i in range(len(df)):
        ret_today = df.iloc[i].values
        valid_today = ~np.isnan(ret_today)
        safe_ret_today = np.where(valid_today, ret_today, 0.0)
        n_valid = np.sum(valid_today)
        if n_valid > 0:
            eq_returns[i] = np.sum(safe_ret_today) / n_valid
            
    eq_tot, eq_dd, eq_sharpe, eq_wr, eq_cum, eq_cagr = calc_metrics(pd.Series(eq_returns, index=df.index))
    print("\n--- EQUAL WEIGHT BENCHMARK ---")
    print(f"CAGR         : {eq_cagr*100:.2f}%")
    print(f"Sharpe Ratio : {eq_sharpe:.4f}")
    print(f"Max Drawdown : {eq_dd*100:.2f}%")
    
    plt.figure(figsize=(12, 6))
    plt.plot(cum_ret, label=f'True Risk Parity WFO (Sharpe {sharpe:.2f})', color='green', linewidth=2)
    plt.plot(eq_cum, label=f'Equal Weight Benchmark (Sharpe {eq_sharpe:.2f})', color='gray', linestyle='--')
    plt.yscale('log')
    plt.title('OPUS-8 Absolution v4: True Risk Parity with Dynamic Universe')
    plt.ylabel('Cumulative Return Multiplier')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_IMG, dpi=150)
    print(f"\nEquity curve saved to {OUT_IMG}")

if __name__ == '__main__':
    optimize_portfolio()
