import os
import numpy as np
import pandas as pd
from opus10_erc_optimizer_v10 import calculate_dynamic_erc_weights
from opus10_gridsearch_v10 import load_v9_matrices

def run_discord_alpha_naive(data_dir):
    dates, returns_matrix, assets = load_v9_matrices(data_dir)
    
    spy_idx = assets.index('SPY')
    frozen_df = pd.read_parquet(os.path.join(data_dir, 'frozen_universe_data.parquet'))
    spy_df = frozen_df.xs('SPY', level='Ticker').reindex(dates)
    spy_close = spy_df['Adj Close'].values
    spy_sma200 = pd.Series(spy_close).rolling(window=200).mean().values
    
    regime = (spy_close > spy_sma200).astype(int)
    
    tqqq_idx = assets.index('TQQQ')
    upro_idx = assets.index('UPRO')
    gld_idx = assets.index('GLD')
    tlt_idx = assets.index('TLT')
    
    N, T = returns_matrix.shape
    positions = np.zeros((N, T))
    
    for t in range(200, T):
        if regime[t-1] == 1:
            positions[tqqq_idx, t] = 1
            positions[upro_idx, t] = 1
        else:
            positions[gld_idx, t] = 1
            positions[tlt_idx, t] = 1
            
    # Calculate NAIVE EQUAL weights
    weights = np.zeros((N, T))
    for t in range(T):
        n_active = np.sum(positions[:, t])
        if n_active > 0:
            weights[:, t] = positions[:, t] / n_active
            
    # Compute Portfolio Returns
    port_returns = np.zeros(T)
    for t in range(1, T):
        port_returns[t] = np.sum(weights[:, t-1] * returns_matrix[:, t])
        
    cum_returns = np.exp(np.cumsum(port_returns))
    
    total_return = cum_returns[-1]
    annualized_return = total_return ** (252 / T) - 1
    
    daily_vol = np.std(port_returns)
    annualized_vol = daily_vol * np.sqrt(252)
    
    sharpe = annualized_return / annualized_vol if annualized_vol > 0 else 0
    
    print(f"--- Discord Alpha: Leverage for the Long Run (NAIVE EQUAL WEIGHTED) ---")
    print(f"Total Return: {total_return:.2f}x")
    print(f"CAGR: {annualized_return*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")

if __name__ == "__main__":
    data_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
    run_discord_alpha_naive(data_dir)
