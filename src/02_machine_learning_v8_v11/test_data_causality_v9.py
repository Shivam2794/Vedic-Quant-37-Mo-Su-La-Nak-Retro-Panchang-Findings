import os
import sys
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
from unittest.mock import patch
from opus8_config import OUT_DIR, PARQUET_FILE, MANIFEST_FILE, CANONICAL_TICKER, TICKERS_TRADED
import download_and_freeze_data_v3

def test_data_prefix_invariance():
    print("Running base data freeze...")
    download_and_freeze_data_v3.download_and_freeze()
    
    base_df = pd.read_parquet(PARQUET_FILE)
    
    # We will mock yf.download to return truncated versions of the raw data.
    print("Fetching raw data for truncation...")
    raw_df = yf.download(TICKERS_TRADED, start='1999-01-01', auto_adjust=False, progress=False)
    raw_irx = yf.download(['^IRX'], start='1999-01-01', auto_adjust=False, progress=False)
    
    spy_idx = raw_df['Close'][CANONICAL_TICKER].dropna().index.normalize()
    
    np.random.seed(42)
    # Pick 20 random truncation dates, avoiding the very beginning
    trunc_indices = np.random.choice(range(500, len(spy_idx)-10), size=20, replace=False)
    trunc_dates = spy_idx[trunc_indices]
    
    for i, t_date in enumerate(trunc_dates):
        print(f"Testing truncation {i+1}/20 at {t_date.date()}...")
        
        # Truncate raw data up to t_date
        trunc_raw_df = raw_df[raw_df.index.normalize() <= t_date].copy()
        trunc_raw_irx = raw_irx[raw_irx.index.normalize() <= t_date].copy()
        
        # Create mock side effects
        def mock_download(tickers, *args, **kwargs):
            if '^IRX' in tickers:
                return trunc_raw_irx
            return trunc_raw_df
            
        # We override PARQUET_FILE and MANIFEST_FILE temporarily
        temp_parquet = PARQUET_FILE + '.test'
        temp_manifest = MANIFEST_FILE + '.test'
        
        with patch('yfinance.download', side_effect=mock_download), \
             patch('download_and_freeze_data_v3.PARQUET_FILE', temp_parquet), \
             patch('download_and_freeze_data_v3.MANIFEST_FILE', temp_manifest):
            download_and_freeze_data_v3.download_and_freeze()
            
        # Load the truncated parquet
        trunc_df = pd.read_parquet(temp_parquet)
        
        # Verify it is an exact prefix of the base_df
        for ticker in TICKERS_TRADED:
            base_t = base_df.loc[ticker]
            trunc_t = trunc_df.loc[ticker]
            
            # The dates in trunc_t should exactly match the prefix of base_t
            base_prefix = base_t[base_t.index <= t_date]
            
            # They should have the exact same shape
            assert len(trunc_t) == len(base_prefix), f"Length mismatch for {ticker} at {t_date}"
            
            # Assert all values match (including NaNs)
            pd.testing.assert_frame_equal(trunc_t, base_prefix)
            
    print("✅ End-to-end data prefix invariance PASS")
    
if __name__ == '__main__':
    test_data_prefix_invariance()
