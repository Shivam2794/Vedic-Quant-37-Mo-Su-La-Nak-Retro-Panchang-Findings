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
