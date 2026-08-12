import os
import json
import numpy as np
import pandas as pd
import warnings
import numba
from opus8_config import IN_DIR, PARQUET_FILE, MANIFEST_FILE, TICKERS_TRADED, LAG

warnings.filterwarnings('ignore')

FAMILIES = ['MACD', 'SMA200']

@numba.njit(cache=True)
def calc_ema_with_mask(arr, span):
    n = arr.shape[0]
    out = np.full(n, np.nan)
    alpha = 2.0 / (span + 1.0)
    
    i0 = -1
    for i in range(n):
        if not np.isnan(arr[i]):
            i0 = i
            break
            
    if i0 < 0:
        return out
        
    out[i0] = arr[i0]
    for i in range(i0 + 1, n):
        if np.isnan(arr[i]):
            out[i] = np.nan # V8 FIX: Do not carry forward EMA when price is NaN (delisting/gaps)
        else:
            # If previous was NaN (gap), reset the EMA to current price
            if np.isnan(out[i-1]):
                out[i] = arr[i]
            else:
                out[i] = arr[i] * alpha + out[i-1] * (1.0 - alpha)
    return out

@numba.njit(cache=True)
def calc_macd_signal_with_mask(close, fast, slow, signal):
    ema_fast = calc_ema_with_mask(close, fast)
    ema_slow = calc_ema_with_mask(close, slow)
    macd = ema_fast - ema_slow
    signal_line = calc_ema_with_mask(macd, signal)
    
    n = close.shape[0]
    sig = np.zeros(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.int8)
    
    burn_in = 5 * slow + 5 * signal
    
    i0 = -1
    for i in range(n):
        if not np.isnan(close[i]):
            i0 = i
            break
            
    if i0 >= 0:
        for i in range(i0 + burn_in, n):
            if not np.isnan(macd[i]) and not np.isnan(signal_line[i]) and not np.isnan(close[i]):
                sig[i] = 1 if macd[i] > signal_line[i] else 0
                valid[i] = 1 # V8 FIX: valid stays 0 if close is NaN (delisting)
                
    return sig, valid

@numba.njit(cache=True)
def calc_sma_with_mask(arr, window):
    n = arr.shape[0]
    out = np.full(n, np.nan)
    i0 = -1
    for i in range(n):
        if not np.isnan(arr[i]):
            i0 = i
            break
            
    if i0 < 0:
        return out
        
    for i in range(i0 + window - 1, n):
        if np.isnan(arr[i]):
            out[i] = np.nan
            continue
            
        s = 0.0
        missing = False
        for j in range(i - window + 1, i + 1):
            if np.isnan(arr[j]):
                missing = True
                break
            s += arr[j]
        if not missing:
            out[i] = s / window
    return out

@numba.njit(cache=True)
def calc_sma200_signal_with_mask(close, window):
    sma = calc_sma_with_mask(close, window)
    n = close.shape[0]
    sig = np.zeros(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.int8)
    
    i0 = -1
    for i in range(n):
        if not np.isnan(close[i]):
            i0 = i
            break
            
    if i0 >= 0:
        for i in range(i0 + window - 1, n):
            if not np.isnan(sma[i]) and not np.isnan(close[i]):
                sig[i] = 1 if close[i] > sma[i] else 0
                valid[i] = 1
                
    return sig, valid

def to_positions(sig, valid, lag=LAG):
    pos = np.zeros_like(sig)
    pos_valid = np.zeros_like(valid)
    pos[:, lag:] = sig[:, :-lag]
    pos_valid[:, lag:] = valid[:, :-lag]
    return pos, pos_valid

def generate_signals(df_ticker, is_causality_test=False, negative_control=False):
    close = df_ticker['Adj Close'].values 
    n = len(close)
    
    macd_params = [(12, 26, 9), (8, 21, 5), (5, 34, 7), (3, 10, 16), (24, 52, 18), (12, 50, 9), (10, 40, 15), (5, 15, 5), (15, 35, 10)]
    macd_sig = np.zeros((9, n), dtype=np.int8)
    macd_val = np.zeros((9, n), dtype=np.int8)
    
    for i, p in enumerate(macd_params):
        macd_sig[i, :], macd_val[i, :] = calc_macd_signal_with_mask(close, p[0], p[1], p[2])
        
    sma_params = [200, 150, 250, 100, 300, 180, 220, 240, 260]
    sma_sig = np.zeros((9, n), dtype=np.int8)
    sma_val = np.zeros((9, n), dtype=np.int8)
    
    for i, p in enumerate(sma_params):
        sma_sig[i, :], sma_val[i, :] = calc_sma200_signal_with_mask(close, p)
        
    if negative_control:
        # V8 FIX: Introduce deliberate same-bar leakage for negative control testing
        return {
            'MACD': macd_sig,
            'MACD_valid': macd_val,
            'SMA200': sma_sig,
            'SMA200_valid': sma_val,
        }
        
    macd_pos, macd_pos_val = to_positions(macd_sig, macd_val)
    sma_pos, sma_pos_val = to_positions(sma_sig, sma_val)
    
    return {
        'MACD': macd_pos,
        'MACD_valid': macd_pos_val,
        'SMA200': sma_pos,
        'SMA200_valid': sma_pos_val,
        'MACD_params': np.array(macd_params),
        'SMA200_params': np.array(sma_params)
    }

def process_all_tickers():
    df = pd.read_parquet(PARQUET_FILE)
    
    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)
        
    data_hash = manifest['data_hash']
    
    for ticker in TICKERS_TRADED:
        df_t = df[df['Ticker'] == ticker]
        dates = df_t.index.get_level_values('Date').astype(np.int64).values
        
        signals = generate_signals(df_t)
        
        for fam in FAMILIES:
            mat = signals[fam]
            valid = signals[f'{fam}_valid']
            
            assert mat.ndim == 2 and mat.size > 0
            assert mat.shape[1] == len(dates)
            assert mat.dtype == np.int8
            assert mat.flags['C_CONTIGUOUS']
            assert ((mat == 0) | (mat == 1)).all()
            
            # V8 FIX: Occupancy computed only over valid entries
            for row in range(mat.shape[0]):
                valid_count = valid[row].sum()
                if valid_count > 0:
                    occ = mat[row, valid[row] == 1].mean()
                    assert 0.001 < occ < 0.999, f"{ticker} {fam} param {row} occupancy: {occ}"
            
            flips = np.abs(np.diff(mat.astype(np.int16), axis=1)).sum(axis=1)
            assert (flips >= 5).all(), f"{ticker} {fam} flips: {flips}"
            
            assert ((mat == 1) & (valid == 0)).sum() == 0, f"{ticker} {fam} invested while invalid!"
            
        npz_data = {
            'dates': dates,
            'data_hash': data_hash,
            'lag': LAG,
            **signals
        }
        
        np.savez_compressed(os.path.join(IN_DIR, f'{ticker}_signals_v8.npz'), **npz_data)
        print(f"Generated and sealed V8 signals for {ticker}")

if __name__ == '__main__':
    process_all_tickers()
