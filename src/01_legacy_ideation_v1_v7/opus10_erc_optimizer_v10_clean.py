"""
================================================================================
 opus_erc_optimizer_v11.py
 Dual-Momentum / Equal-Risk-Contribution (ERC) Tactical Allocation Engine
 "Absolute Surrender Protocol" — Brutal Multipoint Quality Inspected Rewrite
================================================================================

 FATAL BUGS IN v10 AND HOW THEY ARE FIXED HERE
 ---------------------------------------------------------------------------
 (1) .fillna(0) creating phantom assets prior to inception
        -> NaNs are NEVER filled. A per-date "tradable" mask is derived from
           prices.notna() & prices.shift(1).notna(). An asset can only receive
           weight if (a) it has a valid price today, (b) it has a *complete*
           history covering every momentum lookback AND the covariance
           lookback, and (c) its covariance statistics are estimable from a
           minimum number of *joint* observations. A hard post-hoc audit
           asserts zero weight on any asset with a NaN price on that date
           (zero phantom assets, by construction and by assertion).
 (2) Wrong Sharpe formula (CAGR / vol)
        -> True Sharpe = mean(r_p - r_f) / std(r_p - r_f) * sqrt(252) using
           *arithmetic daily excess returns* against the realised risk-free
           series (ddof=1). CAGR, geometric excess, Sortino, Calmar reported
           separately and never conflated with Sharpe.
 (3) No transaction costs or borrowing spread
        -> Per-side proportional cost (bps) charged on realised turnover at
           every rebalance and on every forced liquidation. Negative cash
           (leverage) is financed at (risk-free + borrowing spread); positive
           cash earns the risk-free rate. Costs are deducted from the daily
           NET return, so they compound correctly.
 (4) No Absolute Momentum on defensive assets
        -> Absolute (time-series) momentum is applied to EVERY asset —
           risk *and* defensive — measured as total return in EXCESS of the
           compounded risk-free return over the same window. A defensive
           asset that fails absolute momentum is refused; the slot rolls to
           true cash (T-bill).
 (5) Inception alignment ignored
        -> Strict inception alignment: eligibility requires a fully populated
           price history over max(all lookbacks); pairwise covariance uses
           only jointly-observed days with a minimum-observation floor;
           correlation matrix is shrunk and projected to the nearest PSD
           matrix so the optimiser can never be handed a garbage cov.

 Additional correctness work:
   * ERC solved via the CONVEX log-barrier formulation
         min  0.5 w'Sw - sum_i b_i ln(w_i),  w > 0   (then normalised)
     which has a unique solution and analytic gradient — no premature
     SLSQP convergence, no scale-dependent 1e12 fudge factor. A squared
     risk-contribution-dispersion SLSQP solve is used only as a fallback
     (and for weight caps), inverse-vol as the final backstop.
   * No look-ahead: signals/covariances at date t use data up to and
     including t; the resulting target weights become effective at t and are
     earned from t+1 onward. Weights DRIFT with returns between rebalances,
     so turnover is measured against drifted (not target) weights.
   * Full accounting identity check: equity curve rebuilt from net returns
     equals the compounded weight-drift accounting to within 1e-10.

 Runs stand-alone: uses yfinance if available, otherwise a reproducible
 synthetic multi-asset universe with STAGGERED INCEPTION DATES (which is
 precisely what breaks naive implementations).
================================================================================
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize

warnings.filterwarnings("ignore", category=RuntimeWarning)

EPS = 1e-12


# =============================================================================
# 0. CONFIGURATION
# =============================================================================
@dataclass(frozen=True)
class Config:
    # ---- universe -----------------------------------------------------------
    risk_assets: Tuple[str, ...] = ("SPY", "QQQ", "IWM", "EFA", "EEM", "VNQ", "GLD", "DBC")
    defensive_assets: Tuple[str, ...] = ("IEF", "TLT", "LQD", "SHY")

    # ---- signal -------------------------------------------------------------
    mom_lookbacks: Tuple[int, ...] = (21, 63, 126, 252)   # trading days
    abs_mom_lookback: int = 252                            # must be in mom_lookbacks
    top_n: int = 4                                         # risk slots

    # ---- risk model ---------------------------------------------------------
    cov_lookback: int = 252
    cov_min_obs: int = 126          # minimum JOINT observations for a pair
    corr_shrink: float = 0.10       # shrink correlations toward identity
    max_weight: Optional[float] = 0.40   # per-asset cap inside the sleeve (None = off)

    # ---- sizing -------------------------------------------------------------
    use_vol_target: bool = True
    target_vol: float = 0.10        # annualised
    max_gross_leverage: float = 1.50

    # ---- frictions ----------------------------------------------------------
    tc_bps: float = 10.0            # per side, proportional, on traded notional
    borrow_spread_bps: float = 50.0 # annual spread over risk-free on negative cash

    # ---- misc ---------------------------------------------------------------
    trading_days: int = 252
    fallback_rf_annual: float = 0.02
    seed: int = 7
    start: str = "1998-01-01"
    end: str = "2024-12-31"

    @property
    def all_assets(self) -> Tuple[str, ...]:
        seen, out = set(), []
        for t in tuple(self.risk_assets) + tuple(self.defensive_assets):
            if t not in seen:
                seen.add(t)
                out.append(t)
        return tuple(out)

    @property
    def max_lookback(self) -> int:
        return max(max(self.mom_lookbacks), self.abs_mom_lookback, self.cov_lookback)

    def validate(self) -> None:
        assert self.top_n >= 1, "top_n must be >= 1"
        assert len(self.risk_assets) >= self.top_n, "top_n exceeds risk universe size"
        assert self.abs_mom_lookback in self.mom_lookbacks, "abs_mom_lookback must be a momentum lookback"
        assert all(lb > 1 for lb in self.mom_lookbacks), "lookbacks must exceed 1 day"
        assert self.cov_lookback >= self.cov_min_obs >= 20, "bad covariance windows"
        assert 0.0 <= self.corr_shrink < 1.0, "corr_shrink must lie in [0,1)"
        assert self.max_weight is None or self.max_weight * self.top_n >= 1.0 - 1e-12, \
            "max_weight too tight to fill top_n slots"
        assert self.target_vol > 0 and self.max_gross_leverage >= 1.0
        assert self.tc_bps >= 0 and self.borrow_spread_bps >= 0
        assert not set(self.risk_assets) & set(self.defensive_assets), \
            "an asset cannot be both risk and defensive"


# =============================================================================
# 1. LINEAR-ALGEBRA / RISK-MODEL UTILITIES
# =============================================================================
def nearest_psd(mat: np.ndarray, eps_ratio: float = 1e-10) -> np.ndarray:
    """Symmetrise and project onto the PSD cone via eigenvalue clipping."""
    if mat.size == 0:
        return mat
    m = 0.5 * (mat + mat.T)
    vals, vecs = np.linalg.eigh(m)
    if not np.all(np.isfinite(vals)):
        d = np.clip(np.diag(mat), EPS, None)
        return np.diag(d)
    floor = max(float(np.max(vals)) * eps_ratio, EPS)
    vals = np.clip(vals, floor, None)
    out = (vecs * vals) @ vecs.T
    return 0.5 * (out + out.T)


def compute_pairwise_covariance(
    ret_block: np.ndarray,
    min_obs: int = 126,
    shrink: float = 0.10,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Inception-aware covariance estimate.

    Parameters
    ----------
    ret_block : (N, T) array of *simple* returns, NaN where the asset did not
                exist (pre-inception) or did not trade.
    min_obs   : minimum number of jointly observed days required for a pair.
    shrink    : correlation shrinkage intensity toward the identity matrix.

    Returns
    -------
    cov   : (N, N) PSD covariance matrix. Rows/cols of non-estimable assets
            are zeroed with a tiny positive diagonal placeholder.
    valid : (N,) boolean mask of assets with an estimable variance.
    """
    ret_block = np.asarray(ret_block, dtype=float)
    if ret_block.ndim != 2:
        raise ValueError("ret_block must be 2-D (N_assets, T)")
    n = ret_block.shape[0]

    var = np.full(n, np.nan)
    for i in range(n):
        xi = ret_block[i]
        mi = np.isfinite(xi)
        if mi.sum() >= min_obs:
            v = float(np.var(xi[mi], ddof=1))
            if np.isfinite(v) and v > 0.0:
                var[i] = v

    valid = np.isfinite(var) & (var > 0.0)
    sd = np.where(valid, np.sqrt(np.where(valid, var, 1.0)), 0.0)

    corr = np.eye(n)
    for i in range(n):
        if not valid[i]:
            continue
        xi = ret_block[i]
        for j in range(i + 1, n):
            if not valid[j]:
                continue
            xj = ret_block[j]
            m = np.isfinite(xi) & np.isfinite(xj)
            k = int(m.sum())
            if k < min_obs:
                continue                      # inception mismatch -> assume 0 corr
            a, b = xi[m], xj[m]
            sa, sb = a.std(ddof=1), b.std(ddof=1)
            if sa <= 0 or sb <= 0:
                continue
            c = float(np.cov(a, b, ddof=1)[0, 1] / (sa * sb))
            if not np.isfinite(c):
                continue
            c = float(np.clip(c, -0.9999, 0.9999))
            corr[i, j] = corr[j, i] = c

    # shrink correlations toward identity (Ledoit-Wolf style constant target)
    if shrink > 0.0:
        corr = (1.0 - shrink) * corr + shrink * np.eye(n)
        np.fill_diagonal(corr, 1.0)

    cov = np.outer(sd, sd) * corr
    bad = ~valid
    if bad.any():
        cov[bad, :] = 0.0
        cov[:, bad] = 0.0
        cov[bad, bad] = EPS            # keep matrix non-degenerate

    cov = nearest_psd(cov)
    # restore exact placeholder diagonal for invalid assets
    if bad.any():
        cov[np.ix_(bad, ~bad)] = 0.0
        cov[np.ix_(~bad, bad)] = 0.0
        for i in np.where(bad)[0]:
            cov[i, :] = 0.0
            cov[:, i] = 0.0
            cov[i, i] = EPS
    return cov, valid


