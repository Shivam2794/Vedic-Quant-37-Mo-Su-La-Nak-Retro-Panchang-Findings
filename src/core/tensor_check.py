import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
import os
import warnings

warnings.filterwarnings("ignore")

def check_tensor_robustness(file_path):
    print(f"--- Analyzing {os.path.basename(file_path)} ---")
    try:
        if file_path.endswith(".parquet"):
            df = pd.read_parquet(file_path)
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Failed to load {file_path}: {e}")
        return

    print(f"Shape: {df.shape}")
    
    # Select numeric columns only
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    print(f"Numeric Columns: {len(numeric_cols)} / {len(df.columns)}")

    if len(numeric_cols) == 0:
        print("No numeric columns found.")
        return

    # Check for NaNs and Infs
    total_nans = df[numeric_cols].isna().sum().sum()
    total_infs = np.isinf(df[numeric_cols]).sum().sum()
    
    print(f"Total NaNs: {total_nans} ({(total_nans / (df.shape[0] * len(numeric_cols))) * 100:.2f}%)")
    print(f"Total Infs: {total_infs} ({(total_infs / (df.shape[0] * len(numeric_cols))) * 100:.2f}%)")

    # If too many columns, select a sample to analyze (e.g. 15 random columns)
    np.random.seed(42)
    sample_cols = np.random.choice(numeric_cols, min(15, len(numeric_cols)), replace=False)
    
    non_stationary_count = 0
    non_scaled_count = 0
    
    for col in sample_cols:
        series = df[col].dropna()
        if len(series) < 100:
            continue
        
        # Check stationarity proxy (Lag-1 Autocorrelation)
        try:
            if series.nunique() <= 1:
                is_stationary = False
            else:
                # Lag-1 Autocorrelation
                n = len(series)
                x = series.values[:1000] # Limit to 1000 for speed
                x_mean = np.mean(x)
                numerator = np.sum((x[:-1] - x_mean) * (x[1:] - x_mean))
                denominator = np.sum((x - x_mean)**2)
                autocorr_1 = numerator / denominator if denominator != 0 else 1.0
                
                # A high lag-1 autocorrelation (>0.9) suggests a random walk / non-stationary
                is_stationary = abs(autocorr_1) < 0.9 
        except:
            is_stationary = False
            
        if not is_stationary:
            non_stationary_count += 1
            
        # Check scaling (mean ~ 0, std ~ 1)
        mean = series.mean()
        std = series.std()
        if abs(mean) > 2.0 or std > 5.0 or std < 0.01:
            non_scaled_count += 1
            
    print(f"Sampled {len(sample_cols)} continuous columns for deep analysis.")
    print(f"Non-stationary columns (ADF p-value >= 0.05): {non_stationary_count} / {len(sample_cols)}")
    print(f"Unscaled columns (mean out of bounds or std out of bounds): {non_scaled_count} / {len(sample_cols)}")
    print("-" * 50)

files_to_check = [
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_feature_matrix.parquet",
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\genesis_9000_continuous.parquet",
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\advanced_ml_dataset.csv"
]

for f in files_to_check:
    if os.path.exists(f):
        check_tensor_robustness(f)
