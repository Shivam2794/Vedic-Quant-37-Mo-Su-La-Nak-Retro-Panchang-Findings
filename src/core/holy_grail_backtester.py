import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def compute_drawdown(cum_returns):
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    return max_drawdown

def compute_cagr(cum_returns, days):
    total_return = cum_returns.iloc[-1]
    years = days / 252.0
    cagr = (total_return ** (1 / years)) - 1
    return cagr

def print_inspection(name, cagr, mdd, qqq_cagr, days):
    print(f"\n========================================================")
    print(f"[{name}]")
    print(f"Total Trading Days: {days}")
    print(f"CAGR: {cagr*100:.2f}% | Max Drawdown: {mdd*100:.2f}%")
    print(f"QQQ Benchmark CAGR: {qqq_cagr*100:.2f}%")
    
    # Brutal Inspection Rules
    if cagr > 0.14:
        print("[PASS] BRUTAL INSPECTION: Passed CAGR > 14%")
    else:
        print("[FAIL] BRUTAL INSPECTION: Failed CAGR > 14%")
        
    if mdd > -0.25:
        print("[PASS] BRUTAL INSPECTION: Passed MDD < 25%")
    else:
        print("[FAIL] BRUTAL INSPECTION: Failed MDD < 25%")
        
    if cagr > qqq_cagr:
        print("[PASS] BRUTAL INSPECTION: Strategy Beats QQQ Baseline")
    else:
        print("[FAIL] BRUTAL INSPECTION: Strategy Lags QQQ Baseline")
    print(f"========================================================\n")


def backtest_tactical_rotation(data):
    """
    Fixed Tactical Dual Momentum:
    Assets: SPY, QQQ, GLD, TLT
    Logic: Rank by 6-month return. If top asset's 6m return > 0 and Close > 200d MA, invest 100% in it. 
    Otherwise, invest 100% in TLT (Long term bonds). Rebalance monthly.
    """
    assets = ['SPY', 'QQQ', 'GLD', 'TLT']
    df = data[assets].dropna()
    
    for col in assets:
        df[f'{col}_ret6m'] = df[col].pct_change(126)
        df[f'{col}_ma200'] = df[col].rolling(200).mean()
        df[f'{col}_daily_ret'] = df[col].pct_change()
        
    df = df.dropna()
    monthly = df.resample('ME').last()
    
    allocations = pd.DataFrame(0.0, index=monthly.index, columns=assets)
    
    for idx, row in monthly.iterrows():
        mom_scores = row[[f'{c}_ret6m' for c in ['SPY', 'QQQ', 'GLD']]].rename(index=lambda x: x.replace('_ret6m', ''))
        top_asset = mom_scores.idxmax()
        
        # Absolute momentum & crash check
        if mom_scores[top_asset] > 0 and row[top_asset] > row[f'{top_asset}_ma200']:
            allocations.loc[idx, top_asset] = 1.0
        else:
            allocations.loc[idx, 'TLT'] = 1.0
            
    allocations = allocations.reindex(df.index).ffill().shift(1).fillna(0.0)
    daily_returns = df[[f'{c}_daily_ret' for c in assets]].rename(columns=lambda x: x.replace('_daily_ret', ''))
    port_ret = (allocations * daily_returns).sum(axis=1)
    
    cum_returns = (1 + port_ret).cumprod()
    return cum_returns, compute_cagr(cum_returns, len(cum_returns)), compute_drawdown(cum_returns), len(cum_returns)

def backtest_leveraged_risk_parity(data):
    """
    Fixed Risk Parity (Daily Volatility Targeting)
    Target 15% Annualized Volatility dynamically. 
    """
    df = data[['SPY', 'TLT']].dropna()
    df['SPY_ret'] = df['SPY'].pct_change()
    df['TLT_ret'] = df['TLT'].pct_change()
    
    # Base 55/45 Portfolio
    df['Base_Port'] = (df['SPY_ret'] * 0.55) + (df['TLT_ret'] * 0.45)
    
    # Daily rolling 20d volatility of the base portfolio
    df['Base_Vol'] = df['Base_Port'].rolling(20).std() * np.sqrt(252)
    
    df = df.dropna()
    
    # Dynamic Leverage: Target 16% annualized vol
    df['Target_Lev'] = 0.16 / df['Base_Vol']
    # Cap leverage at 2.5x to prevent extreme margin call risk
    df['Target_Lev'] = df['Target_Lev'].clip(upper=2.5, lower=0.0)
    
    # Shift leverage to simulate applying it the next day
    df['Lev_Applied'] = df['Target_Lev'].shift(1).fillna(1.0)
    
    # Borrowing cost for leverage > 1.0 (approx 3% annualized)
    borrow_cost = (df['Lev_Applied'] - 1.0).clip(lower=0) * (0.03 / 252)
    
    df['Strat_Ret'] = (df['Base_Port'] * df['Lev_Applied']) - borrow_cost
    
    cum_returns = (1 + df['Strat_Ret']).cumprod()
    return cum_returns, compute_cagr(cum_returns, len(cum_returns)), compute_drawdown(cum_returns), len(cum_returns)

