import os
import numpy as np
import pandas as pd
from opus8_config import PARQUET_FILE, TICKERS_TRADED, LAG
from opus8_signal_generator_v8 import generate_signals, FAMILIES

def run_causality_tests():
    print("==================================================")
    print("OPUS 5 V8 CAUSALITY & LEAK DETECTOR (WITH NEGATIVE CONTROL)")
    print("==================================================")
    
    df = pd.read_parquet(PARQUET_FILE)
    
    for ticker in TICKERS_TRADED:
        print(f"\n--- Testing {ticker} ---")
        df_t = df[df['Ticker'] == ticker].copy()
        n = len(df_t)
        
        # 1. Base generation
        base_signals = generate_signals(df_t, is_causality_test=True, negative_control=False)
        
        # 2. Random Truncation Test (Prefix Invariance)
        np.random.seed(42)
        trunc_points = np.random.randint(500, n-100, size=50)
        for t_idx in trunc_points:
            df_trunc = df_t.iloc[:t_idx].copy()
            trunc_signals = generate_signals(df_trunc, is_causality_test=True, negative_control=False)
            
            for fam in FAMILIES:
                base_pos = base_signals[fam]
                trunc_pos = trunc_signals[fam]
                assert np.array_equal(base_pos[:, :t_idx], trunc_pos), f"{ticker} {fam} failed truncation at {t_idx}!"
                
        print("  [PASS] Prefix Invariance (50 random truncations)")
        
        # 3. Append Test (Future Noise Invariance)
        synthetic_rows = df_t.iloc[-100:].copy()
        synthetic_rows['Adj Close'] = synthetic_rows['Adj Close'] * (1 + np.random.normal(0, 0.02, 100))
        df_append = pd.concat([df_t, synthetic_rows])
        
        append_signals = generate_signals(df_append, is_causality_test=True, negative_control=False)
        for fam in FAMILIES:
            base_pos = base_signals[fam]
            app_pos = append_signals[fam]
            assert np.array_equal(base_pos, app_pos[:, :n]), f"{ticker} {fam} failed append test!"
            
        print("  [PASS] Append Invariance (Future Noise)")
        
        # 4. Perturbation Test (Strict 1-Bar Lag Integrity)
        valid_indices = np.where(base_signals['SMA200_valid'][0] == 1)[0]
        if len(valid_indices) < 500:
            print(f"  [SKIP] Not enough valid bars for perturbation test.")
            continue
            
        p_idx = np.random.choice(valid_indices[250:-250])
        df_pert = df_t.copy()
        df_pert.loc[df_pert.index[p_idx], 'Adj Close'] *= 1.20 # 20% shock
        pert_signals = generate_signals(df_pert, is_causality_test=True, negative_control=False)
        
        for fam in FAMILIES:
            base_pos = base_signals[fam]
            pert_pos = pert_signals[fam]
            assert np.array_equal(base_pos[:, :p_idx+1], pert_pos[:, :p_idx+1]), f"{ticker} {fam} failed perturbation leak test!"
            
        print("  [PASS] Perturbation Test (Strict 1-Bar Lag Integrity)")
        
        # 5. NEGATIVE CONTROL TEST (V8 KILL-5 Fix)
        # We run the negative control logic which outputs unlagged signals.
        # The perturbation test MUST fail on an unlagged signal!
        neg_signals = generate_signals(df_t, is_causality_test=True, negative_control=True)
        
        df_pert_up = df_t.copy()
        df_pert_up.loc[df_pert_up.index[p_idx], 'Adj Close'] *= 10.0 # 1000% shock up
        neg_pert_up = generate_signals(df_pert_up, is_causality_test=True, negative_control=True)
        
        df_pert_down = df_t.copy()
        df_pert_down.loc[df_pert_down.index[p_idx], 'Adj Close'] *= 0.1 # 90% shock down
        neg_pert_down = generate_signals(df_pert_down, is_causality_test=True, negative_control=True)
        
        caught_leak = False
        for fam in FAMILIES:
            neg_pos = neg_signals[fam]
            if not np.array_equal(neg_pos[:, :p_idx+1], neg_pert_up[fam][:, :p_idx+1]) or \
               not np.array_equal(neg_pos[:, :p_idx+1], neg_pert_down[fam][:, :p_idx+1]):
                caught_leak = True
                break
                
        assert caught_leak, f"{ticker} FAILED NEGATIVE CONTROL! Causality tester could not detect deliberate same-bar leakage!"
        print("  [PASS] Negative Control Test (Tester successfully detected deliberate same-bar leak)")

    print("\n==================================================")
    print("ALL CAUSALITY & LEAK DETECTOR TESTS PASSED.")
    print("==================================================")

if __name__ == '__main__':
    run_causality_tests()
