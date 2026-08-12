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
    
    df = qqq.copy()
    df = df.rename(columns={'Close': 'QQQ_Close', 'Open': 'QQQ_Open', 'High': 'QQQ_High', 'Low': 'QQQ_Low', 'Volume': 'QQQ_Volume'})
    df['TQQQ_Close'] = tqqq['Close']
    df['TQQQ_Open'] = tqqq['Open']
    df = df.dropna()
    return df

def calc_performance(returns):
    cumulative = (1 + returns).cumprod()
    ann_ret = (cumulative.iloc[-1]) ** ( (252*390) / len(returns) ) - 1
    ann_vol = returns.std() * np.sqrt(252*390)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    return ann_ret, ann_vol, sharpe, max_dd

def run_strategy(df):
    df['Date'] = df.index.date
    
    # Intraday High/Low Breakout (Opening Range Breakout - ORB)
    # Let's define the opening range as the first 30 minutes (09:30 - 10:00)
    # We trade breakouts of this range.
    
    # 1. Calculate ORB High and Low
    orb_window = (df.index.time >= pd.to_datetime('09:30').time()) & (df.index.time <= pd.to_datetime('10:00').time())
    df['ORB_High'] = df.loc[orb_window].groupby('Date')['QQQ_High'].transform('max')
    df['ORB_Low'] = df.loc[orb_window].groupby('Date')['QQQ_Low'].transform('min')
    
    # Forward fill the ORB levels for the rest of the day
    df['ORB_High'] = df.groupby('Date')['ORB_High'].ffill()
    df['ORB_Low'] = df.groupby('Date')['ORB_Low'].ffill()
    
    # We only trade after 10:00
    time_valid = (df.index.time > pd.to_datetime('10:00').time()) & (df.index.time <= pd.to_datetime('15:30').time())
    
    # Entry conditions:
    # Buy when price closes above ORB_High
    # Short when price closes below ORB_Low
    long_entry = time_valid & (df['QQQ_Close'] > df['ORB_High'])
    short_entry = time_valid & (df['QQQ_Close'] < df['ORB_Low'])
    
    # Exit conditions:
    # Exit long if price drops below VWAP or trailing stop
    # Let's just use a simple VWAP
    df['cum_vol'] = df.groupby('Date')['QQQ_Volume'].cumsum()
    df['vol_price'] = df['QQQ_Close'] * df['QQQ_Volume']
    df['cum_vol_price'] = df.groupby('Date')['vol_price'].cumsum()
    df['VWAP'] = df['cum_vol_price'] / df['cum_vol']
    
    # Exit when trend breaks (e.g. crossing VWAP) or EOD
    long_exit = (df['QQQ_Close'] < df['VWAP']) | (df.index.time >= pd.to_datetime('15:55').time())
    short_exit = (df['QQQ_Close'] > df['VWAP']) | (df.index.time >= pd.to_datetime('15:55').time())
    
    long_entry_arr = long_entry.values
    short_entry_arr = short_entry.values
    long_exit_arr = long_exit.values
    short_exit_arr = short_exit.values
    
    pos = 0
    positions = np.zeros(len(df))
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
                
        if time_arr[i] >= end_of_day:
            pos = 0
            
        positions[i] = pos
        
    df['Position'] = np.roll(positions, 1)
    df.loc[df.index[0], 'Position'] = 0
    
    df['TQQQ_Ret'] = df['TQQQ_Close'].pct_change()
    df['Strategy_Ret'] = df['Position'] * df['TQQQ_Ret']
    
    ann_ret, ann_vol, sharpe, max_dd = calc_performance(df['Strategy_Ret'].dropna())
    
    print(f"--- Strategy Performance ---")
    print(f"Annualized Return: {ann_ret*100:.2f}%")
    print(f"Annualized Volatility: {ann_vol*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd*100:.2f}%")
    print(f"Trades taken: {np.sum(np.abs(np.diff(positions))) / 2}")

if __name__ == "__main__":
    df = load_data()
    run_strategy(df)
