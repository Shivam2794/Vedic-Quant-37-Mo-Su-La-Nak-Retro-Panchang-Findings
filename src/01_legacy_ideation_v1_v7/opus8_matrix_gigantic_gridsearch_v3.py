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
TREND_FAMILIES = [f for f in FAMILIES if f not in ['AUTOCORR', 'HURST', 'ENTROPY', 'SMA200']]

TOP_K_PARAMS_PER_FAMILY = 3
MIN_ACTIVE_DAYS = 30
TC_BPS = 0.0005 # 5 bps

IS_WINDOW = 504
OOS_WINDOW = 126

LOGIC_NAMES = ['OR', 'AND', 'MAJORITY', 'CONTINUOUS', 'ASYMMETRIC']

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
                if not (apply_macro and vix_crash[t]):
                    if s[t]: t0 = 1.0
                    if apply_macro and not macro_overlay[t]: t0 = 0.0
                        
                r = rets[t]
                ra = (r * t0) - (abs(t0 - prev_0) * TC_BPS)
                delta = ra - mean_0
                mean_0 += delta / traded_days
                m2_0 += delta * (ra - mean_0)
                if t0 > 0: n_act_0 += 1
                prev_0 = t0
                
            if m2_0 > 0 and n_act_0 >= MIN_ACTIVE_DAYS:
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
        sa, sb = mat_a[ia, :], mat_b[ib, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        prev_0, prev_1, prev_2, prev_3, prev_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        n_act_0, n_act_1, n_act_2, n_act_3, n_act_4 = 0, 0, 0, 0, 0
        traded_days = 0
        
        for t in range(start_is, end_is):
            if np.isnan(rets[t]): continue
            traded_days += 1
            
            a, b = sa[t], sb[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            if not (apply_macro and vix_crash[t]):
                votes = a + b
                if votes > 0: t0 = 1.0
                if votes == 2: t1 = 1.0
                if votes >= 1: t2 = 1.0
                t3 = votes / 2.0
                if a: t4 = votes / 2.0
                
                if apply_macro and not macro_overlay[t]:
                    t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            r = rets[t]
            ra = (r * t0) - (abs(t0 - prev_0) * TC_BPS); delta = ra - mean_0; mean_0 += delta / traded_days; m2_0 += delta * (ra - mean_0)
            if t0 > 0: n_act_0 += 1; prev_0 = t0
            
            ra = (r * t1) - (abs(t1 - prev_1) * TC_BPS); delta = ra - mean_1; mean_1 += delta / traded_days; m2_1 += delta * (ra - mean_1)
            if t1 > 0: n_act_1 += 1; prev_1 = t1
            
            ra = (r * t2) - (abs(t2 - prev_2) * TC_BPS); delta = ra - mean_2; mean_2 += delta / traded_days; m2_2 += delta * (ra - mean_2)
            if t2 > 0: n_act_2 += 1; prev_2 = t2
            
            ra = (r * t3) - (abs(t3 - prev_3) * TC_BPS); delta = ra - mean_3; mean_3 += delta / traded_days; m2_3 += delta * (ra - mean_3)
            if t3 > 0: n_act_3 += 1; prev_3 = t3
            
            ra = (r * t4) - (abs(t4 - prev_4) * TC_BPS); delta = ra - mean_4; mean_4 += delta / traded_days; m2_4 += delta * (ra - mean_4)
            if t4 > 0: n_act_4 += 1; prev_4 = t4
                
        if m2_0 > 0 and n_act_0 >= MIN_ACTIVE_DAYS: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (traded_days-1))) * annualizer
        if m2_1 > 0 and n_act_1 >= MIN_ACTIVE_DAYS: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (traded_days-1))) * annualizer
        if m2_2 > 0 and n_act_2 >= MIN_ACTIVE_DAYS: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (traded_days-1))) * annualizer
        if m2_3 > 0 and n_act_3 >= MIN_ACTIVE_DAYS: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (traded_days-1))) * annualizer
        if m2_4 > 0 and n_act_4 >= MIN_ACTIVE_DAYS: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (traded_days-1))) * annualizer

    return sharpes_out

