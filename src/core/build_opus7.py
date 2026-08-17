import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

def get_data(tickers, start_date='2000-01-01'):
    print(f"Downloading data for {tickers}...")
    df = yf.download(tickers, start=start_date, progress=False, auto_adjust=False)['Close']
    df = df.ffill().dropna(how='all')
    return df

def calculate_momentum(df):
    ret_1m = df.pct_change(21)
    ret_3m = df.pct_change(63)
    ret_6m = df.pct_change(126)
    
    # Blended momentum score
    mom_score = (ret_1m + ret_3m + ret_6m) / 3
    return mom_score

def calculate_macd(df, fast=13, slow=24, signal=13):
    ema_fast = df.ewm(span=fast, adjust=False).mean()
    ema_slow = df.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd > macd_signal

def calculate_3ema(df, fast=7, med=51, slow=82):
    ema_f = df.ewm(span=fast, adjust=False).mean()
    ema_m = df.ewm(span=med, adjust=False).mean()
    ema_s = df.ewm(span=slow, adjust=False).mean()
    # f > m & m > s
    return (ema_f > ema_m) & (ema_m > ema_s)

def calculate_hurst(df, lookback=126):
    # Fast Hurst Exponent approximation using Variance Ratio
    # H = 0.5 * log( Var(z_{t} - z_{t-k}) ) / log(k)
    # where z_t is log price
    # We will compute a simplified version.
    
    # Actually, let's use the empirical approximation:
    # H = log(R/S) / log(T)
    # A rolling implementation is slow in pure pandas. Let's use a simpler proxy for regime if Hurst is too slow,
    # or implement a fast numba version. Let's do a fast numpy rolling computation.
    log_p = np.log(df)
    
    # We will just return a dummy > 0.5 for now, to ensure the rest works, then implement actual Hurst.
    # Actually, a known fast Hurst approximation over n periods:
    # H = log(high - low) / log(n) ... Wait, that's fractal dimension.
    # Let's just use SMA50 > SMA200 as the macro regime filter as specified in the master plan alternatively.
    # But plan says Hurst. Let's implement a simple rolling Variance Ratio proxy for Hurst.
    ret_1 = log_p.diff(1)
    ret_k = log_p.diff(10)
    var_1 = ret_1.rolling(lookback).var() * 10
    var_k = ret_k.rolling(lookback).var()
    # H proxy: VR = var_k / var_1. If VR > 1, trending (H > 0.5). If VR < 1, mean reverting (H < 0.5).
    # Since H ~ 0.5 + 0.5*log2(VR)
    vr = var_k / var_1
    h_proxy = 0.5 + 0.5 * np.log2(vr.clip(lower=0.1, upper=10.0))
    return h_proxy

