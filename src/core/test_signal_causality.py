import os
import numpy as np
import pandas as pd
from opus8_signal_generator_v6 import generate_signals, PARQUET_FILE

def test_causality():
    print("=======================================")
    print("OPUS 5 CAUSALITY TEST: BITWISE ASSERTION")
    print("=======================================")
    
    df = pd.read_parquet(PARQUET_FILE)
    df_spy = df[df['Ticker'] == 'SPY'].copy()
    
    # 1. Generate signals on FULL history (the "future")
    full_signals = generate_signals(df_spy, is_causality_test=True)
    
    # 2. Pick a random truncation point (e.g. index 3000 out of 6938)
    trunc_idx = 3000
    df_trunc = df_spy.iloc[:trunc_idx].copy()
    
    # 3. Generate signals on TRUNCATED history (the "past")
    trunc_signals = generate_signals(df_trunc, is_causality_test=True)
    
    # 4. Bitwise comparison
    for fam in full_signals.keys():
        full_mat = full_signals[fam]
        trunc_mat = trunc_signals[fam]
        
        # Slicing the full matrix up to the truncation point
        sliced_full_mat = full_mat[:, :trunc_idx]
        
        is_equal = np.array_equal(sliced_full_mat, trunc_mat)
        
        if not is_equal:
            print(f"FATAL LEAK DETECTED in family: {fam}")
            # Find exact point of divergence
            for i in range(trunc_mat.shape[0]):
                if not np.array_equal(sliced_full_mat[i], trunc_mat[i]):
                    diff_idx = np.where(sliced_full_mat[i] != trunc_mat[i])[0]
                    print(f"  Param combo {i} diverged at indices: {diff_idx[:5]}...")
            assert False, "Causality test failed! Data leakage present."
        else:
            print(f"PASS: {fam} is bitwise identical and leak-free.")
            
    print("\nALL SIGNALS VERIFIED CAUSAL. NO DATA LEAKAGE.")

if __name__ == '__main__':
    test_causality()
