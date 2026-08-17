import yfinance as yf
import pandas as pd
import numpy as np
from hmmlearn import hmm
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def get_hmm_regimes(spy_returns):
    predictions = pd.Series(index=spy_returns.index, dtype=float)
    # Needs a minimum of 252 days to warm up
    for i in range(252, len(spy_returns)):
        model = hmm.GaussianHMM(n_components=3, covariance_type="diag", n_iter=100, random_state=42, min_covar=1e-6)
        window = spy_returns.iloc[i-252:i].values.reshape(-1, 1)
        model.fit(window)
        # Predict the hidden state of the *last* day in the window
        # Note: States are arbitrary (0,1,2). We must map them by volatility to determine which is the "Crash" state.
        
        hidden_states = model.predict(window)
        
        # Calculate the variance of each state in the window
        variances = []
        for state in range(3):
            state_returns = window[hidden_states == state]
            if len(state_returns) > 0:
                variances.append(np.var(state_returns))
            else:
                variances.append(np.inf) # Invalid state
                
        # State with highest variance is the Crash/Bear state
        crash_state = np.argmax(variances)
        
        # Current state is the last predicted state
        current_state = hidden_states[-1]
        
        # 1 if safe, 0 if crash
        if current_state == crash_state:
            predictions.iloc[i] = 0.0
        else:
            predictions.iloc[i] = 1.0
            
    return predictions

def run_hmm_svxy_arbitrage():
    print("[*] Downloading Data for HMM Volatility Arbitrage...")
    tickers = ['SPY', 'SVXY', 'SHV']
    df = yf.download(tickers, start="2012-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    
    print("[*] Fitting Rolling Hidden Markov Model (This takes a minute)...")
    spy_returns = returns['SPY']
    # Add tiny noise to prevent 0-variance singular covariance matrices in HMM
    np.random.seed(42)
    spy_returns = spy_returns + np.random.normal(0, 1e-6, len(spy_returns))
    if isinstance(spy_returns, pd.DataFrame): spy_returns = spy_returns.iloc[:, 0]
    spy_returns = spy_returns.fillna(0.0)
        
    safe_regime = get_hmm_regimes(spy_returns)
    
    weights = pd.DataFrame(0.0, index=df.index, columns=['SVXY', 'SHV'])
    
    for date in df.index:
        # Safe Regime -> Short Volatility (SVXY)
        # Crash Regime -> Cash (SHV)
        
        is_safe = safe_regime.loc[date] if date in safe_regime.index else np.nan
        
        if pd.isna(is_safe):
            weights.loc[date, 'SHV'] = 1.0
            continue
            
        if is_safe == 1.0:
            weights.loc[date, 'SVXY'] = 1.0
        else:
            weights.loc[date, 'SHV'] = 1.0

    # Prevent look-ahead bias
    weights = weights.shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Assuming SHV yields roughly 2% annually / 252 for cash days
    r_shv = 0.02 / 252
    
    svxy_r = r['SVXY']
    if isinstance(svxy_r, pd.DataFrame): svxy_r = svxy_r.iloc[:, 0]
        
    port_ret = (weights['SVXY'] * svxy_r) + (weights['SHV'] * r_shv)
    
    # Turnover calculation (daily)
    delta = weights.diff().abs().sum(axis=1).fillna(0)
    
    # Apply Brutal Slippage
    port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(port_ret)
    
    print("========================================================")
    print(f"[*] HMM VOLATILITY ARBITRAGE RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    bm_cagr = (1 + spy_returns).prod() ** (252 / len(spy_returns)) - 1
    bm_sharpe = np.sqrt(252) * spy_returns.mean() / (spy_returns.std() + 1e-9)
    bm_max_dd = (((1 + spy_returns).cumprod() - (1 + spy_returns).cumprod().cummax()) / (1 + spy_returns).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_hmm_svxy_arbitrage()
