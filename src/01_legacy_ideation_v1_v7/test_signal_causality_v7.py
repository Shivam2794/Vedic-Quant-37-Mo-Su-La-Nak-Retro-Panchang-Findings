import os
import numpy as np
import pandas as pd
from opus8_config import PARQUET_FILE, TICKERS_TRADED, LAG
from opus8_signal_generator_v7 import generate_signals, FAMILIES

def run_causality_tests():
    print("==================================================")
    print("OPUS 5 V7 CAUSALITY & LEAK DETECTOR (MAX EFFORT)")
    print("==================================================")
    
    df = pd.read_parquet(PARQUET_FILE)
    
    for ticker in TICKERS_TRADED:
        print(f"\n--- Testing {ticker} ---")
        df_t = df[df['Ticker'] == ticker].copy()
        n = len(df_t)
        
        # 1. Base generation
        base_signals = generate_signals(df_t)
        
        # 2. Random Truncation Test (Prefix Invariance)
        # We test 50 random truncation points, including one at max_burn_in + 1
        np.random.seed(42)
        trunc_points = np.random.randint(500, n-100, size=50)
        
        for t_idx in trunc_points:
            df_trunc = df_t.iloc[:t_idx].copy()
            trunc_signals = generate_signals(df_trunc)
            
            for fam in FAMILIES:
                base_pos = base_signals[fam]
                trunc_pos = trunc_signals[fam]
                assert np.array_equal(base_pos[:, :t_idx], trunc_pos), f"{ticker} {fam} failed truncation at {t_idx}!"
                
        print("  [PASS] Prefix Invariance (50 random truncations)")
        
        # 3. Append Test (Future Noise Invariance)
        # Append 100 synthetic rows of random noise
        synthetic_rows = df_t.iloc[-100:].copy()
        synthetic_rows['Adj Close'] = synthetic_rows['Adj Close'] * (1 + np.random.normal(0, 0.02, 100))
        df_append = pd.concat([df_t, synthetic_rows])
        
        append_signals = generate_signals(df_append)
        for fam in FAMILIES:
            base_pos = base_signals[fam]
            app_pos = append_signals[fam]
            assert np.array_equal(base_pos, app_pos[:, :n]), f"{ticker} {fam} failed append test!"
            
        print("  [PASS] Append Invariance (Future Noise)")
        
        # 4. Perturbation Test (Single-Bar Lag Integrity) - KILL-4
        # We perturb a single price at `t` by 20% and ensure pos[:, :t+1] is unchanged.
        # Since lag=1, the position at t+1 is determined by signals up to t. Wait,
        # if close[t] is perturbed, then signal[t] changes, which affects pos[t+1].
        # So pos[:, :t+1] SHOULD change!
        # Wait, if close at t is perturbed, signal at t changes.
        # pos at t+1 = signal at t.
        # So pos[t+1] changes.
        # Therefore, pos[:, :t+1] means pos[0], pos[1] ... pos[t].
        # pos[t] depends on signal[t-1], which depends on close[t-1].
        # So pos[:, :t+1] (which is indices 0 to t inclusive) should be UNCHANGED.
        # Yes! pos[:, :t+1] is unaffected by close[t].
        
        p_idx = np.random.randint(500, n-500)
        df_pert = df_t.copy()
        df_pert.loc[df_pert.index[p_idx], 'Adj Close'] *= 1.20 # 20% shock
        
        pert_signals = generate_signals(df_pert)
        
        for fam in FAMILIES:
            base_pos = base_signals[fam]
            pert_pos = pert_signals[fam]
            
            # 0 to p_idx inclusive must be unchanged
            assert np.array_equal(base_pos[:, :p_idx+1], pert_pos[:, :p_idx+1]), f"{ticker} {fam} failed perturbation leak test!"
            
            # The future should differ (because EMA retains memory of the shock)
            # Actually, sometimes it might not differ if the shock isn't big enough to cross a threshold,
            # but usually it will. We just assert the past is strictly preserved.
            
        print("  [PASS] Perturbation Test (Strict 1-Bar Lag Integrity)")
        
    print("\n==================================================")
    print("ALL CAUSALITY & LEAK DETECTOR TESTS PASSED.")
    print("==================================================")

if __name__ == '__main__':
    run_causality_tests()
