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
OUT_FILE = os.path.join(IN_DIR, 'opus8_gridsearch_absolution_results.csv')

UNIVERSE = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'TQQQ', 'UPRO']
MACRO    = ['HYG', 'LQD', 'XLY', 'XLP', 'XLU', '^VIX']

FAMILIES = [
    'MACD', 'EMA3', 'TEMA', 'TEMA_SIG', 'AROON', 'RSI', 'RSI_CUMRET', 
    'KAMA', 'DONCHIAN', 'ALMA', 'GJR_GARCH', 'BB', 'STC', 'SUPERTREND', 'ADX',
    'FTI', 'AUTOCORR', 'HURST', 'ENTROPY', 'SMA200'
]

# Extract only the trend families for combinations
TREND_FAMILIES = [f for f in FAMILIES if f not in ['AUTOCORR', 'HURST', 'ENTROPY', 'SMA200']]

# PRUNING CONSTANTS
TOP_K_PARAMS_PER_FAMILY = 3
MIN_ACTIVE_DAYS = 250
TC_BPS = 0.0005 # 5 bps

@numba.njit(parallel=True, fastmath=False)
def eval_chunk_2(mat_a, mat_b, idx_a, idx_b, 
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe, annualizer):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib = idx_a[i], idx_b[i]
        sa, sb = mat_a[ia, :], mat_b[ib, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        prev_0, prev_1, prev_2, prev_3, prev_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        n_act_0, n_act_1, n_act_2, n_act_3, n_act_4 = 0, 0, 0, 0, 0
        
        for t in range(1, T):
            a, b = sa[t], sb[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            # Risk ON assets are blocked by extreme VIX > 40. Safe assets activate during VIX crash.
            # We no longer block at VIX > 25 as it cuts off bottom rallies.
            blocked_by_vix = apply_macro and vix_crash[t]
            
            if not blocked_by_vix:
                # We evaluate the indicators purely. No MR/SMA blindfolds.
                votes = a + b
                if votes > 0: t0 = 1.0
                if votes == 2: t1 = 1.0
                if votes >= 1: t2 = 1.0
                t3 = votes / 2.0
                if a: t4 = votes / 2.0
                
                # Apply high-level credit/macro overlay. (Avoid trading SPY when Credit is crashing)
                if apply_macro and not macro_overlay[t]:
                    t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            r = rets[t]
            
            ra = (r * t0) - (abs(t0 - prev_0) * TC_BPS); delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            if t0 > 0: n_act_0 += 1; 
            prev_0 = t0
            
            ra = (r * t1) - (abs(t1 - prev_1) * TC_BPS); delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            if t1 > 0: n_act_1 += 1; 
            prev_1 = t1
            
            ra = (r * t2) - (abs(t2 - prev_2) * TC_BPS); delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            if t2 > 0: n_act_2 += 1; 
            prev_2 = t2
            
            ra = (r * t3) - (abs(t3 - prev_3) * TC_BPS); delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            if t3 > 0: n_act_3 += 1; 
            prev_3 = t3
            
            ra = (r * t4) - (abs(t4 - prev_4) * TC_BPS); delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
            if t4 > 0: n_act_4 += 1; 
            prev_4 = t4
                
        if m2_0 > 0 and n_act_0 >= MIN_ACTIVE_DAYS: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-2))) * annualizer
        if m2_1 > 0 and n_act_1 >= MIN_ACTIVE_DAYS: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-2))) * annualizer
        if m2_2 > 0 and n_act_2 >= MIN_ACTIVE_DAYS: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-2))) * annualizer
        if m2_3 > 0 and n_act_3 >= MIN_ACTIVE_DAYS: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-2))) * annualizer
        if m2_4 > 0 and n_act_4 >= MIN_ACTIVE_DAYS: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-2))) * annualizer

    return sharpes_out


