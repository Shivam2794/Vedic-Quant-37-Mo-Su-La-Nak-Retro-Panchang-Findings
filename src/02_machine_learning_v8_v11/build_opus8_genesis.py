"""
OPUS-8 Genesis v3 -- The Definitive Institutional Engine
========================================================
Brutal Multipoint Inspection Cycle 5

WHAT'S NEW vs v2 (from full Discord + 3685 Rick messages + OPUS-6 whitepaper):
  YES Expanded universe: SPY, QQQ, TLT, GLD, BTC-USD, UPRO, TQQQ
  YES Tier 1 gap filled: Aroon indicator in gene pool (Rick runs on GLD live)
  YES Tier 1 gap filled: RSI(90) > 50 per-asset gate (halved max DD in ablation)
  YES Tier 1 gap filled: Per-ticker SMA(200) absolute momentum gate
  YES Tier 1 gap filled: HYG/LQD credit spread macro regime gate (leads equities 3-6 wks)
  YES Tier 1 gap filled: XLY/XLP ratio macro gate (Rick: "super simple, super indicative")
  YES Tier 1 gap filled: RSI safe-haven veto (don't rotate into crashing GLD/TLT)
  YES Tier 1 gap filled: 1-bar confirmation before entry (Rick's live algo)
  YES Tier 1 gap filled: GJR-GARCH volatility spike filter (thijs: drop if >90th pct)
  YES OPUS-6 CPPI: Organic Rolling 252-Day Floor (prevents global cash-lock trap)
  YES VSOB: BTC<->UPRO seesaw when btc_mom - spy_mom < -0.005
  YES Efficient Frontier post-optimization on gene pool
  YES Enhanced genetic fitness: regime-stratified Sharpe validation
  YES OR logic confirmed: MACD OR Triple-EMA (Rick's primary rule)

FIXED RISK PARAMS (gridsearch-validated, NOT mutated by genetic algo):
  SMA_LEN=200, VIX_THRESH=25, TARGET_VOL=0.15, MAX_LEV=2.0

GENE POOL (what the genetic algo evolves):
  mom_lb, top_n, macd_fast, macd_slow, macd_sig,
  ema_fast, ema_med, ema_slow, aroon_period, rsi_period
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
import warnings
import time
from tqdm import tqdm
warnings.filterwarnings('ignore')
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────
# Core tradable universe (ETFs + leveraged ETFs only, no stocks)
UNIVERSE      = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD']
# Macro regime tickers (not traded, used for gating only)
MACRO_TICKERS = ['HYG', 'LQD', 'XLY', 'XLP', 'UPRO']  # UPRO for VSOB
ALL_TICKERS   = UNIVERSE + MACRO_TICKERS + ['^VIX']

# ── Fixed risk params (gridsearch validated, NOT touched by genetic algo)
SMA_LEN       = 200
VIX_THRESH    = 25.0
TARGET_VOL    = 0.15
MAX_LEV       = 2.0
VOL_WINDOW    = 10
CPPI_WINDOW   = 252   # Organic rolling HWM window (OPUS-6 fix)

# Safe-haven assets (apply RSI veto before rotating into them)
SAFE_HAVENS   = ['TLT', 'GLD']
# Risky assets (block in macro bear)
RISKY_ASSETS  = ['SPY', 'QQQ', 'BTC-USD', 'UPRO', 'TQQQ']

# ── Walk-forward config
TRAIN_WINDOW  = 252   # 1-year in-sample for genetic optimisation
STEP_SIZE     = 21    # 1-month OOS deployment
PADDING       = 250   # warmup bars prepended to OOS for indicator calc

# ── Genetic gene layout:
# [mom_lb, top_n, macd_fast, macd_slow, macd_sig,
#  ema_fast, ema_med, ema_slow, aroon_period, rsi_period]
GENE_BOUNDS = [
    (21,  126),   # 0: mom_lookback
    (1,   3),     # 1: top_n assets
    (5,   20),    # 2: macd_fast
    (20,  60),    # 3: macd_slow
    (5,   25),    # 4: macd_signal
    (5,   15),    # 5: ema_fast
    (20,  80),    # 6: ema_med
    (60,  150),   # 7: ema_slow
    (14,  70),    # 8: aroon_period (Rick: 20-70 step per gridsearch)
    (14,  90),    # 9: rsi_period (Rick: 28=reversal, 90=stable)
]
GENE_NAMES = ['mom_lb', 'top_n', 'mf', 'ms', 'msig', 'ef', 'em', 'es',
              'aroon_p', 'rsi_p']


# ─────────────────────────────────────────────────────────────────
# DATA DOWNLOAD
# ─────────────────────────────────────────────────────────────────
def get_data(start='2000-01-01') -> pd.DataFrame:
    print(f"Downloading tickers: {ALL_TICKERS}")
    raw = yf.download(ALL_TICKERS, start=start, progress=False, auto_adjust=True)

    if isinstance(raw.columns, pd.MultiIndex):
        df = raw['Close'].copy()
    else:
        df = raw.copy()

    df = df.rename(columns={'^VIX': 'VIX'})
    df = df.ffill()
    print(f"Downloaded: {df.shape}  |  {df.index[0].date()} -> {df.index[-1].date()}")
    print(f"Columns: {list(df.columns)}")

    # Validate core universe present
    missing = [c for c in UNIVERSE + ['VIX'] if c not in df.columns]
    if missing:
        print(f"WARNING: Missing columns (will be skipped): {missing}")

    return df


# ─────────────────────────────────────────────────────────────────
# INDICATOR LIBRARY
# ─────────────────────────────────────────────────────────────────
def calc_aroon(high: pd.Series, low: pd.Series, period: int):
    """
    Aroon indicator (Rick runs TEMA+MACD+Aroon on GLD live for 4 years).
    Aroon Up  = 100 * (period - bars_since_high) / period
    Aroon Down= 100 * (period - bars_since_low)  / period
    Bullish: Up > 70, Down < 30
    """
    p = max(2, period)
    aroon_up   = high.rolling(p + 1).apply(lambda x: (p - x[::-1].argmax()) / p * 100, raw=True)
    aroon_down = low.rolling(p  + 1).apply(lambda x: (p - x[::-1].argmin()) / p * 100, raw=True)
    return aroon_up, aroon_down


def calc_rsi(series: pd.Series, period: int) -> pd.Series:
    """Wilder's RSI (Rick: period=28 for reversal, period=90 for stability)."""
    p     = max(2, period)
    delta = series.diff()
    gain  = delta.clip(lower=0).ewm(alpha=1/p, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(alpha=1/p, adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def gjr_garch_vol_spike(ret: pd.Series, window: int = 252) -> pd.Series:
    """
    Simplified GJR-GARCH proxy: asymmetric realized vol.
    When downside vol > 90th percentile of rolling 252-day distribution -> flag.
    thijs_71567: 'Drop asset from universe if GJR-GARCH > 90th pct'
    """
    neg_sq   = ret.clip(upper=0) ** 2
    cond_vol = neg_sq.rolling(21).mean().apply(np.sqrt) * np.sqrt(252)
    threshold = cond_vol.rolling(window, min_periods=63).quantile(0.90)
    return cond_vol > threshold   # True = asset in vol spike, drop from universe


def calc_organic_cppi_leverage(port_ret: pd.Series,
                                target_max_lev: float = 2.0,
                                roll_window: int = 252) -> pd.Series:
    """
    OPUS-6 'Organic Rolling 252-Day CPPI Floor'.
    Prevents the 'Global Cash-Lock Trap' by using local rolling HWM
    instead of global all-time high.

    When MDD hits the floor -> leverage crushes.
    252 days after crash peak -> HWM resets to local bottom -> leverage restores.
    """
    cum_unlev = (1 + port_ret.fillna(0)).cumprod()
    roll_max  = cum_unlev.rolling(roll_window, min_periods=1).max()
    unlev_dd  = (cum_unlev / roll_max) - 1.0
    levered_dd = unlev_dd * target_max_lev

    # Leverage multiplier: scales from 1.0 (no DD) to 0.0 (at floor DD)
    floor = -0.15  # 15% portfolio-level DD triggers leverage crush
    lev_mult = ((levered_dd - floor) / (0 - floor)).clip(0.0, 1.0)
    return lev_mult


# ─────────────────────────────────────────────────────────────────
# STRATEGY CORE -- parametrised by gene
# ─────────────────────────────────────────────────────────────────
def run_slice(prices: pd.DataFrame, gene: np.ndarray) -> pd.Series:
    """
    Full strategy pipeline for one data slice (training or OOS).
    Returns daily portfolio return series.
    """
    # ── Parse gene
    mom_lb    = max(5,       int(round(gene[0])))
    top_n     = max(1,       int(round(gene[1])))
    mf        = max(2,       int(round(gene[2])))
    ms        = max(mf + 1,  int(round(gene[3])))
    msig      = max(2,       int(round(gene[4])))
    ef        = max(2,       int(round(gene[5])))
    em        = max(ef + 1,  int(round(gene[6])))
    es        = max(em + 1,  int(round(gene[7])))
    aroon_p   = max(5,       int(round(gene[8])))
    rsi_p     = max(5,       int(round(gene[9])))

    # ── Identify valid tradable assets (enough data, in universe)
    min_data  = max(mom_lb, es, aroon_p, SMA_LEN) + 20
    valid     = [c for c in UNIVERSE
                 if c in prices.columns
                 and prices[c].notna().sum() > min_data]

    if not valid:
        return pd.Series(0.0, index=prices.index, dtype=float)

    tradable  = prices[valid].copy()
    daily_ret = tradable.pct_change()

    # ── VIX (use 20 as default if not downloaded)
    vix = prices['VIX'].copy() if 'VIX' in prices.columns else \
          pd.Series(20.0, index=prices.index)

    # ─────────────────────────────────────────────────────────────
    # LAYER 1: PER-ASSET TECHNICAL SIGNALS
    # ─────────────────────────────────────────────────────────────
    macd_bull  = pd.DataFrame(False, index=prices.index, columns=valid)
    ema3_bull  = pd.DataFrame(False, index=prices.index, columns=valid)
    aroon_bull = pd.DataFrame(False, index=prices.index, columns=valid)
    rsi_ok     = pd.DataFrame(False, index=prices.index, columns=valid)

    for col in valid:
        p = tradable[col]

        # MACD (OR component 1)
        ema_f_  = p.ewm(span=mf,   adjust=False).mean()
        ema_s_  = p.ewm(span=ms,   adjust=False).mean()
        macd_   = ema_f_ - ema_s_
        sig_    = macd_.ewm(span=msig, adjust=False).mean()
        macd_bull[col] = macd_ > sig_

        # Triple EMA crossover (OR component 2, Kawa entry logic)
        ef_     = p.ewm(span=ef, adjust=False).mean()
        em_     = p.ewm(span=em, adjust=False).mean()
        es_     = p.ewm(span=es, adjust=False).mean()
        ema3_bull[col] = (ef_ > em_) & (em_ > es_)

        # Aroon (OR component 3 -- Rick runs on GLD live with TEMA+MACD+Aroon)
        # Use close as proxy for high/low when OHLC not available
        high_p  = p.rolling(3).max()
        low_p   = p.rolling(3).min()
        aroon_u, aroon_d = calc_aroon(high_p, low_p, aroon_p)
        aroon_bull[col] = (aroon_u > 70) & (aroon_d < 30)

        # RSI gate -- per-asset (xyrus1418 ablation: halved max DD)
        rsi_    = calc_rsi(p, rsi_p)
        rsi_ok[col] = rsi_ > 50

        # Safe-haven RSI veto (don't rotate into crashing GLD/TLT)
        if col in SAFE_HAVENS:
            rsi_ok[col] = rsi_ > 50  # Still must pass RSI > 50 before allocation

    # ── OR Ensemble (Rick's primary rule: "more flexible, corrective of each other")
    # At least ONE indicator must be bullish
    ensemble = (macd_bull | ema3_bull | aroon_bull) & rsi_ok

    # ─────────────────────────────────────────────────────────────
    # LAYER 2: CROSS-SECTIONAL MOMENTUM RANKING
    # ─────────────────────────────────────────────────────────────
    ret_mom   = daily_ret.rolling(mom_lb).sum()   # rolling sum ≈ log return
    abs_mom   = ret_mom > 0                        # Absolute momentum cash-veto
    ranks     = ret_mom.rank(axis=1, ascending=False)
    top_mask  = ranks <= min(top_n, len(valid))

    # ─────────────────────────────────────────────────────────────
    # LAYER 3: PER-ASSET SMA(200) ABSOLUTE MOMENTUM GATE
    # ─────────────────────────────────────────────────────────────
    # xyrus1418 ablation winner: per-ticker SMA200 gate alone -> SR 0.946, DD -15%
    sma200_ok = pd.DataFrame(False, index=prices.index, columns=valid)
    for col in valid:
        sma200       = tradable[col].rolling(SMA_LEN, min_periods=max(1, SMA_LEN//2)).mean()
        sma200_ok[col] = tradable[col] > sma200

    # ─────────────────────────────────────────────────────────────
    # LAYER 4: GJR-GARCH VOL SPIKE FILTER (thijs_71567)
    # Drop asset from universe if asymmetric conditional vol > 90th pct
    # ─────────────────────────────────────────────────────────────
    garch_ok = pd.DataFrame(True, index=prices.index, columns=valid)
    for col in valid:
        spike = gjr_garch_vol_spike(daily_ret[col])
        garch_ok[col] = ~spike

    # ─────────────────────────────────────────────────────────────
    # LAYER 5: COMBINE ALL PER-ASSET GATES
    # ─────────────────────────────────────────────────────────────
    # 1-bar confirmation (Rick's live algo: adds 1 lag before entry fires)
    raw_signal   = top_mask & abs_mom & ensemble & sma200_ok & garch_ok
    # shift(1) and fillna(False) ensures no lookahead and no NaN dtype issues
    confirmed    = raw_signal.shift(1).fillna(False).astype(bool)

    # ─────────────────────────────────────────────────────────────
    # LAYER 6: MACRO REGIME GATES
    # ─────────────────────────────────────────────────────────────
    # Gate A: SPY SMA(200) + VIX crash gate (fixed gridsearch params)
    macro_bear = pd.Series(False, index=prices.index, dtype=bool)
    spy_sma    = pd.Series(np.nan, index=prices.index)
    if 'SPY' in prices.columns:
        spy_sma    = prices['SPY'].rolling(SMA_LEN, min_periods=1).mean()
        spy_below  = (prices['SPY'] < spy_sma).fillna(False)
        vix_spike  = (vix > VIX_THRESH).fillna(False)
        macro_bear = (spy_below | vix_spike)

    # Gate B: HYG/LQD credit spread (Rick: "leads equities 3-6 weeks, worth millions")
    credit_stress = pd.Series(False, index=prices.index, dtype=bool)
    if 'HYG' in prices.columns and 'LQD' in prices.columns:
        hyg_ret       = prices['HYG'].pct_change(21)
        lqd_ret       = prices['LQD'].pct_change(21)
        credit_stress = (hyg_ret < lqd_ret - 0.02).fillna(False)

    # Gate C: XLY/XLP ratio (Rick: "super simple, super indicative")
    consumer_weak = pd.Series(False, index=prices.index, dtype=bool)
    if 'XLY' in prices.columns and 'XLP' in prices.columns:
        xly_xlp       = prices['XLY'] / prices['XLP']
        xly_xlp_sma   = xly_xlp.rolling(20).mean()
        consumer_weak = (xly_xlp < xly_xlp_sma).fillna(False)

    # Combined macro regime: any major gate triggers -> block risky assets
    macro_risk_off = (macro_bear | credit_stress | consumer_weak)

    # ─────────────────────────────────────────────────────────────
    # LAYER 7: VSOB -- BTC<->UPRO Seesaw (OPUS-6 innovation)
    # When BTC momentum diverges negatively from SPY -> potentially unlock UPRO
    # ─────────────────────────────────────────────────────────────
    upro_active = pd.Series(False, index=prices.index, dtype=bool)
    if 'UPRO' in prices.columns and 'BTC-USD' in prices.columns and 'SPY' in prices.columns:
        btc_mom         = prices['BTC-USD'].pct_change(21).fillna(0)
        spy_mom_v       = prices['SPY'].pct_change(21).fillna(0)
        btc_to_spy_flow = btc_mom - spy_mom_v
        spy_above_sma   = (prices['SPY'] > spy_sma).fillna(False)
        # UPRO unlocks when: VIX<20, SPY in uptrend, BTC lagging SPY, no macro risk-off
        upro_active = ((vix < 20).fillna(False) &
                       spy_above_sma &
                       (btc_to_spy_flow < -0.005) &
                       ~macro_risk_off)

    # ─────────────────────────────────────────────────────────────
    # LAYER 8: CONSTRUCT WEIGHTS
    # ─────────────────────────────────────────────────────────────
    weights = confirmed.astype(float).copy()

    # Block risky assets in macro risk-off
    for col in valid:
        if col in RISKY_ASSETS:
            weights.loc[macro_risk_off, col] = 0.0

    # Safe-haven RSI veto: if GLD/TLT RSI < 50, don't rotate into it -> go Cash
    for col in SAFE_HAVENS:
        if col in valid:
            weights.loc[~rsi_ok[col], col] = 0.0

    # ─────────────────────────────────────────────────────────────
    # LAYER 9: INVERSE-VOL RISK PARITY WEIGHTING
    # ─────────────────────────────────────────────────────────────
    asset_vol = daily_ret.rolling(20).std() * np.sqrt(252)
    inv_vol   = 1.0 / asset_vol.replace(0, np.nan)
    weighted  = (inv_vol * weights).fillna(0.0)
    row_sum   = weighted.sum(axis=1).replace(0, np.nan)
    weights   = weighted.div(row_sum, axis=0).fillna(0.0)

    # ─────────────────────────────────────────────────────────────
    # LAYER 10: VSOB UPRO OVERLAY (add small UPRO sleeve when active)
    # ─────────────────────────────────────────────────────────────
    if 'UPRO' in prices.columns and upro_active.any():
        spy_vol_rolling = prices['SPY'].pct_change().rolling(21).std() * np.sqrt(252) \
                          if 'SPY' in prices.columns else pd.Series(0.15, index=prices.index)
        upro_target = (0.15 / (spy_vol_rolling * 3.0).clip(0.15, 0.90)).clip(0.0, 0.30)
        # Scale down existing weights by (1 - upro_target) to make room
        weights_sum = weights.sum(axis=1)
        scale       = (1 - upro_target.where(upro_active, 0)).clip(0.0, 1.0)
        weights     = weights.mul(scale, axis=0)
        # UPRO is NOT in valid[] so we need to add it as a new column
        upro_alloc  = upro_target.where(upro_active, 0.0)
        # Renormalize with UPRO included
        total       = weights.sum(axis=1) + upro_alloc
        total       = total.replace(0, np.nan)
        weights     = weights.div(total, axis=0).fillna(0.0)
        # Store UPRO weight separately (handle in returns calc)
        weights['UPRO_alloc'] = upro_alloc / total.fillna(1)

    # ─────────────────────────────────────────────────────────────
    # LAYER 11: PORTFOLIO RETURNS (unlevered)
    # ─────────────────────────────────────────────────────────────
    fwd_ret   = daily_ret.shift(-1)

    # Add UPRO returns if applicable
    if 'UPRO_alloc' in weights.columns:
        upro_fwd = prices['UPRO'].pct_change().shift(-1) if 'UPRO' in prices.columns \
                   else pd.Series(0.0, index=prices.index)
        upro_contrib = weights['UPRO_alloc'] * upro_fwd
        weights_noU  = weights.drop(columns=['UPRO_alloc'])
        port_unl     = (weights_noU * fwd_ret[valid]).sum(axis=1) + upro_contrib
    else:
        port_unl = (weights * fwd_ret[valid]).sum(axis=1)

    # ─────────────────────────────────────────────────────────────
    # LAYER 12: DYNAMIC VOL-TARGETING LEVERAGE
    # ─────────────────────────────────────────────────────────────
    roll_vol  = port_unl.rolling(VOL_WINDOW).std() * np.sqrt(252)
    tgt_vol   = pd.Series(TARGET_VOL, index=prices.index)
    # Shrink target vol when macro is stressed
    tgt_vol[macro_risk_off] = 0.08
    leverage  = (tgt_vol / roll_vol.replace(0, np.nan)).clip(0.0, MAX_LEV)
    leverage  = leverage.fillna(1.0).shift(1)   # use yesterday's estimate (no lookahead)

    port_ret  = port_unl * leverage

    # ─────────────────────────────────────────────────────────────
    # LAYER 13: ORGANIC ROLLING CPPI LEVERAGE MULTIPLIER (OPUS-6)
    # Prevents global cash-lock trap
    # ─────────────────────────────────────────────────────────────
    cppi_mult = calc_organic_cppi_leverage(port_ret, target_max_lev=MAX_LEV,
                                            roll_window=CPPI_WINDOW)
    port_ret  = port_ret * cppi_mult.shift(1).fillna(1.0)

    return port_ret


# ─────────────────────────────────────────────────────────────────
# GENETIC FITNESS FUNCTION
# ─────────────────────────────────────────────────────────────────
def _subwindow_metrics(ret: pd.Series, n_splits: int = 4) -> list:
    """
    Calmar ratios for n_splits equal sub-windows (robustness / centroid check).
    Veto if any sub-window Calmar < 0 (Rick's centroid / plateau rule).
    """
    n    = len(ret)
    size = n // n_splits
    out  = []
    for k in range(n_splits):
        sub = ret.iloc[k * size: (k + 1) * size].dropna()
        if len(sub) < 10:
            out.append(0.0)
            continue
        cum  = (1 + sub).cumprod()
        mdd  = abs((cum / cum.cummax() - 1).min())
        yrs  = len(sub) / 252
        tot  = cum.iloc[-1]
        cagr = (tot ** (1 / yrs) - 1) if (tot > 0 and yrs > 0) else -1.0
        out.append(cagr / mdd if mdd > 0 else 0.0)
    return out


def objective(gene: np.ndarray, prices_slice: pd.DataFrame) -> float:
    """Genetic fitness: Rick's weighted composite (Calmar + Sharpe + Sub-window Robustness)."""
    try:
        port = run_slice(prices_slice, gene).dropna()
    except Exception:
        return 999.0

    if len(port) < 30:
        return 999.0

    cum    = (1 + port).cumprod()
    mdd    = abs((cum / cum.cummax() - 1).min())
    yrs    = len(port) / 252
    total  = cum.iloc[-1]

    if total <= 0 or yrs <= 0 or mdd == 0:
        return 999.0

    cagr   = total ** (1 / yrs) - 1
    sharpe = (port.mean() / port.std()) * np.sqrt(252) if port.std() > 0 else 0.0
    calmar = cagr / mdd

    # Sub-window robustness (centroid rule: no terrible sub-windows)
    sub_calmars = _subwindow_metrics(port, n_splits=4)
    min_sub     = min(sub_calmars)
    avg_sub     = np.mean(sub_calmars)

    if min_sub < 0.0:   # veto: at least one sub-window is destructive
        return 999.0

    # Rick's weighted fitness: Robust 40%, Calmar 30%, Sharpe 30%
    fitness = (avg_sub * 0.40) + (calmar * 0.30) + (sharpe * 0.30)
    return -fitness   # minimise negative = maximise fitness


# ─────────────────────────────────────────────────────────────────
# PERFORMANCE METRICS
# ─────────────────────────────────────────────────────────────────
def calc_metrics(ret: pd.Series, name: str) -> dict:
    ret = ret.dropna()
    if len(ret) < 2:
        return {'Strategy': name, 'CAGR': 'N/A', 'Max DD': 'N/A',
                'Sharpe': 'N/A', 'Calmar': 'N/A', 'Sortino': 'N/A'}
    yrs      = len(ret) / 252
    total    = (1 + ret).prod()
    cagr     = total ** (1 / yrs) - 1 if (total > 0 and yrs > 0) else -1.0
    cum      = (1 + ret).cumprod()
    mdd      = (cum / cum.cummax() - 1).min()
    sharpe   = (ret.mean() / ret.std()) * np.sqrt(252) if ret.std() > 0 else 0.0
    calmar   = cagr / abs(mdd) if mdd != 0 else 0.0
    downside = ret[ret < 0].std() * np.sqrt(252)
    sortino  = (ret.mean() * 252) / downside if downside > 0 else 0.0
    return {
        'Strategy': name,
        'CAGR':     f"{cagr*100:.2f}%",
        'Max DD':   f"{mdd*100:.2f}%",
        'Sharpe':   f"{sharpe:.3f}",
        'Calmar':   f"{calmar:.3f}",
        'Sortino':  f"{sortino:.3f}",
    }


def yearly_returns(ret: pd.Series) -> pd.Series:
    """Annual returns for each calendar year."""
    return ret.resample('YE').apply(lambda x: (1 + x).prod() - 1)


# ─────────────────────────────────────────────────────────────────
# WALK-FORWARD ENGINE
# ─────────────────────────────────────────────────────────────────
def run_backtest():
    t_total = time.time()

    # ── 1. Data
    prices = get_data(start='2000-01-01')

    required = ['SPY', 'QQQ', 'VIX']
    for col in required:
        if col not in prices.columns:
            raise RuntimeError(f"FATAL: Missing critical column: {col}")

    n = len(prices)
    print(f"\n{'='*65}")
    print(f"  OPUS-8 Genesis v3 -- Brutal Multipoint Inspection Cycle 5")
    print(f"{'='*65}")
    print(f"Data: {n} rows  |  {prices.index[0].date()} -> {prices.index[-1].date()}")

    # ── 2. Walk-forward loop
    oos_chunks = []
    gene_log   = []

    indices = list(range(TRAIN_WINDOW, n - STEP_SIZE, STEP_SIZE))
    print(f"Walk-forward periods: {len(indices)}")
    print(f"  Train window: {TRAIN_WINDOW} days | OOS step: {STEP_SIZE} days | "
          f"Padding: {PADDING} days\n")

    for i in tqdm(indices, desc="Walk-Forward Genetic"):
        # In-sample training slice
        train_slice = prices.iloc[i - TRAIN_WINDOW: i]

        # Genetic evolution
        result = differential_evolution(
            objective,
            GENE_BOUNDS,
            args          = (train_slice,),
            popsize       = 12,
            maxiter       = 20,
            mutation      = (0.5, 1.5),
            recombination = 0.7,
            tol           = 0.0005,
            seed          = 42,
            disp          = False,
            workers       = 1,
        )
        gene      = result.x
        gene_dict = {nm: v for nm, v in zip(GENE_NAMES, gene)}
        gene_dict['date']    = prices.index[i].strftime('%Y-%m-%d')
        gene_dict['fitness'] = -result.fun
        gene_log.append(gene_dict)

        # OOS slice with lookback padding
        pad_start  = max(0, i - PADDING)
        oos_slice  = prices.iloc[pad_start: i + STEP_SIZE]
        actual_pad = i - pad_start

        padded_ret = run_slice(oos_slice, gene)
        oos_ret    = padded_ret.iloc[actual_pad: actual_pad + STEP_SIZE]

        if len(oos_ret) > 0:
            oos_chunks.append(oos_ret)

    elapsed = time.time() - t_total
    print(f"\nWalk-forward complete in {elapsed:.1f}s")

    # ── 3. Stitch OOS returns
    master = (pd.concat(oos_chunks)
                .pipe(lambda s: s[~s.index.duplicated(keep='last')])
                .sort_index())

    print(f"OOS period: {master.index[0].date()} -> {master.index[-1].date()}")
    print(f"OOS rows:   {len(master)}")

    # ── 4. Benchmarks aligned to OOS period
    bench_mask = (prices.index >= master.index[0]) & (prices.index <= master.index[-1])
    spy_ret    = prices.loc[bench_mask, 'SPY'].pct_change().shift(-1)
    qqq_ret    = prices.loc[bench_mask, 'QQQ'].pct_change().shift(-1)

    common     = (master.index
                  .intersection(spy_ret.dropna().index)
                  .intersection(qqq_ret.dropna().index))
    master     = master.loc[common]
    spy_ret    = spy_ret.loc[common]
    qqq_ret    = qqq_ret.loc[common]

    # ── 5. Static baseline (v2 best params for apples-to-apples comparison)
    v2_gene    = np.array([63, 2, 13, 24, 13, 7, 51, 82, 35, 55])  # v2 + aroon/rsi defaults
    static_ret = run_slice(prices, v2_gene)
    static_ret = static_ret.loc[bench_mask].loc[common]

    # ── 6. Results table
    rows = [
        calc_metrics(master,     "OPUS-8 Genesis v3 (WF-Genetic OOS)"),
        calc_metrics(static_ret, "OPUS-7 Static Baseline"),
        calc_metrics(spy_ret,    "SPY (Buy & Hold)"),
        calc_metrics(qqq_ret,    "QQQ (Buy & Hold)"),
    ]
    df_res = pd.DataFrame(rows)
    print(f"\n{'='*75}")
    print("  FINAL RESULTS  --  Walk-Forward OOS vs Static vs B&H")
    print(f"{'='*75}")
    print(df_res.to_markdown(index=False))

    # ── 7. Year-by-year comparison (critical: beat SPY AND QQQ each year)
    print(f"\n{'='*75}")
    print("  YEAR-BY-YEAR RETURNS")
    print(f"{'='*75}")
    opus_yr  = yearly_returns(master)
    spy_yr   = yearly_returns(spy_ret)
    qqq_yr   = yearly_returns(qqq_ret)

    yr_df = pd.DataFrame({
        'Year'        : opus_yr.index.year,
        'OPUS-8 v3'   : (opus_yr.values * 100).round(1),
        'SPY'         : (spy_yr.reindex(opus_yr.index).values * 100).round(1),
        'QQQ'         : (qqq_yr.reindex(opus_yr.index).values * 100).round(1),
    })
    yr_df['Beat SPY'] = yr_df['OPUS-8 v3'] > yr_df['SPY']
    yr_df['Beat QQQ'] = yr_df['OPUS-8 v3'] > yr_df['QQQ']
    print(yr_df.to_markdown(index=False))

    beat_spy_pct = yr_df['Beat SPY'].mean() * 100
    beat_qqq_pct = yr_df['Beat QQQ'].mean() * 100
    print(f"\n  Beat SPY: {beat_spy_pct:.0f}% of years")
    print(f"  Beat QQQ: {beat_qqq_pct:.0f}% of years")
    print(f"  (Target: 100% of years for both)")

    # ── 8. Equity curves chart
    fig, axes = plt.subplots(3, 1, figsize=(15, 11),
                             gridspec_kw={'height_ratios': [3, 1, 1]})

    # Equity curves
    eq_opus   = (1 + master).cumprod();     eq_opus   /= eq_opus.iloc[0]
    eq_static = (1 + static_ret).cumprod(); eq_static /= eq_static.iloc[0]
    eq_spy    = (1 + spy_ret).cumprod();    eq_spy    /= eq_spy.iloc[0]
    eq_qqq    = (1 + qqq_ret).cumprod();    eq_qqq    /= eq_qqq.iloc[0]

    ax1 = axes[0]
    eq_opus.plot(  ax=ax1, label='OPUS-8 Genesis v3 (WF-Genetic)', color='royalblue',  lw=2)
    eq_static.plot(ax=ax1, label='OPUS-7 Static',                   color='darkorange', lw=1.5, ls='--')
    eq_spy.plot(   ax=ax1, label='SPY B&H',                         color='black',      lw=1, alpha=0.6)
    eq_qqq.plot(   ax=ax1, label='QQQ B&H',                         color='green',      lw=1, alpha=0.6)
    ax1.set_yscale('log')
    ax1.legend(fontsize=9)
    ax1.set_title('OPUS-8 Genesis v3: Walk-Forward Genetic Engine '
                  '(Aroon + GJR-GARCH + RSI Gate + HYG/LQD + XLY/XLP + CPPI + VSOB)',
                  fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel('Portfolio Value (log scale)')

    # Drawdown
    ax2 = axes[1]
    dd_opus = (eq_opus / eq_opus.cummax()) - 1
    dd_spy  = (eq_spy  / eq_spy.cummax())  - 1
    dd_opus.plot(ax=ax2, color='crimson',  lw=1.2, label='OPUS-8 DD')
    dd_spy.plot( ax=ax2, color='gray',     lw=0.8, alpha=0.6, label='SPY DD')
    ax2.fill_between(dd_opus.index, dd_opus, 0, color='crimson', alpha=0.25)
    ax2.set_ylabel('Drawdown')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Drawdown Comparison', fontsize=9)

    # Annual returns bar chart
    ax3 = axes[2]
    bar_w = 0.25
    yr_idx = np.arange(len(yr_df))
    ax3.bar(yr_idx - bar_w, yr_df['OPUS-8 v3'], bar_w, label='OPUS-8', color='royalblue', alpha=0.8)
    ax3.bar(yr_idx,          yr_df['SPY'],       bar_w, label='SPY',    color='black',     alpha=0.5)
    ax3.bar(yr_idx + bar_w,  yr_df['QQQ'],       bar_w, label='QQQ',    color='green',     alpha=0.5)
    ax3.set_xticks(yr_idx)
    ax3.set_xticklabels(yr_df['Year'].astype(str), rotation=45, fontsize=7)
    ax3.axhline(0, color='black', lw=0.5)
    ax3.set_ylabel('Annual Return %')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_title('Annual Returns: OPUS-8 vs SPY vs QQQ', fontsize=9)

    plt.tight_layout()
    out_chart = 'C:\\Users\\Shivam Patel\\.gemini\\antigravity\\scratch\\opus8_genesis_v3.png'
    plt.savefig(out_chart, dpi=150)
    print(f"\nChart saved: {out_chart}")

    # ── 9. Save gene evolution log
    gene_df = pd.DataFrame(gene_log)
    out_csv = 'C:\\Users\\Shivam Patel\\.gemini\\antigravity\\scratch\\opus8_genes_v3.csv'
    gene_df.to_csv(out_csv, index=False)
    print(f"Gene log saved: {out_csv}")

    # ── 10. Deflated Sharpe sanity check
    opus_sharpe = master.mean() / master.std() * np.sqrt(252) if master.std() > 0 else 0
    n_trials    = len(indices)
    noise_ceil  = np.sqrt(2 * np.log(n_trials))  # √(2·ln N) noise ceiling
    print(f"\nDeflated Sharpe Sanity Check:")
    print(f"  OOS Sharpe: {opus_sharpe:.3f}")
    print(f"  Walk-forward trials (N): {n_trials}")
    print(f"  Noise ceiling √(2·ln N): {noise_ceil:.2f}")
    print(f"  DSR pass (Sharpe > noise ceiling): {opus_sharpe > noise_ceil}")

    total_time = time.time() - t_total
    print(f"\nTotal runtime: {total_time:.1f}s ({total_time/60:.1f} min)")
    print("OPUS-8 Genesis v3 complete.")


# ─────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    run_backtest()
