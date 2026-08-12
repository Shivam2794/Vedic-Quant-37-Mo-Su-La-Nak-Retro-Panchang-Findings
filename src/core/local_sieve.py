"""
Production Statistical Sieve (Phase 1.7) — High-Performance Version
===================================================================
Processes one ticker at a time using vectorized numpy arrays.
"""
import pandas as pd
import numpy as np
import glob
import os
import json
from scipy import stats
from collections import defaultdict
import time

FEATURES_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"
DEDUP_RULES_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\compiled_rules_deduped.json"
OUTPUT_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sieve_candidates.csv"

# Sieve thresholds
MIN_ACTIVATION_RATE = 0.01
MAX_ACTIVATION_RATE = 0.50
MIN_ABS_DIFF_RETURN = 0.003
MIN_ABS_CORRELATION = 0.015
TRANSACTION_COST = 0.0005

HORIZONS = ['fwd_return_1d', 'fwd_return_5d', 'fwd_return_10d', 'fwd_return_21d', 'fwd_return_63d']
HORIZON_LABELS = {'fwd_return_1d':'1D', 'fwd_return_5d':'5D', 'fwd_return_10d':'10D', 
                  'fwd_return_21d':'21D', 'fwd_return_63d':'63D'}

def run_sieve():
    start_time = time.time()
    print("=" * 60)
    print("PRODUCTION STATISTICAL SIEVE (High-Performance)")
    print("=" * 60)
    
    ret_df = pd.read_parquet(RETURNS_PATH)
    ret_df['date_key'] = pd.to_datetime(ret_df['date']).dt.date.astype(str)
    
    with open(DEDUP_RULES_PATH, "r") as f:
        dedup_rules = list(json.load(f).keys())
    dedup_rule_cols = [f"rule_{r}" for r in dedup_rules]
    
    ticker_dirs = [d for d in os.listdir(FEATURES_DIR) if d.startswith("ticker=")]
    tickers = [d.split("=")[1] for d in ticker_dirs]
    
    rule_active = defaultdict(list)
    rule_inactive = defaultdict(list)
    rule_total_active = defaultdict(int)
    rule_total_count = defaultdict(int)
    
    for ti, ticker in enumerate(tickers):
        t0 = time.time()
        ticker_path = os.path.join(FEATURES_DIR, f"ticker={ticker}")
        year_files = glob.glob(os.path.join(ticker_path, "**", "*.parquet"), recursive=True)
        
        if not year_files:
            continue
            
        ticker_dfs = [pd.read_parquet(f) for f in year_files]
        feat = pd.concat(ticker_dfs, ignore_index=True)
        # Fix fragmentation by copying
        feat = feat.copy()
        feat['date_key'] = pd.to_datetime(feat['date']).dt.date.astype(str)
        
        ret_ticker = ret_df[ret_df['ticker'] == ticker]
        merged = feat.merge(ret_ticker[['date_key'] + HORIZONS], on='date_key', how='inner')
        
        available_rules = [c for c in dedup_rule_cols if c in merged.columns]
        
        for rule_col in available_rules:
            rule_vals = merged[rule_col].values
            rule_total_count[rule_col] += len(rule_vals)
            rule_total_active[rule_col] += int(rule_vals.sum())
            
            for ret_col in HORIZONS:
                ret_vals = merged[ret_col].values
                valid = ~np.isnan(ret_vals)
                rv = rule_vals[valid]
                retv = ret_vals[valid]
                
                active_mask = rv == 1.0
                if active_mask.any():
                    rule_active[(rule_col, ret_col)].append(retv[active_mask])
                if (~active_mask).any():
                    rule_inactive[(rule_col, ret_col)].append(retv[~active_mask])
        
        t1 = time.time()
        if (ti + 1) % 5 == 0:
            print(f"  Processed {ti+1}/{len(tickers)} tickers (Last ticker took {t1-t0:.2f}s)")
    
    print(f"\nComputing final sieve metrics...")
    
    results = []
    for rule_col in dedup_rule_cols:
        total = rule_total_count.get(rule_col, 0)
        active = rule_total_active.get(rule_col, 0)
        if total == 0:
            continue
            
        activation_rate = active / total
        if activation_rate < MIN_ACTIVATION_RATE or activation_rate > MAX_ACTIVATION_RATE:
            continue
        
        for ret_col in HORIZONS:
            key = (rule_col, ret_col)
            # Concatenate list of numpy arrays
            act_rets = np.concatenate(rule_active[key]) if key in rule_active else np.array([])
            inact_rets = np.concatenate(rule_inactive[key]) if key in rule_inactive else np.array([])
            
            if len(act_rets) < 20:
                continue
                
            mean_active = np.mean(act_rets)
            std_active = np.std(act_rets)
            mean_inactive = np.mean(inact_rets) if len(inact_rets) > 0 else 0
            diff_return = mean_active - mean_inactive
            cost_adj_ir = (mean_active - TRANSACTION_COST) / std_active if std_active > 0 else 0
            
            all_rets = np.concatenate([act_rets, inact_rets])
            all_rules = np.concatenate([np.ones(len(act_rets)), np.zeros(len(inact_rets))])
            corr, p_val = stats.pearsonr(all_rules, all_rets)
            
            results.append({
                'rule_name': rule_col.replace('rule_', ''),
                'horizon': HORIZON_LABELS[ret_col],
                'activation_rate': round(activation_rate, 4),
                'n_active': len(act_rets),
                'mean_return_active': round(mean_active, 6),
                'mean_return_inactive': round(mean_inactive, 6),
                'differential_return': round(diff_return, 6),
                'std_return_active': round(std_active, 6),
                'cost_adjusted_ir': round(cost_adj_ir, 4),
                'pearson_corr': round(corr, 6),
                'p_value': round(p_val, 6),
            })
    
    results_df = pd.DataFrame(results)
    candidates = results_df[
        (results_df['activation_rate'] >= MIN_ACTIVATION_RATE) &
        (results_df['activation_rate'] <= MAX_ACTIVATION_RATE) &
        (
            (results_df['differential_return'].abs() > MIN_ABS_DIFF_RETURN) |
            (results_df['pearson_corr'].abs() > MIN_ABS_CORRELATION)
        )
    ].sort_values('cost_adjusted_ir', ascending=False)
    
    candidates.to_csv(OUTPUT_PATH, index=False)
    
    print("\n" + "=" * 60)
    print(f"SIEVE COMPLETE (Took {time.time()-start_time:.1f}s)")
    print("=" * 60)
    print(f"Candidates surviving sieve: {len(candidates)}")
    print(f"Unique rules surviving: {candidates['rule_name'].nunique()}")
    print("\nTop 15 by Cost-Adjusted IR:")
    print(candidates.head(15).to_string(index=False))

if __name__ == "__main__":
    run_sieve()
