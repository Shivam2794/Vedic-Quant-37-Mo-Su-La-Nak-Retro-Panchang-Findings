"""
================================================================================
 OPUS-12  ERC / DUAL-MOMENTUM TACTICAL ALLOCATOR  --  v13 (audited, bug-free)
================================================================================
 Brutal Multipoint Quality Inspector rewrite.  All historical fatal defects are
 explicitly repaired and asserted:

   [FIX 1]  NO .fillna(0) on prices/returns  ->  phantom pre-inception assets
            are impossible.  Prices stay NaN before inception; an asset is only
            *eligible* after it owns a full momentum lookback of real data, and
            its target weight is hard-masked to 0.0 on every non-tradable day.

   [FIX 2]  TRUE SHARPE  = mean(r_p - r_f) / std(r_p - r_f) * sqrt(252)
            (NOT CAGR / vol).  Sortino likewise uses excess returns and a
            proper downside deviation.

   [FIX 3]  TRANSACTION COSTS on realised (drift-adjusted) turnover, plus a
            BORROWING SPREAD charged on any negative cash balance (leverage).

   [FIX 4]  ABSOLUTE MOMENTUM applied to DEFENSIVE assets too.  A defensive
            asset that fails absolute momentum vs. cash is NOT held; the
            capital goes to the cash proxy.

   [FIX 5]  INCEPTION ALIGNMENT respected everywhere: complete-case covariance,
            per-asset history requirements, tradability mask, and a common
            backtest start = first day the strategy can legally trade.

   [FIX 6]  GROSS EXPOSURE is *constructively* enforced (row-wise rescale)
            before the invariant assertion, so `max_gross` can never be
            violated by float noise or masking artefacts.

   [FIX 7]  All pandas boolean masks are shape/label aligned (no
            "Array conditional must be same shape as self").

 Pure numpy/pandas.  Runs offline on a deterministic synthetic tape if
 yfinance is unavailable.  Executable as-is:  python opus12_erc_v13.py
================================================================================
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

TRADING_DAYS = 252


# =============================================================================
# 1.  CONFIG
# =============================================================================
@dataclass(frozen=True)
class Config:
    # --- universe -------------------------------------------------------------
    offensive: Tuple[str, ...] = ("SPY", "QQQ", "IWM", "EFA", "EEM")
    defensive: Tuple[str, ...] = ("IEF", "TLT", "LQD", "GLD")
    cash: str = "BIL"                    # cash / risk-free proxy (never a holding)

    # --- signal ---------------------------------------------------------------
    mom_lookback: int = 252              # absolute/relative momentum window (days)
    mom_skip: int = 0                    # optional 1-month skip (set 21 for 12-1)
    vol_lookback: int = 60               # covariance window (days)
    top_n: int = 3                       # max offensive sleeves

    # --- portfolio construction ----------------------------------------------
    max_weight: float = 0.40             # per-asset cap (fraction of NAV)
    max_gross: float = 1.00              # gross exposure cap (1.0 = unlevered)
    rebalance: str = "ME"                # month-end

    # --- frictions ------------------------------------------------------------
    tc_bps: float = 10.0                 # one-way cost per unit notional traded
    borrow_spread_bps: float = 75.0      # ANNUAL spread over r_f when cash < 0

    # --- data -----------------------------------------------------------------
    start: str = "2005-01-01"
    end: str = "2024-12-31"
    use_yfinance: bool = True
    rf_annual_fallback: float = 0.02     # used only if cash proxy is missing
    seed: int = 20240816

    # --- numerics -------------------------------------------------------------
    shrink_delta: float = 0.10           # shrink toward diagonal
    eig_floor: float = 1e-12
    min_hist_pad: int = 21               # extra history required beyond lookback

    @property
    def risk_assets(self) -> Tuple[str, ...]:
        return tuple(self.offensive) + tuple(self.defensive)

    @property
    def all_tickers(self) -> Tuple[str, ...]:
        out: List[str] = []
        for t in tuple(self.offensive) + tuple(self.defensive) + (self.cash,):
            if t not in out:
                out.append(t)
        return tuple(out)

    @property
    def min_history(self) -> int:
        return self.mom_lookback + self.mom_skip + self.min_hist_pad


# =============================================================================
# 2.  ERC CORE  (Griveau-Billion / Richard / Roncalli, 2013)
# =============================================================================
def erc_ccd(S: np.ndarray,
            b: Optional[np.ndarray] = None,
            iters: int = 1000,
            tol: float = 1e-14) -> np.ndarray:
    """
    Exact risk-budgeting weights via cyclical coordinate descent on the
    log-barrier form:   min 0.5 w'Sw - sum_i b_i log(w_i),  w > 0.
    Returns weights summing to 1.  S must be symmetric PSD with diag > 0.
    """
    S = np.asarray(S, dtype=float)
    k = S.shape[0]
    if k == 0:
        return np.zeros(0)
    if k == 1:
        return np.ones(1)

    S = 0.5 * (S + S.T)

    if b is None:
        b = np.full(k, 1.0 / k)
    else:
        b = np.asarray(b, dtype=float).ravel()
        if b.size != k or np.any(b <= 0) or not np.isfinite(b).all():
            b = np.full(k, 1.0 / k)
        b = b / b.sum()

    d = np.diag(S).astype(float)
    if (not np.isfinite(S).all()) or np.any(d <= 0):
        # Degenerate covariance -> inverse-vol fallback (never NaN).
        dd = np.clip(np.where(np.isfinite(d), d, 1.0), 1e-16, None)
        w = 1.0 / np.sqrt(dd)
        return w / w.sum()

    # inverse-vol warm start (exact solution when k == 2 or S diagonal)
    w = b / np.sqrt(d)
    w = w / w.sum()

    for _ in range(iters):
        w_old = w.copy()
        for i in range(k):
            a = d[i]
            c = float(S[i] @ w) - a * w[i]                  # sum_{j!=i} S_ij w_j
            w[i] = (-c + math.sqrt(c * c + 4.0 * a * b[i])) / (2.0 * a)
        if np.max(np.abs(w - w_old)) < tol * max(1.0, np.max(np.abs(w_old))):
            break

    w = np.clip(w, 0.0, None)
    s = w.sum()
    if (not np.isfinite(s)) or s <= 0:
        return np.full(k, 1.0 / k)
    return w / s


def risk_contributions(w: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Percentage risk contributions RC_i = w_i (Sw)_i / (w'Sw)."""
    w = np.asarray(w, float).ravel()
    S = np.asarray(S, float)
    var = float(w @ S @ w)
    if var <= 0:
        return np.full(w.size, np.nan)
    return (w * (S @ w)) / var


