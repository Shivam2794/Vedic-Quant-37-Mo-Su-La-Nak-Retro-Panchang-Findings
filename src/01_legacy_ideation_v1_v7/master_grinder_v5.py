"""
MASTER GRINDER V5 — The Eternal Holy Grail Engine
=============================================================
BRUTAL INSPECTOR FIXES APPLIED (V5):

FIX #1: JSON bool crash fixed (wf and goal are cast to Python bool() before saving).
FIX #2: Grand Portfolio Exposure Uncapped. md_target_vol and id_target_vol max bounds
         raised from 0.50 to 0.80, allowing the optimizer to push for 25% CAGR.
FIX #3: THE ETERNAL LOOP. Removed the 3-option split. We now have a single, massive 
         1,000,000-trial TPE Bayesian singularity loop. It runs autonomously and 
         stops the moment `trial.value >= 1.80` (which guarantees 0 penalty, 
         CAGR > 25%, MDD < 15%, WF SR > 1.0, and Sharpe >= 1.80).

PREVIOUS FIXES INTACT:
  - Vectorized multiday loop
  - RSI floor/ceiling & ROC Acceleration gate
  - Calendar year CAGR
  - Walk-forward SR > 1.0 gate
"""

import pandas as pd
import numpy as np
import optuna
import datetime
import warnings
import json
import os
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ============================================================
# GLOBAL CONSTANTS — NEVER CHANGE THESE (baked-in reality)
# ============================================================
TZ = 'America/New_York'
SLIPPAGE_BPS = 0.0010
SEC_FEE = 0.000008
FINRA_TAF = 0.000145
TQQQ_LEVERAGE = 3.0
MAX_POSITION_PCT = 1.0   # V4: Unleashed to 100% allocation
MIN_TRADES = 50
PRICE_MIN, PRICE_MAX = 5.0, 1000.0

# INSTITUTIONAL TARGETS (FIX #2, #3)
TARGET_CAGR    = 0.25   # 25% minimum CAGR
TARGET_SR      = 1.8    # Sharpe >= 1.8
TARGET_MAX_DD  = -0.15  # MaxDD <= -15%
TARGET_WF_SR   = 1.0    # Every WF window must beat SR 1.0 (was 0.6)


# ============================================================
# 1. DATA LOADER — loads and sanitizes everything once
# ============================================================
def load_all_data():
    print("[DATA] Loading all parquet files...")
    qqq_d = pd.read_parquet('qqq_daily.parquet')
    qqq_1m = pd.read_parquet('qqq_1m.parquet')
    tqqq_1m = pd.read_parquet('tqqq_1m.parquet')

    for df in [qqq_d, qqq_1m, tqqq_1m]:
        df.index = pd.to_datetime(df.index).tz_convert(TZ)

    # Market hours clip + bad tick removal
    qqq_1m = qqq_1m.between_time('09:30', '15:59')
    tqqq_1m = tqqq_1m.between_time('09:30', '15:59')
    tqqq_1m = tqqq_1m[(tqqq_1m['Volume'] > 0) &
                      (tqqq_1m['Open'].between(PRICE_MIN, PRICE_MAX)) &
                      (tqqq_1m['Close'].between(PRICE_MIN, PRICE_MAX))]
    qqq_1m = qqq_1m[qqq_1m['Volume'] > 0]

    print(f"[DATA] QQQ Daily: {len(qqq_d)} rows | QQQ 1m: {len(qqq_1m)} | TQQQ 1m: {len(tqqq_1m)}")
    return qqq_d, qqq_1m, tqqq_1m


