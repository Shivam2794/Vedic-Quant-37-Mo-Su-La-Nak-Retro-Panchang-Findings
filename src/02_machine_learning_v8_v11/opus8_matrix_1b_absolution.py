"""
OPUS-8 Matrix Engine: Phase 1b - Ensemble Evaluation (TRUE Absolution Edition)
==============================================================================
Implements ALL missing ensemble rules via memory-efficient Numba JIT loop:
- Size-3 Majority Voting (A + B + C)
- Asymmetric Exits (Kawa Rule: exit ONLY when Fast < Slow on primary, not on majority)
- Continuous Allocation Score (0, 0.33, 0.66, 1.0) based on signal agreement
- Credit Spread Macro Overlay (HYG / LQD) & Economic Spread (XLY / XLP)
- VIX Crash Gate (> 25)
- Safe Haven RSI Veto (GLD/TLT Cash switch)
- Regime-Gated Mean Reversion (Autocorr < 0 -> Mean Reversion Engine)
- Per-Asset SMA 200 Trend Filter
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import yfinance as yf
import numba
import os

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
UNIVERSE = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD']
MACRO    = ['HYG', 'LQD', 'XLY', 'XLP', 'XLU', '^VIX']

dates = np.load(os.path.join(IN_DIR, 'dates.npy'), allow_pickle=True)

print("Fetching Macro Data...")
macro_df = yf.download(MACRO, start='1999-01-01', progress=False, auto_adjust=True)['Close']
macro_df = macro_df.reindex(dates).ffill()

# Credit Spread (HYG/LQD)
hyg_lqd = macro_df['HYG'] / macro_df['LQD']
hyg_lqd_ma = hyg_lqd.rolling(50).mean()
credit_risk_on = (hyg_lqd > hyg_lqd_ma).fillna(True).values

# Economic Spread (XLY/XLP)
xly_xlp = macro_df['XLY'] / macro_df['XLP']
xly_xlp_ma = xly_xlp.rolling(50).mean()
econ_risk_on = (xly_xlp > xly_xlp_ma).fillna(True).values

# Risk On requires either Credit or Econ to be bullish
risk_on_macro = credit_risk_on | econ_risk_on

# VIX Crash Gate
vix = macro_df['^VIX'].fillna(0).values
vix_crash = (vix > 25)

@numba.njit
def calc_sharpe_numba(rets):
    mu = np.nanmean(rets)
    std = np.nanstd(rets)
    if std == 0: return 0.0
    return (mu / std) * np.sqrt(252)

@numba.njit(parallel=True)
def run_grid_search_numba(mat_a, mat_b, mat_c, mat_mr, mat_regime, mat_sma, mat_rsi, 
                          rets, macro_overlay, vix_crash, apply_macro, is_safe_haven):
    
    A_len = mat_a.shape[1]
    B_len = mat_b.shape[1]
    C_len = mat_c.shape[1]
    
    # We will just evaluate index 0 of mean reversion and regime (for speed in this demo)
    # as incorporating them fully into the grid search would multiply combinations by another 10,000x.
    sig_mr = mat_mr[:, 0]
    sig_regime_trend = mat_regime[:, 0]
    sig_sma = mat_sma[:, 0]
    sig_rsi = mat_rsi[:, 0]
    
    T = len(rets)
    total_combos = A_len * B_len * C_len
    sharpes = np.zeros(total_combos)
    
    for idx in numba.prange(total_combos):
        c_idx = idx % C_len
        temp = idx // C_len
        b_idx = temp % B_len
        a_idx = temp // B_len
        
        sig_a = mat_a[:, a_idx]
        sig_b = mat_b[:, b_idx]
        sig_c = mat_c[:, c_idx]
        
        strat_rets = np.zeros(T)
        alloc = 0.0
        
        for i in range(1, T):
            target_alloc = 0.0
            
            # VIX Crash Gate
            if vix_crash[i]:
                target_alloc = 0.0
            else:
                # Regime Gated Logic
                if sig_regime_trend[i]:
                    # TRENDING REGIME (Autocorr > 0)
                    # Safe Haven RSI Veto
                    if is_safe_haven and not sig_rsi[i]:
                        target_alloc = 0.0
                    # SMA200 Filter for Risk Assets
                    elif apply_macro and not sig_sma[i]:
                        target_alloc = 0.0
                    else:
                        a = sig_a[i]
                        b = sig_b[i]
                        c = sig_c[i]
                        
                        # Asymmetric Exit Rule: Primary (A) must be True
                        if not a:
                            target_alloc = 0.0
                        else:
                            votes = int(a) + int(b) + int(c)
                            target_alloc = votes / 3.0
                            
                            # Macro gate
                            if apply_macro and not macro_overlay[i]:
                                target_alloc = 0.0
                else:
                    # MEAN REVERTING REGIME (Autocorr < 0)
                    # We ignore Trend ensemble and Macro, we just use Mean Reversion signal
                    mr = sig_mr[i]
                    if mr:
                        target_alloc = 1.0
                    else:
                        target_alloc = 0.0
                        
            # 1-Bar Confirmation on ENTRY
            prev_a = sig_a[i-1]
            prev_b = sig_b[i-1]
            prev_c = sig_c[i-1]
            prev_target = 0.0
            
            if vix_crash[i-1]:
                prev_target = 0.0
            else:
                if sig_regime_trend[i-1]:
                    if is_safe_haven and not sig_rsi[i-1]:
                        prev_target = 0.0
                    elif apply_macro and not sig_sma[i-1]:
                        prev_target = 0.0
                    else:
                        if prev_a:
                            prev_votes = int(prev_a) + int(prev_b) + int(prev_c)
                            prev_target = prev_votes / 3.0
                            if apply_macro and not macro_overlay[i-1]:
                                prev_target = 0.0
                else:
                    if sig_mr[i-1]:
                        prev_target = 1.0
                    
            alloc = min(target_alloc, prev_target)
            strat_rets[i] = rets[i] * alloc
            
        sharpes[idx] = calc_sharpe_numba(strat_rets)
        
    return sharpes

def evaluate_absolution_ensembles():
    results = []
    
    for ticker in UNIVERSE:
        file_path = os.path.join(IN_DIR, f"{ticker}_signals.npz")
        if not os.path.exists(file_path): continue
        print(f"\nProcessing {ticker} TRUE Absolution Ensembles (With Regime Gates)...")
        
        raw = yf.download(ticker, start='1999-01-01', progress=False, auto_adjust=True)['Close']
        raw = raw.reindex(dates).ffill().bfill()
        rets = np.copy(raw.pct_change().values).flatten()
        rets[np.isnan(rets)] = 0.0
        
        data = np.load(file_path)
        
        if 'MACD' not in data or 'AROON' not in data or 'DONCHIAN' not in data: 
            print(f"Skipping {ticker}, missing trend indicators.")
            continue
            
        macd = data['MACD']
        aroon = data['AROON']
        donch = data['DONCHIAN']
        
        # Load new indicators
        autocorr = data['AUTOCORR'] if 'AUTOCORR' in data else np.ones((len(rets), 1), dtype=bool)
        sma200 = data['SMA200'] if 'SMA200' in data else np.ones((len(rets), 1), dtype=bool)
        rsi = data['RSI'] if 'RSI' in data else np.ones((len(rets), 1), dtype=bool) # Used for both Mean Reversion and Veto
        
        apply_macro = (ticker not in ['TLT', 'GLD'])
        is_safe_haven = (ticker in ['TLT', 'GLD'])
        
        sharpes = run_grid_search_numba(macd, aroon, donch, rsi, autocorr, sma200, rsi, 
                                        rets, risk_on_macro, vix_crash, apply_macro, is_safe_haven)
        
        max_idx = np.nanargmax(sharpes)
        best_sharpe = sharpes[max_idx]
        
        C_len = donch.shape[1]
        B_len = aroon.shape[1]
        
        c_idx = max_idx % C_len
        temp = max_idx // C_len
        b_idx = temp % B_len
        a_idx = temp // B_len
        
        with open(os.path.join(IN_DIR, f"{ticker}_params.txt"), 'r') as f:
            lines = f.readlines()
        macd_params = [l.split('|')[2].strip() for l in lines if l.startswith('MACD')]
        aroon_params = [l.split('|')[2].strip() for l in lines if l.startswith('AROON')]
        donch_params = [l.split('|')[2].strip() for l in lines if l.startswith('DONCHIAN')]
        
        pA = macd_params[a_idx]
        pB = aroon_params[b_idx]
        pC = donch_params[c_idx]
        
        res_str = f"[{ticker}] Best Sharpe: {best_sharpe:.3f} | MACD: {pA} | AROON: {pB} | DONCHIAN: {pC}"
        print(res_str)
        results.append(res_str)

    print("\nPhase 1B TRUE Absolution (Regime Gated) Complete.")
    for r in results:
        print(r)

if __name__ == '__main__':
    evaluate_absolution_ensembles()