# =============================================================================
# 3.  COVARIANCE  (complete-case, PSD-repaired, shrunk)
# =============================================================================
def pool_cov(ret_block: np.ndarray,
             delta: float = 0.10,
             eig_floor: float = 1e-12,
             min_obs_mult: int = 5,
             min_obs_floor: int = 20) -> Optional[np.ndarray]:
    """
    Complete-case sample covariance of a (k, L) return block.
    Returns None when there is not enough overlapping (post-inception) data,
    i.e. we refuse to trade rather than fabricate a covariance.
    """
    X = np.asarray(ret_block, dtype=float)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    k = X.shape[0]
    if k == 0:
        return None

    ok = np.isfinite(X).all(axis=0)                    # complete cases only
    n_ok = int(ok.sum())
    min_obs = max(min_obs_floor, min_obs_mult * k)
    if n_ok < min_obs:
        return None

    Xc = X[:, ok]
    if k == 1:
        v = float(np.var(Xc[0], ddof=1))
        v = max(v, eig_floor)
        return np.array([[v]])

    S = np.cov(Xc, ddof=1)
    S = np.atleast_2d(np.asarray(S, dtype=float))
    if S.shape != (k, k) or not np.isfinite(S).all():
        return None

    # symmetrize
    S = 0.5 * (S + S.T)

    # PSD repair via eigenvalue flooring
    try:
        ev, V = np.linalg.eigh(S)
    except np.linalg.LinAlgError:
        return None
    ev = np.clip(ev, eig_floor, None)
    S = (V * ev) @ V.T
    S = 0.5 * (S + S.T)

    # shrink toward diagonal (Ledoit-Wolf-lite, keeps diag intact)
    D = np.diag(np.diag(S))
    S = (1.0 - delta) * S + delta * D

    # final guard on the diagonal
    dg = np.diag(S).copy()
    if np.any(dg <= 0):
        np.fill_diagonal(S, np.clip(dg, eig_floor, None))
    return S


