import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os

def load_data():
    print("Loading data...")
    qqq = pd.read_parquet('qqq_1m.parquet')
    tqqq = pd.read_parquet('tqqq_1m.parquet')
    
    # Filter to regular trading hours (9:30 to 16:00 ET)
    # The timestamps seem to be in UTC. Let's check timezone.
    # 9:30 ET = 13:30 or 14:30 UTC depending on DST. 
    # Let's convert to US/Eastern timezone to be safe.
    qqq.index = pd.to_datetime(qqq.index).tz_convert('US/Eastern')
    tqqq.index = pd.to_datetime(tqqq.index).tz_convert('US/Eastern')
    
    # Keep only 09:30 to 15:59
    qqq = qqq.between_time('09:30', '15:59')
    tqqq = tqqq.between_time('09:30', '15:59')
    
    # Load daily VIX
    vix = yf.download('^VIX', start=qqq.index.min().strftime('%Y-%m-%d'), end=(qqq.index.max() + pd.Timedelta(days=5)).strftime('%Y-%m-%d'))
    vix.index = pd.to_datetime(vix.index).tz_localize('US/Eastern')
    vix = vix.reindex(qqq.index, method='ffill')
    
    return qqq, tqqq, vix

def calc_performance(returns):
    cumulative = (1 + returns).cumprod()
    
    # Annualized Sharpe (assuming 252 * 390 minutes per year)
    ann_ret = (cumulative.iloc[-1]) ** ( (252*390) / len(returns) ) - 1
    ann_vol = returns.std() * np.sqrt(252*390)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    
    # Max Drawdown
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    return ann_ret, ann_vol, sharpe, max_dd, cumulative, drawdown

if __name__ == "__main__":
    qqq, tqqq, vix = load_data()
    print("Data loaded.")
    print("QQQ shape:", qqq.shape)
    print("TQQQ shape:", tqqq.shape)
    
    # We will compute VWAP daily
    # Group by date
    qqq['Date'] = qqq.index.date
    # compute daily vwap
    qqq['cum_vol'] = qqq.groupby('Date')['Volume'].cumsum()
    qqq['cum_vol_price'] = qqq.groupby('Date').apply(lambda x: (x['Close'] * x['Volume']).cumsum()).reset_index(level=0, drop=True)
    qqq['vwap'] = qqq['cum_vol_price'] / qqq['cum_vol']
    
    print(qqq[['Close', 'vwap']].head())
