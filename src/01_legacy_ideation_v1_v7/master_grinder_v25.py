import pandas as pd
import numpy as np
import yfinance as yf
import optuna
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def get_data():
    print("Downloading historical data (Adj Close) for V25 Multi-Asset Grinder...")
    tickers = ["SPY", "QQQ", "TLT", "^IRX"]  # IRX is 13-week treasury bill (risk free rate)
    df = yf.download(tickers, start="2005-01-01", end="2026-12-31", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    
    # Convert IRX from annualized percentage (e.g. 5.0 for 5%) to daily return equivalent
    # Formula: (1 + R)^(1/252) - 1 where R is decimal (IRX/100)
    df['RF_Daily'] = ((1 + (df['^IRX'] / 100.0)) ** (1/252)) - 1
    
    return df

def simulate_dual_momentum(df, start_date, end_date, lookback_1, lookback_2, weight_fast, lev, cash_threshold):
    # Slice data for the period plus buffer for lookback
    buffer_days = max(lookback_1, lookback_2) + 10
    start_idx = df.index.get_indexer([pd.to_datetime(start_date)], method='nearest')[0]
    
    if start_idx < buffer_days:
        sub_df = df.iloc[: df.index.get_indexer([pd.to_datetime(end_date)], method='nearest')[0] + 1]
    else:
        sub_df = df.iloc[start_idx - buffer_days : df.index.get_indexer([pd.to_datetime(end_date)], method='nearest')[0] + 1]
        
    rets = sub_df.pct_change().fillna(0)
    
    mom_1 = sub_df.pct_change(lookback_1).fillna(0)
    mom_2 = sub_df.pct_change(lookback_2).fillna(0)
    mom = (weight_fast * mom_1) + ((1 - weight_fast) * mom_2)
    
    strat_rets = pd.Series(0.0, index=sub_df.index)
    positions = pd.Series('CASH', index=sub_df.index)
    
    for i in range(buffer_days, len(sub_df)):
        prev_mom = mom.iloc[i-1]
        
        spy_m = prev_mom['SPY']
        qqq_m = prev_mom['QQQ']
        tlt_m = prev_mom['TLT']
        
        if spy_m < cash_threshold and qqq_m < cash_threshold:
            if tlt_m > 0:
                current_pos = 'TLT'
            else:
                current_pos = 'CASH'
        else:
            if qqq_m > spy_m:
                current_pos = 'QQQ'
            else:
                current_pos = 'SPY'
                
        positions.iloc[i] = current_pos
        
        # Calculate daily return
        rf = sub_df['RF_Daily'].iloc[i]
        borrow_cost = (lev - 1.0) * rf if lev > 1.0 else 0.0
        
        if current_pos == 'CASH':
            # Earn risk free rate on cash
            strat_rets.iloc[i] = rf
        else:
            # Earn asset return * leverage minus borrow cost
            strat_rets.iloc[i] = (rets[current_pos].iloc[i] * lev) - borrow_cost
            
        # Deduct Slippage / Transaction Cost (5 basis points) if position changed
        if i > buffer_days and positions.iloc[i] != positions.iloc[i-1]:
            # We pay slippage on the ENTIRE leveraged position size
            strat_rets.iloc[i] -= 0.0005 * lev
            
    # Return strictly the requested time window
    mask = (strat_rets.index >= pd.to_datetime(start_date)) & (strat_rets.index <= pd.to_datetime(end_date))
    strat_rets = strat_rets[mask]
    
    return strat_rets

def objective(trial, df, start_date, end_date):
    lookback_1 = trial.suggest_int("lookback_1", 10, 100)
    lookback_2 = trial.suggest_int("lookback_2", 100, 250)
    weight_fast = trial.suggest_float("weight_fast", 0.0, 1.0)
    lev = trial.suggest_float("lev", 1.0, 3.0)
    cash_threshold = trial.suggest_float("cash_threshold", -0.05, 0.05)
    
    strat_rets = simulate_dual_momentum(df, start_date, end_date, lookback_1, lookback_2, weight_fast, lev, cash_threshold)
    
    if len(strat_rets) < 200:
        return -100.0
        
    equity = (1 + strat_rets).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    
    if days < 100:
        return -100.0
        
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    score = cagr
    if cagr < 0.18:
        score -= (0.18 - cagr) * 10
    if mdd < -0.20:
        score -= (-0.20 - mdd) * 10
        
    if cagr == 0:
        return -100.0
        
    return score

def run_wfo():
    df = get_data()
    print("Executing Walk-Forward Optimization (WFO)...")
    
    # Train windows: 3 years. Test windows: 1 year.
    # Total OOS Period: 2011 to 2026
    
    years = range(2011, 2027)
    oos_returns = []
    
    for y in years:
        train_start = f"{y-3}-01-01"
        train_end = f"{y-1}-12-31"
        test_start = f"{y}-01-01"
        test_end = f"{y}-12-31"
        
        # Don't run WFO on partial current year if data is missing, but 2026 doesn't exist yet, we only have data to 2024 probably.
        # Actually yfinance will just return up to today.
        
        if pd.to_datetime(train_end) > df.index[-1]:
            break
            
        print(f"Optimizing Train: {train_start} to {train_end} | Testing OOS: {test_start} to {test_end}")
        
        study = optuna.create_study(direction="maximize")
        study.optimize(lambda trial: objective(trial, df, train_start, train_end), n_trials=150)
        
        best = study.best_params
        print(f"[{y}] Best Params: {best}")
        
        test_rets = simulate_dual_momentum(df, test_start, test_end, **best)
        oos_returns.append(test_rets)
        
    final_oos = pd.concat(oos_returns)
    final_oos = final_oos[~final_oos.index.duplicated(keep='first')]
    final_oos = final_oos.sort_index()
    
    equity = (1 + final_oos).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    print(f"--- STRICT WFO OUT-OF-SAMPLE RESULTS ---")
    print(f"CAGR: {cagr:.2%}")
    print(f"MDD:  {mdd:.2%}")
    
    # SPY benchmark
    spy_ret = df['SPY'].pct_change().fillna(0).loc[final_oos.index[0] : final_oos.index[-1]]
    spy_equity = (1 + spy_ret).cumprod()
    
    plt.figure(figsize=(12, 6))
    plt.plot(equity.index, equity.values, label=f"V25 WFO OOS (CAGR: {cagr:.2%}, MDD: {mdd:.2%})", color='blue')
    plt.plot(spy_equity.index, spy_equity.values, label=f"SPY Benchmark", color='gray', alpha=0.7)
    plt.yscale('log')
    plt.title("V25 Multi-Asset WFO (Slippage + Borrow Cost Included)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plot_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\87028df4-1ec4-40e2-a989-dbc79c4b85bb\v25_equity_curve.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

if __name__ == '__main__':
    run_wfo()
