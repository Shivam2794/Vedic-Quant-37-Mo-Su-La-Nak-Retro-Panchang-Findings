import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def run_trend_risk_parity():
    print("[*] Downloading Trend Risk Parity Data...")
    tickers = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'TLT', 'IEF', 'LQD', 'HYG', 'GLD', 'DBC', 'VNQ', 'SHV']
    df = yf.download(tickers, start="2008-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # 20-day annualized volatility per asset
    vol20 = returns.rolling(20).std() * np.sqrt(252)
    
    # 10-month SMA for Trend Filter
    sma200 = df.rolling(200).mean()
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    assets = ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'TLT', 'IEF', 'LQD', 'HYG', 'GLD', 'DBC', 'VNQ']
    weights = pd.DataFrame(np.nan, index=df.index, columns=tickers)
    
    for date in month_ends:
        if date not in vol20.index or date not in sma200.index:
            continue
            
        inv_vols = {}
        for asset in assets:
            v20 = vol20.loc[date, asset]
            if isinstance(v20, pd.Series): v20 = v20.iloc[0]
            if pd.isna(v20) or v20 == 0: continue
            
            p = df.loc[date, asset]
            if isinstance(p, pd.Series): p = p.iloc[0]
            
            sma = sma200.loc[date, asset]
            if isinstance(sma, pd.Series): sma = sma.iloc[0]
            
            if pd.isna(sma): continue
            
            # Trend Filter
            if p > sma:
                inv_vols[asset] = 1.0 / v20
            else:
                inv_vols[asset] = 0.0 # Don't hold if below 200 SMA
                
        total_inv_vol = sum(inv_vols.values())
        
        for col in tickers:
            weights.loc[date, col] = 0.0
            
        if total_inv_vol > 0:
            for asset, iv in inv_vols.items():
                weights.loc[date, asset] = iv / total_inv_vol
        else:
            weights.loc[date, 'SHV'] = 1.0 # 100% Cash if all assets fail trend

    weights = weights.ffill().shift(1).fillna(0.0)
    
    valid_idx = returns.index.intersection(weights.index)[200:]
    weights = weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    # Raw Return (Risk Parity + Trend)
    raw_port_ret = (weights * r).sum(axis=1)
    
    # --- Overlay: Portfolio Volatility Targeting ---
    # Target 10% Volatility
    TARGET_VOL = 0.10
    port_vol = raw_port_ret.rolling(60).std() * np.sqrt(252) # 60-day smoothed to reduce turnover
    
    vol_target_weights = pd.DataFrame(np.nan, index=weights.index, columns=tickers)
    
    for date in month_ends:
        if date not in port_vol.index or pd.isna(port_vol.loc[date]):
            continue
            
        pv = port_vol.loc[date]
        if pv == 0: continue
        
        multiplier = TARGET_VOL / pv
        multiplier = min(multiplier, 2.0) # Cap leverage at 2.0x
        
        for col in tickers:
            vol_target_weights.loc[date, col] = weights.loc[date, col] * multiplier
            
        vol_target_weights.loc[date, 'SHV'] += (1.0 - multiplier)

    vol_target_weights = vol_target_weights.ffill().shift(1).fillna(0.0)
    
    final_idx = r.index.intersection(vol_target_weights.index)[20:]
    vol_target_weights = vol_target_weights.loc[final_idx]
    r = r.loc[final_idx]
    
    final_port_ret = (vol_target_weights * r).sum(axis=1)
    
    # Turnover calculation
    delta = pd.Series(0.0, index=vol_target_weights.index)
    rebalance_dates = [d for d in month_ends if d in vol_target_weights.index]
    for i in range(1, len(rebalance_dates)):
        curr = rebalance_dates[i]
        prev = rebalance_dates[i-1]
        delta.loc[curr] = (vol_target_weights.loc[curr] - vol_target_weights.loc[prev]).abs().sum()
        
    final_port_ret -= (delta * SLIPPAGE_BPS)
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    annual_turnover = delta.sum() * 252 / len(final_port_ret)
    
    print("========================================================")
    print(f"[*] TREND RISK PARITY VOL-TARGETED RESULTS")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    print(f"Annual Turnover: {annual_turnover:.2f}x")
    
    # Benchmark SPY
    spy = r['SPY'] if isinstance(r, pd.DataFrame) else r
    bm_cagr = (1 + spy).prod() ** (252 / len(spy)) - 1
    bm_sharpe = np.sqrt(252) * spy.mean() / (spy.std() + 1e-9)
    bm_max_dd = (((1 + spy).cumprod() - (1 + spy).cumprod().cummax()) / (1 + spy).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_trend_risk_parity()