def build_oos_return(mat_list, indices, logic_idx, rets, macro_overlay, vix_crash, apply_macro, start_oos, end_oos):
    out = np.full(end_oos - start_oos, np.nan)
    
    # Init prev_inv from start_oos - 1 to account for turnover at boundary
    prev_inv = 0.0
    if start_oos - 1 >= 0:
        votes = sum([mat_list[k][start_oos-1, indices[k]] for k in range(len(mat_list))])
        n_fams = len(mat_list)
        if not (apply_macro and vix_crash[start_oos-1]):
            if logic_idx == 0 and votes > 0: prev_inv = 1.0 # OR
            elif logic_idx == 1 and votes == n_fams: prev_inv = 1.0 # AND
            elif logic_idx == 2 and votes >= np.ceil(n_fams/2): prev_inv = 1.0 # MAJORITY
            elif logic_idx == 3: prev_inv = votes / float(n_fams) # CONTINUOUS
            elif logic_idx == 4: prev_inv = 1.0 if votes == n_fams else votes / (n_fams * 2.0) # ASYMMETRIC
            if apply_macro and not macro_overlay[start_oos-1]: prev_inv = 0.0
            
    for t in range(start_oos, end_oos):
        if t >= len(rets): break
        if np.isnan(rets[t]): continue
        
        votes = sum([mat_list[k][t, indices[k]] for k in range(len(mat_list))])
        n_fams = len(mat_list)
        
        t0 = 0.0
        if not (apply_macro and vix_crash[t]):
            if logic_idx == 0 and votes > 0: t0 = 1.0 # OR
            elif logic_idx == 1 and votes == n_fams: t0 = 1.0 # AND
            elif logic_idx == 2 and votes >= np.ceil(n_fams/2): t0 = 1.0 # MAJORITY
            elif logic_idx == 3: t0 = votes / float(n_fams) # CONTINUOUS
            elif logic_idx == 4: t0 = 1.0 if votes == n_fams else votes / (n_fams * 2.0) # ASYMMETRIC
            
            if apply_macro and not macro_overlay[t]:
                t0 = 0.0
                
        if t >= start_oos:
            r = rets[t]
            ra = (r * t0) - (abs(t0 - prev_inv) * TC_BPS)
            out[t - start_oos] = ra
            
        prev_inv = t0
        
    return out

