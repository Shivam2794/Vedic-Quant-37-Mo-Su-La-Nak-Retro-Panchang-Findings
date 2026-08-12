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
def calc_ema_with_mask(arr, has_print, span):
    n = arr.shape[0]
    out = np.full(n, np.nan)
    alpha = 2.0 / (span + 1.0)
    
    i0 = -1
    for i in range(n):
        if has_print[i]:
            i0 = i
            break
            
    if i0 < 0:
        return out, np.zeros(n, dtype=np.int32)
        
    out[i0] = arr[i0]
    bars_since_reset = np.zeros(n, dtype=np.int32)
    bars_since_reset[i0] = 1
    
    consecutive_missing = 0
    
    for i in range(i0 + 1, n):
        if not has_print[i]:
            consecutive_missing += 1
            # We still compute EMA on filled bars if they exist (carry state)
            if not np.isnan(arr[i]):
                out[i] = arr[i] * alpha + out[i-1] * (1.0 - alpha)
                bars_since_reset[i] = bars_since_reset[i-1] + 1
            else:
                out[i] = np.nan
                bars_since_reset[i] = bars_since_reset[i-1]
        else:
            if consecutive_missing > 3 or np.isnan(out[i-1]):
                # Reset EMA to spot if gap > 3 or previous was NaN
                out[i] = arr[i]
                bars_since_reset[i] = 1
            else:
                out[i] = arr[i] * alpha + out[i-1] * (1.0 - alpha)
                bars_since_reset[i] = bars_since_reset[i-1] + 1
            consecutive_missing = 0
            
    return out, bars_since_reset

@numba.njit(cache=True)
def calc_macd_signal_with_mask(close, has_print, fast, slow, signal):
    ema_fast, reset_fast = calc_ema_with_mask(close, has_print, fast)
    ema_slow, reset_slow = calc_ema_with_mask(close, has_print, slow)
    macd = ema_fast - ema_slow
    
    # We pass a dummy has_print to signal_line EMA because macd doesn't have "prints", it's continuous except at resets
    dummy_has_print = np.ones_like(has_print, dtype=np.bool_)
    for i in range(len(has_print)):
        if np.isnan(macd[i]):
            dummy_has_print[i] = False
            
    signal_line, reset_sig = calc_ema_with_mask(macd, dummy_has_print, signal)
    
    n = close.shape[0]
    sig = np.zeros(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.int8)
    
    burn_in = 5 * slow + 5 * signal
    
    for i in range(n):
        # We need ALL EMA lines to have sufficient burn-in from their last reset
        if reset_slow[i] >= burn_in and reset_fast[i] >= burn_in and reset_sig[i] >= burn_in:
            if not np.isnan(macd[i]) and not np.isnan(signal_line[i]) and not np.isnan(close[i]):
                sig[i] = 1 if macd[i] > signal_line[i] else 0
                valid[i] = 1
                
    return sig, valid

@numba.njit(cache=True)
def calc_sma_with_mask(arr, has_print, window):
    n = arr.shape[0]
    out = np.full(n, np.nan)
    valid_mask = np.zeros(n, dtype=np.int8)
    
    i0 = -1
    for i in range(n):
        if has_print[i]:
            i0 = i
            break
            
    if i0 < 0:
        return out, valid_mask
        
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
            valid_mask[i] = 1
    return out, valid_mask

@numba.njit(cache=True)
def calc_sma200_signal_with_mask(close, has_print, window):
    sma, sma_valid = calc_sma_with_mask(close, has_print, window)
    n = close.shape[0]
    sig = np.zeros(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.int8)
    
    for i in range(n):
        if sma_valid[i] == 1 and not np.isnan(close[i]):
            sig[i] = 1 if close[i] > sma[i] else 0
            valid[i] = 1
                
    return sig, valid

def to_positions(sig, valid, tradeable, lag=LAG):
    assert lag >= 0, "Lag must be >= 0"
    pos = np.zeros_like(sig)
    pos_valid = np.zeros_like(valid)
    
    if lag == 0:
        pos = sig.copy()
        pos_valid = valid.copy() & tradeable
        for row in range(sig.shape[0]):
            pos[row, :] = np.where(pos_valid[row, :], pos[row, :], 0)
        return pos, pos_valid
    
    for row in range(sig.shape[0]):
        pos[row, lag:] = sig[row, :-lag]
        
        # tradeability mask
        t_mask = tradeable[lag:] & tradeable[lag-1:-1]
        s_val = valid[row, :-lag]
        
        pos_valid[row, lag:] = s_val & t_mask
        pos[row, lag:] = np.where(pos_valid[row, lag:], pos[row, lag:], 0)
        
    return pos, pos_valid

