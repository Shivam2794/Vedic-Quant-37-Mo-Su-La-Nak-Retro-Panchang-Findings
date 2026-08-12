import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

def calc_metrics(returns, risk_free=0.02):
    if len(returns) == 0:
        return 0, 0, 0
    cum_ret = (1 + returns).cumprod()
    cagr = (cum_ret.iloc[-1] ** (252 / len(returns))) - 1
    
    vol = returns.std() * np.sqrt(252)
    sharpe = (cagr - risk_free) / vol if vol > 0 else 0
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    return cagr, max_dd, sharpe

def run_strategy_28():
    print("\n[*] Running Strategy 28: Yield Curve Inversion Rotation...")
    # ^TNX = 10Y Treasury Yield, ^IRX = 13-week Treasury Bill Yield
    tickers = ["QQQ", "XLP", "TLT", "^TNX", "^IRX"]
    data = yf.download(tickers, start="2010-01-01", end="2024-01-01", progress=False, auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close'].dropna()
    else:
        close_data = data.dropna()
        
    returns = close_data.pct_change()
    
    # Calculate 10Y - 3M Spread
    # Note: Yahoo returns yields directly as values like 4.5 for 4.5%
    spread = close_data['^TNX'] - close_data['^IRX']
    
    # Strategy Logic
    weight_qqq = pd.Series(0.0, index=close_data.index)
    weight_xlp = pd.Series(0.0, index=close_data.index)
    weight_tlt = pd.Series(0.0, index=close_data.index)
    
    # Inverted = Spread < 0
    inverted = (spread < 0).astype(bool)
    
    # Delay the signal slightly to prevent lookahead
    inverted = inverted.shift(1).fillna(False).astype(bool)
    
    # Normal curve: 100% QQQ
    weight_qqq[~inverted] = 1.0
    
    # Inverted curve: 50% XLP (Defensive), 50% TLT (Treasuries)
    weight_xlp[inverted] = 0.5
    weight_tlt[inverted] = 0.5
    
    strat_returns = (weight_qqq * returns['QQQ']) + (weight_xlp * returns['XLP']) + (weight_tlt * returns['TLT'])
    
    # Transaction Costs
    turnover = weight_qqq.diff().abs() + weight_xlp.diff().abs() + weight_tlt.diff().abs()
    turnover = turnover / 2.0
    strat_returns = strat_returns - (turnover * 0.0010)
    
    cagr, max_dd, sharpe = calc_metrics(strat_returns)
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(returns['QQQ'])
    
    print(f"  Benchmark (QQQ): CAGR: {bm_cagr*100:.2f}% | Max DD: {bm_dd*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print(f"  Yield Curve Strat: CAGR: {cagr*100:.2f}% | Max DD: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")


def run_strategy_44():
    print("\n[*] Running Strategy 44: Low Volatility Anomaly (Dow 30)...")
    dow_30 = ['AAPL', 'MSFT', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'CVX', 
              'MRK', 'KO', 'DIS', 'CSCO', 'MCD', 'BA', 'CRM', 'VZ', 'NKE', 'HON', 
              'IBM', 'AMGN', 'AXP', 'GS', 'CAT', 'MMM', 'INTC', 'TRV', 'WBA', 'DOW']
    
    # WBA and DOW have different inception dates, handle missing data
    data = yf.download(dow_30, start="2010-01-01", end="2024-01-01", progress=False, auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close'].dropna(axis=1, how='any') # Drop stocks that don't exist for full period
    else:
        close_data = data.dropna(axis=1, how='any')
        
    returns = close_data.pct_change()
    
    # 60-day rolling volatility
    rolling_vol = returns.rolling(60).std()
    
    # Shift to prevent lookahead bias
    rolling_vol = rolling_vol.shift(1).dropna(how='all')
    valid_returns = returns.loc[rolling_vol.index]
    
    strat_returns = pd.Series(0.0, index=valid_returns.index)
    turnover_series = pd.Series(0.0, index=valid_returns.index)
    
    # Monthly rebalance to save compute in python loop
    # We will compute weights every day but only change them end of month
    weights_df = pd.DataFrame(0.0, index=valid_returns.index, columns=valid_returns.columns)
    
    for i, date in enumerate(rolling_vol.index):
        if i % 21 != 0: # Roughly monthly
            if i > 0:
                weights_df.iloc[i] = weights_df.iloc[i-1]
            continue
            
        day_vols = rolling_vol.loc[date].dropna()
        if len(day_vols) < 10:
            continue
            
        day_vols_sorted = day_vols.sort_values()
        low_vol_5 = day_vols_sorted.head(5).index
        high_vol_5 = day_vols_sorted.tail(5).index
        
        weights_df.loc[date, low_vol_5] = 1.0 / 5.0 # Long
        weights_df.loc[date, high_vol_5] = -1.0 / 5.0 # Short
        
    # Calculate returns
    port_returns = (weights_df * valid_returns).sum(axis=1)
    
    # Brutal Short Borrowing Costs (assumed 1% annualized for large caps)
    short_weights = weights_df[weights_df < 0].fillna(0)
    borrow_cost_daily = 0.01 / 252
    borrow_fees = short_weights.abs().sum(axis=1) * borrow_cost_daily
    
    # Turnover
    turnover = weights_df.diff().abs().sum(axis=1) / 2.0
    
    final_returns = port_returns - (turnover * 0.0010) - borrow_fees
    
    cagr, max_dd, sharpe = calc_metrics(final_returns, risk_free=0.0) # Market neutral, so risk free is base
    
    # Benchmark is equally weighted portfolio of these stocks
    bm_returns = valid_returns.mean(axis=1)
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(bm_returns)
    
    print(f"  Benchmark (Eq-W Dow30): CAGR: {bm_cagr*100:.2f}% | Max DD: {bm_dd*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print(f"  Low Vol L/S Strat: CAGR: {cagr*100:.2f}% | Max DD: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")


def run_strategy_75():
    print("\n[*] Running Strategy 75: CTA Trend-Following Tail Risk...")
    tickers = ["SPY", "SH", "SHV"]
    data = yf.download(tickers, start="2010-01-01", end="2024-01-01", progress=False, auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        close_data = data['Close'].dropna()
    else:
        close_data = data.dropna()
        
    returns = close_data.pct_change()
    
    # 10-day momentum of SPY
    spy_10d_mom = close_data['SPY'].pct_change(10)
    
    weight_spy = pd.Series(1.0, index=close_data.index)
    weight_sh = pd.Series(0.0, index=close_data.index)
    
    # If 10d mom drops below -3%, we are crashing, rotate immediately to SH (Short S&P 500)
    crash_regime = spy_10d_mom < -0.03
    
    # Shift 1 to prevent lookahead
    crash_regime = crash_regime.shift(1).fillna(False).astype(bool)
    
    weight_spy[crash_regime] = 0.0
    weight_sh[crash_regime] = 1.0
    
    strat_returns = (weight_spy * returns['SPY']) + (weight_sh * returns['SH'])
    
    # Brutal Slippage
    turnover = weight_spy.diff().abs() + weight_sh.diff().abs()
    turnover = turnover / 2.0
    
    # In a crash, slippage is worse. So we use 20 bps (0.0020) for this fast-switching CTA strat
    strat_returns = strat_returns - (turnover * 0.0020)
    
    cagr, max_dd, sharpe = calc_metrics(strat_returns)
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(returns['SPY'])
    
    print(f"  Benchmark (SPY): CAGR: {bm_cagr*100:.2f}% | Max DD: {bm_dd*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print(f"  CTA Tail Risk Strat: CAGR: {cagr*100:.2f}% | Max DD: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")

if __name__ == "__main__":
    run_strategy_28()
    run_strategy_44()
    run_strategy_75()
