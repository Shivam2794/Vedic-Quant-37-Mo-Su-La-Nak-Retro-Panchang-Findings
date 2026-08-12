import pandas as pd
import numpy as np
import optuna
import json
import os
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

class CombinatorialPurgedCrossValidator:
    def __init__(self, n_splits=6, n_test_splits=2, purge_length=63, embargo_length=20):
        self.n_splits = n_splits
        self.n_test_splits = n_test_splits
        self.purge_length = purge_length
        self.embargo_length = embargo_length
        
    def split(self, index):
        n_samples = len(index)
        split_size = n_samples // self.n_splits
        
        # Create array of indices for each split
        splits = []
        for i in range(self.n_splits):
            start = i * split_size
            end = (i + 1) * split_size if i < self.n_splits - 1 else n_samples
            splits.append(np.arange(start, end))
            
        # Generate combinations of test splits
        test_combinations = list(combinations(range(self.n_splits), self.n_test_splits))
        
        for test_indices in test_combinations:
            test_mask = np.zeros(n_samples, dtype=bool)
            train_mask = np.ones(n_samples, dtype=bool)
            
            for test_idx in test_indices:
                t_indices = splits[test_idx]
                test_mask[t_indices] = True
                
                # Apply purge and embargo to train_mask
                start_purge = max(0, t_indices[0] - self.purge_length)
                # Purge before and after, embargo after
                end_purge_embargo = min(n_samples, t_indices[-1] + 1 + self.purge_length + self.embargo_length)
                train_mask[start_purge:end_purge_embargo] = False
                
            yield np.where(train_mask)[0], np.where(test_mask)[0]

def simulate_strategy(df, params, train_idx, test_idx):
    entry_z = params['entry_z']
    sl_mult = params['sl_mult']
    tp_mult = params['tp_mult']
    vb_mult = params['vb_mult']
    direction = params['direction']
    latent_dim = params['latent_dim']
    
    latent_col = f'Latent_{latent_dim}'
    
    if direction == 'long':
        signals = (df[latent_col] < -entry_z).astype(int)
    else: # short
        signals = (df[latent_col] > entry_z).astype(int)
        
    entry_indices = np.where(signals.values)[0]
    
    positions = np.zeros(len(df))
    net_returns = np.zeros(len(df))
    trade_starts = np.zeros(len(df))
    
    total_cost_bps = 3
    cost_dec = (total_cost_bps / 10000.0)
    
    df_vol = df['YZ_Vol'].values
    df_open = df['Open'].values
    df_high = df['High'].values
    df_low = df['Low'].values
    df_close = df['Close'].values
    
    for idx in entry_indices:
        trade_idx = idx + 1
        if trade_idx >= len(df): continue
        
        vol_t = df_vol[idx]
        if np.isnan(vol_t) or vol_t == 0: continue
        
        tp_pct = tp_mult * (vol_t / np.sqrt(252))
        sl_pct = sl_mult * (vol_t / np.sqrt(252))
        v_barrier = max(1, int(vb_mult * (0.15 / vol_t)))
        
        entry_price = df_open[trade_idx]
        hit_barrier = False
        exit_idx = trade_idx
        exit_ret = 0
        
        for k in range(v_barrier):
            curr_idx = trade_idx + k
            if curr_idx >= len(df):
                exit_idx = len(df) - 1
                if direction == 'long':
                    exit_ret = (df_close[exit_idx] / entry_price) - 1.0
                else:
                    exit_ret = (entry_price / df_close[exit_idx]) - 1.0
                hit_barrier = True
                break
                
            high_p = df_high[curr_idx]
            low_p = df_low[curr_idx]
            
            if direction == 'long':
                if low_p <= entry_price * (1 - sl_pct):
                    exit_idx = curr_idx
                    exit_ret = -sl_pct
                    hit_barrier = True
                    break
                elif high_p >= entry_price * (1 + tp_pct):
                    exit_idx = curr_idx
                    exit_ret = tp_pct
                    hit_barrier = True
                    break
            else: # short
                if high_p >= entry_price * (1 + sl_pct):
                    exit_idx = curr_idx
                    exit_ret = -sl_pct
                    hit_barrier = True
                    break
                elif low_p <= entry_price * (1 - tp_pct):
                    exit_idx = curr_idx
                    exit_ret = tp_pct
                    hit_barrier = True
                    break
                
        if not hit_barrier:
            exit_idx = min(trade_idx + v_barrier - 1, len(df) - 1)
            if direction == 'long':
                exit_ret = (df_close[exit_idx] / entry_price) - 1.0
            else:
                exit_ret = (entry_price / df_close[exit_idx]) - 1.0
            
        positions[trade_idx:exit_idx+1] += (1 if direction == 'long' else -1)
        trade_starts[trade_idx] = 1
        
        # Mark to market
        if direction == 'long':
            net_returns[trade_idx] += (df_close[trade_idx] / df_open[trade_idx] - 1.0)
            for c_idx in range(trade_idx + 1, exit_idx + 1):
                net_returns[c_idx] += (df_close[c_idx] / df_close[c_idx-1] - 1.0)
        else: # short mark to market
            net_returns[trade_idx] += (df_open[trade_idx] / df_close[trade_idx] - 1.0)
            for c_idx in range(trade_idx + 1, exit_idx + 1):
                net_returns[c_idx] += (df_close[c_idx-1] / df_close[c_idx] - 1.0)
                
        # Fix exit barrier exact price
        if hit_barrier and exit_idx > trade_idx:
            prev_close = df_close[exit_idx-1]
            if direction == 'long':
                actual_exit_price = entry_price * (1 + exit_ret)
                net_returns[exit_idx] -= (df_close[exit_idx] / prev_close - 1.0) 
                net_returns[exit_idx] += (actual_exit_price / prev_close - 1.0) 
            else:
                actual_exit_price = entry_price * (1 - exit_ret)
                net_returns[exit_idx] -= (prev_close / df_close[exit_idx] - 1.0)
                net_returns[exit_idx] += (prev_close / actual_exit_price - 1.0)
                
        elif hit_barrier and exit_idx == trade_idx:
            if direction == 'long':
                net_returns[exit_idx] -= (df_close[exit_idx] / df_open[exit_idx] - 1.0)
            else:
                net_returns[exit_idx] -= (df_open[exit_idx] / df_close[exit_idx] - 1.0)
            net_returns[exit_idx] += exit_ret
            
        net_returns[trade_idx] -= cost_dec
        net_returns[exit_idx] -= cost_dec

    test_rets = pd.Series(net_returns, index=df.index).iloc[test_idx]
    test_trades = pd.Series(trade_starts, index=df.index).iloc[test_idx]
    
    return test_rets, test_trades

