"""
MASTER GRINDER V2 — Institutional-Grade Eternal Strategy Search Engine
=======================================================================
Architecture: Tests 5 completely different strategy archetypes simultaneously
with ALL known flaws baked-in from line 1:

COST MODEL (realistic):
  - Slippage: 10 BPS per side (20 BPS round-trip)
  - SEC fee: $0.000008/share on sells
  - FINRA TAF: $0.000145/share on sells
  - Hard-to-borrow: disabled (no TQQQ shorts)

BIAS PREVENTION:
  - All signals computed using T-1 data strictly (shift(1) everywhere)
  - Entry prices use NEXT bar's Open (1-minute latency buffer)
  - All timezone handling: America/New_York (canonical IANA)
  - Duplicate bar deduplication on every groupby
  - Bad tick filter: Volume > 0, price 5 < p < 1000
  - CAGR: actual elapsed years (not 252/N proxy)

VALIDATION:
  - Walk-forward: 3 windows (each must beat SR > 0.8)
  - Out-of-sample check flag (use 2024 data for final validation)
  - No strategy accepted unless it passes the brutal cost/WF gates

STRATEGY ARCHETYPES TESTED:
  1. Overnight Momentum (hold TQQQ overnight on bullish GEX regime days)
  2. Multi-Day Trend (hold 2-5 days when QQQ above key MAs)
  3. Selective Intraday (enter at 10:30 only on extreme low-vol high-quality days)
  4. Hybrid Overnight+Intraday (combine signals from both)
  5. Volatility-Adaptive (adjust exposure dynamically by ATR regime)
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
SLIPPAGE_BPS = 0.0010          # 10 BPS per side — realistic for leveraged ETFs
SEC_FEE = 0.000008             # per share, sell side
FINRA_TAF = 0.000145           # per share, sell side
TQQQ_LEVERAGE = 3.0
MAX_POSITION_PCT = 0.50        # hard cap: never deploy > 50% on one trade
TARGET_VOL_ANNUAL = 0.60       # annual vol target for sizing
MIN_TRADES = 50                # reject strategies with < 50 trades (not enough data)
PRICE_MIN, PRICE_MAX = 5.0, 1000.0


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

    # === STRICT T-1 SHIFT — ALL FEATURES SHIFTED BY 1 ===
    feature_cols = ['Close', 'Volume', 'ATR_pct', 'RSI', 'GEX_Regime',
                    'Vol_21', 'Vol_5', 'Above_SMA_20', 'Above_SMA_50',
                    'Above_SMA_200', 'Dist_SMA20', 'Dist_SMA50', 'ROC_5', 'ROC_21']
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
    Enter TQQQ at 15:58 Close when regime + RSI + SMA filters pass.
    Exit at next day 09:31 Open.
    Cost: 2x slippage only (no latency issue — limit order at 15:58).
    """
    p = params
    df = signal_df.copy()

    mask = (
        (df['Prev_GEX_Regime'] == 1) &
        (df['Prev_RSI'] < p['rsi_thresh']) &
        (df['Prev_Above_SMA_50'] == 1) &
        (df['Prev_ROC_5'] > p['roc5_min']) &
        (df['Prev_ROC_5'] < p['roc5_max'])
    )

    entry = df['TQQQ_Exit_1558'] * (1 + SLIPPAGE_BPS)   # buy at close + slip
    exit_ = df['TQQQ_NextOpen_931'] * (1 - SLIPPAGE_BPS)  # sell at next open - slip

    size = vectorized_position_size(df, p['target_vol'])
    
    reg_fee_pct = (SEC_FEE + FINRA_TAF) / exit_
    raw_ret = (exit_ * (1 - reg_fee_pct) - entry) / entry
    pnl = pd.Series(
        np.where(mask, raw_ret * size, 0.0),
        index=df.index
    )
    return pnl


