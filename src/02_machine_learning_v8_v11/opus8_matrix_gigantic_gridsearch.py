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
OUT_FILE = os.path.join(IN_DIR, 'gigantic_gridsearch_results.csv')

UNIVERSE = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD']
MACRO    = ['HYG', 'LQD', 'XLY', 'XLP', 'XLU', '^VIX']

FAMILIES = [
    'MACD', 'EMA3', 'TEMA', 'TEMA_SIG', 'AROON', 'RSI', 'RSI_CUMRET', 
    'KAMA', 'DONCHIAN', 'ALMA', 'GJR_GARCH', 'BB', 'STC', 'SUPERTREND', 'ADX'
]

@numba.njit(parallel=True, fastmath=True)
def eval_chunk_2(mat_a, mat_b, idx_a, idx_b, 
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib = idx_a[i], idx_b[i]
        sa, sb = mat_a[ia, :], mat_b[ib, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for t in range(1, T): # Start at 1 since 0 has no return
            a, b = sa[t], sb[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            if not vix_crash[t]:
                if sig_regime[t]:
                    if is_safe and not sig_rsi[t]: pass
                    elif apply_macro and not sig_sma[t]: pass
                    else:
                        votes = a + b
                        if votes > 0: t0 = 1.0
                        if votes == 2: t1 = 1.0
                        if votes >= 1: t2 = 1.0
                        t3 = votes / 2.0
                        if a: t4 = votes / 2.0
                        
                        if apply_macro and not macro_overlay[t]:
                            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
                else:
                    if sig_mr[t]:
                        t0, t1, t2, t3, t4 = 1.0, 1.0, 1.0, 1.0, 1.0
            
            r = rets[t]
            
            ra = r * t0; delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            ra = r * t1; delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            ra = r * t2; delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            ra = r * t3; delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            ra = r * t4; delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
                
        if m2_0 > 0: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-1))) * 15.874507866
        if m2_1 > 0: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-1))) * 15.874507866
        if m2_2 > 0: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-1))) * 15.874507866
        if m2_3 > 0: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-1))) * 15.874507866
        if m2_4 > 0: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-1))) * 15.874507866

    return sharpes_out


@numba.njit(parallel=True, fastmath=True)
def eval_chunk_3(mat_a, mat_b, mat_c, idx_a, idx_b, idx_c,
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib, ic = idx_a[i], idx_b[i], idx_c[i]
        sa, sb, sc = mat_a[ia, :], mat_b[ib, :], mat_c[ic, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for t in range(1, T):
            a, b, c = sa[t], sb[t], sc[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            if not vix_crash[t]:
                if sig_regime[t]:
                    if is_safe and not sig_rsi[t]: pass
                    elif apply_macro and not sig_sma[t]: pass
                    else:
                        votes = a + b + c
                        if votes > 0: t0 = 1.0
                        if votes == 3: t1 = 1.0
                        if votes >= 2: t2 = 1.0
                        t3 = votes / 3.0
                        if a: t4 = votes / 3.0
                        
                        if apply_macro and not macro_overlay[t]:
                            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
                else:
                    if sig_mr[t]:
                        t0, t1, t2, t3, t4 = 1.0, 1.0, 1.0, 1.0, 1.0
            
            r = rets[t]
            ra = r * t0; delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            ra = r * t1; delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            ra = r * t2; delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            ra = r * t3; delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            ra = r * t4; delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
                
        if m2_0 > 0: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-1))) * 15.874507866
        if m2_1 > 0: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-1))) * 15.874507866
        if m2_2 > 0: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-1))) * 15.874507866
        if m2_3 > 0: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-1))) * 15.874507866
        if m2_4 > 0: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-1))) * 15.874507866

    return sharpes_out


@numba.njit(parallel=True, fastmath=True)
def eval_chunk_4(mat_a, mat_b, mat_c, mat_d, idx_a, idx_b, idx_c, idx_d,
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib, ic, id = idx_a[i], idx_b[i], idx_c[i], idx_d[i]
        sa, sb, sc, sd = mat_a[ia, :], mat_b[ib, :], mat_c[ic, :], mat_d[id, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for t in range(1, T):
            a, b, c, d = sa[t], sb[t], sc[t], sd[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            if not vix_crash[t]:
                if sig_regime[t]:
                    if is_safe and not sig_rsi[t]: pass
                    elif apply_macro and not sig_sma[t]: pass
                    else:
                        votes = a + b + c + d
                        if votes > 0: t0 = 1.0
                        if votes == 4: t1 = 1.0
                        if votes >= 3: t2 = 1.0
                        t3 = votes / 4.0
                        if a: t4 = votes / 4.0
                        
                        if apply_macro and not macro_overlay[t]:
                            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
                else:
                    if sig_mr[t]:
                        t0, t1, t2, t3, t4 = 1.0, 1.0, 1.0, 1.0, 1.0
            
            r = rets[t]
            ra = r * t0; delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            ra = r * t1; delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            ra = r * t2; delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            ra = r * t3; delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            ra = r * t4; delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
                
        if m2_0 > 0: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-1))) * 15.874507866
        if m2_1 > 0: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-1))) * 15.874507866
        if m2_2 > 0: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-1))) * 15.874507866
        if m2_3 > 0: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-1))) * 15.874507866
        if m2_4 > 0: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-1))) * 15.874507866

    return sharpes_out


