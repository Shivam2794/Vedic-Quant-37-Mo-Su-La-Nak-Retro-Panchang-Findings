You are the Master Brain, operating at maximum effort under the 'Absolute Surrender & Relentless Grinder' mandate: we do not stop until we have an error-free, bug-free, logic-gap-free cycle.

TASK: perform a Brutal Multipoint Inspection (Deliverable 1 final review) of the V9 architecture below. V8 failed on 4 Blockers plus several Majors; V9 claims to fix them via a strictly causal data freezer and signal generator.

MANDATORY REGRESSION AUDIT — these five bugs were FATAL in earlier versions of
this strategy. For EACH one, quote the exact line(s) that prove it is fixed, or
declare it a BLOCKER:

 B1. PHANTOM ASSETS: any use of .fillna(0) / .fillna(method=...) / reindex+fill
     on a PRICE or RETURN matrix that can fabricate data before an asset's true
     inception. Prices must be forward-filled ONLY inside [first_valid_index,
     last_valid_index]; anything outside must stay NaN and the asset must be
     excluded from that date's investable universe (weights renormalised).
 B2. SHARPE FORMULA: Sharpe must be the annualised mean of PERIODIC EXCESS
     returns divided by the standard deviation of those same periodic excess
     returns, i.e. mean(r_p - r_f) / std(r_p - r_f) * sqrt(P), with P the
     periods per year and std computed with a stated ddof. CAGR/vol is WRONG
     and must be flagged. Sortino must use downside deviation of excess returns
     about a stated MAR. CAGR must be geometric: (V_T/V_0)^(365.25/days) - 1.
 B3. FRICTIONS: per-rebalance turnover must be costed as
     cost_t = 0.5 * sum(|w_t - w_{t-1}^{drifted}|) * (commission + spread/2 +
     slippage), applied to the portfolio return in the SAME period as the
     trade. Any leverage above 1.0 must be charged (broker_rate = benchmark
     short-rate + spread) on the borrowed notional, accrued daily on an
     ACT/360 or ACT/365 basis (state which).
 B4. ABSOLUTE MOMENTUM ON DEFENSIVES: the risk-off / defensive sleeve must
     itself pass an absolute-momentum (trend) filter versus cash/T-bills. If
     the chosen defensive asset's own excess momentum is negative it must be
     routed to cash, not blindly bought.
 B5. INCEPTION ALIGNMENT: the backtest start date must be
     max(first_valid_index over all REQUIRED assets) plus the longest lookback
     window, so no signal is ever computed from a partially populated window.
     Optional/expansion assets must enter the universe only after their own
     inception + lookback. Report the binding asset and the effective start.

ALSO CHECK, RUTHLESSLY:
 * Look-ahead: signals computed at close of t may only trade at t+1 (or later);
   verify every .shift(), and that no .shift(-k), centred rolling window,
   or full-sample statistic (mean/std/z-score/rank over the entire series)
   leaks the future.
 * Survivorship & delisting: is the ticker list frozen as-of the start date?
 * Total vs price return: dividends handled consistently; no mixing of
   adjusted and unadjusted series.
 * Timezone / calendar joins: inner-join on a single trading calendar, no
   silent reindex that invents rows; resample rules ('M' vs 'ME', 'BM')
   verified for the pandas version in use.
 * Rebalance mechanics: drifted weights vs target weights, cash accounting,
   fractional shares, integer-share rounding residuals.
 * Divide-by-zero / NaN propagation in volatility, ERC and inverse-vol
   weighting; degenerate covariance matrices; sum(weights) == 1 assertions.
 * Determinism: fixed random seeds, no dependence on dict ordering, no
   network calls inside the backtest loop, frozen data hashes.
 * Metrics: max drawdown on the compounded equity curve, Calmar, Ulcer,
   turnover, exposure, and per-year returns all recomputed independently.


NOTE — the following artefacts could NOT be read and are absent from this review package. Treat any gate that depends on them as UNVERIFIED (not passed):
  - V9 Action Plan (16 Acceptance Gates) -> v9_action_plan.md


---
## ARTEFACTS UNDER REVIEW

### V9 Action Plan (16 Acceptance Gates)
```markdown
<<< FILE NOT FOUND: v9_action_plan.md >>>
```

### Data Freezer (download_and_freeze_data_v3.py)
```python
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

```