def run_backtest():
    tickers = ['QQQ', 'SPY', 'TLT', 'GLD', 'BTC-USD', 'NVDA', 'AAPL', 'MSFT']
    # Download data
    prices = get_data(tickers, start_date='2000-01-01')
    
    # 1. Momentum Ranking (Cross-Sectional)
    mom_scores = calculate_momentum(prices)
    # Rank assets cross-sectionally daily, ignoring NaN
    ranks = mom_scores.rank(axis=1, ascending=False)
    
    # We will select top 3 assets each day that have positive momentum
    top_assets = (ranks <= 3) & (mom_scores > 0)
    
    # 2. Ensemble Signal: MACD OR 3EMA
    macd_signal = calculate_macd(prices, 13, 24, 13)
    ema3_signal = calculate_3ema(prices, 7, 51, 82)
    ensemble_signal = macd_signal | ema3_signal
    
    # Combine Filter and Signal
    raw_weights = top_assets & ensemble_signal
    
    # Calculate 20-day rolling volatility for inverse vol weighting
    asset_vol = prices.pct_change().rolling(20).std() * np.sqrt(252)
    inv_vol = 1.0 / asset_vol
    
    # Apply raw weights to inv_vol
    weighted_inv_vol = inv_vol[raw_weights]
    weighted_inv_vol = weighted_inv_vol.fillna(0)
    
    # Normalize weights
    weights = weighted_inv_vol.divide(weighted_inv_vol.sum(axis=1).replace(0, 1), axis=0)
    
    # 4. Macro Regime Gatekeeper
    spy_sma200 = prices['SPY'].rolling(200).mean()
    
    # Macro bear: SPY Price < 200 SMA. Faster and more responsive than 50 < 200.
    macro_bear = (prices['SPY'] < spy_sma200)
    
    # When macro bear is true, force weights of risky assets to 0
    risky_assets = ['QQQ', 'SPY', 'BTC-USD', 'NVDA', 'AAPL', 'MSFT']
    for col in risky_assets:
        weights.loc[macro_bear, col] = 0.0
        
    # In macro bear, if we hold no assets, we want to hold Cash (0 returns) or TLT/GLD if they have positive momentum.
    # We already zeroed out risky assets. The remaining weights are GLD and TLT.
    # Re-normalize weights
    weights = weights.divide(weights.sum(axis=1).replace(0, 1), axis=0).fillna(0.0)
    
    # 5. Calculate preliminary returns
    daily_returns = prices.pct_change().shift(-1) # Shift -1 because weights are decided at close
    port_returns_unlevered = (weights * daily_returns).sum(axis=1)
    
    # 6. Volatility Targeting & Leverage
    # Target 15% annualized vol for stricter drawdown control
    TARGET_VOL = 0.15
    # Rolling 20-day annualized vol of the unlevered portfolio (faster reaction)
    roll_vol = port_returns_unlevered.rolling(20).std() * np.sqrt(252)
    
    # Leverage = Target / Current Vol
    leverage = (TARGET_VOL / roll_vol.replace(0, np.nan)).clip(0.0, 2.5)
    leverage = leverage.fillna(1.0).shift(1) # Shift 1 because we can't know today's vol until close
    
    port_returns_levered = port_returns_unlevered * leverage
    
    # Calculate Equity Curves
    eq_unlev = (1 + port_returns_unlevered).cumprod()
    eq_lev = (1 + port_returns_levered).cumprod()
    
    spy_eq = (1 + daily_returns['SPY']).cumprod()
    qqq_eq = (1 + daily_returns['QQQ']).cumprod()
    
    # Metrics Calculation function
    def calc_metrics(ret_series, name):
        ret_series = ret_series.dropna()
        if len(ret_series) == 0:
            return {}
        years = len(ret_series) / 252
        cum_ret = (1 + ret_series).prod()
        if cum_ret <= 0:
            cagr = -1
        else:
            cagr = cum_ret ** (1/years) - 1
        
        roll_max = (1 + ret_series).cumprod().cummax()
        dd = ((1 + ret_series).cumprod() / roll_max) - 1
        max_dd = dd.min()
        max_dd_idx = dd.idxmin()
        
        sharpe = (ret_series.mean() / ret_series.std()) * np.sqrt(252)
        
        return {'Strategy': name, 'CAGR': f"{cagr*100:.2f}%", 'Max DD': f"{max_dd*100:.2f}%", 'DD Date': str(max_dd_idx.date()) if pd.notnull(max_dd_idx) else '', 'Sharpe': f"{sharpe:.2f}"}

    # Slice into 5y, 10y, 25y horizons
    end_date = pd.to_datetime('today')
    horizons = {
        '5-Year': end_date - pd.DateOffset(years=5),
        '10-Year': end_date - pd.DateOffset(years=10),
        'Full': prices.index[0]
    }
    
    results = []
    for h_name, start_d in horizons.items():
        mask = port_returns_levered.index >= start_d
        res_lev = calc_metrics(port_returns_levered[mask], f"OPUS-7 ({h_name})")
        res_spy = calc_metrics(daily_returns['SPY'][mask], f"SPY ({h_name})")
        res_qqq = calc_metrics(daily_returns['QQQ'][mask], f"QQQ ({h_name})")
        results.extend([res_lev, res_spy, res_qqq])
        
    df_res = pd.DataFrame(results)
    print(df_res.to_markdown(index=False))
    
    # Save chart
    plt.figure(figsize=(12, 6))
    eq_lev.plot(label='OPUS-7', color='blue')
    spy_eq.plot(label='SPY', color='black', alpha=0.6)
    qqq_eq.plot(label='QQQ', color='green', alpha=0.6)
    plt.yscale('log')
    plt.legend()
    plt.title('OPUS-7 vs SPY vs QQQ (Log Scale)')
    plt.grid(True, alpha=0.3)
    plt.savefig('opus7_equity.png')
    print("Saved opus7_equity.png")

if __name__ == '__main__':
    run_backtest()
