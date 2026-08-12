#!/usr/bin/env python3
# =============================================================================
# opus11_goal_gridsearch.py  --  AUDITED / FULLY REWRITTEN
#
# Fatal bugs from previous versions and their fixes:
#   1) .fillna(0) phantom assets  -> NaNs are NEVER filled with 0. Assets only
#      become investable after inception AND after a fully-valid estimation
#      window. Pre-inception data is masked out, never synthesised.
#   2) Wrong Sharpe (CAGR/vol)    -> Sharpe = mean(r - rf)/std(r - rf)*sqrt(252)
#      computed on daily arithmetic excess returns (ddof=1).
#   3) No costs / no borrow cost  -> Explicit one-way transaction cost on realised
#      turnover + cash earns rf, borrowed cash pays rf + spread.
#   4) No Absolute Momentum on defensive assets -> Every defensive (risk-off)
#      asset must beat the risk-free rate over the lookback or its sleeve share
#      is moved to T-bills (cash).
#   5) Inception alignment ignored -> Each combo starts at the first date where
#      ALL required assets have a complete estimation window and the SPY SMA is
#      fully formed. A second, global "common window" (aligned across the entire
#      grid) is also reported so combos are ranked apples-to-apples.
#
# Self-contained: no imports from the buggy opus10_* modules. If the frozen
# universe parquet is unavailable, a deterministic synthetic panel with
# staggered inception dates is generated so the script always executes.
# =============================================================================
from __future__ import annotations

import itertools
import math
import os
import warnings
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

# ----------------------------- configuration --------------------------------
TRADING_DAYS = 252

DATA_DIR = os.environ.get(
    "OPUS_DATA_DIR",
    r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data",
)
PARQUET_NAME = "frozen_universe_data.parquet"
OUT_CSV = "opus11_gridsearch_results.csv"

ONE_WAY_COST_BPS = 10.0        # bps of traded notional, charged one-way
BORROW_SPREAD_ANNUAL = 0.0100  # annual spread over rf paid on borrowed cash
MAX_GROSS_LEVERAGE = 1.0       # gross exposure cap of the invested sleeve
RF_ANNUAL_FALLBACK = 0.02      # used only if no cash proxy exists in the data

COV_SHRINK = 0.10              # shrink covariance toward its diagonal
COV_RIDGE = 1e-12              # numerical floor on variances
FFILL_LIMIT = 5               # forward-fill holiday gaps *inside* an asset's life

APPLY_ABS_MOM_RISK_ON = False  # regime filter already gates the risk-on sleeve
APPLY_ABS_MOM_RISK_OFF = True  # MANDATORY absolute momentum on defensives

MIN_OBS_FULL = 500             # min daily observations to report a combo
MIN_OBS_COMMON = 250           # min observations inside the common window

SMA_WINDOWS: List[int] = [50, 100, 150, 200, 250, 300]
LOOKBACKS: List[int] = [20, 40, 60, 90, 120]

RISK_ON_POOLS: List[List[str]] = [
    ["TQQQ", "UPRO"],
    ["QQQ", "SPY"],
    ["QQQ", "SPY", "TQQQ"],
    ["UPRO", "QQQ"],
]
RISK_OFF_POOLS: List[List[str]] = [
    ["GLD", "TLT"],
    ["GLD"],
    ["TLT"],
    ["BTC-USD", "TLT"],
    ["BTC-USD", "GLD", "TLT"],
]
SIGNAL_TICKER = "SPY"
CASH_PROXY_CANDIDATES = ["^IRX", "IRX", "BIL", "SGOV", "SHV"]

warnings.filterwarnings("ignore", category=RuntimeWarning)


# ------------------------------ data loading --------------------------------
def _pick_price_column(columns: Sequence[str]) -> Optional[str]:
    for cand in ("Adj Close", "adj_close", "AdjClose", "adjclose",
                 "Close", "close", "PX_LAST", "price"):
        if cand in columns:
            return cand
    return None


