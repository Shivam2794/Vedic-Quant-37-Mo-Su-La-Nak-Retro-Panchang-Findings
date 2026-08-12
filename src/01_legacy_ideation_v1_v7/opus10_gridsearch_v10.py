import os
import numpy as np
import pandas as pd
from opus10_erc_optimizer_v10 import calculate_dynamic_erc_weights

def load_v9_matrices(data_dir):
    """
    Loads all V9 signal matrices and returns.
    """
    print(f"Loading V9 matrices from {data_dir}...")
    assets = ['BTC-USD', 'GLD', 'QQQ', 'SPY', 'TLT', 'TQQQ', 'UPRO']
    
    # Load dates
    dates = np.load(os.path.join(data_dir, 'dates.npy'))
    
    # Load returns
    frozen_df = pd.read_parquet(os.path.join(data_dir, 'frozen_universe_data.parquet'))
    
    # Restructure returns into (N_assets, T) array
    returns = []
    signals = {}
    
    for ticker in assets:
        ticker_df = frozen_df.xs(ticker, level='Ticker')
        ticker_df = ticker_df.reindex(dates)
        
        # Calculate daily log returns based on Adj Close
        ret = np.log(ticker_df['Adj Close'] / ticker_df['Adj Close'].shift(1)).fillna(0).values
        returns.append(ret)
        
        # sig_data = np.load(os.path.join(data_dir, f'{ticker}_signals_v9.npz'))
        # We only need returns for the ERC optimization in this test.
        
    return dates, np.array(returns), assets

def run_discord_alpha_gridsearch(data_dir):
    """
    Implements the 200MA + Leverage Switching strategy as discussed in the Skool Discord.
    """
    dates, returns_matrix, assets = load_v9_matrices(data_dir)
    
    # Get SPY 200MA signal
    spy_idx = assets.index('SPY')
    # Find the parameter row corresponding to SMA200
    # In V9, SMA family has 'window' parameter. 
    # For now, let's just manually construct the 200MA for SPY
    frozen_df = pd.read_parquet(os.path.join(data_dir, 'frozen_universe_data.parquet'))
    spy_df = frozen_df.xs('SPY', level='Ticker').reindex(dates)
    spy_close = spy_df['Adj Close'].values
    spy_sma200 = pd.Series(spy_close).rolling(window=200).mean().values
    
    # Regime: 1 if SPY > 200MA, 0 otherwise
    regime = (spy_close > spy_sma200).astype(int)
    
    # The Strategy: 
    # If Regime == 1 (Bull): 50% TQQQ, 50% UPRO (or QQQ/SPY leveraged)
    # If Regime == 0 (Bear): 50% GLD, 50% TLT
    
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
            
    # Calculate ERC weights dynamically based on a 60-day lookback
    print("Calculating ERC weights...")
    weights = calculate_dynamic_erc_weights(returns_matrix, positions, lookback=60)
    
    # Compute Portfolio Returns
    # Weight at time t-1 * return at time t
    port_returns = np.zeros(T)
    for t in range(1, T):
        port_returns[t] = np.sum(weights[:, t-1] * returns_matrix[:, t])
        
    cum_returns = np.exp(np.cumsum(port_returns))
    
    # Stats
    total_return = cum_returns[-1]
    annualized_return = total_return ** (252 / T) - 1
    
    daily_vol = np.std(port_returns)
    annualized_vol = daily_vol * np.sqrt(252)
    
    sharpe = annualized_return / annualized_vol if annualized_vol > 0 else 0
    
    print(f"--- Discord Alpha: Leverage for the Long Run (ERC Weighted) ---")
    print(f"Total Return: {total_return:.2f}x")
    print(f"CAGR: {annualized_return*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    
    return dates, cum_returns

if __name__ == "__main__":
    data_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
    dates, cum_returns = run_discord_alpha_gridsearch(data_dir)
    
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.plot(dates, cum_returns, label="Discord Alpha (ERC Weighted)")
    plt.yscale('log')
    plt.title("Discord Alpha: Regime Filter + ERC Leverage Rotation")
    plt.grid(True)
    plt.legend()
    plt.savefig("discord_alpha_equity_curve.png")
    print("Saved equity curve to discord_alpha_equity_curve.png")
