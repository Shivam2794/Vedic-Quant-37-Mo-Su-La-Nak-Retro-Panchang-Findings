import pandas as pd
import numpy as np
import yfinance as yf
import ta

def load_data():
    qqq = pd.read_parquet('qqq_1m.parquet')
    tqqq = pd.read_parquet('tqqq_1m.parquet')
    
    qqq.index = pd.to_datetime(qqq.index).tz_convert('US/Eastern')
    tqqq.index = pd.to_datetime(tqqq.index).tz_convert('US/Eastern')
    
    qqq = qqq.between_time('09:30', '15:59')
    tqqq = tqqq.between_time('09:30', '15:59')
    
    # Align data
    df = qqq.copy()
    df = df.rename(columns={'Close': 'QQQ_Close', 'Open': 'QQQ_Open', 'High': 'QQQ_High', 'Low': 'QQQ_Low', 'Volume': 'QQQ_Volume'})
    df['TQQQ_Close'] = tqqq['Close']
    df['TQQQ_Open'] = tqqq['Open']
    df = df.dropna()
    
    # Load daily VIX
    vix = yf.download('^VIX', start=df.index.min().strftime('%Y-%m-%d'), end=(df.index.max() + pd.Timedelta(days=5)).strftime('%Y-%m-%d'), auto_adjust=False)
    vix.index = pd.to_datetime(vix.index).tz_localize('US/Eastern')
    vix = vix.reindex(df.index, method='ffill')
    df['VIX'] = vix['Close'].values
    
    return df

def calc_performance(returns):
    # filter out zeros for calculation of annual metrics if needed, but keeping them is accurate for time
    cumulative = (1 + returns).cumprod()
    
    ann_ret = (cumulative.iloc[-1]) ** ( (252*390) / len(returns) ) - 1
    ann_vol = returns.std() * np.sqrt(252*390)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    return ann_ret, ann_vol, sharpe, max_dd

def run_strategy(df):
    print("Calculating features...")
    df['Date'] = df.index.date
    df['Time'] = df.index.time
    
    # VWAP
    print("Calculating VWAP...")
    # faster way to compute intraday VWAP
    df['cum_vol'] = df.groupby('Date')['QQQ_Volume'].cumsum()
    df['vol_price'] = df['QQQ_Close'] * df['QQQ_Volume']
    df['cum_vol_price'] = df.groupby('Date')['vol_price'].cumsum()
    df['VWAP'] = df['cum_vol_price'] / df['cum_vol']
    
    print("Calculating Rolling Std...")
    df['Rolling_Std'] = df['QQQ_Close'].rolling(30).std()
    df['Z_Score'] = (df['QQQ_Close'] - df['VWAP']) / df['Rolling_Std']
    
    print("Calculating RSI...")
    df['RSI'] = ta.momentum.RSIIndicator(close=df['QQQ_Close'], window=14).rsi()
    
    # VIX Regime
    print("Simulating trades...")
    # Trading Logic
    position = 0 # 1 for long, -1 for short
    positions = np.zeros(len(df))
    
    # Vectorized signals
    time_valid = (df.index.time >= pd.to_datetime('10:00').time()) & (df.index.time <= pd.to_datetime('15:30').time())
    long_entry = time_valid & (df['Z_Score'] < -2.0) & (df['RSI'] < 25)
    short_entry = time_valid & (df['Z_Score'] > 2.0) & (df['RSI'] > 75)
    
    long_exit = (df['QQQ_Close'] > df['VWAP']) | (df.index.time >= pd.to_datetime('15:55').time())
    short_exit = (df['QQQ_Close'] < df['VWAP']) | (df.index.time >= pd.to_datetime('15:55').time())
    
    long_entry_arr = long_entry.values
    short_entry_arr = short_entry.values
    long_exit_arr = long_exit.values
    short_exit_arr = short_exit.values
    
    pos = 0
    time_arr = df.index.time
    end_of_day = pd.to_datetime('15:55').time()
    
    for i in range(len(df)):
        if pos == 0:
            if long_entry_arr[i]:
                pos = 1
            elif short_entry_arr[i]:
                pos = -1
        elif pos == 1:
            if long_exit_arr[i]:
                pos = 0
        elif pos == -1:
            if short_exit_arr[i]:
                pos = 0
        
        # force close at end of day
        if time_arr[i] >= end_of_day:
            pos = 0
            
        positions[i] = pos
        
    df['Position'] = np.roll(positions, 1) # Position applies to next bar return
    df.loc[df.index[0], 'Position'] = 0
    
    # Returns
    df['TQQQ_Ret'] = df['TQQQ_Close'].pct_change()
    df['Strategy_Ret'] = df['Position'] * df['TQQQ_Ret']
    
    ann_ret, ann_vol, sharpe, max_dd = calc_performance(df['Strategy_Ret'].dropna())
    
    print(f"--- Strategy Performance ---")
    print(f"Annualized Return: {ann_ret*100:.2f}%")
    print(f"Annualized Volatility: {ann_vol*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd*100:.2f}%")
    print(f"Trades taken: {np.sum(np.abs(np.diff(positions))) / 2}")
    
    return df

if __name__ == "__main__":
    df = load_data()
    run_strategy(df)
