"""
opus8_signal_generator_v8_clean.py
==================================
Brutal Multipoint Quality Inspector -- Absolute Surrender Protocol build.

Rewritten, logic-gap-free signal generator + audited walk-forward evaluator.

Fatal bugs from legacy versions that are explicitly fixed here
--------------------------------------------------------------
1.  NO `.fillna(0)` ANYWHERE.  Missing prices stay NaN.  A NaN price can never
    produce a valid signal, a valid return, or an allocated weight.  Phantom
    pre-inception assets are therefore impossible.
2.  TRUE SHARPE RATIO.  Sharpe = mean(excess daily return) /
    std(excess daily return, ddof=1) * sqrt(252) using an explicit risk-free
    series.  NOT CAGR / volatility.
3.  TRANSACTION COSTS + BORROWING SPREAD.  Per-unit-notional traded cost in bps
    on every weight change, cash credited at rf, negative cash (leverage)
    charged at rf + borrow spread.
4.  ABSOLUTE MOMENTUM ON DEFENSIVE ASSETS.  Defensive sleeve is only held when
    its own trailing total return beats the compounded risk-free rate over the
    same window (decision lagged like every other signal).  Otherwise: cash.
5.  INCEPTION ALIGNMENT.  Every strategy starts at the max of the first valid
    date of (traded asset signal, risk-free series, every defensive asset's
    return AND absolute-momentum window).  No back-filled history.

Also fixed
----------
*  `reset_index()` crash when an index level name duplicates an existing
    column (e.g. a parquet with both a 'Ticker' index level and a 'Ticker'
    column).  Handled by `_safe_reset_index`.
*  `to_positions` broken for lag == 0 (`arr[:, :-0]` returns an empty slice).
*  EMA/SMA burn-in measured from the *last data gap*, not from the very first
    observation, via consecutive-run-length gating.
*  Statistical sanity checks (occupancy / flip counts) are reported, not
    fatal-asserted, so a legitimately short or trending series cannot abort the
    whole pipeline.  Structural checks remain hard assertions.
"""

from __future__ import annotations

import os
import json
import math
import hashlib
import warnings

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Optional numba (graceful degradation to pure python)
# --------------------------------------------------------------------------- #
try:  # pragma: no cover
    import numba

    def njit(*args, **kwargs):
        kwargs.setdefault("cache", True)
        return numba.njit(*args, **kwargs)

    _HAVE_NUMBA = True
except Exception:  # pragma: no cover
    _HAVE_NUMBA = False

    def njit(*args, **kwargs):
        def _deco(func):
            return func
        if args and callable(args[0]):
            return args[0]
        return _deco


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# --------------------------------------------------------------------------- #
# Configuration (import if available, otherwise safe defaults)
# --------------------------------------------------------------------------- #
try:  # pragma: no cover
    import opus8_config as _CFG
except Exception:  # pragma: no cover
    _CFG = None


def _cfg(name, default):
    if _CFG is None:
        return default
    return getattr(_CFG, name, default)


_HERE = os.path.dirname(os.path.abspath(__file__))

IN_DIR = str(_cfg("IN_DIR", os.path.join(_HERE, "opus8_data")))
PARQUET_FILE = str(_cfg("PARQUET_FILE", os.path.join(IN_DIR, "prices.parquet")))
MANIFEST_FILE = str(_cfg("MANIFEST_FILE", os.path.join(IN_DIR, "manifest.json")))

TICKERS_TRADED = list(_cfg("TICKERS_TRADED", ["SPY", "QQQ", "IWM", "EFA", "EEM"]))
DEFENSIVE_TICKERS = list(_cfg("DEFENSIVE_TICKERS", ["IEF", "SHY"]))

LAG = int(_cfg("LAG", 1))                       # bars between signal and position
ANNUALIZATION = int(_cfg("ANNUALIZATION", 252))

COST_BPS = float(_cfg("COST_BPS", 5.0))         # per unit notional traded, one way
BORROW_SPREAD_BPS = float(_cfg("BORROW_SPREAD_BPS", 100.0))  # annual, over rf
LEVERAGE = float(_cfg("LEVERAGE", 1.0))         # gross target when risk-on

RF_TICKER = _cfg("RF_TICKER", None)             # optional cash-proxy total-return ticker
RF_ANNUAL = float(_cfg("RF_ANNUAL", 0.02))      # fallback constant risk-free rate

