import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def compute_metrics(returns, cy_arr, delta_days, name):
    excess = returns - (cy_arr * delta_days)
    std = np.std(returns, ddof=1)
    if std == 0:
        return
    sharpe = np.sqrt(252) * np.mean(excess) / std
    cagr = np.prod(1 + returns) ** (252 / len(returns)) - 1
    cum = np.cumprod(1 + returns)
    cummax = np.maximum.accumulate(cum)
    max_dd = np.min((cum - cummax) / cummax)
    
    print(f"[{name}]")
    print(f"  CAGR:   {cagr:.2%}")
    print(f"  Sharpe: {sharpe:.2f}")
    print(f"  Max DD: {max_dd:.2%}")

def run_path2():
    print("[*] PATH 2: Out-Of-Sample (OOS) Validation & Vol-Target Benchmark Test...")
    df_raw = yf.download(['BTC-USD', 'SPY', '^IRX'], start="2014-01-01", end="2024-01-01", progress=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']['BTC-USD']
    open_prices = df_raw['Open']['BTC-USD']
    irx = df_raw['Close']['^IRX']
    
    # Strategy Signals (2/40 SMA)
    sma_fast = close_prices.rolling(2).mean()
    sma_slow = close_prices.rolling(40).mean()
    trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
    
    vol20 = close_prices.pct_change().rolling(20).std() * np.sqrt(365)
    vol_w = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
    
    target_weights_strat = trend * vol_w
    target_weights_bench = vol_w # Always long (Buy & Hold Vol-Targeted)
    
    weights_strat_biz = target_weights_strat.ffill().reindex(biz_idx).ffill()
    weights_bench_biz = target_weights_bench.ffill().reindex(biz_idx).ffill()
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    
    r_open = (open_biz.shift(-1) / open_biz) - 1
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    
    valid_idx = biz_idx[250:-1]
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    
    r_mat = r_open.loc[valid_idx].values
    cy_arr = cy.loc[valid_idx].values
    slip_cost = 0.0020
    
    # Run simulation for Strategy and Benchmark over full period
    def sim_portfolio(target_w_series):
        target_w = target_w_series.loc[valid_idx].values
        final_port_ret = np.zeros(len(valid_idx))
        prev_actual_w = 0.0
        for i in range(len(valid_idx)):
            w = target_w[i]
            turnover = np.abs(w - prev_actual_w)
            slip = turnover * slip_cost
            cash = 1.0 - np.abs(w)
            a_ret = w * r_mat[i]
            if cash > 0:
                c_ret = cash * cy_arr[i] * delta_days[i]
            else:
                c_ret = cash * (cy_arr[i] + (0.015 / 252)) * delta_days[i]
            port_ret = a_ret + c_ret - slip
            final_port_ret[i] = port_ret
            if port_ret > -1.0:
                drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)
                prev_actual_w = w * drift_factor
            else:
                prev_actual_w = 0.0
        return pd.Series(final_port_ret, index=valid_idx)
        
    ret_strat = sim_portfolio(weights_strat_biz)
    ret_bench = sim_portfolio(weights_bench_biz)
    
    print("=" * 55)
    compute_metrics(ret_bench.values, cy_arr, delta_days, "BENCHMARK: 15% Vol-Targeted Buy & Hold BTC (Full 2014-2024)")
    print("-" * 55)
    compute_metrics(ret_strat.values, cy_arr, delta_days, "STRATEGY: V8 Trend + Vol-Target (Full 2014-2024)")
    print("=" * 55)
    
    # Split In-Sample vs Out-Of-Sample
    is_mask = valid_idx < "2021-01-01"
    oos_mask = valid_idx >= "2021-01-01"
    
    compute_metrics(ret_strat.loc[is_mask].values, cy_arr[is_mask], delta_days[is_mask], "STRATEGY In-Sample (2014-2020)")
    print("-" * 55)
    compute_metrics(ret_strat.loc[oos_mask].values, cy_arr[oos_mask], delta_days[oos_mask], "STRATEGY Out-Of-Sample (2021-2024)")
    print("=" * 55)

if __name__ == "__main__":
    run_path2()
