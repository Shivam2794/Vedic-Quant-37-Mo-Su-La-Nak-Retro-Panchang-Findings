import numpy as np
import pandas as pd


def get_optuna_params(trial):
    return {
        # position of 15:00 close inside the day's range below which we consider it a "washed out" dip
        'range_pos_max': trial.suggest_float('range_pos_max', 0.30, 0.65),
        # minimum morning strength (10:00 open vs 9:30 open) required to trust the snapback
        'am_mom_min': trial.suggest_float('am_mom_min', -0.006, 0.004),
        # RSI ceiling: avoid buying dips when prior day was already overbought
        'rsi_max': trial.suggest_float('rsi_max', 55.0, 80.0),
        # ATR floor: require some minimum prior volatility so the snapback has juice
        'atr_min': trial.suggest_float('atr_min', 0.000, 0.012),
        # secondary morning-session trade: buy 10:31 if 10:30 close reclaimed 9:30 open by this margin
        'reclaim_min': trial.suggest_float('reclaim_min', -0.004, 0.006),
        # blend weight between afternoon snapback leg and morning reclaim leg
        'leg_weight': trial.suggest_float('leg_weight', 0.3, 0.7),
    }


def strategy_logic(df, params):
    slip = 0.0010
    size = np.minimum(0.5, 0.60 / np.maximum(df['Prev_Vol_21'] * 3.0, 0.05))

    # --- Shared intraday geometry ---
    rng = (df['ID_High'] - df['ID_Low']).replace(0, np.nan)
    # where does the 15:00 QQQ close sit within the intraday range? (0 = at low, 1 = at high)
    range_pos = (df['QQQ_Close_1500'] - df['ID_Low']) / rng
    range_pos = range_pos.fillna(0.5)

    # morning momentum: 9:30 -> 10:00 drift
    am_mom = (df['QQQ_Open_1000'] - df['QQQ_Open_930']) / df['QQQ_Open_930']
    # reclaim: 10:30 close vs 9:30 open
    reclaim = (df['QQQ_Close_1030'] - df['QQQ_Open_930']) / df['QQQ_Open_930']

    # ================= LEG A: Late-Day Washout Snapback =================
    # Price got pushed to the lower part of the day's range by 15:00, but the
    # morning tape was constructive and prior day wasn't overbought.
    # Buy 15:01, exit 15:58 (final-hour mean reversion pop).
    mask_a = (
        (range_pos <= params['range_pos_max']) &
        (am_mom >= params['am_mom_min']) &
        (df['Prev_RSI'] <= params['rsi_max']) &
        (df['Prev_ATR_pct'] >= params['atr_min'])
    )
    entry_a = df['TQQQ_Entry_1501'] * (1.0 + slip)
    exit_a = df['TQQQ_Exit_1558'] * (1.0 - slip)
    ret_a = (exit_a - entry_a) / entry_a
    pnl_a = pd.Series(np.where(mask_a, ret_a * size, 0.0), index=df.index)

    # ================= LEG B: Morning Open-Reclaim Continuation =================
    # First hour closed back above (or near) the 9:30 open -> intraday trend day
    # candidate. Buy 10:31, exit 15:58 riding the session.
    mask_b = (
        (reclaim >= params['reclaim_min']) &
        (df['Prev_RSI'] <= params['rsi_max']) &
        (df['Prev_ATR_pct'] >= params['atr_min'])
    )
    entry_b = df['TQQQ_Entry_1031'] * (1.0 + slip)
    exit_b = df['TQQQ_Exit_1558'] * (1.0 - slip)
    ret_b = (exit_b - entry_b) / entry_b
    pnl_b = pd.Series(np.where(mask_b, ret_b * size, 0.0), index=df.index)

    w = params['leg_weight']
    pnl = w * pnl_a + (1.0 - w) * pnl_b
    pnl = pnl.fillna(0.0)
    pnl.index = df.index
    return pnl
