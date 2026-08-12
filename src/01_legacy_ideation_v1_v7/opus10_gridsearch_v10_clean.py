"""
opus10_gridsearch_v10.py  —  AUDIT-HARDENED REWRITE (Absolute Surrender Protocol)
=================================================================================
Strategy
--------
Regime-switched, absolute-momentum-filtered, ERC-sized leveraged rotation.

    * Regime filter : SPY Adj Close > SPY SMA(200)   -> "risk-on"
    * Risk-on sleeve  : TQQQ, UPRO
    * Risk-off sleeve : GLD, TLT
    * EVERY sleeve member (offensive AND defensive) must independently pass an
      *excess* absolute-momentum test (12m total return > compounded T-bill
      return over the same window). Failing members go to CASH.
    * Surviving members are sized by Equal Risk Contribution (ERC) on a
      shrunk, look-back-only covariance matrix, with a per-asset weight cap.
    * Portfolio is rebalanced only when the sleeve/eligibility set changes or
      when buy-and-hold drift breaches an L1 band  ->  realistic turnover.

Bugs fixed relative to the legacy version
-----------------------------------------
 1. NO `.fillna(0)` ANYWHERE. Missing prices stay NaN; each asset has an
    explicit inception date and an explicit "live" mask (inception + warm-up).
    Phantom pre-inception assets are structurally impossible.
 2. TRUE Sharpe ratio: mean(excess daily simple return) / std(excess) * sqrt(252),
    where excess is measured against an actual (or explicit constant) risk-free
    series. CAGR/vol is reported separately and clearly labelled.
 3. Transaction costs (bps per unit of one-way turnover) AND financing:
    cash earns rf, negative cash (gross > 1) pays rf + borrow spread.
 4. Absolute momentum applied to defensive assets (GLD, TLT) as well.
 5. Inception alignment: the backtest starts only when the regime signal is
    valid and at least one sleeve asset is live; no asset can be traded before
    it possesses a full signal history.
 6. Portfolio aggregation uses SIMPLE returns (log returns are NOT additive
    across assets); compounding is done on simple returns.
 7. No look-ahead: signals at t use data through t only, and are applied to the
    return of t+1. Covariance uses a strictly trailing window.
 8. Self-contained, dependency-free, numerically guarded ERC optimizer
    (external `opus10_erc_optimizer_v10` is used only if it exposes a
    compatible cov->weights function).
 9. Executable with or without the frozen data set (deterministic synthetic
    fallback universe with staggered inceptions).

Author: Brutal Multipoint Quality Inspector
"""

from __future__ import annotations

import math
import os
import warnings
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Optional external ERC optimizer (strictly optional, never required)
# --------------------------------------------------------------------------- #
_EXT_ERC = None
try:  # pragma: no cover - environment dependent
    import opus10_erc_optimizer_v10 as _ext  # type: ignore

    for _name in ("erc_weights_from_cov", "erc_weights", "solve_erc"):
        if hasattr(_ext, _name):
            _EXT_ERC = getattr(_ext, _name)
            break
except Exception:
    _EXT_ERC = None


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Config:
    # Universe -------------------------------------------------------------- #
    assets: Tuple[str, ...] = ("BTC-USD", "GLD", "QQQ", "SPY", "TLT", "TQQQ", "UPRO")
    offensive: Tuple[str, ...] = ("TQQQ", "UPRO")
    defensive: Tuple[str, ...] = ("GLD", "TLT")
    regime_asset: str = "SPY"

    # Signals --------------------------------------------------------------- #
    regime_window: int = 200          # SMA window on regime asset
    abs_mom_window: int = 252         # absolute (excess) momentum look-back
    cov_lookback: int = 60            # trailing window for covariance
    cov_min_obs: int = 40             # min overlapping obs to trust covariance
    cov_shrinkage: float = 0.10       # shrink toward diagonal
    max_weight: float = 0.60          # per-asset cap inside a sleeve
    rebalance_band: float = 0.05      # L1 drift band before we trade

    # Frictions ------------------------------------------------------------- #
    cost_bps: float = 10.0            # one-way cost per unit turnover (bps)
    borrow_spread_bps: float = 100.0  # annual spread OVER rf on negative cash
    cash_spread_bps: float = 10.0     # annual haircut on positive cash yield

    # Risk free ------------------------------------------------------------- #
    default_annual_rf: float = 0.02   # used only if no rf data is found

    # Conventions ----------------------------------------------------------- #
    trading_days: int = 252
    max_price_ffill: int = 5          # max consecutive stale days tolerated

    def validate(self) -> None:
        if self.regime_asset not in self.assets:
            raise ValueError("regime_asset must be part of the universe")
        for grp, name in ((self.offensive, "offensive"), (self.defensive, "defensive")):
            if not grp:
                raise ValueError(f"{name} sleeve is empty")
            missing = [a for a in grp if a not in self.assets]
            if missing:
                raise ValueError(f"{name} sleeve contains non-universe assets: {missing}")
        if min(self.regime_window, self.abs_mom_window, self.cov_lookback) < 2:
            raise ValueError("signal windows must be >= 2")
        if not (0.0 <= self.cov_shrinkage <= 1.0):
            raise ValueError("cov_shrinkage must be in [0, 1]")
        if not (0.0 < self.max_weight <= 1.0):
            raise ValueError("max_weight must be in (0, 1]")
        if self.rebalance_band < 0:
            raise ValueError("rebalance_band must be >= 0")
        if min(self.cost_bps, self.borrow_spread_bps, self.cash_spread_bps) < 0:
            raise ValueError("friction parameters must be >= 0")
        if self.trading_days <= 0:
            raise ValueError("trading_days must be positive")