def generate_signals(df_ticker, lag=LAG, is_causality_test=False, negative_control=False):
    close = df_ticker['Adj Close'].values 
    has_print = df_ticker['has_print'].values
    tradeable = df_ticker['has_print'].values # tradeable implies has_print
    
    n = len(close)
    
    macd_params = [(12, 26, 9), (8, 21, 5), (5, 34, 7), (3, 10, 16), (24, 52, 18), (12, 50, 9), (10, 40, 15), (5, 15, 5), (15, 35, 10)]
    macd_sig = np.zeros((9, n), dtype=np.int8)
    macd_val = np.zeros((9, n), dtype=np.int8)
    
    for i, p in enumerate(macd_params):
        macd_sig[i, :], macd_val[i, :] = calc_macd_signal_with_mask(close, has_print, p[0], p[1], p[2])
        
    sma_params = [200, 150, 250, 100, 300, 180, 220, 240, 260]
    sma_sig = np.zeros((9, n), dtype=np.int8)
    sma_val = np.zeros((9, n), dtype=np.int8)
    
    for i, p in enumerate(sma_params):
        sma_sig[i, :], sma_val[i, :] = calc_sma200_signal_with_mask(close, has_print, p)
        
    if negative_control:
        # DO NOT SHIP
        return {
            'MACD_UNLAGGED_DO_NOT_SHIP': macd_sig,
            'MACD_valid_UNLAGGED_DO_NOT_SHIP': macd_val,
            'SMA200_UNLAGGED_DO_NOT_SHIP': sma_sig,
            'SMA200_valid_UNLAGGED_DO_NOT_SHIP': sma_val,
        }
        
    macd_pos, macd_pos_val = to_positions(macd_sig, macd_val, tradeable, lag)
    sma_pos, sma_pos_val = to_positions(sma_sig, sma_val, tradeable, lag)
    
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
    
    temp_dir = os.path.join(IN_DIR, 'tmp_v9')
    os.makedirs(temp_dir, exist_ok=True)
    
    for ticker in TICKERS_TRADED:
        df_t = df[df['Ticker'] == ticker]
        
        # Check monotonicity and uniqueness
        assert df_t.index.is_monotonic_increasing
        assert df_t.index.is_unique
        
        dates = df_t.index.get_level_values('Date').astype(np.int64).values
        
        signals = generate_signals(df_t, lag=LAG)
        
        # Oracle checks: Ensure we're not producing NaN returns on valid positions
        adj = df_t['Adj Close'].values
        ret = np.zeros_like(adj)
        ret[1:] = adj[1:] / adj[:-1] - 1.0
        
        for fam in FAMILIES:
            mat = signals[fam]
            valid = signals[f'{fam}_valid']
            
            assert mat.ndim == 2 and mat.size > 0
            assert mat.shape[1] == len(dates)
            assert mat.dtype == np.int8
            assert mat.flags['C_CONTIGUOUS']
            assert ((mat == 0) | (mat == 1)).all()
            
            # Occupancy computed only over valid entries
            for row in range(mat.shape[0]):
                valid_mask = (valid[row] == 1)
                valid_count = valid_mask.sum()
                if valid_count > 0:
                    occ = mat[row, valid_mask].mean()
                    assert 0.001 < occ < 0.999, f"{ticker} {fam} param {row} occupancy: {occ}"
                    
                    # Compute flips only on valid bars
                    valid_idx = np.where(valid_mask)[0]
                    if len(valid_idx) > 1:
                        flips = np.abs(np.diff(mat[row, valid_idx])).sum()
                        assert flips >= 5, f"{ticker} {fam} row {row} flips: {flips}"
                        
                # Ensure no NaN returns when valid
                invalid_returns = np.isnan(ret[valid_mask])
                assert not invalid_returns.any(), f"{ticker} {fam} row {row} has valid=1 but return is NaN!"
                
            assert ((mat == 1) & (valid == 0)).sum() == 0, f"{ticker} {fam} invested while invalid!"
            
            # Artifact self-description
            # Note: We can't strictly assert equality with raw unlagged signal anymore because `pos` is zeroed out when `pos_valid` is 0.
            
        npz_data = {
            'dates': dates,
            'data_hash': data_hash,
            'lag': LAG,
            **signals
        }
        
        np.savez_compressed(os.path.join(temp_dir, f'{ticker}_signals_v9.npz'), **npz_data)
        print(f"Generated V9 signals for {ticker}")
        
    # Atomic rename
    for ticker in TICKERS_TRADED:
        os.replace(os.path.join(temp_dir, f'{ticker}_signals_v9.npz'), os.path.join(IN_DIR, f'{ticker}_signals_v9.npz'))
    os.rmdir(temp_dir)
    print("All V9 artifacts atomically sealed.")

if __name__ == '__main__':
    process_all_tickers()
