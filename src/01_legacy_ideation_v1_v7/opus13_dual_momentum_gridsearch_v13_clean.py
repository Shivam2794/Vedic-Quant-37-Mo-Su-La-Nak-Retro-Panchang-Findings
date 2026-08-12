"""
opus13_dual_momentum_gridsearch_v13.py  --  BRUTAL MULTIPOINT AUDIT / ABSOLUTE SURRENDER REBUILD

Dual-Momentum (relative + ABSOLUTE) regime strategy grid search over:
    SMA window x ERC lookback x hysteresis buffer x momentum window

Audit fixes applied (every historical fatal bug closed):
  [FIX 1] NO .fillna(0) anywhere. Missing history stays NaN. An asset can only receive
          weight once it has `lookback` consecutive finite returns => zero phantom assets
          before inception (TQQQ/UPRO/GLD/TLT/QQQ all respected).
  [FIX 2] TRUE Sharpe = mean(excess daily)/std(excess daily, ddof=1) * sqrt(252),
          NOT CAGR/vol. Excess computed vs the daily risk-free series.
  [FIX 3] Transaction costs on ACTUAL traded notional (leverage-scaled positions,
          per-asset bps) + explicit BORROWING SPREAD on any exposure above 1.0 and
          cash interest credited on un-invested capital.
  [FIX 4] ABSOLUTE momentum filter applied to BOTH offensive (SPY/QQQ) AND defensive
          (GLD/TLT) sleeves; assets failing vs the risk-free compounded return over the
          same lookback are dropped to CASH.
  [FIX 5] Inception alignment enforced: evaluation window starts after the LAST signal
          asset's inception plus the full maximum warm-up of every grid parameter, so
          all parameter combinations are scored on the IDENTICAL sample.
  [FIX 6] Removed look-ahead: ERC weights, ex-ante vol, regime and momentum are all
          computed on data up to and including day t and applied to day t+1 returns
          (single consistent one-day lag for weights, leverage and costs).
  [FIX 7] Hysteresis state machine initialised from the first valid price/SMA comparison
          instead of being hard-wired to "risk-off"; undefined regime = flat (cash),
          never a phantom defensive allocation.
  [FIX 8] Volatility targeting uses the ex-ante portfolio vol from the same lookback
          covariance (causal, no zero-inflation from flat days); invalid vol => 0
          leverage instead of silently assuming TARGET_VOL.
  [FIX 9] Robust first-valid-index (an entirely absent asset is NOT treated as valid at
          index 0), duplicate/unsorted index handling, non-positive price sanitisation.
  [FIX 10] Self-contained, dependency-free ERC optimiser (mathematically exact for n<=2,
          convergent cyclical-coordinate-descent for n>2) + deterministic synthetic
          fallback panel so the script is always executable.
"""

from __future__ import annotations

import itertools
import os
import sys
import warnings

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------
DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"
PARQUET_FILE = "frozen_universe_data.parquet"
RESULTS_FILE = "opus13_gridsearch_results.csv"

ASSETS = ['SPY', 'QQQ', 'TQQQ', 'UPRO', 'TLT', 'GLD']

# Round-trip-agnostic one-way trading cost in basis points of traded notional.
BPS_COSTS = {'SPY': 1.0, 'QQQ': 1.0, 'TQQQ': 2.0, 'UPRO': 3.0, 'TLT': 1.0, 'GLD': 1.0}

# Offensive sleeves (base asset -> ERC pool) and defensive universe.
RISK_ON_POOLS = {'QQQ': ('QQQ', 'TQQQ'), 'SPY': ('SPY', 'UPRO')}
DEFENSIVE_ASSETS = ('GLD', 'TLT')
# Assets whose history is mandatory for a decision to be well defined.
SIGNAL_ASSETS = ('SPY', 'QQQ', 'GLD', 'TLT')

TARGET_VOL = 0.15
MAX_LEV_RO = 1.0        # cap while risk-on (sleeve already holds 3x ETFs)
MAX_LEV_ROFF = 1.5      # cap while defensive

RF_ANNUAL = 0.02              # annualised risk-free (compounded to daily)
BORROW_SPREAD_ANNUAL = 0.005  # financing spread ABOVE rf on exposure > 100%

