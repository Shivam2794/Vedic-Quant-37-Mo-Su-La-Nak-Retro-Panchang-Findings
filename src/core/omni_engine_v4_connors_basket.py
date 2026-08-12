import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 5 / 10000

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def run_omni_connors_basket():
    print("[*] Downloading Data for Connors Mean Reversion Basket...")
    # Diverse non-correlated ETFs + VIX + IRX
    tickers = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'GLD', 'TLT', 'LQD', 'VNQ', 'XLE', '^VIX', '^IRX']
    df = yf.download(tickers, start="2007-01-01", end="2024-01-01")['Close']
    df = df.ffill().dropna()
    
    etfs = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'GLD', 'TLT', 'LQD', 'VNQ', 'XLE']
    
    returns = df[etfs].pct_change().dropna()
    vix = df['^VIX'].loc[returns.index]
    daily_cash_yield = (df['^IRX'].loc[returns.index] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    weights = pd.DataFrame(0.0, index=returns.index, columns=etfs)
    
    print("[*] Calculating Indicators and Signals...")
    # Pre-calculate indicators to avoid loops
    sma200 = df[etfs].rolling(200).mean()
    sma5 = df[etfs].rolling(5).mean()
    
    rsi2 = pd.DataFrame(index=df.index, columns=etfs)
    for col in etfs:
        rsi2[col] = rsi(df[col], 2)
        
    sma200 = sma200.loc[returns.index]
    sma5 = sma5.loc[returns.index]
    rsi2 = rsi2.loc[returns.index]
    df_etfs = df[etfs].loc[returns.index]
    
    # State tracking
    in_position = {etf: False for etf in etfs}
    
    for i in range(len(returns)):
        date = returns.index[i]
        current_vix = vix.iloc[i]
        
        # Don't enter new positions if VIX is in absolute panic mode
        vix_panic = current_vix > 35
        
        for etf in etfs:
            price = df_etfs[etf].iloc[i]
            if pd.isna(sma200[etf].iloc[i]): continue
                
            # Exit rules: RSI2 > 70 or Price closes above 5-day SMA
            if in_position[etf]:
                if rsi2[etf].iloc[i] > 70 or price > sma5[etf].iloc[i]:
                    in_position[etf] = False
                    
            # Entry rules: Price > 200 SMA (uptrend) AND RSI2 < 10 (oversold) AND NOT Vix Panic
            if not in_position[etf] and not vix_panic:
                if price > sma200[etf].iloc[i] and rsi2[etf].iloc[i] < 10:
                    in_position[etf] = True
                    
            # Record weight
            if in_position[etf]:
                weights.loc[date, etf] = 1.0

    # Shift weights by 1 day to prevent lookahead bias (execute at next open/close)
    weights = weights.shift(1).fillna(0.0)
    
    # Capital Allocation: We have 10 ETFs. We can allocate 10% per signal to avoid leverage,
    # OR we can allocate 25% per signal (up to 4 signals, then equal weight).
    # Since signals are rare, let's allocate 25% to each active signal, capping at 100% total exposure.
    MAX_EXPOSURE = 1.0
    ALLOCATION_PER_SIGNAL = 0.25
    
    final_weights = pd.DataFrame(0.0, index=returns.index, columns=etfs)
    
    for i in range(len(weights)):
        date = weights.index[i]
        active_signals = weights.iloc[i].sum()
        
        if active_signals > 0:
            if active_signals * ALLOCATION_PER_SIGNAL > MAX_EXPOSURE:
                # Scale down so total exposure is exactly MAX_EXPOSURE
                scaled_weight = MAX_EXPOSURE / active_signals
                final_weights.iloc[i] = weights.iloc[i] * scaled_weight
            else:
                final_weights.iloc[i] = weights.iloc[i] * ALLOCATION_PER_SIGNAL

    # Calculate returns
    asset_ret = (final_weights * returns).sum(axis=1)
    
    # Cash accounting
    gross_exposure = final_weights.sum(axis=1)
    cash_position = 1.0 - gross_exposure
    cash_ret = cash_position * daily_cash_yield
    
    # Slippage
    delta = final_weights.diff().abs().sum(axis=1).fillna(0)
    total_slippage = delta * SLIPPAGE_BPS
    
    port_ret = asset_ret + cash_ret - total_slippage
    
    # Leverage the entire portfolio 2x since it's in cash most of the time
    LEVERAGE = 2.0
    borrow_spread = 0.01 / 252
    borrow_cost = (LEVERAGE - 1.0) * (daily_cash_yield + borrow_spread)
    
    port_ret_leveraged = (port_ret * LEVERAGE) - borrow_cost
    
    # ---------------------------------------------------------
    # STATS
    # ---------------------------------------------------------
    def calc_stats(ret_series, name):
        cagr = (1 + ret_series).prod() ** (252 / len(ret_series)) - 1
        sharpe = np.sqrt(252) * ret_series.mean() / (ret_series.std() + 1e-9)
        cum_ret = (1 + ret_series).cumprod()
        max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
        print(f"[*] {name}")
        print(f"CAGR: {cagr:.2%}")
        print(f"Sharpe: {sharpe:.2f}")
        print(f"Max DD: {max_dd:.2%}")
        return sharpe, max_dd
        
    print("========================================================")
    calc_stats(port_ret, "CONNORS BASKET (1X UNLEVERAGED)")
    print("--------------------------------------------------------")
    calc_stats(port_ret_leveraged, "CONNORS BASKET (2X LEVERAGED)")
    print("--------------------------------------------------------")
    
    spy_r = returns['SPY']
    calc_stats(spy_r, "SPY BENCHMARK")
    print("========================================================")

if __name__ == "__main__":
    run_omni_connors_basket()
