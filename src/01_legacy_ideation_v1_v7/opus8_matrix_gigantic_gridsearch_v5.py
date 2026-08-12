import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import yfinance as yf
import numba
import os
import itertools
import time

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
OUT_FILE = os.path.join(IN_DIR, 'opus8_gridsearch_absolution_wfo_results.csv')
WFO_RETURNS_FILE = os.path.join(IN_DIR, 'opus8_portfolio_returns.csv')

UNIVERSE = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'TQQQ', 'UPRO']
MACRO    = ['HYG', 'LQD', 'XLY', 'XLP', 'XLU', '^VIX']

FAMILIES = [
    'MACD', 'EMA3', 'TEMA', 'TEMA_SIG', 'AROON', 'RSI', 'RSI_CUMRET', 
    'KAMA', 'DONCHIAN', 'ALMA', 'GJR_GARCH', 'BB', 'STC', 'SUPERTREND', 'ADX',
    'FTI', 'AUTOCORR', 'HURST', 'ENTROPY', 'SMA200'
]
TREND_FAMILIES = [f for f in FAMILIES if f not in ['AUTOCORR', 'HURST', 'ENTROPY', 'SMA200', 'GJR_GARCH']]

TOP_K_PARAMS_PER_FAMILY = 3
MIN_ACTIVE_DAYS = 30
TC_BPS = 0.0005 # 5 bps

IS_WINDOW = 504
OOS_WINDOW = 126

LOGIC_NAMES = ['OR', 'AND', 'MAJORITY', 'CONTINUOUS', 'ASYMMETRIC']

@numba.njit(fastmath=False)
def eval_logic_gate(votes, n_fams, logic_idx):
    if logic_idx == 0:
        return 1.0 if votes > 0 else 0.0 # OR
    elif logic_idx == 1:
        return 1.0 if votes == n_fams else 0.0 # AND
    elif logic_idx == 2:
        return 1.0 if votes >= np.ceil(n_fams/2.0) else 0.0 # MAJORITY
    elif logic_idx == 3:
        return votes / float(n_fams) # CONTINUOUS
    elif logic_idx == 4:
        return 1.0 if votes == n_fams else votes / (n_fams * 2.0) # ASYMMETRIC
    return 0.0

@numba.njit(parallel=True, fastmath=False)
def eval_single_fam_wfo(mat, rets, macro_overlay, vix_crash, apply_macro, annualizer, W):
    N = mat.shape[1]
    sharpes_out = np.full((N, W), -999.0)
    
    for i in numba.prange(N):
        s = mat[:, i]
        for w in range(W):
            start_is = w * OOS_WINDOW
            end_is = start_is + IS_WINDOW
            
            mean_0 = 0.0
            m2_0 = 0.0
            prev_0 = 0.0
            n_act_0 = 0
            traded_days = 0
            
            for t in range(start_is, end_is):
                if np.isnan(rets[t]): continue
                traded_days += 1
                
                t0 = 0.0
                if t > 0 and not (apply_macro and vix_crash[t-1]):
                    if s[t-1]: t0 = 1.0
                    if apply_macro and not macro_overlay[t-1]: t0 = 0.0
                        
                r = rets[t]
                ra = (r * t0) - (abs(t0 - prev_0) * TC_BPS)
                delta = ra - mean_0
                mean_0 += delta / traded_days
                m2_0 += delta * (ra - mean_0)
                
                if t0 > 0: n_act_0 += 1
                prev_0 = t0
                
            if m2_0 > 0 and n_act_0 >= MIN_ACTIVE_DAYS:
                if traded_days > 1:
                    sharpes_out[i, w] = (mean_0 / np.sqrt(m2_0 / (traded_days-1))) * annualizer
                
    return sharpes_out

