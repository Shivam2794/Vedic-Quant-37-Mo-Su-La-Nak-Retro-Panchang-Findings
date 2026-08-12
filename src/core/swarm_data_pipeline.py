import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import lfilter
import sys
import argparse

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
    w = get_weights_ffd(d, thres)
    width = len(w)
    res = lfilter(w, [1.0], series.values)
    res_series = pd.Series(res, index=series.index, dtype=float)
    res_series.iloc[:width-1] = np.nan
    return res_series

def yang_zhang_volatility(df, window=21):
    log_ho = (df['High'] / df['Open']).apply(np.log)
    log_lo = (df['Low'] / df['Open']).apply(np.log)
    log_co = (df['Close'] / df['Open']).apply(np.log)
    log_oc = (df['Open'] / df['Close'].shift(1)).apply(np.log)
    
    open_vol = log_oc.rolling(window=window).var(ddof=1)
    close_vol = log_co.rolling(window=window).var(ddof=1)
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    window_rs = rs.rolling(window=window).mean()
    
    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    yz_var = open_vol + k * close_vol + (1 - k) * window_rs
    yz_var.iloc[:window] = np.nan
    return np.sqrt(yz_var)

def execute_pipeline(ticker):
    print(f"[SWARM DATA] Fetching {ticker}...")
    df = yf.download(ticker, start='2010-01-01', end='2025-12-31')
    
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df.dropna()
    print(f"Data points: {len(df)}")
    
    # Base Features
    df['Returns'] = df['Close'].pct_change()
    df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Yang-Zhang Volatility (Dynamic Constraint)
    df['YZ_Vol'] = yang_zhang_volatility(df, window=21)
    
    # Fractional Differentiation (Stationarity without memory loss)
    # Applying on log prices to make it dimensionless
    log_close = np.log(df['Close'])
    df['Frac_Diff'] = frac_diff_ffd(log_close, d=0.10)
    
    # Compute returns on frac diff to prevent negative value pct_change bugs
    df['Frac_Diff_Ret'] = df['Frac_Diff'].diff()
    
    # Standardize Stationary Inputs
    df['Frac_Diff_Z'] = (df['Frac_Diff_Ret'] - df['Frac_Diff_Ret'].rolling(252).mean()) / df['Frac_Diff_Ret'].rolling(252).std()
    df['YZ_Vol_Z'] = (df['YZ_Vol'] - df['YZ_Vol'].rolling(252).mean()) / df['YZ_Vol'].rolling(252).std()
    
    df['RSI_14'] = df['Close'].diff().apply(lambda x: x if x > 0 else 0).rolling(14).mean() / (df['Close'].diff().apply(lambda x: abs(x) if x < 0 else 0).rolling(14).mean() + 1e-8)
    df['RSI_14_Z'] = (df['RSI_14'] - df['RSI_14'].rolling(252).mean()) / df['RSI_14'].rolling(252).std()
    
    df = df.dropna()
    print(f"Post-Feature Engineering Rows: {len(df)}")
    
    out_file = f'{ticker}_daily_V17_raw.parquet'
    df.to_parquet(out_file)
    print(f"[SUCCESS] Saved {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", type=str, required=True)
    args = parser.parse_args()
    execute_pipeline(args.ticker)
