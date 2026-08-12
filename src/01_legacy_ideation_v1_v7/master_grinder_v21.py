import pandas as pd
import numpy as np
import optuna
import os
from joblib import Parallel, delayed

def simulate_trades(df, rsi_buy, rsi_sell, sl_mult, tp_mult, vol_threshold, sma_period):
    in_position = False
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    
    trades = []
    
    # Calculate dynamic SMA
    sma_col = f'SMA_{int(sma_period)}'
    if sma_col not in df.columns:
        df = df.copy()
        df[sma_col] = df['Close'].rolling(window=int(sma_period)).mean().bfill()
        
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # Check Entry
        if not in_position:
            if prev_row['RSI_14'] < rsi_buy and prev_row['Close'] > prev_row[sma_col] and prev_row['YZ_Vol'] < vol_threshold:
                in_position = True
                entry_price = row['Open']
                
                # Volatility-based SL/TP using YZ_Vol
                vol = prev_row['YZ_Vol']
                sl_price = entry_price * (1 - sl_mult * vol)
                tp_price = entry_price * (1 + tp_mult * vol)
                
                entry_date = df.index[i]
                entry_idx = i
                
        # We DO NOT use an else block.
        # If we entered today, we can also exit today (same-day exit).
        if in_position:
            # Check SL / TP
            open_price = row['Open']
            low = row['Low']
            high = row['High']
            
            exit_price = None
            exit_reason = None
            
            # Check if market gapped down below SL
            if open_price <= sl_price:
                exit_price = open_price # Slipped to open
                exit_reason = 'SL_GAP'
            # Check if market gapped up above TP
            elif open_price >= tp_price:
                exit_price = open_price # Slipped to open
                exit_reason = 'TP_GAP'
            elif low <= sl_price:
                exit_price = sl_price
                exit_reason = 'SL'
            elif high >= tp_price:
                exit_price = tp_price
                exit_reason = 'TP'
            elif prev_row['RSI_14'] > rsi_sell and i > entry_idx: # Prevent same-day signal exit
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
    rsi_buy = trial.suggest_float('rsi_buy', 10.0, 70.0)
    rsi_sell = trial.suggest_float('rsi_sell', 50.0, 90.0)
    sl_mult = trial.suggest_float('sl_mult', 0.5, 5.0)
    tp_mult = trial.suggest_float('tp_mult', 1.0, 10.0)
    vol_threshold = trial.suggest_float('vol_threshold', 0.005, 0.05)
    sma_period = trial.suggest_categorical('sma_period', [20, 50, 100, 200])
    
    trades = simulate_trades(df, rsi_buy, rsi_sell, sl_mult, tp_mult, vol_threshold, sma_period)
    
    if len(trades) < 50:
        return -1.0
        
    df_trades = pd.DataFrame(trades)
    
    # Calculate daily returns
    df_trades['Entry_Time'] = pd.to_datetime(df_trades['entry_date'])
    df_trades.set_index('Entry_Time', inplace=True)
    df_trades = df_trades.sort_index()
    daily_ret = df_trades.resample('D')['return'].sum().fillna(0)
    
    if daily_ret.std() == 0:
        return -1.0
        
    # Calculate CAGR
    total_days = (daily_ret.index[-1] - daily_ret.index[0]).days
    if total_days < 365:
        return -1.0
    
    equity = (1 + daily_ret).cumprod()
    cagr = (equity.iloc[-1] ** (365.25 / total_days)) - 1
    
    # Calculate MDD
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    mdd = drawdown.min()
    
    if mdd == 0:
        return cagr
        
    calmar = cagr / abs(mdd)
    return calmar

def run_grinder(ticker):
    print(f"[{ticker}] Running V21 Master Grinder (18% CAGR Singularity)...")
    latent_file = f"{ticker}_daily_V21_latent.parquet"
    if not os.path.exists(latent_file):
        print(f"File {latent_file} not found. Ensure latent encoder ran.")
        return
        
    df = pd.read_parquet(latent_file)
    
    # Calculate all potential SMAs for Trend Filter
    for period in [20, 50, 100, 200]:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean().bfill()
    
    
    # We only use in-sample data for grinding to prevent lookahead
    # V21: 54.5% split gives exactly 15 years out of sample (2011 to 2026)
    train_size = int(len(df) * 0.545)
    df_train = df.iloc[:train_size]
    
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, df_train), n_trials=300)
    
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
    
    out_file = f"{ticker}_V21_trades.parquet"
    trades_df.to_parquet(out_file)
    print(f"Saved {len(all_trades)} trades to {out_file} for Meta-Labeling.")

if __name__ == '__main__':
    run_grinder('SPY')
