import yfinance as yf
import pandas as pd
import numpy as np

def backtest_drift_regimes():
    print("Fetching data for a basket of large-cap tech and finance stocks...")
    tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "META", "TSLA", "NVDA", "JPM", "BAC", "WFC"]
    data = yf.download(tickers, start="2015-01-01", end="2025-01-01")['Close']
    
    # Calculate daily returns
    returns = data.pct_change()
    
    # 1. Drift Regime: >60% positive days in trailing 63 days
    is_positive = (returns > 0).astype(int)
    rolling_positive_pct = is_positive.rolling(window=63).mean()
    drift_regime = (rolling_positive_pct > 0.60).astype(int)
    
    # 2. Short-term Reversal Signal: 5-day return
    return_5d = data.pct_change(5)
    # Reversal signal: If 5-day return is negative, we want to go LONG (value/reversal)
    # If 5-day return is positive, we go SHORT
    # So our position is roughly proportional to -return_5d
    # We rank the reversal signal cross-sectionally
    
    # We only activate the signal if the stock is in a drift regime
    # Position = -sign(return_5d) * drift_regime
    position = (-np.sign(return_5d)) * drift_regime
    
    # Shift position by 1 to avoid look-ahead bias
    position = position.shift(1)
    
    # Calculate strategy returns
    # Normalize positions so we are fully invested (sum of abs weights = 1)
    # To handle div by zero, replace 0 with NaN temporarily
    pos_sum = position.abs().sum(axis=1)
    pos_sum = pos_sum.replace(0, np.nan)
    weights = position.div(pos_sum, axis=0).fillna(0)
    
    strat_returns = (weights * returns).sum(axis=1)
    
    # Metrics
    cum_returns = (1 + strat_returns).cumprod()
    cagr = (cum_returns.iloc[-1] ** (252 / len(strat_returns))) - 1
    
    vol = strat_returns.std() * np.sqrt(252)
    sharpe = (cagr - 0.02) / vol if vol > 0 else 0
    
    roll_max = cum_returns.cummax()
    drawdown = (cum_returns - roll_max) / roll_max
    max_dd = drawdown.min()
    
    print("\n==========================================")
    print("BACKTEST: DRIFT REGIME + SHORT-TERM REVERSAL")
    print("==========================================")
    print(f"Total Return: {(cum_returns.iloc[-1]-1)*100:.2f}%")
    print(f"CAGR:         {cagr*100:.2f}%")
    print(f"Max Drawdown: {max_dd*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print("==========================================")

if __name__ == "__main__":
    backtest_drift_regimes()
