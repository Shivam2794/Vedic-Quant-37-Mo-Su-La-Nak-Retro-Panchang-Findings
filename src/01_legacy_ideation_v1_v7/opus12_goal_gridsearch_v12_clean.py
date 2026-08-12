"""
opus12_goal_gridsearch_v12.py  --  BRUTAL MULTIPOINT QUALITY INSPECTOR EDITION
=============================================================================
Grid-search of a dual-momentum / ERC (equal-risk-contribution) tactical
allocation strategy.

ALL KNOWN FATAL BUGS OF PREVIOUS VERSIONS ARE FIXED HERE:

 1. NO `.fillna(0)` ANYWHERE.  Missing history stays NaN; an asset can only
    receive weight on a day where it has a *complete* finite lookback window
    of real returns (post-inception).  Phantom pre-inception assets are
    impossible: weights are hard-masked by an availability mask and an
    assertion verifies that no weight is ever placed on a non-finite return.

 2. TRUE SHARPE RATIO:  mean(excess)/std(excess) * sqrt(252) with
    excess = net_daily_return - daily_risk_free.  (Not CAGR/vol.)

 3. TRANSACTION COSTS + BORROWING SPREAD:  per-asset bps charged on the
    absolute change of the *effective* (post-leverage) weights, plus an
    explicit financing cost (rf + spread) on any negative cash balance and
    interest earned (rf) on any positive cash balance.

 4. ABSOLUTE MOMENTUM ON *ALL* ASSETS, INCLUDING THE DEFENSIVE POOL:
    an asset must beat the compounded risk-free rate over the lookback
    window to be held.  If nothing qualifies, the sleeve goes to cash.

 5. INCEPTION ALIGNMENT ENFORCED:  every grid combination is evaluated over
    one identical, common evaluation window that begins only after every
    asset used by *any* pool has enough real history for the longest
    lookback / SMA / vol window.  No look-ahead: all signals are computed
    from data up to and including day t and applied to day t+1 returns.

The script is fully self-contained (built-in ERC optimizer) and executable:
if the frozen parquet matrix is not found, a deterministic synthetic
universe with realistic staggered inception dates is generated so that the
logic can still be exercised end-to-end.
"""

from __future__ import annotations

import itertools
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --------------------------------------------------------------------------- #
#                               CONFIGURATION                                 #
# --------------------------------------------------------------------------- #
DATA_DIR = os.environ.get(
    "OPUS_DATA_DIR",
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data",
)
PARQUET_NAME = "frozen_universe_data.parquet"
RESULTS_NAME = "opus12_gridsearch_results.csv"

ASSETS = ["SPY", "QQQ", "TQQQ", "UPRO", "TLT", "GLD", "BTC-USD"]

# One-way transaction cost in basis points (per unit of turnover, per asset)
BPS_COSTS = {
    "SPY": 1.0,
    "QQQ": 1.0,
    "TQQQ": 2.0,
    "UPRO": 3.0,
    "TLT": 1.0,
    "GLD": 1.0,
    "BTC-USD": 15.0,
}

TARGET_VOL = 0.15          # annualised vol target
MAX_LEV = 1.0              # hard leverage cap (1.0 => no borrowing)
MIN_LEV = 0.0
VOL_WINDOW = 20            # trailing window for realised vol (days)
TRADING_DAYS = 252

RF_ANNUAL = 0.02           # risk-free (annualised, simple compounding)
BORROW_SPREAD = 0.0075     # financing spread over rf on borrowed cash

REGIME_SIGNAL_ASSET = "SPY"

RISK_ON_POOLS = [
    ["QQQ", "SPY", "TQQQ"],
    ["TQQQ", "UPRO"],
    ["QQQ", "TQQQ"],
    ["SPY", "UPRO"],
]

RISK_OFF_POOLS = [
    ["GLD", "TLT"],
    ["TLT"],
    ["GLD"],
]

LOOKBACKS = [20, 40, 60, 90, 120]
SMA_WINDOWS = [50, 100, 150, 200, 250]

