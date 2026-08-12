import pandas as pd
import numpy as np

# Load Data
qqq_daily = pd.read_parquet("qqq_daily.parquet")
qqq_1m = pd.read_parquet("qqq_1m.parquet")
tqqq_1m = pd.read_parquet("tqqq_1m.parquet")

qqq_daily.index = pd.to_datetime(qqq_daily.index).tz_convert('America/New_York')
qqq_1m.index = pd.to_datetime(qqq_1m.index).tz_convert('America/New_York')
tqqq_1m.index = pd.to_datetime(tqqq_1m.index).tz_convert('America/New_York')

hl = qqq_daily['High'] - qqq_daily['Low']
hc = np.abs(qqq_daily['High'] - qqq_daily['Close'].shift(1))
lc = np.abs(qqq_daily['Low'] - qqq_daily['Close'].shift(1))
tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
qqq_daily['ATR'] = tr.rolling(14).mean()

delta = qqq_daily['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
qqq_daily['RSI'] = 100 - (100 / (1 + rs))

ret = qqq_daily['Close'].pct_change()
qqq_daily['Realized_Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
qqq_daily['Realized_Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
qqq_daily['GEX_Regime'] = np.where(qqq_daily['Realized_Vol_5'] < qqq_daily['Realized_Vol_21'], 1, -1)

qqq_daily['Prev_Close'] = qqq_daily['Close'].shift(1)
qqq_daily['Prev_Volume'] = qqq_daily['Volume'].shift(1)
qqq_daily['Prev_ATR_pct'] = (qqq_daily['ATR'] / qqq_daily['Close']).shift(1)
qqq_daily['Prev_RSI'] = qqq_daily['RSI'].shift(1)
qqq_daily['Prev_Regime'] = qqq_daily['GEX_Regime'].shift(1)
qqq_daily['Prev_Vol_21'] = qqq_daily['Realized_Vol_21'].shift(1)

qqq_daily['date_str'] = qqq_daily.index.strftime('%Y-%m-%d')
qqq_daily_feat = qqq_daily[['date_str', 'Prev_Close', 'Prev_Volume', 'Prev_ATR_pct', 'Prev_RSI', 'Prev_Regime', 'Prev_Vol_21']].dropna()
qqq_daily_feat.set_index('date_str', inplace=True)

qqq_1m['date_str'] = qqq_1m.index.strftime('%Y-%m-%d')
qqq_1m['hour'] = qqq_1m.index.hour
qqq_1m['minute'] = qqq_1m.index.minute

tqqq_1m['date_str'] = tqqq_1m.index.strftime('%Y-%m-%d')
tqqq_1m['hour'] = tqqq_1m.index.hour
tqqq_1m['minute'] = tqqq_1m.index.minute

first_hour = qqq_1m[(qqq_1m['hour'] == 9) | ((qqq_1m['hour'] == 10) & (qqq_1m['minute'] < 30))]
fh_grouped = first_hour.groupby('date_str').agg({'Open': 'first', 'Close': 'last', 'Volume': 'sum'})
fh_grouped.rename(columns={'Open': 'FH_Open', 'Close': 'FH_Close', 'Volume': 'FH_Vol'}, inplace=True)

signal_df = fh_grouped.join(qqq_daily_feat, how='inner')
signal_df['FH_Green'] = signal_df['FH_Close'] > signal_df['FH_Open']
signal_df['Gap_Pct'] = (signal_df['FH_Open'] / signal_df['Prev_Close']) - 1.0
signal_df['Vol_Ratio'] = signal_df['FH_Vol'] / signal_df['Prev_Volume']

tqqq_1030 = tqqq_1m[(tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] == 30)].groupby('date_str').first()[['Open']].rename(columns={'Open': 'Entry_1030'})
signal_df = signal_df.join(tqqq_1030, how='inner')

tqqq_1558 = tqqq_1m[(tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] == 58)].groupby('date_str').first()[['Close']].rename(columns={'Close': 'Close_1558'})
signal_df = signal_df.join(tqqq_1558, how='inner')

tqqq_0930 = tqqq_1m[(tqqq_1m['hour'] == 9) & (tqqq_1m['minute'] == 30)].groupby('date_str').first()[['Open']].rename(columns={'Open': 'Open_0930'})
tqqq_0930['Next_0930'] = tqqq_0930['Open_0930'].shift(-1)
signal_df = signal_df.join(tqqq_0930['Next_0930'], how='inner')

intraday_period = tqqq_1m[((tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] > 30)) | ((tqqq_1m['hour'] > 10) & (tqqq_1m['hour'] < 15)) | ((tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] <= 58))]
intraday_hl = intraday_period.groupby('date_str').agg({'High': 'max', 'Low': 'min'}).rename(columns={'High': 'ID_High', 'Low': 'ID_Low'})
signal_df = signal_df.join(intraday_hl, how='inner')