def calc_rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def backtest_deep_mean_reversion(data):
    """
    Fixed Mean Reversion (Leveraged Overlay on QQQ)
    Hold 100% QQQ normally. 
    If QQQ crashes (RSI2 < 10) in a macro uptrend (>200MA), borrow margin to go 200% QQQ to catch the knife.
    If QQQ euphoric (RSI2 > 90), rotate to 100% TLT.
    """
    df = data[['QQQ', 'TLT']].dropna()
    df['QQQ_ret'] = df['QQQ'].pct_change()
    df['TLT_ret'] = df['TLT'].pct_change()
    df['RSI2'] = calc_rsi(df['QQQ'], 2)
    df['MA200'] = df['QQQ'].rolling(200).mean()
    
    df = df.dropna()
    
    alloc_qqq = np.ones(len(df))
    alloc_tlt = np.zeros(len(df))
    
    for i in range(len(df)):
        rsi = df['RSI2'].iloc[i]
        close = df['QQQ'].iloc[i]
        ma200 = df['MA200'].iloc[i]
        
        if rsi < 10 and close > ma200:
            alloc_qqq[i] = 2.0  # 2x Leverage
            alloc_tlt[i] = 0.0
        elif rsi > 90:
            alloc_qqq[i] = 0.0
            alloc_tlt[i] = 1.0
        else:
            alloc_qqq[i] = 1.0
            alloc_tlt[i] = 0.0
            
    # Shift allocations by 1 to apply to next day returns
    alloc_qqq = pd.Series(alloc_qqq, index=df.index).shift(1).fillna(1.0)
    alloc_tlt = pd.Series(alloc_tlt, index=df.index).shift(1).fillna(0.0)
    
    borrow_cost = (alloc_qqq - 1.0).clip(lower=0) * (0.03 / 252)
    
    df['Strat_Ret'] = (alloc_qqq * df['QQQ_ret']) + (alloc_tlt * df['TLT_ret']) - borrow_cost
    
    cum_returns = (1 + df['Strat_Ret']).cumprod()
    return cum_returns, compute_cagr(cum_returns, len(cum_returns)), compute_drawdown(cum_returns), len(cum_returns)

def main():
    print("Downloading 20 Years of Market Data (SPY, QQQ, GLD, TLT, IWM, EFA)...")
    tickers = ['SPY', 'QQQ', 'GLD', 'TLT', 'IWM', 'EFA']
    data = yf.download(tickers, start='2005-01-01', end='2026-07-07', auto_adjust=False)['Close']
    
    # Calculate baseline QQQ
    qqq = data['QQQ'].dropna()
    qqq_cum = (1 + qqq.pct_change().dropna()).cumprod()
    qqq_cagr = compute_cagr(qqq_cum, len(qqq_cum))
    
    print("\nExecuting Brutal Multipoint Inspection...")
    
    _, cagr1, mdd1, d1 = backtest_tactical_rotation(data)
    print_inspection("Tactical Multi-Asset Rotation (Dual Momentum)", cagr1, mdd1, qqq_cagr, d1)
    
    _, cagr2, mdd2, d2 = backtest_leveraged_risk_parity(data)
    print_inspection("Leveraged Risk Parity (HEDGEFUNDIE + Vol Target)", cagr2, mdd2, qqq_cagr, d2)
    
    _, cagr3, mdd3, d3 = backtest_deep_mean_reversion(data)
    print_inspection("SPY/QQQ Deep Mean Reversion", cagr3, mdd3, qqq_cagr, d3)

if __name__ == "__main__":
    main()
