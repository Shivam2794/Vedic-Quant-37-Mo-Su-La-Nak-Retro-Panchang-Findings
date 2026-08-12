import pandas as pd
import numpy as np
import yfinance as yf
import optuna
import matplotlib.pyplot as plt

def get_data():
    print("Downloading historical data for V24 Multi-Asset Grinder...")
    tickers = ["SPY", "QQQ", "TLT"]
    df = yf.download(tickers, start="2010-01-01", end="2026-12-31")['Close']
    df = df.ffill().dropna()
    return df

def simulate_dual_momentum(df, lookback_1, lookback_2, weight_fast, lev, cash_threshold):
    # Calculate returns
    rets = df.pct_change().fillna(0)
    
    # Calculate Momentum
    mom_1 = df.pct_change(lookback_1).fillna(0)
    mom_2 = df.pct_change(lookback_2).fillna(0)
    
    # Blended Momentum
    mom = (weight_fast * mom_1) + ((1 - weight_fast) * mom_2)
    
    # Pre-allocate strategy returns
    strat_rets = pd.Series(0.0, index=df.index)
    
    for i in range(max(lookback_1, lookback_2), len(df)):
        # Yesterday's momentum determines today's position
        prev_mom = mom.iloc[i-1]
        
        spy_m = prev_mom['SPY']
        qqq_m = prev_mom['QQQ']
        tlt_m = prev_mom['TLT']
        
        # Determine asset to hold
        if spy_m < cash_threshold and qqq_m < cash_threshold:
            # Defensive (Flight to safety)
            if tlt_m > 0:
                pos_ret = rets['TLT'].iloc[i] * lev
            else:
                pos_ret = 0.0 # Cash
        else:
            # Offensive (Risk-On)
            if qqq_m > spy_m:
                pos_ret = rets['QQQ'].iloc[i] * lev
            else:
                pos_ret = rets['SPY'].iloc[i] * lev
                
        strat_rets.iloc[i] = pos_ret
        
    # We evaluate from 2011 to present (15 years)
    strat_rets = strat_rets.loc['2011-01-01':]
    
    equity = (1 + strat_rets).cumprod()
    days = (equity.index[-1] - equity.index[0]).days
    
    if days < 365:
        return 0, 0, strat_rets
        
    cagr = (equity.iloc[-1] ** (365.25 / days)) - 1
    mdd = ((equity - equity.cummax()) / equity.cummax()).min()
    
    return cagr, mdd, strat_rets

def objective(trial, df):
    lookback_1 = trial.suggest_int("lookback_1", 10, 100)
    lookback_2 = trial.suggest_int("lookback_2", 100, 250)
    weight_fast = trial.suggest_float("weight_fast", 0.0, 1.0)
    lev = trial.suggest_float("lev", 1.0, 3.0)
    cash_threshold = trial.suggest_float("cash_threshold", -0.05, 0.05)
    
    cagr, mdd, _ = simulate_dual_momentum(df, lookback_1, lookback_2, weight_fast, lev, cash_threshold)
    
    score = cagr
    if cagr < 0.18:
        score -= (0.18 - cagr) * 10
    if mdd < -0.20:
        score -= (-0.20 - mdd) * 10
        
    # Return heavily penalized score if it's invalid
    if cagr == 0:
        return -100.0
        
    return score

def run_v24():
    df = get_data()
    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: objective(trial, df), n_trials=500)
    
    best_params = study.best_params
    print("BEST PARAMS:", best_params)
    
    cagr, mdd, strat_rets = simulate_dual_momentum(df, **best_params)
    
    print(f"FINAL CAGR: {cagr:.2%}")
    print(f"FINAL MDD: {mdd:.2%}")
    
    equity = (1 + strat_rets).cumprod()
    
    spy_ret = df['SPY'].pct_change().fillna(0).loc['2011-01-01':]
    spy_equity = (1 + spy_ret).cumprod()
    
    plt.figure(figsize=(12, 6))
    plt.plot(equity.index, equity.values, label=f"V24 Multi-Asset (CAGR: {cagr:.2%}, MDD: {mdd:.2%})", color='blue')
    plt.plot(spy_equity.index, spy_equity.values, label=f"SPY Benchmark", color='gray', alpha=0.7)
    plt.yscale('log')
    plt.title("V24 Multi-Asset Dual Momentum")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plot_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\87028df4-1ec4-40e2-a989-dbc79c4b85bb\v24_equity_curve.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
    with open('v24_results.txt', 'w') as f:
        f.write(f"CAGR: {cagr:.4f}\nMDD: {mdd:.4f}")

if __name__ == '__main__':
    run_v24()
