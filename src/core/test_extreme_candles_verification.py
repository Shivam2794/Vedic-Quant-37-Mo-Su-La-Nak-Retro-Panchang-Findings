"""
Automated Verification Suite for SPY Extreme Candlestick Anomalies (V2 Hardened)
Branch: feat/extreme-solid-candlestick-anomalies
"""

import os
import json
import pandas as pd
import numpy as np


def run_verification():
    repo_root = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings"
    data_dir = os.path.join(repo_root, "data")
    
    print("================================================================================")
    print("  RUNNING COMPREHENSIVE ATOMIC VERIFICATION TESTS (V2 HARDENED)")
    print("================================================================================")
    
    timeframes = ['1h', '2h', '4h', '1d', '1w', '1mo']
    total_anomalies_counted = 0
    passed_tests = 0
    total_tests = 0
    
    def assert_test(cond, msg):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if cond:
            passed_tests += 1
            print(f"  [PASS] {msg}")
        else:
            print(f"  [FAIL] {msg}")
            raise AssertionError(f"Test failed: {msg}")

    # Test 1: Summary Stats JSON exists
    summary_path = os.path.join(data_dir, "spy_anomalies_summary_stats.json")
    assert_test(os.path.exists(summary_path), f"Summary JSON exists at {summary_path}")
    with open(summary_path, 'r') as f:
        summary_stats = json.load(f)

    # Test 2: Master Manifest exists and is valid
    master_parquet = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
    master_csv = os.path.join(data_dir, "spy_anomalies_master_manifest.csv")
    assert_test(os.path.exists(master_parquet), f"Master manifest parquet exists: {master_parquet}")
    assert_test(os.path.exists(master_csv), f"Master manifest CSV exists: {master_csv}")
    
    df_master = pd.read_parquet(master_parquet)
    assert_test(len(df_master) > 0, f"Master manifest is non-empty ({len(df_master)} total anomalies)")
    
    time_col = 'Datetime_UTC' if 'Datetime_UTC' in df_master.columns else 'Datetime'
    assert_test(df_master[time_col].is_monotonic_increasing, "Master manifest is sorted in ascending datetime order")
    
    # Test 3: Validate each timeframe individually
    for tf in timeframes:
        parquet_path = os.path.join(data_dir, f"spy_anomalies_{tf}.parquet")
        csv_path = os.path.join(data_dir, f"spy_anomalies_{tf}.csv")
        full_series_path = os.path.join(data_dir, f"spy_full_series_{tf}.parquet")
        
        assert_test(os.path.exists(parquet_path), f"Timeframe [{tf.upper()}] Parquet exists: {parquet_path}")
        assert_test(os.path.exists(csv_path), f"Timeframe [{tf.upper()}] CSV exists: {csv_path}")
        assert_test(os.path.exists(full_series_path), f"Timeframe [{tf.upper()}] Full Series Parquet exists: {full_series_path}")
        
        df_tf = pd.read_parquet(parquet_path)
        df_full = pd.read_parquet(full_series_path)
        
        assert_test(len(df_tf) > 0, f"Timeframe [{tf.upper()}] has {len(df_tf)} extracted anomalies")
        total_anomalies_counted += len(df_tf)
        
        tf_time_col = 'Datetime_UTC' if 'Datetime_UTC' in df_tf.columns else 'Datetime'
        # Check zero duplicates
        dupes = df_tf[tf_time_col].duplicated().sum()
        assert_test(dupes == 0, f"Timeframe [{tf.upper()}] has ZERO duplicate timestamps")
        
        # Check zero NaNs in critical columns
        crit_cols = [tf_time_col, 'Open', 'High', 'Low', 'Close', 'Volume', 'Solid_Ratio', 'RVOL', 'Body_ATR_Ratio', 'Direction']
        for c in crit_cols:
            assert_test(df_tf[c].isna().sum() == 0, f"Timeframe [{tf.upper()}] column '{c}' has ZERO NaNs")
            
        # Mathematical Condition Verification:
        # A) Solid Ratio >= 0.65
        invalid_solid = (df_tf['Solid_Ratio'] < 0.65).sum()
        assert_test(invalid_solid == 0, f"Timeframe [{tf.upper()}] 100% of rows have Solid_Ratio >= 0.65 (min: {df_tf['Solid_Ratio'].min():.3f})")
        
        # B) RVOL >= 1.50
        invalid_rvol = (df_tf['RVOL'] < 1.50).sum()
        assert_test(invalid_rvol == 0, f"Timeframe [{tf.upper()}] 100% of rows have RVOL >= 1.50 (min: {df_tf['RVOL'].min():.2f}x)")
        
        # C) Direction in {'GREEN', 'RED'}
        invalid_dir = (~df_tf['Direction'].isin(['GREEN', 'RED'])).sum()
        assert_test(invalid_dir == 0, f"Timeframe [{tf.upper()}] 100% of rows have valid GREEN or RED direction")
        
        # D) Magnitude: Body/ATR >= 1.50 or Abs_Body_Return_Pct >= Min_Return_Floor
        ret_col = 'Abs_Body_Return_Pct' if 'Abs_Body_Return_Pct' in df_tf.columns else 'Abs_Return_Pct'
        valid_mag = ((df_tf['Body_ATR_Ratio'] >= 1.50) | (df_tf[ret_col] >= df_tf['Min_Return_Floor'])).all()
        assert_test(valid_mag, f"Timeframe [{tf.upper()}] 100% of rows meet big magnitude criteria")
        
        # E) Wick dominance check
        if 'Max_Wick_Ratio' in df_tf.columns:
            invalid_wicks = (df_tf['Max_Wick_Ratio'] > 0.25).sum()
            assert_test(invalid_wicks == 0, f"Timeframe [{tf.upper()}] 100% of rows satisfy Max_Wick_Ratio <= 0.25 (max: {df_tf['Max_Wick_Ratio'].max():.3f})")

        # Full historical evaluation dataset span check
        full_start_year = pd.to_datetime(df_full[tf_time_col]).dt.year.min()
        if tf in ['1h', '2h', '4h']:
            assert_test(full_start_year <= 2016, f"Timeframe [{tf.upper()}] full evaluated history starts in {full_start_year} (<= 2016)")
        else:
            assert_test(full_start_year <= 1993, f"Timeframe [{tf.upper()}] full evaluated history starts in {full_start_year} (<= 1993)")

    # Test 4: Master Manifest length equals sum of all timeframes
    assert_test(len(df_master) == total_anomalies_counted,
                f"Master manifest row count ({len(df_master)}) matches sum of timeframe counts ({total_anomalies_counted})")
    
    print("\n================================================================================")
    print(f"  ALL {passed_tests}/{total_tests} VERIFICATION AUDITS PASSED WITH 100% MATHEMATICAL RIGOR")
    print("================================================================================")
    
    return True


if __name__ == "__main__":
    run_verification()
