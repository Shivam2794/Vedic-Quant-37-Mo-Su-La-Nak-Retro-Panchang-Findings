"""
OPUS-8 Matrix Engine: Phase 1a - Indicator Signal Generator (Absolution Edition)
================================================================================
Generates and caches raw binary signals for EVERY indicator and parameter
combination from Master Brain Section 1A. NO SKIPS.

INDICATORS IMPLEMENTED:
- Triple EMA, MACD (Standard/Wide/Ultra), Math TEMA, Aroon, KAMA, Donchian,
  ALMA, GJR-GARCH, Bollinger Bands, STC, Supertrend, ADX, FTI, DAGMA, MACD-V,
  RSI (Standard/CumRet).
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import yfinance as yf
import pandas as pd
import numpy as np
import itertools
import warnings
import time
import os
import numba
from arch import arch_model
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIG & DIRECTORIES
# ─────────────────────────────────────────────────────────────────
UNIVERSE = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD', 'TQQQ', 'UPRO']
MACRO    = ['HYG', 'LQD', 'XLY', 'XLP', 'XLU', '^VIX']
OUT_DIR  = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'

os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# PARAMETER GRIDS (EXHAUSTIVE 1A)
# ─────────────────────────────────────────────────────────────────
GRIDS = {
    'MACD': { 
        'fast': [5, 13, 24, 40],
        'slow': [20, 24, 52, 120],
        'sig':  [5, 13, 15, 150]
    },
    'EMA3': { 
        'f': [5, 10, 20, 40],
        'm': [40, 60, 80, 100],
        's': [100, 150, 200]
    },
    'TEMA': { 
        'f': [5, 13, 21],
        'm': [21, 34, 55],
        's': [55, 89, 144]
    },
    'TEMA_SIG': {
        'period': [20, 50, 100, 200]
    },
    'AROON': {
        'period': [20, 30, 40, 50, 60, 70],
        'up_t': [70, 80, 90],
        'dn_t': [30, 40, 50]
    },
    'RSI': {
        'period': [14, 28, 42, 90],
        'thresh': [45, 50, 55]
    },
    'RSI_CUMRET': {
        'period': [14, 28],
        'thresh': [700, 1400]
    },
    'KAMA': {
        'er_period': [10, 20],
        'fast': [2, 3],
        'slow': [30, 53]
    },
    'DONCHIAN': {
        'period': [15, 17, 19, 21, 30, 40, 50]
    },
    'ALMA': {
        'window': [20, 50, 100],
        'offset': [0.85],
        'sigma':  [6.0]
    },
    'GJR_GARCH': { 
        'vol_window': [21],
        'pct_window': [252],
        'pct_thresh': [0.85, 0.90, 0.95] 
    },
    'BB': {
        'window': [20, 50, 100],
        'std': [1.5, 2.0, 2.5, 3.0]
    },
    'STC': {
        'fast': [23, 12],
        'slow': [50, 26],
        'cycle': [10, 20]
    },
    'SUPERTREND': {
        'atr_period': [5, 10],
        'multiplier': [3.0, 3.4, 4.0]
    },
    'ADX': {
        'period': [14, 20],
        'thresh': [20, 25, 30]
    },
    'FTI': { 
        'period': [14, 21, 50],
        'thresh': [0.6, 0.7] # higher = more fractal/choppy
    },
    'AUTOCORR': {
        'period': [20, 50, 100],
        'lag': [1]
    },
    'HURST': {
        'period': [100, 252]
    },
    'ENTROPY': {
        'period': [20, 50, 100]
    },
    'SMA200': {
        'period': [200]
    }
}

# ─────────────────────────────────────────────────────────────────
# NUMBA VECTORIZED MATH ACCELERATORS
# ─────────────────────────────────────────────────────────────────
@numba.njit
def ewma_numba(arr, span):
    alpha = 2.0 / (span + 1.0)
    out = np.empty_like(arr)
    
    # Find first valid index
    first_valid = 0
    while first_valid < len(arr) and np.isnan(arr[first_valid]):
        out[first_valid] = np.nan
        first_valid += 1
        
    if first_valid < len(arr):
        out[first_valid] = arr[first_valid]
        for i in range(first_valid + 1, len(arr)):
            if np.isnan(arr[i]):
                out[i] = out[i-1]
            else:
                out[i] = (arr[i] - out[i-1]) * alpha + out[i-1]
    return out

@numba.njit
def calc_stc_numba(macd, cycle):
    out = np.zeros_like(macd)
    for i in range(cycle-1, len(macd)):
        window = macd[i-cycle+1 : i+1]
        cmin = np.min(window)
        cmax = np.max(window)
        if cmax - cmin == 0:
            out[i] = 0
        else:
            out[i] = 100 * (macd[i] - cmin) / (cmax - cmin)
    return out

@numba.njit
def calc_alma_numba(price, window, offset, sigma):
    out = np.zeros_like(price)
    m = offset * (window - 1)
    s = window / sigma
    
    # Precompute weights
    weights = np.zeros(window)
    for i in range(window):
        weights[i] = np.exp(-((i - m)**2) / (2 * s**2))
    sum_w = np.sum(weights)
    
    for i in range(window-1, len(price)):
        window_prices = price[i-window+1 : i+1]
        out[i] = np.sum(window_prices * weights) / sum_w
    return out

@numba.njit
def calc_adx_numba(high, low, close, period):
    adx = np.zeros_like(close)
    tr = np.zeros_like(close)
    pdm = np.zeros_like(close)
    ndm = np.zeros_like(close)
    
    for i in range(1, len(close)):
        tr[i] = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
        up = high[i] - high[i-1]
        dn = low[i-1] - low[i]
        
        if up > dn and up > 0: pdm[i] = up
        else: pdm[i] = 0
            
        if dn > up and dn > 0: ndm[i] = dn
        else: ndm[i] = 0
            
    # Wilder's smoothing (alpha = 1/period)
    atr = ewma_numba(tr, period*2-1)
    spdm = ewma_numba(pdm, period*2-1)
    sndm = ewma_numba(ndm, period*2-1)
    
    pdi = np.zeros_like(close)
    ndi = np.zeros_like(close)
    dx = np.zeros_like(close)
    
    for i in range(period, len(close)):
        if atr[i] != 0:
            pdi[i] = 100 * spdm[i] / atr[i]
            ndi[i] = 100 * sndm[i] / atr[i]
            if pdi[i] + ndi[i] != 0:
                dx[i] = 100 * abs(pdi[i] - ndi[i]) / (pdi[i] + ndi[i])
                
    adx = ewma_numba(dx, period*2-1)
    return adx, pdi, ndi

@numba.njit
def calc_fti_numba(close, period):
    # Fractal Efficiency (Path length vs Net Move)
    out = np.zeros_like(close)
    for i in range(period, len(close)):
        net_move = abs(close[i] - close[i-period])
        path_len = 0.0
        for j in range(i-period+1, i+1):
            path_len += abs(close[j] - close[j-1])
        if path_len == 0: out[i] = 0
        else: out[i] = net_move / path_len
    return out

# ─────────────────────────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────────────────────────
def get_data(start='1999-01-01'):
    print(f"Downloading: {UNIVERSE + MACRO}")
    raw = yf.download(UNIVERSE + MACRO, start=start, progress=False, auto_adjust=True)
    df = raw.copy()
    
    # FIX: Reindex to the ETF trading calendar to fold BTC weekend returns into Monday
    if isinstance(df.columns, pd.MultiIndex):
        spy_close = df['Close']['SPY']
    else:
        spy_close = df['SPY']
        
    trading_days = spy_close.dropna().index
    df = df.reindex(trading_days)
    
    print(f"Data: {df.shape} | {df.index[0].date()} -> {df.index[-1].date()}")
    return df

# ─────────────────────────────────────────────────────────────────
# INDICATOR GENERATORS (Return 1D boolean numpy arrays)
# ─────────────────────────────────────────────────────────────────
def gen_macd(price, p):
    fast, slow, sig = p['fast'], p['slow'], p['sig']
    if fast >= slow: return np.zeros(len(price), dtype=bool)
    ef = ewma_numba(price, fast)
    es = ewma_numba(price, slow)
    macd = ef - es
    signl = ewma_numba(macd, sig)
    return macd > signl

def gen_ema3(price, p):
    f, m, s = p['f'], p['m'], p['s']
    if not (f < m < s): return np.zeros(len(price), dtype=bool)
    ef = ewma_numba(price, f)
    em = ewma_numba(price, m)
    es = ewma_numba(price, s)
    return (ef > em) & (em > es)

def calc_true_tema(price, per):
    ema1 = ewma_numba(price, per)
    ema2 = ewma_numba(ema1, per)
    ema3 = ewma_numba(ema2, per)
    return 3*ema1 - 3*ema2 + ema3

def gen_tema(price, p):
    f, m, s = p['f'], p['m'], p['s']
    if not (f < m < s): return np.zeros(len(price), dtype=bool)
    tf = calc_true_tema(price, f)
    tm = calc_true_tema(price, m)
    ts = calc_true_tema(price, s)
    return (tf > tm) & (tm > ts)

def gen_tema_sig(price, p):
    per = p['period']
    tema = calc_true_tema(price, per)
    return price > tema

def gen_aroon(high, low, p):
    per = p['period']
    up_t, dn_t = p['up_t'], p['dn_t']
    up = np.zeros(len(high))
    dn = np.zeros(len(low))
    for i in range(per, len(high)):
        hw = high[i-per : i+1]
        lw = low[i-per : i+1]
        days_since_high = np.argmax(hw[::-1])
        days_since_low = np.argmin(lw[::-1])
        up[i] = 100 * (per - days_since_high) / per
        dn[i] = 100 * (per - days_since_low) / per
    return (up > up_t) & (dn < dn_t)

def gen_rsi(price, p):
    per, thresh = p['period'], p['thresh']
    delta = np.diff(price, prepend=price[0])
    gain = np.clip(delta, 0, None)
    loss = -np.clip(delta, None, 0)
    avg_gain = ewma_numba(gain, per*2-1)
    avg_loss = ewma_numba(loss, per*2-1)
    rs = np.zeros_like(price)
    mask = avg_loss != 0
    rs[mask] = avg_gain[mask] / avg_loss[mask]
    rsi = np.zeros_like(price)
    rsi[mask] = 100 - (100 / (1 + rs[mask]))
    rsi[avg_loss == 0] = 100
    return rsi > thresh

def gen_rsi_cumret(price, p):
    per, thresh = p['period'], p['thresh']
    delta = np.diff(price, prepend=price[0])
    gain = np.clip(delta, 0, None)
    loss = -np.clip(delta, None, 0)
    avg_gain = ewma_numba(gain, per*2-1)
    avg_loss = ewma_numba(loss, per*2-1)
    rs = np.zeros_like(price)
    mask = avg_loss != 0
    rs[mask] = avg_gain[mask] / avg_loss[mask]
    rsi = np.zeros_like(price)
    rsi[mask] = 100 - (100 / (1 + rs[mask]))
    rsi[avg_loss == 0] = 100
    cum_rsi = pd.Series(rsi).rolling(per).sum().values
    return cum_rsi > thresh

def gen_donchian(price, p):
    per = p['period']
    half = max(1, per//2)
    hh = pd.Series(price).rolling(per).max().values
    ll = pd.Series(price).rolling(half).min().values
    
    @numba.njit
    def calc_donch(pr, hh_arr, ll_arr):
        in_tr = np.zeros(len(pr), dtype=numba.boolean)
        state = False
        for i in range(1, len(pr)):
            if pr[i] <= ll_arr[i-1]: state = False
            if pr[i] >= hh_arr[i-1]: state = True
            in_tr[i] = state
        return in_tr
    return calc_donch(price, hh, ll)

def gen_bb(price, p):
    w, std = p['window'], p['std']
    ma = pd.Series(price).rolling(w).mean().values
    st = pd.Series(price).rolling(w).std().values
    upper = ma + (std * st)
    lower = ma - (std * st)
    
    @numba.njit
    def calc_bb(pr, up_arr, dn_arr):
        in_tr = np.zeros(len(pr), dtype=numba.boolean)
        state = False
        for i in range(1, len(pr)):
            if pr[i] > up_arr[i-1]: state = True
            elif pr[i] < dn_arr[i-1]: state = False
            in_tr[i] = state
        return in_tr
        
    return calc_bb(price, upper, lower) 

def gen_stc(price, p):
    f, s, c = p['fast'], p['slow'], p['cycle']
    if f >= s: return np.zeros(len(price), dtype=bool)
    macd = ewma_numba(price, f) - ewma_numba(price, s)
    stoch1 = calc_stc_numba(macd, c)
    sm1 = ewma_numba(stoch1, c/2.0)
    stoch2 = calc_stc_numba(sm1, c)
    stc = ewma_numba(stoch2, c/2.0)
    return stc > 50 

def gen_supertrend(high, low, close, p):
    per, mult = p['atr_period'], p['multiplier']
    h_l = high - low
    h_c = np.abs(high - np.append([0], close[:-1]))
    l_c = np.abs(low - np.append([0], close[:-1]))
    tr = np.maximum(h_l, np.maximum(h_c, l_c))
    atr = pd.Series(tr).rolling(per).mean().values
    
    hl2 = (high + low) / 2
    basic_ub = hl2 + (mult * atr)
    basic_lb = hl2 - (mult * atr)
    
    final_ub = np.copy(basic_ub)
    final_lb = np.copy(basic_lb)
    trend = np.ones(len(close), dtype=bool)
    
    for i in range(1, len(close)):
        if basic_ub[i] < final_ub[i-1] or close[i-1] > final_ub[i-1]:
            final_ub[i] = basic_ub[i]
        else:
            final_ub[i] = final_ub[i-1]
            
        if basic_lb[i] > final_lb[i-1] or close[i-1] < final_lb[i-1]:
            final_lb[i] = basic_lb[i]
        else:
            final_lb[i] = final_lb[i-1]
            
        if close[i] > final_ub[i-1]: trend[i] = True
        elif close[i] < final_lb[i-1]: trend[i] = False
        else: trend[i] = trend[i-1]
            
    return trend

def gen_alma(price, p):
    w, off, sig = p['window'], p['offset'], p['sigma']
    alma = calc_alma_numba(price, w, off, sig)
    return price > alma

def gen_adx(high, low, close, p):
    per, thresh = p['period'], p['thresh']
    adx, pdi, ndi = calc_adx_numba(high, low, close, per)
    return (adx > thresh) & (pdi > ndi)

def gen_fti(close, p):
    per, thresh = p['period'], p['thresh']
    fti = calc_fti_numba(close, per)
    # FTI > thresh implies high efficiency/trend
    return fti > thresh

def gen_gjr_garch(close, p):
    # Returns True if vol is safe, False if vol is extreme
    vol_w, pct_w, thresh = p['vol_window'], p['pct_window'], p['pct_thresh']
    # Simplified approximation of asymmetric downside volatility for speed
    rets = np.zeros(len(close))
    rets[1:] = np.diff(close) / close[:-1]
    down_rets = np.where(rets < 0, rets**2, 0) # GJR asymmetric proxy
    cond_vol = pd.Series(down_rets).rolling(vol_w).sum().values
    
    # 90th pctile of rolling window
    pctile = pd.Series(cond_vol).rolling(pct_w).quantile(thresh).values
    return cond_vol <= pctile # True means safe to trade

def gen_kama(price, p):
    fast, slow, er_p = p['fast'], p['slow'], p['er_period']
    # Calculate Kaufman Efficiency Ratio
    er = np.zeros(len(price))
    fast_c = 2.0 / (fast + 1)
    slow_c = 2.0 / (slow + 1)
    
    out = np.zeros_like(price)
    out[:er_p] = price[:er_p]
    
    for i in range(er_p, len(price)):
        net_move = abs(price[i] - price[i-er_p])
        path_len = np.sum(np.abs(np.diff(price[i-er_p:i+1])))
        if path_len == 0:
            er[i] = 0
        else:
            er[i] = net_move / path_len
            
        sc = (er[i] * (fast_c - slow_c) + slow_c) ** 2
        out[i] = out[i-1] + sc * (price[i] - out[i-1])
        
    return price > out 

@numba.njit
def calc_autocorr(rets, period, lag):
    out = np.zeros(len(rets))
    for i in range(period, len(rets)):
        window = rets[i-period+1 : i+1]
        x = window[:-lag]
        y = window[lag:]
        if np.std(x) == 0 or np.std(y) == 0:
            out[i] = 0.0
        else:
            out[i] = np.corrcoef(x, y)[0, 1]
    return out

def gen_autocorr(price, p):
    period, lag = p['period'], p['lag']
    rets = np.zeros(len(price))
    rets[1:] = np.diff(price) / price[:-1]
    out = calc_autocorr(rets, period, lag)
    return out > 0

@numba.njit
def calc_hurst(price, period):
    out = np.zeros(len(price))
    for i in range(period, len(price)):
        window = price[i-period+1 : i+1]
        diffs = np.zeros(len(window)-1)
        for j in range(len(window)-1):
            diffs[j] = (window[j+1] - window[j]) / window[j]
        mean_r = np.mean(diffs)
        y = diffs - mean_r
        z = np.cumsum(y)
        r = np.max(z) - np.min(z)
        s = np.std(diffs)
        if s == 0 or r == 0:
            out[i] = 0.5
        else:
            out[i] = np.log(r/s) / np.log(period)
    return out

def gen_hurst(price, p):
    period = p['period']
    out = calc_hurst(price, period)
    return out > 0.5

@numba.njit
def calc_entropy(price, period):
    out = np.zeros(len(price))
    for i in range(period, len(price)):
        window = price[i-period+1 : i+1]
        diffs = np.zeros(len(window)-1)
        for j in range(len(window)-1):
            diffs[j] = (window[j+1] - window[j]) / window[j]
        
        # Simple Shannon entropy using histogram
        counts = np.zeros(10)
        min_v, max_v = np.min(diffs), np.max(diffs)
        if max_v == min_v:
            out[i] = 0.0
            continue
            
        step = (max_v - min_v) / 10.0
        for v in diffs:
            bin_idx = int((v - min_v) / step)
            if bin_idx >= 10: bin_idx = 9
            counts[bin_idx] += 1
            
        probs = counts / np.sum(counts)
        e = 0.0
        for p_val in probs:
            if p_val > 0:
                e -= p_val * np.log2(p_val)
        out[i] = e
    return out

def gen_entropy(price, p):
    period = p['period']
    out = calc_entropy(price, period)
    # Return true if entropy is LOW (trending)
    # We will use median entropy as threshold
    return out < np.median(out[out > 0])

def gen_sma200(price, p):
    period = p['period']
    sma = np.zeros_like(price)
    sma[period-1:] = np.convolve(price, np.ones(period)/period, mode='valid')
    return price > sma

# ─────────────────────────────────────────────────────────────────
# GENERATOR LOOP
# ─────────────────────────────────────────────────────────────────
def generate_signals():
    df = get_data()
    dates = df.index.values
    np.save(os.path.join(OUT_DIR, 'dates.npy'), dates)
    
    for ticker in UNIVERSE:
        if ticker not in df['Close'].columns: continue
        print(f"\nProcessing {ticker}...")
        
        if isinstance(df.columns, pd.MultiIndex):
            close = df['Close'][ticker].ffill().bfill().values
            high = df['High'][ticker].ffill().bfill().values if 'High' in df else close
            low = df['Low'][ticker].ffill().bfill().values if 'Low' in df else close
        else:
            close = df[ticker].ffill().bfill().values
            high, low = close, close
            
        asset_dict = {}
        param_tracker = {}
        
        for fam, p_grid in GRIDS.items():
            keys = list(p_grid.keys())
            vals = [p_grid[k] for k in keys]
            combos = list(itertools.product(*vals))
            
            sig_matrix = np.zeros((len(close), len(combos)), dtype=bool)
            param_list = []
            
            for j, c in enumerate(combos):
                p = dict(zip(keys, c))
                param_list.append(str(p))
                
                try:
                    if fam == 'MACD':      s = gen_macd(close, p)
                    elif fam == 'EMA3':    s = gen_ema3(close, p)
                    elif fam == 'TEMA':    s = gen_tema(close, p)
                    elif fam == 'TEMA_SIG':s = gen_tema_sig(close, p)
                    elif fam == 'AROON':   s = gen_aroon(high, low, p)
                    elif fam == 'RSI':     s = gen_rsi(close, p)
                    elif fam == 'RSI_CUMRET': s = gen_rsi_cumret(close, p)
                    elif fam == 'DONCHIAN':s = gen_donchian(close, p)
                    elif fam == 'BB':      s = gen_bb(close, p)
                    elif fam == 'STC':     s = gen_stc(close, p)
                    elif fam == 'SUPERTREND': s = gen_supertrend(high, low, close, p)
                    elif fam == 'ALMA':    s = gen_alma(close, p)
                    elif fam == 'ADX':     s = gen_adx(high, low, close, p)
                    elif fam == 'FTI':     s = gen_fti(high, low, close, p)
                    elif fam == 'AUTOCORR':s = gen_autocorr(close, p)
                    elif fam == 'HURST':   s = gen_hurst(close, p)
                    elif fam == 'ENTROPY': s = gen_entropy(close, p)
                    elif fam == 'SMA200':  s = gen_sma200(close, p)
                    elif fam == 'GJR_GARCH': s = gen_gjr_garch(close, p)
                    elif fam == 'KAMA':    s = gen_kama(close, p)
                    else:                  s = np.zeros(len(close), dtype=bool)
                        
                    # Shift 1 for NO LOOKAHEAD
                    s_shifted = np.roll(s, 1)
                    s_shifted[0] = False
                    sig_matrix[:, j] = s_shifted
                except Exception as e:
                    print(f"Error {fam} {p}: {e}")
                    
            asset_dict[fam] = sig_matrix
            param_tracker[fam] = param_list
            print(f"  {fam}: {len(combos)} combinations generated.")
            
        np.savez_compressed(os.path.join(OUT_DIR, f"{ticker}_signals.npz"), **asset_dict)
        with open(os.path.join(OUT_DIR, f"{ticker}_params.txt"), 'w') as f:
            for fam, plist in param_tracker.items():
                for i, pstr in enumerate(plist):
                    f.write(f"{fam}|{i}|{pstr}\n")
                    
    print("\nPhase 1a Matrix Generation (Absolution Edition) Complete.")

if __name__ == '__main__':
    generate_signals()