# --------------------------------------------------------------------------- #
# Data loading (NaN-preserving, inception-aware)
# --------------------------------------------------------------------------- #
_PRICE_COL_CANDIDATES = ("Adj Close", "adj_close", "AdjClose", "adjclose", "Close", "close")


def _pick_price_column(df: pd.DataFrame) -> str:
    for c in _PRICE_COL_CANDIDATES:
        if c in df.columns:
            return c
    lower = {str(c).lower().replace(" ", "").replace("_", ""): c for c in df.columns}
    for key in ("adjclose", "close"):
        if key in lower:
            return lower[key]
    raise KeyError(f"No usable price column found in {list(df.columns)}")


def _to_naive_datetime_index(idx: Iterable) -> pd.DatetimeIndex:
    di = pd.DatetimeIndex(pd.to_datetime(list(idx), errors="coerce"))
    try:
        if di.tz is not None:
            di = di.tz_convert(None)
    except (TypeError, AttributeError):
        pass
    return di.normalize()


def load_wide_prices(data_dir: str, assets: Sequence[str]) -> pd.DataFrame:
    """
    Load a (dates x assets) adjusted-close matrix from the frozen parquet.
    Missing observations are preserved as NaN (NEVER filled with 0).
    """
    path = os.path.join(data_dir, "frozen_universe_data.parquet")
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    df = pd.read_parquet(path)

    if isinstance(df.index, pd.MultiIndex):
        names = [("" if n is None else str(n)).lower() for n in df.index.names]
        tick_lvl = next((i for i, n in enumerate(names) if "ticker" in n or "symbol" in n), None)
        if tick_lvl is None:
            tick_lvl = len(names) - 1
        date_lvl = next((i for i in range(len(names)) if i != tick_lvl), 0)
        price_col = _pick_price_column(df)
        wide = df[price_col].unstack(level=tick_lvl)
        wide.index = _to_naive_datetime_index(df.index.get_level_values(date_lvl).unique().sort_values())
        wide = wide.sort_index()
    else:
        if isinstance(df.columns, pd.MultiIndex):
            price_col = _pick_price_column(pd.DataFrame(columns=df.columns.get_level_values(0).unique()))
            wide = df.xs(price_col, axis=1, level=0)
        else:
            wide = df
        wide.index = _to_naive_datetime_index(wide.index)
        wide = wide.sort_index()

    wide = wide.apply(pd.to_numeric, errors="coerce")
    wide = wide.loc[~wide.index.duplicated(keep="last")]

    # Optional master calendar (dates.npy) -> INTERSECTION only, never reindex-fill.
    dates_path = os.path.join(data_dir, "dates.npy")
    if os.path.isfile(dates_path):
        try:
            raw = np.load(dates_path, allow_pickle=True)
            cal = _to_naive_datetime_index(np.asarray(raw).ravel().tolist())
            cal = cal[~cal.isna()].unique().sort_values()
            common = wide.index.intersection(cal)
            if len(common) >= max(300, int(0.5 * len(wide.index))):
                wide = wide.loc[common]
            else:
                warnings.warn("dates.npy overlaps the price index too little; ignoring it.")
        except Exception as exc:  # pragma: no cover
            warnings.warn(f"Could not use dates.npy ({exc}); using parquet calendar.")

    have = [a for a in assets if a in wide.columns]
    missing = [a for a in assets if a not in wide.columns]
    if missing:
        warnings.warn(f"Assets absent from the data set (excluded, NOT zero-filled): {missing}")
    if not have:
        raise ValueError("None of the requested assets are present in the data set")

    wide = wide[have]
    wide = wide.mask(~np.isfinite(wide.to_numpy()))
    wide = wide.mask(wide <= 0.0)  # non-positive prices are invalid
    return wide