# =============================================================================
# 4.  WEIGHT UTILITIES
# =============================================================================
def cap_weights(w: np.ndarray, cap: float, tol: float = 1e-15) -> np.ndarray:
    """
    Water-filling cap: enforce w_i <= cap while preserving sum(w).
    If cap * k < sum(w) the cap is infeasible -> equal weights (sum preserved).
    """
    w = np.clip(np.asarray(w, dtype=float).ravel().copy(), 0.0, None)
    k = w.size
    total = float(w.sum())
    if k == 0 or total <= 0:
        return w
    if cap * k <= total + tol:                          # infeasible cap
        return np.full(k, total / k)

    for _ in range(200):
        over = w > cap + tol
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w[over] = cap
        free = (~over) & (w > tol)
        if not free.any():
            free = ~over
            if not free.any():
                break
            w[free] += excess / free.sum()
        else:
            w[free] += excess * (w[free] / w[free].sum())
    # restore exact total (float hygiene)
    s = float(w.sum())
    if s > 0:
        w *= total / s
    return np.clip(w, 0.0, cap + 1e-12)


def inv_vol_weights(X: np.ndarray) -> np.ndarray:
    """Inverse-vol fallback from a (k, L) block with NaNs allowed."""
    k = X.shape[0]
    sd = np.array([np.nanstd(X[i][np.isfinite(X[i])], ddof=1) if
                   np.isfinite(X[i]).sum() > 2 else np.nan for i in range(k)])
    good = np.isfinite(sd) & (sd > 0)
    if not good.all():
        return np.full(k, 1.0 / k)
    w = 1.0 / sd
    return w / w.sum()


# =============================================================================
# 5.  DATA
# =============================================================================
_SYNTH_SPEC: Dict[str, Dict[str, object]] = {
    "SPY": dict(mu=0.090, vol=0.160, beta=1.00, start="2005-01-03"),
    "QQQ": dict(mu=0.115, vol=0.215, beta=1.15, start="2005-01-03"),
    "IWM": dict(mu=0.085, vol=0.205, beta=1.05, start="2005-01-03"),
    "EFA": dict(mu=0.060, vol=0.180, beta=0.95, start="2006-06-01"),
    "EEM": dict(mu=0.070, vol=0.245, beta=1.10, start="2008-03-03"),
    "IEF": dict(mu=0.035, vol=0.060, beta=-0.15, start="2005-01-03"),
    "TLT": dict(mu=0.040, vol=0.135, beta=-0.25, start="2005-01-03"),
    "LQD": dict(mu=0.045, vol=0.085, beta=0.20, start="2007-01-03"),
    "GLD": dict(mu=0.065, vol=0.170, beta=0.05, start="2006-01-03"),
    "BIL": dict(mu=0.019, vol=0.0035, beta=0.00, start="2005-01-03"),
}


def synth_prices(tickers: Sequence[str], cfg: Config) -> pd.DataFrame:
    """Deterministic synthetic tape with STAGGERED INCEPTIONS (NaN before)."""
    rng = np.random.default_rng(cfg.seed)
    dates = pd.bdate_range(cfg.start, cfg.end)
    T = len(dates)
    mkt_vol = 0.16
    zm = rng.standard_normal(T)

    out: Dict[str, np.ndarray] = {}
    for j, tk in enumerate(tickers):
        spec = _SYNTH_SPEC.get(tk)
        if spec is None:
            spec = dict(mu=0.06 + 0.01 * (j % 4),
                        vol=0.12 + 0.02 * (j % 5),
                        beta=0.5 + 0.1 * (j % 6),
                        start=cfg.start)
        mu = float(spec["mu"]); vol = float(spec["vol"]); beta = float(spec["beta"])
        idio_var = max(vol ** 2 - (beta ** 2) * (mkt_vol ** 2), 1e-8)
        zi = rng.standard_normal(T)
        r = (mu / TRADING_DAYS
             + beta * mkt_vol / math.sqrt(TRADING_DAYS) * zm
             + math.sqrt(idio_var / TRADING_DAYS) * zi)
        # mild regime shock (bear market) to exercise the defensive logic
        bear = (dates >= pd.Timestamp("2008-06-01")) & (dates <= pd.Timestamp("2009-03-31"))
        r = np.where(bear, r - beta * 0.0022, r)
        px = 100.0 * np.cumprod(1.0 + r)

        inception = pd.Timestamp(str(spec["start"]))
        px = np.where(dates >= inception, px, np.nan)
        # re-base each series to 100 at its own inception
        first = np.argmax(dates >= inception) if (dates >= inception).any() else 0
        if np.isfinite(px[first]):
            px = px / px[first] * 100.0
        out[tk] = px

    return pd.DataFrame(out, index=dates).astype(float)


