import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def get_data():
    tickers = ["SPY", "QQQ", "TLT", "NVDA", "AAPL", "MSFT", "AMZN", "^IRX"]
    df = yf.download(tickers, start="2005-01-01", end="2026-12-31")['Close']
    df = df.ffill().dropna()
    df['RF_Daily'] = ((1 + (df['^IRX'] / 100.0)) ** (1/252)) - 1
    return df

def run_v28(df):
    rets = df.pct_change().fillna(0)
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    stocks = ["NVDA", "AAPL", "MSFT", "AMZN"]
    mom = df[stocks].pct_change(126).fillna(0) # 6 month momentum
    
    for i in range(126, len(df)):
        mom_prev = mom.iloc[i-1]
        tlt_ret_prev = df['TLT'].pct_change(126).iloc[i-1]
        
        best_stock = mom_prev.idxmax()
        best_mom = mom_prev.max()
        
        if best_mom > 0:
            current_pos = best_stock
        elif tlt_ret_prev > 0:
            current_pos = 'TLT'
        else:
            current_pos = 'CASH'
            
        positions.iloc[i] = current_pos
        rf = df['RF_Daily'].iloc[i]
        
        if current_pos == 'CASH':
            strat_rets.iloc[i] = rf
        else:
            strat_rets.iloc[i] = rets[current_pos].iloc[i]
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 # Slippage
            
    return strat_rets

def run_v14_proxy(df):
    """Proxy for V14.2 Shannon/Vol Adjusted strategy (Approx 24% CAGR, -24% MDD)"""
    rets = df.pct_change().fillna(0)
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    # Dual Momentum QQQ / TLT + Volatility Filter
    lev = 1.5
    mom = df[['QQQ', 'TLT']].pct_change(60).fillna(0)
    vol = df['QQQ'].pct_change().rolling(20).std() * np.sqrt(252)
    
    for i in range(60, len(df)):
        qqq_m = mom['QQQ'].iloc[i-1]
        tlt_m = mom['TLT'].iloc[i-1]
        qqq_v = vol.iloc[i-1]
        
        # V14 logic approximation: Only trade QQQ if Vol is manageable, else TLT
        if qqq_m > 0 and qqq_m > tlt_m and qqq_v < 0.25:
            current_pos = 'QQQ'
        elif tlt_m > 0:
            current_pos = 'TLT'
        else:
            current_pos = 'CASH'
            
        positions.iloc[i] = current_pos
        rf = df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        
        if current_pos == 'CASH':
            strat_rets.iloc[i] = rf
        else:
            strat_rets.iloc[i] = (rets[current_pos].iloc[i] * lev) - borrow_cost
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 * lev
            
    return strat_rets

def run_v29(df):
    """Holy Grail Trailing Stop"""
    rets = df.pct_change().fillna(0)
    lookback = 60
    mom = df[['QQQ', 'TLT']].pct_change(lookback).fillna(0)
    strat_rets = pd.Series(0.0, index=df.index)
    positions = pd.Series('CASH', index=df.index)
    
    lev = 2.0
    high_water_mark = 1.0
    current_equity = 1.0
    in_market = True
    cooldown = 0
    
    for i in range(lookback, len(df)):
        qqq_m = mom['QQQ'].iloc[i-1]
        tlt_m = mom['TLT'].iloc[i-1]
        
        if qqq_m > 0 and qqq_m > tlt_m:
            target_pos = 'QQQ'
        elif tlt_m > 0 and tlt_m > qqq_m:
            target_pos = 'TLT'
        else:
            target_pos = 'CASH'
            
        rf = df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        
        if target_pos == 'CASH':
            raw_ret = rf
        else:
            raw_ret = (rets[target_pos].iloc[i] * lev) - borrow_cost
            
        if in_market:
            actual_ret = raw_ret
            current_equity *= (1 + actual_ret)
            if current_equity > high_water_mark:
                high_water_mark = current_equity
            drawdown = (current_equity - high_water_mark) / high_water_mark
            
            if drawdown < -0.15:
                in_market = False
                cooldown = 60
                positions.iloc[i] = 'CASH'
                strat_rets.iloc[i] = actual_ret
                continue
                
            positions.iloc[i] = target_pos
            strat_rets.iloc[i] = actual_ret
        else:
            cooldown -= 1
            if cooldown <= 0:
                in_market = True
                high_water_mark = current_equity 
            positions.iloc[i] = 'CASH'
            strat_rets.iloc[i] = rf
            
        if positions.iloc[i] != positions.iloc[i-1]:
            strat_rets.iloc[i] -= 0.0005 * lev
            
    return strat_rets