def synthesize_universe(assets: Sequence[str], seed: int = 20240719) -> pd.DataFrame:
    """
    Deterministic synthetic fallback universe with realistic staggered
    inceptions, so this script is always executable and always exercises the
    inception-alignment logic.
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2004-01-02", "2024-12-31")
    T = len(idx)

    base_specs = {
        "SPY": (0.085, 0.180),
        "QQQ": (0.105, 0.230),
        "GLD": (0.060, 0.160),
        "TLT": (0.035, 0.140),
        "BTC-USD": (0.500, 0.700),
    }
    corr_driver = rng.standard_normal(T)

    base_rets: Dict[str, np.ndarray] = {}
    for name, (mu, sig) in base_specs.items():
        beta = 0.55 if name in ("SPY", "QQQ") else (0.10 if name == "BTC-USD" else -0.15)
        z = beta * corr_driver + math.sqrt(max(1e-12, 1.0 - beta ** 2)) * rng.standard_normal(T)
        base_rets[name] = (mu - 0.5 * sig ** 2) / 252.0 + sig / math.sqrt(252.0) * z

    def levered(source: str, k: float, fee: float) -> np.ndarray:
        r = np.expm1(base_rets[source])           # simple daily return of base
        lev = k * r - (fee + 0.02 * (k - 1.0)) / 252.0
        return np.log1p(np.clip(lev, -0.95, None))  # back to log space

    log_rets = dict(base_rets)
    log_rets["TQQQ"] = levered("QQQ", 3.0, 0.0095)
    log_rets["UPRO"] = levered("SPY", 3.0, 0.0091)

    inception = {
        "SPY": "2004-01-02", "QQQ": "2004-01-02", "TLT": "2004-01-02",
        "GLD": "2004-11-18", "UPRO": "2009-06-25", "TQQQ": "2010-02-11",
        "BTC-USD": "2014-09-17",
    }
    start_px = {"SPY": 110.0, "QQQ": 36.0, "GLD": 44.0, "TLT": 88.0,
                "TQQQ": 1.0, "UPRO": 2.0, "BTC-USD": 457.0}

    out = pd.DataFrame(index=idx)
    for a in assets:
        if a not in log_rets:
            continue
        px = start_px.get(a, 100.0) * np.exp(np.cumsum(log_rets[a]))
        s = pd.Series(px, index=idx)
        s.loc[s.index < pd.Timestamp(inception.get(a, idx[0]))] = np.nan
        first = s.first_valid_index()
        if first is not None:  # renormalize so the series starts at start_px
            s.loc[first:] = s.loc[first:] / s.loc[first] * start_px.get(a, 100.0)
        out[a] = s
    return out


def load_risk_free(data_dir: str, index: pd.DatetimeIndex, default_annual: float) -> pd.Series:
    """
    Annualized risk-free rate aligned to `index`.  Tries local files, then falls
    back to an explicit constant (never silently 0 unless configured).
    """
    candidates = ("risk_free.csv", "rf.csv", "risk_free_rate.csv", "DGS3MO.csv",
                  "irx.csv", "IRX.csv", "TB3MS.csv", "risk_free.parquet")
    for fname in candidates:
        path = os.path.join(data_dir, fname)
        if not os.path.isfile(path):
            continue
        try:
            raw = pd.read_parquet(path) if fname.endswith(".parquet") else pd.read_csv(path)
            date_col = next((c for c in raw.columns if "date" in str(c).lower()), raw.columns[0])
            raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
            raw = raw.dropna(subset=[date_col]).set_index(date_col).sort_index()
            num = raw.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")
            if num.empty:
                continue
            s = num.iloc[:, 0].astype(float)
            s.index = _to_naive_datetime_index(s.index)
            if float(np.nanmedian(np.abs(s.to_numpy()))) > 0.25:  # quoted in percent
                s = s / 100.0
            s = s.reindex(index.union(s.index)).ffill().reindex(index)
            s = s.ffill().bfill()
            if s.isna().any():
                continue
            print(f"[rf] Loaded risk-free series from {fname} "
                  f"(mean = {s.mean() * 100:.2f}% annual)")
            return s.clip(lower=0.0).rename("rf_annual")
        except Exception as exc:  # pragma: no cover
            warnings.warn(f"Failed reading {fname}: {exc}")

    print(f"[rf] No risk-free file found; using explicit constant "
          f"{default_annual * 100:.2f}% annual for BOTH Sharpe and financing.")
    return pd.Series(float(default_annual), index=index, name="rf_annual")


# --------------------------------------------------------------------------- #
# ERC optimizer (long only, fully guarded)
# --------------------------------------------------------------------------- #
def _shrink_cov(cov: np.ndarray, lam: float) -> np.ndarray:
    cov = 0.5 * (cov + cov.T)
    d = np.diag(cov).copy()
    d[~np.isfinite(d) | (d <= 0.0)] = 1e-12
    shrunk = (1.0 - lam) * cov + lam * np.diag(d)
    shrunk[np.diag_indices_from(shrunk)] = np.maximum(np.diag(shrunk), 1e-14)
    ridge = 1e-10 * float(np.mean(np.diag(shrunk)))
    return shrunk + ridge * np.eye(shrunk.shape[0])


def erc_weights_from_cov(cov: np.ndarray, max_iter: int = 5000, tol: float = 1e-12) -> np.ndarray:
    """
    Equal Risk Contribution weights: w_i * (Sigma w)_i = const, w >= 0, sum w = 1.
    Damped fixed-point iteration w_i <- 1 / (Sigma w)_i (then renormalize).
    """
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if n == 0:
        return np.zeros(0)
    if n == 1:
        return np.ones(1)
    if not np.all(np.isfinite(cov)):
        return np.full(n, 1.0 / n)

    vol = np.sqrt(np.maximum(np.diag(cov), 1e-18))
    w = (1.0 / vol) / np.sum(1.0 / vol)  # inverse-vol warm start

    for _ in range(max_iter):
        m = cov @ w
        if not np.all(np.isfinite(m)) or np.any(m <= 0.0):
            return (1.0 / vol) / np.sum(1.0 / vol)
        w_new = 1.0 / m
        w_new /= w_new.sum()
        step = float(np.max(np.abs(w_new - w)))
        w = 0.5 * w + 0.5 * w_new
        w = np.clip(w, 1e-12, None)
        w /= w.sum()
        if step < tol:
            break

    if not np.all(np.isfinite(w)) or w.sum() <= 0:
        return np.full(n, 1.0 / n)
    return w / w.sum()


def _erc(cov: np.ndarray) -> np.ndarray:
    if _EXT_ERC is not None:
        try:
            w = np.asarray(_EXT_ERC(cov), dtype=float).ravel()
            if w.size == cov.shape[0] and np.all(np.isfinite(w)) and w.min() >= -1e-9 and w.sum() > 0:
                return np.clip(w, 0.0, None) / np.clip(w, 0.0, None).sum()
        except Exception:
            pass
    return erc_weights_from_cov(cov)


def apply_weight_cap(w: np.ndarray, cap: float) -> np.ndarray:
    """Waterfall cap. If n*cap < 1 the shortfall is intentionally left in cash."""
    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    n = w.size
    if n == 0:
        return w
    if n * cap <= 1.0 + 1e-12:
        return np.minimum(w, cap)
    for _ in range(100):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess = float(np.sum(w[over] - cap))
        w[over] = cap
        free = ~over
        pool = float(np.sum(w[free]))
        if pool <= 1e-15:
            w[free] = excess / max(1, int(free.sum()))
            break
        w[free] += excess * w[free] / pool
    return np.minimum(w, cap)


# --------------------------------------------------------------------------- #
# Signal construction
# --------------------------------------------------------------------------- #
@dataclass
class Signals:
    dates: pd.DatetimeIndex
    assets: List[str]
    prices: np.ndarray        # (T, N) NaN-preserving
    rets: np.ndarray          # (T, N) simple returns, NaN where undefined
    valid_ret: np.ndarray     # (T, N) bool
    live: np.ndarray          # (T, N) bool: inception + full signal warm-up
    regime_on: np.ndarray     # (T,) bool
    regime_valid: np.ndarray  # (T,) bool
    mom_ok: np.ndarray        # (T, N) bool: excess absolute momentum > 0
    rf_daily: np.ndarray      # (T,) simple daily risk-free
    inception: Dict[str, Optional[pd.Timestamp]] = field(default_factory=dict)


def build_signals(wide: pd.DataFrame, rf_annual: pd.Series, cfg: Config) -> Signals:
    wide = wide.sort_index()
    assets = list(wide.columns)
    dates = pd.DatetimeIndex(wide.index)
    T, N = len(dates), len(assets)
    if T < cfg.abs_mom_window + cfg.cov_lookback + 5:
        raise ValueError("Insufficient history for the configured signal windows")

    inception: Dict[str, Optional[pd.Timestamp]] = {}
    px_clean = pd.DataFrame(index=dates, columns=assets, dtype=float)
    for a in assets:
        s = wide[a].astype(float)
        first = s.first_valid_index()
        inception[a] = first
        if first is None:
            continue
        seg = s.loc[first:].ffill(limit=cfg.max_price_ffill)  # tolerate short halts
        px_clean.loc[seg.index, a] = seg.to_numpy()

    prices = px_clean.to_numpy(dtype=float)

    prev = np.vstack([np.full((1, N), np.nan), prices[:-1, :]])
    with np.errstate(invalid="ignore", divide="ignore"):
        rets = prices / prev - 1.0
    valid_ret = np.isfinite(rets) & np.isfinite(prices) & np.isfinite(prev)
    rets = np.where(valid_ret, rets, np.nan)

    # ---- risk free (simple daily) ---------------------------------------- #
    rf_a = rf_annual.reindex(dates).ffill().bfill().to_numpy(dtype=float)
    rf_a = np.where(np.isfinite(rf_a), rf_a, cfg.default_annual_rf)
    rf_daily = (1.0 + np.maximum(rf_a, 0.0)) ** (1.0 / cfg.trading_days) - 1.0

    # ---- "live" mask: inception + full warm-up of valid observations ------ #
    warmup = max(cfg.abs_mom_window, cfg.cov_lookback) + 1
    valid_count = np.cumsum(valid_ret.astype(np.int64), axis=0)
    live = valid_count >= warmup
    live &= np.isfinite(prices)

    # ---- regime: SPY > SMA200 (trailing only) ----------------------------- #
    ridx = assets.index(cfg.regime_asset) if cfg.regime_asset in assets else None
    regime_on = np.zeros(T, dtype=bool)
    regime_valid = np.zeros(T, dtype=bool)
    if ridx is not None:
        rp = pd.Series(prices[:, ridx], index=dates)
        sma = rp.rolling(cfg.regime_window, min_periods=cfg.regime_window).mean()
        ok = rp.notna() & sma.notna()
        regime_valid = ok.to_numpy()
        regime_on = np.where(regime_valid, (rp > sma).to_numpy(), False)
    else:
        raise ValueError(f"Regime asset {cfg.regime_asset} not available in the data")

    # ---- excess absolute momentum ---------------------------------------- #
    W = cfg.abs_mom_window
    mom_ok = np.zeros((T, N), dtype=bool)
    px_lag = np.vstack([np.full((W, N), np.nan), prices[:-W, :]])
    with np.errstate(invalid="ignore", divide="ignore"):
        total_ret = prices / px_lag - 1.0
    rf_growth = (
        pd.Series(1.0 + rf_daily, index=dates)
        .rolling(W, min_periods=W)
        .apply(np.prod, raw=True)
        .to_numpy()
    ) - 1.0
    finite = np.isfinite(total_ret) & np.isfinite(rf_growth)[:, None]
    mom_ok = finite & (total_ret > rf_growth[:, None]) & live

    return Signals(dates=dates, assets=assets, prices=prices, rets=rets,
                   valid_ret=valid_ret, live=live, regime_on=regime_on,
                   regime_valid=regime_valid, mom_ok=mom_ok, rf_daily=rf_daily,
                   inception=inception)


def build_target_weights(sig: Signals, cfg: Config) -> Tuple[np.ndarray, np.ndarray]:
    """
    Target risky weights per date (info through t only) plus a boolean flag
    marking dates where the eligible set changed (forced rebalance).
    """
    T, N = sig.rets.shape
    idx_of = {a: i for i, a in enumerate(sig.assets)}
    off = [idx_of[a] for a in cfg.offensive if a in idx_of]
    dfn = [idx_of[a] for a in cfg.defensive if a in idx_of]
    if not off or not dfn:
        raise ValueError("At least one offensive and one defensive asset must exist in the data")

    targets = np.zeros((T, N), dtype=float)
    set_change = np.zeros(T, dtype=bool)
    prev_key: Optional[Tuple[int, ...]] = None

    for t in range(T):
        if not sig.regime_valid[t]:
            if prev_key is not None:
                set_change[t] = True
                prev_key = None
            continue

        sleeve = off if sig.regime_on[t] else dfn
        elig = [j for j in sleeve if sig.live[t, j] and sig.mom_ok[t, j] and sig.valid_ret[t, j]]

        key = tuple(elig)
        if key != prev_key:
            set_change[t] = True
            prev_key = key
        if not elig:
            continue

        lo = max(0, t - cfg.cov_lookback + 1)
        win = sig.rets[lo:t + 1, :][:, elig]
        rows = np.all(np.isfinite(win), axis=1)
        obs = win[rows, :]

        if obs.shape[0] >= max(cfg.cov_min_obs, len(elig) + 2):
            cov = _shrink_cov(np.cov(obs, rowvar=False, ddof=1).reshape(len(elig), len(elig)),
                              cfg.cov_shrinkage)
            w = _erc(cov)
        elif obs.shape[0] >= 5:
            vol = np.std(obs, axis=0, ddof=1)
            vol = np.where(np.isfinite(vol) & (vol > 0), vol, np.nan)
            if np.all(np.isnan(vol)):
                w = np.full(len(elig), 1.0 / len(elig))
            else:
                inv = 1.0 / np.where(np.isnan(vol), np.nanmax(vol), vol)
                w = inv / inv.sum()
        else:
            w = np.full(len(elig), 1.0 / len(elig))

        w = apply_weight_cap(w, cfg.max_weight)
        s = w.sum()
        if s > 1.0 + 1e-12:
            w = w / s
        targets[t, elig] = w

    return targets, set_change


# --------------------------------------------------------------------------- #
# Backtest engine (drift, bands, costs, financing)
# --------------------------------------------------------------------------- #
@dataclass
class BacktestResult:
    equity: pd.Series
    port_ret: pd.Series
    rf_daily: pd.Series
    weights: pd.DataFrame
    turnover: pd.Series
    gross_exposure: pd.Series
    start: pd.Timestamp
    metrics: Dict[str, float]


def run_backtest(sig: Signals, cfg: Config) -> BacktestResult:
    T, N = sig.rets.shape
    targets, set_change = build_target_weights(sig, cfg)

    tradable = sig.regime_valid & np.any(sig.live & np.isfinite(sig.rets), axis=1)
    starts = np.flatnonzero(tradable & (targets.sum(axis=1) > 0))
    if starts.size == 0:
        raise ValueError("No tradable date: check inceptions, warm-up and momentum filters")
    t0 = int(starts[0])

    cost_rate = cfg.cost_bps / 1e4
    borrow_d = (1.0 + cfg.borrow_spread_bps / 1e4) ** (1.0 / cfg.trading_days) - 1.0
    cashsp_d = (1.0 + cfg.cash_spread_bps / 1e4) ** (1.0 / cfg.trading_days) - 1.0

    n_steps = T - t0
    eq = np.empty(n_steps)
    pr = np.zeros(n_steps)
    tn = np.zeros(n_steps)
    gx = np.zeros(n_steps)
    W = np.zeros((n_steps, N))

    # --- initial rebalance out of cash at the close of t0 ------------------ #
    w = targets[t0].copy()
    cash = 1.0 - w.sum()
    turn0 = float(np.abs(w).sum())
    equity = 1.0 * (1.0 - turn0 * cost_rate)
    eq[0] = equity
    pr[0] = equity - 1.0
    tn[0] = turn0
    gx[0] = float(w.sum())
    W[0] = w

    for k in range(1, n_steps):
        t = t0 + k

        # ---- 1) mark to market on day t --------------------------------- #
        r = np.where(sig.valid_ret[t], sig.rets[t], 0.0)   # stale asset -> 0% (never NaN)
        r = np.where(np.isfinite(r), r, 0.0)
        asset_val = w * (1.0 + r)

        rfd = float(sig.rf_daily[t])
        if cash >= 0.0:
            cash_val = cash * (1.0 + max(rfd - cashsp_d, -1.0))
        else:
            cash_val = cash * (1.0 + rfd + borrow_d)   # negative cash -> pays rf + spread

        gross = float(asset_val.sum() + cash_val)
        if gross <= 1e-12:
            gross = 1e-12
        day_ret = gross - 1.0

        w = asset_val / gross
        cash = cash_val / gross

        # ---- 2) rebalance decision using info through day t -------------- #
        tgt = targets[t]
        drift = float(np.abs(w - tgt).sum())
        must = bool(set_change[t]) or (not tradable[t]) or (drift > cfg.rebalance_band)

        turn = 0.0
        if must:
            turn = drift
            w = tgt.copy()
            cash = 1.0 - w.sum()
            day_ret = (1.0 + day_ret) * (1.0 - turn * cost_rate) - 1.0

        equity *= (1.0 + day_ret)
        eq[k] = equity
        pr[k] = day_ret
        tn[k] = turn
        gx[k] = float(w.sum())
        W[k] = w

    idx = sig.dates[t0:]
    equity_s = pd.Series(eq, index=idx, name="equity")
    pr_s = pd.Series(pr, index=idx, name="port_ret")
    rf_s = pd.Series(sig.rf_daily[t0:], index=idx, name="rf_daily")
    w_df = pd.DataFrame(W, index=idx, columns=sig.assets)
    tn_s = pd.Series(tn, index=idx, name="turnover")
    gx_s = pd.Series(gx, index=idx, name="gross_exposure")

    metrics = compute_metrics(pr_s, rf_s, equity_s, tn_s, cfg)
    return BacktestResult(equity_s, pr_s, rf_s, w_df, tn_s, gx_s, idx[0], metrics)


# --------------------------------------------------------------------------- #
# Performance analytics (mathematically correct)
# --------------------------------------------------------------------------- #
def compute_metrics(port_ret: pd.Series, rf_daily: pd.Series, equity: pd.Series,
                    turnover: pd.Series, cfg: Config) -> Dict[str, float]:
    r = port_ret.to_numpy(dtype=float)
    rf = rf_daily.to_numpy(dtype=float)
    ann = float(cfg.trading_days)
    n = r.size
    if n < 2:
        return {"n_days": float(n)}

    excess = r - rf
    total_growth = float(equity.iloc[-1])
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)

    cagr = total_growth ** (1.0 / years) - 1.0 if total_growth > 0 else -1.0
    vol = float(np.std(r, ddof=1)) * math.sqrt(ann)
    ex_mu = float(np.mean(excess)) * ann
    ex_sd = float(np.std(excess, ddof=1)) * math.sqrt(ann)
    sharpe = ex_mu / ex_sd if ex_sd > 0 else float("nan")

    dn = excess[excess < 0.0]
    dvol = float(np.sqrt(np.mean(dn ** 2))) * math.sqrt(ann) if dn.size else 0.0
    sortino = ex_mu / dvol if dvol > 0 else float("nan")

    peak = np.maximum.accumulate(equity.to_numpy(dtype=float))
    dd = equity.to_numpy(dtype=float) / peak - 1.0
    max_dd = float(dd.min())
    calmar = cagr / abs(max_dd) if max_dd < -1e-12 else float("nan")

    under = dd < -1e-12
    longest, run = 0, 0
    for u in under:
        run = run + 1 if u else 0
        longest = max(longest, run)

    rf_cagr = float(np.prod(1.0 + rf)) ** (1.0 / years) - 1.0

    return {
        "start": equity.index[0], "end": equity.index[-1],
        "n_days": float(n), "years": years,
        "total_growth_x": total_growth,
        "total_return_pct": (total_growth - 1.0) * 100.0,
        "cagr_pct": cagr * 100.0,
        "ann_vol_pct": vol * 100.0,
        "ann_excess_return_pct": ex_mu * 100.0,
        "sharpe_true_excess": sharpe,
        "sortino": sortino,
        "return_over_vol_NOT_sharpe": cagr / vol if vol > 0 else float("nan"),
        "max_drawdown_pct": max_dd * 100.0,
        "calmar": calmar,
        "longest_drawdown_days": float(longest),
        "hit_rate_pct": float(np.mean(r > 0.0) * 100.0),
        "best_day_pct": float(r.max() * 100.0),
        "worst_day_pct": float(r.min() * 100.0),
        "annual_turnover_x": float(turnover.sum() / years),
        "avg_rf_pct": rf_cagr * 100.0,
        "skew": float(pd.Series(r).skew()),
        "excess_kurtosis": float(pd.Series(r).kurtosis()),
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def print_report(sig: Signals, res: BacktestResult, cfg: Config) -> None:
    line = "=" * 78
    print("\n" + line)
    print("DISCORD ALPHA v10 — Regime Filter + Excess Absolute Momentum + ERC (AUDITED)")
    print(line)

    print("\n[Inception alignment]")
    for a in sig.assets:
        inc = sig.inception.get(a)
        first_live = np.flatnonzero(sig.live[:, a_i]) if False else np.flatnonzero(sig.live[:, sig.assets.index(a)])
        live_txt = sig.dates[first_live[0]].date() if first_live.size else "never (insufficient history)"
        print(f"  {a:<9} first price: {str(inc.date()) if inc is not None else 'NONE':<12}"
              f" first tradable: {live_txt}")

    print("\n[Frictions]")
    print(f"  one-way cost         : {cfg.cost_bps:.1f} bps per unit turnover")
    print(f"  borrow spread        : {cfg.borrow_spread_bps:.1f} bps annual over rf on negative cash")
    print(f"  cash yield haircut   : {cfg.cash_spread_bps:.1f} bps annual")
    print(f"  annual turnover      : {res.metrics['annual_turnover_x']:.2f}x")

    print("\n[Regime / exposure]")
    on = sig.regime_on[sig.dates.get_indexer(res.equity.index)]
    print(f"  days risk-on         : {on.sum()} / {len(on)} ({on.mean() * 100:.1f}%)")
    print(f"  avg gross exposure   : {res.gross_exposure.mean():.3f}")
    print(f"  avg cash weight      : {1.0 - res.gross_exposure.mean():.3f}")
    for a in sig.assets:
        wm = res.weights[a].mean()
        if wm > 1e-6:
            print(f"  avg weight {a:<9}: {wm:.4f}")

    m = res.metrics
    print("\n[Performance]")
    print(f"  period               : {m['start'].date()} -> {m['end'].date()}  ({m['years']:.2f}y)")
    print(f"  total growth         : {m['total_growth_x']:.2f}x  ({m['total_return_pct']:.1f}%)")
    print(f"  CAGR                 : {m['cagr_pct']:.2f}%")
    print(f"  ann. volatility      : {m['ann_vol_pct']:.2f}%")
    print(f"  ann. excess return   : {m['ann_excess_return_pct']:.2f}%   (rf ~ {m['avg_rf_pct']:.2f}%)")
    print(f"  SHARPE (true excess) : {m['sharpe_true_excess']:.3f}")
    print(f"  Sortino              : {m['sortino']:.3f}")
    print(f"  CAGR/vol (NOT Sharpe): {m['return_over_vol_NOT_sharpe']:.3f}")
    print(f"  max drawdown         : {m['max_drawdown_pct']:.2f}%")
    print(f"  Calmar               : {m['calmar']:.3f}")
    print(f"  longest drawdown     : {int(m['longest_drawdown_days'])} trading days")
    print(f"  hit rate             : {m['hit_rate_pct']:.2f}%")
    print(f"  best / worst day     : {m['best_day_pct']:.2f}% / {m['worst_day_pct']:.2f}%")
    print(f"  skew / exc. kurtosis : {m['skew']:.2f} / {m['excess_kurtosis']:.2f}")
    print(line + "\n")


def plot_equity(res: BacktestResult, out_png: str = "discord_alpha_equity_curve.png") -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        warnings.warn(f"matplotlib unavailable ({exc}); skipping plot.")
        return
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(res.equity.index, res.equity.to_numpy(), lw=1.2,
             label="Discord Alpha v10 (net of costs)")
    ax1.set_yscale("log")
    ax1.set_title("Regime Filter + Excess Absolute Momentum + ERC Rotation (audited, net)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(loc="upper left")
    eqv = res.equity.to_numpy()
    dd = eqv / np.maximum.accumulate(eqv) - 1.0
    ax2.fill_between(res.equity.index, dd * 100.0, 0.0, color="crimson", alpha=0.45)
    ax2.set_ylabel("Drawdown (%)")
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    plt.close(fig)
    print(f"Saved equity curve to {out_png}")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def run_discord_alpha(data_dir: str, cfg: Optional[Config] = None,
                      allow_synthetic: bool = True) -> BacktestResult:
    cfg = cfg or Config()
    cfg.validate()

    try:
        wide = load_wide_prices(data_dir, cfg.assets)
        print(f"[data] Loaded {wide.shape[1]} assets x {wide.shape[0]} dates from {data_dir}")
    except Exception as exc:
        if not allow_synthetic:
            raise
        warnings.warn(f"Falling back to synthetic universe ({exc}).")
        wide = synthesize_universe(cfg.assets)
        print(f"[data] SYNTHETIC universe: {wide.shape[1]} assets x {wide.shape[0]} dates")

    rf = load_risk_free(data_dir, pd.DatetimeIndex(wide.index), cfg.default_annual_rf)
    sig = build_signals(wide, rf, cfg)
    res = run_backtest(sig, cfg)
    print_report(sig, res, cfg)
    return res


def main() -> None:
    data_dir = os.environ.get(
        "OPUS_DATA_DIR",
        os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "scratch",
                     "opus8_matrix_data"),
    )
    cfg = Config()
    res = run_discord_alpha(data_dir, cfg, allow_synthetic=True)

    try:
        pd.DataFrame({
            "equity": res.equity,
            "port_ret": res.port_ret,
            "rf_daily": res.rf_daily,
            "turnover": res.turnover,
            "gross_exposure": res.gross_exposure,
        }).join(res.weights.add_prefix("w_")).to_csv("discord_alpha_v10_results.csv")
        print("Saved daily results to discord_alpha_v10_results.csv")
    except Exception as exc:  # pragma: no cover
        warnings.warn(f"Could not write results CSV: {exc}")

    plot_equity(res)


if __name__ == "__main__":
    main()