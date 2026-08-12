import pandas as pd
import numpy as np

def compile_v18_portfolio():
    print("Compiling V18 Concurrency-Aware Portfolio...")
    
    # In a full run, we would iterate over multiple tickers
    tickers = ['SPY']
    all_trades = []
    
    for ticker in tickers:
        trades_file = f"{ticker}_V18_trades.parquet"
        try:
            df_trades = pd.read_parquet(trades_file)
            df_trades['ticker'] = ticker
            all_trades.append(df_trades)
        except:
            continue
            
    if not all_trades:
        print("No trades found.")
        return
        
    df = pd.concat(all_trades, ignore_index=True)
    df = df.sort_values('entry_date')
    
    # Simulate realistic concurrency across the portfolio
    # A simple single-thread portfolio constraint: we can only hold 1 asset at a time
    portfolio_trades = []
    current_exit = None
    
    for _, row in df.iterrows():
        if current_exit is None or row['entry_date'] > current_exit:
            portfolio_trades.append(row)
            current_exit = row['exit_date']
            
    df_port = pd.DataFrame(portfolio_trades)
    print(f"Total possible signals: {len(df)}")
    print(f"Total concurrent-safe trades: {len(df_port)}")
    
    returns = df_port['return'].values
    win_rate = sum(returns > 0) / len(returns)
    mean_ret = np.mean(returns)
    std_ret = np.std(returns)
    sharpe = (mean_ret / std_ret) * np.sqrt(252 / np.mean(df_port['bars_held'])) if std_ret > 0 else 0
    
    print(f"V18 Portfolio Win Rate: {win_rate:.2%}")
    print(f"V18 Portfolio Sharpe:   {sharpe:.2f}")

if __name__ == '__main__':
    compile_v18_portfolio()
