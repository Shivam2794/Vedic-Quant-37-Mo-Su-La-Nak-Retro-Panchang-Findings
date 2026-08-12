import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from master_trading_plan_v6 import V5ContinuousVedicEngine, load_celestial_matrix

def generate_equity_curve():
    raw_df, source_path = load_celestial_matrix()
    engine = V5ContinuousVedicEngine(raw_df)
    tensor_df = engine.compute_all_tensors()
    
    spy = yf.download("SPY", start="1993-01-01", end="2026-12-31", progress=False)
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.get_level_values(0)
    
    tensor_df['date'] = pd.to_datetime(tensor_df['date'])
    spy.index = pd.to_datetime(spy.index)
    
    feature_cols = [c for c in tensor_df.columns if c != 'date']
    merged = spy.join(tensor_df.set_index('date'), how='inner')
    
    X = merged[feature_cols].to_numpy(dtype=np.float64)
    opens = merged['Open'].to_numpy(dtype=np.float64)
    highs = merged['High'].to_numpy(dtype=np.float64)
    lows = merged['Low'].to_numpy(dtype=np.float64)
    closes = merged['Close'].to_numpy(dtype=np.float64)
    sma200 = merged['Close'].rolling(window=200, min_periods=1).mean().to_numpy(dtype=np.float64)
    
    model_path = "eternal_best_model_v6_phase4.json"
    if not os.path.exists(model_path):
        print(f"Model {model_path} not found.")
        return
    
    with open(model_path, 'r') as f:
        champion = json.load(f)
        
    weights = np.array(champion['weights'], dtype=np.float64)
    v_th = champion['v_th']
    max_leverage = champion['max_leverage']
    stop_loss = champion['stop_loss']
    take_profit = champion['take_profit']
    
    scores = X @ weights
    
    # Run numpy backtest to get daily returns
    N = len(scores)
    signals = np.zeros(N, dtype=np.int8)
    signals[scores > v_th] = 1
    signals[scores < -v_th] = -1
    signals[(signals == 1) & (closes < sma200)] = 0
    signals[(signals == -1) & (closes > sma200)] = 0
    
    base_friction = 0.0003
    margin_rate = 0.05 / 252.0
    
    pos = np.zeros(N, dtype=np.int8)
    daily_rets = np.zeros(N, dtype=np.float64)
    
    # Simple vectorized approximation for plotting (no intraday high/low strict ordering)
    for t in range(1, N):
        if np.isnan(sma200[t-1]):
            continue
        
        target = signals[t-1]
        c_prev = closes[t-1]
        o_t = opens[t]
        c_t = closes[t]
        if c_prev <= 1e-8: continue
        
        # SL/TP approximation (simplified for plotting, true physics is in numba)
        # We will just use the day's return
        current_pos = pos[t-1]
        
        if current_pos == 0:
            if target == 1:
                pos[t] = 1
                ret = (c_t - o_t) / o_t
                daily_rets[t] = max_leverage * ret - (base_friction * max_leverage)
            elif target == -1:
                pos[t] = -1
                ret = (o_t - c_t) / o_t
                daily_rets[t] = max_leverage * ret - (base_friction * max_leverage)
        elif current_pos == 1:
            if target == 1:
                pos[t] = 1
                ret = (c_t - c_prev) / c_prev
                daily_rets[t] = max_leverage * ret - (margin_rate * max(0.0, max_leverage - 1.0))
            else:
                pos[t] = 0
                ret = (o_t - c_prev) / c_prev
                daily_rets[t] = max_leverage * ret - (base_friction * max_leverage) - (margin_rate * max(0.0, max_leverage - 1.0))
                # Add intraday entry if target == -1
                if target == -1:
                    pos[t] = -1
                    ret2 = (o_t - c_t) / o_t
                    daily_rets[t] += max_leverage * ret2 - (base_friction * max_leverage)
        elif current_pos == -1:
            if target == -1:
                pos[t] = -1
                ret = (c_prev - c_t) / c_prev
                daily_rets[t] = max_leverage * ret - (margin_rate * max(0.0, max_leverage - 1.0))
            else:
                pos[t] = 0
                ret = (c_prev - o_t) / c_prev
                daily_rets[t] = max_leverage * ret - (base_friction * max_leverage) - (margin_rate * max(0.0, max_leverage - 1.0))
                if target == 1:
                    pos[t] = 1
                    ret2 = (c_t - o_t) / o_t
                    daily_rets[t] += max_leverage * ret2 - (base_friction * max_leverage)

    eq_curve = np.cumprod(1.0 + daily_rets)
    spy_rets = np.zeros(N, dtype=np.float64)
    for t in range(1, N):
        c_prev = closes[t-1]
        c_t = closes[t]
        if c_prev > 1e-8:
            spy_rets[t] = (c_t - c_prev) / c_prev
    spy_eq = np.cumprod(1.0 + spy_rets)
    
    plt.figure(figsize=(12, 6))
    plt.plot(merged.index, eq_curve, label='Vedic Tensor Strategy', color='green')
    plt.plot(merged.index, spy_eq, label='SPY Benchmark', color='blue', alpha=0.7)
    plt.yscale('log')
    plt.title('Vedic Quant Engine (Phase 4 Full Period) vs SPY Benchmark (Log Scale)')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return (Log Scale)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('v6_equity_curve.png', dpi=300)
    print("Plot saved to v6_equity_curve.png")

if __name__ == "__main__":
    generate_equity_curve()