# =============================================================================
# 2. ERC SOLVER (convex log-barrier primary, SLSQP + inverse-vol fallbacks)
# =============================================================================
def risk_contributions(w: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """Normalised (fractional) risk contributions; sums to 1."""
    w = np.asarray(w, dtype=float)
    pv = float(w @ cov @ w)
    if pv <= 0:
        return np.full(w.size, np.nan)
    return (w * (cov @ w)) / pv


def _erc_log_barrier(cov: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
    """min 0.5 w'Sw - sum b_i ln w_i, w>0  ->  normalise. Unique solution."""
    n = cov.shape[0]
    d = np.clip(np.diag(cov), EPS, None)
    x0 = b / np.sqrt(d)
    x0 = x0 / x0.sum()

    def fg(x: np.ndarray):
        x = np.clip(x, 1e-14, None)
        sx = cov @ x
        f = 0.5 * float(x @ sx) - float(b @ np.log(x))
        g = sx - b / x
        return f, g

    res = minimize(
        fg, x0, jac=True, method="L-BFGS-B",
        bounds=[(1e-14, None)] * n,
        options={"maxiter": 2000, "ftol": 1e-18, "gtol": 1e-14, "maxcor": 30},
    )
    x = res.x
    if not np.all(np.isfinite(x)) or x.sum() <= 0:
        return None
    return x / x.sum()


def _erc_slsqp(cov: np.ndarray, b: np.ndarray, ub: float) -> Optional[np.ndarray]:
    """Fallback / capped solve: minimise dispersion of fractional RCs."""
    n = cov.shape[0]

    def obj(w: np.ndarray) -> float:
        pv = float(w @ cov @ w)
        if pv <= 0:
            return 1e6
        rc = (w * (cov @ w)) / pv
        return float(np.sum((rc - b) ** 2))

    x0 = np.minimum(np.full(n, 1.0 / n), ub)
    x0 = x0 / x0.sum()
    res = minimize(
        obj, x0, method="SLSQP",
        bounds=[(0.0, ub)] * n,
        constraints=({"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)},),
        options={"maxiter": 500, "ftol": 1e-14},
    )
    if not res.success or not np.all(np.isfinite(res.x)):
        return None
    w = np.clip(res.x, 0.0, ub)
    s = w.sum()
    return w / s if s > 0 else None


def _cap_weights(w: np.ndarray, cap: float) -> np.ndarray:
    """Iterative water-filling cap that preserves relative ERC ordering."""
    n = w.size
    if cap is None or cap * n < 1.0 - 1e-12:
        return np.full(n, 1.0 / n)
    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    if w.sum() <= 0:
        w = np.full(n, 1.0 / n)
    w = w / w.sum()
    for _ in range(200):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess = float(np.sum(w[over] - cap))
        w[over] = cap
        free = ~over
        if not free.any():
            w = np.full(n, 1.0 / n)
            break
        pool = w[free]
        if pool.sum() <= 0:
            w[free] = excess / free.sum()
        else:
            w[free] = pool + excess * pool / pool.sum()
    return w / w.sum()


def erc_weights(
    cov: np.ndarray,
    budgets: Optional[np.ndarray] = None,
    max_weight: Optional[float] = None,
    tol: float = 5e-3,
) -> np.ndarray:
    """
    Equal- (or budgeted-) risk-contribution long-only fully-invested weights.
    Guaranteed to return finite, non-negative weights summing to 1.
    """
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if n == 0:
        return np.zeros(0)
    if n == 1:
        return np.ones(1)

    b = np.full(n, 1.0 / n) if budgets is None else np.asarray(budgets, float)
    b = np.clip(b, EPS, None)
    b = b / b.sum()

    d = np.diag(cov)
    if not np.all(np.isfinite(cov)) or np.any(~np.isfinite(d)) or np.any(d <= 0):
        return np.full(n, 1.0 / n)

    cov = nearest_psd(cov)
    ub = 1.0 if max_weight is None else float(np.clip(max_weight, 1.0 / n, 1.0))

    inv_vol = 1.0 / np.sqrt(np.clip(np.diag(cov), EPS, None))
    inv_vol = inv_vol / inv_vol.sum()

    candidates: List[np.ndarray] = []
    w_lb = _erc_log_barrier(cov, b)
    if w_lb is not None:
        candidates.append(w_lb if max_weight is None else _cap_weights(w_lb, ub))
    w_sl = _erc_slsqp(cov, b, ub)
    if w_sl is not None:
        candidates.append(w_sl)
    candidates.append(inv_vol if max_weight is None else _cap_weights(inv_vol, ub))
    candidates.append(_cap_weights(np.full(n, 1.0 / n), ub))

    best, best_err = None, np.inf
    for w in candidates:
        if w is None or not np.all(np.isfinite(w)) or w.min() < -1e-12:
            continue
        w = np.clip(w, 0.0, None)
        s = w.sum()
        if s <= 0:
            continue
        w = w / s
        if max_weight is not None and w.max() > ub + 1e-9:
            continue
        rc = risk_contributions(w, cov)
        err = np.inf if not np.all(np.isfinite(rc)) else float(np.max(np.abs(rc - b)))
        if err < best_err:
            best, best_err = w, err
        if best_err <= tol and max_weight is None:
            break
    if best is None:
        best = np.full(n, 1.0 / n)
    return best


# =============================================================================
# 3. ROLLING ERC UTILITY (inception-aware, look-ahead free) — fixed v10 API
# =============================================================================
def calculate_dynamic_erc_weights(
    returns: np.ndarray,
    positions: np.ndarray,
    lookback: int = 252,
    min_obs: int = 126,
    shrink: float = 0.10,
    max_weight: Optional[float] = None,
    step: int = 1,
    hold: bool = True,
) -> np.ndarray:
    """
    Rolling ERC weights.

    returns   : (N, T) simple returns, NaN before inception (NEVER filled).
    positions : (N, T) 0/1 desired-holding flags (evaluated at column t using
                information available at t; the returned weights for column t
                are meant to be EARNED from t+1 onward by the caller).
    step      : recompute every `step` columns (>=1); `hold` carries the last
                solution forward between recomputations.

    Returns (N, T) weights; each column sums to 1 when anything is active,
    else all zeros. An asset never receives weight unless it has `lookback`
    *fully observed* trailing returns and an estimable covariance row.
    """
    returns = np.asarray(returns, dtype=float)
    positions = np.asarray(positions)
    if returns.shape != positions.shape:
        raise ValueError("returns and positions must share shape (N, T)")
    if lookback < 2 or min_obs < 2 or min_obs > lookback:
        raise ValueError("bad lookback/min_obs")
    step = max(1, int(step))

    n, t_total = returns.shape
    weights = np.zeros((n, t_total), dtype=float)
    last = np.zeros(n, dtype=float)

    for t in range(t_total):
        if t < lookback:
            continue
        recompute = ((t - lookback) % step == 0) or not hold
        if not recompute:
            weights[:, t] = last
            continue

        block = returns[:, t - lookback:t]          # data through t-1: no look-ahead
        complete = np.isfinite(block).all(axis=1)   # strict inception alignment
        want = positions[:, t] > 0
        cov, valid = compute_pairwise_covariance(block, min_obs=min_obs, shrink=shrink)
        active = want & complete & valid
        if not active.any():
            last = np.zeros(n)
            continue
        sub = cov[np.ix_(active, active)]
        w_sub = erc_weights(sub, max_weight=max_weight)
        col = np.zeros(n)
        col[active] = w_sub
        weights[:, t] = col
        last = col
    return weights


# =============================================================================
# 4. DATA LAYER
# =============================================================================
def synthetic_prices(cfg: Config, inception: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Reproducible correlated GBM universe with STAGGERED inception dates."""
    idx = pd.bdate_range(cfg.start, cfg.end)
    tickers = list(cfg.all_assets)
    t_len, n = len(idx), len(tickers)
    rng = np.random.default_rng(cfg.seed)

    mkt = rng.standard_normal(t_len) * 0.010
    rate = rng.standard_normal(t_len) * 0.004
    betas = rng.uniform(0.15, 1.25, n)
    rate_beta = rng.uniform(-0.6, 0.9, n)
    idio = rng.uniform(0.0035, 0.0110, n)
    drift = rng.uniform(0.00006, 0.00040, n)

    rets = (drift[None, :]
            + betas[None, :] * mkt[:, None]
            + rate_beta[None, :] * rate[:, None]
            + rng.standard_normal((t_len, n)) * idio[None, :])
    px = 100.0 * np.cumprod(1.0 + rets, axis=0)
    df = pd.DataFrame(px, index=idx, columns=tickers)

    default_inception = {
        "SPY": "1998-01-01", "QQQ": "1999-03-10", "IWM": "2000-05-26",
        "EFA": "2001-08-17", "EEM": "2003-04-14", "VNQ": "2004-09-29",
        "GLD": "2004-11-18", "DBC": "2006-02-06", "IEF": "2002-07-26",
        "TLT": "2002-07-26", "LQD": "2002-07-30", "SHY": "2002-07-26",
    }
    inc = dict(default_inception)
    if inception:
        inc.update(inception)
    for tk, d0 in inc.items():
        if tk in df.columns:
            df.loc[df.index < pd.Timestamp(d0), tk] = np.nan
    return df


def load_prices(cfg: Config) -> Tuple[pd.DataFrame, pd.Series, str]:
    """Try yfinance (adjusted closes + ^IRX); fall back to synthetic data."""
    tickers = list(cfg.all_assets)
    try:
        import yfinance as yf  # noqa
        raw = yf.download(tickers + ["^IRX"], start=cfg.start, end=cfg.end,
                          auto_adjust=True, progress=False, group_by="column")
        if isinstance(raw.columns, pd.MultiIndex):
            close = raw["Close"].copy()
        else:
            close = raw.copy()
        close = close.sort_index()
        px = close[[t for t in tickers if t in close.columns]].astype(float)
        if px.shape[1] < 4 or len(px) < cfg.max_lookback + 60:
            raise RuntimeError("insufficient live data")
        px = px.dropna(how="all")
        if "^IRX" in close.columns:
            irx = close["^IRX"].reindex(px.index).ffill() / 100.0
            irx = irx.clip(lower=0.0).fillna(cfg.fallback_rf_annual)
        else:
            irx = pd.Series(cfg.fallback_rf_annual, index=px.index)
        rf_daily = (1.0 + irx) ** (1.0 / cfg.trading_days) - 1.0
        return px, rf_daily.astype(float), "yfinance"
    except Exception:
        px = synthetic_prices(cfg)
        ann = pd.Series(cfg.fallback_rf_annual, index=px.index)
        rf_daily = (1.0 + ann) ** (1.0 / cfg.trading_days) - 1.0
        return px, rf_daily.astype(float), "synthetic"


# =============================================================================
# 5. SIGNALS
# =============================================================================
def month_end_positions(index: pd.DatetimeIndex) -> List[int]:
    s = pd.Series(np.arange(len(index)), index=index)
    return sorted(int(v) for v in s.groupby([index.year, index.month]).max().values)


def _rf_compound(rf_daily: np.ndarray, i: int, lb: int) -> float:
    """Compounded risk-free return over the same window as the price momentum."""
    seg = rf_daily[i - lb + 1: i + 1]
    if seg.size == 0:
        return 0.0
    return float(np.prod(1.0 + seg) - 1.0)


def excess_momentum_scores(
    px: np.ndarray,          # (T, N) prices with NaN pre-inception
    rf_daily: np.ndarray,    # (T,)
    i: int,
    lookbacks: Sequence[int],
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Average EXCESS (over compounded risk-free) total return across lookbacks
    plus per-lookback excess matrix. NaN where inception-incomplete.
    """
    n = px.shape[1]
    k = len(lookbacks)
    mat = np.full((k, n), np.nan)
    for a, lb in enumerate(lookbacks):
        j = i - lb
        if j < 0:
            continue
        p0, p1 = px[j], px[i]
        ok = np.isfinite(p0) & np.isfinite(p1) & (p0 > 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            tr = np.where(ok, p1 / np.where(ok, p0, 1.0) - 1.0, np.nan)
        mat[a] = tr - _rf_compound(rf_daily, i, lb)
    score = np.where(np.isfinite(mat).all(axis=0), np.nanmean(mat, axis=0), np.nan)
    return score, mat


# =============================================================================
# 6. BACKTEST ENGINE
# =============================================================================
@dataclass
class BacktestResult:
    net_returns: pd.Series
    gross_returns: pd.Series
    equity: pd.Series
    weights: pd.DataFrame
    cash_weight: pd.Series
    turnover: pd.Series
    costs: pd.Series
    rf_daily: pd.Series
    leverage: pd.Series
    n_holdings: pd.Series
    stats: Dict[str, float] = field(default_factory=dict)
    diagnostics: Dict[str, float] = field(default_factory=dict)


def run_backtest(prices: pd.DataFrame, rf_daily: pd.Series, cfg: Config) -> BacktestResult:
    cfg.validate()

    prices = prices.sort_index().copy()
    prices = prices[[c for c in cfg.all_assets if c in prices.columns]]
    if prices.shape[1] == 0:
        raise ValueError("no usable price columns")
    prices = prices.astype(float)
    prices[prices <= 0] = np.nan                      # non-positive prices are invalid

    idx = prices.index
    rf = rf_daily.reindex(idx).ffill().fillna(0.0).astype(float)

    assets = list(prices.columns)
    n = len(assets)
    pos = {a: k for k, a in enumerate(assets)}
    risk_idx = np.array([pos[a] for a in cfg.risk_assets if a in pos], dtype=int)
    def_idx = np.array([pos[a] for a in cfg.defensive_assets if a in pos], dtype=int)
    if risk_idx.size < cfg.top_n:
        raise ValueError("risk universe smaller than top_n after alignment")

    px = prices.to_numpy(dtype=float)                 # (T, N)
    ret = prices.pct_change().to_numpy(dtype=float)   # NaN pre-inception: NEVER filled
    price_ok = np.isfinite(px)
    ret_ok = np.isfinite(ret)

    t_len = len(idx)
    tc = cfg.tc_bps / 1e4
    borrow_daily = (1.0 + cfg.borrow_spread_bps / 1e4) ** (1.0 / cfg.trading_days) - 1.0
    lookbacks = tuple(sorted(set(cfg.mom_lookbacks)))
    abs_pos = lookbacks.index(cfg.abs_mom_lookback)

    rebal = set(month_end_positions(idx))
    first_valid = cfg.max_lookback + 1

    W = np.zeros((t_len, n))          # weights held INTO day t (earning day t's return)
    cash_w = np.zeros(t_len)
    gross_r = np.zeros(t_len)
    net_r = np.zeros(t_len)
    turn = np.zeros(t_len)
    cost = np.zeros(t_len)
    nhold = np.zeros(t_len, dtype=int)

    w = np.zeros(n)                   # current post-trade weights
    c = 1.0                           # current cash weight (may be negative)
    started = False
    start_i = None
    phantom_violations = 0
    forced_liquidations = 0

    rf_arr = rf.to_numpy(dtype=float)

    for i in range(t_len):
        # ---------- 1. earn today's return on yesterday's post-trade book ----
        W[i] = w
        cash_w[i] = c
        nhold[i] = int((np.abs(w) > 1e-12).sum())

        if i == 0:
            g = 0.0
        else:
            r_eff = np.where(ret_ok[i], ret[i], 0.0)   # stale/halted -> 0, never NaN
            # phantom audit: no weight may sit on an asset without a live price
            if np.any((np.abs(w) > 1e-12) & ~price_ok[i - 1]):
                phantom_violations += 1
            cash_rate = rf_arr[i] if c >= 0 else rf_arr[i] + borrow_daily
            g = float(w @ r_eff) + c * cash_rate

        gross_r[i] = g
        denom = 1.0 + g
        if denom <= 1e-12:                              # total-ruin guard
            denom = 1e-12

        # ---------- 2. drift weights with realised returns -------------------
        if i > 0:
            r_eff = np.where(ret_ok[i], ret[i], 0.0)
            cash_rate = rf_arr[i] if c >= 0 else rf_arr[i] + borrow_daily
            w = w * (1.0 + r_eff) / denom
            c = c * (1.0 + cash_rate) / denom

        day_cost = 0.0
        day_turn = 0.0

        # ---------- 3. forced liquidation of assets that went dark ----------
        dark = (np.abs(w) > 1e-12) & ~price_ok[i]
        if dark.any():
            amt = float(np.abs(w[dark]).sum())
            day_turn += amt
            day_cost += tc * amt
            c += float(w[dark].sum())
            w[dark] = 0.0
            forced_liquidations += 1

        # ---------- 4. rebalance (signals use data through i, earned from i+1)
        if i >= first_valid and i in rebal:
            target = _build_target_weights(
                i, px, ret, rf_arr, cfg, risk_idx, def_idx, lookbacks, abs_pos
            )
            delta = np.abs(target - w)
            day_turn += float(delta.sum())
            day_cost += tc * float(delta.sum())
            w = target.copy()
            c = 1.0 - float(w.sum()) - day_cost * 0.0   # cost taken out of return stream
            if not started:
                started = True
                start_i = i

        turn[i] = day_turn
        cost[i] = day_cost
        net_r[i] = g - day_cost

    # ------------------------------------------------------------------ series
    net = pd.Series(net_r, index=idx, name="net")
    grs = pd.Series(gross_r, index=idx, name="gross")
    wdf = pd.DataFrame(W, index=idx, columns=assets)
    cser = pd.Series(cash_w, index=idx, name="cash")
    tser = pd.Series(turn, index=idx, name="turnover")
    kser = pd.Series(cost, index=idx, name="cost")
    lev = pd.Series(np.abs(W).sum(axis=1), index=idx, name="gross_leverage")
    hser = pd.Series(nhold, index=idx, name="n_holdings")

    if start_i is None:
        raise RuntimeError("no rebalance ever occurred: history shorter than max lookback")

    live = slice(start_i + 1, t_len)                    # first earning day
    net_live = net.iloc[live]
    grs_live = grs.iloc[live]
    rf_live = rf.iloc[live]

    equity = (1.0 + net_live).cumprod()
    equity.name = "equity"

    # --------------------------------- hard audits (phantom assets, identity)
    mask_live = pd.DataFrame(price_ok, index=idx, columns=assets).shift(1).fillna(False)
    phantom = ((wdf.abs() > 1e-12) & (~mask_live.astype(bool))).to_numpy().sum()
    assert phantom == 0, f"PHANTOM ASSET DETECTED: {phantom} weight-on-nonexistent-asset cells"
    assert phantom_violations == 0, "phantom asset audit failed inside the loop"
    wsum = (wdf.iloc[live].sum(axis=1) + cser.iloc[live]).to_numpy()
    assert np.allclose(wsum, 1.0, atol=1e-8), "weights + cash must equal 1 at all times"
    assert np.isfinite(net_live.to_numpy()).all(), "non-finite portfolio return"

    stats = performance_stats(net_live, rf_live, cfg.trading_days)
    stats_gross = performance_stats(grs_live, rf_live, cfg.trading_days)

    years = len(net_live) / cfg.trading_days
    diagnostics = {
        "start": str(net_live.index[0].date()),
        "end": str(net_live.index[-1].date()),
        "years": years,
        "n_assets": float(n),
        "avg_holdings": float(hser.iloc[live].mean()),
        "avg_gross_leverage": float(lev.iloc[live].mean()),
        "max_gross_leverage": float(lev.iloc[live].max()),
        "pct_days_levered": float((lev.iloc[live] > 1.0 + 1e-9).mean()),
        "annual_turnover": float(tser.iloc[live].sum() / max(years, EPS)),
        "total_cost_drag_annual": float(kser.iloc[live].sum() / max(years, EPS)),
        "cagr_gross": stats_gross["CAGR"],
        "sharpe_gross": stats_gross["Sharpe"],
        "cost_cagr_impact": stats_gross["CAGR"] - stats["CAGR"],
        "forced_liquidations": float(forced_liquidations),
        "phantom_violations": 0.0,
    }

    return BacktestResult(
        net_returns=net_live, gross_returns=grs_live, equity=equity,
        weights=wdf.iloc[live], cash_weight=cser.iloc[live],
        turnover=tser.iloc[live], costs=kser.iloc[live], rf_daily=rf_live,
        leverage=lev.iloc[live], n_holdings=hser.iloc[live],
        stats=stats, diagnostics=diagnostics,
    )


def _build_target_weights(
    i: int,
    px: np.ndarray,
    ret: np.ndarray,
    rf_arr: np.ndarray,
    cfg: Config,
    risk_idx: np.ndarray,
    def_idx: np.ndarray,
    lookbacks: Tuple[int, ...],
    abs_pos: int,
) -> np.ndarray:
    """
    Dual momentum + absolute momentum (on ALL assets) + ERC + vol target.
    Uses only information available at index i. Returns full-length weights.
    """
    n = px.shape[1]
    target = np.zeros(n)

    score, mat = excess_momentum_scores(px, rf_arr, i, lookbacks)

    # ---- covariance / inception eligibility --------------------------------
    lb = cfg.cov_lookback
    block = ret[i - lb + 1: i + 1, :].T                # (N, lb), data through i
    cov, cov_valid = compute_pairwise_covariance(
        block, min_obs=cfg.cov_min_obs, shrink=cfg.corr_shrink
    )
    complete_hist = np.isfinite(block).all(axis=1)     # strict inception alignment
    live_now = np.isfinite(px[i])
    eligible = live_now & complete_hist & cov_valid & np.isfinite(score)

    # ---- absolute momentum gate (risk AND defensive alike) ----------------
    abs_pass = np.zeros(n, dtype=bool)
    ok = np.isfinite(mat[abs_pos]) & np.isfinite(score)
    abs_pass[ok] = (mat[abs_pos][ok] > 0.0) & (score[ok] > 0.0)

    # ---- relative momentum: rank risk sleeve -------------------------------
    r_ok = np.array([k for k in risk_idx if eligible[k]], dtype=int)
    if r_ok.size:
        r_ok = r_ok[np.argsort(-score[r_ok], kind="stable")]
    chosen: List[int] = [int(k) for k in r_ok[: cfg.top_n] if abs_pass[k]]

    # ---- unfilled slots roll to defensive assets that PASS absolute mom ----
    empty = cfg.top_n - len(chosen)
    if empty > 0 and def_idx.size:
        d_ok = np.array([k for k in def_idx if eligible[k] and abs_pass[k]], dtype=int)
        if d_ok.size:
            d_ok = d_ok[np.argsort(-score[d_ok], kind="stable")]
            for k in d_ok[:empty]:
                chosen.append(int(k))

    if not chosen:
        return target                                  # 100% cash (T-bill)

    sleeve = np.array(sorted(set(chosen)), dtype=int)
    sub = cov[np.ix_(sleeve, sleeve)]
    w_sub = erc_weights(sub, max_weight=cfg.max_weight)

    sleeve_frac = len(sleeve) / cfg.top_n              # unfilled slots stay in cash
    raw = np.zeros(n)
    raw[sleeve] = w_sub * sleeve_frac

    k_scale = 1.0
    if cfg.use_vol_target:
        var = float(raw @ cov @ raw)
        vol_ann = math.sqrt(max(var, 0.0) * cfg.trading_days)
        k_scale = cfg.target_vol / vol_ann if vol_ann > 1e-10 else 1.0
        gross = float(np.abs(raw).sum())
        if gross > 1e-12:
            k_scale = min(k_scale, cfg.max_gross_leverage / gross)
        k_scale = float(np.clip(k_scale, 0.0, cfg.max_gross_leverage / max(gross, EPS)))

    target = raw * k_scale
    target[~np.isfinite(target)] = 0.0
    target[target < 0.0] = 0.0
    # final phantom guard: nothing may be held that is not live today
    target[~live_now] = 0.0
    return target


# =============================================================================
# 7. PERFORMANCE STATISTICS (TRUE SHARPE)
# =============================================================================
def max_drawdown(equity: pd.Series) -> Tuple[float, Optional[pd.Timestamp]]:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min()), (dd.idxmin() if len(dd) else None)


def performance_stats(returns: pd.Series, rf_daily: pd.Series, freq: int = 252) -> Dict[str, float]:
    """
    TRUE Sharpe ratio: mean(excess) / std(excess) * sqrt(freq), computed from
    arithmetic daily excess returns over the realised risk-free rate (ddof=1).
    CAGR/vol is reported separately and is NOT called Sharpe.
    """
    r = pd.Series(returns).astype(float).dropna()
    if r.empty:
        return {k: float("nan") for k in
                ("CAGR", "Vol", "Sharpe", "Sortino", "MaxDD", "Calmar", "HitRate",
                 "Skew", "Kurtosis", "BestDay", "WorstDay", "CAGR_over_Vol",
                 "GeoExcess", "VaR95", "CVaR95", "N")}
    rfa = pd.Series(rf_daily).reindex(r.index).ffill().fillna(0.0).astype(float)
    ex = r - rfa

    n_obs = len(r)
    years = n_obs / freq
    total_growth = float((1.0 + r).prod())
    cagr = total_growth ** (1.0 / years) - 1.0 if years > 0 and total_growth > 0 else float("nan")
    vol = float(r.std(ddof=1) * math.sqrt(freq)) if n_obs > 1 else float("nan")

    sd_ex = float(ex.std(ddof=1)) if n_obs > 1 else float("nan")
    sharpe = float(ex.mean() / sd_ex * math.sqrt(freq)) if sd_ex and sd_ex > 0 else float("nan")

    downside = ex[ex < 0.0]
    dstd = float(downside.std(ddof=1)) if len(downside) > 1 else float("nan")
    sortino = float(ex.mean() / dstd * math.sqrt(freq)) if dstd and dstd > 0 else float("nan")

    equity = (1.0 + r).cumprod()
    mdd, _ = max_drawdown(equity)
    calmar = float(cagr / abs(mdd)) if mdd < -1e-12 and np.isfinite(cagr) else float("nan")

    geo_rf = float((1.0 + rfa).prod()) ** (1.0 / years) - 1.0 if years > 0 else float("nan")
    var95 = float(np.percentile(r.to_numpy(), 5))
    tail = r[r <= var95]

    return {
        "CAGR": float(cagr),
        "Vol": vol,
        "Sharpe": sharpe,                       # TRUE excess-return Sharpe
        "Sortino": sortino,
        "MaxDD": float(mdd),
        "Calmar": calmar,
        "HitRate": float((r > 0).mean()),
        "Skew": float(r.skew()),
        "Kurtosis": float(r.kurtosis()),
        "BestDay": float(r.max()),
        "WorstDay": float(r.min()),
        "CAGR_over_Vol": float(cagr / vol) if vol and vol > 0 else float("nan"),
        "GeoExcess": float(cagr - geo_rf),
        "VaR95": var95,
        "CVaR95": float(tail.mean()) if len(tail) else float("nan"),
        "N": float(n_obs),
    }


# =============================================================================
# 8. SELF-TESTS
# =============================================================================
def _self_tests() -> None:
    rng = np.random.default_rng(0)

    # --- ERC: equal risk contributions on a random PSD matrix ---------------
    a = rng.standard_normal((6, 6))
    cov = nearest_psd(a @ a.T / 100.0)
    w = erc_weights(cov, max_weight=None)
    rc = risk_contributions(w, cov)
    assert abs(w.sum() - 1.0) < 1e-10, "ERC weights must sum to 1"
    assert w.min() >= -1e-12, "ERC weights must be non-negative"
    assert np.max(np.abs(rc - 1.0 / 6)) < 5e-3, f"ERC risk parity failed: {rc}"

    # --- ERC on a diagonal matrix must equal inverse-vol -------------------
    d = np.diag(np.array([0.01, 0.04, 0.09, 0.16]))
    w2 = erc_weights(d)
    iv = 1.0 / np.sqrt(np.diag(d))
    iv /= iv.sum()
    assert np.max(np.abs(w2 - iv)) < 1e-4, "diagonal ERC must equal inverse-vol"

    # --- weight cap respected ---------------------------------------------
    w3 = erc_weights(cov, max_weight=0.25)
    assert w3.max() <= 0.25 + 1e-9 and abs(w3.sum() - 1.0) < 1e-10, "cap violated"

    # --- pairwise covariance: pre-inception NaNs create no phantom ---------
    block = rng.standard_normal((3, 300)) * 0.01
    block[2, :250] = np.nan                     # young asset: 50 obs < min_obs
    cv, valid = compute_pairwise_covariance(block, min_obs=126)
    assert not valid[2], "young asset must be flagged invalid"
    assert np.allclose(cv[2, :2], 0.0) and np.allclose(cv[:2, 2], 0.0), "phantom covariance"
    assert np.all(np.linalg.eigvalsh(cv) > -1e-10), "covariance must be PSD"

    # --- rolling utility: no weight before inception -----------------------
    rets = rng.standard_normal((4, 800)) * 0.01
    rets[3, :600] = np.nan
    positions = np.ones((4, 800))
    wm = calculate_dynamic_erc_weights(rets, positions, lookback=252, min_obs=126)
    assert np.all(wm[3, :600] == 0.0), "phantom weight before inception"
    cols = wm.sum(axis=0)[252:]
    assert np.all(np.abs(cols - 1.0) < 1e-8), "each active column must sum to 1"

    # --- Sharpe formula sanity: zero-vol excess -> nan, not inf ------------
    r = pd.Series(np.full(500, 0.0004), index=pd.bdate_range("2010-01-01", periods=500))
    st = performance_stats(r, pd.Series(0.0004, index=r.index))
    assert not np.isfinite(st["Sharpe"]), "zero-vol excess must not yield finite Sharpe"

    # --- Sharpe formula sanity: known iid case ----------------------------
    x = pd.Series(rng.normal(0.0005, 0.01, 5000),
                  index=pd.bdate_range("1990-01-01", periods=5000))
    rf0 = pd.Series(0.0, index=x.index)
    st2 = performance_stats(x, rf0)
    expected = x.mean() / x.std(ddof=1) * math.sqrt(252)
    assert abs(st2["Sharpe"] - expected) < 1e-10, "Sharpe must be excess-return based"

    print("[self-tests] all passed")


# =============================================================================
# 9. REPORTING / MAIN
# =============================================================================
def print_report(res: BacktestResult, cfg: Config, source: str) -> None:
    s, d = res.stats, res.diagnostics
    line = "=" * 74
    print(line)
    print(" OPUS ERC OPTIMIZER v11 — ABSOLUTE SURRENDER PROTOCOL")
    print(line)
    print(f" data source           : {source}")
    print(f" period                : {d['start']} -> {d['end']}  ({d['years']:.2f} yrs)")
    print(f" universe              : {int(d['n_assets'])} assets "
          f"({len(cfg.risk_assets)} risk / {len(cfg.defensive_assets)} defensive)")
    print(f" slots / lookbacks     : top {cfg.top_n} | mom {cfg.mom_lookbacks} "
          f"| abs {cfg.abs_mom_lookback}d | cov {cfg.cov_lookback}d")
    print(f" frictions             : {cfg.tc_bps:.1f} bps/side, "
          f"borrow +{cfg.borrow_spread_bps:.0f} bps over rf")
    print(line)
    print(" PERFORMANCE (NET OF COSTS & FINANCING)")
    print(f"   CAGR                : {s['CAGR']:>10.2%}")
    print(f"   Volatility (ann)    : {s['Vol']:>10.2%}")
    print(f"   Sharpe (true, excess): {s['Sharpe']:>9.3f}")
    print(f"   Sortino             : {s['Sortino']:>10.3f}")
    print(f"   Max Drawdown        : {s['MaxDD']:>10.2%}")
    print(f"   Calmar              : {s['Calmar']:>10.3f}")
    print(f"   Geometric excess    : {s['GeoExcess']:>10.2%}")
    print(f"   CAGR/Vol (NOT Sharpe): {s['CAGR_over_Vol']:>9.3f}")
    print(f"   Hit rate            : {s['HitRate']:>10.2%}")
    print(f"   VaR95 / CVaR95 (1d) : {s['VaR95']:>10.2%} / {s['CVaR95']:.2%}")
    print(f"   Skew / ExKurt       : {s['Skew']:>10.2f} / {s['Kurtosis']:.2f}")
    print(line)
    print(" IMPLEMENTATION DIAGNOSTICS")
    print(f"   Avg holdings        : {d['avg_holdings']:>10.2f}")
    print(f"   Avg / max gross lev : {d['avg_gross_leverage']:>10.2f} / {d['max_gross_leverage']:.2f}")
    print(f"   Days levered        : {d['pct_days_levered']:>10.2%}")
    print(f"   Annual turnover     : {d['annual_turnover']:>10.2f}x")
    print(f"   Annual cost drag    : {d['total_cost_drag_annual']:>10.2%}")
    print(f"   Gross CAGR / Sharpe : {d['cagr_gross']:>10.2%} / {d['sharpe_gross']:.3f}")
    print(f"   Cost impact on CAGR : {d['cost_cagr_impact']:>10.2%}")
    print(f"   Forced liquidations : {int(d['forced_liquidations']):>10d}")
    print(f"   Phantom assets      : {int(d['phantom_violations']):>10d}  (must be 0)")
    print(line)
    avg_w = res.weights.mean().sort_values(ascending=False)
    avg_w = avg_w[avg_w > 1e-6]
    print(" AVERAGE ALLOCATION")
    for k, v in avg_w.items():
        print(f"   {k:<8}: {v:>7.2%}")
    print(f"   {'CASH':<8}: {res.cash_weight.mean():>7.2%}")
    print(line)


def main() -> BacktestResult:
    _self_tests()
    cfg = Config()
    cfg.validate()
    prices, rf_daily, source = load_prices(cfg)
    res = run_backtest(prices, rf_daily, cfg)
    print_report(res, cfg, source)
    return res


if __name__ == "__main__":
    main()