@numba.njit(parallel=True, fastmath=False)
def eval_chunk_3(mat_a, mat_b, mat_c, idx_a, idx_b, idx_c,
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe, annualizer):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib, ic = idx_a[i], idx_b[i], idx_c[i]
        sa, sb, sc = mat_a[ia, :], mat_b[ib, :], mat_c[ic, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        prev_0, prev_1, prev_2, prev_3, prev_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        n_act_0, n_act_1, n_act_2, n_act_3, n_act_4 = 0, 0, 0, 0, 0
        
        for t in range(1, T):
            a, b, c = sa[t], sb[t], sc[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            blocked_by_vix = apply_macro and vix_crash[t]
            
            if not blocked_by_vix:
                votes = a + b + c
                if votes > 0: t0 = 1.0
                if votes == 3: t1 = 1.0
                if votes >= 2: t2 = 1.0
                t3 = votes / 3.0
                if a: t4 = votes / 3.0
                
                if apply_macro and not macro_overlay[t]:
                    t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            r = rets[t]
            
            ra = (r * t0) - (abs(t0 - prev_0) * TC_BPS); delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            if t0 > 0: n_act_0 += 1; 
            prev_0 = t0
            
            ra = (r * t1) - (abs(t1 - prev_1) * TC_BPS); delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            if t1 > 0: n_act_1 += 1; 
            prev_1 = t1
            
            ra = (r * t2) - (abs(t2 - prev_2) * TC_BPS); delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            if t2 > 0: n_act_2 += 1; 
            prev_2 = t2
            
            ra = (r * t3) - (abs(t3 - prev_3) * TC_BPS); delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            if t3 > 0: n_act_3 += 1; 
            prev_3 = t3
            
            ra = (r * t4) - (abs(t4 - prev_4) * TC_BPS); delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
            if t4 > 0: n_act_4 += 1; 
            prev_4 = t4
                
        if m2_0 > 0 and n_act_0 >= MIN_ACTIVE_DAYS: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-2))) * annualizer
        if m2_1 > 0 and n_act_1 >= MIN_ACTIVE_DAYS: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-2))) * annualizer
        if m2_2 > 0 and n_act_2 >= MIN_ACTIVE_DAYS: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-2))) * annualizer
        if m2_3 > 0 and n_act_3 >= MIN_ACTIVE_DAYS: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-2))) * annualizer
        if m2_4 > 0 and n_act_4 >= MIN_ACTIVE_DAYS: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-2))) * annualizer

    return sharpes_out


@numba.njit(parallel=True, fastmath=False)
def eval_chunk_4(mat_a, mat_b, mat_c, mat_d, idx_a, idx_b, idx_c, idx_d,
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe, annualizer):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib, ic, i_d = idx_a[i], idx_b[i], idx_c[i], idx_d[i]
        sa, sb, sc, sd = mat_a[ia, :], mat_b[ib, :], mat_c[ic, :], mat_d[i_d, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        prev_0, prev_1, prev_2, prev_3, prev_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        n_act_0, n_act_1, n_act_2, n_act_3, n_act_4 = 0, 0, 0, 0, 0
        
        for t in range(1, T):
            a, b, c, d = sa[t], sb[t], sc[t], sd[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            blocked_by_vix = apply_macro and vix_crash[t]
            
            if not blocked_by_vix:
                votes = a + b + c + d
                if votes > 0: t0 = 1.0
                if votes == 4: t1 = 1.0
                if votes >= 3: t2 = 1.0
                t3 = votes / 4.0
                if a: t4 = votes / 4.0
                
                if apply_macro and not macro_overlay[t]:
                    t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            r = rets[t]
            ra = (r * t0) - (abs(t0 - prev_0) * TC_BPS); delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            if t0 > 0: n_act_0 += 1; 
            prev_0 = t0
            
            ra = (r * t1) - (abs(t1 - prev_1) * TC_BPS); delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            if t1 > 0: n_act_1 += 1; 
            prev_1 = t1
            
            ra = (r * t2) - (abs(t2 - prev_2) * TC_BPS); delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            if t2 > 0: n_act_2 += 1; 
            prev_2 = t2
            
            ra = (r * t3) - (abs(t3 - prev_3) * TC_BPS); delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            if t3 > 0: n_act_3 += 1; 
            prev_3 = t3
            
            ra = (r * t4) - (abs(t4 - prev_4) * TC_BPS); delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
            if t4 > 0: n_act_4 += 1; 
            prev_4 = t4
                
        if m2_0 > 0 and n_act_0 >= MIN_ACTIVE_DAYS: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-2))) * annualizer
        if m2_1 > 0 and n_act_1 >= MIN_ACTIVE_DAYS: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-2))) * annualizer
        if m2_2 > 0 and n_act_2 >= MIN_ACTIVE_DAYS: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-2))) * annualizer
        if m2_3 > 0 and n_act_3 >= MIN_ACTIVE_DAYS: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-2))) * annualizer
        if m2_4 > 0 and n_act_4 >= MIN_ACTIVE_DAYS: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-2))) * annualizer

    return sharpes_out

