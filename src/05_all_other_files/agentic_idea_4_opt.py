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
    return sharpe, max_dd, ann_ret

def run_strategy(df, start_time_str='10:00', enter_time_str='15:00', exit_time_str='15:55', threshold=0.005, day_of_week_filter=None):
    if 'Date' not in df.columns:
        df['Date'] = df.index.date
        
    df_start = df[df.index.time == pd.to_datetime(start_time_str).time()][['QQQ_Close']]
    df_start['Date'] = df_start.index.date
    df_start = df_start.rename(columns={'QQQ_Close': 'Close_start'})
    
    df_enter = df[df.index.time == pd.to_datetime(enter_time_str).time()][['QQQ_Close']]
    df_enter['Date'] = df_enter.index.date
    df_enter = df_enter.rename(columns={'QQQ_Close': 'Close_enter'})
    
    daily_stats = pd.merge(df_start, df_enter, on='Date', how='inner')
    daily_stats['MidDay_Return'] = (daily_stats['Close_enter'] - daily_stats['Close_start']) / daily_stats['Close_start']
    
    daily_stats['Signal'] = 0
    daily_stats.loc[daily_stats['MidDay_Return'] > threshold, 'Signal'] = 1
    daily_stats.loc[daily_stats['MidDay_Return'] < -threshold, 'Signal'] = -1
    
    if day_of_week_filter is not None:
        daily_stats['DOW'] = pd.to_datetime(daily_stats['Date']).dt.dayofweek
        daily_stats.loc[~daily_stats['DOW'].isin(day_of_week_filter), 'Signal'] = 0
    
    df_sig = pd.merge(df.reset_index(), daily_stats[['Date', 'Signal']], on='Date', how='left').set_index('timestamp')
    
    positions = np.zeros(len(df_sig))
    time_arr = df_sig.index.time
    signal_arr = df_sig['Signal'].fillna(0).values
    
    enter_time = pd.to_datetime(enter_time_str).time()
    exit_time = pd.to_datetime(exit_time_str).time()
    
    pos = 0
    for i in range(len(df_sig)):
        if time_arr[i] == enter_time:
            pos = signal_arr[i]
        elif time_arr[i] >= exit_time:
            pos = 0
        positions[i] = pos
        
    df_sig['Position'] = np.roll(positions, 1)
    df_sig.loc[df_sig.index[0], 'Position'] = 0
    
    df_sig['TQQQ_Ret'] = df_sig['TQQQ_Close'].pct_change()
    df_sig['Strategy_Ret'] = df_sig['Position'] * df_sig['TQQQ_Ret']
    
    sharpe, max_dd, ann_ret = calc_performance(df_sig['Strategy_Ret'].dropna())
    return sharpe, max_dd, ann_ret

if __name__ == "__main__":
    df = load_data()
    
    results = []
    
    for start_t in ['09:45', '10:00', '10:30']:
        for enter_t in ['14:30', '15:00', '15:30']:
            for exit_t in ['15:55', '15:59']:
                for th in [0.003, 0.004, 0.005, 0.006, 0.007]:
                    sharpe, dd, ret = run_strategy(df, start_time_str=start_t, enter_time_str=enter_t, exit_time_str=exit_t, threshold=th)
                    results.append({
                        'Start': start_t,
                        'Enter': enter_t,
                        'Exit': exit_t,
                        'Threshold': th,
                        'Sharpe': sharpe,
                        'MaxDD': dd,
                        'AnnRet': ret
                    })
                    print(f"Start: {start_t}, Enter: {enter_t}, Exit: {exit_t}, Th: {th:.3f} | Sharpe: {sharpe:.2f}, DD: {dd*100:.2f}%")
    
    res_df = pd.DataFrame(results)
    best = res_df.sort_values('Sharpe', ascending=False).iloc[0]
    print("--- BEST RESULT ---")
    print(best)
