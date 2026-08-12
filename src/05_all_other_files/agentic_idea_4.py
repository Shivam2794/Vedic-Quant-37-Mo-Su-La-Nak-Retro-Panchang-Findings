import pandas as pd
import numpy as np

def load_data():
    qqq = pd.read_parquet('qqq_1m.parquet')
    tqqq = pd.read_parquet('tqqq_1m.parquet')
    
    qqq.index = pd.to_datetime(qqq.index).tz_convert('US/Eastern')
    tqqq.index = pd.to_datetime(tqqq.index).tz_convert('US/Eastern')
    
    qqq = qqq.between_time('09:30', '15:59')
    tqqq = tqqq.between_time('09:30', '15:59')
    
    df = qqq.copy()
    df = df.rename(columns={'Close': 'QQQ_Close', 'Open': 'QQQ_Open'})
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
    
    # We want the price at 10:00 and 15:00
    df_1000 = df[df.index.time == pd.to_datetime('10:00').time()][['Date', 'QQQ_Close']].rename(columns={'QQQ_Close': 'Close_1000'})
    df_1500 = df[df.index.time == pd.to_datetime('15:00').time()][['Date', 'QQQ_Close']].rename(columns={'QQQ_Close': 'Close_1500'})
    
    daily_stats = pd.merge(df_1000, df_1500, on='Date', how='inner')
    daily_stats['MidDay_Return'] = (daily_stats['Close_1500'] - daily_stats['Close_1000']) / daily_stats['Close_1000']
    
    daily_stats['Signal'] = 0
    # Threshold for trend continuation
    threshold = 0.005 # 0.5% move
    daily_stats.loc[daily_stats['MidDay_Return'] > threshold, 'Signal'] = 1
    daily_stats.loc[daily_stats['MidDay_Return'] < -threshold, 'Signal'] = -1
    
    # Merge signal back
    df = pd.merge(df.reset_index(), daily_stats[['Date', 'Signal']], on='Date', how='left').set_index('timestamp')
    
    # Position logic:
    # Enter at 15:00 based on Signal, Exit at 15:55
    positions = np.zeros(len(df))
    time_arr = df.index.time
    signal_arr = df['Signal'].values
    
    start_time = pd.to_datetime('15:00').time()
    end_time = pd.to_datetime('15:55').time()
    
    pos = 0
    for i in range(len(df)):
        if time_arr[i] == start_time:
            pos = signal_arr[i]
        elif time_arr[i] >= end_time:
            pos = 0
            
        positions[i] = pos
        
    df['Position'] = np.roll(positions, 1)
    df.loc[df.index[0], 'Position'] = 0
    
    df['TQQQ_Ret'] = df['TQQQ_Close'].pct_change()
    df['Strategy_Ret'] = df['Position'] * df['TQQQ_Ret']
    
    ann_ret, ann_vol, sharpe, max_dd = calc_performance(df['Strategy_Ret'].dropna())
    
    print(f"--- Power Hour Continuation Strategy ---")
    print(f"Threshold: {threshold*100}%")
    print(f"Annualized Return: {ann_ret*100:.2f}%")
    print(f"Annualized Volatility: {ann_vol*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_dd*100:.2f}%")
    print(f"Trades taken: {np.sum(np.abs(np.diff(positions))) / 2}")

if __name__ == "__main__":
    df = load_data()
    run_strategy(df)
