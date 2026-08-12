import numpy as np
import pandas as pd


def get_optuna_params(trial):
    # Archetype: "Coiled Spring" — morning range compression relative to prior ATR,
    # combined with a mid-morning directional tilt and regime/RSI gating.
    # Idea: when the first hour trades in an unusually tight band vs recent volatility,
    # energy is stored; a positive drift into 10:30 resolves upward more often.
    return {
        'compression_ratio': trial.suggest_float('compression_ratio', 0.15, 0.90),
        'tilt_threshold':    trial.suggest_float('tilt_threshold', -0.003, 0.006),
        'rsi_low':           trial.suggest_float('rsi_low', 25.0, 55.0),
        'rsi_high':          trial.suggest_float('rsi_high', 55.0, 85.0),
        'gex_mode':          trial.suggest_categorical('gex_mode', ['any', 'positive_only', 'negative_only']),
    }


def strategy_logic(df, params):
    SLIP = 0.0010

    # --- Sizing (mandated) ---
    size = np.minimum(0.5, 0.60 / np.maximum(df['Prev_Vol_21'] * 3.0, 0.05))

    # --- Morning range compression vs prior ATR ---
    open_930 = df['QQQ_Open_930']
    morning_high = np.maximum(df['QQQ_Open_1000'], df['QQQ_Close_1030'])
    morning_low  = np.minimum(df['QQQ_Open_1000'], df['QQQ_Close_1030'])
    morning_high = np.maximum(morning_high, open_930)
    morning_low  = np.minimum(morning_low,  open_930)
    morning_range_pct = (morning_high - morning_low) / open_930

    atr_pct = np.maximum(df['Prev_ATR_pct'], 1e-6)
    compressed = morning_range_pct < (params['compression_ratio'] * atr_pct)

    # --- Directional tilt into 10:30 ---
    tilt = (df['QQQ_Close_1030'] - open_930) / open_930
    tilt_ok = tilt > params['tilt_threshold']

    # --- RSI band gate ---
    rsi_ok = (df['Prev_RSI'] >= params['rsi_low']) & (df['Prev_RSI'] <= params['rsi_high'])

    # --- GEX regime gate ---
    if params['gex_mode'] == 'positive_only':
        gex_ok = df['Prev_GEX_Regime'] > 0
    elif params['gex_mode'] == 'negative_only':
        gex_ok = df['Prev_GEX_Regime'] <= 0
    else:
        gex_ok = pd.Series(True, index=df.index)

    primary_mask = compressed & tilt_ok & rsi_ok & gex_ok

    # --- Primary trade: enter 10:31, exit 15:58 ---
    entry_am = df['TQQQ_Entry_1031'] * (1.0 + SLIP)
    exit_px  = df['TQQQ_Exit_1558'] * (1.0 - SLIP)
    
    # Intraday Margin Borrow Cost (approx 5% annualized)
    # Deducted because we are return-stacking this on top of a 100% QQQ position.
    MARGIN_RATE_ANNUAL = 0.05
    margin_cost_daily = (MARGIN_RATE_ANNUAL / 252.0) * size

    pnl_am = (exit_px / entry_am - 1.0) * size - margin_cost_daily

    pnl = pd.Series(0.0, index=df.index)
    pnl[primary_mask] = pnl_am[primary_mask]
    pnl = pnl.fillna(0.0)

    return pnl

