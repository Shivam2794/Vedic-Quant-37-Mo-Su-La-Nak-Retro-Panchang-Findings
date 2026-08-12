import pandas as pd
import numpy as np
import os
from scipy.signal import lfilter

def get_weights_ffd(d, thres=1e-4):
    w = [1.]
    k = 1
    while True:
        w_ = -w[-1] / k * (d - k + 1)
        if abs(w_) < thres:
            break
        w.append(w_)
        k += 1
    return np.array(w)

def frac_diff_ffd(series, d, thres=1e-4):
    # Constant width window based on threshold
    w = get_weights_ffd(d, thres)
    width = len(w)
    
    # Convolution with padding
    # We want to use valid mode to ensure we don't have look-ahead or expanding window bias
    # But for a pandas series, we can just use lfilter and then NaN out the warmup period
    res = lfilter(w, [1.0], series.values)
    res_series = pd.Series(res, index=series.index, dtype=float)
    
    # NaN out the warmup period to strictly enforce constant width
    res_series.iloc[:width-1] = np.nan
    return res_series

def yang_zhang_volatility(df, window=21):
    # Yang-Zhang Volatility
    log_ho = (df['High'] / df['Open']).apply(np.log)
    log_lo = (df['Low'] / df['Open']).apply(np.log)
    log_co = (df['Close'] / df['Open']).apply(np.log)
    
    log_oc = (df['Open'] / df['Close'].shift(1)).apply(np.log)
    
    # YZ uses sample variance for open and close vols
    open_vol = log_oc.rolling(window=window).var(ddof=1)
    close_vol = log_co.rolling(window=window).var(ddof=1)
    
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    
    window_rs = rs.rolling(window=window).mean()
    
    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    
    yz_var = open_vol + k * close_vol + (1 - k) * window_rs
    yz_var.iloc[:window] = np.nan
    yz_vol = np.sqrt(yz_var) * np.sqrt(252)
    return yz_vol

def build_v16_features(df_daily: pd.DataFrame) -> pd.DataFrame:
    d = df_daily.copy()
    
    print("[INFO] Computing Fixed-Width Fractional Differentiation (d=0.10)...")
    d['FD_Close'] = frac_diff_ffd(np.log(d['Close']), 0.10, thres=1e-4)
    
    print("[INFO] Computing Yang-Zhang Volatility...")
    d['YZ_Vol_21'] = yang_zhang_volatility(d, window=21)
    d['YZ_Vol_63'] = yang_zhang_volatility(d, window=63)
    d['YZ_Vol_252'] = yang_zhang_volatility(d, window=252)
    
    # Base features on FD_Close
    delta = d['FD_Close'].diff()
    d['RSI_FD'] = 100 - (100 / (1 + (
        delta.where(delta > 0, 0).rolling(14).mean() /
        np.clip(-delta.where(delta < 0, 0).rolling(14).mean(), 1e-10, None)
    )))
    
    # ROC Z-Scores (using difference instead of pct_change since FD_Close has negative values)
    d['ROC_5'] = d['FD_Close'].diff(5)
    d['ROC_21'] = d['FD_Close'].diff(21)
    
    # 63-day rolling normalization (defines our max purge window)
    d['ROC_5_Z'] = (d['ROC_5'] - d['ROC_5'].rolling(63).mean()) / np.clip(d['ROC_5'].rolling(63).std(), 1e-8, None)
    d['ROC_21_Z'] = (d['ROC_21'] - d['ROC_21'].rolling(63).mean()) / np.clip(d['ROC_21'].rolling(63).std(), 1e-8, None)
    
    # Distance to SMAs (Stationary)
    sma_20 = d['Close'].rolling(20).mean()
    sma_50 = d['Close'].rolling(50).mean()
    d['Dist_SMA20'] = (d['Close'] / sma_20) - 1.0
    d['Dist_SMA50'] = (d['Close'] / sma_50) - 1.0
    
    return d

if __name__ == '__main__':
    print("V16 Data Pipeline Executing...")
    df = pd.read_parquet('qqq_daily.parquet')
    df_feats = build_v16_features(df)
    df_feats = df_feats.dropna()
    df_feats.to_parquet('qqq_daily_V16_feats.parquet')
    print("[SUCCESS] V16 Features computed and saved.")
