import pandas as pd
import numpy as np
import optuna
import os
import yfinance as yf
from joblib import Parallel, delayed

def simulate_trades(df, rsi_buy, rsi_sell, sl_mult, tp_mult):
    in_position = False
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    
    trades = []
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        if not in_position:
            # RSI Mean Reversion Entry
            if prev_row['RSI_14'] < rsi_buy:
                in_position = True
                entry_price = row['Open']
                
                # Volatility-based SL/TP using YZ_Vol
                vol = prev_row['YZ_Vol']
                sl_price = entry_price * (1 - sl_mult * vol)
                tp_price = entry_price * (1 + tp_mult * vol)
                
                entry_date = df.index[i]
                entry_idx = i
        else:
            # Check SL / TP
            low = row['Low']
            high = row['High']
            close = row['Close']
            
            exit_price = None
            exit_reason = None
            
            if low <= sl_price:
                exit_price = sl_price
                exit_reason = 'SL'
            elif high >= tp_price:
                exit_price = tp_price
                exit_reason = 'TP'
            elif prev_row['RSI_14'] > rsi_sell:
                # Time/Condition exit
                exit_price = row['Open']
                exit_reason = 'Signal_Exit'
                
            if exit_price is not None:
                ret = (exit_price - entry_price) / entry_price
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': df.index[i],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return': ret,
                    'reason': exit_reason,
                    'bars_held': i - entry_idx
                })
                in_position = False
                
    return trades

def objective(trial, df):
    rsi_buy = trial.suggest_float('rsi_buy', 10.0, 45.0)
    rsi_sell = trial.suggest_float('rsi_sell', 55.0, 90.0)
    sl_mult = trial.suggest_float('sl_mult', 0.5, 5.0)
    tp_mult = trial.suggest_float('tp_mult', 0.5, 10.0)
    
    trades = simulate_trades(df, rsi_buy, rsi_sell, sl_mult, tp_mult)
    
    if len(trades) < 25:
        return -1.0 # Penalize too few trades
        
    returns = [t['return'] for t in trades]
    win_rate = sum(1 for r in returns if r > 0) / len(returns)
    
    if win_rate < 0.40:
        return -1.0 # Penalize sub-40% win rate (absolute minimum for structured signal)
        
    mean_ret = np.mean(returns)
    std_ret = np.std(returns) if np.std(returns) > 0 else 1e-6
    sharpe = (mean_ret / std_ret) * np.sqrt(252 / np.mean([t['bars_held'] for t in trades]))
    
    return sharpe

def run_grinder(ticker):
    print(f"[{ticker}] Running V18 Master Grinder (Structural RSI Edge with Concurrency Limits)...")
    latent_file = f"{ticker}_daily_V18_latent.parquet"
    if not os.path.exists(latent_file):
        print(f"File {latent_file} not found. Ensure latent encoder ran.")
        return
        
    df = pd.read_parquet(latent_file)
    
    # We only use in-sample data for grinding to prevent lookahead
    train_size = int(len(df) * 0.7)
    df_train = df.iloc[:train_size]
    
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, df_train), n_trials=200)
    
    best_params = study.best_params
    print(f"[{ticker}] Best Params: {best_params}")
    print(f"[{ticker}] Best IS Sharpe: {study.best_value}")
    
    # Run Out-Of-Sample
    df_test = df.iloc[train_size:]
    oos_trades = simulate_trades(df_test, **best_params)
    
    if len(oos_trades) > 0:
        oos_returns = [t['return'] for t in oos_trades]
        oos_win_rate = sum(1 for r in oos_returns if r > 0) / len(oos_returns)
        mean_ret = np.mean(oos_returns)
        std_ret = np.std(oos_returns) if np.std(oos_returns) > 0 else 1e-6
        oos_sharpe = (mean_ret / std_ret) * np.sqrt(252 / np.mean([t['bars_held'] for t in oos_trades]))
        print(f"[{ticker}] OOS Sharpe: {oos_sharpe:.2f} | OOS Win Rate: {oos_win_rate:.2%}")
    else:
        print(f"[{ticker}] No OOS trades generated.")
        
    # Generate full dataset of trades for Meta-Labeling
    all_trades = simulate_trades(df, **best_params)
    trades_df = pd.DataFrame(all_trades)
    
    out_file = f"{ticker}_V18_trades.parquet"
    trades_df.to_parquet(out_file)
    print(f"Saved {len(all_trades)} trades to {out_file} for Meta-Labeling.")

if __name__ == '__main__':
    run_grinder('SPY')