signal_df.dropna(inplace=True)

# BINGO PARAMS
TP_M = 5.2711
SL_M = 7.6553
RSI_M = 60.0045
GAP_M = 0.0050
VOL_M = 0.1500
PORTFOLIO_LEVERAGE = 3.0
TARGET_VOL = 0.60
OVERNIGHT_ALLOCATION = 0.20
SLIPPAGE = 0.0005

mask = (signal_df['FH_Green'] & (signal_df['Prev_RSI'] < RSI_M) & (signal_df['Gap_Pct'] < -GAP_M) & (signal_df['Vol_Ratio'] > VOL_M))

tqqq_realized_vol = signal_df['Prev_Vol_21'] * 3.0
exposure = np.minimum(1.0, TARGET_VOL / np.maximum(tqqq_realized_vol, 0.0001))
exposure = np.where(signal_df['Prev_Regime'] == -1, exposure * 0.50, exposure)
total_exposure = exposure * PORTFOLIO_LEVERAGE

entry_price = signal_df['Entry_1030'] * (1 + SLIPPAGE)
vol_dollars = signal_df['Prev_ATR_pct'] * entry_price
tp_price = entry_price + (vol_dollars * TP_M)
sl_price = entry_price - (vol_dollars * SL_M)

hit_tp = signal_df['ID_High'] >= tp_price
hit_sl = signal_df['ID_Low'] <= sl_price

exit_price = signal_df['Close_1558'] * (1 - SLIPPAGE)
exit_price = np.where(hit_tp & ~hit_sl, tp_price, exit_price)
exit_price = np.where(hit_sl & ~hit_tp, sl_price, exit_price)
exit_price = np.where(hit_sl & hit_tp, sl_price, exit_price)

intraday_ret = np.where(mask, (exit_price / entry_price) - 1.0, 0.0)
intraday_pnl = intraday_ret * total_exposure

ovn_mask = (signal_df['Prev_Regime'] == 1)
ovn_entry = signal_df['Close_1558'] * (1 + SLIPPAGE)
ovn_exit = signal_df['Next_0930'] * (1 - SLIPPAGE)
ovn_ret = np.where(ovn_mask, (ovn_exit / ovn_entry) - 1.0, 0.0)
ovn_pnl = ovn_ret * (OVERNIGHT_ALLOCATION * PORTFOLIO_LEVERAGE)

total_daily_pnl = intraday_pnl + ovn_pnl
daily_pnl = pd.Series(total_daily_pnl, index=signal_df.index)

# CALCULATE METRICS
ann_ret = daily_pnl.mean() * 252
ann_vol = daily_pnl.std() * np.sqrt(252)
sharpe = ann_ret / ann_vol

cum = (1 + daily_pnl).cumprod()
roll_max = cum.cummax()
dd = (cum / roll_max) - 1.0
max_dd = abs(dd.min())

total_return = cum.iloc[-1] - 1.0
cagr = (cum.iloc[-1] ** (1 / (len(cum) / 252))) - 1.0

# Win Rate
total_trades = mask.sum() + ovn_mask.sum()
win_trades = (intraday_pnl > 0).sum() + (ovn_pnl > 0).sum()
win_rate = win_trades / total_trades if total_trades > 0 else 0

print(f"Total Return: {total_return*100:.2f}%")
print(f"CAGR: {cagr*100:.2f}%")
print(f"Max DD: {max_dd*100:.2f}%")
print(f"Sharpe Ratio: {sharpe:.2f}")
print(f"Win Rate: {win_rate*100:.2f}%")
print(f"Total Trades: {total_trades}")