def run_gigantic_gridsearch():
    print("Initializing OPUS-8 Absolution Grid Search Engine...")
    dates = np.load(os.path.join(IN_DIR, 'dates.npy'), allow_pickle=True)
    
    # -----------------------------
    # 1. MACRO OVERLAY BUG FIXES
    # -----------------------------
    macro_df = yf.download(MACRO, start='1999-01-01', progress=False, auto_adjust=True)['Close']
    macro_df = macro_df.reindex(dates).ffill()

    hyg_lqd = macro_df['HYG'] / macro_df['LQD']
    hyg_lqd_ma = hyg_lqd.rolling(50).mean()
    
    # OPUS-5 FIX: fillna(True) doesn't work on boolean series resulting from NaN comparions. Use explicit mask.
    mask = hyg_lqd_ma.isna()
    credit_risk_on = (hyg_lqd > hyg_lqd_ma) | mask
    credit_risk_on = credit_risk_on.values

    xly_xlp = macro_df['XLY'] / macro_df['XLP']
    xly_xlp_ma = xly_xlp.rolling(50).mean()
    mask2 = xly_xlp_ma.isna()
    econ_risk_on = (xly_xlp > xly_xlp_ma) | mask2
    econ_risk_on = econ_risk_on.values

    risk_on_macro = credit_risk_on | econ_risk_on
    vix = macro_df['^VIX'].fillna(0).values
    vix_crash = (vix > 40)

    risk_on_macro = np.roll(risk_on_macro, 1)
    risk_on_macro[0] = False
    
    vix_crash = np.roll(vix_crash, 1)
    vix_crash[0] = False

    if not os.path.exists(OUT_FILE):
        with open(OUT_FILE, 'w') as f:
            f.write("Ticker,Size,Families,Logic,Sharpe,Params\n")

    for ticker in UNIVERSE:
        print(f"\n=========================================")
        print(f"[{ticker}] Initiating Absolution Matrix...")
        
        file_path = os.path.join(IN_DIR, f"{ticker}_signals.npz")
        if not os.path.exists(file_path): continue
        
        raw = yf.download(ticker, start='1999-01-01', progress=False, auto_adjust=True)['Close']
        
        # OPUS-5 FIX: Fix BTC-USD corrupted data (weekend truncation + 15 yr zeros)
        first_valid_idx = raw.first_valid_index()
        raw = raw.loc[first_valid_idx:]
        
        # All assets are now aligned to dates.npy (approx 252 days/yr)
        annualizer = 15.874507866
        
        # Align dates. 
        # For Equities, reindex to dates.npy from the first valid index onwards.
        # For Crypto, we keep its native 365 calendar, but our indicator generator used dates.npy.
        # Wait, the signals were generated using dates.npy calendar for all assets!
        # This means the generator `.npz` files ALREADY truncated crypto weekends!
        # Since the `.npz` is tied to `dates.npy`, we MUST reindex to `dates.npy` to align dimensions.
        raw = raw.reindex(dates).ffill().bfill()
        
        # Find the first index in `dates` that is >= first_valid_idx
        start_i = 0
        for i, d in enumerate(dates):
            if d >= first_valid_idx:
                start_i = i
                break
                
        rets = np.copy(raw.pct_change().values).flatten()
        rets[np.isnan(rets)] = 0.0
        
        # Slice everything from start_i onwards to prevent bfill pollution
        rets = rets[start_i:]
        t_risk_on_macro = risk_on_macro[start_i:]
        t_vix_crash = vix_crash[start_i:]
        
        data = np.load(file_path)
        
        apply_macro = (ticker not in ['TLT', 'GLD'])
        is_safe_haven = (ticker in ['TLT', 'GLD'])
        
        sig_mr = data['RSI'][start_i:, 0] if 'RSI' in data else np.ones(len(rets), dtype=bool)
        sig_regime = data['AUTOCORR'][start_i:, 0] if 'AUTOCORR' in data else np.ones(len(rets), dtype=bool)
        sig_sma = data['SMA200'][start_i:, 0] if 'SMA200' in data else np.ones(len(rets), dtype=bool)
        sig_rsi = np.copy(sig_mr) # Un-alias
        
        valid_fams = [f for f in TREND_FAMILIES if f in data and data[f].shape[1] > 0]
        fam_params = {}
        with open(os.path.join(IN_DIR, f"{ticker}_params.txt"), 'r') as f:
            lines = f.readlines()
        for f in valid_fams:
            fam_params[f] = [l.split('|')[2].strip() for l in lines if l.startswith(f"{f}|")]
            
        print(f"[{ticker}] Valid trend families: {len(valid_fams)}")
        print(f"[{ticker}] Valid trading days: {len(rets)}")
        
        CHUNK_SIZE = 5_000_000
        logics = ['OR', 'AND', 'MAJORITY', 'CONTINUOUS', 'ASYMMETRIC']
        
        # Phase 1: Pruning - Run Size 2 to find Top-K parameters per family
        print(f"[{ticker}] Phase 1: Parameter Pruning (Size 2)")
        
        # To prune, we will track the best Sharpe achieved by each parameter index in Size 2
        # fam_best_sharpes = {fam: np.full(num_params, -999.0) }
        fam_best_sharpes = {f: np.full(data[f].shape[1], -999.0) for f in valid_fams}
        
        combos_2 = list(itertools.combinations(valid_fams, 2))
        for combo in combos_2:
            f0, f1 = combo[0], combo[1]
            m0 = np.ascontiguousarray(data[f0][start_i:, :].T)
            m1 = np.ascontiguousarray(data[f1][start_i:, :].T)
            l0, l1 = m0.shape[0], m1.shape[0]
            total = l0 * l1
            
            for chunk_start in range(0, total, CHUNK_SIZE):
                chunk_end = min(chunk_start + CHUNK_SIZE, total)
                idx_arr = np.arange(chunk_start, chunk_end, dtype=np.int64)
                i0, i1 = idx_arr // l1, idx_arr % l1
                
                res = eval_chunk_2(m0, m1, i0, i1,
                                   rets, t_risk_on_macro, t_vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                   apply_macro, is_safe_haven, annualizer)
                
                # Max over all logics
                max_sharpes = np.nanmax(res, axis=1) 
                
                for k in range(len(max_sharpes)):
                    s = max_sharpes[k]
                    if s > -990.0:
                        idx0, idx1 = i0[k], i1[k]
                        if s > fam_best_sharpes[f0][idx0]: fam_best_sharpes[f0][idx0] = s
                        if s > fam_best_sharpes[f1][idx1]: fam_best_sharpes[f1][idx1] = s

        # Now extract the Top K parameter indices for each family
        top_k_indices = {}
        for f in valid_fams:
            scores = fam_best_sharpes[f]
            # argsort sorts ascending, so we take the last K elements
            best_idx = np.argsort(scores)[-TOP_K_PARAMS_PER_FAMILY:]
            # filter out any that are still -999.0
            best_idx = [i for i in best_idx if scores[i] > -990.0]
            if len(best_idx) == 0:
                best_idx = [0] # fallback
            top_k_indices[f] = best_idx
            
        print(f"[{ticker}] Pruning complete. Reduced parameter space to Top {TOP_K_PARAMS_PER_FAMILY} per family.")

        # Prune the data dictionary matrices
        pruned_mats = {}
        pruned_params = {}
        for f in valid_fams:
            pruned_mats[f] = data[f][start_i:, top_k_indices[f]]
            pruned_params[f] = [fam_params[f][i] for i in top_k_indices[f]]

        # Phase 2: Gigantic Combinations using Pruned Matrices
        for size in [3, 4]:
            print(f"[{ticker}] Evaluating Pruned Size {size} ensembles...")
            combos = list(itertools.combinations(valid_fams, size))
            
            for combo in combos:
                mats = [np.ascontiguousarray(pruned_mats[f].T) for f in combo]
                lens = [m.shape[0] for m in mats]
                total = np.prod(lens)
                
                best_s = [-999.0] * 5
                best_i = [0] * 5
                
                for chunk_start in range(0, total, CHUNK_SIZE):
                    chunk_end = min(chunk_start + CHUNK_SIZE, total)
                    N = chunk_end - chunk_start
                    idx_arr = np.arange(chunk_start, chunk_end, dtype=np.int64)
                    
                    indices = []
                    temp = idx_arr
                    for L in reversed(lens):
                        indices.append(temp % L)
                        temp = temp // L
                    indices.reverse()
                    
                    if size == 3:
                        res = eval_chunk_3(mats[0], mats[1], mats[2], indices[0], indices[1], indices[2],
                                           rets, t_risk_on_macro, t_vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                           apply_macro, is_safe_haven, annualizer)
                    elif size == 4:
                        res = eval_chunk_4(mats[0], mats[1], mats[2], mats[3], indices[0], indices[1], indices[2], indices[3],
                                           rets, t_risk_on_macro, t_vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                           apply_macro, is_safe_haven, annualizer)
                        
                    for k in range(5):
                        max_idx = np.nanargmax(res[:, k])
                        local_best = res[max_idx, k]
                        if local_best > best_s[k]:
                            best_s[k] = local_best
                            best_i[k] = idx_arr[max_idx]

                with open(OUT_FILE, 'a') as f:
                    for k in range(5):
                        if best_s[k] == -999.0: continue
                        
                        idx_decode = []
                        temp = best_i[k]
                        for L in reversed(lens):
                            idx_decode.append(temp % L)
                            temp = temp // L
                        idx_decode.reverse()
                        
                        param_strs = [f"{combo[j]}: {pruned_params[combo[j]][idx_decode[j]]}" for j in range(size)]
                        p_str = " | ".join(param_strs)
                        f.write(f"{ticker},{size},{'-'.join(combo)},{logics[k]},{best_s[k]:.4f},{p_str}\n")
                        
    print("Gigantic Grid Search (Absolution Edition) Fully Completed.")

if __name__ == '__main__':
    run_gigantic_gridsearch()