def _clean_price_series(s: pd.Series, ffill_limit: int = FFILL_LIMIT) -> pd.Series:
    """Forward-fill only *inside* the asset's own life span. Never before
    inception, never after the last observation -> no phantom assets."""
    s = pd.to_numeric(s, errors="coerce").astype(float)
    s = s.where(s > 0.0)  # non-positive prices are invalid
    first, last = s.first_valid_index(), s.last_valid_index()
    if first is None:
        return s
    out = s.copy()
    out.loc[first:last] = s.loc[first:last].ffill(limit=ffill_limit)
    return out


def load_price_panel(data_dir: str) -> Tuple[pd.DataFrame, str]:
    """Returns (wide price DataFrame indexed by date, source tag)."""
    path = os.path.join(data_dir, PARQUET_NAME)
    if os.path.isfile(path):
        raw = pd.read_parquet(path)
        if isinstance(raw.index, pd.MultiIndex):
            names = [n if n is not None else f"level_{i}"
                     for i, n in enumerate(raw.index.names)]
            raw = raw.copy()
            raw.index = raw.index.set_names(names)
            tick_lvl = next((n for n in names if str(n).lower()
                             in ("ticker", "symbol", "asset")), names[-1])
            col = _pick_price_column(list(raw.columns))
            if col is None:
                raise ValueError(f"No usable price column in {path}: {list(raw.columns)}")
            prices = raw[col].unstack(tick_lvl)
        else:
            col = _pick_price_column(list(raw.columns))
            if col is not None and raw.columns.size <= 3:
                raise ValueError("Long-format frame without a ticker index level.")
            prices = raw
        prices.index = pd.to_datetime(prices.index)
        prices = prices.sort_index()
        prices = prices[~prices.index.duplicated(keep="last")]
        prices = prices.apply(_clean_price_series)
        prices = prices.dropna(axis=1, how="all")
        if prices.shape[0] > 100 and prices.shape[1] > 0:
            return prices, f"parquet:{path}"
        raise ValueError("Parquet loaded but contains no usable history.")
    return make_synthetic_prices(), "synthetic"


def make_synthetic_prices(seed: int = 7, n_days: int = 5200) -> pd.DataFrame:
    """Deterministic fallback panel with realistic staggered inception dates."""
    idx = pd.bdate_range("2003-01-02", periods=n_days)
    # ticker -> (inception, mu, vol, beta_to_market)
    spec = {
        "SPY":     ("2003-01-02", 0.085, 0.180, 1.00),
        "QQQ":     ("2003-01-02", 0.110, 0.225, 0.95),
        "TLT":     ("2003-01-02", 0.040, 0.135, -0.20),
        "GLD":     ("2004-11-18", 0.070, 0.170, 0.05),
        "UPRO":    ("2009-06-25", 0.170, 0.520, 0.90),
        "TQQQ":    ("2010-02-11", 0.200, 0.600, 0.90),
        "BTC-USD": ("2014-09-17", 0.350, 0.750, 0.15),
        "BIL":     ("2007-05-30", 0.018, 0.002, 0.00),
    }
    rng = np.random.default_rng(seed)
    mkt = rng.standard_normal(n_days)
    data: Dict[str, pd.Series] = {}
    for tk, (start, mu, vol, beta) in spec.items():
        idio = rng.standard_normal(n_days)
        b = float(np.clip(beta, -1.0, 1.0))
        shock = b * mkt + math.sqrt(max(1.0 - b * b, 0.0)) * idio
        r = mu / TRADING_DAYS + (vol / math.sqrt(TRADING_DAYS)) * shock
        p = 100.0 * np.cumprod(1.0 + r)
        s = pd.Series(p, index=idx, dtype=float)
        s[s.index < pd.Timestamp(start)] = np.nan
        data[tk] = s
    return pd.DataFrame(data)


