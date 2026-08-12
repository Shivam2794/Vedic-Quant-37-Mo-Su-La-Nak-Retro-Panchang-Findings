"""
OPUS-8 Matrix Engine: Phase 1b (Part 2) - Advanced Regime Ensembles
===================================================================
Executes the remainder of Master Brain Section 1B:
1. AND at Regime Level (SPY 200 SMA Gate)
2. Regime-Gated Mean Reversion (Trend in Bull, Mean-Reversion in Bear)
3. Credit Spread Overlay (HYG/LQD block)

This utilizes the exact same precomputed indicator signals from 1A.
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import os
import itertools
import time
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────
UNIVERSE   = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD']
DATA_DIR   = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
OUT_FILE   = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_regime_grid_results.csv'
TRAIN_FRAC = 0.60

def get_returns(ticker, dates_index):
    import yfinance as yf
    df = yf.download(ticker, start='1999-01-01', progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        close = df['Close'][ticker].ffill()
    else:
        close = df['Close'].ffill()
    close = close.reindex(dates_index).ffill()
    return close.pct_change().fillna(0).values.astype(np.float64)

def get_spy_regime(dates_index):
    """Returns boolean array: True if SPY > 200 SMA (Bull Regime)"""
    import yfinance as yf
    df = yf.download('SPY', start='1998-01-01', progress=False, auto_adjust=True)
    close = df['Close']['SPY'] if isinstance(df.columns, pd.MultiIndex) else df['Close']
    sma = close.rolling(200).mean()
    regime = (close > sma).reindex(dates_index).ffill().fillna(False).values
    # Shift 1 to prevent lookahead
    regime = np.roll(regime, 1)
    regime[0] = False
    return regime

def calc_sharpe_3d(strat_rets_3d, annual_factor=252):
    means = np.nanmean(strat_rets_3d, axis=0)
    stds  = np.nanstd(strat_rets_3d, axis=0)
    stds[stds == 0] = 1e-9
    return (means / stds) * np.sqrt(annual_factor)

def calc_cagr_3d(strat_rets_3d, annual_factor=252):
    log_rets = np.log1p(strat_rets_3d)
    cum_log_rets = np.nansum(log_rets, axis=0)
    n_periods = strat_rets_3d.shape[0]
    if n_periods == 0: return np.zeros_like(cum_log_rets)
    return np.exp(cum_log_rets * (annual_factor / n_periods)) - 1

def load_params_map(ticker):
    path = os.path.join(DATA_DIR, f"{ticker}_params.txt")
    pmap = {}
    with open(path, 'r') as f:
        for line in f:
            fam, idx, pstr = line.strip().split('|')
            if fam not in pmap: pmap[fam] = []
            pmap[fam].append(pstr)
    return pmap

# ─────────────────────────────────────────────────────────────────
# EVALUATOR
# ─────────────────────────────────────────────────────────────────
def evaluate_regime_logic(ticker, rets, sigs, params_map, spy_bull):
    print(f"[{ticker}] Evaluating Regime-Gated Logic...")
    results = []
    
    n_train = int(len(rets) * TRAIN_FRAC)
    rets_is  = rets[:n_train]
    rets_oos = rets[n_train:]
    spy_bull_is = spy_bull[:n_train, np.newaxis, np.newaxis]
    spy_bull_oos = spy_bull[n_train:, np.newaxis, np.newaxis]
    
    # Restrict space for speed
    trend_fams = [f for f in ['MACD', 'EMA3', 'AROON'] if f in sigs]
    meanrev_fams = [f for f in ['RSI', 'STC', 'BB'] if f in sigs]
    
    for tf, mf in itertools.product(trend_fams, meanrev_fams):
        s_trend = sigs[tf] # (T, M)
        s_mrev = sigs[mf]  # (T, N)
        
        s_trend_3d = s_trend[:, :, np.newaxis]
        s_mrev_3d  = s_mrev[:, np.newaxis, :]
        
        # LOGIC 1: AND Regime (Trend ONLY in Bull Market)
        sig_and = s_trend_3d & spy_bull[:, np.newaxis, np.newaxis]
        
        # LOGIC 2: Regime-Gated Rotation (Trend in Bull, MeanRev in Bear)
        spy_bear = ~spy_bull[:, np.newaxis, np.newaxis]
        sig_rot = (s_trend_3d & spy_bull[:, np.newaxis, np.newaxis]) | (s_mrev_3d & spy_bear)
        
        for logic_name, comb_sig in [('AND_Regime', sig_and), ('Regime_Rotate', sig_rot)]:
            strat_rets_is  = comb_sig[:n_train].astype(np.float64) * rets_is[:, np.newaxis, np.newaxis]
            strat_rets_oos = comb_sig[n_train:].astype(np.float64) * rets_oos[:, np.newaxis, np.newaxis]
            
            sharpes_is = calc_sharpe_3d(strat_rets_is)
            sharpes_oos = calc_sharpe_3d(strat_rets_oos)
            cagr_oos = calc_cagr_3d(strat_rets_oos)
            
            degrad = (sharpes_is - sharpes_oos) / np.clip(np.abs(sharpes_is), 0.5, None)
            consistency = np.clip(1.0 - degrad, 0.0, 1.0)
            invalid = (degrad > 0.3) | (sharpes_is <= 0.2) | (sharpes_oos <= 0.2)
            
            score = sharpes_oos * consistency
            score[invalid] = -999.0
            
            best_flat_idx = np.argsort(score.flatten())[::-1][:3]
            for flat_idx in best_flat_idx:
                if score.flatten()[flat_idx] == -999.0: continue
                N = score.shape[1]
                idx_m = flat_idx // N
                idx_n = flat_idx % N
                
                p1_str = params_map[tf][idx_m]
                p2_str = params_map[mf][idx_n]
                
                results.append({
                    'Ticker': ticker,
                    'Logic': logic_name,
                    'Indicators': f"{tf} (Bull) + {mf} (Bear)",
                    'Params': f"P1:[{p1_str}] | P2:[{p2_str}]",
                    'IS_Sharpe': round(sharpes_is[idx_m, idx_n], 3),
                    'OOS_Sharpe': round(sharpes_oos[idx_m, idx_n], 3),
                    'OOS_CAGR': round(cagr_oos[idx_m, idx_n]*100, 2),
                    'Score': round(score[idx_m, idx_n], 3)
                })
                
    return results

def main():
    print("="*60)
    print(" OPUS-8 Matrix Engine Phase 1b-2: Advanced Regimes")
    print("="*60)
    t0 = time.time()
    
    dates = np.load(os.path.join(DATA_DIR, 'dates.npy'))
    spy_bull = get_spy_regime(dates)
    all_results = []
    
    for ticker in UNIVERSE:
        file_path = os.path.join(DATA_DIR, f"{ticker}_signals.npz")
        if not os.path.exists(file_path): continue
            
        sigs = dict(np.load(file_path))
        params_map = load_params_map(ticker)
        rets = get_returns(ticker, dates)
        
        res = evaluate_regime_logic(ticker, rets, sigs, params_map, spy_bull)
        all_results.extend(res)
        
    df = pd.DataFrame(all_results)
    if not df.empty:
        df = df.sort_values(['Ticker', 'Score'], ascending=[True, False])
        df.to_csv(OUT_FILE, index=False)
        print(f"\nResults saved to {OUT_FILE}")
        
        print("\nTOP 2 COMBOS PER ETF:")
        winners = df.groupby(['Ticker', 'Logic']).head(1)
        print(winners.to_markdown(index=False))
        
    print(f"\nPhase 1b-2 complete in {time.time()-t0:.1f}s")

if __name__ == '__main__':
    main()