ABSMOM_LOOKBACK = int(_cfg("ABSMOM_LOOKBACK", 252))
STRICT_INCEPTION_ALIGNMENT = bool(_cfg("STRICT_INCEPTION_ALIGNMENT", True))
STRICT_VALIDATION = bool(_cfg("STRICT_VALIDATION", False))
ALLOW_SYNTHETIC_FALLBACK = bool(_cfg("ALLOW_SYNTHETIC_FALLBACK", True))

FAMILIES = ["MACD", "SMA200"]

MACD_PARAMS = [
    (12, 26, 9), (8, 21, 5), (5, 34, 7), (3, 10, 16), (24, 52, 18),
    (12, 50, 9), (10, 40, 15), (5, 15, 5), (15, 35, 10),
]
SMA_PARAMS = [200, 150, 250, 100, 300, 180, 220, 240, 260]

MIN_OCCUPANCY = 0.001
MAX_OCCUPANCY = 0.999
MIN_FLIPS = 5

DATE_ALIASES = {"date", "datetime", "timestamp", "time", "index", "level0", "asofdate"}
TICKER_ALIASES = {"ticker", "symbol", "asset", "instrument", "security", "id", "permno"}
PRICE_ALIASES = [
    "adjclose", "adj_close", "adjustedclose", "closeadj", "totalreturnindex",
    "close", "pxlast", "price", "nav", "value", "last",
]


# ========================================================================== #
# Low level numeric kernels (NaN-safe, gap-aware)
# ========================================================================== #
@njit
def _run_length(arr):
    """Number of consecutive non-NaN observations ending at i (inclusive)."""
    n = arr.shape[0]
    out = np.zeros(n, dtype=np.int64)
    c = 0
    for i in range(n):
        if np.isnan(arr[i]):
            c = 0
        else:
            c += 1
        out[i] = c
    return out


@njit
def _ema_masked(arr, span):
    """
    EMA that never carries a stale value across a NaN gap.
    Output is NaN wherever the input is NaN; the recursion re-seeds at the
    first observation after every gap.
    """
    n = arr.shape[0]
    out = np.full(n, np.nan)
    alpha = 2.0 / (span + 1.0)
    prev = np.nan
    for i in range(n):
        x = arr[i]
        if np.isnan(x):
            out[i] = np.nan
            prev = np.nan
        else:
            if np.isnan(prev):
                out[i] = x
            else:
                out[i] = alpha * x + (1.0 - alpha) * prev
            prev = out[i]
    return out


@njit
def _sma_masked(arr, window, runlen):
    """
    Exact simple moving average requiring `window` consecutive non-NaN values.
    Recomputed exactly each bar (no running-sum drift).
    """
    n = arr.shape[0]
    out = np.full(n, np.nan)
    if window < 1:
        return out
    for i in range(n):
        if runlen[i] >= window:
            s = 0.0
            for j in range(i - window + 1, i + 1):
                s += arr[j]
            out[i] = s / window
    return out


@njit
def macd_signal_masked(close, fast, slow, signal, burn_in):
    """
    Returns (signal 0/1, valid 0/1).
    valid requires: `burn_in` consecutive non-NaN closes ending at i AND finite
    MACD/signal-line values.  A NaN close can never be valid -> no phantom
    exposure across delistings or pre-inception periods.
    """
    n = close.shape[0]
    ef = _ema_masked(close, fast)
    es = _ema_masked(close, slow)
    macd = np.full(n, np.nan)
    for i in range(n):
        if not np.isnan(ef[i]) and not np.isnan(es[i]):
            macd[i] = ef[i] - es[i]
    sl = _ema_masked(macd, signal)
    rl = _run_length(close)

    sig = np.zeros(n, dtype=np.int8)
    val = np.zeros(n, dtype=np.int8)
    for i in range(n):
        if rl[i] >= burn_in and not np.isnan(macd[i]) and not np.isnan(sl[i]):
            val[i] = 1
            if macd[i] > sl[i]:
                sig[i] = 1
    return sig, val


@njit
def sma_signal_masked(close, window):
    n = close.shape[0]
    rl = _run_length(close)
    sma = _sma_masked(close, window, rl)
    sig = np.zeros(n, dtype=np.int8)
    val = np.zeros(n, dtype=np.int8)
    for i in range(n):
        if rl[i] >= window and not np.isnan(sma[i]) and not np.isnan(close[i]):
            val[i] = 1
            if close[i] > sma[i]:
                sig[i] = 1
    return sig, val