RIDGE = 1e-10              # covariance regularisation
ERC_MAX_ITER = 500
ERC_TOL = 1e-12


# --------------------------------------------------------------------------- #
#                        ERC / RISK-PARITY OPTIMIZER                          #
# --------------------------------------------------------------------------- #
def erc_weights_from_cov(cov: np.ndarray) -> np.ndarray:
    """
    Long-only, fully-invested Equal-Risk-Contribution weights.

    Solves the fixed point  w_i * (Sigma w)_i = const  for all i via the
    standard convergent multiplicative iteration  w <- normalise(1 / (Sigma w)).
    Falls back to inverse-volatility (and then equal weight) on degeneracy.
    """
    n = cov.shape[0]
    if n == 0:
        return np.zeros(0, dtype=float)
    if n == 1:
        return np.ones(1, dtype=float)

    cov = np.asarray(cov, dtype=float)
    cov = 0.5 * (cov + cov.T)
    diag = np.diag(cov).copy()
    if not np.all(np.isfinite(cov)) or np.any(diag <= 0.0):
        return np.full(n, 1.0 / n)

    # Regularise for numerical stability
    cov = cov + np.eye(n) * (RIDGE + 1e-12 * float(np.mean(diag)))

    inv_vol = 1.0 / np.sqrt(diag)
    w = inv_vol / inv_vol.sum()          # sensible warm start

    for _ in range(ERC_MAX_ITER):
        m = cov @ w
        if not np.all(np.isfinite(m)) or np.any(m <= 0.0):
            break
        w_new = 1.0 / m
        s = w_new.sum()
        if not np.isfinite(s) or s <= 0.0:
            break
        w_new /= s
        if np.max(np.abs(w_new - w)) < ERC_TOL:
            w = w_new
            break
        w = w_new

    if (not np.all(np.isfinite(w))) or w.sum() <= 0.0 or np.any(w < -1e-12):
        w = inv_vol / inv_vol.sum()

    w = np.clip(w, 0.0, None)
    total = w.sum()
    return w / total if total > 0 else np.full(n, 1.0 / n)


# --------------------------------------------------------------------------- #
#                                DATA LOADING                                 #
# --------------------------------------------------------------------------- #
def _load_parquet() -> tuple[pd.DataFrame, pd.DataFrame] | None:
    path = os.path.join(DATA_DIR, PARQUET_NAME)
    if not os.path.isfile(path):
        return None
    try:
        df = pd.read_parquet(path)
    except Exception as exc:                                # pragma: no cover
        print(f"[WARN] Could not read {path}: {exc}")
        return None

    try:
        if isinstance(df.index, pd.MultiIndex):
            if 'Ticker' in df.index.names and 'Ticker' in df.columns:
                df = df.drop(columns=['Ticker'])
            names = [str(n) for n in df.index.names]
            date_name = next(n for n in names if n.lower() in ("date", "datetime"))
            tick_name = next(n for n in names if n.lower() in ("ticker", "symbol", "asset"))
            df = df.reset_index()
        else:
            df = df.reset_index()
            # drop duplicates if any
            df = df.loc[:,~df.columns.duplicated()]
            cols = [str(c) for c in df.columns]
            date_name = next(c for c in cols if c.lower() in ("date", "datetime", "index"))
            tick_name = next(c for c in cols if c.lower() in ("ticker", "symbol", "asset"))

        cols_lower = {str(c).lower(): c for c in df.columns}
        adj_col = cols_lower.get("adj close", cols_lower.get("adj_close", cols_lower.get("close")))
        cls_col = cols_lower.get("close", adj_col)
        if adj_col is None:
            return None

        df[date_name] = pd.to_datetime(df[date_name])
        adj = df.pivot_table(index=date_name, columns=tick_name, values=adj_col, aggfunc="last")
        cls = df.pivot_table(index=date_name, columns=tick_name, values=cls_col, aggfunc="last")
    except Exception as exc:                                # pragma: no cover
        print(f"[WARN] Unexpected parquet schema: {exc}")
        return None

    missing = [a for a in ASSETS if a not in adj.columns]
    if missing:
        print(f"[WARN] Parquet missing assets {missing} -> falling back to synthetic data.")
        return None

    adj = adj.reindex(columns=ASSETS).sort_index()
    cls = cls.reindex(columns=ASSETS).sort_index()
    return adj, cls