@numba.njit(parallel=True, fastmath=False)
def eval_pairs_wfo(mat_a, mat_b, idx_a, idx_b, rets, macro_overlay, vix_crash, apply_macro, annualizer, w):
    N = len(idx_a)
    sharpes_out = np.full((N, 5), -999.0)
    
    start_is = w * OOS_WINDOW
    end_is = start_is + IS_WINDOW
    
    for i in numba.prange(N):
        ia, ib = idx_a[i], idx_b[i]
        
        # FATAL FLAW #1 FIXED: Correctly slice across the time dimension
        sa, sb = mat_a[:, ia], mat_b[:, ib]
        
        means = np.zeros(5)
        m2s = np.zeros(5)
        prevs = np.zeros(5)
        n_acts = np.zeros(5, dtype=np.int32)
        traded_days = 0
        
        for t in range(start_is, end_is):
            if np.isnan(rets[t]): continue
            traded_days += 1
            
            t_vals = np.zeros(5)
            
            if t > 0 and not (apply_macro and vix_crash[t-1]):
                a, b = sa[t-1], sb[t-1]
                # FATAL FLAW #2 FIXED: Explicitly cast to prevent boolean promotion (True+True=True)
                votes = int(a) + int(b)
                
                for logic_idx in range(5):
                    t_vals[logic_idx] = eval_logic_gate(votes, 2, logic_idx)
                    
                if apply_macro and not macro_overlay[t-1]:
                    t_vals[:] = 0.0
            
            r = rets[t]
            
            for logic_idx in range(5):
                t_val = t_vals[logic_idx]
                ra = (r * t_val) - (abs(t_val - prevs[logic_idx]) * TC_BPS)
                delta = ra - means[logic_idx]
                means[logic_idx] += delta / traded_days
                m2s[logic_idx] += delta * (ra - means[logic_idx])
                
                if t_val > 0: n_acts[logic_idx] += 1
                prevs[logic_idx] = t_val 
                
        if traded_days > 1:
            for logic_idx in range(5):
                if m2s[logic_idx] > 0 and n_acts[logic_idx] >= MIN_ACTIVE_DAYS:
                    sharpes_out[i, logic_idx] = (means[logic_idx] / np.sqrt(m2s[logic_idx] / (traded_days-1))) * annualizer

    return sharpes_out

def build_oos_return(mat_list, indices, logic_idx, rets, macro_overlay, vix_crash, apply_macro, start_oos, end_oos, initial_prev_inv):
    out = np.full(end_oos - start_oos, np.nan)
    prev_inv = initial_prev_inv
            
    for t in range(start_oos, end_oos):
        if t >= len(rets): break
        if np.isnan(rets[t]): continue
        
        t0 = 0.0
        
        if t > 0 and not (apply_macro and vix_crash[t-1]):
            # Cast to int to prevent boolean promotion here as well!
            votes = sum([int(mat_list[k][t-1, indices[k]]) for k in range(len(mat_list))])
            n_fams = len(mat_list)
            
            t0 = eval_logic_gate(votes, n_fams, logic_idx)
            
            if apply_macro and not macro_overlay[t-1]:
                t0 = 0.0
                
        r = rets[t]
        ra = (r * t0) - (abs(t0 - prev_inv) * TC_BPS)
        out[t - start_oos] = ra
        prev_inv = t0
        
    return out, prev_inv