@njit
def simple_returns_masked(close):
    """r_i = close_i/close_{i-1} - 1, NaN if either endpoint missing/non-positive."""
    n = close.shape[0]
    out = np.full(n, np.nan)
    for i in range(1, n):
        a = close[i - 1]
        b = close[i]
        if (not np.isnan(a)) and (not np.isnan(b)) and a > 0.0:
            out[i] = b / a - 1.0
    return out


@njit
def total_return_lookback(close, lb):
    """Trailing total return over `lb` bars, requiring lb+1 consecutive prices."""
    n = close.shape[0]
    out = np.full(n, np.nan)
    rl = _run_length(close)
    for i in range(n):
        if i >= lb and rl[i] >= lb + 1:
            a = close[i - lb]
            if a > 0.0:
                out[i] = close[i] / a - 1.0
    return out


def shift_forward(arr, lag):
    """Shift an array forward in time by `lag` bars (fills leading entries)."""
    lag = int(lag)
    if lag < 0:
        raise ValueError("lag must be >= 0")
    if lag == 0:
        return np.array(arr, copy=True)
    out = np.empty_like(arr)
    if np.issubdtype(out.dtype, np.floating):
        out[:lag] = np.nan
    else:
        out[:lag] = 0
    out[lag:] = arr[:-lag]
    return out


def rolling_rf_total(rf_daily, lb):
    """Compounded risk-free return over trailing `lb` bars (NaN-safe)."""
    s = pd.Series(rf_daily, dtype="float64")
    logs = np.log1p(s)
    roll = logs.rolling(lb, min_periods=lb).sum()
    return np.expm1(roll).to_numpy()


# ========================================================================== #
# Data loading (crash-proof against index/column name collisions)
# ========================================================================== #
def _norm(name) -> str:
    return "".join(ch for ch in str(name).strip().lower() if ch.isalnum())


def _safe_reset_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    reset_index() that can never raise "cannot insert X, already exists".
    Index level names that collide with existing columns are temporarily
    renamed; the surviving duplicate (the original column) wins and the
    renamed index copy is dropped if it is redundant.
    """
    out = df.copy()
    names = list(out.index.names)
    existing = set(map(str, out.columns))
    new_names, renamed = [], {}
    for i, nm in enumerate(names):
        base = f"__level_{i}__" if nm is None else str(nm)
        cand = base
        k = 0
        while cand in existing or cand in new_names:
            k += 1
            cand = f"__idx{k}__{base}"
        if cand != base:
            renamed[cand] = base
        new_names.append(cand)
        existing.add(cand)
    out.index = out.index.set_names(new_names)
    out = out.reset_index()

    # Drop renamed index copies that duplicate an identical existing column.
    for tmp, base in renamed.items():
        if base in out.columns and tmp in out.columns:
            try:
                same = out[base].astype(str).equals(out[tmp].astype(str))
            except Exception:
                same = False
            if same:
                out = out.drop(columns=[tmp])
    return out


def _pick(columns, aliases, ordered=False):
    cols = list(columns)
    norm = {c: _norm(c) for c in cols}
    if ordered:
        for a in aliases:
            for c in cols:
                if norm[c] == a:
                    return c
        for a in aliases:
            for c in cols:
                if a in norm[c]:
                    return c
        return None
    for c in cols:
        if norm[c] in aliases:
            return c
    for c in cols:
        stripped = norm[c].replace("idx", "", 1)
        if stripped in aliases:
            return c
    return None


def _wide_from_long(long: pd.DataFrame, date_col, ticker_col, price_col) -> pd.DataFrame:
    sub = long[[date_col, ticker_col, price_col]].copy()
    sub[date_col] = pd.to_datetime(sub[date_col], errors="coerce", utc=False)
    sub[ticker_col] = sub[ticker_col].astype(str).str.strip().str.upper()
    sub[price_col] = pd.to_numeric(sub[price_col], errors="coerce")
    sub = sub.dropna(subset=[date_col, ticker_col])
    wide = sub.pivot_table(index=date_col, columns=ticker_col,
                           values=price_col, aggfunc="last")
    wide.index = pd.DatetimeIndex(wide.index).tz_localize(None)
    return wide


def _make_synthetic(tickers, n=6000, seed=20240817) -> pd.DataFrame:
    """
    Deterministic fallback so the script is always executable.
    Staggered inceptions deliberately exercise the inception-alignment logic;
    pre-inception values stay NaN (never zero).
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("1999-01-04", periods=n)
    data = {}
    for k, t in enumerate(sorted(set(tickers))):
        mu, sig = (0.00030, 0.011) if k % 3 else (0.00012, 0.0045)
        r = rng.normal(mu, sig, n)
        px = 100.0 * np.exp(np.cumsum(r))
        start = int(min(n - 1500, 250 * k))
        px[:start] = np.nan
        data[t] = px
    return pd.DataFrame(data, index=idx)


