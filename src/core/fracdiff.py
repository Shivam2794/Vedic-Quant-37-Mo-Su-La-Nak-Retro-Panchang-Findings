import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

from scipy.signal import lfilter

def get_weights(d, size):
    w = [1.]
    for k in range(1, size):
        w_ = -w[-1] / k * (d - k + 1)
        w.append(w_)
    return np.array(w)

def frac_diff_ffd(series, d, thres=1e-4):
    w = get_weights(d, len(series))
    
    # Expanding window frac diff using lfilter
    # w[0]=1 (current), w[1] (t-1), etc.
    res = lfilter(w, [1.0], series.values)
    
    res_series = pd.Series(res, index=series.index, dtype=float)
    return res_series

def find_min_d(series, max_d=1.0, step=0.1, p_val_thresh=0.05):
    for d in np.arange(0.1, max_d + step, step):
        fd = frac_diff_ffd(series, d)
        fd = fd.dropna()
        if len(fd) > 0:
            p_val = adfuller(fd, maxlag=1, regression='c', autolag=None)[1]
            if p_val < p_val_thresh:
                return d
    return max_d

if __name__ == '__main__':
    qqq_d = pd.read_parquet('qqq_daily.parquet')
    qqq_d.index = pd.to_datetime(qqq_d.index).tz_convert('America/New_York')
    
    # Let's find optimal d for QQQ Close
    log_close = np.log(qqq_d['Close'])
    opt_d = find_min_d(log_close, max_d=1.0, step=0.05)
    print(f"Optimal d for QQQ log(Close): {opt_d:.2f}")
    
    fd_series = frac_diff_ffd(log_close, opt_d)
    corr = np.corrcoef(log_close.loc[fd_series.dropna().index], fd_series.dropna())[0,1]
    print(f"Correlation with original: {corr:.4f}")
