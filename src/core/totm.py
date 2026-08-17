import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_totm():
    print(f"[*] Downloading Data for Turn of the Month Strategy...")
    df = yf.download(['SPY', '^IRX'], start="2000-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    df = df[df.index.dayofweek < 5] # Strict business days
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    valid_idx = returns.index[20:]
    
    # Calculate days to month end
    # Get the last business day of each month
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    weights = pd.Series(0.0, index=df.index)
    
    for month_end in month_ends:
        # Find the index position of the month_end
        idx = df.index.get_loc(month_end)
        
        # Buy 4 days before, sell 3 days after
        start_idx = max(0, idx - 4)
        end_idx = min(len(df) - 1, idx + 3)
        
        for i in range(start_idx, end_idx + 1):
            weights.iloc[i] = 1.0
            
    # Shift by 1 to avoid lookahead
    # Wait, Turn of the Month is known in advance. We don't need to shift if we calculate the calendar dates!
    # But to be safe in the execution engine, we shift by 1.
    weights = weights.shift(1).fillna(0.0)
    
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]['SPY']
    cy = daily_cash_yield.loc[valid_idx]
    
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    delta = weights.diff().abs().fillna(0)
    slip = delta * (3 / 10000) # 3bps slippage for SPY
    
    # Exact vector math
    a_ret = weights * r
    cash = 1.0 - weights
    c_ret = cash * cy
    
    final_port_ret = a_ret + c_ret - slip
    
    excess = final_port_ret - cy
    std = final_port_ret.std()
    
    sharpe = np.sqrt(252) * excess.mean() / std
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    cum = (1 + final_port_ret).cumprod()
    max_dd = ((cum - cum.cummax()) / cum.cummax()).min()
    
    print("========================================================")
    print(f"[*] TURN OF THE MONTH (SPY)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_totm()
