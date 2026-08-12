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
    print("Generating V18 Performance Report...")
    trades_file = "SPY_V18_trades.parquet"
    if not os.path.exists(trades_file):
        print("Trades file not found.")
        return
        
    df_trades = pd.read_parquet(trades_file)
    df_trades['target'] = (df_trades['return'] > 0).astype(int)
    
    # We will compute metrics for the Out-Of-Sample period.
    # From master_grinder, train_size was int(len(df) * 0.7).
    # Since we don't have the exact split index in the trades, we can just split the trades dataframe by 70%.
    train_size = int(len(df_trades) * 0.7)
    df_oos = df_trades.iloc[train_size:].copy()
    
    start_date = df_oos['entry_date'].min()
    end_date = df_oos['exit_date'].max()
    
    print(f"OOS Duration: {start_date.date()} to {end_date.date()}")
    
    # Download benchmark SPY
    benchmark = yf.download("SPY", start=start_date, end=end_date)
    benchmark['Daily_Ret'] = benchmark['Close'].pct_change().fillna(0)
    benchmark['Equity'] = (1 + benchmark['Daily_Ret']).cumprod()
    
    # Construct Strategy Equity Curve
    # To keep it simple and accurate, we take a starting capital of 1.0.
    # At each trade entry, we invest 100% (or the Kelly fraction, but let's assume 100% of allocated capital for SR comparison)
    # Actually, we use the Fractional Kelly sizing cap of 10% from the meta labeler!
    # But for raw strategy performance comparison, 1x leverage of the capital used is standard.
    # Let's plot 1x leverage.
    
    strat_daily = pd.DataFrame(index=benchmark.index)
    strat_daily['Strat_Ret'] = 0.0
    
    # Since we can hold only 1 trade at a time, we map the trade returns.
    # If a trade takes N days, we could distribute the return, or just add it on the exit day.
    # For daily sharpe, it's better to distribute it evenly or take the exact daily price.
    # To be perfectly accurate, we just compound the trade returns on the exit dates.
    
    strat_equity = pd.Series(1.0, index=benchmark.index)
    current_equity = 1.0
    
    for idx, row in df_oos.iterrows():
        exit_date = row['exit_date']
        # Find the closest date in index
        if exit_date in strat_equity.index:
            current_equity *= (1 + row['return'])
            strat_equity.loc[exit_date:] = current_equity
            
    # Calculate daily returns of the strategy equity curve for Sharpe
    strat_daily_ret = strat_equity.pct_change().fillna(0)
    
    # Alternatively, just use the raw trade returns for Sharpe (which we did in Grinder)
    trade_returns = df_oos['return'].values
    win_rate = sum(trade_returns > 0) / len(trade_returns)
    mean_ret = np.mean(trade_returns)
    std_ret = np.std(trade_returns)
    sr = (mean_ret / std_ret) * np.sqrt(252 / np.mean(df_oos['bars_held'])) if std_ret > 0 else 0
    
    # Calculate CAGR and MDD from the equity curve
    years = (end_date - start_date).days / 365.25
    cagr = calculate_cagr(strat_equity, years)
    mdd = calculate_drawdown(strat_equity)
    
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
    plt.plot(strat_equity.index, strat_equity.values, label='V18 Strategy (OOS)', color='blue')
    plt.plot(benchmark.index, benchmark['Equity'].values, label='SPY Benchmark', color='gray', alpha=0.7)
    plt.title(f'V18 Strategy vs SPY Out-Of-Sample\nCAGR: {cagr:.2%} | MDD: {mdd:.2%} | SR: {sr:.2f}')
    plt.ylabel('Cumulative Equity')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save plot for artifact
    plot_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\87028df4-1ec4-40e2-a989-dbc79c4b85bb\v18_equity_curve.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
if __name__ == '__main__':
    generate_report()
