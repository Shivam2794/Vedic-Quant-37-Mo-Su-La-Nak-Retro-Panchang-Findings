import pandas as pd
import numpy as np

def compile_v21_portfolio():
    print("Compiling v21 Concurrency-Aware Portfolio (with XGBoost Meta-Label Filtering)...")
    
    tickers = ['SPY']
    all_trades = []
    
    for ticker in tickers:
        trades_file = f"{ticker}_V21_trades.parquet"
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
    
    total_signals = len(df)
    
    # FILTER TRADES USING META LABELER APPROVAL
    if 'meta_label_approve' in df.columns:
        df = df[df['meta_label_approve'] == 1]
    
    total_approved = len(df)
    print(f"Total base signals generated: {total_signals}")
    print(f"Total signals approved by XGBoost: {total_approved}")
    
    # Simulate realistic concurrency across the portfolio
    portfolio_trades = []
    current_exit = None
    
    for _, row in df.iterrows():
        if current_exit is None or row['entry_date'] > current_exit:
            portfolio_trades.append(row)
            current_exit = row['exit_date']
            
    df_port = pd.DataFrame(portfolio_trades)
    print(f"Total concurrent-safe trades executed: {len(df_port)}")
    
    if len(df_port) == 0:
        print("No trades left in portfolio.")
        return
        
    returns = df_port['return'].values
    win_rate = sum(returns > 0) / len(returns)
    mean_ret = np.mean(returns)
    std_ret = np.std(returns)
    sharpe = (mean_ret / std_ret) * np.sqrt(252 / np.mean(df_port['bars_held'])) if std_ret > 0 else 0
    
    print(f"v21 Portfolio Win Rate: {win_rate:.2%}")
    print(f"v21 Portfolio Sharpe:   {sharpe:.2f}")
    
    df_port.to_parquet('portfolio_v21_executed_trades.parquet')
    print("Executed trades saved to portfolio_v21_executed_trades.parquet")

if __name__ == '__main__':
    compile_v21_portfolio()
