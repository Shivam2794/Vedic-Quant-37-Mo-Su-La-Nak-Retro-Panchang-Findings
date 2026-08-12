import os
import numpy as np
import pandas as pd
import warnings
import numba

# Suppress annoying pandas warnings
warnings.filterwarnings('ignore')

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
PARQUET_FILE = os.path.join(IN_DIR, 'frozen_universe_data.parquet')

# Exclude IRX as it's our cash yield
TICKERS = ['SPY', 'QQQ', 'TQQQ', 'UPRO', 'TLT', 'GLD', 'BTC-USD']

# Re-enabling GJR_GARCH and SMA200!
FAMILIES = [
    'MACD', 'RSI', 'BB', 'EMA3', 'KAMA', 'ALMA', 'TEMA', 
    'TEMA_SIG', 'DONCHIAN', 'AROON', 'STC', 'ADX', 'RSI_CUMRET',
    'SMA200', 'GJR_GARCH'
]

# Numba optimized functions for speed
@numba.njit(cache=True)
def calc_ema(arr, span):
    alpha = 2 / (span + 1)
    out = np.zeros_like(arr)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        if np.isnan(arr[i]):
            out[i] = out[i-1]
        else:
            out[i] = arr[i] * alpha + out[i-1] * (1 - alpha)
    return out

@numba.njit(cache=True)
def calc_macd_signal(close, fast, slow, signal):
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)
    macd = ema_fast - ema_slow
    signal_line = calc_ema(macd, signal)
    return np.where(macd > signal_line, 1, 0).astype(np.int8)

@numba.njit(cache=True)
def calc_rsi_signal(close, period, upper, lower):
    delta = np.zeros_like(close)
    delta[1:] = close[1:] - close[:-1]
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    
    rs_up = calc_ema(up, period)
    rs_down = calc_ema(down, period)
    
    rsi = np.zeros_like(close)
    for i in range(len(close)):
        if rs_down[i] == 0:
            rsi[i] = 100
        else:
            rsi[i] = 100 - (100 / (1 + rs_up[i] / rs_down[i]))
            
    # Oversold = Buy (Contrarian)
    return np.where(rsi < lower, 1, 0).astype(np.int8)

@numba.njit(cache=True)
def calc_sma(arr, window):
    out = np.zeros_like(arr)
    for i in range(len(arr)):
        if i < window - 1:
            out[i] = np.nan
        else:
            out[i] = np.nanmean(arr[i-window+1:i+1])
    return out

@numba.njit(cache=True)
def calc_sma200_signal(close):
    sma = calc_sma(close, 200)
    return np.where(close > sma, 1, 0).astype(np.int8)

# Simplified generator for demonstration of the causality test
# We will just generate 2 families for the causality test first
def generate_signals(df_ticker, is_causality_test=False):
    close = df_ticker['Close'].ffill().values
    n = len(close)
    
    # 9 param combos for MACD
    macd_params = [(12, 26, 9), (8, 21, 5), (5, 34, 7), (3, 10, 16), (24, 52, 18), (12, 50, 9), (10, 40, 15), (5, 15, 5), (15, 35, 10)]
    macd_mat = np.zeros((9, n), dtype=np.int8)
    for i, p in enumerate(macd_params):
        macd_mat[i, :] = calc_macd_signal(close, p[0], p[1], p[2])
        
    # 9 param combos for SMA200 (using different periods around 200 for variations)
    sma_params = [200, 150, 250, 100, 300, 180, 220, 240, 260]
    sma_mat = np.zeros((9, n), dtype=np.int8)
    for i, p in enumerate(sma_params):
        sma = calc_sma(close, p)
        sma_mat[i, :] = np.where(close > sma, 1, 0).astype(np.int8)
        
    if is_causality_test:
        return {'MACD': macd_mat, 'SMA200': sma_mat}
        
    # We will expand this to all families in the next step, once causality is proven.
    return {'MACD': macd_mat, 'SMA200': sma_mat}

def process_all_tickers():
    df = pd.read_parquet(PARQUET_FILE)
    
    for ticker in TICKERS:
        df_t = df[df['Ticker'] == ticker]
        signals = generate_signals(df_t)
        
        # FATAL-9 FIX: Assert dtype is strictly int8 and contains only 0 or 1
        for fam, mat in signals.items():
            assert mat.dtype == np.int8, f"{ticker} {fam} dtype is {mat.dtype}, expected int8"
            assert np.isin(np.unique(mat), [0, 1]).all(), f"{ticker} {fam} contains invalid values!"
            
        np.savez_compressed(os.path.join(IN_DIR, f'{ticker}_signals_v6.npz'), **signals)
        print(f"Generated and sealed V6 signals for {ticker}")

if __name__ == '__main__':
    process_all_tickers()