def run_wfo():
    print("Starting Nested Walk-Forward Gridsearch (Absolution Edition v5)...")
    
    macro_df = yf.download(MACRO, start='1999-01-01', progress=False, auto_adjust=True)
    if isinstance(macro_df.columns, pd.MultiIndex):
        macro_df = macro_df['Close']
        
    df_dates = np.load(os.path.join(IN_DIR, 'dates.npy'), allow_pickle=True)
    macro_df = macro_df.reindex(df_dates).ffill()
    
    hyg_lqd = macro_df['HYG'] / macro_df['LQD']
    hyg_lqd_ma = hyg_lqd.rolling(50).mean()
    credit_risk_on = (hyg_lqd > hyg_lqd_ma) | hyg_lqd_ma.isna()
    
    xly_xlp = macro_df['XLY'] / macro_df['XLP']
    xly_xlp_ma = xly_xlp.rolling(50).mean()
    econ_risk_on = (xly_xlp > xly_xlp_ma) | xly_xlp_ma.isna()
    
    macro_overlay = (credit_risk_on | econ_risk_on).values
    vix = macro_df['^VIX'].fillna(0).values
    vix_crash = (vix > 40)
    
    T = len(df_dates)
    W = (T - IS_WINDOW) // OOS_WINDOW
    if W <= 0:
        return
        
    print(f"Total Windows: {W}")
    
    portfolio_dict = {}
    
    for ticker in UNIVERSE:
        print(f"\n--- {ticker} ---")
        sig_file = os.path.join(IN_DIR, f"{ticker}_signals.npz")
        if not os.path.exists(sig_file): continue
        
        raw_df = yf.download([ticker], start='1999-01-01', progress=False, auto_adjust=True)
        if isinstance(raw_df.columns, pd.MultiIndex):
            orig_close = raw_df['Close'][ticker].reindex(df_dates).values.flatten()
        else:
            orig_close = raw_df['Close'].reindex(df_dates).values.flatten()
        
        close = pd.Series(orig_close).ffill().bfill().values
        rets = np.zeros(T)
        rets[1:] = np.diff(close) / close[:-1]
        rets[np.isnan(orig_close)] = np.nan 
        
        annualizer = np.sqrt(252)
        # GLD is a non-equity macro diversifier, exempt from equity macro filters
        apply_macro = ticker not in ['TLT', 'GLD']
        
        npz = np.load(sig_file)
        oos_portfolio = np.full(T, np.nan)
        current_position = 0.0
        
        # Precompute the single families for this ticker
        precomputed_fams = {}
        for fam in TREND_FAMILIES:
            precomputed_fams[fam] = eval_single_fam_wfo(npz[fam], rets, macro_overlay, vix_crash, apply_macro, annualizer, W)
            
        for w in range(W):
            start_is = w * OOS_WINDOW
            end_is = start_is + IS_WINDOW
            start_oos = end_is
            end_oos = min(start_oos + OOS_WINDOW, T)
            
            if np.isnan(rets[start_is:end_is]).all():
                continue 
                
            best_params_per_fam = {}
            for fam in TREND_FAMILIES:
                w_sharpes = precomputed_fams[fam][:, w]
                valid_idx = np.where(w_sharpes > -990.0)[0]
                if len(valid_idx) == 0:
                    best_params_per_fam[fam] = np.array([])
                else:
                    best_idx = valid_idx[np.argsort(w_sharpes[valid_idx])[-TOP_K_PARAMS_PER_FAMILY:]]
                    best_params_per_fam[fam] = best_idx
                
            best_pair_sharpe = -999.0
            best_pair_logic = 0
            best_pair_indices = None
            best_pair_fams = None
            
            fam_pairs = list(itertools.combinations(TREND_FAMILIES, 2))
            for fa, fb in fam_pairs:
                idx_a = best_params_per_fam[fa]
                idx_b = best_params_per_fam[fb]
                if len(idx_a) == 0 or len(idx_b) == 0: continue
                
                mat_a = npz[fa]
                mat_b = npz[fb]
                
                mesh_a, mesh_b = np.meshgrid(idx_a, idx_b)
                combos_a = mesh_a.flatten()
                combos_b = mesh_b.flatten()
                
                sharpes = eval_pairs_wfo(mat_a, mat_b, combos_a, combos_b, rets, macro_overlay, vix_crash, apply_macro, annualizer, w)
                
                max_idx = np.unravel_index(np.argmax(sharpes), sharpes.shape)
                val = sharpes[max_idx]
                if val > best_pair_sharpe:
                    best_pair_sharpe = val
                    best_pair_logic = max_idx[1]
                    best_pair_indices = (combos_a[max_idx[0]], combos_b[max_idx[0]])
                    best_pair_fams = (fa, fb)
                    
            if best_pair_sharpe > 0:
                print(f"  Win W{w}: {best_pair_fams} {LOGIC_NAMES[best_pair_logic]} IS_SR: {best_pair_sharpe:.2f}")
                mat_list = [npz[best_pair_fams[0]], npz[best_pair_fams[1]]]
                indices = best_pair_indices
                
                oos_ret, current_position = build_oos_return(
                    mat_list, indices, best_pair_logic, rets, macro_overlay, vix_crash, apply_macro, start_oos, end_oos, current_position
                )
                oos_portfolio[start_oos:end_oos] = oos_ret
            else:
                exit_cost = current_position * TC_BPS
                oos_portfolio[start_oos] = -exit_cost
                oos_portfolio[start_oos+1:end_oos] = 0.0
                current_position = 0.0
                
        portfolio_dict[ticker] = oos_portfolio
        
    ret_df = pd.DataFrame(portfolio_dict, index=df_dates)
    ret_df.to_csv(WFO_RETURNS_FILE)
    print(f"\nSaved OOS WFO strategy returns to {WFO_RETURNS_FILE}")

if __name__ == '__main__':
    run_wfo()