@numba.njit(parallel=True, fastmath=True)
def eval_chunk_5(mat_a, mat_b, mat_c, mat_d, mat_e, idx_a, idx_b, idx_c, idx_d, idx_e,
                 rets, macro_overlay, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi, 
                 apply_macro, is_safe):
    
    N = len(idx_a)
    T = len(rets)
    sharpes_out = np.full((N, 5), -999.0)
    
    for i in numba.prange(N):
        ia, ib, ic, id, ie = idx_a[i], idx_b[i], idx_c[i], idx_d[i], idx_e[i]
        sa, sb, sc, sd, se = mat_a[ia, :], mat_b[ib, :], mat_c[ic, :], mat_d[id, :], mat_e[ie, :]
        
        mean_0, mean_1, mean_2, mean_3, mean_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        m2_0, m2_1, m2_2, m2_3, m2_4 = 0.0, 0.0, 0.0, 0.0, 0.0
        
        for t in range(1, T):
            a, b, c, d, e = sa[t], sb[t], sc[t], sd[t], se[t]
            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
            
            if not vix_crash[t]:
                if sig_regime[t]:
                    if is_safe and not sig_rsi[t]: pass
                    elif apply_macro and not sig_sma[t]: pass
                    else:
                        votes = a + b + c + d + e
                        if votes > 0: t0 = 1.0
                        if votes == 5: t1 = 1.0
                        if votes >= 3: t2 = 1.0
                        t3 = votes / 5.0
                        if a: t4 = votes / 5.0
                        
                        if apply_macro and not macro_overlay[t]:
                            t0, t1, t2, t3, t4 = 0.0, 0.0, 0.0, 0.0, 0.0
                else:
                    if sig_mr[t]:
                        t0, t1, t2, t3, t4 = 1.0, 1.0, 1.0, 1.0, 1.0
            
            r = rets[t]
            ra = r * t0; delta = ra - mean_0; mean_0 += delta / t; m2_0 += delta * (ra - mean_0)
            ra = r * t1; delta = ra - mean_1; mean_1 += delta / t; m2_1 += delta * (ra - mean_1)
            ra = r * t2; delta = ra - mean_2; mean_2 += delta / t; m2_2 += delta * (ra - mean_2)
            ra = r * t3; delta = ra - mean_3; mean_3 += delta / t; m2_3 += delta * (ra - mean_3)
            ra = r * t4; delta = ra - mean_4; mean_4 += delta / t; m2_4 += delta * (ra - mean_4)
                
        if m2_0 > 0: sharpes_out[i, 0] = (mean_0 / np.sqrt(m2_0 / (T-1))) * 15.874507866
        if m2_1 > 0: sharpes_out[i, 1] = (mean_1 / np.sqrt(m2_1 / (T-1))) * 15.874507866
        if m2_2 > 0: sharpes_out[i, 2] = (mean_2 / np.sqrt(m2_2 / (T-1))) * 15.874507866
        if m2_3 > 0: sharpes_out[i, 3] = (mean_3 / np.sqrt(m2_3 / (T-1))) * 15.874507866
        if m2_4 > 0: sharpes_out[i, 4] = (mean_4 / np.sqrt(m2_4 / (T-1))) * 15.874507866

    return sharpes_out


