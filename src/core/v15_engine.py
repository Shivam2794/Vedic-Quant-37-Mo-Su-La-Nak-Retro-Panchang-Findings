import yfinance as yf
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge
from master_trading_plan_v7 import load_celestial_matrix_v7, V5ContinuousVedicEngine

os.makedirs('v15_engine', exist_ok=True)

def run_v15_wfa_engine():
    print("Fetching QQQ and SPY data...")
    data = yf.download(['QQQ', 'SPY'], start='1999-03-10', end='2026-01-01', auto_adjust=False, progress=False)
    qqq = data['Close']['QQQ'].ffill().dropna()
    spy = data['Close']['SPY'].ffill().dropna()
    
    print("Loading V5 Celestial Tensors via SPY dates...")
    # The new load_celestial_matrix_v7 returns a 10-tuple.
    # We only need the merged dataframe which contains the tensors joined with SPY.
    # Alternatively, we can just call it to get tensor_df, but it returns a tuple.
    # Actually, let's just use load_celestial_matrix_v7()[0] to get merged_df, which has all tensors + SPY
    # Wait, the v15 engine manually builds it. Let's just reproduce the SPY date trick directly here to avoid tuple unpacking issues.
    
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
    
    # 1. Macro Regime Filter (50/250)
    fast = qqq.rolling(50).mean()
    slow = qqq.rolling(250).mean()
    base_bull = (fast > slow).shift(1).fillna(False)
    
    dr = qqq.pct_change().fillna(0)
    
    # Features: dynamically use all F* features, but select top 12 per WFA split
    all_feature_cols = [c for c in t.columns if c != 'date' and (c.startswith('F') or c.startswith('asp_') or c.startswith('v_') or c.startswith('a_') or 'dist' in c)]
    if not all_feature_cols:
        all_feature_cols = [c for c in t.columns if c != 'date']
        
    X = t[all_feature_cols].shift(1).fillna(0) # Strict causality
    Y = dr # Target is next day return (strictly causal since X is shifted 1)
    
    print("Running Embargoed Walk-Forward Analysis (WFA) with Dynamic Feature Selection...")
    
    tscv = TimeSeriesSplit(n_splits=10, test_size=252*2) # 2-year rolling test windows
    
    alpha_score = pd.Series(0.0, index=common)
    
    from sklearn.feature_selection import SelectKBest, mutual_info_regression
    
    # Train Ridge model iteratively
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        Y_train = Y.iloc[train_index]
        
        # Embargo: Ignore the last 20 days of training data to prevent overlap leak
        embargo = 20
        if len(X_train) > embargo:
            X_train = X_train.iloc[:-embargo]
            Y_train = Y_train.iloc[:-embargo]
            
        # Dynamically select top 12 features using mutual information on training data ONLY
        selector = SelectKBest(score_func=mutual_info_regression, k=min(12, len(all_feature_cols)))
        X_train_sel = selector.fit_transform(X_train, Y_train)
        X_test_sel = selector.transform(X_test)
            
        model = Ridge(alpha=100.0) # Regularized heavily to avoid overfit
        model.fit(X_train_sel, Y_train)
        
        alpha_score.iloc[test_index] = model.predict(X_test_sel)
        
    alpha_score_z = (alpha_score - alpha_score.rolling(252).mean()) / alpha_score.rolling(252).std()
    alpha_score_z = alpha_score_z.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    N = len(qqq)
    equity = np.ones(N)
    start_idx = np.where(qqq.index >= '2005-01-01')[0][0]
    
    equity_exp = 0.0
    for i in range(start_idx, N):
        target_exp = 2.0 if base_bull.iloc[i] else 0.0
        
        z = alpha_score_z.iloc[i]
        if z > 1.5:
            target_exp = 2.5 
        elif z < -1.5:
            target_exp = 0.0 
            
        current_exp = target_exp if i == start_idx else equity_exp
        
        borrowed = max(0.0, target_exp - 1.0)
        cash_bal = max(0.0, 1.0 - target_exp)
        margin_drag = borrowed * (0.05 / 252)
        cash_yield = cash_bal * (0.04 / 252)
        
        turnover = abs(target_exp - current_exp)
        slippage = turnover * 0.0010
        
        net_ret = (target_exp * dr.iloc[i]) - margin_drag + cash_yield - slippage
        equity[i] = equity[i-1] * (1 + net_ret)
        equity[i] = max(equity[i], 1e-8)  # M12 FIX: Bankruptcy floor guard
        
        # dynamic max drawdown risk cap
        current_dd = (equity[i] / np.max(equity[:i+1])) - 1
        if current_dd < -0.28: # Hard stop loss at 28% to defend the -30% limit
            target_exp = 0.0
            
        equity_exp = (target_exp * (1 + dr.iloc[i])) / (1 + net_ret)
        
    final_eq = equity[-1]
    years = (qqq.index[-1] - qqq.index[start_idx-1]).days / 365.25
    cagr = (final_eq ** (1 / years)) - 1
    
    qqq_cagr = (qqq.iloc[-1] / qqq.iloc[start_idx-1]) ** (1 / years) - 1
    spy_cagr = (spy.iloc[-1] / spy.iloc[start_idx-1]) ** (1 / years) - 1
    
    strat_eq_series = np.concatenate(([1.0], equity[start_idx:]))
    dd = (strat_eq_series - np.maximum.accumulate(strat_eq_series)) / np.maximum.accumulate(strat_eq_series)
    max_dd = np.min(dd)
    
    strat_full = pd.Series(strat_eq_series, index=qqq.index[start_idx-1:])
    qqq_full = qqq.iloc[start_idx-1:]
    
    strat_yearly = strat_full.resample('YE').last() / strat_full.resample('YE').first() - 1
    qqq_yearly = qqq_full.resample('YE').last() / qqq_full.resample('YE').first() - 1
    
    common_years = strat_yearly.index.intersection(qqq_yearly.index)
    wins_qqq = (strat_yearly[common_years] > qqq_yearly[common_years]).sum()
    win_rate_qqq = wins_qqq / len(common_years)
    
    calmar = cagr / abs(max_dd) if max_dd < 0 else cagr
    
    print("-" * 50)
    print("V15 VEDIC HYBRID ENGINE PERFORMANCE (WFA) (2005-2026)")
    print("-" * 50)
    print(f"V15 CAGR: {cagr:.2%} (Beats QQQ: {cagr > qqq_cagr})")
    print(f"QQQ CAGR: {qqq_cagr:.2%}")
    print("-" * 50)
    print(f"V15 Max DD: {max_dd:.2%} (Beats QQQ: {max_dd > np.min((qqq_full - qqq_full.cummax())/qqq_full.cummax())})")
    print(f"Calmar Ratio: {calmar:.2f}")
    print("-" * 50)
    print(f"Win Rate vs QQQ: {win_rate_qqq:.2%} ({wins_qqq}/{len(common_years)} years)")
    print("-" * 50)
    
if __name__ == "__main__":
    run_v15_wfa_engine()
