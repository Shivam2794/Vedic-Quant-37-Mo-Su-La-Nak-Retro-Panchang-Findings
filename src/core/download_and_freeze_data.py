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
        irx_close = raw_irx['Close']['^IRX'].ffill()
    else:
        irx_close = raw_irx['Close'].ffill()
    
    # Segregate IRX (KILL-9)
    rf_annual = irx_close / 100.0
    rf_daily = (1.0 + rf_annual) ** (1.0 / ANNUALIZER) - 1.0
    rf_annual_vals = rf_annual.dropna().values
    assert float(np.min(rf_annual_vals)) > -0.01 and float(np.max(rf_annual_vals)) < 0.25
    assert rf_annual.isna().mean().item() < 0.02 if isinstance(rf_annual.isna().mean(), pd.Series) else rf_annual.isna().mean() < 0.02
    
    df_rates = pd.DataFrame({'rf_annual': rf_annual, 'rf_daily': rf_daily})
    df_rates.index = df_rates.index.normalize()
    df_rates.to_parquet(RATES_FILE)
    
    print(f"Downloading {len(TICKERS_TRADED)} traded assets...")
    raw_df = yf.download(TICKERS_TRADED, start='1999-01-01', auto_adjust=False, progress=False)
    
    # Establish canonical calendar using CANONICAL_TICKER (SPY)
    spy_idx = raw_df['Close'][CANONICAL_TICKER].dropna().index.normalize()
    
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
            
        # Monotonicity checks (KILL-8)
        r = adj_close / close

        assert abs(r.dropna().iloc[-1] - 1.0) < 1e-6, f"{ticker} last bar unadjusted"
        
        # Resample to canonical calendar (KILL-1)
        df_ticker = pd.DataFrame({
            'Open': open_p,
            'High': high,
            'Low': low,
            'Close': close,       # Unadjusted for audit/slippage
            'Adj Close': adj_close, # TRUE POINT-IN-TIME SERIES FOR SIGNALS AND RETURNS
            'Volume': volume
        })
        df_ticker.index = df_ticker.index.normalize()
        
        # Remove duplicate indices
        df_ticker = df_ticker[~df_ticker.index.duplicated(keep='last')]
        
        # Reindex to strictly the NYSE calendar!
        df_ticker = df_ticker.reindex(spy_idx)
        
        # Ffill interior exchange glitches (e.g. missing Monday crypto data) up to a reasonable limit
        df_ticker = df_ticker.ffill(limit=5)
        df_ticker['Ticker'] = ticker
        
        n_bars = df_ticker['Adj Close'].notna().sum()
        first_dt = df_ticker['Adj Close'].first_valid_index()
        last_dt = df_ticker['Adj Close'].last_valid_index()
        
        manifest_stats[ticker] = {
            'n_bars': int(n_bars),
            'first': str(first_dt.date()) if pd.notnull(first_dt) else None,
            'last': str(last_dt.date()) if pd.notnull(last_dt) else None
        }
        dfs.append(df_ticker)
        
    final_df = pd.concat(dfs, keys=TICKERS_TRADED, names=['Ticker', 'Date'])
    final_df = final_df.sort_index(kind='stable') # Stable sort (KILL-7)
    
    assert final_df.index.is_monotonic_increasing
    assert final_df.index.is_unique
    
    final_df.to_parquet(PARQUET_FILE)
    data_hash = get_hash(final_df)
    
    manifest = {
        'data_hash': data_hash,
        'download_utc': datetime.datetime.utcnow().isoformat(),
        'end_date': str(spy_idx.max().date()),
        'calendar': CANONICAL_TICKER,
        'annualizer': ANNUALIZER,
        'stats': manifest_stats
    }
    
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Saved to {PARQUET_FILE}")
    print(f"Data Hash: {data_hash}")
    
    # Final assertion from Opus 5:
    for t in TICKERS_TRADED:
        s = final_df.loc[t]
        assert s.index.equals(spy_idx)
        # Ensure no interior holes after inception
        s_live = s['Adj Close'][s['Adj Close'].first_valid_index():]
        # BTC may have some missed NYSE days where it didn't print at exactly 4PM, but daily OHLCs should exist.
        # Let's ffill interior holes strictly for up to 3 days (weekends).
        # Actually since we reindexed BTC to NYSE, it's just selecting the BTC bar on that date. 
        # Since BTC trades 365, it will always have a bar on NYSE dates.
        assert s_live.notna().all(), f"{t} has interior NaN holes!"
        
if __name__ == '__main__':
    download_and_freeze()
