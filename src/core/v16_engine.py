import yfinance as yf
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge
from master_trading_plan_v7 import load_celestial_matrix_v7, V5ContinuousVedicEngine

os.makedirs('v16_engine', exist_ok=True)

def simulate_wfa_step(dr, base_bull, alpha_score_z, vol_60, start_idx, end_idx, vt, ml, ath, equity_exp_start):
    """Simulates a single out-of-sample window using fixed parameters."""
    N = end_idx - start_idx
    equity = np.ones(N)
    equity_exp = equity_exp_start
    
    vol_target_alloc = (vt / vol_60).clip(0, ml).shift(1).fillna(0.0)
    
    for k, i in enumerate(range(start_idx, end_idx)):
        if base_bull.iloc[i]:
            target_exp = vol_target_alloc.iloc[i]
        else:
            target_exp = 0.0
            
        z = alpha_score_z.iloc[i]
        if z > ath:
            target_exp = ml
        elif z < -ath:
            target_exp = 0.0
            
        current_exp = target_exp if k == 0 else equity_exp
        
        borrowed = max(0.0, target_exp - 1.0)
        cash_bal = max(0.0, 1.0 - target_exp)
        margin_drag = borrowed * (0.05 / 252)
        cash_yield = cash_bal * (0.04 / 252)
        
        turnover = abs(target_exp - current_exp)
        slippage = turnover * 0.0010
        
        net_ret = (target_exp * dr.iloc[i]) - margin_drag + cash_yield - slippage
        
        equity[k] = equity[k-1] * (1 + net_ret) if k > 0 else (1 + net_ret)
        equity_exp = (target_exp * (1 + dr.iloc[i])) / (1 + net_ret)
        
    return equity, equity_exp