def objective(trial, df):
    # Dynamically determine the maximum latent dimension present in the dataframe
    latent_cols = [c for c in df.columns if c.startswith('Latent_')]
    max_latent_idx = len(latent_cols) - 1
    
    params = {
        'entry_z': trial.suggest_float('entry_z', 1.0, 3.0),
        'sl_mult': trial.suggest_float('sl_mult', 0.5, 3.0),
        'tp_mult': trial.suggest_float('tp_mult', 0.5, 5.0),
        'vb_mult': trial.suggest_float('vb_mult', 1.0, 10.0),
        'direction': trial.suggest_categorical('direction', ['long', 'short']),
        'latent_dim': trial.suggest_int('latent_dim', 0, max_latent_idx)
    }
    
    cv = CombinatorialPurgedCrossValidator(n_splits=6, n_test_splits=2, purge_length=63, embargo_length=20)
    
    # Precompute group indices for path recombination
    n_samples = len(df)
    split_size = n_samples // 6
    group_indices = []
    for i in range(6):
        start = i * split_size
        end = (i + 1) * split_size if i < 5 else n_samples
        group_indices.append(df.index[start:end])
        
    test_combinations = list(combinations(range(6), 2))
    
    split_group_returns = {}
    split_group_trades = {}
    
    for split_idx, (train_idx, test_idx) in enumerate(cv.split(df.index)):
        net_ret_series, pos_series = simulate_strategy(df, params, train_idx, test_idx)
        
        g1, g2 = test_combinations[split_idx]
        
        split_group_returns[(split_idx, g1)] = net_ret_series.loc[group_indices[g1]].values
        split_group_returns[(split_idx, g2)] = net_ret_series.loc[group_indices[g2]].values
        
        split_group_trades[(split_idx, g1)] = pos_series.loc[group_indices[g1]].sum()
        split_group_trades[(split_idx, g2)] = pos_series.loc[group_indices[g2]].sum()
        
    # Recombine into 5 continuous paths
    group_to_splits = {g: [] for g in range(6)}
    for split_idx, test_groups in enumerate(test_combinations):
        for g in test_groups:
            group_to_splits[g].append(split_idx)
            
    paths_returns = []
    paths_trades = []
    
    for p in range(5):
        path_ret = []
        path_trade_count = 0
        for g in range(6):
            split_idx = group_to_splits[g][p]
            path_ret.append(split_group_returns[(split_idx, g)])
            path_trade_count += split_group_trades[(split_idx, g)]
            
        paths_returns.append(np.concatenate(path_ret))
        paths_trades.append(path_trade_count)
        
    # Prune if ANY path generates fewer than 50 trades
    if any(t < 50 for t in paths_trades):
        raise optuna.TrialPruned()
        
    path_sharpes = []
    for ret_arr in paths_returns:
        mean_ret = np.mean(ret_arr)
        std_ret = np.std(ret_arr)
        if std_ret == 0:
            raise optuna.TrialPruned()
        sharpe = (mean_ret / std_ret) * np.sqrt(252)
        path_sharpes.append(sharpe)
        
    path_sharpes = np.array(path_sharpes)
    sharpe_mean = np.mean(path_sharpes)
    
    return sharpe_mean

def run_v16_grinder(ticker, n_trials=1000):
    print(f"Executing V17 Core Engine Grinder for {ticker}...")
    df = pd.read_parquet(f'{ticker}_daily_V17_latent.parquet')
    df = df.reset_index(drop=True)
    
    study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(lambda trial: objective(trial, df), n_trials=n_trials, n_jobs=-1)
    
    print("Optimization finished.")
    print("Best Trial:")
    print(study.best_trial.value)
    print("Best Params:")
    print(study.best_trial.params)
    
    # Save ledger for DSR
    ledger = []
    for t in study.trials:
        if t.state == optuna.trial.TrialState.COMPLETE:
            ledger.append({
                'number': t.number,
                'value': t.value,
                'params': t.params
            })
            
    out_file = f'{ticker}_trial_ledger.json'
    with open(out_file, 'w') as f:
        json.dump(ledger, f, indent=4)
        
    print(f"[SUCCESS] Grinder finished. Ledger saved to {out_file}.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", type=str, required=True)
    parser.add_argument("--trials", type=int, default=5000)
    args = parser.parse_args()
    
    run_v16_grinder(args.ticker, n_trials=args.trials)