TRADING_DAYS = 252
MIN_EVAL_DAYS = 3 * TRADING_DAYS

LOOKBACKS = [20, 60, 120]           # ERC / ex-ante vol covariance windows
SMA_WINDOWS = [150, 200, 250]       # trend filter windows
BUFFERS = [0.01, 0.02, 0.03]        # 1%, 2%, 3% hysteresis buffer
MOM_WINDOWS = [126, 252]            # 6m / 12m momentum

NEG_INF = -np.inf


# ----------------------------------------------------------------------------------
# ERC OPTIMISER (self-contained, no external module -> no imported bugs)
# ----------------------------------------------------------------------------------
def erc_weights_from_cov(cov: np.ndarray, max_iter: int = 500, tol: float = 1e-12):
    """
    Equal-Risk-Contribution (long-only, fully invested) weights for a covariance matrix.

    n == 1 : trivially 1.0
    n == 2 : ERC is EXACTLY inverse-volatility (w1*s1 == w2*s2), closed form.
    n >= 3 : cyclical coordinate descent on
                 f(w) = 0.5 * w' S w - (1/n) * sum(log w_i),
             whose stationary point satisfies w_i*(S w)_i = const  (true ERC).
    Returns None if the covariance is not usable.
    """
    cov = np.asarray(cov, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1] or cov.shape[0] == 0:
        return None
    if not np.all(np.isfinite(cov)):
        return None
    d = np.diag(cov).astype(float)
    if np.any(d <= 0.0):
        return None

    n = cov.shape[0]
    if n == 1:
        return np.array([1.0])

    vol = np.sqrt(d)
    w = (1.0 / vol)
    w = w / w.sum()
    if n == 2:
        return w  # exact ERC

    for _ in range(max_iter):
        w_prev = w.copy()
        for i in range(n):
            b = float(cov[i] @ w - cov[i, i] * w[i])
            disc = b * b + 4.0 * cov[i, i] / n
            if not np.isfinite(disc) or disc < 0.0:
                return None
            w[i] = (-b + np.sqrt(disc)) / (2.0 * cov[i, i])
            if not np.isfinite(w[i]) or w[i] <= 0.0:
                return None
        s = w.sum()
        if not np.isfinite(s) or s <= 0.0:
            return None
        if np.max(np.abs(w / s - w_prev / w_prev.sum())) < tol:
            break

    s = w.sum()
    if not np.isfinite(s) or s <= 0.0:
        return None
    return w / s


def precompute_pool_erc(returns: np.ndarray, pool_names, lookback: int, asset_index: dict):
    """
    Rolling ERC weights + ex-ante annualised portfolio vol for one pool / lookback.

    Returns (W, vol) where:
      W   : (N, T) full-universe weight matrix (zeros outside the pool). Column t uses
            ONLY returns in [t-lookback+1, t] (causal).
      vol : (T,)  annualised ex-ante vol sqrt(252 * w'Sw), NaN where undefined.

    An asset enters the pool at date t only if ALL `lookback` returns in the window are
    finite (post-inception, no gaps) -> phantom-asset-proof.
    """
    N, T = returns.shape
    idx = [asset_index[a] for a in pool_names]
    k = len(idx)

    W = np.zeros((N, T), dtype=float)
    pvol = np.full(T, np.nan, dtype=float)
    if lookback < 2 or T == 0:
        return W, pvol

    sub = pd.DataFrame(returns[idx, :].T)  # T x k, NaN preserved (never filled)
    cnt = sub.notna().rolling(lookback, min_periods=lookback).sum().to_numpy()

    cov = np.full((k, k, T), np.nan, dtype=float)
    for a in range(k):
        for b in range(a, k):
            c = sub.iloc[:, a].rolling(lookback, min_periods=lookback).cov(sub.iloc[:, b]).to_numpy()
            cov[a, b, :] = c
            cov[b, a, :] = c

    full = np.where(np.isfinite(cnt), cnt, -1.0) >= float(lookback)

    for t in range(lookback - 1, T):
        Ct = cov[:, :, t]
        diag = np.diag(Ct)
        usable = full[t] & np.isfinite(diag) & (diag > 0.0)
        m = int(usable.sum())
        if m == 0:
            continue
        sel = np.flatnonzero(usable)
        C = Ct[np.ix_(sel, sel)]
        if not np.all(np.isfinite(C)):
            continue
        w = erc_weights_from_cov(C)
        if w is None:
            continue
        pv = float(w @ C @ w)
        if not np.isfinite(pv) or pv <= 0.0:
            continue
        W[np.array(idx)[sel], t] = w
        pvol[t] = np.sqrt(pv * TRADING_DAYS)

    return W, pvol