def build_risk_free(prices: pd.DataFrame) -> Tuple[np.ndarray, str]:
    """Daily simple risk-free rate aligned to the price index."""
    n = len(prices.index)
    for tk in CASH_PROXY_CANDIDATES:
        if tk not in prices.columns:
            continue
        s = prices[tk].dropna()
        if s.empty:
            continue
        if tk in ("^IRX", "IRX"):  # annualised yield in percent
            y = (prices[tk] / 100.0).clip(lower=0.0, upper=0.25)
            y = y.ffill().bfill()
            rf = (1.0 + y.values) ** (1.0 / TRADING_DAYS) - 1.0
            return rf.astype(float), f"yield:{tk}"
        r = prices[tk].pct_change()
        med = float(np.nanmedian(np.abs(r.values)))
        if not np.isfinite(med) or med > 0.005:  # too volatile to be a bill proxy
            continue
        rf = r.fillna(0.0).clip(lower=-0.001, upper=0.001).values
        # extend flat outside the proxy's life using its own mean
        mean_r = float(np.nanmean(r.values))
        mask = ~np.isfinite(rf) | (r.isna().values)
        rf = np.where(mask, mean_r if np.isfinite(mean_r) else 0.0, rf)
        return rf.astype(float), f"etf:{tk}"
    flat = (1.0 + RF_ANNUAL_FALLBACK) ** (1.0 / TRADING_DAYS) - 1.0
    return np.full(n, flat, dtype=float), f"constant:{RF_ANNUAL_FALLBACK:.4f}"


# -------------------------------- ERC solver --------------------------------
def erc_weights(cov: np.ndarray, max_iter: int = 500, tol: float = 1e-12) -> np.ndarray:
    """Equal Risk Contribution weights (long-only, sum to 1) via cyclical
    coordinate descent on x_i * (Sigma x)_i = const."""
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if n == 0:
        return np.zeros(0)
    if n == 1:
        return np.ones(1)

    var = np.diag(cov).copy()
    if not np.all(np.isfinite(var)) or np.any(var <= 0.0):
        return np.full(n, 1.0 / n)

    vol = np.sqrt(var)
    x = 1.0 / vol
    x = x / x.sum()
    target = 1.0 / n

    for _ in range(max_iter):
        x_prev = x.copy()
        for i in range(n):
            a = var[i]
            b = float(cov[i].dot(x) - a * x[i])
            disc = b * b + 4.0 * a * target
            if disc <= 0.0 or a <= 0.0:
                continue
            x[i] = (-b + math.sqrt(disc)) / (2.0 * a)
        s = x.sum()
        if not np.isfinite(s) or s <= 0.0:
            return np.full(n, 1.0 / n)
        x = x / s
        if np.max(np.abs(x - x_prev)) < tol:
            break

    x = np.clip(x, 0.0, None)
    s = x.sum()
    if not np.isfinite(s) or s <= 0.0:
        return np.full(n, 1.0 / n)
    return x / s


def shrunk_cov(window: np.ndarray) -> np.ndarray:
    """Sample covariance with diagonal shrinkage + ridge (window is T x k)."""
    k = window.shape[1]
    if window.shape[0] < 2:
        return np.eye(k)
    cov = np.cov(window, rowvar=False, ddof=1)
    cov = np.atleast_2d(np.asarray(cov, dtype=float))
    if cov.shape != (k, k):
        cov = np.eye(k) * float(np.nanvar(window, ddof=1))
    diag = np.diag(np.diag(cov))
    cov = (1.0 - COV_SHRINK) * cov + COV_SHRINK * diag
    cov = cov + np.eye(k) * COV_RIDGE
    d = np.diag(cov).copy()
    d[~np.isfinite(d) | (d <= 0.0)] = COV_RIDGE
    np.fill_diagonal(cov, d)
    cov[~np.isfinite(cov)] = 0.0
    return cov


# ------------------------------- performance --------------------------------
def max_drawdown(equity: np.ndarray) -> float:
    """Max drawdown of an equity curve that starts at 1.0 (returns <= 0)."""
    if equity.size == 0:
        return 0.0
    curve = np.concatenate(([1.0], equity))
    peak = np.maximum.accumulate(curve)
    dd = curve / peak - 1.0
    return float(np.min(dd))