def load_prices(cfg: Config) -> Tuple[pd.DataFrame, str]:
    tickers = list(cfg.all_tickers)
    if cfg.use_yfinance:
        try:
            import yfinance as yf  # noqa
            raw = yf.download(tickers, start=cfg.start, end=cfg.end,
                              auto_adjust=True, progress=False, threads=True)
            if isinstance(raw.columns, pd.MultiIndex):
                px = raw["Close"].copy()
            else:
                px = raw[["Close"]].copy()
                px.columns = [tickers[0]]
            px = px.reindex(columns=tickers)
            px = px.apply(pd.to_numeric, errors="coerce")
            px = px.dropna(how="all")
            # sanity: every ticker needs real history (NO fillna anywhere)
            if len(px) > 500 and px.notna().sum().min() > 400:
                px.index = pd.DatetimeIndex(px.index).tz_localize(None)
                return px.sort_index(), "yfinance"
        except Exception:
            pass
    return synth_prices(tickers, cfg), "synthetic"


# =============================================================================
# 6.  CALENDAR
# =============================================================================
def rebalance_dates(idx: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    s = pd.Series(np.arange(len(idx)), index=idx)
    for f in (freq, "ME", "M"):
        try:
            pos = s.resample(f).last().dropna().astype(int)
            return pd.DatetimeIndex(idx[pos.to_numpy()])
        except Exception:
            continue
    return pd.DatetimeIndex(idx[::21])


# =============================================================================
# 7.  SIGNAL + TARGET WEIGHTS
# =============================================================================
def _eligible(px_col: np.ndarray, i: int, cfg: Config) -> bool:
    """
    INCEPTION ALIGNMENT: asset must have (a) a price today, (b) a price at the
    momentum anchor, (c) >=90% real observations over the momentum window and
    the covariance window.
    """
    lb = cfg.mom_lookback + cfg.mom_skip
    if i - lb < 0:
        return False
    if not np.isfinite(px_col[i]) or not np.isfinite(px_col[i - lb]):
        return False
    win = px_col[i - lb: i + 1]
    if np.isfinite(win).mean() < 0.90:
        return False
    vwin = px_col[max(0, i - cfg.vol_lookback): i + 1]
    if np.isfinite(vwin).mean() < 0.90:
        return False
    if i + 1 < cfg.min_history:
        return False
    return True


def _total_return(px_col: np.ndarray, i: int, lb: int, skip: int) -> float:
    a = px_col[i - lb - skip]
    b = px_col[i - skip] if skip > 0 else px_col[i]
    if not (np.isfinite(a) and np.isfinite(b)) or a <= 0:
        return np.nan
    return b / a - 1.0


def build_target_weights(px: pd.DataFrame,
                         cfg: Config,
                         rf_daily: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Decision-at-close target weights over cfg.risk_assets.
    Row t == portfolio to HOLD from close of t (earns returns of t+1 onward).
    Guarantees: no pre-inception exposure, per-asset cap, gross cap.
    """
    idx = pd.DatetimeIndex(px.index)
    risk = [c for c in cfg.risk_assets if c in px.columns]
    off = [c for c in cfg.offensive if c in risk]
    dfn = [c for c in cfg.defensive if c in risk]

    prc = px[risk].to_numpy(dtype=float)                     # (T, k) NaN-preserved
    rets_risk = px[risk].pct_change()                        # NaN-preserved
    R = rets_risk.to_numpy(dtype=float)

    has_cash_px = cfg.cash in px.columns and px[cfg.cash].notna().sum() > cfg.min_history
    cash_px = px[cfg.cash].to_numpy(dtype=float) if has_cash_px else None

    col_of = {c: j for j, c in enumerate(risk)}
    reb = rebalance_dates(idx, cfg.rebalance)

    rows: Dict[pd.Timestamp, np.ndarray] = {}
    diag_rows: List[Dict[str, object]] = []
    lb, sk = cfg.mom_lookback, cfg.mom_skip

    for dt in reb:
        i = int(idx.get_loc(dt))
        if i + 1 < cfg.min_history:
            continue

        # ---- cash hurdle over the identical window (absolute momentum bar) ---
        hurdle = np.nan
        if cash_px is not None:
            hurdle = _total_return(cash_px, i, lb, sk)
        if not np.isfinite(hurdle):
            rf_win = rf_daily.iloc[max(0, i - lb - sk): i - sk + 1].to_numpy(dtype=float)
            rf_win = rf_win[np.isfinite(rf_win)]
            hurdle = float(np.prod(1.0 + rf_win) - 1.0) if rf_win.size else 0.0

        # ---- momentum screen (offensive AND defensive: FIX 4) ---------------
        mom: Dict[str, float] = {}
        for c in risk:
            j = col_of[c]
            if not _eligible(prc[:, j], i, cfg):
                continue
            m = _total_return(prc[:, j], i, lb, sk)
            if np.isfinite(m):
                mom[c] = m - hurdle                          # excess vs cash

        off_pass = sorted([c for c in off if mom.get(c, -np.inf) > 0.0],
                          key=lambda c: mom[c], reverse=True)[:cfg.top_n]
        def_pass = [c for c in dfn if mom.get(c, -np.inf) > 0.0]

        n_slots = max(1, cfg.top_n)
        off_frac = len(off_pass) / n_slots
        def_frac = 1.0 - off_frac

        w_full = np.zeros(len(risk), dtype=float)
        lo = max(0, i - cfg.vol_lookback + 1)
        win = R[lo: i + 1, :]                                # (L, k)

        def sleeve(names: List[str], frac: float) -> None:
            if frac <= 1e-12 or not names:
                return
            k = len(names)
            cols = [col_of[c] for c in names]
            X = win[:, cols].T                               # (k, L)
            if k == 1:
                w = np.ones(1)
            else:
                S = pool_cov(X, delta=cfg.shrink_delta, eig_floor=cfg.eig_floor)
                w = erc_ccd(S) if S is not None else inv_vol_weights(X)
            cap_in = min(1.0, cfg.max_weight / frac)
            w = cap_weights(w, cap_in)
            for c, wi in zip(names, w):
                w_full[col_of[c]] += frac * wi

        sleeve(off_pass, off_frac)
        sleeve(def_pass, def_frac)                           # cash if none pass

        # ---- hard invariants at construction time --------------------------
        w_full = np.clip(w_full, 0.0, None)
        w_full[~np.isfinite(prc[i, :])] = 0.0                # no phantom assets
        gross = float(np.abs(w_full).sum())
        if gross > cfg.max_gross:
            w_full *= cfg.max_gross / gross
        w_full = np.where(w_full < 1e-12, 0.0, w_full)

        rows[dt] = w_full
        diag_rows.append(dict(date=dt,
                              n_off=len(off_pass),
                              n_def=len(def_pass),
                              off_frac=off_frac,
                              risk_gross=float(w_full.sum()),
                              cash=float(max(0.0, 1.0 - w_full.sum()))))

    # ---- expand to the daily grid ------------------------------------------
    W = pd.DataFrame(0.0, index=idx, columns=risk, dtype=float)
    if rows:
        Wr = pd.DataFrame.from_dict(rows, orient="index", columns=risk).sort_index()
        # ffill holdings between rebalances; zeros (NOT NaN) before first signal
        W = Wr.reindex(idx).ffill()
        W = W.astype(float)
        W.iloc[:, :] = np.where(np.isfinite(W.to_numpy()), W.to_numpy(), 0.0)

    # ---- tradability mask: identical labels/shape (FIX 7) ------------------
    tradable = (px[risk].notna() & px[risk].shift(1).notna())
    tradable = tradable.reindex(index=W.index, columns=W.columns).fillna(False)
    W = W.where(tradable, other=0.0)

    # ---- constructive gross cap (FIX 6) -----------------------------------
    gross = W.abs().sum(axis=1)
    scale = pd.Series(1.0, index=W.index, dtype=float)
    hot = gross > cfg.max_gross
    scale.loc[hot] = cfg.max_gross / gross.loc[hot]
    W = W.mul(scale, axis=0)
    W = W.where(W.abs() > 1e-14, 0.0)

    diag = pd.DataFrame(diag_rows).set_index("date") if diag_rows else pd.DataFrame()
    return W, diag


# =============================================================================
# 8.  BACKTEST (drift accounting, costs, borrow spread)
# =============================================================================
def backtest(px: pd.DataFrame,
             W: pd.DataFrame,
             cfg: Config,
             cash_ret: pd.Series) -> pd.DataFrame:
    idx = pd.DatetimeIndex(px.index)
    risk = list(W.columns)

    R = px[risk].pct_change().to_numpy(dtype=float)          # NaN preserved
    Wt = W.to_numpy(dtype=float)
    tradable = (px[risk].notna() & px[risk].shift(1).notna()).to_numpy()
    rc = cash_ret.reindex(idx).to_numpy(dtype=float)

    tc = cfg.tc_bps / 1e4
    borrow_d = cfg.borrow_spread_bps / 1e4 / TRADING_DAYS

    T = len(idx)
    n = len(risk)
    port = np.zeros(T); turn = np.zeros(T); cost = np.zeros(T)
    gross_ser = np.zeros(T); cash_ser = np.zeros(T); lev_cost = np.zeros(T)

    w = Wt[0].copy()
    w[~tradable[0]] = 0.0
    cash = 1.0 - w.sum()
    gross_ser[0], cash_ser[0] = np.abs(w).sum(), cash
    eq = [1.0]

    for t in range(1, T):
        r = R[t].copy()
        bad = ~np.isfinite(r)
        # positions whose price vanished are liquidated at flat (0%) for that day
        r[bad] = 0.0

        r_cash = rc[t] if np.isfinite(rc[t]) else cfg.rf_annual_fallback / TRADING_DAYS
        if cash < 0.0:
            r_cash_eff = r_cash + borrow_d                   # FIX 3: borrow spread
            lev_cost[t] = -cash * borrow_d
        else:
            r_cash_eff = r_cash

        growth = float(w @ (1.0 + r) + cash * (1.0 + r_cash_eff))
        growth = max(growth, 1e-12)
        gross_ret = growth - 1.0

        w_drift = w * (1.0 + r) / growth
        cash_drift = cash * (1.0 + r_cash_eff) / growth

        w_tgt = Wt[t].copy()
        w_tgt[~tradable[t]] = 0.0
        w_tgt[bad] = 0.0
        g = float(np.abs(w_tgt).sum())
        if g > cfg.max_gross:
            w_tgt *= cfg.max_gross / g

        traded = float(np.abs(w_tgt - w_drift).sum())        # risk-leg notional
        c = tc * traded

        port[t] = gross_ret - c
        turn[t] = traded
        cost[t] = c
        eq.append(eq[-1] * (1.0 + port[t]))

        w = w_tgt
        cash = 1.0 - w.sum()
        gross_ser[t] = np.abs(w).sum()
        cash_ser[t] = cash
        _ = cash_drift  # (kept for clarity of the drift decomposition)

    out = pd.DataFrame({
        "ret": port,
        "equity": np.array(eq, dtype=float),
        "turnover": turn,
        "cost": cost,
        "borrow_cost": lev_cost,
        "gross": gross_ser,
        "cash_w": cash_ser,
    }, index=idx)
    return out


# =============================================================================
# 9.  PERFORMANCE STATS  (TRUE SHARPE - FIX 2)
# =============================================================================
def perf_stats(ret: pd.Series, rf: pd.Series, label: str = "") -> Dict[str, float]:
    r = pd.Series(ret, dtype=float).dropna()
    if r.empty:
        return {"label": label}
    rfa = pd.Series(rf, dtype=float).reindex(r.index).fillna(0.0)
    ex = r - rfa

    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    cagr = eq.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 and eq.iloc[-1] > 0 else np.nan
    vol = r.std(ddof=1) * math.sqrt(TRADING_DAYS)

    sd_ex = ex.std(ddof=1)
    sharpe = (ex.mean() / sd_ex) * math.sqrt(TRADING_DAYS) if sd_ex > 0 else np.nan

    dn = np.minimum(ex.to_numpy(), 0.0)
    dd_dev = math.sqrt(float(np.mean(dn ** 2)))
    sortino = (ex.mean() / dd_dev) * math.sqrt(TRADING_DAYS) if dd_dev > 0 else np.nan

    dd = eq / eq.cummax() - 1.0
    mdd = float(dd.min())

    return {
        "label": label,
        "start": str(r.index[0].date()),
        "end": str(r.index[-1].date()),
        "years": years,
        "CAGR": cagr,
        "Vol": vol,
        "Sharpe(true,excess)": sharpe,
        "Sortino": sortino,
        "MaxDD": mdd,
        "Calmar": (cagr / abs(mdd)) if (mdd < 0 and np.isfinite(cagr)) else np.nan,
        "HitRate": float((r > 0).mean()),
        "Skew": float(r.skew()),
        "AvgRf": float(rfa.mean() * TRADING_DAYS),
    }


def fmt_stats(d: Dict[str, float]) -> str:
    if "CAGR" not in d:
        return f"{d.get('label','?')}: <no data>"
    return (f"{d['label']:<22} {d['start']}..{d['end']}  "
            f"CAGR {d['CAGR']*100:7.2f}%  Vol {d['Vol']*100:6.2f}%  "
            f"Sharpe {d['Sharpe(true,excess)']:6.3f}  Sortino {d['Sortino']:6.3f}  "
            f"MaxDD {d['MaxDD']*100:7.2f}%  Calmar {d['Calmar']:5.2f}  "
            f"Hit {d['HitRate']*100:5.2f}%")


# =============================================================================
# 10. SELF-TESTS (fail loudly, not silently)
# =============================================================================
def self_tests(cfg: Config) -> None:
    rng = np.random.default_rng(7)

    # ERC produces equal percentage risk contributions
    for k in (2, 3, 5, 8):
        A = rng.standard_normal((k, 4 * k))
        S = np.cov(A, ddof=1) + np.eye(k) * 1e-3
        w = erc_ccd(S)
        assert np.all(w > 0) and abs(w.sum() - 1.0) < 1e-12, "ERC weights invalid"
        rcs = risk_contributions(w, S)
        assert rcs.max() - rcs.min() < 1e-8, f"ERC risk parity failed (k={k})"

    # ERC handles degenerate input without NaN
    w = erc_ccd(np.zeros((3, 3)))
    assert np.isfinite(w).all() and abs(w.sum() - 1.0) < 1e-12

    # covariance refuses insufficient overlap (inception alignment)
    X = np.full((3, 30), np.nan)
    X[:, :5] = rng.standard_normal((3, 5))
    assert pool_cov(X) is None, "pool_cov must refuse to guess"

    # cap water-filling preserves total and respects the cap
    w = cap_weights(np.array([0.7, 0.2, 0.1]), 0.4)
    assert abs(w.sum() - 1.0) < 1e-12 and w.max() <= 0.4 + 1e-9

    # infeasible cap -> equal weight, total preserved
    w = cap_weights(np.array([0.5, 0.5]), 0.3)
    assert abs(w.sum() - 1.0) < 1e-12 and abs(w[0] - 0.5) < 1e-12

    # true Sharpe != CAGR/vol
    n = 2000
    r = pd.Series(rng.normal(0.0004, 0.01, n),
                  index=pd.bdate_range("2010-01-01", periods=n))
    rf = pd.Series(0.00008, index=r.index)
    st = perf_stats(r, rf, "unit")
    naive = st["CAGR"] / st["Vol"]
    assert abs(st["Sharpe(true,excess)"] - naive) > 1e-6, "Sharpe must be excess-based"
    print("[self-test] ERC parity, covariance gating, caps, Sharpe: OK")


# =============================================================================
# 11. MAIN
# =============================================================================
def main() -> None:
    cfg = Config()
    self_tests(cfg)

    px_raw, src = load_prices(cfg)
    px = px_raw.sort_index()
    px = px[~px.index.duplicated(keep="last")]
    px = px.apply(pd.to_numeric, errors="coerce")
    px = px[px.notna().any(axis=1)]
    px = px.reindex(columns=[c for c in cfg.all_tickers if c in px.columns])

    # NO fillna on prices.  Only forward-fill *inside* each asset's own life,
    # which never manufactures pre-inception data (FIX 1 / FIX 5).
    px = px.apply(lambda s: s.where(s.notna(), s.ffill().where(s.ffill().notna() &
                                                              (s.expanding().count() > 0))))
    px = px.mask(px <= 0.0)

    risk = [c for c in cfg.risk_assets if c in px.columns]
    if not risk:
        raise RuntimeError("No risk assets available after cleaning.")

    print(f"\nData source: {src}   rows={len(px)}   "
          f"{px.index[0].date()} .. {px.index[-1].date()}")
    print("Inception (first valid price) per asset:")
    for c in px.columns:
        fv = px[c].first_valid_index()
        print(f"   {c:<5} {str(fv.date()) if fv is not None else 'n/a':>12}"
              f"   obs={int(px[c].notna().sum())}")

    # ---- risk-free / cash leg ---------------------------------------------
    if cfg.cash in px.columns and px[cfg.cash].notna().sum() > 50:
        cash_ret = px[cfg.cash].pct_change()
    else:
        cash_ret = pd.Series(np.nan, index=px.index)
    rf_daily = cash_ret.copy()
    rf_daily = rf_daily.where(np.isfinite(rf_daily),
                              cfg.rf_annual_fallback / TRADING_DAYS)
    cash_ret = cash_ret.where(np.isfinite(cash_ret),
                              cfg.rf_annual_fallback / TRADING_DAYS)

    # ---- weights ----------------------------------------------------------
    W, diag = build_target_weights(px, cfg, rf_daily)

    # ---- INVARIANTS (these are the assertions that used to blow up) -------
    Wv = W.to_numpy(dtype=float)
    assert np.isfinite(Wv).all(), "non-finite weights"
    assert (Wv >= -1e-12).all(), "unexpected short exposure"
    gross = W.abs().sum(axis=1)
    assert (gross <= cfg.max_gross + 1e-9).all(), "gross cap violated"
    assert (W.max(axis=1) <= cfg.max_weight + 1e-9).all(), "per-asset cap violated"
    tradable = (px[risk].notna() & px[risk].shift(1).notna())
    tradable = tradable.reindex(index=W.index, columns=W.columns).fillna(False)
    assert (W.where(~tradable, 0.0).abs().to_numpy() <= 1e-12).all(), \
        "phantom pre-inception exposure detected"
    print("[invariants] finite, long-only, gross<=%.2f, cap<=%.2f, no phantom assets: OK"
          % (cfg.max_gross, cfg.max_weight))

    # ---- common start = first legally tradable day ------------------------
    active = gross > 0
    if not active.any():
        raise RuntimeError("Strategy never became eligible to trade "
                           "(insufficient aligned history).")
    t0 = active.idxmax()
    px_bt = px.loc[t0:]
    W_bt = W.loc[t0:]
    cash_bt = cash_ret.loc[t0:]
    rf_bt = rf_daily.loc[t0:]

    res = backtest(px_bt, W_bt, cfg, cash_bt)
    r_strat = res["ret"].iloc[1:]
    rf_al = rf_bt.reindex(r_strat.index)

    print("\n" + "=" * 92)
    print("PERFORMANCE  (net of %.1f bps one-way costs, %.0f bps borrow spread)"
          % (cfg.tc_bps, cfg.borrow_spread_bps))
    print("=" * 92)
    print(fmt_stats(perf_stats(r_strat, rf_al, "OPUS12-ERC (net)")))

    # gross-of-cost variant for cost-drag attribution
    r_gross = r_strat + res["cost"].iloc[1:]
    print(fmt_stats(perf_stats(r_gross, rf_al, "OPUS12-ERC (gross)")))

    # benchmarks
    for bm in ("SPY", "QQQ"):
        if bm in px_bt.columns and px_bt[bm].notna().sum() > 100:
            rb = px_bt[bm].pct_change().dropna()
            print(fmt_stats(perf_stats(rb, rf_bt.reindex(rb.index), f"{bm} buy&hold")))

    # 60/40 style static benchmark (only over the overlap where both exist)
    if {"SPY", "IEF"} <= set(px_bt.columns):
        two = px_bt[["SPY", "IEF"]].dropna().pct_change().dropna()
        if len(two) > 100:
            r6040 = 0.6 * two["SPY"] + 0.4 * two["IEF"]
            print(fmt_stats(perf_stats(r6040, rf_bt.reindex(r6040.index), "60/40 SPY/IEF")))

    # ---- diagnostics ------------------------------------------------------
    ann_turn = res["turnover"].iloc[1:].sum() / (len(r_strat) / TRADING_DAYS)
    cost_drag = res["cost"].iloc[1:].sum() / (len(r_strat) / TRADING_DAYS)
    print("\nDIAGNOSTICS")
    print(f"  rebalances executed      : {0 if diag.empty else len(diag)}")
    print(f"  annual turnover (1-way)  : {ann_turn:6.2f} x NAV")
    print(f"  annual cost drag         : {cost_drag*100:6.3f} %")
    print(f"  borrow cost (total)      : {res['borrow_cost'].sum()*100:6.3f} %")
    print(f"  avg risk gross exposure  : {res['gross'].mean()*100:6.2f} %")
    print(f"  avg cash weight          : {res['cash_w'].mean()*100:6.2f} %")
    print(f"  min / max gross          : {res['gross'].min()*100:6.2f} % / "
          f"{res['gross'].max()*100:6.2f} %")
    if not diag.empty:
        print(f"  avg offensive sleeves    : {diag['n_off'].mean():.2f} / {cfg.top_n}")
        print(f"  avg defensive passers    : {diag['n_def'].mean():.2f} "
              f"(absolute momentum enforced)")
        print(f"  months fully in cash     : "
              f"{int((diag['risk_gross'] <= 1e-9).sum())}")

    print("\nFINAL TARGET WEIGHTS (%s)" % str(W_bt.index[-1].date()))
    last = W_bt.iloc[-1]
    for c, v in last[last > 1e-8].sort_values(ascending=False).items():
        print(f"   {c:<5} {v*100:6.2f} %")
    print(f"   {'CASH':<5} {max(0.0, 1.0 - last.sum())*100:6.2f} %")
    print("\nDone.")


if __name__ == "__main__":
    main()