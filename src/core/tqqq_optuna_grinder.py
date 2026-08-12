import pandas as pd
import numpy as np
import optuna
import time
import os
import matplotlib.pyplot as plt

# Strategy Config Matching Live Bot
PORTFOLIO_LEVERAGE = 3.0
TARGET_VOL = 0.60
OVERNIGHT_ALLOCATION = 0.20

# Trading Costs
SLIPPAGE = 0.0005 # 5 bps

print("Loading dataset...")
qqq_daily = pd.read_parquet("qqq_daily.parquet")
qqq_1m = pd.read_parquet("qqq_1m.parquet")
tqqq_1m = pd.read_parquet("tqqq_1m.parquet")

print("Calculating Base Features...")
# Align to NY time for easier filtering
qqq_daily.index = pd.to_datetime(qqq_daily.index).tz_convert('America/New_York')
qqq_1m.index = pd.to_datetime(qqq_1m.index).tz_convert('America/New_York')
tqqq_1m.index = pd.to_datetime(tqqq_1m.index).tz_convert('America/New_York')

# 1. Daily Features (computed exactly as live_bot.py)
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

# Pre-compute Prev Close and Prev Volume
qqq_daily['Prev_Close'] = qqq_daily['Close'].shift(1)
qqq_daily['Prev_Volume'] = qqq_daily['Volume'].shift(1)
qqq_daily['Prev_ATR_pct'] = (qqq_daily['ATR'] / qqq_daily['Close']).shift(1)
qqq_daily['Prev_RSI'] = qqq_daily['RSI'].shift(1)
qqq_daily['Prev_Regime'] = qqq_daily['GEX_Regime'].shift(1)
qqq_daily['Prev_Vol_21'] = qqq_daily['Realized_Vol_21'].shift(1)

# Shift daily to match "yesterday's data" for today's intraday action
qqq_daily['date_str'] = qqq_daily.index.strftime('%Y-%m-%d')
qqq_daily_feat = qqq_daily[['date_str', 'Prev_Close', 'Prev_Volume', 'Prev_ATR_pct', 'Prev_RSI', 'Prev_Regime', 'Prev_Vol_21']].dropna()
qqq_daily_feat.set_index('date_str', inplace=True)

# 2. Intraday Features (09:30 to 10:30)
qqq_1m['date_str'] = qqq_1m.index.strftime('%Y-%m-%d')
qqq_1m['hour'] = qqq_1m.index.hour
qqq_1m['minute'] = qqq_1m.index.minute

tqqq_1m['date_str'] = tqqq_1m.index.strftime('%Y-%m-%d')
tqqq_1m['hour'] = tqqq_1m.index.hour
tqqq_1m['minute'] = tqqq_1m.index.minute

# Filter First Hour (09:30 to 10:29)
first_hour = qqq_1m[(qqq_1m['hour'] == 9) | ((qqq_1m['hour'] == 10) & (qqq_1m['minute'] < 30))]

fh_grouped = first_hour.groupby('date_str').agg({
    'Open': 'first',
    'Close': 'last',
    'Volume': 'sum'
})
fh_grouped.rename(columns={'Open': 'FH_Open', 'Close': 'FH_Close', 'Volume': 'FH_Vol'}, inplace=True)

# Combine for Daily Signal Matrix
signal_df = fh_grouped.join(qqq_daily_feat, how='inner')
signal_df['FH_Green'] = signal_df['FH_Close'] > signal_df['FH_Open']
signal_df['Gap_Pct'] = (signal_df['FH_Open'] / signal_df['Prev_Close']) - 1.0
signal_df['Vol_Ratio'] = signal_df['FH_Vol'] / signal_df['Prev_Volume']

# Fast Lookup DataFrames for 10:30 and 15:58
# TQQQ 10:30 prices (Intraday Entry)
tqqq_1030 = tqqq_1m[(tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] == 30)]
tqqq_1030 = tqqq_1030.groupby('date_str').first()[['Open']]
tqqq_1030.rename(columns={'Open': 'Entry_1030'}, inplace=True)
signal_df = signal_df.join(tqqq_1030, how='inner')

# TQQQ 15:58 prices (Intraday Exit, Overnight Entry)
tqqq_1558 = tqqq_1m[(tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] == 58)]
tqqq_1558 = tqqq_1558.groupby('date_str').first()[['Close']]
tqqq_1558.rename(columns={'Close': 'Close_1558'}, inplace=True)
signal_df = signal_df.join(tqqq_1558, how='inner')

# TQQQ Next Day 09:30 (Overnight Exit)
tqqq_0930 = tqqq_1m[(tqqq_1m['hour'] == 9) & (tqqq_1m['minute'] == 30)]
tqqq_0930 = tqqq_0930.groupby('date_str').first()[['Open']]
tqqq_0930.rename(columns={'Open': 'Open_0930'}, inplace=True)
tqqq_0930['Next_0930'] = tqqq_0930['Open_0930'].shift(-1)
signal_df = signal_df.join(tqqq_0930['Next_0930'], how='inner')

# TQQQ Highs and Lows between 10:30 and 15:58 for Bracket Triggers
intraday_period = tqqq_1m[
    ((tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] > 30)) |
    ((tqqq_1m['hour'] > 10) & (tqqq_1m['hour'] < 15)) |
    ((tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] <= 58))
]
intraday_hl = intraday_period.groupby('date_str').agg({
    'High': 'max',
    'Low': 'min'
})
intraday_hl.rename(columns={'High': 'ID_High', 'Low': 'ID_Low'}, inplace=True)
signal_df = signal_df.join(intraday_hl, how='inner')