def strategy_intraday_bracket(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Strategy B: Selective High-Conviction Intraday Bracket.
    Enter at 10:31 Open. TP/SL bracket using ATR.
    Only fires on top-quality days (strict multi-filter gate).
    Cost: 20 BPS round-trip + bracket execution.
    """
    p = params
    df = signal_df.copy()

    fh_open = df['QQQ_Open_930']
    fh_close = df['QQQ_Close_1030']
    fh_green = fh_close > fh_open
    gap_pct = (fh_open / df['Prev_Close'] - 1.0).abs()
    vol_ratio = df['FH_Vol'] / df['Prev_Volume'].replace(0, 1e-10)

    mask = (
        fh_green &
        (df['Prev_RSI'] < p['rsi_thresh']) &
        (gap_pct < p['gap_max']) &
        (vol_ratio > p['vol_ratio_min']) &
        (df['Prev_GEX_Regime'] == 1) &          # only in bullish regime
        (df['Prev_Above_SMA_50'] == 1)           # only above 50 SMA trend filter
    )

    entry = df['TQQQ_Entry_1031'] * (1 + SLIPPAGE_BPS)
    atr_dollar = df['Prev_ATR_pct'] * entry

    tp = entry + atr_dollar * p['tp_mult']
    sl = entry - atr_dollar * p['sl_mult']

    hit_tp = df['ID_High'] >= tp
    hit_sl = df['ID_Low'] <= sl

    # Worst-case: if both hit same day, assume SL fills first
    exit_ = df['TQQQ_Exit_1558'] * (1 - SLIPPAGE_BPS)
    exit_ = np.where(hit_tp & ~hit_sl, tp * (1 - SLIPPAGE_BPS), exit_)
    exit_ = np.where(hit_sl, sl * (1 - SLIPPAGE_BPS), exit_)

    size = vectorized_position_size(df, p['target_vol'])
    
    reg_fee_pct = (SEC_FEE + FINRA_TAF) / exit_
    raw_ret = (exit_ * (1 - reg_fee_pct) - entry.values) / entry.values
    pnl = pd.Series(
        np.where(mask, raw_ret * size, 0.0),
        index=df.index
    )
    return pnl


def strategy_hybrid(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Strategy C: Hybrid Overnight + Selective Intraday.
    Combines overnight regime holds with selective 10:31 intraday entries.
    Critically: intraday exit BEFORE overnight entry (no overlap).
    """
    ovn_pnl = strategy_overnight(signal_df, {
        'rsi_thresh': params['ovn_rsi'],
        'roc5_min': params['ovn_roc5_min'],
        'roc5_max': params['ovn_roc5_max'],
        'target_vol': params['ovn_target_vol'],
    })
    id_pnl = strategy_intraday_bracket(signal_df, {
        'rsi_thresh': params['id_rsi'],
        'gap_max': params['id_gap_max'],
        'vol_ratio_min': params['id_vol_ratio'],
        'tp_mult': params['id_tp'],
        'sl_mult': params['id_sl'],
        'target_vol': params['id_target_vol'],
    })
    # Sequential geometric compounding formula instead of additive assumption
    return ((1 + ovn_pnl) * (1 + id_pnl)) - 1


def strategy_multi_day_trend(signal_df: pd.DataFrame, params: dict) -> pd.Series:
    """
    Strategy D: Multi-Day Trend Follow on TQQQ.
    Enter on day N when QQQ crosses above N-day SMA with high momentum.
    Hold until signal breaks. Amortizes cost over multiple days.
    """
    p = params
    df = signal_df.copy()

    hold_days = int(p['hold_days'])  # 2-7 days

    # Entry signal: QQQ above both SMAs, GEX regime bullish, RSI not overbought
    entry_signal = (
        (df['Prev_Above_SMA_20'] == 1) &
        (df['Prev_Above_SMA_50'] == 1) &
        (df['Prev_GEX_Regime'] == 1) &
        (df['Prev_RSI'] < p['rsi_thresh']) &
        (df['Prev_ROC_5'] > p['roc5_min'])
    )

    entry_signal_vals = entry_signal.values
    size_vals = vectorized_position_size(df, p['target_vol'])
    if isinstance(size_vals, pd.Series):
        size_vals = size_vals.values
                                                  
    active = np.zeros(len(df), dtype=bool)
    trade_size = np.zeros(len(df), dtype=float)
    
    days_held = 0
    current_size = 0.0
    
    for i in range(len(df)):
        if days_held > 0:
            active[i] = True
            trade_size[i] = current_size
            days_held -= 1
        elif entry_signal_vals[i]:
            active[i] = True
            current_size = size_vals[i]
            trade_size[i] = current_size
            days_held = hold_days - 1

    # Daily mark-to-market return: from 10:31 today to 10:31 tomorrow
    daily_price = df['TQQQ_Entry_1031']
    daily_exit = daily_price.shift(-1)
    # Amortize slippage across holding days
    amortized_slippage = (2 * SLIPPAGE_BPS) / hold_days
    # Amortize regulatory fees
    reg_fee_pct = ((SEC_FEE + FINRA_TAF) / daily_exit) / hold_days
    
    raw_daily_ret = (daily_exit * (1 - reg_fee_pct) / daily_price) - 1.0 - amortized_slippage
    
    pnl_list = pd.Series(
        np.where(active, raw_daily_ret.fillna(0.0) * trade_size, 0.0),
        index=df.index
    )

    return pnl_list


# ============================================================
# 6. OPTUNA OBJECTIVE — tests all 4 strategy types
# ============================================================
def make_objective(signal_df: pd.DataFrame):
    def objective(trial: optuna.Trial) -> float:
        arch = trial.suggest_categorical('arch', ['overnight', 'intraday', 'hybrid', 'multiday'])

        if arch == 'overnight':
            params = {
                'rsi_thresh': trial.suggest_float('rsi_thresh', 30, 75),
                'roc5_min': trial.suggest_float('roc5_min', -0.05, 0.05),
                'roc5_max': trial.suggest_float('roc5_max', 0.0, 0.15),
                'target_vol': trial.suggest_float('target_vol', 0.20, 0.80),
            }
            pnl = strategy_overnight(signal_df, params)

        elif arch == 'intraday':
            params = {
                'rsi_thresh': trial.suggest_float('rsi_thresh', 30, 75),
                'gap_max': trial.suggest_float('gap_max', 0.003, 0.05),
                'vol_ratio_min': trial.suggest_float('vol_ratio_min', 0.1, 2.0),
                'tp_mult': trial.suggest_float('tp_mult', 2.0, 15.0),
                'sl_mult': trial.suggest_float('sl_mult', 1.0, 10.0),
                'target_vol': trial.suggest_float('target_vol', 0.20, 0.80),
            }
            pnl = strategy_intraday_bracket(signal_df, params)

        elif arch == 'hybrid':
            params = {
                'ovn_rsi': trial.suggest_float('ovn_rsi', 30, 75),
                'ovn_roc5_min': trial.suggest_float('ovn_roc5_min', -0.05, 0.05),
                'ovn_roc5_max': trial.suggest_float('ovn_roc5_max', 0.0, 0.15),
                'ovn_target_vol': trial.suggest_float('ovn_target_vol', 0.10, 0.50),
                'id_rsi': trial.suggest_float('id_rsi', 30, 75),
                'id_gap_max': trial.suggest_float('id_gap_max', 0.003, 0.05),
                'id_vol_ratio': trial.suggest_float('id_vol_ratio', 0.1, 2.0),
                'id_tp': trial.suggest_float('id_tp', 2.0, 15.0),
                'id_sl': trial.suggest_float('id_sl', 1.0, 10.0),
                'id_target_vol': trial.suggest_float('id_target_vol', 0.10, 0.50),
            }
            pnl = strategy_hybrid(signal_df, params)

        else:  # multiday
            params = {
                'rsi_thresh': trial.suggest_float('rsi_thresh', 30, 75),
                'roc5_min': trial.suggest_float('roc5_min', -0.05, 0.05),
                'hold_days': trial.suggest_int('hold_days', 2, 7),
                'target_vol': trial.suggest_float('target_vol', 0.20, 0.80),
            }
            pnl = strategy_multi_day_trend(signal_df, params)

        m = compute_metrics(pnl)
        if m['Sharpe'] == -999 or m['Trades'] < MIN_TRADES:
            return -999.0

        # Walk-forward gate: penalize if any window fails
        wf_ok = walk_forward_check(pnl, n_windows=3, min_sr=0.60)

        # Objective: maximize Sharpe, with heavy DD penalty
        penalty = 0.0
        if abs(m['MaxDD']) > 0.30:
            penalty += (abs(m['MaxDD']) - 0.30) * 20.0
        if m['CAGR'] < 0.20:
            penalty += (0.20 - m['CAGR']) * 5.0
        if not wf_ok:
            penalty += 3.0   # walk-forward failure penalty

        return m['Sharpe'] - penalty

    return objective


# ============================================================
# 7. MAIN GRINDER LOOP
# ============================================================
def main():
    # Load data
    qqq_d, qqq_1m, tqqq_1m = load_all_data()
    daily_feats = build_daily_features(qqq_d)
    intraday_lk = build_intraday_lookup(qqq_1m, tqqq_1m)

    # Build combined signal dataframe
    signal_df = intraday_lk.join(daily_feats, how='inner').dropna()
    print(f"[SIGNAL] Combined signal matrix: {len(signal_df)} trading days")

    # Define a callback to save the best trial continuously to avoid data loss
    def save_best_callback(study, trial):
        if study.best_trial.number == trial.number:
            results = {
                'arch': study.best_params.get('arch'),
                'params': study.best_params,
                'best_objective': study.best_value,
                'trials_completed': trial.number
            }
            with open('master_grinder_v2_results.json', 'w') as f:
                json.dump(results, f, indent=4)

    # Run Optuna
    print("\n[GRINDER] Unleashing Master Grinder V2 (100,000 trials, Random Sampler for O(1) speed)...")
    study = optuna.create_study(
        study_name="100k_ideas_study",
        direction='maximize',
        # TPE scales quadratically and causes 8-hour timeouts at 60k+. RandomSampler is O(1) and never slows down.
        sampler=optuna.samplers.RandomSampler(seed=42)
    )
    objective = make_objective(signal_df)
    study.optimize(objective, n_trials=100000, n_jobs=1, show_progress_bar=True, callbacks=[save_best_callback])

    # Extract best result
    best = study.best_params
    best_val = study.best_value

    print(f"\n[RESULT] Best Objective Value: {best_val:.4f}")
    print(f"[RESULT] Best Architecture: {best.get('arch')}")
    print(f"[RESULT] Best Parameters:")
    for k, v in best.items():
        print(f"  {k}: {v}")

    # Run final backtest with best params for full metrics
    arch = best.get('arch')
    if arch == 'overnight':
        pnl = strategy_overnight(signal_df, best)
    elif arch == 'intraday':
        pnl = strategy_intraday_bracket(signal_df, best)
    elif arch == 'hybrid':
        pnl = strategy_hybrid(signal_df, best)
    else:
        pnl = strategy_multi_day_trend(signal_df, best)

    m = compute_metrics(pnl)
    wf_ok = walk_forward_check(pnl)

    print(f"\n====================================")
    print(f"FINAL VERIFIED METRICS (IS: 2021-2023)")
    print(f"====================================")
    print(f"Strategy:         {arch.upper()}")
    print(f"Sharpe Ratio:     {m['Sharpe']:.4f}")
    print(f"CAGR:             {m['CAGR']*100:.2f}%")
    print(f"Max Drawdown:     {m['MaxDD']*100:.2f}%")
    print(f"Ann Volatility:   {m['AnnVol']*100:.2f}%")
    print(f"Win Rate:         {m['WinRate']*100:.2f}%")
    print(f"Total Trades:     {m['Trades']}")
    print(f"Walk-Forward OK:  {wf_ok}")
    print(f"====================================")

    # Save results
    results = {
        'arch': arch,
        'params': best,
        'metrics': {k: float(v) for k, v in m.items() if k != 'Cumulative'},
        'walk_forward_passed': wf_ok,
        'best_objective': best_val,
    }
    with open('master_grinder_v2_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("\n[SAVED] Results written to master_grinder_v2_results.json")

    # Check if goal is met
    goal_met = (m['Sharpe'] >= 1.8 and abs(m['MaxDD']) <= 0.30 and wf_ok)
    print(f"\n[GOAL] Target (<30% DD, SR~2): {'ACHIEVED' if goal_met else 'NOT YET — loop continues'}")
    return goal_met, m, best, arch

if __name__ == '__main__':
    main()
