import os
import sys
import time
import numpy as np
import pandas as pd

def run_verification():
    path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\7b03663a-d01b-4302-8959-0a511c484299\scratch\universe_data.parquet"
    print(f"Loading data from {path}...")
    
    # 7. Test how the DataFrame handles loading and indexing
    start_load = time.time()
    df = pd.read_parquet(path)
    end_load = time.time()
    load_time = end_load - start_load
    print(f"Loaded successfully in {load_time:.4f} seconds.")
    print(f"DataFrame shape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Let's perform some indexing tests
    start_idx = time.time()
    # Slicing by date range
    sub_df = df.loc['2020-01-01':'2020-12-31']
    # Selecting single ticker
    nvda_close = df.loc[:, ('Adj Close', 'NVDA')]
    # Selecting all Close
    adj_closes = df['Adj Close']
    end_idx = time.time()
    idx_time = end_idx - start_idx
    print(f"Indexing operations completed in {idx_time:.4f} seconds.")
    
    errors = []
    warnings = []
    
    # 1. Exactly 0 infinite values in the entire DataFrame
    inf_mask = np.isinf(df)
    inf_count = inf_mask.sum().sum()
    print(f"Check 1 (Infinite values): Found {inf_count} infinite values.")
    if inf_count != 0:
        errors.append(f"Infinite values found: {inf_count}")
        # Identify where they are
        inf_locations = inf_mask.stack()
        inf_locations = inf_locations[inf_locations]
        print("Infinite locations:", inf_locations.index.tolist()[:10])
        
    # 2. Exactly 0 negative prices in 'Adj Close' (i.e. all non-NaN entries are >= 0.0001)
    if 'Adj Close' in df.columns.levels[0]:
        close_df = df['Adj Close']
        invalid_prices_mask = (close_df < 0.0001) & close_df.notna()
        invalid_prices_count = invalid_prices_mask.sum().sum()
        print(f"Check 2 (Adj Close >= 0.0001): Found {invalid_prices_count} invalid price entries.")
        if invalid_prices_count != 0:
            errors.append(f"Invalid prices (< 0.0001) found: {invalid_prices_count}")
            # Locate some invalid prices
            invalid_locs = invalid_prices_mask.stack()
            invalid_locs = invalid_locs[invalid_locs]
            print("Invalid price locations (first 10):")
            for idx in invalid_locs.index[:10]:
                val = close_df.loc[idx]
                print(f"  {idx}: {val}")
    else:
        errors.append("Column level 0 'Adj Close' not found!")
        
    # 3. All volume values are non-negative
    if 'Volume' in df.columns.levels[0]:
        vol_df = df['Volume']
        neg_vol_mask = (vol_df < 0) & vol_df.notna()
        neg_vol_count = neg_vol_mask.sum().sum()
        print(f"Check 3 (Volume >= 0): Found {neg_vol_count} negative volume entries.")
        if neg_vol_count != 0:
            errors.append(f"Negative volume values found: {neg_vol_count}")
            neg_locs = neg_vol_mask.stack()
            neg_locs = neg_locs[neg_locs]
            print("Negative volume locations (first 10):")
            for idx in neg_locs.index[:10]:
                val = vol_df.loc[idx]
                print(f"  {idx}: {val}")
    else:
        errors.append("Column level 0 'Volume' not found!")
        
    # 4. The date index increases monotonically and has no duplicates
    is_monotonic = df.index.is_monotonic_increasing
    is_unique = df.index.is_unique
    print(f"Check 4 (Date index): Monotonic? {is_monotonic}, Unique? {is_unique}")
    if not is_monotonic:
        errors.append("Date index is not monotonically increasing!")
    if not is_unique:
        errors.append("Date index has duplicates!")
        dup_dates = df.index[df.index.duplicated()].unique()
        print("Duplicated dates:", dup_dates.tolist()[:10])
        
    # 5. Count the number of active assets on 2015-01-01 and ensure they have valid float prices
    target_date = '2015-01-01'
    if target_date in df.index:
        prices_on_date = df.loc[target_date, 'Adj Close']
        active_assets = prices_on_date[prices_on_date.notna()]
        active_count = len(active_assets)
        print(f"Check 5 (Active assets on 2015-01-01): Count = {active_count}")
        print("Active assets list:", active_assets.index.tolist())
        # Check if they have valid float prices (i.e. not inf, and are float type, and >= 0.0001)
        invalid_active = []
        for ticker, val in active_assets.items():
            if not isinstance(val, (float, np.float64, np.float32, int, np.integer)):
                invalid_active.append((ticker, val, "not a number type"))
            elif np.isnan(val) or np.isinf(val) or val < 0.0001:
                invalid_active.append((ticker, val, "invalid numeric value"))
        if len(invalid_active) > 0:
            errors.append(f"Active assets on 2015-01-01 have invalid prices: {invalid_active}")
        else:
            print("All active assets on 2015-01-01 have valid float prices.")
    else:
        errors.append(f"Date '{target_date}' not found in index!")

    # 6. Verify weekend day behavior (crypto vs non-crypto)
    # Crypto: BTC-USD, ETH-USD
    # Weekend days: Saturday (5) and Sunday (6)
    weekend_mask = df.index.dayofweek.isin([5, 6])
    weekend_df = df[weekend_mask]
    
    crypto_tickers = ['BTC-USD', 'ETH-USD']
    # Filter only tickers that are in the DataFrame columns
    df_tickers = df.columns.levels[1].tolist()
    crypto_tickers_present = [t for t in crypto_tickers if t in df_tickers]
    non_crypto_tickers_present = [t for t in df_tickers if t not in crypto_tickers]
    
    print(f"Weekend days check: Found {len(weekend_df)} weekend rows.")
    
    # Check crypto data on weekend
    print(f"Crypto tickers present: {crypto_tickers_present}")
    if crypto_tickers_present:
        for ticker in crypto_tickers_present:
            # check if prices change on weekend and volume is non-zero
            ticker_close = df.loc[:, ('Adj Close', ticker)]
            ticker_vol = df.loc[:, ('Volume', ticker)]
            
            # Let's count weekend dates where price is not NaN and volume is not NaN
            weekend_data = weekend_df.loc[:, [('Adj Close', ticker), ('Volume', ticker)]]
            nan_prices = weekend_data[('Adj Close', ticker)].isna().sum()
            nan_vols = weekend_data[('Volume', ticker)].isna().sum()
            zero_vols = (weekend_data[('Volume', ticker)] == 0).sum()
            
            print(f"  Ticker {ticker} on weekends: NaN Prices: {nan_prices}, NaN Vols: {nan_vols}, Zero Vols: {zero_vols} (out of {len(weekend_df)} weekend days)")
            
            # We want to make sure crypto assets HAVE data on weekend days, i.e., not all NaN, and not forward filled with 0 volume.
            # Let's check if the price actually changes on weekends
            # Let's compute differences
            ticker_diffs = ticker_close.diff()
            # Diff on weekend dates
            weekend_diffs = ticker_diffs[weekend_mask]
            # How many weekend diffs are non-zero?
            non_zero_diffs = (weekend_diffs != 0).sum()
            print(f"  Ticker {ticker} weekend price changes: {non_zero_diffs} non-zero diffs.")
            if non_zero_diffs == 0:
                warnings.append(f"Crypto asset {ticker} has 0 price changes on weekends. This suggests it might be forward-filled or has static data.")
    else:
        warnings.append("No crypto tickers (BTC-USD, ETH-USD) found in the columns!")
        
    # Check non-crypto data on weekend
    # AAPL, NVDA, etc. should be forward-filled from Friday.
    # Friday price == Saturday price == Sunday price.
    # Volume on Sat/Sun should be 0 or NaN/filled. Let's see what it is.
    print(f"Checking forward-filled non-crypto tickers on weekends...")
    non_crypto_ff_errors = 0
    non_crypto_vol_errors = 0
    
    # We will iterate through weekend dates and check if Saturday/Sunday match the Friday before.
    # To make this robust, we can check for all Saturday/Sunday index entries, find their previous Friday.
    for date in df.index:
        dow = date.dayofweek
        if dow in [5, 6]: # Sat, Sun
            # Previous Friday would be date - 1 day (for Sat) or date - 2 days (for Sun)
            offset = 1 if dow == 5 else 2
            friday_date = date - pd.Timedelta(days=offset)
            if friday_date in df.index:
                # Check if non-crypto asset prices are identical
                friday_prices = df.loc[friday_date, 'Adj Close']
                weekend_prices = df.loc[date, 'Adj Close']
                
                # Check for present non-crypto tickers
                diff_prices = (friday_prices[non_crypto_tickers_present] != weekend_prices[non_crypto_tickers_present]) & friday_prices[non_crypto_tickers_present].notna() & weekend_prices[non_crypto_tickers_present].notna()
                if diff_prices.any():
                    non_crypto_ff_errors += diff_prices.sum()
                    if non_crypto_ff_errors <= 10:
                        mismatches = diff_prices[diff_prices].index.tolist()
                        print(f"  Mismatch on {date.date()} compared to Friday {friday_date.date()} for: {mismatches}")
                        for m in mismatches:
                            print(f"    Friday: {friday_prices[m]}, Weekend: {weekend_prices[m]}")
                
                # Check volumes on Saturday/Sunday for non-crypto
                weekend_volumes = df.loc[date, 'Volume'][non_crypto_tickers_present]
                # Volume must be 0 or NaN (or filled as specified, let's see if they are non-zero)
                invalid_vols = (weekend_volumes != 0) & weekend_volumes.notna()
                if invalid_vols.any():
                    non_crypto_vol_errors += invalid_vols.sum()
                    if non_crypto_vol_errors <= 10:
                        bad_vols = invalid_vols[invalid_vols].index.tolist()
                        print(f"  Non-zero volume on {date.date()} for non-crypto: {bad_vols}")
                        for bv in bad_vols:
                            print(f"    Volume: {weekend_volumes[bv]}")

    print(f"Check 6 Result:")
    print(f"  Non-crypto price forward-fill mismatches on weekends: {non_crypto_ff_errors}")
    print(f"  Non-crypto non-zero/non-NaN volume entries on weekends: {non_crypto_vol_errors}")
    
    if non_crypto_ff_errors > 0:
        errors.append(f"Non-crypto asset prices are not correctly forward-filled on weekends! Mismatch count: {non_crypto_ff_errors}")
    if non_crypto_vol_errors > 0:
        errors.append(f"Non-crypto assets have non-zero volume on weekends! Count: {non_crypto_vol_errors}")

    print("\n--- Summary of Verification ---")
    if len(errors) == 0:
        print("VERIFICATION SUCCESS: All checks passed with 0 errors!")
    else:
        print(f"VERIFICATION FAILURE: Found {len(errors)} errors.")
        for err in errors:
            print(f"  - ERROR: {err}")
            
    if len(warnings) > 0:
        print(f"Warnings/Anomalies ({len(warnings)}):")
        for wrn in warnings:
            print(f"  - WARNING: {wrn}")

if __name__ == "__main__":
    run_verification()