def run_wfo():
    print("Starting Nested Walk-Forward Gridsearch (Absolution Edition)...")
    
    macro_df = yf.download(MACRO, start='1999-01-01', progress=False, auto_adjust=True)['Close']
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
    
    # SHIFT to prevent lookahead
    macro_overlay = np.roll(macro_overlay, 1)
    macro_overlay[0] = False
    vix_crash = np.roll(vix_crash, 1)
    vix_crash[0] = False
    
    T = len(df_dates)
    W = (T - IS_WINDOW) // OOS_WINDOW
    if W <= 0:
        print("Not enough data for WFO.")
        return
        
    print(f"Total Windows: {W}")
    
    portfolio_dict = {}
    
    for ticker in UNIVERSE:
        print(f"\n--- {ticker} ---")
        sig_file = os.path.join(IN_DIR, f"{ticker}_signals.npz")
        if not os.path.exists(sig_file): continue
        
        raw_df = yf.download([ticker], start='1999-01-01', progress=False, auto_adjust=True)
        orig_close = raw_df['Close'].reindex(df_dates).values.flatten()
        
        # Calculate unshifted raw returns (na where it doesn't exist)
        close = pd.Series(orig_close).ffill().bfill().values
        rets = np.zeros(T)
        rets[1:] = np.diff(close) / close[:-1]
        rets[np.isnan(orig_close)] = np.nan # Nullify non-existent days
        
        annualizer = np.sqrt(252)
        apply_macro = ticker not in ['TLT', 'GLD']
        
        npz = np.load(sig_file)
        
        # We will build an out-of-sample return series for this ticker
        oos_portfolio = np.full(T, np.nan)
        
        for w in range(W):
            start_is = w * OOS_WINDOW
            end_is = start_is + IS_WINDOW
            start_oos = end_is
            end_oos = min(start_oos + OOS_WINDOW, T)
            
            if np.isnan(rets[start_is:end_is]).all():
                continue # Asset didn't exist in this IS window
                
            print(f"  Window {w}/{W} (IS: {df_dates[start_is]}->{df_dates[end_is-1]})")
            
            # Step 1: Find best parameters per family in IS window
            best_params_per_fam = {}
            for fam in TREND_FAMILIES:
                mat = npz[fam]
                # Evaluate single fam Sharpe over this specific window
                mean_0 = 0.0
                m2_0 = 0.0
                n_act = 0
                
                # To speed up, we prune down to top K combinations
                # We reuse eval_single_fam_wfo which does it for all windows, but we only look at w
                sharpes = eval_single_fam_wfo(mat, rets, macro_overlay, vix_crash, apply_macro, annualizer, W)
                w_sharpes = sharpes[:, w]
                best_idx = np.argsort(w_sharpes)[-TOP_K_PARAMS_PER_FAMILY:]
                best_params_per_fam[fam] = best_idx
                
            # Step 2: Evaluate pairs of families
            best_pair_sharpe = -999.0
            best_pair_logic = 0
            best_pair_indices = None
            best_pair_fams = None
            
            fam_pairs = list(itertools.combinations(TREND_FAMILIES, 2))
            for fa, fb in fam_pairs:
                mat_a = npz[fa]
                mat_b = npz[fb]
                idx_a = best_params_per_fam[fa]
                idx_b = best_params_per_fam[fb]
                
                mesh_a, mesh_b = np.meshgrid(idx_a, idx_b)
                combos_a = mesh_a.flatten()
                combos_b = mesh_b.flatten()
                
                sharpes = eval_pairs_wfo(mat_a, mat_b, combos_a, combos_b, rets, macro_overlay, vix_crash, apply_macro, annualizer, w)
                
                # Find best across the 5 logics
                max_idx = np.unravel_index(np.argmax(sharpes), sharpes.shape)
                val = sharpes[max_idx]
                if val > best_pair_sharpe:
                    best_pair_sharpe = val
                    best_pair_logic = max_idx[1]
                    best_pair_indices = (combos_a[max_idx[0]], combos_b[max_idx[0]])
                    best_pair_fams = (fa, fb)
                    
            if best_pair_sharpe > 0:
                print(f"    Winner: {best_pair_fams} Logic: {LOGIC_NAMES[best_pair_logic]} Sharpe: {best_pair_sharpe:.2f}")
                # Build OOS return for this window
                mat_list = [npz[best_pair_fams[0]], npz[best_pair_fams[1]]]
                indices = best_pair_indices
                
                oos_ret = build_oos_return(mat_list, indices, best_pair_logic, rets, macro_overlay, vix_crash, apply_macro, start_oos, end_oos)
                oos_portfolio[start_oos:end_oos] = oos_ret
            else:
                # No positive Sharpe, stay in cash (return 0)
                oos_portfolio[start_oos:end_oos] = 0.0
                
        portfolio_dict[ticker] = oos_portfolio
        
    # Save the aggregated out-of-sample portfolio returns
    ret_df = pd.DataFrame(portfolio_dict, index=df_dates)
    ret_df.to_csv(WFO_RETURNS_FILE)
    print(f"\nSaved OOS WFO strategy returns to {WFO_RETURNS_FILE}")

if __name__ == '__main__':
    run_wfo()
