import os
import json
import datetime
import hashlib
import numpy as np
import pandas as pd
import yfinance as yf
from opus8_config import OUT_DIR, PARQUET_FILE, RATES_FILE, MANIFEST_FILE, CANONICAL_TICKER, TICKERS_TRADED, ANNUALIZER

def get_hash(df):
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

def download_and_freeze():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print("Downloading ^IRX (Cash Yield)...")
    raw_irx = yf.download(['^IRX'], start='1999-01-01', auto_adjust=False, progress=False)
    if isinstance(raw_irx.columns, pd.MultiIndex):
        irx_close = raw_irx['Close']['^IRX']
    else:
        irx_close = raw_irx['Close']
    
    # KILL-8 fix: BEY conversion
    d = irx_close / 100.0
    rf_annual = (365 * d) / (360 - d * 365) # Bond equivalent yield
    
    rf_daily = (1.0 + rf_annual) ** (1.0 / ANNUALIZER) - 1.0
    rf_annual_vals = rf_annual.dropna().values
    
    df_rates = pd.DataFrame({'rf_annual': rf_annual, 'rf_daily': rf_daily})
    df_rates.index = df_rates.index.normalize()
    
    print(f"Downloading {len(TICKERS_TRADED)} traded assets...")
    raw_df = yf.download(TICKERS_TRADED, start='1999-01-01', auto_adjust=False, progress=False)
    
    spy_idx = raw_df['Close'][CANONICAL_TICKER].dropna().index.normalize()
    
    # KILL-8 fix: rates reindexed and coverage asserted
    df_rates = df_rates.reindex(spy_idx)
    df_rates = df_rates.ffill(limit=5)
    assert df_rates['rf_annual'].notna().all(), "Rates do not cover the canonical calendar"
    df_rates.to_parquet(RATES_FILE)
    
    dfs = []
    manifest_stats = {}
    
    for ticker in TICKERS_TRADED:
        if isinstance(raw_df.columns, pd.MultiIndex):
            close = raw_df['Close'][ticker]
            adj_close = raw_df['Adj Close'][ticker]
            open_p = raw_df['Open'][ticker]
            high = raw_df['High'][ticker]
            low = raw_df['Low'][ticker]
            volume = raw_df['Volume'][ticker]
        else:
            close = raw_df['Close']
            adj_close = raw_df['Adj Close']
            open_p = raw_df['Open']
            high = raw_df['High']
            low = raw_df['Low']
            volume = raw_df['Volume']
            
        r = adj_close / close
        
        # SPEC-2: Assert ratio is monotonic non-decreasing and <= 1 + eps
        r_clean = r.dropna()
        if len(r_clean) > 0:
            assert r_clean.is_monotonic_increasing or np.all(np.diff(r_clean.values) >= -1e-4), f"{ticker} adjustment ratio is not monotonically non-decreasing"
            assert np.max(r_clean.values) <= 1.0 + 1e-4, f"{ticker} adjustment ratio exceeds 1.0"
        
        df_ticker = pd.DataFrame({
            'Open': open_p,
            'High': high,
            'Low': low,
            'Close': close,
            'Adj Close': adj_close,
            'Volume': volume
        })
        df_ticker.index = df_ticker.index.normalize()
        df_ticker = df_ticker[~df_ticker.index.duplicated(keep='last')]
        
        # Reindex to canonical calendar
        df_ticker = df_ticker.reindex(spy_idx)
        
        # KILL-1 and KILL-7 fix: Causal fill with is_filled/has_print
        has_print = df_ticker['Close'].notna()
        
        for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            df_ticker[col] = df_ticker[col].ffill(limit=3)
            
        is_filled = df_ticker['Close'].notna() & ~has_print
        
        df_ticker['has_print'] = has_print
        df_ticker['is_filled'] = is_filled
        df_ticker['Ticker'] = ticker
        
        n_bars = has_print.sum()
        first_dt = df_ticker['Close'].first_valid_index()
        last_dt = df_ticker['Close'].last_valid_index()
        
        manifest_stats[ticker] = {
            'n_bars': int(n_bars),
            'first': str(first_dt.date()) if pd.notnull(first_dt) else None,
            'last': str(last_dt.date()) if pd.notnull(last_dt) else None
        }
        dfs.append(df_ticker)
        
    final_df = pd.concat(dfs, keys=TICKERS_TRADED, names=['Ticker', 'Date'])
    final_df = final_df.sort_index(kind='stable')
    
    assert final_df.index.is_monotonic_increasing
    assert final_df.index.is_unique
    
    # Save parquet
    final_df.to_parquet(PARQUET_FILE)
    data_hash = get_hash(final_df)
    
    # We should add a dividends/splits download here to freeze them per SPEC-2
    divs_splits_hash = "TODO: freeze corporate actions"
    
    import pkg_resources
    try:
        pd_version = pkg_resources.get_distribution("pandas").version
        np_version = pkg_resources.get_distribution("numpy").version
        yf_version = pkg_resources.get_distribution("yfinance").version
    except Exception:
        pd_version = pd.__version__
        np_version = np.__version__
        yf_version = yf.__version__
    
    manifest = {
        'data_hash': data_hash,
        'divs_splits_hash': divs_splits_hash,
        'download_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'end_date': str(spy_idx.max().date()),
        'calendar': CANONICAL_TICKER,
        'annualizer': ANNUALIZER,
        'stats': manifest_stats,
        'versions': {
            'pandas': pd_version,
            'numpy': np_version,
            'yfinance': yf_version
        }
    }
    
    # Write to a temporary file, then atomic rename
    temp_manifest = MANIFEST_FILE + ".tmp"
    with open(temp_manifest, 'w') as f:
        json.dump(manifest, f, indent=2)
    os.replace(temp_manifest, MANIFEST_FILE)
        
    print(f"Saved to {PARQUET_FILE}")
    print(f"Data Hash: {data_hash}")

if __name__ == '__main__':
    download_and_freeze()