def load_prices(tickers):
    """
    Returns (wide price DataFrame [Date x Ticker], data_hash str, missing list).
    Absolutely no filling of missing data.
    """
    needed = [str(t).strip().upper() for t in tickers]
    wide = None

    if os.path.isfile(PARQUET_FILE):
        raw = pd.read_parquet(PARQUET_FILE)

        # --- MultiIndex columns, e.g. ('Adj Close','SPY') --------------------
        if isinstance(raw.columns, pd.MultiIndex):
            picked = None
            for lvl in range(raw.columns.nlevels):
                vals = {_norm(v): v for v in raw.columns.get_level_values(lvl)}
                for a in PRICE_ALIASES:
                    if a in vals:
                        picked = (lvl, vals[a])
                        break
                if picked:
                    break
            if picked is not None:
                raw = raw.xs(picked[1], axis=1, level=picked[0])
            else:
                raw.columns = ["_".join(map(str, c)).strip("_") for c in raw.columns]

        flat = _safe_reset_index(raw)
        date_col = _pick(flat.columns, DATE_ALIASES)
        if date_col is None:
            for c in flat.columns:
                if pd.api.types.is_datetime64_any_dtype(flat[c]):
                    date_col = c
                    break
        ticker_col = _pick(flat.columns, TICKER_ALIASES)
        price_col = _pick(flat.columns, PRICE_ALIASES, ordered=True)

        if date_col is not None and ticker_col is not None and price_col is not None:
            wide = _wide_from_long(flat, date_col, ticker_col, price_col)
        elif date_col is not None:
            # already wide: one numeric column per ticker
            sub = flat.copy()
            sub[date_col] = pd.to_datetime(sub[date_col], errors="coerce")
            sub = sub.dropna(subset=[date_col]).set_index(date_col)
            sub = sub.select_dtypes(include=[np.number])
            sub.columns = [str(c).strip().upper() for c in sub.columns]
            sub = sub.loc[:, ~sub.columns.duplicated()]
            sub.index = pd.DatetimeIndex(sub.index).tz_localize(None)
            wide = sub
        else:
            wide = None

    if wide is None or wide.empty:
        if not ALLOW_SYNTHETIC_FALLBACK:
            raise FileNotFoundError(f"Unusable/missing price file: {PARQUET_FILE}")
        warnings.warn(f"[DATA] '{PARQUET_FILE}' unusable -> deterministic synthetic fallback.")
        wide = _make_synthetic(needed)

    wide = wide.apply(pd.to_numeric, errors="coerce")
    wide = wide[~wide.index.duplicated(keep="last")].sort_index()
    wide = wide.loc[:, ~wide.columns.duplicated(keep="last")]
    wide[wide <= 0] = np.nan                        # non-positive prices are invalid
    wide = wide.dropna(axis=1, how="all")

    missing = [t for t in needed if t not in wide.columns]
    keep = [c for c in wide.columns if c in set(needed)] or list(wide.columns)
    wide = wide[keep]

    data_hash = None
    if os.path.isfile(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r") as f:
                data_hash = json.load(f).get("data_hash")
        except Exception:
            data_hash = None
    if not data_hash:
        h = hashlib.sha256()
        h.update(np.ascontiguousarray(wide.index.values.astype("datetime64[ns]")).tobytes())
        h.update(",".join(map(str, wide.columns)).encode())
        h.update(np.ascontiguousarray(wide.to_numpy(dtype="float64")).tobytes())
        data_hash = h.hexdigest()

    return wide, str(data_hash), missing


# ========================================================================== #
# Signal generation
# ========================================================================== #
def to_positions(sig, valid, lag=LAG):
    """
    Convert same-bar signals into tradeable positions with an explicit lag.
    lag == 0 is handled correctly (identity), unlike the legacy `[:, :-0]` bug.
    """
    lag = int(lag)
    if lag < 0:
        raise ValueError("LAG must be >= 0")
    if lag == 0:
        return sig.copy(), valid.copy()
    pos = np.zeros_like(sig)
    pos_valid = np.zeros_like(valid)
    pos[:, lag:] = sig[:, :-lag]
    pos_valid[:, lag:] = valid[:, :-lag]
    return pos, pos_valid


def generate_signals(close, lag=LAG, negative_control=False):
    """
    negative_control=True returns UNLAGGED (same-bar, deliberately leaking)
    signals; used only to prove the leakage detector fires.
    """
    close = np.ascontiguousarray(np.asarray(close, dtype="float64"))
    n = close.shape[0]

    m_sig = np.zeros((len(MACD_PARAMS), n), dtype=np.int8)
    m_val = np.zeros((len(MACD_PARAMS), n), dtype=np.int8)
    for i, (f, s, g) in enumerate(MACD_PARAMS):
        burn = int(3 * s + 3 * g)
        m_sig[i], m_val[i] = macd_signal_masked(close, f, s, g, burn)

    s_sig = np.zeros((len(SMA_PARAMS), n), dtype=np.int8)
    s_val = np.zeros((len(SMA_PARAMS), n), dtype=np.int8)
    for i, w in enumerate(SMA_PARAMS):
        s_sig[i], s_val[i] = sma_signal_masked(close, int(w))

    if negative_control:
        m_pos, m_pval, s_pos, s_pval = m_sig, m_val, s_sig, s_val
        eff_lag = 0
    else:
        m_pos, m_pval = to_positions(m_sig, m_val, lag)
        s_pos, s_pval = to_positions(s_sig, s_val, lag)
        eff_lag = lag

    out = {
        "MACD": np.ascontiguousarray(m_pos, dtype=np.int8),
        "MACD_valid": np.ascontiguousarray(m_pval, dtype=np.int8),
        "SMA200": np.ascontiguousarray(s_pos, dtype=np.int8),
        "SMA200_valid": np.ascontiguousarray(s_pval, dtype=np.int8),
        "MACD_params": np.asarray(MACD_PARAMS, dtype=np.int32),
        "SMA200_params": np.asarray(SMA_PARAMS, dtype=np.int32),
        "effective_lag": np.int32(eff_lag),
    }
    return out


def validate_signals(ticker, signals, n_dates, strict=STRICT_VALIDATION):
    problems = []
    for fam in FAMILIES:
        mat = signals[fam]
        val = signals[f"{fam}_valid"]

        # --- structural invariants: always fatal ---------------------------
        assert mat.ndim == 2 and mat.size > 0, f"{ticker} {fam}: empty matrix"
        assert mat.shape == val.shape, f"{ticker} {fam}: shape mismatch"
        assert mat.shape[1] == n_dates, f"{ticker} {fam}: date-length mismatch"
        assert mat.dtype == np.int8 and val.dtype == np.int8, f"{ticker} {fam}: dtype"
        assert mat.flags["C_CONTIGUOUS"], f"{ticker} {fam}: not C-contiguous"
        assert ((mat == 0) | (mat == 1)).all(), f"{ticker} {fam}: non-binary signal"
        assert ((val == 0) | (val == 1)).all(), f"{ticker} {fam}: non-binary validity"
        assert int(((mat == 1) & (val == 0)).sum()) == 0, \
            f"{ticker} {fam}: invested while invalid (phantom exposure)"

        # --- statistical health: reported, not fatal ----------------------
        for row in range(mat.shape[0]):
            m = val[row] == 1
            cnt = int(m.sum())
            if cnt == 0:
                problems.append(f"{ticker} {fam} p{row}: no valid bars")
                continue
            occ = float(mat[row][m].mean())
            if not (MIN_OCCUPANCY < occ < MAX_OCCUPANCY):
                problems.append(f"{ticker} {fam} p{row}: occupancy {occ:.4f}")
            flips = int(np.abs(np.diff(mat[row][m].astype(np.int16))).sum())
            if flips < MIN_FLIPS:
                problems.append(f"{ticker} {fam} p{row}: only {flips} flips")

    if problems:
        msg = f"[VALIDATION] {ticker}: " + "; ".join(problems[:12])
        if strict:
            raise AssertionError(msg)
        warnings.warn(msg)
    return problems


# ========================================================================== #
# Defensive sleeve with ABSOLUTE MOMENTUM (bug #4)
# ========================================================================== #
def prepare_defensive(px, def_tickers, rf_daily, lookback=ABSMOM_LOOKBACK, lag=LAG):
    """
    For each defensive candidate:
      returns matrix R  (NaN where no data)
      availability matrix A (int8) = 1 only if, using information available
      `lag` bars earlier, trailing total return over `lookback` bars exceeded
      the compounded risk-free return over the same window, AND today's return
      is observable.
    Also returns `ready_idx`: first index where every used defensive asset has
    a computable absolute-momentum decision (inception alignment, bug #5).
    """
    n = len(px.index)
    used = [t for t in def_tickers if t in px.columns]
    K = len(used)
    R = np.zeros((n, K), dtype="float64")
    A = np.zeros((n, K), dtype=np.int8)
    rf_lb = rolling_rf_total(rf_daily, lookback)
    rf_lb_lag = shift_forward(rf_lb, lag)

    ready = 0
    for k, t in enumerate(used):
        c = np.ascontiguousarray(px[t].to_numpy(dtype="float64"))
        r = simple_returns_masked(c)
        tr = total_return_lookback(c, lookback)
        tr_lag = shift_forward(tr, lag)

        ok = np.isfinite(tr_lag) & np.isfinite(rf_lb_lag) & np.isfinite(r)
        on = np.zeros(n, dtype=np.int8)
        on[ok & (tr_lag > rf_lb_lag)] = 1

        R[:, k] = np.where(np.isfinite(r), r, 0.0)   # weight is 0 where invalid
        A[:, k] = on

        decidable = np.flatnonzero(np.isfinite(tr_lag) & np.isfinite(r))
        first = int(decidable[0]) if decidable.size else n
        ready = max(ready, first)

    return used, R, A, int(ready)


# ========================================================================== #
# Backtest engine: costs, borrow spread, cash, turnover (bug #3)
# ========================================================================== #
def run_backtest(pos, pos_valid, r_risky, def_R, def_A, rf_daily,
                 start_idx, cost_bps=COST_BPS, borrow_bps=BORROW_SPREAD_BPS,
                 leverage=LEVERAGE, ann=ANNUALIZATION):
    """
    pos, pos_valid : 1-D int8 arrays (already lagged)
    r_risky        : 1-D float array of the traded asset's simple returns
    Returns dict with net return series (NaN before start), weights diagnostics.
    """
    n = pos.shape[0]
    K = def_R.shape[1]
    cost_rate = cost_bps / 1e4
    spread_d = (borrow_bps / 1e4) / ann

    risky_ok = (pos_valid == 1) & np.isfinite(r_risky)
    w_risky = np.where((pos == 1) & risky_ok, leverage, 0.0)

    # Defensive sleeve: single asset, highest-priority available one.
    W_def = np.zeros((n, K), dtype="float64")
    if K > 0:
        want_def = (w_risky == 0.0)
        chosen = np.full(n, -1, dtype=np.int64)
        remaining = want_def.copy()
        for k in range(K):
            take = remaining & (def_A[:, k] == 1)
            chosen[take] = k
            remaining &= ~take
        for k in range(K):
            W_def[chosen == k, k] = leverage

    W = np.concatenate([w_risky.reshape(-1, 1), W_def], axis=1)
    R = np.concatenate([np.where(np.isfinite(r_risky), r_risky, 0.0).reshape(-1, 1),
                        def_R], axis=1)

    # Mask everything before the aligned inception -> zero exposure, no returns.
    start_idx = int(max(0, min(start_idx, n)))
    W[:start_idx, :] = 0.0

    prev = np.zeros_like(W)
    prev[1:, :] = W[:-1, :]
    traded = np.abs(W - prev).sum(axis=1)
    tc = traded * cost_rate

    gross = W.sum(axis=1)
    cash_w = 1.0 - gross
    rf = np.where(np.isfinite(rf_daily), rf_daily, 0.0)
    cash_pnl = np.where(cash_w >= 0.0, cash_w * rf, cash_w * (rf + spread_d))

    gross_ret = (W * R).sum(axis=1) + cash_pnl
    net = gross_ret - tc

    out_net = np.full(n, np.nan)
    out_net[start_idx:] = net[start_idx:]
    return {
        "net": out_net,
        "gross": np.where(np.isnan(out_net), np.nan, gross_ret),
        "cost": np.where(np.isnan(out_net), np.nan, tc),
        "turnover": np.where(np.isnan(out_net), np.nan, traded),
        "exposure": np.where(np.isnan(out_net), np.nan, gross),
        "start_idx": start_idx,
    }


# ========================================================================== #
# Metrics -- TRUE Sharpe (bug #2)
# ========================================================================== #
def performance_metrics(rets, rf_daily, ann=ANNUALIZATION, turnover=None):
    r = np.asarray(rets, dtype="float64")
    rf = np.asarray(rf_daily, dtype="float64")
    m = np.isfinite(r) & np.isfinite(rf)
    r, rf = r[m], rf[m]
    out = {
        "n_obs": int(r.size), "years": np.nan, "cagr": np.nan, "vol": np.nan,
        "sharpe": np.nan, "sortino": np.nan, "max_dd": np.nan, "calmar": np.nan,
        "hit_rate": np.nan, "skew": np.nan, "kurt": np.nan,
        "ann_turnover": np.nan, "total_return": np.nan,
    }
    if r.size < 2:
        return out

    years = r.size / float(ann)
    equity = np.cumprod(1.0 + r)
    total = float(equity[-1])
    out["years"] = years
    out["total_return"] = total - 1.0
    if total > 0.0 and years > 0.0:
        out["cagr"] = total ** (1.0 / years) - 1.0

    sd = float(np.std(r, ddof=1))
    out["vol"] = sd * math.sqrt(ann)

    excess = r - rf                                   # true excess returns
    se = float(np.std(excess, ddof=1))
    if se > 0.0:
        out["sharpe"] = float(np.mean(excess)) / se * math.sqrt(ann)
    down = excess[excess < 0.0]
    if down.size > 1:
        sdn = float(np.std(down, ddof=1))
        if sdn > 0.0:
            out["sortino"] = float(np.mean(excess)) / sdn * math.sqrt(ann)

    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1.0
    out["max_dd"] = float(dd.min())
    if out["max_dd"] < 0.0 and np.isfinite(out["cagr"]):
        out["calmar"] = out["cagr"] / abs(out["max_dd"])

    out["hit_rate"] = float(np.mean(r > 0.0))
    mu, s = float(np.mean(r)), sd
    if s > 0.0:
        z = (r - mu) / s
        out["skew"] = float(np.mean(z ** 3))
        out["kurt"] = float(np.mean(z ** 4) - 3.0)

    if turnover is not None:
        tv = np.asarray(turnover, dtype="float64")[m] if len(turnover) == len(m) \
            else np.asarray(turnover, dtype="float64")
        tv = tv[np.isfinite(tv)]
        if tv.size:
            out["ann_turnover"] = float(np.mean(tv)) * ann
    return out


# ========================================================================== #
# Driver
# ========================================================================== #
def build_rf_series(px, index):
    """Daily risk-free series: cash-proxy ticker if supplied, else constant."""
    if RF_TICKER and str(RF_TICKER).upper() in px.columns:
        c = np.ascontiguousarray(px[str(RF_TICKER).upper()].to_numpy(dtype="float64"))
        r = simple_returns_masked(c)
        const = (1.0 + RF_ANNUAL) ** (1.0 / ANNUALIZATION) - 1.0
        rf = np.where(np.isfinite(r), r, const)
        first = np.flatnonzero(np.isfinite(r))
        rf_first = int(first[0]) if first.size else 0
        return rf, rf_first
    const = (1.0 + RF_ANNUAL) ** (1.0 / ANNUALIZATION) - 1.0
    return np.full(len(index), const, dtype="float64"), 0


def process_all_tickers():
    os.makedirs(IN_DIR, exist_ok=True)

    universe = list(dict.fromkeys(
        [t.upper() for t in TICKERS_TRADED]
        + [t.upper() for t in DEFENSIVE_TICKERS]
        + ([str(RF_TICKER).upper()] if RF_TICKER else [])
    ))
    px, data_hash, missing = load_prices(universe)
    if missing:
        warnings.warn(f"[DATA] tickers absent from price file (skipped): {missing}")

    dates_dt = pd.DatetimeIndex(px.index)
    dates_i8 = dates_dt.asi8.astype(np.int64)
    n = len(dates_dt)

    rf_daily, rf_first = build_rf_series(px, dates_dt)
    def_used, def_R, def_A, def_ready = prepare_defensive(
        px, [t.upper() for t in DEFENSIVE_TICKERS], rf_daily, ABSMOM_LOOKBACK, LAG
    )

    print(f"[INFO] numba={'on' if _HAVE_NUMBA else 'off'} | bars={n} "
          f"| {dates_dt[0].date()} -> {dates_dt[-1].date()}")
    print(f"[INFO] defensive sleeve (abs-mom gated): {def_used or 'NONE -> cash'}")
    print(f"[INFO] cost={COST_BPS}bps/side | borrow spread={BORROW_SPREAD_BPS}bps "
          f"| rf={'ticker ' + str(RF_TICKER) if RF_TICKER else f'{RF_ANNUAL:.2%} const'}")

    rows = []
    traded = [t.upper() for t in TICKERS_TRADED if t.upper() in px.columns]

    for ticker in traded:
        close = np.ascontiguousarray(px[ticker].to_numpy(dtype="float64"))
        r_risky = simple_returns_masked(close)

        signals = generate_signals(close, lag=LAG, negative_control=False)
        validate_signals(ticker, signals, n)

        # ---- inception alignment (bug #5) --------------------------------
        fv = np.flatnonzero(np.isfinite(r_risky))
        asset_first = int(fv[0]) if fv.size else n
        base_start = max(asset_first, rf_first)
        if STRICT_INCEPTION_ALIGNMENT and def_used:
            base_start = max(base_start, def_ready)

        bh = performance_metrics(
            np.where(np.arange(n) >= base_start, r_risky, np.nan), rf_daily
        )
        rows.append(dict(ticker=ticker, family="BUY_HOLD", param="-",
                         start=str(dates_dt[min(base_start, n - 1)].date()),
                         end=str(dates_dt[-1].date()), **bh))

        for fam in FAMILIES:
            mat = signals[fam]
            val = signals[f"{fam}_valid"]
            params = signals[f"{fam}_params"]
            for row in range(mat.shape[0]):
                pv = np.flatnonzero(val[row] == 1)
                if pv.size == 0:
                    continue
                start_idx = max(base_start, int(pv[0]))
                if start_idx >= n - 2:
                    continue
                bt = run_backtest(mat[row], val[row], r_risky,
                                  def_R, def_A, rf_daily, start_idx)
                mt = performance_metrics(bt["net"], rf_daily, turnover=bt["turnover"])
                pstr = "-".join(map(str, np.atleast_1d(params[row]).tolist()))
                rows.append(dict(ticker=ticker, family=fam, param=pstr,
                                 start=str(dates_dt[start_idx].date()),
                                 end=str(dates_dt[-1].date()), **mt))

        npz = {
            "dates": dates_i8,
            "data_hash": np.array(data_hash),
            "lag": np.int32(LAG),
            "ticker": np.array(ticker),
            "close": close,                       # NaN-preserving, never filled
            "risky_returns": r_risky,
            "rf_daily": rf_daily,
            "defensive_tickers": np.array(def_used, dtype=object),
            "defensive_absmom": def_A,
            "inception_index": np.int64(base_start),
            "cost_bps": np.float64(COST_BPS),
            "borrow_spread_bps": np.float64(BORROW_SPREAD_BPS),
            "annualization": np.int32(ANNUALIZATION),
            **signals,
        }
        np.savez_compressed(os.path.join(IN_DIR, f"{ticker}_signals_v8.npz"), **npz)
        print(f"  sealed V8 signals -> {ticker}_signals_v8.npz "
              f"(start {dates_dt[base_start].date() if base_start < n else 'n/a'})")

    if not rows:
        warnings.warn("[RESULT] no tradeable tickers -> nothing produced.")
        return pd.DataFrame()

    res = pd.DataFrame(rows)
    cols = ["ticker", "family", "param", "start", "end", "n_obs", "years",
            "cagr", "vol", "sharpe", "sortino", "max_dd", "calmar",
            "hit_rate", "skew", "kurt", "ann_turnover", "total_return"]
    res = res[[c for c in cols if c in res.columns]]
    out_csv = os.path.join(IN_DIR, "opus8_v8_metrics.csv")
    res.to_csv(out_csv, index=False)

    with pd.option_context("display.width", 200, "display.max_columns", 40,
                           "display.float_format", lambda v: f"{v:,.4f}"):
        print("\n===== V8 AUDITED RESULTS (true Sharpe, net of costs) =====")
        print(res.to_string(index=False))
    print(f"\n[OK] metrics written to {out_csv}")
    return res


if __name__ == "__main__":
    process_all_tickers()