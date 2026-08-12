"""
Fractional Differentiation (Phase 1)
====================================
Standard integer differencing (d=1) removes stationarity issues but strips out all memory 
(which ruins slow-moving astrological cycles). 

This script applies Fractional Differentiation to the non-stationary planetary longitudes, 
finding the minimum $d^*$ that achieves stationarity (ADF p-value < 0.05) while maximizing 
the preservation of the original signal memory (correlation).

Outputs a series of weights and the fractionally differenced time series.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def get_weights(d, size):
    """
    Returns weights for fractional differentiation.
    w = [1, -d, d(d-1)/2!, -d(d-1)(d-2)/3!, ...]
    """
    w = [1.]
    for k in range(1, size):
        w_ = -w[-1] / k * (d - k + 1)
        w.append(w_)
    return np.array(w[::-1]).reshape(-1, 1)

def frac_diff(series, d, thres=1e-5):
    """
    Applies fractional differentiation to a pandas Series using a weight threshold.
    """
    # 1. Compute weights
    w = [1.]
    for k in range(1, len(series)):
        w_ = -w[-1] / k * (d - k + 1)
        if abs(w_) < thres:
            break
        w.append(w_)
    w = np.array(w[::-1]).reshape(-1, 1)
    
    # 2. Apply weights to series
    df = pd.Series(index=series.index, dtype=float)
    width = len(w)
    for i in range(width - 1, len(series)):
        window = series.iloc[i - width + 1 : i + 1].values.reshape(-1, 1)
        df.iloc[i] = np.dot(w.T, window)[0, 0]
        
    return df.dropna()

def find_optimal_d(series, max_d=1.0, step=0.1, p_val_thresh=0.05):
    """
    Finds the minimum fractional differencing parameter d* that passes the 
    Augmented Dickey-Fuller test for stationarity.
    """
    out = pd.DataFrame(columns=['adf_stat', 'p_val', 'corr', 'd'])
    for d in np.arange(0.0, max_d + step, step):
        if d == 0.0:
            df_diff = series
        else:
            df_diff = frac_diff(series, d)
            
        if len(df_diff) < 20: # Not enough data
            continue
            
        res = adfuller(df_diff, maxlag=1, regression='c', autolag=None)
        corr = np.corrcoef(series.loc[df_diff.index], df_diff)[0, 1]
        
        out.loc[d] = [res[0], res[1], corr, d]
        
        # Stop early if we found a stationary series with the lowest possible d
        if res[1] <= p_val_thresh:
            break
            
    return out

def process_parquet_partition(parquet_path):
    """
    Reads a partitioned parquet file, applies fractional differentiation to all 
    planetary longitudes, and outputs the updated dataframe.
    """
    print(f"Loading {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    
    lon_cols = [c for c in df.columns if "longitude" in c and not c.endswith("_sin") and not c.endswith("_cos")]
    
    print(f"Finding optimal d* for {len(lon_cols)} longitude series...")
    optimal_d_vals = {}
    
    for col in lon_cols:
        series = df[col].dropna()
        if len(series) < 100:
            continue
            
        res_df = find_optimal_d(series, max_d=1.5, step=0.1)
        if not res_df.empty:
            best_d = res_df['d'].iloc[-1]
            p_val = res_df['p_val'].iloc[-1]
            corr = res_df['corr'].iloc[-1]
            optimal_d_vals[col] = best_d
            print(f"  {col}: d* = {best_d:.1f} (p-val={p_val:.4f}, corr={corr:.3f})")
            
            # Apply transformation
            df[f"{col}_frac_diff"] = frac_diff(series, best_d)
            
    return df, optimal_d_vals

if __name__ == "__main__":
    # Example usage for testing Phase 1
    # Note: Requires the output from generate_matrix.py
    import glob
    files = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned\**\*.parquet", recursive=True)
    if files:
        test_file = files[0]
        df, optimal_d = process_parquet_partition(test_file)
        print("Test Complete. Differentiated columns added.")
    else:
        print("No partitioned parquet files found to test.")
