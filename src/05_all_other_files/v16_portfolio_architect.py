import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import os
import scipy.stats as stats

def create_v16_report(ticker):
    print(f"Generating V16 Institutional Performance Report for {ticker}...")
    
    with open(f'{ticker}_trial_ledger.json', 'r') as f:
        ledger = json.load(f)
        
    df = pd.read_parquet(f'{ticker}_daily_V17_latent.parquet')
    df = df.reset_index(drop=True)
    
    best_trial = max(ledger, key=lambda x: x['value'])
    params = best_trial['params']
    
    df_vol = df['YZ_Vol'].values
    df_open = df['Open'].values
    df_high = df['High'].values
    df_low = df['Low'].values
    df_close = df['Close'].values
    
    sl_mult = params['sl_mult']
    tp_mult = params['tp_mult']
    vb_mult = params['vb_mult']
    
    direction = params['direction']
    latent_dim = params['latent_dim']
    latent_col = f'Latent_{latent_dim}'
    
    if direction == 'long':
        signals = (df[latent_col] < -params['entry_z']).astype(int)
    else:
        signals = (df[latent_col] > params['entry_z']).astype(int)
        
    entry_indices = np.where(signals.values)[0]
    
    net_returns = np.zeros(len(df))
    trades_executed = np.zeros(len(df))
    
    total_cost_bps = 3
    cost_dec = (total_cost_bps / 10000.0)
    
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
            else:
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
            
        # Mark to market
        if direction == 'long':
            net_returns[trade_idx] += (df_close[trade_idx] / df_open[trade_idx] - 1.0)
            for c_idx in range(trade_idx + 1, exit_idx + 1):
                net_returns[c_idx] += (df_close[c_idx] / df_close[c_idx-1] - 1.0)
        else:
            net_returns[trade_idx] += (df_open[trade_idx] / df_close[trade_idx] - 1.0)
            for c_idx in range(trade_idx + 1, exit_idx + 1):
                net_returns[c_idx] += (df_close[c_idx-1] / df_close[c_idx] - 1.0)
            
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
        trades_executed[trade_idx] = 1
        
    df['Net_Ret'] = net_returns
    T = len(net_returns)
    total_trades = int(np.sum(trades_executed))
    
    # Calculate exact trade-level win rate
    trade_returns = []
    for idx in entry_indices:
        trade_idx = idx + 1
        if trade_idx >= len(df): continue
        if trades_executed[trade_idx] == 1:
            # Reconstruct the trade return to get win rate
            vol_t = df_vol[idx]
            if np.isnan(vol_t) or vol_t == 0: continue
            tp_pct = tp_mult * (vol_t / np.sqrt(252))
            sl_pct = sl_mult * (vol_t / np.sqrt(252))
            v_barrier = max(1, int(vb_mult * (0.15 / vol_t)))
            
            entry_price = df_open[trade_idx]
            hit_barrier = False
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
                
                if direction == 'long':
                    if df_low[curr_idx] <= entry_price * (1 - sl_pct):
                        exit_ret = -sl_pct
                        hit_barrier = True
                        break
                    elif df_high[curr_idx] >= entry_price * (1 + tp_pct):
                        exit_ret = tp_pct
                        hit_barrier = True
                        break
                else: # short
                    if df_high[curr_idx] >= entry_price * (1 + sl_pct):
                        exit_ret = -sl_pct
                        hit_barrier = True
                        break
                    elif df_low[curr_idx] <= entry_price * (1 - tp_pct):
                        exit_ret = tp_pct
                        hit_barrier = True
                        break
                    
            if not hit_barrier:
                exit_idx = min(trade_idx + v_barrier - 1, len(df) - 1)
                if direction == 'long':
                    exit_ret = (df_close[exit_idx] / entry_price) - 1.0
                else:
                    exit_ret = (entry_price / df_close[exit_idx]) - 1.0
                
            net_ret = exit_ret - cost_dec * 2
            trade_returns.append(net_ret)
            
    win_rate = np.mean([1 if r > 0 else 0 for r in trade_returns]) if len(trade_returns) > 0 else 0.0
    
    mean_ret_unann = net_returns.mean()
    std_ret_unann = net_returns.std()
    sr_unann = mean_ret_unann / std_ret_unann if std_ret_unann > 0 else 0
    
    mean_ret = mean_ret_unann * 252
    std_ret = std_ret_unann * np.sqrt(252)
    sharpe = mean_ret / std_ret if std_ret > 0 else 0
    
    # Calculate DSR (Deflated Sharpe Ratio)
    sr_trials = np.array([t['value'] for t in ledger if t.get('value') is not None])
    N = 5000 # Total combinatorial trials searched
    
    if len(sr_trials) > 0:
        mean_sr = np.mean(sr_trials)
        std_sr = np.std(sr_trials, ddof=1)
        emc = 0.5772156649
        max_Z = (1 - emc) * stats.norm.ppf(1 - 1.0 / N) + emc * stats.norm.ppf(1 - 1.0 / (N * np.e))
        expected_max_sr = mean_sr + std_sr * max_Z
    else:
        expected_max_sr = 0.0
        
    skewness = stats.skew(net_returns)
    kurtosis = stats.kurtosis(net_returns, fisher=False)
    
    N = len(ledger)
    
    # Calculate DSR properly
    sr_daily = sr_unann
    if expected_max_sr > 0 and std_ret_unann > 0:
        # expected_max_sr is annualized because trial values are annualized sharpes (see master_grinder_v16.py: sharpe = (mean_ret / std_ret) * np.sqrt(252))
        expected_max_sr_daily = expected_max_sr / np.sqrt(252)
        numerator = (sr_daily - expected_max_sr_daily) * np.sqrt(T - 1)
        denominator = np.sqrt(1 - skewness * sr_daily + (kurtosis - 1) / 4.0 * (sr_daily ** 2))
        dsr = stats.norm.cdf(numerator / denominator)
    else:
        dsr = 0.0
    
    out_data = {
        'ticker': ticker,
        'trials': N,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'annual_return': mean_ret,
        'annual_volatility': std_ret,
        'sharpe': sharpe,
        'expected_max_sr': expected_max_sr,
        'dsr': dsr,
        'best_params': params
    }
    
    with open(f'{ticker}_performance.json', 'w') as f:
        json.dump(out_data, f, indent=4)
        
    print(f"[SUCCESS] Report generated for {ticker}.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", type=str, required=True)
    args = parser.parse_args()
    
    create_v16_report(args.ticker)