### Signal Generator (opus9_signal_generator_v9.py)
```python
import os
import json
import numpy as np
import pandas as pd
import warnings
import numba
from opus8_config import IN_DIR, PARQUET_FILE, MANIFEST_FILE, TICKERS_TRADED, LAG

warnings.filterwarnings('ignore')

FAMILIES = ['MACD', 'SMA200']

@numba.njit(cache=True)
def calc_ema_with_mask(arr, has_print, span):
    n = arr.shape[0]
    out = np.full(n, np.nan)
    alpha = 2.0 / (span + 1.0)
    
    i0 = -1
    for i in range(n):
        if has_print[i]:
            i0 = i
            break
            
    if i0 < 0:
        return out, np.zeros(n, dtype=np.int32)
        
    out[i0] = arr[i0]
    bars_since_reset = np.zeros(n, dtype=np.int32)
    bars_since_reset[i0] = 1
    
    consecutive_missing = 0
    
    for i in range(i0 + 1, n):
        if not has_print[i]:
            consecutive_missing += 1
            # We still compute EMA on filled bars if they exist (carry state)
            if not np.isnan(arr[i]):
                out[i] = arr[i] * alpha + out[i-1] * (1.0 - alpha)
                bars_since_reset[i] = bars_since_reset[i-1] + 1
            else:
                out[i] = np.nan
                bars_since_reset[i] = bars_since_reset[i-1]
        else:
            if consecutive_missing > 3 or np.isnan(out[i-1]):
                # Reset EMA to spot if gap > 3 or previous was NaN
                out[i] = arr[i]
                bars_since_reset[i] = 1
            else:
                out[i] = arr[i] * alpha + out[i-1] * (1.0 - alpha)
                bars_since_reset[i] = bars_since_reset[i-1] + 1
            consecutive_missing = 0
            
    return out, bars_since_reset

@numba.njit(cache=True)
def calc_macd_signal_with_mask(close, has_print, fast, slow, signal):
    ema_fast, reset_fast = calc_ema_with_mask(close, has_print, fast)
    ema_slow, reset_slow = calc_ema_with_mask(close, has_print, slow)
    macd = ema_fast - ema_slow
    
    # We pass a dummy has_print to signal_line EMA because macd doesn't have "prints", it's continuous except at resets
    dummy_has_print = np.ones_like(has_print, dtype=np.bool_)
    for i in range(len(has_print)):
        if np.isnan(macd[i]):
            dummy_has_print[i] = False
            
    signal_line, reset_sig = calc_ema_with_mask(macd, dummy_has_print, signal)
    
    n = close.shape[0]
    sig = np.zeros(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.int8)
    
    burn_in = 5 * slow + 5 * signal
    
    for i in range(n):
        # We need ALL EMA lines to have sufficient burn-in from their last reset
        if reset_slow[i] >= burn_in and reset_fast[i] >= burn_in and reset_sig[i] >= burn_in:
            if not np.isnan(macd[i]) and not np.isnan(signal_line[i]) and not np.isnan(close[i]):
                sig[i] = 1 if macd[i] > signal_line[i] else 0
                valid[i] = 1
                
    return sig, valid

@numba.njit(cache=True)
def calc_sma_with_mask(arr, has_print, window):
    n = arr.shape[0]
    out = np.full(n, np.nan)
    valid_mask = np.zeros(n, dtype=np.int8)
    
    i0 = -1
    for i in range(n):
        if has_print[i]:
            i0 = i
            break
            
    if i0 < 0:
        return out, valid_mask
        
    for i in range(i0 + window - 1, n):
        if np.isnan(arr[i]):
            out[i] = np.nan
            continue
            
        s = 0.0
        missing = False
        for j in range(i - window + 1, i + 1):
            if np.isnan(arr[j]):
                missing = True
                break
            s += arr[j]
        if not missing:
            out[i] = s / window
            valid_mask[i] = 1
    return out, valid_mask

@numba.njit(cache=True)
def calc_sma200_signal_with_mask(close, has_print, window):
    sma, sma_valid = calc_sma_with_mask(close, has_print, window)
    n = close.shape[0]
    sig = np.zeros(n, dtype=np.int8)
    valid = np.zeros(n, dtype=np.int8)
    
    for i in range(n):
        if sma_valid[i] == 1 and not np.isnan(close[i]):
            sig[i] = 1 if close[i] > sma[i] else 0
            valid[i] = 1
                
    return sig, valid

def to_positions(sig, valid, tradeable, lag=LAG):
    assert lag >= 0, "Lag must be >= 0"
    pos = np.zeros_like(sig)
    pos_valid = np.zeros_like(valid)
    
    if lag == 0:
        pos = sig.copy()
        pos_valid = valid.copy() & tradeable
        for row in range(sig.shape[0]):
            pos[row, :] = np.where(pos_valid[row, :], pos[row, :], 0)
        return pos, pos_valid
    
    for row in range(sig.shape[0]):
        pos[row, lag:] = sig[row, :-lag]
        
        # tradeability mask
        t_mask = tradeable[lag:] & tradeable[lag-1:-1]
        s_val = valid[row, :-lag]
        
        pos_valid[row, lag:] = s_val & t_mask
        pos[row, lag:] = np.where(pos_valid[row, lag:], pos[row, lag:], 0)
        
    return pos, pos_valid

def generate_signals(df_ticker, lag=LAG, is_causality_test=False, negative_control=False):
    close = df_ticker['Adj Close'].values 
    has_print = df_ticker['has_print'].values
    tradeable = df_ticker['has_print'].values # tradeable implies has_print
    
    n = len(close)
    
    macd_params = [(12, 26, 9), (8, 21, 5), (5, 34, 7), (3, 10, 16), (24, 52, 18), (12, 50, 9), (10, 40, 15), (5, 15, 5), (15, 35, 10)]
    macd_sig = np.zeros((9, n), dtype=np.int8)
    macd_val = np.zeros((9, n), dtype=np.int8)
    
    for i, p in enumerate(macd_params):
        macd_sig[i, :], macd_val[i, :] = calc_macd_signal_with_mask(close, has_print, p[0], p[1], p[2])
        
    sma_params = [200, 150, 250, 100, 300, 180, 220, 240, 260]
    sma_sig = np.zeros((9, n), dtype=np.int8)
    sma_val = np.zeros((9, n), dtype=np.int8)
    
    for i, p in enumerate(sma_params):
        sma_sig[i, :], sma_val[i, :] = calc_sma200_signal_with_mask(close, has_print, p)
        
    if negative_control:
        # DO NOT SHIP
        return {
            'MACD_UNLAGGED_DO_NOT_SHIP': macd_sig,
            'MACD_valid_UNLAGGED_DO_NOT_SHIP': macd_val,
            'SMA200_UNLAGGED_DO_NOT_SHIP': sma_sig,
            'SMA200_valid_UNLAGGED_DO_NOT_SHIP': sma_val,
        }
        
    macd_pos, macd_pos_val = to_positions(macd_sig, macd_val, tradeable, lag)
    sma_pos, sma_pos_val = to_positions(sma_sig, sma_val, tradeable, lag)
    
    return {
        'MACD': macd_pos,
        'MACD_valid': macd_pos_val,
        'SMA200': sma_pos,
        'SMA200_valid': sma_pos_val,
        'MACD_params': np.array(macd_params),
        'SMA200_params': np.array(sma_params)
    }

def process_all_tickers():
    df = pd.read_parquet(PARQUET_FILE)
    
    with open(MANIFEST_FILE, 'r') as f:
        manifest = json.load(f)
        
    data_hash = manifest['data_hash']
    
    temp_dir = os.path.join(IN_DIR, 'tmp_v9')
    os.makedirs(temp_dir, exist_ok=True)
    
    for ticker in TICKERS_TRADED:
        df_t = df[df['Ticker'] == ticker]
        
        # Check monotonicity and uniqueness
        assert df_t.index.is_monotonic_increasing
        assert df_t.index.is_unique
        
        dates = df_t.index.get_level_values('Date').astype(np.int64).values
        
        signals = generate_signals(df_t, lag=LAG)
        
        # Oracle checks: Ensure we're not producing NaN returns on valid positions
        adj = df_t['Adj Close'].values
        ret = np.zeros_like(adj)
        ret[1:] = adj[1:] / adj[:-1] - 1.0
        
        for fam in FAMILIES:
            mat = signals[fam]
            valid = signals[f'{fam}_valid']
            
            assert mat.ndim == 2 and mat.size > 0
            assert mat.shape[1] == len(dates)
            assert mat.dtype == np.int8
            assert mat.flags['C_CONTIGUOUS']
            assert ((mat == 0) | (mat == 1)).all()
            
            # Occupancy computed only over valid entries
            for row in range(mat.shape[0]):
                valid_mask = (valid[row] == 1)
                valid_count = valid_mask.sum()
                if valid_count > 0:
                    occ = mat[row, valid_mask].mean()
                    assert 0.001 < occ < 0.999, f"{ticker} {fam} param {row} occupancy: {occ}"
                    
                    # Compute flips only on valid bars
                    valid_idx = np.where(valid_mask)[0]
                    if len(valid_idx) > 1:
                        flips = np.abs(np.diff(mat[row, valid_idx])).sum()
                        assert flips >= 5, f"{ticker} {fam} row {row} flips: {flips}"
                        
                # Ensure no NaN returns when valid
                invalid_returns = np.isnan(ret[valid_mask])
                assert not invalid_returns.any(), f"{ticker} {fam} row {row} has valid=1 but return is NaN!"
                
            assert ((mat == 1) & (valid == 0)).sum() == 0, f"{ticker} {fam} invested while invalid!"
            
            # Artifact self-description
            # Note: We can't strictly assert equality with raw unlagged signal anymore because `pos` is zeroed out when `pos_valid` is 0.
            
        npz_data = {
            'dates': dates,
            'data_hash': data_hash,
            'lag': LAG,
            **signals
        }
        
        np.savez_compressed(os.path.join(temp_dir, f'{ticker}_signals_v9.npz'), **npz_data)
        print(f"Generated V9 signals for {ticker}")
        
    # Atomic rename
    for ticker in TICKERS_TRADED:
        os.replace(os.path.join(temp_dir, f'{ticker}_signals_v9.npz'), os.path.join(IN_DIR, f'{ticker}_signals_v9.npz'))
    os.rmdir(temp_dir)
    print("All V9 artifacts atomically sealed.")

if __name__ == '__main__':
    process_all_tickers()

```

