import pandas as pd
import numpy as np
import optuna
import time
import os
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

PORTFOLIO_LEVERAGE = 3.0
TARGET_VOL = 0.60
OVERNIGHT_ALLOCATION = 0.20
SLIPPAGE = 0.0005 # 5 bps

print("Loading dataset...")
qqq_daily = pd.read_parquet("qqq_daily.parquet")
qqq_1m = pd.read_parquet("qqq_1m.parquet")
tqqq_1m = pd.read_parquet("tqqq_1m.parquet")

print("Calculating Base & Expanded Features...")
qqq_daily.index = pd.to_datetime(qqq_daily.index).tz_convert('America/New_York')
qqq_1m.index = pd.to_datetime(qqq_1m.index).tz_convert('America/New_York')
tqqq_1m.index = pd.to_datetime(tqqq_1m.index).tz_convert('America/New_York')

# 1. Volatility & ATR
hl = qqq_daily['High'] - qqq_daily['Low']
hc = np.abs(qqq_daily['High'] - qqq_daily['Close'].shift(1))
lc = np.abs(qqq_daily['Low'] - qqq_daily['Close'].shift(1))
tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
qqq_daily['ATR'] = tr.rolling(14).mean()
qqq_daily['ATR_pct'] = qqq_daily['ATR'] / qqq_daily['Close']

