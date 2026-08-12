import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

def get_data(tickers, start_date='2010-01-01'): # Starting 2010 to align with leveraged ETFs
    print(f"Downloading data for {tickers}...")
    df = yf.download(tickers, start=start_date, progress=False)['Close']
    df = df.ffill().dropna(how='all')
    return df

def calculate_momentum(df):
    ret_1m = df.pct_change(21)
    ret_3m = df.pct_change(63)
    ret_6m = df.pct_change(126)
    
    # Blended momentum score
    mom_score = (ret_1m * 0.4) + (ret_3m * 0.3) + (ret_6m * 0.3)
    
    # Absolute momentum check (3-month trend)
    abs_mom = ret_3m > 0
    return mom_score, abs_mom

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
    return (ema_f > ema_m) & (ema_m > ema_s)

def run_backtest():
    # Universe of Leveraged ETFs and Unleveraged Proxies for Regime
    universe = ['UPRO', 'TQQQ', 'SOXL', 'TECL', 'TMF', 'UGL']
    regime_tickers = ['SPY', 'QQQ', '^VIX']
    tickers = universe + regime_tickers
    
    # Download data
    prices = get_data(tickers, start_date='2010-01-01')
    vix = prices['^VIX']
    
    # Focus on the tradable universe
    tradable_prices = prices[universe]
    
    # 1. Momentum Ranking (Cross-Sectional)
    mom_scores, abs_mom = calculate_momentum(tradable_prices)
    ranks = mom_scores.rank(axis=1, ascending=False)
    
    # Select top 2 assets to concentrate momentum
    top_assets = (ranks <= 2)
    
    # 2. Ensemble Signal: MACD OR 3EMA (Calculated on the tradable assets)
    macd_signal = calculate_macd(tradable_prices, 13, 24, 13)
    ema3_signal = calculate_3ema(tradable_prices, 7, 51, 82)
    ensemble_signal = macd_signal | ema3_signal
    
    # 3. Combine Filter and Signal
    # Must be top ranked, have positive absolute momentum, and have a positive ensemble signal
    raw_weights = top_assets & abs_mom & ensemble_signal
    
    # 4. Inverse Volatility Sizing (Risk Parity) to balance 3x tech vs 3x bonds
    asset_vol = tradable_prices.pct_change().rolling(20).std() * np.sqrt(252)
    inv_vol = 1.0 / asset_vol
    weighted_inv_vol = inv_vol[raw_weights].fillna(0)
    
    # Normalize weights
    weights = weighted_inv_vol.divide(weighted_inv_vol.sum(axis=1).replace(0, 1), axis=0)
    
    # 5. Macro Regime Gatekeeper (Responsive Crash Filter)
    spy_sma200 = prices['SPY'].rolling(200).mean()
    
    # If SPY drops below its 200-day trend OR if market fear spikes (VIX > 25)
    macro_bear = (prices['SPY'] < spy_sma200) | (vix > 25)
    
    # When macro bear is true, aggressively cut risky leveraged equities
    risky_assets = ['UPRO', 'TQQQ', 'SOXL', 'TECL']
    for col in risky_assets:
        weights.loc[macro_bear, col] = 0.0
        
    # Re-normalize to ensure remaining capital (if TMF/UGL passed) is fully deployed
    # If nothing passed, it defaults to Cash.
    weights = weights.divide(weights.sum(axis=1).replace(0, 1), axis=0).fillna(0.0)
    
    # 6. Calculate Returns (No Portfolio-Level Leverage since assets are 3x)
    daily_returns = tradable_prices.pct_change().shift(-1)
    port_returns = (weights * daily_returns).sum(axis=1)
    
    # 7. Equity Curves
    eq = (1 + port_returns).cumprod()
    spy_eq = (1 + prices['SPY'].pct_change().shift(-1)).cumprod()
    qqq_eq = (1 + prices['QQQ'].pct_change().shift(-1)).cumprod()
    
    # Metrics
    def calc_metrics(ret_series, name):
        ret_series = ret_series.dropna()
        if len(ret_series) == 0:
            return {}
        years = len(ret_series) / 252
        cum_ret = (1 + ret_series).prod()
        cagr = cum_ret ** (1/years) - 1 if cum_ret > 0 else -1
        
        roll_max = (1 + ret_series).cumprod().cummax()
        dd = ((1 + ret_series).cumprod() / roll_max) - 1
        max_dd = dd.min()
        sharpe = (ret_series.mean() / ret_series.std()) * np.sqrt(252)
        return {'Strategy': name, 'CAGR': f"{cagr*100:.2f}%", 'Max DD': f"{max_dd*100:.2f}%", 'Sharpe': f"{sharpe:.2f}"}

    end_date = pd.to_datetime('today')
    horizons = {
        '5-Year': end_date - pd.DateOffset(years=5),
        '10-Year': end_date - pd.DateOffset(years=10),
        'Full (Since 2010)': prices.index[0]
    }
    
    results = []
    for h_name, start_d in horizons.items():
        mask = port_returns.index >= start_d
        res = calc_metrics(port_returns[mask], f"OPUS-7 Apex ({h_name})")
        res_spy = calc_metrics(prices['SPY'].pct_change().shift(-1)[mask], f"SPY ({h_name})")
        res_qqq = calc_metrics(prices['QQQ'].pct_change().shift(-1)[mask], f"QQQ ({h_name})")
        results.extend([res, res_spy, res_qqq])
        
    df_res = pd.DataFrame(results)
    print(df_res.to_markdown(index=False))
    
    plt.figure(figsize=(12, 6))
    eq.plot(label='OPUS-7 Apex (Leveraged ETFs)', color='blue')
    spy_eq.plot(label='SPY', color='black', alpha=0.6)
    qqq_eq.plot(label='QQQ', color='green', alpha=0.6)
    plt.yscale('log')
    plt.legend()
    plt.title('OPUS-7 Apex vs SPY vs QQQ (Log Scale)')
    plt.grid(True, alpha=0.3)
    plt.savefig('opus7_apex_equity.png')
    print("Saved opus7_apex_equity.png")

if __name__ == '__main__':
    run_backtest()
