import os
import json
import optuna
import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import warnings

# Suppress optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings('ignore')

import master_grinder_v12 as mg

def objective_grand_portfolio(trial, df):
    """
    Optuna objective function for a specific dataframe window.
    """
    params = {
        # Multi-Day Trend
        'md_rsi_min': trial.suggest_float('md_rsi_min', 30, 50),
        'md_rsi_max': trial.suggest_float('md_rsi_max', 60, 90),
        'md_roc5_min': trial.suggest_float('md_roc5_min', 0.0, 0.05),
        'md_accel_min': trial.suggest_float('md_accel_min', 0.0, 0.03),
        'md_hold_days': trial.suggest_int('md_hold_days', 2, 10),
        'md_target_vol': trial.suggest_float('md_target_vol', 0.1, 0.4),
        'md_max_size': trial.suggest_float('md_max_size', 0.5, 1.0),
        
        # Intraday
        'id_rsi_min': trial.suggest_float('id_rsi_min', 20, 45),
        'id_rsi_max': trial.suggest_float('id_rsi_max', 50, 75),
        'id_gap_max': trial.suggest_float('id_gap_max', 0.005, 0.03),
        'id_vol_ratio': trial.suggest_float('id_vol_ratio', 0.0, 0.5),
        'id_tp': trial.suggest_float('id_tp', 1.0, 10.0),
        'id_sl': trial.suggest_float('id_sl', 1.0, 10.0),
        'id_target_vol': trial.suggest_float('id_target_vol', 0.3, 0.8),
        
        # Overnight
        'on_rsi_min': trial.suggest_float('on_rsi_min', 30, 60),
        'on_rsi_max': trial.suggest_float('on_rsi_max', 65, 95),
        'on_roc5_min': trial.suggest_float('on_roc5_min', 0.0, 0.05),
        'on_accel_min': trial.suggest_float('on_accel_min', 0.0, 0.03),
        'on_target_vol': trial.suggest_float('on_target_vol', 0.2, 0.6)
    }
    
    pnl, trades = mg.strategy_grand_portfolio(df, params)
    trades = int(np.sum(trades))
    
    # Calculate Sharpe
    if trades < 5:  # Require at least 5 trades in a train window to prevent trivial fits
        return -999.0
        
    mean_ret = np.mean(pnl)
    std_ret = np.std(pnl)
    
    if std_ret == 0:
        return -999.0
        
    sharpe = (mean_ret / std_ret) * np.sqrt(252)
    
    return sharpe

def run_wfo():
    print("="*60)
    print("V13 INSTITUTIONAL WALK-FORWARD OPTIMIZATION (WFO)")
    print("="*60)
    
    print("[INFO] Booting Data Pipeline...")
    qqq_d, qqq_1m, tqqq_1m = mg.load_all_data()
    daily_feats = mg.build_daily_features(qqq_d)
    intraday_lk = mg.build_intraday_lookup(qqq_1m, tqqq_1m)
    signal_df = intraday_lk.join(daily_feats, how='inner').dropna()
    print(f"[INFO] Signal Matrix Ready: {len(signal_df)} days")
    
    # Convert index to DatetimeIndex to easily use relativedelta slicing
    signal_df.index = pd.to_datetime([str(d) for d in signal_df.index])
    
    start_date = signal_df.index.min()
    end_date = signal_df.index.max()
    
    print(f"[WFO] Dataset spans from {start_date.date()} to {end_date.date()}")
    
    train_months = 24  # 2 years
    test_months = 6    # 6 months
    
    current_train_start = start_date
    oos_pnl = []
    oos_dates = []
    window_count = 1
    
    wfo_history = []
    
    while True:
        train_end = current_train_start + relativedelta(months=train_months)
        test_end = train_end + relativedelta(months=test_months)
        
        if test_end > end_date:
            # We can allow the final test window to be shorter than 6 months
            test_end = end_date
            if train_end >= end_date:
                break
                
        # Slice datasets
        train_df = signal_df[(signal_df.index >= current_train_start) & (signal_df.index < train_end)]
        test_df = signal_df[(signal_df.index >= train_end) & (signal_df.index <= test_end)]
        
        if len(train_df) < 200 or len(test_df) < 10:
            print(f"[WFO] Window {window_count} has insufficient data. Stopping.")
            break
            
        print(f"\n[WINDOW {window_count}]")
        print(f"  TRAIN: {current_train_start.date()} to {train_end.date()} ({len(train_df)} days)")
        print(f"  TEST : {train_end.date()} to {test_end.date()} ({len(test_df)} days)")
        
        # Optimize on Train
        study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler())
        # Wrap objective to pass train_df
        obj = lambda trial: objective_grand_portfolio(trial, train_df)
        
        # Run optimization
        print(f"  -> Optimizing 1500 trials on Train data...", flush=True)
        study.optimize(obj, n_trials=1500, n_jobs=1)
        
        best_params = study.best_params
        best_train_sharpe = study.best_value
        
        # Evaluate on Test
        print(f"  -> Evaluating best parameters on unseen Test data...")
        test_pnl, test_trades = mg.strategy_grand_portfolio(test_df, best_params)
        
        # Calculate OOS Sharpe
        if np.std(test_pnl) > 0:
            oos_sharpe = (np.mean(test_pnl) / np.std(test_pnl)) * np.sqrt(252)
        else:
            oos_sharpe = 0.0
            
        print(f"  -> IS Sharpe: {best_train_sharpe:.2f} | OOS Sharpe: {oos_sharpe:.2f} | OOS Trades: {int(np.sum(test_trades))}")
        
        # Store results
        oos_pnl.extend(test_pnl)
        oos_dates.extend(test_df.index.strftime('%Y-%m-%d').tolist())
        
        wfo_history.append({
            'window': window_count,
            'train_start': str(current_train_start.date()),
            'train_end': str(train_end.date()),
            'test_end': str(test_end.date()),
            'is_sharpe': best_train_sharpe,
            'oos_sharpe': oos_sharpe,
            'params': best_params
        })
        
        # Step forward
        current_train_start += relativedelta(months=test_months)
        window_count += 1
        
    print("\n" + "="*60)
    print("WFO PROCESS COMPLETE")
    print("="*60)
    
    # Save to JSON
    output = {
        'oos_pnl': oos_pnl,
        'oos_dates': oos_dates,
        'wfo_history': wfo_history
    }
    
    with open('wfo_v13_oos_results.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print("[INFO] WFO results saved to wfo_v13_oos_results.json")
    
if __name__ == '__main__':
    run_wfo()