# ----------------------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------------------
def _synthetic_panel() -> pd.DataFrame:
    """Deterministic fallback panel with REALISTIC inception dates (keeps the pipeline
    honest about inception alignment even without the frozen parquet)."""
    dates = pd.bdate_range('1993-01-29', '2024-12-31')
    T = len(dates)
    rng = np.random.default_rng(20240613)

    inception = {
        'SPY': '1993-01-29', 'QQQ': '1999-03-10', 'TLT': '2002-07-30',
        'GLD': '2004-11-18', 'UPRO': '2009-06-25', 'TQQQ': '2010-02-11',
    }
    mkt = rng.normal(0.00032, 0.0102, T)
    tech = 1.15 * mkt + rng.normal(0.00008, 0.0062, T)
    bond = rng.normal(0.00016, 0.0058, T) - 0.18 * mkt
    gold = rng.normal(0.00018, 0.0090, T) + 0.05 * mkt
    base = {'SPY': mkt, 'QQQ': tech, 'TLT': bond, 'GLD': gold}
    lev_map = {'UPRO': ('SPY', 3.0), 'TQQQ': ('QQQ', 3.0)}

    frames = []
    for a in ASSETS:
        if a in base:
            r = base[a].copy()
        else:
            src, mult = lev_map[a]
            r = mult * base[src] - 0.0095 / TRADING_DAYS  # 3x ETF fee/financing drag
        start = int(dates.searchsorted(pd.Timestamp(inception[a])))
        start = min(max(start, 0), T - 1)
        rr = r[start:].copy()
        rr[0] = 0.0
        px = 100.0 * np.cumprod(1.0 + rr)
        f = pd.DataFrame({'Close': px, 'Adj Close': px}, index=dates[start:])
        f.index.name = 'Date'
        f['Ticker'] = a
        frames.append(f.reset_index())

    out = pd.concat(frames, ignore_index=True).set_index(['Date', 'Ticker']).sort_index()
    return out


