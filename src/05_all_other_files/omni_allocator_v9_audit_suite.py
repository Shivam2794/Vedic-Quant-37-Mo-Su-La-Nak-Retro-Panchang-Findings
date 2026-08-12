import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def compute_and_print(returns, cy_arr, delta_days, label):
    excess = returns - (cy_arr * delta_days)
    std = np.std(returns, ddof=1)
    if std == 0: return
    sharpe = np.sqrt(252) * np.mean(excess) / std
    cagr = np.prod(1 + returns) ** (252 / len(returns)) - 1
    cum = np.cumprod(1 + returns)
    cummax = np.maximum.accumulate(cum)
    dd = np.min((cum - cummax) / cummax)
    print(f"  [{label}] -> CAGR: {cagr:.2%} | Sharpe: {sharpe:.2f} | Max DD: {dd:.2%}")

def run_v9_audit_suite():
    print("[*] OMNI-ALLOCATOR V9 AUDIT SUITE: LATENCY & OUT-OF-SAMPLE STRESS TEST...")
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']
    open_prices = df_raw['Open']
    irx = df_raw['Close']['^IRX']
    
    valid_idx = biz_idx[250:-1]
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    r_mat = r_open[assets].loc[valid_idx].values
    
    irx = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy = (irx / 100) / 252
    cy = cy.fillna(0.0001)
    cy_arr = cy.loc[valid_idx].values
    
    slip_cost = np.array([0.0020, 0.0003, 0.0003])
    
    configs = [
        ("Config A: 50% BTC / 25% GLD / 25% SPY (15% VolTarget)", [0.50, 0.25, 0.25], 0.15),
        ("Config B: 70% BTC / 15% GLD / 15% SPY (15% VolTarget)", [0.70, 0.15, 0.15], 0.15),
    ]
    
    for conf_name, alloc, vt in configs:
        print("\n" + "="*65)
        print(conf_name)
        print("="*65)
        
        master_weights = pd.DataFrame(0.0, index=biz_idx, columns=assets)
        for idx_a, t in enumerate(assets):
            c = close_prices[t]
            w_base = alloc[idx_a]
            if t == 'BTC-USD':
                sma_fast = c.rolling(2).mean()
                sma_slow = c.rolling(40).mean()
                trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
                vol20 = c.pct_change().rolling(20).std() * np.sqrt(365)
                vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                target_weights_365 = trend * vol_w
                master_weights[t] = target_weights_365.ffill().reindex(biz_idx).ffill() * w_base
            else:
                c_biz = c.ffill().reindex(biz_idx).ffill()
                sma_fast = c_biz.rolling(10).mean()
                sma_slow = c_biz.rolling(100).mean()
                trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
                vol20 = c_biz.pct_change().rolling(20).std() * np.sqrt(252)
                vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                master_weights[t] = trend * vol_w * w_base
                
        for lag in [0, 1]:
            if lag == 0:
                target_w = master_weights.loc[valid_idx].values
                lag_label = "Standard 0-Bar Lag"
            else:
                target_w = master_weights.shift(lag).loc[valid_idx].fillna(0.0).values
                lag_label = "Hard 1-Bar Institutional Execution Lag"
                
            final_port_ret = np.zeros(len(valid_idx))
            prev_actual_w = np.zeros(len(assets))
            
            for i in range(len(valid_idx)):
                w = target_w[i]
                turnover = np.abs(w - prev_actual_w)
                slip = np.sum(turnover * slip_cost)
                cash = 1.0 - np.sum(np.abs(w))
                a_ret = np.sum(w * r_mat[i])
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
                    prev_actual_w = np.zeros(len(assets))
                    
            print(f"\n  --- {lag_label} ---")
            compute_and_print(final_port_ret, cy_arr, delta_days, "Full Sample (2014-2024)")
            
            is_mask = valid_idx < "2021-01-01"
            oos_mask = valid_idx >= "2021-01-01"
            compute_and_print(final_port_ret[is_mask], cy_arr[is_mask], delta_days[is_mask], "In-Sample (2014-2020)")
            compute_and_print(final_port_ret[oos_mask], cy_arr[oos_mask], delta_days[oos_mask], "Out-Of-Sample (2021-2024)")

if __name__ == "__main__":
    run_v9_audit_suite()
