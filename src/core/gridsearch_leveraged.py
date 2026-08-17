import yfinance as yf
import pandas as pd
import numpy as np
import itertools
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')

def get_data(tickers, start_date='2010-01-01'):
    print(f"Downloading data for {tickers}...")
    df = yf.download(tickers, start=start_date, progress=False, auto_adjust=False)['Close']
    df = df.ffill().dropna(how='all')
    return df

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

def run_simulation(args):
    prices, vix, params = args
    (sma_len, vix_threshold, mom_lookback, top_n) = params
    
    universe = ['UPRO', 'TQQQ', 'SOXL', 'TECL', 'TMF', 'UGL']
    tradable_prices = prices[universe]
    
    # Momentum
    ret_mom = tradable_prices.pct_change(mom_lookback)
    abs_mom = ret_mom > 0
    ranks = ret_mom.rank(axis=1, ascending=False)
    top_assets = (ranks <= top_n)
    
    # Signals
    macd_signal = calculate_macd(tradable_prices)
    ema3_signal = calculate_3ema(tradable_prices)
    ensemble = macd_signal | ema3_signal
    
    # Weights
    raw_weights = top_assets & abs_mom & ensemble
    
    # Inverse Vol Sizing
    asset_vol = tradable_prices.pct_change().rolling(20).std() * np.sqrt(252)
    inv_vol = 1.0 / asset_vol
    weighted = inv_vol[raw_weights].fillna(0)
    weights = weighted.divide(weighted.sum(axis=1).replace(0, 1), axis=0)
    
    # Macro Gatekeeper
    spy_sma = prices['SPY'].rolling(sma_len).mean()
    macro_bear = (prices['SPY'] < spy_sma) | (vix > vix_threshold)
    
    risky_assets = ['UPRO', 'TQQQ', 'SOXL', 'TECL']
    for col in risky_assets:
        weights.loc[macro_bear, col] = 0.0
        
    weights = weights.divide(weights.sum(axis=1).replace(0, 1), axis=0).fillna(0.0)
    
    # Returns
    daily_returns = tradable_prices.pct_change().shift(-1)
    port_returns = (weights * daily_returns).sum(axis=1)
    
    # Metrics
    ret_series = port_returns.dropna()
    if len(ret_series) < 252:
        return None
        
    years = len(ret_series) / 252
    cum_ret = (1 + ret_series).prod()
    cagr = cum_ret ** (1/years) - 1 if cum_ret > 0 else -1
    
    roll_max = (1 + ret_series).cumprod().cummax()
    dd = ((1 + ret_series).cumprod() / roll_max) - 1
    max_dd = dd.min()
    
    sharpe = (ret_series.mean() / ret_series.std()) * np.sqrt(252)
    
    return {
        'SMA': sma_len,
        'VixThresh': vix_threshold,
        'MomWindow': mom_lookback,
        'TopN': top_n,
        'CAGR': cagr,
        'MaxDD': max_dd,
        'Sharpe': sharpe
    }

if __name__ == '__main__':
    universe = ['UPRO', 'TQQQ', 'SOXL', 'TECL', 'TMF', 'UGL']
    tickers = universe + ['SPY', '^VIX']
    prices = get_data(tickers, start_date='2010-01-01')
    vix = prices['^VIX']
    
    smas = [20, 50, 100, 200]
    vix_threshs = [18, 20, 25, 30]
    mom_lookbacks = [21, 42, 63, 126]
    top_ns = [1, 2]
    
    grid = list(itertools.product(smas, vix_threshs, mom_lookbacks, top_ns))
    print(f"Total combinations: {len(grid)}")
    
    args = [(prices, vix, p) for p in grid]
    
    results = []
    with Pool(cpu_count()) as p:
        for res in p.imap_unordered(run_simulation, args):
            if res is not None:
                results.append(res)
                
    df_res = pd.DataFrame(results)
    df_res.to_csv('gridsearch_leveraged_results.csv', index=False)
    
    acceptable = df_res[df_res['MaxDD'] > -0.30]
    if len(acceptable) > 0:
        print("\nBest Parameters (Max DD < 30%):")
        print(acceptable.sort_values(by='CAGR', ascending=False).head(10).to_markdown(index=False))
    else:
        print("\nNo parameters with Max DD < 30%. Top by Sharpe:")
        print(df_res.sort_values(by='Sharpe', ascending=False).head(10).to_markdown(index=False))