def _normalise_panel(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Check if Ticker is both in index and columns, if so, drop the column version
    if isinstance(df.index, pd.MultiIndex):
        if 'Ticker' in df.index.names and 'Ticker' in df.columns:
            df = df.drop(columns=['Ticker'])
            
    # If it's already a MultiIndex with Date and Ticker, just ensure Date is datetime
    if isinstance(df.index, pd.MultiIndex) and 'Date' in df.index.names and 'Ticker' in df.index.names:
        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index(['Date', 'Ticker'])
    else:
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
        cols = {str(c).lower(): c for c in df.columns}
        dcol = cols.get('date') or cols.get('index') or cols.get('datetime')
        tcol = cols.get('ticker') or cols.get('symbol') or cols.get('asset')
        if dcol is None or tcol is None:
            # Maybe the index is Date and Ticker is a column
            if df.index.name and str(df.index.name).lower() in ['date', 'datetime']:
                df = df.reset_index()
                dcol = df.columns[0]
            else:
                raise ValueError("Panel must expose Date and Ticker (index levels or columns).")
        
        df[dcol] = pd.to_datetime(df[dcol])
        df = df.rename(columns={dcol: 'Date', tcol: 'Ticker'})
        # drop duplicates if any
        df = df.loc[:,~df.columns.duplicated()]
        if 'Date' in df.columns and 'Ticker' in df.columns:
            df = df.set_index(['Date', 'Ticker'])

    if 'Adj Close' not in df.columns and 'Close' in df.columns:
        df['Adj Close'] = df['Close']
    if 'Close' not in df.columns and 'Adj Close' in df.columns:
        df['Close'] = df['Adj Close']
    if 'Adj Close' not in df.columns:
        raise ValueError("Panel must contain 'Adj Close' and/or 'Close'.")

    df = df[~df.index.duplicated(keep='last')].sort_index()
    return df


def load_universe():
    """Load (or synthesise) the frozen panel and build NaN-honest matrices."""
    path = os.path.join(DATA_DIR, PARQUET_FILE)
    src = "parquet"
    if os.path.isfile(path):
        try:
            raw = _normalise_panel(pd.read_parquet(path))
        except Exception as exc:  # pragma: no cover
            warnings.warn(f"Failed to read {path} ({exc}); falling back to synthetic panel.")
            raw, src = _synthetic_panel(), "synthetic"
    else:
        warnings.warn(f"{path} not found; using deterministic synthetic panel.")
        raw, src = _synthetic_panel(), "synthetic"

    dates = pd.DatetimeIndex(raw.index.get_level_values('Date').unique()).sort_values()
    N, T = len(ASSETS), len(dates)
    adj = np.full((N, T), np.nan, dtype=float)

    for i, asset in enumerate(ASSETS):
        try:
            sub = raw.xs(asset, level='Ticker')
        except KeyError:
            continue
        sub = sub[~sub.index.duplicated(keep='last')].sort_index().reindex(dates)  # NaN, never 0
        px = pd.to_numeric(sub['Adj Close'], errors='coerce').to_numpy(dtype=float)
        px = np.where(np.isfinite(px) & (px > 0.0), px, np.nan)  # sanitise bad prices
        adj[i, :] = px

    # Total-return based simple returns; NaN propagates across inception boundaries.
    returns = np.full((N, T), np.nan, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        returns[:, 1:] = adj[:, 1:] / adj[:, :-1] - 1.0
    returns = np.where(np.isfinite(returns), returns, np.nan)

    rf_daily = np.full(T, (1.0 + RF_ANNUAL) ** (1.0 / TRADING_DAYS) - 1.0, dtype=float)
    return adj, returns, rf_daily, dates, src


def first_finite_index(row: np.ndarray):
    finite = np.isfinite(row)
    if not finite.any():
        return None
    return int(np.argmax(finite))


# ----------------------------------------------------------------------------------
# SIGNALS
# ----------------------------------------------------------------------------------
def buffered_regime(price: np.ndarray, sma: np.ndarray, buffer: float) -> np.ndarray:
    """Hysteresis trend regime: 1 = risk-on, 0 = risk-off, -1 = undefined (flat)."""
    T = len(price)
    regime = np.full(T, -1, dtype=int)
    state = -1
    for t in range(T):
        p, s = price[t], sma[t]
        if not (np.isfinite(p) and np.isfinite(s) and s > 0.0):
            continue
        if state == -1:
            state = 1 if p > s else 0                       # unbiased initialisation
        elif state == 0 and p > s * (1.0 + buffer):
            state = 1
        elif state == 1 and p < s * (1.0 - buffer):
            state = 0
        regime[t] = state
    return regime


def momentum_matrix(adj: np.ndarray, window: int) -> np.ndarray:
    """Total-return momentum over `window` sessions; NaN before window is complete."""
    N, T = adj.shape
    mom = np.full((N, T), np.nan, dtype=float)
    if window < T:
        with np.errstate(divide='ignore', invalid='ignore'):
            mom[:, window:] = adj[:, window:] / adj[:, :-window] - 1.0
    return np.where(np.isfinite(mom), mom, np.nan)


def rf_window_return(rf_daily: np.ndarray, window: int) -> np.ndarray:
    """Compounded risk-free return over the trailing `window` sessions (absolute-mom hurdle)."""
    T = len(rf_daily)
    idx = np.concatenate(([1.0], np.cumprod(1.0 + rf_daily)))  # idx[t+1] = growth through t
    out = np.full(T, np.nan, dtype=float)
    if window < T:
        out[window:] = idx[window + 1:] / idx[1:T - window + 1] - 1.0
    return out


# ----------------------------------------------------------------------------------
# METRICS
# ----------------------------------------------------------------------------------
def performance_stats(ret: np.ndarray, rf: np.ndarray, dts: pd.DatetimeIndex):
    growth = 1.0 + ret
    if not np.all(np.isfinite(growth)) or np.any(growth <= 0.0):
        return None  # ruin / invalid path

    equity = np.cumprod(growth)
    n = len(ret)
    years = (dts[-1] - dts[0]).days / 365.25
    if years <= 0:
        years = n / TRADING_DAYS
    cagr = equity[-1] ** (1.0 / years) - 1.0

    ex = ret - rf
    sd_ex = float(np.std(ex, ddof=1)) if n > 1 else np.nan
    sharpe = (float(np.mean(ex)) / sd_ex) * np.sqrt(TRADING_DAYS) if (sd_ex and sd_ex > 0) else np.nan

    ann_vol = (float(np.std(ret, ddof=1)) * np.sqrt(TRADING_DAYS)) if n > 1 else np.nan
    downside = np.sqrt(np.mean(np.minimum(ex, 0.0) ** 2))
    sortino = (float(np.mean(ex)) / downside) * np.sqrt(TRADING_DAYS) if downside > 0 else np.nan

    dd = equity / np.maximum.accumulate(equity) - 1.0
    mdd = float(dd.min())
    calmar = cagr / abs(mdd) if mdd < 0 else np.nan

    return {
        'cagr': cagr, 'sharpe': sharpe, 'sortino': sortino, 'ann_vol': ann_vol,
        'mdd': mdd, 'calmar': calmar, 'total_return': equity[-1] - 1.0, 'days': n,
        'years': years,
    }


# ----------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------
def main() -> int:
    global DATA_DIR
    if not os.path.isdir(DATA_DIR):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
        except Exception:
            DATA_DIR = os.getcwd()

    adj, returns, rf_daily, dates, src = load_universe()
    N, T = returns.shape
    asset_index = {a: i for i, a in enumerate(ASSETS)}
    print(f"Loaded panel [{src}] : {N} assets x {T} sessions "
          f"({dates[0].date()} -> {dates[-1].date()})")

    # ---- inception map (FIX 5 / FIX 9) -------------------------------------------
    first_valid = {}
    for a in ASSETS:
        fv = first_finite_index(returns[asset_index[a]])
        first_valid[a] = fv
        print(f"   {a:<5} inception(return) : "
              f"{'ABSENT' if fv is None else dates[fv].date()}")

    missing = [a for a in SIGNAL_ASSETS if first_valid[a] is None]
    if missing:
        print(f"FATAL: mandatory signal assets missing from panel: {missing}")
        return 1

    # ---- precompute ERC weights + ex-ante vol -----------------------------------
    pools = []
    for pool in RISK_ON_POOLS.values():
        pools.append(tuple(a for a in pool if first_valid[a] is not None))
    defensive_present = tuple(a for a in DEFENSIVE_ASSETS if first_valid[a] is not None)
    for r in range(1, len(defensive_present) + 1):
        for combo in itertools.combinations(defensive_present, r):
            pools.append(combo)
    pools = [p for p in dict.fromkeys(pools) if len(p) > 0]

    print("Precalculating rolling ERC weights / ex-ante vols ...")
    cache = {}
    for pool in pools:
        for lb in LOOKBACKS:
            cache[(pool, lb)] = precompute_pool_erc(returns, pool, lb, asset_index)

    pool_qqq = tuple(a for a in RISK_ON_POOLS['QQQ'] if first_valid[a] is not None)
    pool_spy = tuple(a for a in RISK_ON_POOLS['SPY'] if first_valid[a] is not None)
    def_key = {frozenset(k): k for k in pools}

    # ---- signal caches ------------------------------------------------------------
    spy_i, qqq_i = asset_index['SPY'], asset_index['QQQ']
    gld_i, tlt_i = asset_index['GLD'], asset_index['TLT']

    regime_cache = {}
    spy_px = adj[spy_i]
    for sma_w in SMA_WINDOWS:
        sma = pd.Series(spy_px).rolling(sma_w, min_periods=sma_w).mean().to_numpy()
        for buf in BUFFERS:
            regime_cache[(sma_w, buf)] = buffered_regime(spy_px, sma, buf)

    mom_cache, hurdle_cache = {}, {}
    for mw in MOM_WINDOWS:
        mom_cache[mw] = momentum_matrix(adj, mw)
        hurdle_cache[mw] = rf_window_return(rf_daily, mw)

    # ---- common evaluation start (identical sample for every combination) --------
    last_signal_inception = max(first_valid[a] for a in SIGNAL_ASSETS)
    warmup = max(max(SMA_WINDOWS), max(MOM_WINDOWS), max(LOOKBACKS))
    global_start = last_signal_inception + warmup + 2  # +2 for the causal 1-day shifts
    if global_start >= T - MIN_EVAL_DAYS:
        print(f"FATAL: insufficient history. start={global_start}, T={T}, "
              f"need >= {MIN_EVAL_DAYS} evaluation days.")
        return 1
    print(f"Common evaluation window: {dates[global_start].date()} -> {dates[-1].date()} "
          f"({T - global_start} sessions)")

    cost_bps = np.array([BPS_COSTS[a] for a in ASSETS], dtype=float) / 10000.0
    spread_daily = (1.0 + BORROW_SPREAD_ANNUAL) ** (1.0 / TRADING_DAYS) - 1.0
    R0 = np.where(np.isfinite(returns), returns, 0.0)
    R_finite = np.isfinite(returns)

    combos = list(itertools.product(SMA_WINDOWS, LOOKBACKS, BUFFERS, MOM_WINDOWS))
    print(f"Sweeping {len(combos)} combinations ...")

    results, skipped = [], 0

    for sma_w, lb, buf, mom_w in combos:
        regime = regime_cache[(sma_w, buf)]
        M = mom_cache[mom_w]
        hurdle = hurdle_cache[mom_w]
        h = np.where(np.isfinite(hurdle), hurdle, np.inf)  # unknown hurdle => cannot pass

        m_spy = np.where(np.isfinite(M[spy_i]), M[spy_i], NEG_INF)
        m_qqq = np.where(np.isfinite(M[qqq_i]), M[qqq_i], NEG_INF)
        m_gld = np.where(np.isfinite(M[gld_i]), M[gld_i], NEG_INF)
        m_tlt = np.where(np.isfinite(M[tlt_i]), M[tlt_i], NEG_INF)

        risk_on = (regime == 1)
        prefer_qqq = m_qqq >= m_spy                                   # relative momentum
        choose_qqq = risk_on & prefer_qqq & (m_qqq > h)                # + absolute momentum
        choose_spy = risk_on & (~prefer_qqq) & (m_spy > h)
        defensive = ((regime == 0) | (risk_on & ~(choose_qqq | choose_spy)))

        gld_ok = defensive & (m_gld > h)                               # FIX 4
        tlt_ok = defensive & (m_tlt > h)

        W_dec = np.zeros((N, T), dtype=float)
        sig_dec = np.full(T, np.nan, dtype=float)
        cap_dec = np.full(T, np.nan, dtype=float)

        def _assign(mask, pool):
            if pool is None or len(pool) == 0 or not mask.any():
                return
            entry = cache.get((pool, lb))
            if entry is None:
                return
            Wp, vp = entry
            W_dec[:, mask] = Wp[:, mask]
            sig_dec[mask] = vp[mask]

        _assign(choose_qqq, pool_qqq)
        _assign(choose_spy, pool_spy)
        cap_dec[choose_qqq | choose_spy] = MAX_LEV_RO

        both = gld_ok & tlt_ok
        only_g = gld_ok & ~tlt_ok
        only_t = tlt_ok & ~gld_ok
        _assign(both, def_key.get(frozenset(('GLD', 'TLT'))))
        _assign(only_g, def_key.get(frozenset(('GLD',))))
        _assign(only_t, def_key.get(frozenset(('TLT',))))
        cap_dec[defensive] = MAX_LEV_ROFF

        # Kill any residual weight on assets without a usable ex-ante vol / weights.
        gross_dec = W_dec.sum(axis=0)
        bad = ~(np.isfinite(sig_dec) & (sig_dec > 0.0) & np.isfinite(cap_dec) & (gross_dec > 0.0))
        if bad.any():
            W_dec[:, bad] = 0.0

        with np.errstate(divide='ignore', invalid='ignore'):
            lev_dec = np.where(bad, 0.0, np.clip(TARGET_VOL / np.where(bad, 1.0, sig_dec),
                                                 0.0, np.where(bad, 0.0, cap_dec)))
        lev_dec = np.where(np.isfinite(lev_dec), lev_dec, 0.0)

        # ---- causal one-day application lag (FIX 6) ------------------------------
        W_appl = np.zeros((N, T), dtype=float)
        W_appl[:, 1:] = W_dec[:, :-1]
        lev_appl = np.zeros(T, dtype=float)
        lev_appl[1:] = lev_dec[:-1]

        # Drop (and renormalise away from) assets with a missing return on the day.
        W_eff = np.where(R_finite, W_appl, 0.0)
        tgt = W_appl.sum(axis=0)
        got = W_eff.sum(axis=0)
        with np.errstate(divide='ignore', invalid='ignore'):
            scale = np.where(got > 0.0, tgt / np.where(got > 0.0, got, 1.0), 0.0)
        W_eff = W_eff * scale

        # Actual leverage-scaled positions -> costs & financing on real notional.
        P = W_eff * lev_appl
        dP = np.diff(P, axis=1, prepend=np.zeros((N, 1)))
        turnover = np.abs(dP)
        cost = (turnover * cost_bps[:, None]).sum(axis=0)          # FIX 3

        g = P.sum(axis=0)                                          # gross exposure
        asset_pnl = (P * R0).sum(axis=0)
        cash_leg = (1.0 - g) * rf_daily                            # earn/pay rf on cash
        borrow_leg = np.maximum(g - 1.0, 0.0) * spread_daily       # spread above rf
        port_net = asset_pnl + cash_leg - borrow_leg - cost

        eval_ret = port_net[global_start:]
        eval_rf = rf_daily[global_start:]
        eval_dts = dates[global_start:]

        stats = performance_stats(eval_ret, eval_rf, eval_dts)
        if stats is None or stats['days'] < MIN_EVAL_DAYS:
            skipped += 1
            continue

        exposure = g[global_start:]
        results.append({
            'sma': sma_w, 'lookback': lb, 'buffer': buf, 'mom_w': mom_w,
            'cagr': stats['cagr'], 'sharpe': stats['sharpe'], 'sortino': stats['sortino'],
            'ann_vol': stats['ann_vol'], 'mdd': stats['mdd'], 'calmar': stats['calmar'],
            'total_return': stats['total_return'],
            'ann_turnover': float(turnover[:, global_start:].sum(axis=0).mean() * TRADING_DAYS),
            'ann_cost_drag': float(cost[global_start:].mean() * TRADING_DAYS),
            'avg_exposure': float(exposure.mean()),
            'max_exposure': float(exposure.max()),
            'pct_invested': float((exposure > 1e-12).mean()),
            'days': stats['days'], 'years': stats['years'],
            'start': str(eval_dts[0].date()), 'end': str(eval_dts[-1].date()),
        })

    if not results:
        print(f"No valid configurations (skipped {skipped}).")
        return 1

    df = pd.DataFrame(results).sort_values(
        ['sharpe', 'calmar', 'cagr'], ascending=[False, False, False]
    ).reset_index(drop=True)

    pd.set_option('display.width', 220)
    pd.set_option('display.max_columns', 40)
    print("\n--- BEST STRATEGIES (V13 DUAL MOMENTUM, AUDITED) ---")
    show = ['sma', 'lookback', 'buffer', 'mom_w', 'cagr', 'sharpe', 'sortino',
            'ann_vol', 'mdd', 'calmar', 'ann_turnover', 'ann_cost_drag',
            'avg_exposure', 'pct_invested']
    print(df.head(10)[show].to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

    out_path = os.path.join(DATA_DIR, RESULTS_FILE)
    try:
        df.to_csv(out_path, index=False)
        print(f"\nSaved {len(df)} rows -> {out_path}")
    except Exception as exc:
        fallback = os.path.join(os.getcwd(), RESULTS_FILE)
        df.to_csv(fallback, index=False)
        print(f"\nCould not write to {out_path} ({exc}); saved -> {fallback}")

    b = df.iloc[0]
    print(f"\nBEST: SMA={int(b['sma'])} LB={int(b['lookback'])} BUF={b['buffer']:.2%} "
          f"MOM={int(b['mom_w'])} | Sharpe={b['sharpe']:.3f} CAGR={b['cagr']:.2%} "
          f"Vol={b['ann_vol']:.2%} MDD={b['mdd']:.2%} | {b['start']} -> {b['end']}")
    print(f"Skipped configurations (ruin / insufficient sample): {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())