### Data Causality Test (test_data_causality_v9.py)
```python
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

```

### Signal Causality Test (test_signal_causality_v9.py)
```python
import os
import numpy as np
import pandas as pd
from opus8_config import PARQUET_FILE, CANONICAL_TICKER, TICKERS_TRADED
from opus9_signal_generator_v9 import generate_signals, calc_ema_with_mask, calc_sma_with_mask, FAMILIES, to_positions

def test_oracle_correctness():
    # Test EMA against pandas ewm
    print("Running oracle correctness tests...")
    n = 1000
    np.random.seed(42)
    close = np.random.lognormal(0, 0.01, n).cumprod()
    
    # inject nans
    close[100:105] = np.nan
    close[500:520] = np.nan # large gap
    
    has_print = ~np.isnan(close)
    df = pd.Series(close)
    
    # Test SMA
    sma_numba, sma_valid = calc_sma_with_mask(close, has_print, 200)
    sma_pandas = df.rolling(200).mean().values
    
    # We must match exactly on bars where SMA is valid
    valid_idx = np.where(sma_valid == 1)[0]
    assert len(valid_idx) > 0
    np.testing.assert_allclose(sma_numba[valid_idx], sma_pandas[valid_idx], rtol=1e-5)
    
    # Test EMA
    ema_numba, resets = calc_ema_with_mask(close, has_print, 12)
    
    # We test pandas ewm on a continuous segment after a reset to verify alpha scaling
    segment = df.iloc[520:]
    ema_pandas = segment.ewm(span=12, adjust=False).mean().values
    
    np.testing.assert_allclose(ema_numba[520:], ema_pandas, rtol=1e-5)
    print("✅ Oracle correctness PASS")

def test_causality():
    df = pd.read_parquet(PARQUET_FILE)
    
    for ticker in TICKERS_TRADED:
        print(f"Testing causality for {ticker}...")
        df_t = df[df['Ticker'] == ticker]
        close = df_t['Adj Close'].values
        
        # 1. Determinism
        base = generate_signals(df_t)
        base2 = generate_signals(df_t)
        for k in base.keys():
            np.testing.assert_array_equal(base[k], base2[k])
            
        # 2. Scale Invariance (SPEC-2 concession condition)
        scale_factor = np.random.uniform(0.5, 2.0)
        df_scaled = df_t.copy()
        df_scaled['Adj Close'] = df_scaled['Adj Close'] * scale_factor
        df_scaled['Close'] = df_scaled['Close'] * scale_factor
        scaled = generate_signals(df_scaled)
        
        for k in base.keys():
            if 'params' not in k:
                np.testing.assert_array_equal(base[k], scaled[k], err_msg=f"{k} failed scale invariance")
                
        # 3. Negative & Positive Control (Perturbation Sweep)
        # We mutate `to_positions` behavior for the negative control to verify test catches leaks.
        # But here we are writing the test.
        # Let's sweep >= 200 indices per ticker.
        valid_indices = np.where(base['SMA200_valid'][0] == 1)[0]
        
        if len(valid_indices) == 0:
            continue
            
        # Pick 200 indices: first, last, gap-adjacent, and random
        has_print = df_t['has_print'].values
        gap_adjacent = np.where(np.diff(has_print.astype(int)) != 0)[0]
        
        sweep_idx = list(gap_adjacent) + [valid_indices[0], valid_indices[-1]] + list(np.random.choice(valid_indices, size=150, replace=False))
        sweep_idx = np.unique(sweep_idx)
        
        for p_idx in sweep_idx:
            # We shock the input at p_idx
            df_pert = df_t.copy()
            df_pert['Adj Close'].iloc[p_idx] *= 10.0 # Huge up shock
            df_pert['Close'].iloc[p_idx] *= 10.0
            
            pert = generate_signals(df_pert)
            
            for fam in FAMILIES:
                b = base[fam]
                p = pert[fam]
                
                # PREFIX INVARIANCE: Everything up to p_idx must be identical
                np.testing.assert_array_equal(b[:, :p_idx+1], p[:, :p_idx+1], err_msg=f"{fam} prefix leaked at {p_idx}")
                
                # POSITIVE CONTROL: The shock MUST propagate forward at p_idx+1
                # Because the shock is huge, we assert that AT LEAST ONE parameter row changes.
                if p_idx + 1 < b.shape[1]:
                    assert not np.array_equal(b[:, p_idx+1:], p[:, p_idx+1:]), f"{fam} positive control failed at {p_idx}"
                    
        # 4. Mock negative control (to prove test detects lag bugs)
        # We simulate a leaky generator that uses lag=0
        leaky_signals = generate_signals(df_t, lag=0) # NO LAG!
        
        caught_leak = False
        try:
            p_idx = valid_indices[-100]
            df_pert = df_t.copy()
            df_pert['Adj Close'].iloc[p_idx] *= 10.0
            pert_leaky = generate_signals(df_pert, lag=0)
            
            for fam in FAMILIES:
                b = leaky_signals[fam]
                p = pert_leaky[fam]
                # This should FAIL because at p_idx, lag=0 uses Close[p_idx]
                np.testing.assert_array_equal(b[:, :p_idx+1], p[:, :p_idx+1])
        except AssertionError:
            caught_leak = True
            
        assert caught_leak, "Test suite failed to catch deliberate same-bar leakage!"
        
    print("✅ All causality and invariance controls PASS")
    
if __name__ == '__main__':
    test_oracle_correctness()
    test_causality()

```


---
## REQUIRED OUTPUT FORMAT
1. VERDICT: one of CLEARANCE GRANTED / CLEARANCE DENIED.
2. ACCEPTANCE GATE TABLE: every gate in the action plan -> PASS / FAIL / UNVERIFIED, with the file:line evidence.
3. REGRESSION AUDIT TABLE: B1..B5 -> FIXED / BROKEN / UNVERIFIED with quoted evidence.
4. FINDINGS ordered BLOCKER -> MAJOR -> MINOR -> NIT. For each: file, line, why it is wrong, the mathematically correct statement, and a minimal unified-diff patch.
5. MISSING TESTS: the exact pytest cases that would have caught each BLOCKER.
6. Final answer to: do I have CLEARANCE to proceed to Deliverable 2 (Gridsearch & ERC Optimizer)? If not, list the minimum set of fixes.
Be adversarial. Assume every number is wrong until proven otherwise. Do not praise. Do not summarise the code back to me.