def run_gigantic_gridsearch():
    print("Initializing Gigantic Grid Search Matrix Engine (Opus-5 Tuned & Fully Inspected)...")
    dates = np.load(os.path.join(IN_DIR, 'dates.npy'), allow_pickle=True)
    
    macro_df = yf.download(MACRO, start='1999-01-01', progress=False, auto_adjust=True)['Close']
    macro_df = macro_df.reindex(dates).ffill()

    hyg_lqd = macro_df['HYG'] / macro_df['LQD']
    hyg_lqd_ma = hyg_lqd.rolling(50).mean()
    credit_risk_on = (hyg_lqd > hyg_lqd_ma).fillna(True).values

    xly_xlp = macro_df['XLY'] / macro_df['XLP']
    xly_xlp_ma = xly_xlp.rolling(50).mean()
    econ_risk_on = (xly_xlp > xly_xlp_ma).fillna(True).values

    risk_on_macro = credit_risk_on | econ_risk_on
    vix = macro_df['^VIX'].fillna(0).values
    vix_crash = (vix > 25)

    # BRUTAL INSPECTION FIX: Shift macro arrays by 1 to prevent severe lookahead bias!
    risk_on_macro = np.roll(risk_on_macro, 1)
    risk_on_macro[0] = False
    
    vix_crash = np.roll(vix_crash, 1)
    vix_crash[0] = False

    if not os.path.exists(OUT_FILE):
        with open(OUT_FILE, 'w') as f:
            f.write("Asset,Size,Families,Logic,Sharpe,Params\n")

    for ticker in UNIVERSE:
        print(f"\n[{ticker}] Loading Matrix Data...")
        file_path = os.path.join(IN_DIR, f"{ticker}_signals.npz")
        if not os.path.exists(file_path): continue
        
        raw = yf.download(ticker, start='1999-01-01', progress=False, auto_adjust=True)['Close']
        raw = raw.reindex(dates).ffill().bfill()
        rets = np.copy(raw.pct_change().values).flatten()
        rets[np.isnan(rets)] = 0.0
        
        data = np.load(file_path)
        
        apply_macro = (ticker not in ['TLT', 'GLD'])
        is_safe_haven = (ticker in ['TLT', 'GLD'])
        
        sig_mr = data['RSI'][:, 0] if 'RSI' in data else np.ones(len(rets), dtype=bool)
        sig_regime = data['AUTOCORR'][:, 0] if 'AUTOCORR' in data else np.ones(len(rets), dtype=bool)
        sig_sma = data['SMA200'][:, 0] if 'SMA200' in data else np.ones(len(rets), dtype=bool)
        sig_rsi = sig_mr
        
        valid_fams = [f for f in FAMILIES if f in data and data[f].shape[1] > 0]
        fam_params = {}
        with open(os.path.join(IN_DIR, f"{ticker}_params.txt"), 'r') as f:
            lines = f.readlines()
        for f in valid_fams:
            fam_params[f] = [l.split('|')[2].strip() for l in lines if l.startswith(f"{f}|")]
            
        print(f"[{ticker}] Valid families: {len(valid_fams)}")
        
        CHUNK_SIZE = 5_000_000 # Increased chunk size
        logics = ['OR', 'AND', 'MAJORITY', 'CONTINUOUS', 'ASYMMETRIC']
        
        for size in [2, 3, 4, 5]:
            print(f"[{ticker}] Evaluating Size {size} ensembles...")
            combos = list(itertools.combinations(valid_fams, size))
            
            for combo in combos:
                # Transpose arrays in Python to make them C-contiguous (P, T)
                mats = [np.ascontiguousarray(data[f].T) for f in combo]
                lens = [m.shape[0] for m in mats] # P is now dim 0
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
                    
                    if size == 2:
                        res = eval_chunk_2(mats[0], mats[1], indices[0], indices[1],
                                           rets, risk_on_macro, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                           apply_macro, is_safe_haven)
                    elif size == 3:
                        res = eval_chunk_3(mats[0], mats[1], mats[2], indices[0], indices[1], indices[2],
                                           rets, risk_on_macro, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                           apply_macro, is_safe_haven)
                    elif size == 4:
                        res = eval_chunk_4(mats[0], mats[1], mats[2], mats[3], indices[0], indices[1], indices[2], indices[3],
                                           rets, risk_on_macro, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                           apply_macro, is_safe_haven)
                    elif size == 5:
                        res = eval_chunk_5(mats[0], mats[1], mats[2], mats[3], mats[4], indices[0], indices[1], indices[2], indices[3], indices[4],
                                           rets, risk_on_macro, vix_crash, sig_mr, sig_regime, sig_sma, sig_rsi,
                                           apply_macro, is_safe_haven)
                        
                    for k in range(5):
                        max_idx = np.nanargmax(res[:, k])
                        local_best = res[max_idx, k]
                        if local_best > best_s[k]:
                            best_s[k] = local_best
                            best_i[k] = idx_arr[max_idx]

                with open(OUT_FILE, 'a') as f:
                    for k in range(5):
                        idx_decode = []
                        temp = best_i[k]
                        for L in reversed(lens):
                            idx_decode.append(temp % L)
                            temp = temp // L
                        idx_decode.reverse()
                        
                        param_strs = [f"{combo[j]}: {fam_params[combo[j]][idx_decode[j]]}" for j in range(size)]
                        p_str = " | ".join(param_strs)
                        f.write(f"{ticker},{size},{'-'.join(combo)},{logics[k]},{best_s[k]:.4f},{p_str}\n")
                        
    print("Gigantic Grid Search Fully Completed.")

if __name__ == '__main__':
    run_gigantic_gridsearch()
