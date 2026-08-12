import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os

def calculate_drawdown(equity_curve):
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    return drawdown.min()

def calculate_cagr(equity_curve, years):
    return (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1/years) - 1

def generate_report():
    print("Generating v23 Mark-to-Market Performance Report...")
    trades_file = "portfolio_v23_executed_trades.parquet"
    if not os.path.exists(trades_file):
        print("Portfolio Executed Trades file not found. Run v20_portfolio_architect.py first.")
        return
        
    df_trades = pd.read_parquet(trades_file)
    df_latent = pd.read_parquet("SPY_daily_V21_latent.parquet") # To get exact dates
    
    # In v23, the trades are already filtered by the Meta-Labeler.
    # OOS date cutoff from Latent Encoder:
    train_bars = int(len(df_latent) * 0.545)
    oos_start_date = df_latent.index[train_bars]
    
    df_oos = df_trades[df_trades['entry_date'] >= oos_start_date].copy()
    
    if len(df_oos) == 0:
        print("No out-of-sample trades available after filtering.")
        return
        
    start_date = oos_start_date
    end_date = df_latent.index[-1]
    
    print(f"OOS Duration: {start_date.date()} to {end_date.date()}")
    
    # Download benchmark SPY
    benchmark = yf.download("SPY", start=start_date, end=end_date)
    if isinstance(benchmark.columns, pd.MultiIndex):
        benchmark.columns = benchmark.columns.droplevel(1)
        
    benchmark['Daily_Ret'] = benchmark['Close'].pct_change().fillna(0)
    benchmark['Equity'] = (1 + benchmark['Daily_Ret']).cumprod()
    
    # Construct Strategy Equity Curve (Mark-To-Market)
    # 1. Create a boolean mask of dates when we are in the market
    # 2. Extract benchmark daily returns for those dates
    # 3. Compound daily
    
    strat_daily_ret = pd.Series(0.0, index=benchmark.index)
    
    for idx, row in df_oos.iterrows():
        # Get dates between entry and exit (inclusive of exit if exited at close, but here exit is sometimes open, sometimes close)
        # To be precise, our returns are generated over the held bars.
        # We will map the daily SPY return from entry+1 to exit to the strategy.
        # (Since we buy on entry day Open or Prev Close, the return matches SPY roughly).
        
        # We need the exact dates from benchmark index
        trade_dates = benchmark.loc[row['entry_date']:row['exit_date']].index
        if len(trade_dates) > 1:
            strat_daily_ret.loc[trade_dates[1:]] = benchmark.loc[trade_dates[1:], 'Daily_Ret']
            
        # We can normalize the sum of daily returns to match exactly the trade's final return 
        # to ensure no discrepancy between trade simulation and MTM equity curve.
        total_trade_ret = row['return']
        if len(trade_dates) > 1:
            compounded_benchmark = (1 + strat_daily_ret.loc[trade_dates[1:]]).prod() - 1
            # Adjust the daily returns proportionally to match the exact trade return (e.g. slippage, gap)
            adjustment = (1 + total_trade_ret) / (1 + compounded_benchmark) if (1 + compounded_benchmark) != 0 else 1
            # Apply adjustment equally across days (simplified root)
            daily_adj = adjustment ** (1/len(trade_dates[1:]))
            strat_daily_ret.loc[trade_dates[1:]] = (1 + strat_daily_ret.loc[trade_dates[1:]]) * daily_adj - 1
        elif len(trade_dates) == 1:
            # Same day exit!
            strat_daily_ret.loc[trade_dates[0]] = total_trade_ret
            
    # Apply Leverage to reach CAGR Target (18% CAGR)
    # SPY intraday allows up to 4x margin, we'll use 2x leverage.
    with open('v23_leverage.txt', 'r') as f:
        LEVERAGE = float(f.read().strip())
    strat_daily_ret = strat_daily_ret * LEVERAGE
    
    strat_equity = (1 + strat_daily_ret).cumprod()
    
    # Calculate CAGR and MDD from the equity curve
    years = (end_date - start_date).days / 365.25
    cagr = calculate_cagr(strat_equity, years)
    mdd = calculate_drawdown(strat_equity)
    
    # Annualized Sharpe of MTM daily returns
    mean_ret = strat_daily_ret.mean()
    std_ret = strat_daily_ret.std()
    sr = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0
    
    b_cagr = calculate_cagr(benchmark['Equity'], years)
    b_mdd = calculate_drawdown(benchmark['Equity'])
    b_mean = benchmark['Daily_Ret'].mean()
    b_std = benchmark['Daily_Ret'].std()
    b_sr = (b_mean / b_std) * np.sqrt(252) if b_std > 0 else 0
    
    print(f"--- OUT OF SAMPLE RESULTS ---")
    print(f"Duration: {years:.2f} years")
    print(f"Strategy CAGR: {cagr:.2%}")
    print(f"Strategy MDD:  {mdd:.2%}")
    print(f"Strategy SR:   {sr:.2f}")
    print(f"Benchmark CAGR: {b_cagr:.2%}")
    print(f"Benchmark MDD:  {b_mdd:.2%}")
    print(f"Benchmark SR:   {b_sr:.2f}")
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(strat_equity.index, strat_equity.values, label='v23 Strategy (OOS)', color='blue')
    plt.plot(benchmark.index, benchmark['Equity'].values, label='SPY Benchmark', color='gray', alpha=0.7)
    plt.title(f'v23 Strategy vs SPY Out-Of-Sample (Mark-to-Market)\nCAGR: {cagr:.2%} | MDD: {mdd:.2%} | SR: {sr:.2f}')
    plt.ylabel('Cumulative Equity')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plot_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\87028df4-1ec4-40e2-a989-dbc79c4b85bb\v23_equity_curve.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
if __name__ == '__main__':
    generate_report()