def _synthetic_universe() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deterministic synthetic universe with realistic staggered inceptions."""
    print("[INFO] Frozen matrix not found -> generating deterministic synthetic universe.")
    rng = np.random.default_rng(20240612)
    dates = pd.bdate_range("1999-01-04", "2024-12-31")
    T = len(dates)

    mkt = rng.normal(0.00030, 0.0110, T)          # broad equity factor
    rates = rng.normal(0.00008, 0.0075, T)        # duration factor
    gold = rng.normal(0.00016, 0.0090, T)
    crypto = rng.normal(0.00180, 0.0400, T)

    spy = 1.00 * mkt + rng.normal(0.0, 0.0025, T)
    qqq = 1.18 * mkt + rng.normal(0.0, 0.0045, T)
    daily_fee = 0.0095 / TRADING_DAYS
    tqqq = 3.0 * qqq - daily_fee
    upro = 3.0 * spy - daily_fee
    tlt = -0.20 * mkt + 1.0 * rates
    gld = 0.05 * mkt + 1.0 * gold
    btc = 0.40 * mkt + 1.0 * crypto

    rets = {
        "SPY": spy, "QQQ": qqq, "TQQQ": tqqq, "UPRO": upro,
        "TLT": tlt, "GLD": gld, "BTC-USD": btc,
    }
    inception = {
        "SPY": "1999-01-04", "QQQ": "1999-03-10", "TLT": "2002-07-30",
        "GLD": "2004-11-18", "UPRO": "2009-06-25", "TQQQ": "2010-02-11",
        "BTC-USD": "2014-09-17",
    }

    prices = {}
    for a in ASSETS:
        r = np.clip(rets[a], -0.60, 0.60)
        p = 100.0 * np.cumprod(1.0 + r)
        s = pd.Series(p, index=dates, dtype=float)
        s.loc[s.index < pd.Timestamp(inception[a])] = np.nan   # NO fillna: real NaNs
        prices[a] = s

    adj = pd.DataFrame(prices, columns=ASSETS)
    return adj, adj.copy()


def load_universe() -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DatetimeIndex]:
    """
    Returns
    -------
    R        : (N, T) simple returns, NaN where unavailable (never filled)
    P        : (N, T) adjusted close levels, NaN where unavailable
    rf_daily : (T,)   daily risk-free rate
    dates    : DatetimeIndex length T
    """
    loaded = _load_parquet()
    adj, _cls = loaded if loaded is not None else _synthetic_universe()

    adj = adj.astype(float).sort_index()
    adj = adj[~adj.index.duplicated(keep="last")]
    # Drop days with no data at all; keep NaNs elsewhere (inception integrity).
    adj = adj.dropna(how="all")

    rets = adj.pct_change()
    # A return is only valid if both endpoints are real prices.
    valid = adj.notna() & adj.shift(1).notna()
    rets = rets.where(valid)

    P = adj.to_numpy(dtype=float).T.copy()
    R = rets.to_numpy(dtype=float).T.copy()
    dates = pd.DatetimeIndex(adj.index)

    rf_d = (1.0 + RF_ANNUAL) ** (1.0 / TRADING_DAYS) - 1.0
    rf_daily = np.full(len(dates), rf_d, dtype=float)

    return R, P, rf_daily, dates


# --------------------------------------------------------------------------- #
#                       POOL WEIGHT CONSTRUCTION (SIGNAL)                     #
# --------------------------------------------------------------------------- #
def _rolling_finite_count(finite: np.ndarray, window: int) -> np.ndarray:
    """count[:, t] = number of finite obs in (t-window, t] inclusive of t."""
    k, T = finite.shape
    out = np.zeros((k, T), dtype=float)
    if window > T:
        return out
    cs = np.concatenate([np.zeros((k, 1)), np.cumsum(finite.astype(float), axis=1)], axis=1)
    out[:, window - 1:] = cs[:, window:] - cs[:, :-window]
    return out


def pool_signal_weights(
    R: np.ndarray,
    P: np.ndarray,
    rf_daily: np.ndarray,
    asset_idx: list[int],
    lookback: int,
    start_t: int,
) -> np.ndarray:
    """
    ERC weights for one pool, decided using information up to and including
    day t (to be *held* on day t+1).  Absolute-momentum filtered.

    An asset is eligible on day t iff
      * it has `lookback` consecutive finite daily returns ending at t
        (i.e. it is fully post-inception), AND
      * finite prices at t and t-lookback, AND
      * total return over the lookback exceeds the compounded risk-free rate
        over the same window (ABSOLUTE MOMENTUM -- applied to defensive
        assets too).

    Weights of ineligible assets are exactly zero; the un-allocated remainder
    is cash.  Returned array is (N, T) and never places weight on a NaN return.
    """
    N, T = R.shape
    W = np.zeros((N, T), dtype=float)
    k = len(asset_idx)
    if k == 0 or lookback >= T:
        return W

    sub_R = R[asset_idx, :]
    sub_P = P[asset_idx, :]

    finite_r = np.isfinite(sub_R)
    full_hist = _rolling_finite_count(finite_r, lookback) == float(lookback)

    # Absolute momentum vs compounded risk-free over the same window
    log_rf = np.cumsum(np.log1p(rf_daily))
    mom_ok = np.zeros((k, T), dtype=bool)
    t0 = max(lookback, 1)
    if t0 < T:
        p_now = sub_P[:, t0:]
        p_then = sub_P[:, : T - t0]
        with np.errstate(invalid="ignore", divide="ignore"):
            gross = p_now / p_then
        rf_gross = np.exp(log_rf[t0:] - log_rf[: T - t0])[None, :]
        ok = np.isfinite(gross) & (p_then > 0) & (gross > rf_gross)
        mom_ok[:, t0:] = ok

    eligible = full_hist & mom_ok & np.isfinite(sub_P) & finite_r

    lo = max(lookback - 1, start_t)
    for t in range(lo, T):
        rows = np.flatnonzero(eligible[:, t])
        if rows.size == 0:
            continue
        win = sub_R[np.ix_(rows, np.arange(t - lookback + 1, t + 1))]
        if not np.all(np.isfinite(win)):            # defensive: never trust
            keep = np.all(np.isfinite(win), axis=1)
            rows = rows[keep]
            win = win[keep]
            if rows.size == 0:
                continue
        if rows.size == 1:
            w = np.ones(1)
        else:
            cov = np.cov(win, rowvar=True, ddof=1)
            cov = np.atleast_2d(cov)
            var = np.diag(cov)
            good = np.isfinite(var) & (var > 0)
            if not np.any(good):
                continue
            rows = rows[good]
            cov = cov[np.ix_(good, good)]
            w = erc_weights_from_cov(cov)
        W[np.asarray(asset_idx)[rows], t] = w

    return W


# --------------------------------------------------------------------------- #
#                                  METRICS                                    #
# --------------------------------------------------------------------------- #
def performance_stats(
    net_ret: np.ndarray,
    rf: np.ndarray,
    dates: pd.DatetimeIndex,
    turnover: np.ndarray | None = None,
) -> dict:
    n = len(net_ret)
    if n < 2 or not np.all(np.isfinite(net_ret)):
        return {}
    if np.any(net_ret <= -1.0):
        return {}

    equity = np.cumprod(1.0 + net_ret)
    years = max((dates[-1] - dates[0]).days / 365.25, 1.0 / 365.25)
    cagr = equity[-1] ** (1.0 / years) - 1.0

    ex = net_ret - rf
    vol = float(np.std(net_ret, ddof=1)) * np.sqrt(TRADING_DAYS)
    ex_vol = float(np.std(ex, ddof=1)) * np.sqrt(TRADING_DAYS)
    sharpe = (float(np.mean(ex)) * TRADING_DAYS / ex_vol) if ex_vol > 0 else 0.0

    downside = np.minimum(ex, 0.0)
    dd_dev = float(np.sqrt(np.mean(downside ** 2))) * np.sqrt(TRADING_DAYS)
    sortino = (float(np.mean(ex)) * TRADING_DAYS / dd_dev) if dd_dev > 0 else 0.0

    peak = np.maximum.accumulate(equity)
    mdd = float((equity / peak - 1.0).min())
    calmar = (cagr / abs(mdd)) if mdd < 0 else np.nan

    stats = {
        "cagr": float(cagr),
        "vol": float(vol),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "mdd": mdd,
        "calmar": float(calmar) if np.isfinite(calmar) else np.nan,
        "final_equity": float(equity[-1]),
        "n_days": int(n),
        "years": float(years),
    }
    if turnover is not None and len(turnover) == n:
        stats["ann_turnover"] = float(np.mean(turnover) * TRADING_DAYS)
    return stats


# --------------------------------------------------------------------------- #
#                                   ENGINE                                    #
# --------------------------------------------------------------------------- #
def run_backtest(
    W_signal_on: np.ndarray,
    W_signal_off: np.ndarray,
    regime_signal: np.ndarray,
    R: np.ndarray,
    rf_daily: np.ndarray,
    cost_frac: np.ndarray,
    avail: np.ndarray,
    eval_start: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns (net_return, turnover, effective_leverage) full-length arrays.
    Everything is shifted so that signals from close(t) drive day t+1.
    """
    N, T = R.shape

    # ---- shift signals by one day (no look-ahead) --------------------------
    W_on = np.zeros_like(W_signal_on)
    W_off = np.zeros_like(W_signal_off)
    W_on[:, 1:] = W_signal_on[:, :-1]
    W_off[:, 1:] = W_signal_off[:, :-1]

    reg = np.full(T, -1, dtype=int)
    reg[1:] = regime_signal[:-1]

    W_hold = np.zeros((N, T), dtype=float)
    m_on = reg == 1
    m_off = reg == 0
    W_hold[:, m_on] = W_on[:, m_on]
    W_hold[:, m_off] = W_off[:, m_off]

    # ---- hard inception mask (kills phantom assets stone dead) -------------
    W_hold = np.where(avail, W_hold, 0.0)
    Rz = np.where(avail, R, 0.0)          # only zeroed where weight is 0 anyway
    assert not np.any(W_hold[~np.isfinite(R)]), "weight placed on non-finite return"

    # ---- unlevered strategy return (invested + cash) ----------------------
    inv = W_hold.sum(axis=0)
    r_unlev = np.einsum("it,it->t", W_hold, Rz) + (1.0 - inv) * rf_daily

    # ---- volatility targeting on strictly lagged information --------------
    sig = (
        pd.Series(r_unlev)
        .rolling(VOL_WINDOW, min_periods=VOL_WINDOW)
        .std(ddof=1)
        .shift(1)
        .to_numpy()
        * np.sqrt(TRADING_DAYS)
    )
    lev = np.where(np.isfinite(sig) & (sig > 0), TARGET_VOL / np.maximum(sig, 1e-12), MIN_LEV)
    lev = np.clip(lev, MIN_LEV, MAX_LEV)
    lev = np.where(np.isfinite(lev), lev, MIN_LEV)

    W_eff = W_hold * lev[None, :]

    # ---- transaction costs on effective weight changes ---------------------
    prev = np.zeros((N, T), dtype=float)
    prev[:, 1:] = W_eff[:, :-1]
    dW = np.abs(W_eff - prev)
    turnover = dW.sum(axis=0)
    cost = (dW * cost_frac[:, None]).sum(axis=0)

    # ---- cash / financing --------------------------------------------------
    cash_w = 1.0 - W_eff.sum(axis=0)
    borrow_daily = (1.0 + BORROW_SPREAD) ** (1.0 / TRADING_DAYS) - 1.0
    cash_ret = np.where(cash_w >= 0.0, cash_w * rf_daily, cash_w * (rf_daily + borrow_daily))

    net = np.einsum("it,it->t", W_eff, Rz) + cash_ret - cost
    net[:eval_start] = 0.0
    return net, turnover, lev