def run_v16_wfa_optimizer():
    print("Fetching data...")
    data = yf.download(['QQQ', 'SPY'], start='1999-03-10', end='2026-01-01', auto_adjust=False, progress=False)
    qqq = data['Close']['QQQ'].ffill().dropna()
    spy = data['Close']['SPY'].ffill().dropna()
    spy_dates_df = pd.DataFrame({'date': spy.index})
    engine = V5ContinuousVedicEngine(spy_dates_df)
    tensors = engine.compute_all_tensors()
    
    tensors.index = pd.to_datetime(tensors['date'])
    qqq.index = pd.to_datetime(qqq.index).tz_localize(None)
    spy.index = pd.to_datetime(spy.index).tz_localize(None)
    
    common = tensors.index.intersection(qqq.index)
    qqq = qqq.loc[common]
    spy = spy.loc[common]
    t = tensors.loc[common]
    
    dr = qqq.pct_change().fillna(0)
    vol_60 = dr.rolling(60).std() * np.sqrt(252)
    vol_60 = vol_60.replace(0, np.nan).ffill().fillna(0.15)  # H6 FIX: ffill, not bfill (no lookahead)
    fast = qqq.rolling(50).mean()
    slow = qqq.rolling(250).mean()
    base_bull = (fast > slow).shift(1).fillna(False)
    
    # Features: dynamically use all F* features, but select top 12 per WFA split
    all_feature_cols = [c for c in t.columns if c != 'date' and (c.startswith('F') or c.startswith('asp_') or c.startswith('v_') or c.startswith('a_') or 'dist' in c)]
    if not all_feature_cols:
        all_feature_cols = [c for c in t.columns if c != 'date']
        
    X = t[all_feature_cols].shift(1).fillna(0)
    Y = dr
    
    tscv = TimeSeriesSplit(n_splits=10, test_size=252*2)
    alpha_score = pd.Series(0.0, index=common)
    
    from sklearn.feature_selection import SelectKBest, mutual_info_regression
    
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        Y_train = Y.iloc[train_index]
        embargo = 20
        if len(X_train) > embargo:
            X_train = X_train.iloc[:-embargo]
            Y_train = Y_train.iloc[:-embargo]
            
        # Dynamically select top 12 features using mutual information on training data ONLY
        selector = SelectKBest(score_func=mutual_info_regression, k=min(12, len(all_feature_cols)))
        X_train_sel = selector.fit_transform(X_train, Y_train)
        X_test_sel = selector.transform(X_test)
            
        model = Ridge(alpha=100.0)
        model.fit(X_train_sel, Y_train)
        alpha_score.iloc[test_index] = model.predict(X_test_sel)
        
    alpha_score_z = (alpha_score - alpha_score.rolling(252).mean()) / alpha_score.rolling(252).std()
    alpha_score_z = alpha_score_z.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # 2. Walk Forward Parameter Optimization
    vol_targets = [0.10, 0.12, 0.14, 0.16]
    max_leverages = [1.5, 2.0, 2.5]
    alpha_thresholds = [1.0, 1.25, 1.5]
    
    start_idx = np.where(qqq.index >= '2005-01-01')[0][0]
    out_of_sample_equity = []
    equity_exp_carry = 0.0
    
    print("\nStarting Autonomous WFA Grid Search (Rolling OOS)...")
    
    # Create 5 chunks of ~4 years each
    chunk_size = (len(qqq) - start_idx) // 5
    
    for chunk in range(5):
        c_start = start_idx + chunk * chunk_size
        c_end = start_idx + (chunk + 1) * chunk_size if chunk < 4 else len(qqq)
        
        # Train (Find best params using data BEFORE c_start)
        # We simulate the parameter grid from start_idx up to c_start
        train_start = start_idx
        train_end = c_start
        
        if train_end - train_start < 252:
            # If not enough history, use a default conservative parameter
            best_params = (0.12, 2.0, 1.5)
        else:
            best_cagr = -999
            best_params = (0.12, 2.0, 1.5)
            
            for vt in vol_targets:
                for ml in max_leverages:
                    for ath in alpha_thresholds:
                        eq, _ = simulate_wfa_step(dr, base_bull, alpha_score_z, vol_60, train_start, train_end, vt, ml, ath, 0.0)
                        
                        years = (train_end - train_start) / 252
                        cagr = (eq[-1] ** (1 / years)) - 1
                        
                        strat_eq_series = np.concatenate(([1.0], eq))
                        dd = (strat_eq_series - np.maximum.accumulate(strat_eq_series)) / np.maximum.accumulate(strat_eq_series)
                        max_dd = np.min(dd)
                        
                        if max_dd > -0.30 and cagr > best_cagr:
                            best_cagr = cagr
                            best_params = (vt, ml, ath)
        
        print(f"OOS Window {chunk+1}: Selected Params -> {best_params}")
        # Run OOS step
        oos_eq, equity_exp_carry = simulate_wfa_step(
            dr, base_bull, alpha_score_z, vol_60, 
            c_start, c_end, 
            best_params[0], best_params[1], best_params[2], 
            equity_exp_carry
        )
        
        # Convert cumulative equity in this chunk to daily returns so we can compound it continuously
        chunk_ret = np.diff(oos_eq, prepend=1.0) / np.concatenate(([1.0], oos_eq[:-1]))
        out_of_sample_equity.extend(chunk_ret.tolist())

    # Compile OOS Results
    equity = np.array(out_of_sample_equity)
    
    # Compound properly
    compiled_eq = np.cumprod(1.0 + equity)
    
    final_eq = compiled_eq[-1]
    years = (qqq.index[-1] - qqq.index[start_idx-1]).days / 365.25
    cagr = (final_eq ** (1 / years)) - 1
    
    qqq_cagr = (qqq.iloc[-1] / qqq.iloc[start_idx-1]) ** (1 / years) - 1
    
    strat_eq_series = np.concatenate(([1.0], compiled_eq))
    dd = (strat_eq_series - np.maximum.accumulate(strat_eq_series)) / np.maximum.accumulate(strat_eq_series)
    max_dd = np.min(dd)
    
    print("\n" + "="*50)
    print("V16 FACTORY OOS CHAMPION (STRICT EMBARGOED WFA)")
    print("="*50)
    print(f"Net CAGR: {cagr:.2%} (vs QQQ: {qqq_cagr:.2%})")
    print(f"Max DD: {max_dd:.2%}")
    print("="*50)

if __name__ == "__main__":
    run_v16_wfa_optimizer()
