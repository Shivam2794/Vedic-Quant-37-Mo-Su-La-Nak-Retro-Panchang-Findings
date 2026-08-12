import pandas as pd
import numpy as np
import optuna
import os

def simulate_trades(df, fast_period, slow_period, vol_threshold, exit_vol_threshold, sl_mult, tp_mult):
    in_position = False
    entry_price = 0.0
    sl_price = 0.0
    tp_price = 0.0
    
    trades = []
    
    fast_col = f'SMA_{int(fast_period)}'
    slow_col = f'SMA_{int(slow_period)}'
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # Check Entry
        if not in_position:
            if prev_row[fast_col] > prev_row[slow_col] and prev_row['YZ_Vol'] < vol_threshold:
                in_position = True
                entry_price = row['Open']
                
                vol = prev_row['YZ_Vol']
                sl_price = entry_price * (1 - sl_mult * vol)
                tp_price = entry_price * (1 + tp_mult * vol)
                
                entry_date = df.index[i]
                entry_idx = i
                
        if in_position:
            open_price = row['Open']
            low = row['Low']
            high = row['High']
            
            exit_price = None
            exit_reason = None
            
            if open_price <= sl_price:
                exit_price = open_price 
                exit_reason = 'SL_GAP'
            elif open_price >= tp_price:
                exit_price = open_price 
                exit_reason = 'TP_GAP'
            elif low <= sl_price:
                exit_price = sl_price
                exit_reason = 'SL'
            elif high >= tp_price:
                exit_price = tp_price
                exit_reason = 'TP'
            elif (prev_row[fast_col] < prev_row[slow_col] or prev_row['YZ_Vol'] > exit_vol_threshold) and i > entry_idx: 
                exit_price = row['Open']
                exit_reason = 'Trend_Reversal'
                
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
    fast_period = trial.suggest_categorical('fast_period', [5, 10, 20, 50])
    slow_period = trial.suggest_categorical('slow_period', [50, 100, 200])
    if fast_period >= slow_period:
        return -1.0 # Invalid combination
        
    vol_threshold = trial.suggest_float('vol_threshold', 0.005, 0.03)
    exit_vol_threshold = trial.suggest_float('exit_vol_threshold', 0.02, 0.1)
    sl_mult = trial.suggest_float('sl_mult', 1.0, 10.0)
    tp_mult = trial.suggest_float('tp_mult', 1.0, 20.0)
    
    trades = simulate_trades(df, fast_period, slow_period, vol_threshold, exit_vol_threshold, sl_mult, tp_mult)
    
    if len(trades) < 20:
        return -1.0
        
    df_trades = pd.DataFrame(trades)
    
    df_trades['Entry_Time'] = pd.to_datetime(df_trades['entry_date'])
    df_trades.set_index('Entry_Time', inplace=True)
    df_trades = df_trades.sort_index()
    daily_ret = df_trades.resample('D')['return'].sum().fillna(0)
    
    if daily_ret.std() == 0:
        return -1.0
        
    total_days = (daily_ret.index[-1] - daily_ret.index[0]).days
    if total_days < 365:
        return -1.0
    
    equity = (1 + daily_ret).cumprod()
    cagr = (equity.iloc[-1] ** (365.25 / total_days)) - 1
    
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    mdd = drawdown.min()
    
    if mdd == 0:
        return cagr
        
    calmar = cagr / abs(mdd)
    return calmar

def run_grinder(ticker):
    print(f"[{ticker}] Running V22 Master Grinder (Trend-Following)...")
    latent_file = f"{ticker}_daily_V21_latent.parquet"
    if not os.path.exists(latent_file):
        print(f"File {latent_file} not found.")
        return
        
    df = pd.read_parquet(latent_file)
    
    for period in [5, 10, 20, 50, 100, 200]:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean().bfill()
    
    train_size = int(len(df) * 0.545)
    df_train = df.iloc[:train_size]
    
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, df_train), n_trials=300)
    
    best_params = study.best_params
    print(f"[{ticker}] Best Params: {best_params}")
    print(f"[{ticker}] Best IS Calmar: {study.best_value}")
    
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
        
    all_trades = simulate_trades(df, **best_params)
    trades_df = pd.DataFrame(all_trades)
    
    out_file = f"{ticker}_V22_trades.parquet"
    trades_df.to_parquet(out_file)
    print(f"Saved {len(all_trades)} trades to {out_file} for Meta-Labeling.")

if __name__ == '__main__':
    run_grinder('SPY')
