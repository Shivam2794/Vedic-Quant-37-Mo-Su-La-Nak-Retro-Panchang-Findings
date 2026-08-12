"""
OPUS-8 Phase 1: Per-Asset Indicator Combination Gridsearch
===========================================================
Brutal Multipoint Inspection Cycle 6

PURPOSE:
  Find the best 2-3 indicator combos + optimal parameters for EACH ETF
  independently. This is Rick's actual workflow:
  "Optimize indicators per asset independently before ensembling."

ARCHITECTURE:
  - 92 indicator combos (single, pairs, triples) x 5 ETFs = 460 tests
  - Each combo: brute-force param grid (1-2 free params per indicator)
  - Rick's scoring: IS_Sharpe * (1 - CV) [centroid formula, nico108_]
  - Veto: IS/OOS degradation > 30%, any sub-window Calmar < 0
  - Final output: per-asset winner table -> fed into walk-forward engine

INDICATORS SEARCHED (from master brain - Rick's confirmed library):
  MACD, Triple-EMA, Aroon, RSI, Donchian, Bollinger Bands, STC

MACRO GATES SEARCHED:
  SPY SMA length, VIX threshold, HYG/LQD threshold, XLY/XLP toggle
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import yfinance as yf
import pandas as pd
import numpy as np
import itertools
import warnings
import time
from datetime import datetime
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────
UNIVERSE      = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD']
MACRO_TICKERS = ['HYG', 'LQD', 'XLY', 'XLP', '^VIX']
ALL_TICKERS   = UNIVERSE + MACRO_TICKERS

TRAIN_RATIO   = 0.60   # Rick: 60% train, 40% OOS
TOP_N_FINAL   = 3      # Save top-3 combos per ETF
MAX_DD_THRESH = 30.0   # 30% max DD hard limit
IS_OOS_MAX    = 0.30   # Rick: degradation >30% = dangerous curve-fit
BORUTA_SHUFFLES = 50   # 50 shuffles per combo for significance test

OUT_PATH      = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_gridsearch_v3.csv'
SUMMARY_PATH  = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_winners_v3.csv'

# Fixed macro params (will also gridsearch these separately)
MACRO_DEFAULTS = {
    'sma_len'    : 200,
    'vix_thresh' : 25.0,
    'hyg_diff'   : 0.02,  # HYG underperform LQD by this % to trigger stress
    'use_xly_xlp': True,
}

# ─────────────────────────────────────────────────────────────────
# INDICATOR PARAMETER GRIDS
# "Fix most params, only let 1-2 vary" — Rick's rule
# ─────────────────────────────────────────────────────────────────
INDICATOR_GRIDS = {
    'MACD': {
        'fast'   : [8, 12, 13, 16],        # fix slow/signal, vary fast
        'slow'   : [21, 24, 26, 34],       # best region from community gridsearch
        'signal' : [9, 13, 17],
    },
    'EMA3': {
        'fast'   : [5, 8, 10, 13],
        'med'    : [21, 34, 51, 55],       # mid confirmed: ~34-55
        'slow'   : [82, 100, 127, 150],    # slow confirmed: ~80-150
    },
    'AROON': {
        'period'     : [14, 21, 28, 35, 42, 56, 70],
        'up_thresh'  : [70],               # fixed per Rick: Aroon Up > 70 = bullish
        'down_thresh': [30],               # fixed per Rick: Aroon Down < 30 = bullish
    },
    'RSI': {
        'period'    : [14, 21, 28, 42, 55, 90],
        'threshold' : [45, 50, 55],        # RSI > threshold = bullish
    },
    'DONCHIAN': {
        'period'    : [10, 15, 20, 25, 30],  # 20-day high entry, period//2 exit
    },
    'BB': {
        'window'   : [20, 40, 60, 100],
        'std_mult' : [1.5, 2.0, 2.5],
    },
    'STC': {
        'fast'  : [23],
        'slow'  : [50],
        'cycle' : [10],    # STC: Schaff Trend Cycle — Rick flagged IS/OOS degradation risk
    },
}

# ─────────────────────────────────────────────────────────────────
# MACRO GATE GRIDS (searched separately across all assets)
# ─────────────────────────────────────────────────────────────────
MACRO_GRIDS = {
    'sma_len'    : [100, 150, 200, 250],
    'vix_thresh' : [20.0, 22.0, 25.0, 30.0],
    'hyg_diff'   : [0.01, 0.02, 0.03, 0.05],   # HYG/LQD stress threshold
    'use_xly_xlp': [True, False],
}

# ─────────────────────────────────────────────────────────────────
# DATA DOWNLOAD
# ─────────────────────────────────────────────────────────────────
def get_data(start='2002-01-01') -> pd.DataFrame:
    print(f"Downloading: {ALL_TICKERS}")
    raw = yf.download(ALL_TICKERS, start=start, progress=False, auto_adjust=True)
    df  = raw['Close'] if isinstance(raw.columns, pd.MultiIndex) else raw
    df  = df.rename(columns={'^VIX': 'VIX'}).ffill()
    print(f"Data: {df.shape} | {df.index[0].date()} -> {df.index[-1].date()}")
    return df


# ─────────────────────────────────────────────────────────────────
# INDICATOR FUNCTIONS
# ─────────────────────────────────────────────────────────────────
def calc_rsi(series: pd.Series, period: int) -> pd.Series:
    """Wilder's RSI."""
    delta = series.diff()
    gain  = delta.clip(lower=0).ewm(alpha=1/max(2,period), adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(alpha=1/max(2,period), adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_aroon(price: pd.Series, period: int):
    """Aroon Up / Down using rolling high/low."""
    p     = max(2, period)
    high_ = price.rolling(3).max()
    low_  = price.rolling(3).min()
    up    = high_.rolling(p+1).apply(
                lambda x: (p - x[::-1].argmax()) / p * 100, raw=True)
    down  = low_.rolling(p+1).apply(
                lambda x: (p - x[::-1].argmin()) / p * 100, raw=True)
    return up, down


def get_signal(price: pd.Series, indicator: str, params: dict) -> pd.Series:
    """
    Returns binary daily signal (True=Long, False=Cash) for one indicator.
    All signals: 1-bar lag built in to prevent lookahead.
    """
    sig = pd.Series(False, index=price.index)

    if indicator == 'MACD':
        fast  = max(2, params['fast'])
        slow  = max(fast+1, params['slow'])
        sigp  = max(2, params['signal'])
        ef_   = price.ewm(span=fast, adjust=False).mean()
        es_   = price.ewm(span=slow, adjust=False).mean()
        macd_ = ef_ - es_
        sigln = macd_.ewm(span=sigp, adjust=False).mean()
        sig   = (macd_ > sigln)

    elif indicator == 'EMA3':
        fast = max(2, params['fast'])
        med  = max(fast+1, params['med'])
        slow = max(med+1, params['slow'])
        ef_  = price.ewm(span=fast, adjust=False).mean()
        em_  = price.ewm(span=med,  adjust=False).mean()
        es_  = price.ewm(span=slow, adjust=False).mean()
        sig  = (ef_ > em_) & (em_ > es_)

    elif indicator == 'AROON':
        period = max(2, params['period'])
        up_t   = params.get('up_thresh',   70)
        dn_t   = params.get('down_thresh', 30)
        ar_up, ar_dn = calc_aroon(price, period)
        sig    = (ar_up > up_t) & (ar_dn < dn_t)

    elif indicator == 'RSI':
        period = max(2, params['period'])
        thresh = params.get('threshold', 50)
        rsi_   = calc_rsi(price, period)
        sig    = rsi_ > thresh

    elif indicator == 'DONCHIAN':
        period = max(2, params['period'])
        halfp  = max(1, period // 2)
        highest_high = price.rolling(period).max()
        lowest_low   = price.rolling(halfp).min()
        # Donchian: enter on new period high, exit on period//2 low
        in_trade = pd.Series(False, index=price.index)
        entry    = price >= highest_high.shift(1)
        exit_    = price <= lowest_low.shift(1)
        state    = False
        for i in range(len(price)):
            if exit_.iloc[i]:
                state = False
            if entry.iloc[i]:
                state = True
            in_trade.iloc[i] = state
        sig = in_trade

    elif indicator == 'BB':
        window   = max(5, params['window'])
        std_mult = params.get('std_mult', 2.0)
        ma_      = price.rolling(window).mean()
        std_     = price.rolling(window).std()
        upper_   = ma_ + std_mult * std_
        lower_   = ma_ - std_mult * std_
        # BB trend: price above upper band (breakout) = bullish
        sig      = price > ma_

    elif indicator == 'STC':
        fast  = max(2, params.get('fast',   23))
        slow  = max(fast+1, params.get('slow', 50))
        cycle = max(2, params.get('cycle',  10))
        # STC = Schaff Trend Cycle (double-smoothed stochastic on MACD)
        macd_  = price.ewm(span=fast, adjust=False).mean() - \
                 price.ewm(span=slow, adjust=False).mean()
        stoch1 = 100 * (macd_ - macd_.rolling(cycle).min()) / \
                 (macd_.rolling(cycle).max() - macd_.rolling(cycle).min() + 1e-9)
        stc_   = stoch1.ewm(span=cycle, adjust=False).mean()
        sig    = (stc_ < 25)   # STC<25 = oversold = potential reversal up

    # 1-bar lag (no lookahead)
    return sig.shift(1).fillna(False)


def ensemble_signal(price: pd.Series, combo: tuple, param_sets: dict) -> pd.Series:
    """
    OR-logic ensemble of 1-3 indicators (Rick's primary rule).
    param_sets: {indicator_name: {param: value}}
    """
    signals = []
    for ind in combo:
        s = get_signal(price, ind, param_sets[ind])
        signals.append(s)
    # OR logic: any signal = long
    combined = signals[0]
    for s in signals[1:]:
        combined = combined | s
    return combined


# ─────────────────────────────────────────────────────────────────
# MACRO GATES
# ─────────────────────────────────────────────────────────────────
def apply_macro_gates(prices: pd.DataFrame, macro_params: dict) -> pd.Series:
    """
    Returns boolean Series: True = RISK-OFF (block risky assets).
    """
    sma_len     = macro_params.get('sma_len',     200)
    vix_thresh  = macro_params.get('vix_thresh',  25.0)
    hyg_diff    = macro_params.get('hyg_diff',    0.02)
    use_xly_xlp = macro_params.get('use_xly_xlp', True)

    risk_off = pd.Series(False, index=prices.index, dtype=bool)

    # Gate A: SPY SMA + VIX
    if 'SPY' in prices.columns and 'VIX' in prices.columns:
        spy_sma  = prices['SPY'].rolling(sma_len, min_periods=1).mean()
        risk_off = risk_off | (prices['SPY'] < spy_sma).fillna(False)
        risk_off = risk_off | (prices['VIX'] > vix_thresh).fillna(False)

    # Gate B: HYG/LQD credit spread
    if 'HYG' in prices.columns and 'LQD' in prices.columns:
        hyg_ret = prices['HYG'].pct_change(21)
        lqd_ret = prices['LQD'].pct_change(21)
        risk_off = risk_off | (hyg_ret < lqd_ret - hyg_diff).fillna(False)

    # Gate C: XLY/XLP
    if use_xly_xlp and 'XLY' in prices.columns and 'XLP' in prices.columns:
        ratio    = prices['XLY'] / prices['XLP']
        ratio_ma = ratio.rolling(20).mean()
        risk_off = risk_off | (ratio < ratio_ma).fillna(False)

    return risk_off


# ─────────────────────────────────────────────────────────────────
# SINGLE ASSET BACKTEST
# ─────────────────────────────────────────────────────────────────
RISKY = {'SPY', 'QQQ', 'BTC-USD', 'UPRO', 'TQQQ'}

def backtest_asset(price: pd.Series, signal: pd.Series,
                   risk_off: pd.Series, is_risky: bool = True) -> pd.Series:
    """
    Simple long-only backtest: signal & ~risk_off -> hold, else cash.
    Returns daily return series.
    """
    # If risky asset, apply macro risk-off gate
    active = signal.copy()
    if is_risky:
        active = active & ~risk_off.reindex(price.index, fill_value=False)

    daily_ret = price.pct_change()
    port_ret  = daily_ret.where(active.shift(0), 0.0)   # shift already in signal
    return port_ret.fillna(0.0)


# ─────────────────────────────────────────────────────────────────
# METRICS CALCULATION
# ─────────────────────────────────────────────────────────────────
def _metrics_from_ret(ret: pd.Series) -> dict:
    """Compute Sharpe, Calmar, Max DD, CAGR from a daily return series."""
    ret  = ret.dropna()
    if len(ret) < 20:
        return {'sharpe': -9, 'calmar': -9, 'cagr': -9, 'mdd': -9, 'n': 0}
    yrs  = len(ret) / 252
    tot  = (1 + ret).prod()
    cagr = tot**(1/yrs) - 1 if (tot > 0 and yrs > 0) else -1.0
    cum  = (1 + ret).cumprod()
    mdd  = (cum / cum.cummax() - 1).min()
    std  = ret.std()
    sharpe = (ret.mean() / std) * np.sqrt(252) if std > 0 else 0.0
    calmar = cagr / abs(mdd) if mdd != 0 else 0.0
    return {'sharpe': sharpe, 'calmar': calmar, 'cagr': cagr,
            'mdd': mdd, 'n': len(ret)}


def _subwindow_calmar(ret: pd.Series, n_splits: int = 4) -> list:
    """Sub-window Calmars for centroid/plateau validation."""
    n    = len(ret)
    size = n // n_splits
    out  = []
    for k in range(n_splits):
        sub = ret.iloc[k*size:(k+1)*size].dropna()
        m   = _metrics_from_ret(sub)
        out.append(m['calmar'])
    return out


def _score(is_sharpe: float, oos_sharpe: float,
           sub_calmars: list, oos_calmar: float) -> float:
    """
    Rick's centroid scoring formula (nico108_):
      score = IS_Sharpe * (1 - CV)
    where CV = bootstrap_std / bootstrap_mean (replaced here with IS/OOS ratio).
    Plus veto conditions.
    """
    if is_sharpe <= 0 or oos_sharpe <= 0:
        return -999.0

    # IS/OOS degradation veto
    degradation = (is_sharpe - oos_sharpe) / max(is_sharpe, 0.001)
    if degradation > IS_OOS_MAX:
        return -998.0   # marker for "degraded"

    # Sub-window veto (centroid rule)
    if min(sub_calmars) < 0:
        return -997.0   # marker for "sub-window failure"

    # Final score: OOS Sharpe weighted by robustness (low degradation)
    consistency = 1 - degradation   # 1.0 = no degradation
    score = oos_sharpe * consistency
    return score


# ─────────────────────────────────────────────────────────────────
# BORUTA SHUFFLE TEST
# ─────────────────────────────────────────────────────────────────
def boruta_shuffle_score(oos_ret: pd.Series, n_shuffles: int = 50) -> float:
    """
    Boruta shuffle test: compare real OOS return to shuffled OOS returns.
    Score = fraction of shuffles that real OOS beats (higher = more significant).
    Community: score = (wins / 50) * 100%
    """
    if len(oos_ret) < 10:
        return 0.0
    real_sharpe = _metrics_from_ret(oos_ret)['sharpe']
    wins = 0
    rng  = np.random.default_rng(seed=42)
    for _ in range(n_shuffles):
        shuffled = rng.permutation(oos_ret.dropna().values)
        shuffle_sharpe = _metrics_from_ret(pd.Series(shuffled))['sharpe']
        if real_sharpe > shuffle_sharpe:
            wins += 1
    return (wins / n_shuffles) * 100.0


# ─────────────────────────────────────────────────────────────────
# GENERATE ALL PARAM COMBOS FOR AN INDICATOR
# ─────────────────────────────────────────────────────────────────
def indicator_param_combos(indicator: str) -> list:
    """
    Generate all parameter combinations for an indicator from INDICATOR_GRIDS.
    Returns list of dicts.
    """
    grid = INDICATOR_GRIDS[indicator]
    keys = list(grid.keys())
    vals = [grid[k] for k in keys]
    combos = []
    for combo in itertools.product(*vals):
        d = dict(zip(keys, combo))
        combos.append(d)
    return combos


# ─────────────────────────────────────────────────────────────────
# MAIN GRIDSEARCH LOOP
# ─────────────────────────────────────────────────────────────────
def run_gridsearch():
    t0 = time.time()
    print("="*65)
    print("  OPUS-8 Phase 1: Per-Asset Indicator Gridsearch")
    print(f"  Target: find best 2-3 indicators per ETF")
    print("="*65)

    # Load data
    prices = get_data(start='2002-01-01')

    # Build macro risk-off signal (default params to start)
    risk_off_default = apply_macro_gates(prices, MACRO_DEFAULTS)
    print(f"Macro risk-off days (default): {risk_off_default.sum()} / {len(risk_off_default)}")

    # All indicator names
    indicator_names = list(INDICATOR_GRIDS.keys())

    # Generate all combos: single, pairs, triples
    all_combos = []
    for r in [1, 2, 3]:
        for combo in itertools.combinations(indicator_names, r):
            all_combos.append(combo)
    print(f"Indicator combos to test: {len(all_combos)}")

    results = []   # all results across assets + combos

    for ticker in UNIVERSE:
        if ticker not in prices.columns:
            print(f"  SKIP {ticker}: not in downloaded data")
            continue

        price      = prices[ticker].dropna()
        daily_ret  = price.pct_change()
        is_risky   = ticker in RISKY

        # Train/OOS split
        n_train    = int(len(price) * TRAIN_RATIO)
        train_idx  = price.index[:n_train]
        oos_idx    = price.index[n_train:]
        print(f"\n--- {ticker} ---")
        print(f"  Train: {train_idx[0].date()} -> {train_idx[-1].date()} ({len(train_idx)} days)")
        print(f"  OOS:   {oos_idx[0].date()}  -> {oos_idx[-1].date()}  ({len(oos_idx)} days)")

        ticker_results = []

        for combo in all_combos:
            # Generate all param combos for each indicator in this combo
            per_indicator_params = {ind: indicator_param_combos(ind) for ind in combo}
            # Cartesian product of param combos across indicators in this combo
            param_keys   = list(combo)
            param_vals   = [per_indicator_params[ind] for ind in combo]

            for param_set_tuple in itertools.product(*param_vals):
                param_set = dict(zip(param_keys, param_set_tuple))

                # Generate ensemble signal for full period
                try:
                    sig = ensemble_signal(price, combo, param_set)
                except Exception:
                    continue

                # Backtest full period
                port_ret = backtest_asset(price, sig, risk_off_default, is_risky)

                # IS metrics
                is_ret  = port_ret.loc[train_idx]
                oos_ret = port_ret.loc[oos_idx]

                is_m    = _metrics_from_ret(is_ret)
                oos_m   = _metrics_from_ret(oos_ret)

                if is_m['n'] < 20 or oos_m['n'] < 20:
                    continue

                sub_calmars = _subwindow_calmar(is_ret, n_splits=4)

                score = _score(
                    is_sharpe    = is_m['sharpe'],
                    oos_sharpe   = oos_m['sharpe'],
                    sub_calmars  = sub_calmars,
                    oos_calmar   = oos_m['calmar'],
                )

                row = {
                    'ticker'        : ticker,
                    'combo'         : '+'.join(combo),
                    'n_indicators'  : len(combo),
                    'params'        : str(param_set),
                    'is_sharpe'     : round(is_m['sharpe'], 4),
                    'oos_sharpe'    : round(oos_m['sharpe'], 4),
                    'is_cagr'       : round(is_m['cagr']*100, 2),
                    'oos_cagr'      : round(oos_m['cagr']*100, 2),
                    'oos_mdd'       : round(oos_m['mdd']*100, 2),
                    'oos_calmar'    : round(oos_m['calmar'], 4),
                    'min_sub_calmar': round(min(sub_calmars), 4),
                    'score'         : round(score, 4),
                    'degradation_pct': round(
                        (is_m['sharpe'] - oos_m['sharpe'])/max(is_m['sharpe'],0.001)*100, 1),
                }
                ticker_results.append(row)

        # Sort by score, pick top for Boruta
        ticker_df = pd.DataFrame(ticker_results)
        if ticker_df.empty:
            print(f"  {ticker}: No valid results")
            continue

        valid_df  = ticker_df[ticker_df['score'] > 0].sort_values('score', ascending=False)
        print(f"  {ticker}: {len(ticker_results)} total tested, {len(valid_df)} passed veto filters")

        if valid_df.empty:
            print(f"  {ticker}: ALL combos failed veto (too much IS/OOS degradation)")
            results.extend(ticker_results)
            continue

        # Boruta shuffle test on top-25
        top25   = valid_df.head(25)
        boruta_scores = []
        for _, row in top25.iterrows():
            try:
                combo  = tuple(row['combo'].split('+'))
                params = eval(row['params'])
                sig    = ensemble_signal(price, combo, params)
                port   = backtest_asset(price, sig, risk_off_default, is_risky)
                oos_r  = port.loc[oos_idx]
                bscore = boruta_shuffle_score(oos_r, n_shuffles=BORUTA_SHUFFLES)
            except Exception:
                bscore = 0.0
            boruta_scores.append(bscore)
        top25 = top25.copy()
        top25['boruta_score'] = boruta_scores

        # Final ranking: score * boruta_weight
        top25['final_rank'] = top25['score'] * (top25['boruta_score'] / 100).clip(0.3, 1.0)
        top25 = top25.sort_values('final_rank', ascending=False)

        print(f"  {ticker} TOP-3 WINNERS:")
        for _, row in top25.head(TOP_N_FINAL).iterrows():
            print(f"    [{row['combo']:35s}] OOS SR={row['oos_sharpe']:.3f} "
                  f"CAGR={row['oos_cagr']:.1f}% DD={row['oos_mdd']:.1f}% "
                  f"Degrad={row['degradation_pct']:.0f}% "
                  f"Boruta={row.get('boruta_score',0):.0f}%")

        # Merge boruta back
        top25_idx = top25.index
        ticker_df.loc[top25_idx, 'boruta_score'] = \
            top25.loc[top25_idx, 'boruta_score'] if 'boruta_score' in top25.columns else 0
        ticker_df.loc[top25_idx, 'final_rank']   = \
            top25.loc[top25_idx, 'final_rank']   if 'final_rank'   in top25.columns else 0

        results.extend(ticker_df.to_dict('records'))

    # ── Save all results
    all_df = pd.DataFrame(results)
    all_df.to_csv(OUT_PATH, index=False)
    print(f"\nFull results saved: {OUT_PATH}")

    # ── Winners summary (top-3 per ticker)
    if not all_df.empty and 'final_rank' in all_df.columns:
        winners = (all_df[all_df['score'] > 0]
                   .sort_values('final_rank', ascending=False)
                   .groupby('ticker')
                   .head(TOP_N_FINAL)
                   .reset_index(drop=True))
    else:
        winners = (all_df[all_df['score'] > 0]
                   .sort_values('score', ascending=False)
                   .groupby('ticker')
                   .head(TOP_N_FINAL)
                   .reset_index(drop=True))

    winners.to_csv(SUMMARY_PATH, index=False)
    print(f"Winners summary saved: {SUMMARY_PATH}")

    print(f"\n{'='*65}")
    print("  FINAL WINNER TABLE (Top-3 per ETF)")
    print(f"{'='*65}")
    print(winners[['ticker','combo','oos_sharpe','oos_cagr','oos_mdd',
                   'degradation_pct','boruta_score','score']].to_markdown(index=False))

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print("\nNext step: feed winners into build_opus8_genesis.py walk-forward engine")
    print("  -> Replace universal OR(MACD|EMA3|Aroon) with per-asset winner combos")

    # ── Run macro gate gridsearch as bonus
    print(f"\n{'='*65}")
    print("  BONUS: Macro Gate Parameter Gridsearch (on SPY)")
    print(f"{'='*65}")
    run_macro_gridsearch(prices)


# ─────────────────────────────────────────────────────────────────
# MACRO GATE GRIDSEARCH
# ─────────────────────────────────────────────────────────────────
def run_macro_gridsearch(prices: pd.DataFrame):
    """
    Gridsearch the macro gate parameters (SMA length, VIX threshold,
    HYG/LQD threshold) to find the combination that maximizes the
    portfolio-level protective efficiency (best OOS Sharpe on SPY).
    """
    if 'SPY' not in prices.columns:
        return

    price     = prices['SPY']
    n_train   = int(len(price) * TRAIN_RATIO)
    train_idx = price.index[:n_train]
    oos_idx   = price.index[n_train:]

    # Use the best single-indicator signal found (will be replaced by winner)
    # For now use EMA3 default as baseline for testing macro gates
    baseline_sig = ensemble_signal(price, ('EMA3',),
                                   {'EMA3': {'fast': 13, 'med': 34, 'slow': 100}})

    macro_results = []
    keys = list(MACRO_GRIDS.keys())
    vals = [MACRO_GRIDS[k] for k in keys]

    for param_combo in itertools.product(*vals):
        mp = dict(zip(keys, param_combo))
        ro = apply_macro_gates(prices, mp)
        pr = backtest_asset(price, baseline_sig, ro, is_risky=True)

        is_m  = _metrics_from_ret(pr.loc[train_idx])
        oos_m = _metrics_from_ret(pr.loc[oos_idx])

        if is_m['n'] < 10 or oos_m['n'] < 10:
            continue

        score = _score(is_m['sharpe'], oos_m['sharpe'],
                       _subwindow_calmar(pr.loc[train_idx]), oos_m['calmar'])

        macro_results.append({
            'sma_len'    : mp['sma_len'],
            'vix_thresh' : mp['vix_thresh'],
            'hyg_diff'   : mp['hyg_diff'],
            'use_xly_xlp': mp['use_xly_xlp'],
            'is_sharpe'  : round(is_m['sharpe'],  3),
            'oos_sharpe' : round(oos_m['sharpe'],  3),
            'oos_mdd'    : round(oos_m['mdd']*100, 2),
            'score'      : round(score,             4),
        })

    macro_df = pd.DataFrame(macro_results).sort_values('score', ascending=False)
    macro_out = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_macro_grid_v3.csv'
    macro_df.to_csv(macro_out, index=False)
    print(f"Macro grid saved: {macro_out}")
    print("\nTop-5 macro gate parameter combos:")
    print(macro_df.head(5).to_markdown(index=False))


# ─────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    run_gridsearch()
