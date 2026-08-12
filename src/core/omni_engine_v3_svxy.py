import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_svxy_buy_hold():
    print("[*] Downloading SVXY Data...")
    df = yf.download('SVXY', start="2012-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    port_ret = returns
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    if isinstance(cagr, pd.Series): cagr = cagr.iloc[0]
    if isinstance(sharpe, pd.Series): sharpe = sharpe.iloc[0]
    if isinstance(max_dd, pd.Series): max_dd = max_dd.iloc[0]
    
    print("========================================================")
    print(f"[*] SVXY BUY AND HOLD RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_svxy_buy_hold()