# Drop NA
signal_df.dropna(inplace=True)
print(f"Data ready. Total Trading Days: {len(signal_df)}")


def run_backtest(params):
    TP_M = params['TP_M']
    SL_M = params['SL_M']
    RSI_M = params['RSI_M']
    GAP_M = params['GAP_M']
    VOL_M = params['VOL_M']
    
    # Intraday Signals
    mask = (
        signal_df['FH_Green'] &
        (signal_df['Prev_RSI'] < RSI_M) &
        (signal_df['Gap_Pct'] < -GAP_M) &
        (signal_df['Vol_Ratio'] > VOL_M)
    )
    
    # Calculate Exposure
    tqqq_realized_vol = signal_df['Prev_Vol_21'] * 3.0
    exposure = np.minimum(1.0, TARGET_VOL / np.maximum(tqqq_realized_vol, 0.0001))
    
    # Apply regime halving
    exposure = np.where(signal_df['Prev_Regime'] == -1, exposure * 0.50, exposure)
    total_exposure = exposure * PORTFOLIO_LEVERAGE
    
    # Intraday trades
    entry_price = signal_df['Entry_1030'] * (1 + SLIPPAGE)
    vol_dollars = signal_df['Prev_ATR_pct'] * entry_price
    tp_price = entry_price + (vol_dollars * TP_M)
    sl_price = entry_price - (vol_dollars * SL_M)
    
    # Vectorized bracket resolution
    hit_tp = signal_df['ID_High'] >= tp_price
    hit_sl = signal_df['ID_Low'] <= sl_price
    
    exit_price = signal_df['Close_1558'] * (1 - SLIPPAGE)
    exit_price = np.where(hit_tp & ~hit_sl, tp_price, exit_price)
    exit_price = np.where(hit_sl & ~hit_tp, sl_price, exit_price)
    
    # If both hit in the same day, take worst case (stop loss)
    exit_price = np.where(hit_sl & hit_tp, sl_price, exit_price)
    
    intraday_ret = np.where(mask, (exit_price / entry_price) - 1.0, 0.0)
    intraday_pnl = intraday_ret * total_exposure
    
    # Overnight trades
    ovn_mask = (signal_df['Prev_Regime'] == 1)
    ovn_entry = signal_df['Close_1558'] * (1 + SLIPPAGE)
    ovn_exit = signal_df['Next_0930'] * (1 - SLIPPAGE)
    ovn_ret = np.where(ovn_mask, (ovn_exit / ovn_entry) - 1.0, 0.0)
    ovn_pnl = ovn_ret * (OVERNIGHT_ALLOCATION * PORTFOLIO_LEVERAGE)
    
    # Combine
    total_daily_pnl = intraday_pnl + ovn_pnl
    return pd.Series(total_daily_pnl, index=signal_df.index)

def objective(trial):
    params = {
        'TP_M': trial.suggest_float('TP_M', 1.0, 10.0),
        'SL_M': trial.suggest_float('SL_M', 1.0, 10.0),
        'RSI_M': trial.suggest_float('RSI_M', 30.0, 80.0),
        'GAP_M': trial.suggest_float('GAP_M', 0.005, 0.10),
        'VOL_M': trial.suggest_float('VOL_M', 0.1, 3.0)
    }
    
    daily_pnl = run_backtest(params)
    
    # Deflated Sharpe
    ann_ret = daily_pnl.mean() * 252
    ann_vol = daily_pnl.std() * np.sqrt(252)
    if ann_vol == 0: return -999
    
    sharpe = ann_ret / ann_vol
    
    # Max Drawdown
    cum = (1 + daily_pnl).cumprod()
    roll_max = cum.cummax()
    dd = (cum / roll_max) - 1.0
    max_dd = abs(dd.min())
    
    # Fable's Brutal Penalty:
    # Need return > 0.40, MaxDD < 0.25
    penalty = 0
    if max_dd > 0.25:
        penalty += (max_dd - 0.25) * 10
    if ann_ret < 0.40:
        penalty += (0.40 - ann_ret) * 10
        
    obj = sharpe - penalty
    return obj

if __name__ == "__main__":
    study = optuna.create_study(direction="maximize")
    print("Unleashing Vectorized Optuna Grinder...")
    study.optimize(objective, n_trials=5000, n_jobs=-1)
    
    print("\n[+] BINGO! New Holy Grail Parameters:")
    best = study.best_params
    for k, v in best.items():
        print(f"    {k} = {v:.4f}")
        
    print(f"\nBest Objective Value: {study.best_value:.4f}")
    
    # Save Equity Curve
    best_pnl = run_backtest(best)
    cum = (1 + best_pnl).cumprod()
    
    plt.figure(figsize=(10,5))
    plt.plot(pd.to_datetime(cum.index), cum.values, label='Corrected Strategy (TQQQ)')
    plt.title("Corrected Institutional TQQQ Engine (In-Sample)")
    plt.grid()
    plt.legend()
    plt.savefig("corrected_tqqq_equity.png")
    print("Saved plot to corrected_tqqq_equity.png")