def main():
    print("Fetching data...")
    df = get_data()
    print("Running V28 (Tier 2 - Absolute Return)...")
    v28_rets = run_v28(df).loc['2011-01-01':]
    print("Running V14 (Tier 1 - Risk Adjusted)...")
    v14_rets = run_v14_proxy(df).loc['2011-01-01':]
    print("Running V29 (Tier 3 - Holy Grail Trail Stop)...")
    v29_rets = run_v29(df).loc['2011-01-01':]
    
    spy_rets = df['SPY'].pct_change().fillna(0).loc['2011-01-01':]
    
    # Calculate Equity
    eq_v28 = (1 + v28_rets).cumprod()
    eq_v14 = (1 + v14_rets).cumprod()
    eq_v29 = (1 + v29_rets).cumprod()
    eq_spy = (1 + spy_rets).cumprod()
    
    def calc_metrics(eq):
        days = (eq.index[-1] - eq.index[0]).days
        cagr = (eq.iloc[-1] ** (365.25 / max(days, 1))) - 1
        mdd = ((eq - eq.cummax()) / eq.cummax()).min()
        return cagr, mdd
        
    cagr_v28, mdd_v28 = calc_metrics(eq_v28)
    cagr_v14, mdd_v14 = calc_metrics(eq_v14)
    cagr_v29, mdd_v29 = calc_metrics(eq_v29)
    cagr_spy, mdd_spy = calc_metrics(eq_spy)
    
    print(f"V28 Actual: {cagr_v28:.2%} / {mdd_v28:.2%}")
    print(f"V14 Proxy Actual: {cagr_v14:.2%} / {mdd_v14:.2%}")
    print(f"V29 Actual: {cagr_v29:.2%} / {mdd_v29:.2%}")
    print(f"SPY Actual: {cagr_spy:.2%} / {mdd_spy:.2%}")
    
    plt.style.use('dark_background')
    plt.figure(figsize=(14, 8))
    plt.plot(eq_v28.index, eq_v28, label=f'Tier 2: V28 Tech Rotation ({cagr_v28:.1%} CAGR, {mdd_v28:.1%} MDD)', color='magenta', linewidth=2)
    plt.plot(eq_v14.index, eq_v14, label=f'Tier 1: V14 Proxy ({cagr_v14:.1%} CAGR, {mdd_v14:.1%} MDD)', color='cyan', linewidth=2)
    plt.plot(eq_v29.index, eq_v29, label=f'Tier 3: V29 Strict Trail Stop ({cagr_v29:.1%} CAGR, {mdd_v29:.1%} MDD)', color='yellow', linewidth=2)
    plt.plot(eq_spy.index, eq_spy, label=f'Benchmark: SPY S&P 500 ({cagr_spy:.1%} CAGR, {mdd_spy:.1%} MDD)', color='white', linewidth=2, linestyle='--')
    
    plt.yscale('log')
    plt.title('Top 3 Strategies vs Benchmark (2011 - 2026)', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Cumulative Growth (Log Scale)', fontsize=12)
    plt.legend(loc='upper left', fontsize=12)
    plt.grid(True, alpha=0.2, linestyle='--')
    
    save_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\87028df4-1ec4-40e2-a989-dbc79c4b85bb\top3_equity_curves.png"
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    print(f"Plot saved to {save_path}")

if __name__ == '__main__':
    main()
