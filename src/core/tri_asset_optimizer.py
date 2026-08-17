import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product
import warnings
warnings.filterwarnings('ignore')

def run_tri_asset_optimizer():
    print("[*] Downloading Data for Tri-Asset Optimizer (BTC + GLD + SPY)...")
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
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
    
    slip_cost = np.array([0.0020, 0.0003, 0.0003]) # BTC: 20bps, GLD: 3bps, SPY: 3bps
    
    # Grid search over Base Allocation Weights, Fast/Slow SMAs, and Vol Targets
    base_allocations = [
        np.array([0.50, 0.25, 0.25]),
        np.array([0.60, 0.20, 0.20]),
        np.array([0.40, 0.30, 0.30]),
        np.array([0.34, 0.33, 0.33]),
        np.array([0.70, 0.15, 0.15])
    ]
    
    btc_sma_pairs = [(2, 40), (5, 50), (10, 100)]
    macro_sma_pairs = [(10, 100), (20, 200), (10, 200), (5, 50)]
    vol_targets = [0.10, 0.15, 0.20]
    
    best_sharpe = 0
    best_config = None
    best_metrics = {}
    
    for alloc, (b_fast, b_slow), (m_fast, m_slow), vt in product(base_allocations, btc_sma_pairs, macro_sma_pairs, vol_targets):
        master_weights = pd.DataFrame(0.0, index=biz_idx, columns=assets)
        
        for idx_a, t in enumerate(assets):
            c = close_prices[t]
            w_base = alloc[idx_a]
            
            if t == 'BTC-USD':
                sma_fast = c.rolling(b_fast).mean()
                sma_slow = c.rolling(b_slow).mean()
                trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
                vol20 = c.pct_change().rolling(20).std() * np.sqrt(365)
                vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                target_weights_365 = trend * vol_w
                master_weights[t] = target_weights_365.ffill().reindex(biz_idx).ffill() * w_base
            else:
                c_biz = c.ffill().reindex(biz_idx).ffill()
                sma_fast = c_biz.rolling(m_fast).mean()
                sma_slow = c_biz.rolling(m_slow).mean()
                trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
                vol20 = c_biz.pct_change().rolling(20).std() * np.sqrt(252)
                vol_w = (vt / vol20).clip(upper=1.5).shift(1).fillna(0.0)
                master_weights[t] = trend * vol_w * w_base
                
        target_w = master_weights.loc[valid_idx].values
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
                
        excess = final_port_ret - (cy_arr * delta_days)
        std = np.std(final_port_ret, ddof=1)
        if std == 0: continue
        
        sharpe = np.sqrt(252) * np.mean(excess) / std
        cum = np.cumprod(1 + final_port_ret)
        cummax = np.maximum.accumulate(cum)
        dd = np.min((cum - cummax) / cummax)
        cagr = cum[-1] ** (252 / len(valid_idx)) - 1
        
        if dd > -0.20 and sharpe > best_sharpe:
            best_sharpe = sharpe
            best_config = (alloc, (b_fast, b_slow), (m_fast, m_slow), vt)
            best_metrics = {'CAGR': cagr, 'Sharpe': sharpe, 'DD': dd}
            print(f"New Best! Alloc={alloc} BTC_SMA={(b_fast, b_slow)} Macro_SMA={(m_fast, m_slow)} VolTarget={vt} | Sharpe={sharpe:.2f} DD={dd:.2%} CAGR={cagr:.2%}")

    print("\n========================================================")
    print(f"[*] BEST TRI-ASSET CONFIGURATION FOUND:")
    print(f"    Allocation (BTC, GLD, SPY): {best_config[0]}")
    print(f"    BTC SMA:                    {best_config[1]}")
    print(f"    Macro SMA (GLD/SPY):        {best_config[2]}")
    print(f"    Vol Target:                 {best_config[3]:.0%}")
    print(f"    CAGR:                       {best_metrics['CAGR']:.2%}")
    print(f"    Sharpe Ratio:               {best_metrics['Sharpe']:.2f}")
    print(f"    Max Drawdown:               {best_metrics['DD']:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_tri_asset_optimizer()