ret = qqq_daily['Close'].pct_change()
qqq_daily['Realized_Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
qqq_daily['Realized_Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
qqq_daily['GEX_Regime'] = np.where(qqq_daily['Realized_Vol_5'] < qqq_daily['Realized_Vol_21'], 1, -1)

# 2. RSI (Wilder's)
delta = qqq_daily['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
qqq_daily['RSI'] = 100 - (100 / (1 + rs))

# 3. Moving Averages & Trend
qqq_daily['SMA_20'] = qqq_daily['Close'].rolling(20).mean()
qqq_daily['SMA_50'] = qqq_daily['Close'].rolling(50).mean()
qqq_daily['SMA_200'] = qqq_daily['Close'].rolling(200).mean()

qqq_daily['Dist_SMA_20'] = (qqq_daily['Close'] / qqq_daily['SMA_20']) - 1.0
qqq_daily['Dist_SMA_50'] = (qqq_daily['Close'] / qqq_daily['SMA_50']) - 1.0

# 4. Momentum (Rate of Change)
qqq_daily['ROC_5'] = qqq_daily['Close'].pct_change(5)
qqq_daily['ROC_21'] = qqq_daily['Close'].pct_change(21)

# Shift daily features to T-1 for Intraday usage
daily_feats = ['Close', 'Volume', 'ATR_pct', 'RSI', 'GEX_Regime', 'Realized_Vol_21', 'Dist_SMA_20', 'Dist_SMA_50', 'ROC_5', 'ROC_21']
for col in daily_feats:
    qqq_daily[f'Prev_{col}'] = qqq_daily[col].shift(1)

qqq_daily['date_str'] = qqq_daily.index.strftime('%Y-%m-%d')
cols_to_keep = ['date_str'] + [f'Prev_{col}' for col in daily_feats]
qqq_daily_feat = qqq_daily[cols_to_keep].dropna()
qqq_daily_feat.set_index('date_str', inplace=True)

# Intraday Features
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
signal_df['DayOfWeek'] = pd.to_datetime(signal_df.index).dayofweek

# Fast Lookup DataFrames for 10:30 and 15:58
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
print(f"Data ready. Total Trading Days: {len(signal_df)}")

def objective(trial):
    # Strategy Hyperparameters
    TP_M = trial.suggest_float('TP_M', 1.0, 20.0)
    SL_M = trial.suggest_float('SL_M', 1.0, 15.0)
    
    # Feature Toggles
    use_rsi = trial.suggest_categorical('use_rsi', [True, False])
    use_gap = trial.suggest_categorical('use_gap', [True, False])
    use_vol = trial.suggest_categorical('use_vol', [True, False])
    use_fh_green = trial.suggest_categorical('use_fh_green', [True, False])
    use_trend = trial.suggest_categorical('use_trend', [True, False])
    use_mom = trial.suggest_categorical('use_mom', [True, False])
    
    # Feature Thresholds
    RSI_M = trial.suggest_float('RSI_M', 20.0, 80.0) if use_rsi else 100.0 # if not used, < 100 is always true
    GAP_M = trial.suggest_float('GAP_M', -0.05, 0.05) if use_gap else 999.0
    VOL_M = trial.suggest_float('VOL_M', 0.1, 2.0) if use_vol else 0.0
    TREND_M = trial.suggest_float('TREND_M', -0.1, 0.1) if use_trend else -999.0 # Distance from SMA 20
    MOM_M = trial.suggest_float('MOM_M', -0.1, 0.1) if use_mom else -999.0 # 5 Day ROC
    
    mask = pd.Series(True, index=signal_df.index)
    
    if use_fh_green: mask &= signal_df['FH_Green']
    if use_rsi: mask &= (signal_df['Prev_RSI'] < RSI_M)
    if use_gap: mask &= (signal_df['Gap_Pct'] < -GAP_M) # True gap must be worse than -GAP_M (e.g. < -0.01)
    if use_vol: mask &= (signal_df['Vol_Ratio'] > VOL_M)
    if use_trend: mask &= (signal_df['Prev_Dist_SMA_20'] > TREND_M)
    if use_mom: mask &= (signal_df['Prev_ROC_5'] > MOM_M)
    
    # Calculate Exposure
    tqqq_realized_vol = signal_df['Prev_Realized_Vol_21'] * 3.0
    exposure = np.minimum(1.0, TARGET_VOL / np.maximum(tqqq_realized_vol, 0.0001))
    exposure = np.where(signal_df['Prev_GEX_Regime'] == -1, exposure * 0.50, exposure)
    total_exposure = exposure * PORTFOLIO_LEVERAGE
    
    # Intraday Trades
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
    
    # Overnight Trades (Unchanged logic, just optimize allocation maybe? No, fix at 0.20 for now)
    ovn_mask = (signal_df['Prev_GEX_Regime'] == 1)
    ovn_entry = signal_df['Close_1558'] * (1 + SLIPPAGE)
    ovn_exit = signal_df['Next_0930'] * (1 - SLIPPAGE)
    ovn_ret = np.where(ovn_mask, (ovn_exit / ovn_entry) - 1.0, 0.0)
    ovn_pnl = ovn_ret * (OVERNIGHT_ALLOCATION * PORTFOLIO_LEVERAGE)
    
    total_daily_pnl = intraday_pnl + ovn_pnl
    daily_pnl = pd.Series(total_daily_pnl, index=signal_df.index)
    
    ann_ret = daily_pnl.mean() * 252
    ann_vol = daily_pnl.std() * np.sqrt(252)
    if ann_vol == 0: return -999
    
    sharpe = ann_ret / ann_vol
    
    cum = (1 + daily_pnl).cumprod()
    roll_max = cum.cummax()
    dd = (cum / roll_max) - 1.0
    max_dd = abs(dd.min())
    
    # Objective: Return high Sharpe, but MUST have DD < 30%
    penalty = 0
    if max_dd > 0.30:
        penalty += (max_dd - 0.30) * 50  # Massive penalty for >30% DD
    
    if ann_ret < 0.25:
        penalty += (0.25 - ann_ret) * 10
        
    return sharpe - penalty

if __name__ == "__main__":
    # We want a Sharpe around 2.0 and DD < 0.30
    print("Starting Eternal Grinder...")
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20000, n_jobs=-1)
    
    print("\n==============================")
    print("BEST PARAMETERS FOUND")
    print("==============================")
    for k, v in study.best_params.items():
        print(f"{k} = {v}")
    
    print(f"Best Objective: {study.best_value}")
    
    # Run the best params through a final print loop
    best = study.best_params
    # I'll just write the best params to a file so we can analyze them
    with open("best_eternal_params.json", "w") as f:
        import json
        json.dump(best, f, indent=4)