def main() -> None:
    R, P, rf_daily, dates = load_universe()
    N, T = R.shape
    print(f"[INFO] Universe: {N} assets x {T} days  ({dates[0].date()} -> {dates[-1].date()})")

    finite_r = np.isfinite(R)
    if not finite_r.any():
        print("[FATAL] No finite returns in universe.")
        return

    first_valid = np.array(
        [int(np.argmax(finite_r[i])) if finite_r[i].any() else T for i in range(N)]
    )
    for i, a in enumerate(ASSETS):
        fv = first_valid[i]
        print(f"        {a:<8} first return: {dates[fv].date() if fv < T else 'NEVER'}")

    # ---- validate pools ----------------------------------------------------
    def valid_pool(pool: list[str]) -> bool:
        return all(a in ASSETS and first_valid[ASSETS.index(a)] < T for a in pool)

    ro_pools = [p for p in RISK_ON_POOLS if valid_pool(p)]
    roff_pools = [p for p in RISK_OFF_POOLS if valid_pool(p)]
    if not ro_pools or not roff_pools:
        print("[FATAL] No usable pools given available history.")
        return
    if REGIME_SIGNAL_ASSET not in ASSETS or first_valid[ASSETS.index(REGIME_SIGNAL_ASSET)] >= T:
        print("[FATAL] Regime signal asset unavailable.")
        return

    # ---- INCEPTION-ALIGNED COMMON EVALUATION WINDOW ------------------------
    used_assets = sorted(set(a for p in ro_pools for a in p) | set(a for p in roff_pools for a in p))
    max_lb = max(LOOKBACKS)
    max_sma = max(SMA_WINDOWS)
    sig_idx = ASSETS.index(REGIME_SIGNAL_ASSET)

    # need max_lb finite returns AND a price max_lb days back  -> +max_lb bars
    need_assets = max(first_valid[ASSETS.index(a)] + max_lb for a in used_assets)
    need_sma = first_valid[sig_idx] + max_sma            # SMA on adjusted closes
    signal_ready = max(need_assets, need_sma)            # last index of warm-up (signal valid at t)
    eval_start = signal_ready + VOL_WINDOW + 2           # +1 shift, +vol warm-up
    if eval_start >= T - TRADING_DAYS:
        print("[FATAL] Not enough history for an inception-aligned evaluation window.")
        return

    comp_start = max(0, eval_start - VOL_WINDOW - 3)     # weights needed slightly earlier
    print(
        f"[INFO] Common evaluation window: {dates[eval_start].date()} -> {dates[-1].date()} "
        f"({T - eval_start} days, aligned on assets {used_assets})"
    )

    avail = finite_r  # availability == real, finite, post-inception return

    # ---- pre-compute ERC + absolute-momentum weights per (pool, lookback) --
    cache: dict[tuple[tuple[str, ...], int], np.ndarray] = {}
    all_pools = {tuple(sorted(set(p))): [ASSETS.index(a) for a in sorted(set(p))]
                 for p in ro_pools + roff_pools}
    print(f"[INFO] Pre-computing weights for {len(all_pools)} pools x {len(LOOKBACKS)} lookbacks...")
    for key, idx in all_pools.items():
        for lb in LOOKBACKS:
            cache[(key, lb)] = pool_signal_weights(R, P, rf_daily, idx, lb, comp_start)

    cost_frac = np.array([BPS_COSTS.get(a, 5.0) / 10000.0 for a in ASSETS], dtype=float)
    sig_px = P[sig_idx]

    # ---- SMA regimes (cached per window) -----------------------------------
    regimes: dict[int, np.ndarray] = {}
    px_series = pd.Series(sig_px)
    for w in SMA_WINDOWS:
        sma = px_series.rolling(w, min_periods=w).mean().to_numpy()
        reg = np.full(T, -1, dtype=int)
        ok = np.isfinite(sma) & np.isfinite(sig_px)
        reg[ok] = (sig_px[ok] > sma[ok]).astype(int)
        regimes[w] = reg

    combos = list(itertools.product(SMA_WINDOWS, LOOKBACKS, range(len(ro_pools)), range(len(roff_pools))))
    print(f"[INFO] Sweeping {len(combos)} combinations...")

    eval_rf = rf_daily[eval_start:]
    eval_dates = dates[eval_start:]

    results = []
    for sma_w, lb, i_on, i_off in combos:
        ro_pool, roff_pool = ro_pools[i_on], roff_pools[i_off]
        W_on = cache[(tuple(sorted(set(ro_pool))), lb)]
        W_off = cache[(tuple(sorted(set(roff_pool))), lb)]

        net, turnover, lev = run_backtest(
            W_on, W_off, regimes[sma_w], R, rf_daily, cost_frac, avail, eval_start
        )

        eval_net = net[eval_start:]
        if np.any(~np.isfinite(eval_net)) or np.any(eval_net <= -1.0):
            continue

        stats = performance_stats(eval_net, eval_rf, eval_dates, turnover[eval_start:])
        if not stats:
            continue

        stats.update(
            {
                "sma": sma_w,
                "lookback": lb,
                "risk_on": "|".join(ro_pool),
                "risk_off": "|".join(roff_pool),
                "avg_leverage": float(np.mean(lev[eval_start:])),
                "exposure": float(np.mean(np.abs(net[eval_start:]) > 0)),
            }
        )
        results.append(stats)

    if not results:
        print("[FATAL] No valid results produced.")
        return

    cols = [
        "sma", "lookback", "risk_on", "risk_off", "cagr", "vol", "sharpe",
        "sortino", "mdd", "calmar", "ann_turnover", "avg_leverage",
        "final_equity", "n_days", "years",
    ]
    df = pd.DataFrame(results)
    df = df.reindex(columns=[c for c in cols if c in df.columns])
    df = df.sort_values("sharpe", ascending=False).reset_index(drop=True)

    # ---- benchmark: buy & hold regime asset over the identical window ------
    bench = np.where(np.isfinite(R[sig_idx, eval_start:]), R[sig_idx, eval_start:], 0.0)
    bench_stats = performance_stats(bench, eval_rf, eval_dates)

    print("\n--- BEST STRATEGIES (V12, inception-aligned, net of costs) ---")
    with pd.option_context("display.width", 220, "display.max_columns", 50):
        print(df.head(10).to_string(index=False, float_format=lambda x: f"{x:,.4f}"))

    if bench_stats:
        print(
            f"\nBenchmark {REGIME_SIGNAL_ASSET} buy&hold  "
            f"CAGR={bench_stats['cagr']:.4f}  Sharpe={bench_stats['sharpe']:.4f}  "
            f"Vol={bench_stats['vol']:.4f}  MaxDD={bench_stats['mdd']:.4f}"
        )

    out_dir = DATA_DIR if (os.path.isdir(DATA_DIR) and os.access(DATA_DIR, os.W_OK)) else os.getcwd()
    out_path = os.path.join(out_dir, RESULTS_NAME)
    try:
        df.to_csv(out_path, index=False)
        print(f"\n[INFO] Results written to {out_path}")
    except Exception as exc:                                # pragma: no cover
        print(f"[WARN] Could not write results: {exc}")


if __name__ == "__main__":
    main()