import yfinance as yf
import pandas as pd
import numpy as np
import itertools
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')

def get_data(tickers, start_date='2000-01-01'):
    print(f"Downloading data for {tickers}...")
    df = yf.download(tickers, start=start_date, progress=False, auto_adjust=False)['Close']
    df = df.ffill().dropna(how='all')
    return df

def calculate_macd(df, fast, slow, signal):
    ema_fast = df.ewm(span=fast, adjust=False).mean()
    ema_slow = df.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd > macd_signal

def calculate_3ema(df, fast, med, slow):
    ema_f = df.ewm(span=fast, adjust=False).mean()
    ema_m = df.ewm(span=med, adjust=False).mean()
    ema_s = df.ewm(span=slow, adjust=False).mean()
    return (ema_f > ema_m) & (ema_m > ema_s)

def run_simulation(args):
    prices, vix, params = args
    (sma_len, target_vol, vol_window, max_lev, mom_lookback, vix_threshold) = params
    
    universe = ['QQQ', 'SPY', 'TLT', 'GLD', 'BTC-USD']
    tradable_prices = prices[universe]
    
    # Momentum
    ret_mom = tradable_prices.pct_change(mom_lookback)
    abs_mom = ret_mom > 0
    ranks = ret_mom.rank(axis=1, ascending=False)
    top_assets = (ranks <= 2)
    
    # Signals
    macd_signal = calculate_macd(tradable_prices, 13, 24, 13)
    ema3_signal = calculate_3ema(tradable_prices, 7, 51, 82)
    ensemble = macd_signal | ema3_signal
    
    # Weights
    raw_weights = top_assets & abs_mom & ensemble
    
    # Inverse Vol
    asset_vol = tradable_prices.pct_change().rolling(vol_window).std() * np.sqrt(252)
    inv_vol = 1.0 / asset_vol
    weighted = inv_vol[raw_weights].fillna(0)
    weights = weighted.divide(weighted.sum(axis=1).replace(0, 1), axis=0)
    
    # Macro Gatekeeper
    spy_sma = prices['SPY'].rolling(sma_len).mean()
    macro_bear = (prices['SPY'] < spy_sma) | (vix > vix_threshold)
    
    for col in ['QQQ', 'SPY', 'BTC-USD']:
        weights.loc[macro_bear, col] = 0.0
        
    weights = weights.divide(weights.sum(axis=1).replace(0, 1), axis=0).fillna(0.0)
    
    # Unlevered Returns
    daily_returns = tradable_prices.pct_change().shift(-1)
    port_unlevered = (weights * daily_returns).sum(axis=1)
    
    # Dynamic Vol Targeting
    roll_vol = port_unlevered.rolling(vol_window).std() * np.sqrt(252)
    leverage = (target_vol / roll_vol.replace(0, np.nan)).clip(0.0, max_lev)
    leverage = leverage.fillna(1.0).shift(1)
    
    port_levered = port_unlevered * leverage
    
    # Metrics
    ret_series = port_levered.dropna()
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
        'TargetVol': target_vol,
        'VolWindow': vol_window,
        'MaxLev': max_lev,
        'MomWindow': mom_lookback,
        'VixThresh': vix_threshold,
        'CAGR': cagr,
        'MaxDD': max_dd,
        'Sharpe': sharpe
    }

if __name__ == '__main__':
    universe = ['QQQ', 'SPY', 'TLT', 'GLD', 'BTC-USD']
    tickers = universe + ['^VIX']
    prices = get_data(tickers, start_date='2000-01-01')
    vix = prices['^VIX']
    
    # Parameter grid
    smas = [100, 150, 200]
    target_vols = [0.10, 0.12, 0.15]
    vol_windows = [10, 20, 40]
    max_levs = [1.5, 2.0, 2.5]
    mom_lookbacks = [42, 63, 126]
    vix_threshs = [20, 25, 30]
    
    grid = list(itertools.product(smas, target_vols, vol_windows, max_levs, mom_lookbacks, vix_threshs))
    print(f"Total combinations: {len(grid)}")
    
    args = [(prices, vix, p) for p in grid]
    
    results = []
    with Pool(cpu_count()) as p:
        for res in p.imap_unordered(run_simulation, args):
            if res is not None:
                results.append(res)
                
    df_res = pd.DataFrame(results)
    df_res = df_res.sort_values(by=['MaxDD', 'CAGR'], ascending=[False, False])
    
    # Filter for acceptable Max DD (< 20%) and sort by CAGR
    acceptable = df_res[df_res['MaxDD'] > -0.30]
    if len(acceptable) > 0:
        best = acceptable.sort_values(by='CAGR', ascending=False).head(10)
        print("\nBest Parameters (Max DD < 30%):")
        print(best.to_markdown(index=False))
    else:
        print("\nNo parameters found with Max DD < 20%. Top 10 by Sharpe:")
        best = df_res.sort_values(by='Sharpe', ascending=False).head(10)
        print(best.to_markdown(index=False))
        
    df_res.to_csv('gridsearch_results.csv', index=False)