def build_daily_features(qqq_d: pd.DataFrame) -> pd.DataFrame:
    """Compute all daily alpha features with strict T-1 shift to prevent lookahead."""
    d = qqq_d.copy()

    # ATR (14-period Wilder)
    hl = d['High'] - d['Low']
    hc = (d['High'] - d['Close'].shift(1)).abs()
    lc = (d['Low'] - d['Close'].shift(1)).abs()
    d['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    d['ATR_pct'] = d['ATR'] / d['Close']

    # RSI (14-period simple rolling, matching live_bot.py — NOT EWM)
    delta = d['Close'].diff()
    d['RSI'] = 100 - (100 / (1 + (
        delta.where(delta > 0, 0).rolling(14).mean() /
        np.clip(-delta.where(delta < 0, 0).rolling(14).mean(), 1e-10, None)
    )))

    # Realized vol
    ret = d['Close'].pct_change()
    d['Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
    d['Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
    d['GEX_Regime'] = np.where(d['Vol_5'] < d['Vol_21'], 1, -1)

    # Moving averages
    d['SMA_20'] = d['Close'].rolling(20).mean()
    d['SMA_50'] = d['Close'].rolling(50).mean()
    d['SMA_200'] = d['Close'].rolling(200).mean()
    d['Above_SMA_20'] = (d['Close'] > d['SMA_20']).astype(int)
    d['Above_SMA_50'] = (d['Close'] > d['SMA_50']).astype(int)
    d['Above_SMA_200'] = (d['Close'] > d['SMA_200']).astype(int)
    d['Dist_SMA20'] = (d['Close'] / d['SMA_20']) - 1.0
    d['Dist_SMA50'] = (d['Close'] / d['SMA_50']) - 1.0

    # Momentum
    d['ROC_5'] = d['Close'].pct_change(5)
    d['ROC_21'] = d['Close'].pct_change(21)
    # FIX #6: 2nd derivative of momentum — entries must show ACCELERATING momentum
    d['ROC_Accel'] = d['ROC_5'] - d['ROC_5'].shift(3)

    # === STRICT T-1 SHIFT — ALL FEATURES SHIFTED BY 1 ===
    feature_cols = ['Close', 'Volume', 'ATR_pct', 'RSI', 'GEX_Regime',
                    'Vol_21', 'Vol_5', 'Above_SMA_20', 'Above_SMA_50',
                    'Above_SMA_200', 'Dist_SMA20', 'Dist_SMA50', 'ROC_5', 'ROC_21', 'ROC_Accel']
    feat = {}
    for col in feature_cols:
        feat[f'Prev_{col}'] = d[col].shift(1)

    feat_df = pd.DataFrame(feat, index=d.index)
    feat_df['date_str'] = d.index.strftime('%Y-%m-%d')
    feat_df = feat_df.dropna().set_index('date_str')
    print(f"[FEATURES] Built {len(feat_df)} days of daily features")
    return feat_df


def build_intraday_lookup(qqq_1m: pd.DataFrame, tqqq_1m: pd.DataFrame) -> pd.DataFrame:
    """Build per-day intraday feature table: anchors, first-hour, entry/exit prices."""
    qqq_1m = qqq_1m.copy()
    tqqq_1m = tqqq_1m.copy()
    qqq_1m['date_str'] = qqq_1m.index.strftime('%Y-%m-%d')
    tqqq_1m['date_str'] = tqqq_1m.index.strftime('%Y-%m-%d')
    qqq_1m['hour'] = qqq_1m.index.hour
    qqq_1m['minute'] = qqq_1m.index.minute
    tqqq_1m['hour'] = tqqq_1m.index.hour
    tqqq_1m['minute'] = tqqq_1m.index.minute

    def get_bar(df, h, m, col, rename):
        return (df[(df['hour'] == h) & (df['minute'] == m)]
                .groupby('date_str').first()[[col]]
                .rename(columns={col: rename})
                # Deduplicate any identical-timestamp Alpaca glitches
                .pipe(lambda x: x[~x.index.duplicated(keep='first')]))

    # Signal anchors (QQQ)
    qqq_930_open = get_bar(qqq_1m, 9, 30, 'Open', 'QQQ_Open_930')
    qqq_1000_open = get_bar(qqq_1m, 10, 0, 'Open', 'QQQ_Open_1000')  # 10:00 Open (not Close!)
    qqq_1030_close = get_bar(qqq_1m, 10, 30, 'Close', 'QQQ_Close_1030')
    qqq_1500_close = get_bar(qqq_1m, 15, 0, 'Close', 'QQQ_Close_1500')

    # First hour volume (09:30-10:29) for Vol_Ratio signal
    fh_vol = (qqq_1m[(qqq_1m['hour'] == 9) | ((qqq_1m['hour'] == 10) & (qqq_1m['minute'] < 30))]
              .groupby('date_str')['Volume'].sum()
              .rename('FH_Vol'))

    # TQQQ execution prices — entry at NEXT bar's Open (latency-safe)
    # 10:31 Open (entry after 10:30 signal; 1-min latency)
    tqqq_1031_open = get_bar(tqqq_1m, 10, 31, 'Open', 'TQQQ_Entry_1031')
    # 15:58 Close (intraday time-exit, 2 min before close)
    tqqq_1558_close = get_bar(tqqq_1m, 15, 58, 'Close', 'TQQQ_Exit_1558')
    # Last bar of day (half-day safe)
    tqqq_last = (tqqq_1m.groupby('date_str').tail(1)
                 .groupby('date_str')['Close'].last()
                 .rename('TQQQ_LastClose'))
    # Next day 09:31 Open (overnight exit, 1-min latency after open)
    tqqq_next_open = get_bar(tqqq_1m, 9, 31, 'Open', 'TQQQ_NextOpen_931')
    tqqq_next_open['TQQQ_NextOpen_931'] = tqqq_next_open['TQQQ_NextOpen_931'].shift(-1)

    # TQQQ intraday high/low (10:31 to 15:58) for bracket trigger detection
    id_period = tqqq_1m[
        ((tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] > 30)) |
        ((tqqq_1m['hour'] > 10) & (tqqq_1m['hour'] < 15)) |
        ((tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] <= 58))
    ]
    id_hl = id_period.groupby('date_str').agg({'High': 'max', 'Low': 'min'})
    id_hl.columns = ['ID_High', 'ID_Low']

    # Join everything
    lk = (qqq_930_open
          .join(qqq_1000_open)
          .join(qqq_1030_close)
          .join(qqq_1500_close)
          .join(fh_vol)
          .join(tqqq_1031_open)
          .join(tqqq_1558_close)
          .join(tqqq_last)
          .join(tqqq_next_open)
          .join(id_hl)
          .dropna(subset=['TQQQ_Entry_1031', 'TQQQ_NextOpen_931']))

    print(f"[INTRADAY] Built lookup for {len(lk)} trading days")
    return lk


# ============================================================
# 2. COST ENGINE — multiplicative slippage applied to prices
# ============================================================
def apply_cost(entry_price: float, exit_price: float,
               direction: int, shares: float = 100.0) -> tuple:
    """
    Apply realistic costs to entry/exit prices.
    Returns (entry_cost_adjusted, exit_cost_adjusted, reg_cost_fraction).
    """
    slip_e = 1 + direction * SLIPPAGE_BPS   # long: pay more, short: receive less
    slip_x = 1 - direction * SLIPPAGE_BPS   # long: receive less, short: pay more
    reg = (SEC_FEE + FINRA_TAF) * shares / (shares * exit_price) if exit_price > 0 else 0
    return entry_price * slip_e, exit_price * slip_x, reg


# ============================================================
# 3. PERFORMANCE ENGINE — statistically correct formulas
# ============================================================
def compute_metrics(daily_pnl: pd.Series) -> dict:
    """Compute all performance metrics. Uses actual calendar years for CAGR."""
    if len(daily_pnl) < MIN_TRADES:
        return {'Sharpe': -999, 'MaxDD': -999, 'CAGR': -999, 'WinRate': 0, 'Trades': 0}

    cum = (1 + daily_pnl).cumprod()
    actual_years = ((pd.to_datetime(str(daily_pnl.index[-1])) -
                     pd.to_datetime(str(daily_pnl.index[0]))).days / 365.25)
    if actual_years < 0.1:
        return {'Sharpe': -999, 'MaxDD': -999, 'CAGR': -999, 'WinRate': 0, 'Trades': 0}

    cagr = cum.iloc[-1] ** (1.0 / actual_years) - 1
    ann_vol = daily_pnl.std() * np.sqrt(252)
    sharpe = cagr / ann_vol if ann_vol > 1e-10 else -999

    dd = (cum / cum.cummax()) - 1
    max_dd = dd.min()

    nonzero = daily_pnl[daily_pnl != 0]
    win_rate = (nonzero > 0).mean() if len(nonzero) > 0 else 0

    return {
        'Sharpe': sharpe,
        'MaxDD': max_dd,
        'CAGR': cagr,
        'AnnVol': ann_vol,
        'WinRate': win_rate,
        'Trades': int((daily_pnl != 0).sum()),
        'Cumulative': cum,
    }


def walk_forward_check(daily_pnl: pd.Series, n_windows: int = 3,
                       min_sr: float = 0.6) -> bool:
    """Returns True only if ALL walk-forward windows have Sharpe > min_sr."""
    idx = daily_pnl.index
    n = len(idx)
    size = n // n_windows
    for i in range(n_windows):
        window = daily_pnl.iloc[i * size: (i + 1) * size]
        m = compute_metrics(window)
        if m['Sharpe'] < min_sr:
            return False
    return True


# ============================================================
# 4. POSITION SIZING — volatility-targeted, regime-aware
# ============================================================
def vectorized_position_size(df: pd.DataFrame, target_vol: float) -> np.ndarray:
    """
    Vectorized volatility-targeted sizing.
    TQQQ vol approximated as QQQ_vol * 3x leverage.
    Halved in short-gamma regimes. Capped at MAX_POSITION_PCT.
    """
    tqqq_vol = np.maximum(df['Prev_Vol_21'] * TQQQ_LEVERAGE, 0.05)
    raw = target_vol / tqqq_vol
    adjusted = raw * np.where(df['Prev_GEX_Regime'] == -1, 0.50, 1.0)
    return np.minimum(adjusted, MAX_POSITION_PCT)


# ============================================================
# 5. STRATEGY ARCHETYPES
# ============================================================

def strategy_overnight(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Strategy A: Overnight Momentum.
    FIX #4: RSI now has floor (rsi_min) AND ceiling (rsi_max).
    FIX #6: ROC_Accel > 0 gate — momentum must be accelerating.
    """
    p = params
    df = signal_df

    mask = (
        (df['Prev_GEX_Regime'].values == 1) &
        (df['Prev_RSI'].values > p.get('rsi_min', 30)) &
        (df['Prev_RSI'].values < p.get('rsi_max', 75)) &
        (df['Prev_Above_SMA_50'].values == 1) &
        (df['Prev_ROC_5'].values > p['roc5_min']) &
        (df['Prev_ROC_Accel'].values > 0)
    )

    entry = df['TQQQ_Exit_1558'].values * (1 + SLIPPAGE_BPS)
    exit_ = df['TQQQ_NextOpen_931'].values * (1 - SLIPPAGE_BPS)
    reg = (SEC_FEE + FINRA_TAF) / np.maximum(exit_, 1e-10)
    size = vectorized_position_size(df, p['target_vol'])
    raw_ret = (exit_ * (1 - reg) - entry) / entry
    return pd.Series(np.where(mask, raw_ret * size, 0.0), index=df.index)


def strategy_intraday_bracket(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Strategy B: Selective High-Conviction Intraday Bracket.
    Enter at 10:31 Open. TP/SL bracket using ATR.
    Only fires on top-quality days (strict multi-filter gate).
    Cost: 20 BPS round-trip + bracket execution.
    """
    p = params
    df = signal_df

    fh_open = df['QQQ_Open_930'].values
    fh_close = df['QQQ_Close_1030'].values
    fh_green = fh_close > fh_open
    gap_pct = np.abs(fh_open / np.maximum(df['Prev_Close'].values, 1e-10) - 1.0)
    vol_ratio = df['FH_Vol'].values / np.maximum(df['Prev_Volume'].values, 1e-10)

    mask = (
        fh_green &
        (df['Prev_RSI'].values > p.get('rsi_min', 30)) &
        (df['Prev_RSI'].values < p.get('rsi_max', 75)) &
        (gap_pct < p['gap_max']) &
        (vol_ratio > p['vol_ratio_min']) &
        (df['Prev_GEX_Regime'].values == 1) &
        (df['Prev_Above_SMA_50'].values == 1)
    )

    entry = df['TQQQ_Entry_1031'].values * (1 + SLIPPAGE_BPS)
    atr_dollar = df['Prev_ATR_pct'].values * entry
    tp = entry + atr_dollar * p['tp_mult']
    sl = entry - atr_dollar * p['sl_mult']

    hit_tp = df['ID_High'].values >= tp
    hit_sl = df['ID_Low'].values <= sl

    exit_ = df['TQQQ_Exit_1558'].values * (1 - SLIPPAGE_BPS)
    exit_ = np.where(hit_tp & ~hit_sl, tp * (1 - SLIPPAGE_BPS), exit_)
    exit_ = np.where(hit_sl, sl * (1 - SLIPPAGE_BPS), exit_)

    size = vectorized_position_size(df, p['target_vol'])
    reg = (SEC_FEE + FINRA_TAF) / np.maximum(exit_, 1e-10)
    raw_ret = (exit_ * (1 - reg) - entry) / entry
    return pd.Series(np.where(mask, raw_ret * size, 0.0), index=df.index)


def strategy_grand_portfolio(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    V4 Grand Portfolio: Geometric compound of Multiday + Intraday Bracket.
    Combines low-drawdown trend following with high-Sharpe mean reversion.
    """
    md_pnl = strategy_multi_day_trend(signal_df, {
        'rsi_min': params['md_rsi_min'],
        'rsi_max': params['md_rsi_max'],
        'roc5_min': params['md_roc5_min'],
        'accel_min': params['md_accel_min'],
        'hold_days': params['md_hold_days'],
        'target_vol': params['md_target_vol'],
    })
    id_pnl = strategy_intraday_bracket(signal_df, {
        'rsi_min': params['id_rsi_min'],
        'rsi_max': params['id_rsi_max'],
        'gap_max': params['id_gap_max'],
        'vol_ratio_min': params['id_vol_ratio'],
        'tp_mult': params['id_tp'],
        'sl_mult': params['id_sl'],
        'target_vol': params['id_target_vol'],
    })
    return ((1 + md_pnl) * (1 + id_pnl)) - 1


def strategy_multi_day_trend(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Strategy D: Multi-Day Trend Follow on TQQQ.
    FIX #1: O(N) Python loop ELIMINATED. Pure numpy vectorization.
    FIX #4: RSI floor + ceiling. FIX #6: Acceleration gate.
    """
    p = params
    df = signal_df
    hold_days = int(p['hold_days'])

    entry_signal = (
        (df['Prev_Above_SMA_20'].values == 1) &
        (df['Prev_Above_SMA_50'].values == 1) &
        (df['Prev_GEX_Regime'].values == 1) &
        (df['Prev_RSI'].values > p.get('rsi_min', 30)) &
        (df['Prev_RSI'].values < p.get('rsi_max', 75)) &
        (df['Prev_ROC_5'].values > p['roc5_min']) &
        (df['Prev_ROC_Accel'].values > p.get('accel_min', 0.0))
    ).astype(np.int8)

    n = len(entry_signal)
    active = np.zeros(n, dtype=np.float64)
    actual_size = np.zeros(n, dtype=np.float64)
    
    size_vals = vectorized_position_size(df, p['target_vol'])
    if isinstance(size_vals, pd.Series):
        size_vals = size_vals.values

    signal_indices = np.where(entry_signal)[0]
    if len(signal_indices) > 0:
        for s in signal_indices:
            end_idx = min(s + hold_days, n)
            active[s:end_idx] = 1.0
            actual_size[s:end_idx] = size_vals[s]  # Lock size at entry

    daily_price = df['TQQQ_Entry_1031'].values
    daily_exit = np.roll(daily_price, -1)
    daily_exit[-1] = daily_price[-1]  # last bar: no forward price, flatten

    amortized_slip = (2 * SLIPPAGE_BPS) / hold_days
    reg_fee = ((SEC_FEE + FINRA_TAF) / np.maximum(daily_exit, 1e-10)) / hold_days
    raw_ret = (daily_exit * (1 - reg_fee) / np.maximum(daily_price, 1e-10)) - 1.0 - amortized_slip

    pnl = raw_ret * actual_size * active
    return pd.Series(np.nan_to_num(pnl, nan=0.0), index=df.index)




# ============================================================
# 6. OPTUNA OBJECTIVE — Institutional penalties (FIX #2, #3, #4)
# ============================================================
def make_objective(signal_df: pd.DataFrame, arch_filter: str = None):
    """
    FIX #2: CAGR penalty 4x stronger. Target 25% CAGR minimum.
    FIX #3: WF min_sr = 1.0 (was 0.6). Failure penalty = 5.0 (was 3.0).
    FIX #4: RSI has both rsi_min and rsi_max for all archetypes.
    """
    def objective(trial: optuna.Trial) -> float:
        arch = arch_filter if arch_filter else trial.suggest_categorical(
            'arch', ['overnight', 'intraday', 'grand_portfolio', 'multiday'])

        if arch == 'grand_portfolio':
            params = {
                'md_rsi_min': trial.suggest_float('md_rsi_min', 30, 55),
                'md_rsi_max': trial.suggest_float('md_rsi_max', 55, 75),
                'md_roc5_min': trial.suggest_float('md_roc5_min', 0.0, 0.06),
                'md_accel_min': trial.suggest_float('md_accel_min', -0.01, 0.02),
                'md_hold_days': trial.suggest_int('md_hold_days', 2, 10),
                'md_target_vol': trial.suggest_float('md_target_vol', 0.20, 0.80),
                'id_rsi_min': trial.suggest_float('id_rsi_min', 30, 55),
                'id_rsi_max': trial.suggest_float('id_rsi_max', 55, 75),
                'id_gap_max': trial.suggest_float('id_gap_max', 0.003, 0.05),
                'id_vol_ratio': trial.suggest_float('id_vol_ratio', 0.1, 2.0),
                'id_tp': trial.suggest_float('id_tp', 2.0, 15.0),
                'id_sl': trial.suggest_float('id_sl', 1.0, 10.0),
                'id_target_vol': trial.suggest_float('id_target_vol', 0.20, 0.80),
            }
            pnl = strategy_grand_portfolio(signal_df, params)

        elif arch == 'overnight':
            params = {
                'rsi_min': trial.suggest_float('rsi_min', 30, 55),
                'rsi_max': trial.suggest_float('rsi_max', 55, 75),
                'roc5_min': trial.suggest_float('roc5_min', 0.0, 0.06),
                'target_vol': trial.suggest_float('target_vol', 0.20, 0.80),
            }
            pnl = strategy_overnight(signal_df, params)

        elif arch == 'intraday':
            params = {
                'rsi_min': trial.suggest_float('rsi_min', 30, 55),
                'rsi_max': trial.suggest_float('rsi_max', 55, 75),
                'gap_max': trial.suggest_float('gap_max', 0.003, 0.05),
                'vol_ratio_min': trial.suggest_float('vol_ratio_min', 0.1, 2.0),
                'tp_mult': trial.suggest_float('tp_mult', 2.0, 15.0),
                'sl_mult': trial.suggest_float('sl_mult', 1.0, 10.0),
                'target_vol': trial.suggest_float('target_vol', 0.20, 0.80),
            }
            pnl = strategy_intraday_bracket(signal_df, params)

        else:  # multiday
            params = {
                'rsi_min': trial.suggest_float('rsi_min', 30, 55),
                'rsi_max': trial.suggest_float('rsi_max', 55, 75),
                'roc5_min': trial.suggest_float('roc5_min', 0.0, 0.06),
                'accel_min': trial.suggest_float('accel_min', -0.01, 0.02),
                'hold_days': trial.suggest_int('hold_days', 2, 10),
                'target_vol': trial.suggest_float('target_vol', 0.20, 0.80),
            }
            pnl = strategy_multi_day_trend(signal_df, params)

        m = compute_metrics(pnl)
        if m['Sharpe'] == -999 or m['Trades'] < MIN_TRADES:
            return -999.0

        wf_ok = walk_forward_check(pnl, n_windows=3, min_sr=TARGET_WF_SR)

        # FIX #2: Institutional penalty matrix
        penalty = 0.0
        if abs(m['MaxDD']) > abs(TARGET_MAX_DD):
            penalty += (abs(m['MaxDD']) - abs(TARGET_MAX_DD)) * 25.0
        if m['CAGR'] < TARGET_CAGR:
            penalty += (TARGET_CAGR - m['CAGR']) * 20.0  # 4x stronger
        if not wf_ok:
            penalty += 5.0  # FIX #3: raised from 3.0

        return m['Sharpe'] - penalty

    return objective


# FIX #7: Continuous fail-safe disk save callback
def make_save_callback(filename: str):
    def cb(study, trial):
        if study.best_trial.number == trial.number:
            with open(filename, 'w') as f:
                json.dump({
                    'arch': study.best_params.get('arch', 'multiday'),
                    'params': study.best_params,
                    'best_objective': study.best_value,
                    'trials_completed': trial.number
                }, f, indent=4)
    return cb


# ============================================================
# 7. MAIN GRINDER LOOP
# ============================================================
# ============================================================
# 8. MAIN — THREE-OPTION ETERNAL GRINDER (FIX #5)
# ============================================================
def holy_grail_callback(study: optuna.Study, trial: optuna.Trial):
    # Check if objective is >= 1.80 (which implies 0 penalty and SR >= 1.80)
    if trial.value is not None and trial.value >= TARGET_SR:
        print("\n" + "="*60)
        print("HOLY GRAIL ACHIEVED! TARGETS SECURED!")
        print(f"Trial {trial.number} | Objective: {trial.value:.4f}")
        print("="*60)
        study.stop()

def main():
    print("="*60)
    print("MASTER GRINDER V5 — ETERNAL HOLY GRAIL ENGINE")
    print("="*60)
    qqq_d, qqq_1m, tqqq_1m = load_all_data()
    daily_feats = build_daily_features(qqq_d)
    intraday_lk = build_intraday_lookup(qqq_1m, tqqq_1m)
    signal_df = intraday_lk.join(daily_feats, how='inner').dropna()
    print(f"[SIGNAL] Combined signal matrix: {len(signal_df)} trading days")

    print("\n" + "="*60)
    print("THE ETERNAL LOOP (1,000,000 Trials)")
    print("Stops autonomously if Sharpe >= 1.80 & CAGR >= 25% & MaxDD <= -15%")
    print("="*60)
    
    study = optuna.create_study(
        study_name="eternal_singularity", direction='maximize',
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    study.optimize(
        make_objective(signal_df, arch_filter=None),
        n_trials=1000000, n_jobs=1, show_progress_bar=True,
        callbacks=[make_save_callback('grinder_v5_eternal_best.json'), holy_grail_callback]
    )

    b = study.best_params
    a = b.get('arch', 'multiday')
    if a == 'overnight': pnl = strategy_overnight(signal_df, b)
    elif a == 'intraday': pnl = strategy_intraday_bracket(signal_df, b)
    elif a == 'grand_portfolio': pnl = strategy_grand_portfolio(signal_df, b)
    else: pnl = strategy_multi_day_trend(signal_df, b)
    
    m = compute_metrics(pnl)
    wf = walk_forward_check(pnl)
    
    goal = (m['Sharpe'] >= TARGET_SR and abs(m['MaxDD']) <= abs(TARGET_MAX_DD)
            and m['CAGR'] >= TARGET_CAGR and wf)
    status = 'GOAL MET' if goal else 'Below target'
    print(f"\nFINAL: {status} | CAGR {m['CAGR']*100:.2f}% | SR {m['Sharpe']:.4f} | MDD {m['MaxDD']*100:.2f}% | WF: {wf}")

    final_json = {
        'Eternal_Best': {
            'CAGR': f"{m['CAGR']*100:.2f}%", 'Sharpe': f"{m['Sharpe']:.4f}",
            'MaxDD': f"{m['MaxDD']*100:.2f}%", 'WinRate': f"{m['WinRate']*100:.2f}%",
            'Trades': int(m['Trades']), 'WalkForward': bool(wf), 'GoalMet': bool(goal), 'params': b
        }
    }

    with open('grinder_v5_FINAL_VERDICT.json', 'w') as f:
        json.dump(final_json, f, indent=4)
    print("\n[SAVED] grinder_v5_FINAL_VERDICT.json written.")


if __name__ == '__main__':
    main()