def perf_stats(rets: np.ndarray, rf: np.ndarray, prefix: str) -> Dict[str, float]:
    out = {
        f"{prefix}_n_obs": 0, f"{prefix}_years": np.nan, f"{prefix}_cagr": np.nan,
        f"{prefix}_vol": np.nan, f"{prefix}_sharpe": np.nan,
        f"{prefix}_sortino": np.nan, f"{prefix}_mdd": np.nan,
        f"{prefix}_calmar": np.nan, f"{prefix}_total_return": np.nan,
    }
    r = np.asarray(rets, dtype=float)
    f = np.asarray(rf, dtype=float)
    ok = np.isfinite(r) & np.isfinite(f)
    r, f = r[ok], f[ok]
    n = r.size
    out[f"{prefix}_n_obs"] = int(n)
    if n < 2:
        return out

    years = n / TRADING_DAYS
    equity = np.cumprod(1.0 + r)
    total = float(equity[-1])
    out[f"{prefix}_total_return"] = total - 1.0
    out[f"{prefix}_years"] = years
    out[f"{prefix}_cagr"] = (total ** (1.0 / years) - 1.0) if total > 0.0 else -1.0
    out[f"{prefix}_vol"] = float(np.std(r, ddof=1) * math.sqrt(TRADING_DAYS))

    ex = r - f                                       # TRUE excess returns
    sd = float(np.std(ex, ddof=1))
    out[f"{prefix}_sharpe"] = (float(np.mean(ex)) / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else np.nan
    neg = ex[ex < 0.0]
    if neg.size > 1:
        dsd = float(np.std(neg, ddof=1))
        out[f"{prefix}_sortino"] = (float(np.mean(ex)) / dsd * math.sqrt(TRADING_DAYS)) if dsd > 0 else np.nan
    mdd = max_drawdown(equity)
    out[f"{prefix}_mdd"] = mdd
    if mdd < 0.0 and np.isfinite(out[f"{prefix}_cagr"]):
        out[f"{prefix}_calmar"] = out[f"{prefix}_cagr"] / abs(mdd)
    return out


# --------------------------------- engine -----------------------------------
class GridEngine:
    def __init__(self, prices: pd.DataFrame, universe: Sequence[str],
                 signal_ticker: str, lookbacks: Sequence[int],
                 sma_windows: Sequence[int]):
        self.dates = prices.index
        self.T = len(self.dates)
        self.tickers = list(universe)
        self.idx_of = {tk: i for i, tk in enumerate(self.tickers)}
        self.N = len(self.tickers)

        px = prices[self.tickers]
        self.P = px.values.astype(float)
        rets = px.pct_change()
        # a return exists only if BOTH consecutive prices exist -> no phantoms
        self.R = rets.values.astype(float)
        self.R[~np.isfinite(self.R)] = np.nan

        self.rf, self.rf_source = build_risk_free(prices)
        self.rf = np.where(np.isfinite(self.rf), self.rf, 0.0)
        self.borrow_daily = BORROW_SPREAD_ANNUAL / TRADING_DAYS
        self.cost_rate = ONE_WAY_COST_BPS / 1e4

        valid = np.isfinite(self.R)
        vdf = pd.DataFrame(valid.astype(float), index=self.dates, columns=self.tickers)
        logr = pd.DataFrame(np.log1p(np.where(valid, self.R, np.nan)),
                            index=self.dates, columns=self.tickers)
        rf_log = pd.Series(np.log1p(self.rf), index=self.dates)

        self.cnt: Dict[int, np.ndarray] = {}
        self.mom_excess: Dict[int, np.ndarray] = {}
        for lb in sorted(set(int(x) for x in lookbacks)):
            self.cnt[lb] = vdf.rolling(lb, min_periods=lb).sum().values
            asset_log = logr.rolling(lb, min_periods=lb).sum().values
            cash_log = rf_log.rolling(lb, min_periods=lb).sum().values.reshape(-1, 1)
            self.mom_excess[lb] = asset_log - cash_log

        # SPY regime (signal computed at t, applied to t+1 -> no look-ahead)
        if signal_ticker not in self.idx_of:
            raise ValueError(f"Signal ticker {signal_ticker} missing from universe.")
        sig = pd.Series(self.P[:, self.idx_of[signal_ticker]], index=self.dates)
        self.regime: Dict[int, np.ndarray] = {}
        self.regime_valid: Dict[int, np.ndarray] = {}
        for w in sorted(set(int(x) for x in sma_windows)):
            sma = sig.rolling(w, min_periods=w).mean()
            ok = sma.notna().values & sig.notna().values
            self.regime[w] = (sig.values > sma.values) & ok
            self.regime_valid[w] = ok

        per = self.dates.to_period("M").values
        me = np.zeros(self.T, dtype=bool)
        if self.T > 1:
            me[:-1] = per[:-1] != per[1:]
        if self.T:
            me[-1] = True
        self.month_end = me

        self._erc_cache: Dict[Tuple[Tuple[int, ...], int, int], np.ndarray] = {}

    # -- helpers -------------------------------------------------------------
    def pool_indices(self, pool: Sequence[str]) -> Optional[Tuple[int, ...]]:
        if any(tk not in self.idx_of for tk in pool):
            return None
        return tuple(self.idx_of[tk] for tk in pool)

    def first_aligned_index(self, req: Sequence[int], lb: int, sma_w: int) -> Optional[int]:
        """Inception alignment: first t where every required asset has a FULL
        lookback window and the SMA is fully formed."""
        cnt = self.cnt[lb]
        ok = self.regime_valid[sma_w].copy()
        for i in req:
            ok &= (cnt[:, i] == lb)
        pos = np.flatnonzero(ok)
        if pos.size == 0:
            return None
        t0 = int(pos[0])
        return t0 if t0 < self.T - 1 else None

    def _erc(self, active: Tuple[int, ...], lb: int, t: int) -> np.ndarray:
        key = (active, lb, t)
        w = self._erc_cache.get(key)
        if w is None:
            window = self.R[t - lb + 1: t + 1, list(active)]
            w = erc_weights(shrunk_cov(window))
            self._erc_cache[key] = w
        return w

    def target_key(self, t: int, pool_idx: Tuple[int, ...], lb: int,
                   apply_abs_mom: bool) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
        cnt = self.cnt[lb]
        active = tuple(i for i in pool_idx if cnt[t, i] == lb)
        if apply_abs_mom:
            mom = self.mom_excess[lb]
            keep = tuple(i for i in active if np.isfinite(mom[t, i]) and mom[t, i] > 0.0)
        else:
            keep = active
        return active, keep

    def target_weights(self, t: int, lb: int, active: Tuple[int, ...],
                       keep: Tuple[int, ...]) -> Tuple[np.ndarray, float]:
        h = np.zeros(self.N, dtype=float)
        if len(active) == 0 or len(keep) == 0:
            return h, 1.0
        w = self._erc(active, lb, t) * MAX_GROSS_LEVERAGE
        keep_set = set(keep)
        for j, i in enumerate(active):
            if i in keep_set:
                h[i] = w[j]          # failed abs-mom sleeves go to cash
        return h, 1.0 - float(h.sum())

    # -- simulation ----------------------------------------------------------
    def simulate(self, sma_w: int, lb: int, ro_idx: Tuple[int, ...],
                 roff_idx: Tuple[int, ...]) -> Optional[Dict[str, object]]:
        req = tuple(sorted(set(ro_idx) | set(roff_idx)))
        t0 = self.first_aligned_index(req, lb, sma_w)
        if t0 is None:
            return None

        regime = self.regime[sma_w]
        rets = np.full(self.T, np.nan, dtype=float)

        def targets(t: int):
            risk_on = bool(regime[t])
            pool = ro_idx if risk_on else roff_idx
            abs_mom = APPLY_ABS_MOM_RISK_ON if risk_on else APPLY_ABS_MOM_RISK_OFF
            active, keep = self.target_key(t, pool, lb, abs_mom)
            return risk_on, active, keep

        risk_on, active, keep = targets(t0)
        h, c = self.target_weights(t0, lb, active, keep)
        cur_key = (risk_on, active, keep)
        pending_cost = float(np.abs(h).sum()) * self.cost_rate
        turnover_total = float(np.abs(h).sum())
        n_rebalances = 1
        ruined = False
        stale_price_days = 0

        for t in range(t0 + 1, self.T):
            r_assets = self.R[t]
            held = h != 0.0
            if np.any(held & ~np.isfinite(r_assets)):
                stale_price_days += 1
            r_eff = np.where(np.isfinite(r_assets), r_assets, 0.0)

            cash_rate = self.rf[t] + (self.borrow_daily if c < 0.0 else 0.0)
            gross = float(np.dot(h, r_eff) + c * cash_rate)
            net = (1.0 + gross) * (1.0 - pending_cost) - 1.0
            pending_cost = 0.0
            rets[t] = net

            denom = 1.0 + gross
            if not np.isfinite(denom) or denom <= 1e-8:
                ruined = True
                break
            h = h * (1.0 + r_eff) / denom
            c = c * (1.0 + cash_rate) / denom

            if t >= self.T - 1:
                break
            risk_on, active, keep = targets(t)
            new_key = (risk_on, active, keep)
            if self.month_end[t] or new_key != cur_key:
                h_t, c_t = self.target_weights(t, lb, active, keep)
                turn = float(np.abs(h_t - h).sum())
                pending_cost = turn * self.cost_rate
                turnover_total += turn
                n_rebalances += 1
                h, c = h_t, c_t
                cur_key = new_key

        return {
            "rets": rets,
            "start_idx": t0,
            "turnover": turnover_total,
            "n_rebalances": n_rebalances,
            "ruined": ruined,
            "stale_price_days": stale_price_days,
        }


# ---------------------------------- driver ----------------------------------
def optimize_and_sweep(data_dir: str = DATA_DIR) -> pd.DataFrame:
    prices, source = load_price_panel(data_dir)
    print(f"[data] source = {source}")
    print(f"[data] {prices.shape[1]} tickers | {prices.shape[0]} rows | "
          f"{prices.index[0].date()} -> {prices.index[-1].date()}")

    needed = set(SIGNAL_TICKER for _ in (0,))
    for p in RISK_ON_POOLS + RISK_OFF_POOLS:
        needed.update(p)
    missing = sorted(t for t in needed if t not in prices.columns)
    if missing:
        print(f"[warn] tickers absent from data (pools using them are skipped): {missing}")
    if SIGNAL_TICKER not in prices.columns:
        raise SystemExit(f"[fatal] signal ticker {SIGNAL_TICKER} unavailable.")

    universe = [t for t in sorted(needed) if t in prices.columns]
    engine = GridEngine(prices, universe, SIGNAL_TICKER, LOOKBACKS, SMA_WINDOWS)
    print(f"[rf]   risk-free source = {engine.rf_source}")

    ro_pools = [p for p in RISK_ON_POOLS if engine.pool_indices(p) is not None]
    roff_pools = [p for p in RISK_OFF_POOLS if engine.pool_indices(p) is not None]
    if not ro_pools or not roff_pools:
        raise SystemExit("[fatal] no usable asset pools after availability screening.")

    # Global common window -> apples-to-apples ranking across the whole grid.
    all_used = sorted({t for p in ro_pools + roff_pools for t in p} | {SIGNAL_TICKER})
    global_req = tuple(engine.idx_of[t] for t in all_used)
    common_start = engine.first_aligned_index(global_req, max(LOOKBACKS), max(SMA_WINDOWS))
    if common_start is None:
        raise SystemExit("[fatal] no common window exists for the requested grid.")
    print(f"[align] common evaluation window starts "
          f"{engine.dates[common_start + 1].date()} "
          f"({engine.T - common_start - 1} obs)")

    combos = list(itertools.product(SMA_WINDOWS, LOOKBACKS, ro_pools, roff_pools))
    print(f"[grid] sweeping {len(combos)} combinations "
          f"(cost={ONE_WAY_COST_BPS:.1f}bps one-way, "
          f"borrow spread={BORROW_SPREAD_ANNUAL:.2%})")

    results: List[Dict[str, object]] = []
    for k, (sma_w, lb, ro_pool, roff_pool) in enumerate(combos, start=1):
        ro_idx = engine.pool_indices(ro_pool)
        roff_idx = engine.pool_indices(roff_pool)
        sim = engine.simulate(sma_w, lb, ro_idx, roff_idx)
        if sim is None:
            continue

        rets = sim["rets"]
        t0 = int(sim["start_idx"])
        full_slice = slice(t0 + 1, engine.T)
        r_full = rets[full_slice]
        rf_full = engine.rf[full_slice]
        if np.count_nonzero(np.isfinite(r_full)) < MIN_OBS_FULL:
            continue

        row: Dict[str, object] = {
            "sma": sma_w,
            "lookback": lb,
            "risk_on": "|".join(ro_pool),
            "risk_off": "|".join(roff_pool),
            "start_date": engine.dates[t0 + 1].date().isoformat(),
            "end_date": engine.dates[engine.T - 1].date().isoformat(),
            "n_rebalances": int(sim["n_rebalances"]),
            "ruined": bool(sim["ruined"]),
            "stale_price_days": int(sim["stale_price_days"]),
        }
        row.update(perf_stats(r_full, rf_full, "full"))
        yrs = row["full_years"]
        row["ann_turnover"] = (float(sim["turnover"]) / yrs) if (yrs and yrs > 0) else np.nan

        if t0 <= common_start:
            cs = slice(common_start + 1, engine.T)
            r_com, rf_com = rets[cs], engine.rf[cs]
            if np.count_nonzero(np.isfinite(r_com)) >= MIN_OBS_COMMON:
                row.update(perf_stats(r_com, rf_com, "common"))
            else:
                row.update(perf_stats(np.array([]), np.array([]), "common"))
        else:
            row.update(perf_stats(np.array([]), np.array([]), "common"))

        results.append(row)
        if k % 100 == 0 or k == len(combos):
            print(f"  ... {k}/{len(combos)} combos evaluated "
                  f"({len(results)} retained)")

    if not results:
        raise SystemExit("[fatal] no combination produced a valid track record.")

    df = pd.DataFrame(results)
    rank_col = "common_sharpe" if df["common_sharpe"].notna().any() else "full_sharpe"
    df = df.sort_values([rank_col, "full_sharpe"], ascending=False,
                        na_position="last").reset_index(drop=True)
    df.to_csv(OUT_CSV, index=False)

    show = ["sma", "lookback", "risk_on", "risk_off", "start_date",
            "common_sharpe", "common_cagr", "common_mdd",
            "full_sharpe", "full_cagr", "full_vol", "full_mdd",
            "ann_turnover", "full_n_obs"]
    show = [c for c in show if c in df.columns]

    print("\n--- BEST STRATEGIES (ranked by %s) ---" % rank_col)
    with pd.option_context("display.width", 200, "display.max_columns", 50,
                           "display.float_format", lambda v: f"{v:,.4f}"):
        print(df[show].head(5).to_string(index=False))

    best = df.iloc[0]
    print("\n[best] SMA=%s  lookback=%s  risk_on=[%s]  risk_off=[%s]"
          % (best["sma"], best["lookback"], best["risk_on"], best["risk_off"]))
    print("[best] common: sharpe=%.4f cagr=%.4f mdd=%.4f | full: sharpe=%.4f "
          "cagr=%.4f vol=%.4f mdd=%.4f | ann turnover=%.2fx"
          % (float(best.get("common_sharpe", np.nan)),
             float(best.get("common_cagr", np.nan)),
             float(best.get("common_mdd", np.nan)),
             float(best["full_sharpe"]), float(best["full_cagr"]),
             float(best["full_vol"]), float(best["full_mdd"]),
             float(best["ann_turnover"])))
    print(f"[out] results written to {os.path.abspath(OUT_CSV)}")
    return df


if __name__ == "__main__":
    optimize_and_sweep()