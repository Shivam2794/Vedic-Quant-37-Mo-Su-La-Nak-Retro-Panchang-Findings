"""
opus10_compare_naive.py  --  BRUTAL MULTIPOINT QUALITY INSPECTOR / ABSOLUTE SURRENDER BUILD
=============================================================================================
"Leverage for the Long Run" style regime strategy, audited and rebuilt.

Fatal bugs from prior versions -- ALL FIXED:
  1. .fillna(0) creating phantom assets prior to inception   -> NaN is preserved; assets are
                                                                only investable after a verified
                                                                inception + warm-up window.
  2. Wrong Sharpe (CAGR / vol)                               -> true Sharpe = mean(excess)/std(excess)*sqrt(252)
  3. No transaction costs / borrowing spread                 -> per-unit-turnover cost, spread,
                                                                cash yield, and financing charge on
                                                                any gross leverage > 1.
  4. No Absolute Momentum on defensive assets                -> defensive sleeve requires 12m
                                                                excess-of-cash absolute momentum,
                                                                else it goes to T-bills.
  5. Inception alignment ignored                             -> backtest starts at the first date
                                                                where the signal AND at least one
                                                                tradable asset genuinely exist;
                                                                weights renormalized on live assets.

Also fixed: the `ValueError: cannot insert Ticker, already exists` crash (index/column name
collision on reset_index) via a defensive frame-flattening loader that supports long, wide and
MultiIndex-column parquet layouts.

Signal timing is strictly t-1 -> t (no look-ahead). Holdings drift between rebalances so that
turnover (and therefore cost) is measured honestly.
"""

from __future__ import annotations

import os
import sys
import math
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------------------------
TRADING_DAYS = 252
CALENDAR_DAYS = 365.25

CFG = {
    "price_file": "frozen_universe_data.parquet",
    "risk_on_assets": ["TQQQ", "UPRO"],
    "risk_off_assets": ["GLD", "TLT"],
    "benchmark": "SPY",
    "regime_asset": "SPY",
    "sma_window": 200,
    "abs_mom_lookback": 252,      # 12 months absolute (excess-of-cash) momentum
    "min_history_days": 25,       # warm-up after inception before an asset is investable
    "cov_window": 126,            # trailing window for the ERC covariance
    "cov_ridge": 1e-10,
    "rebalance": "M",             # month-end scheduled rebalance (+ event driven)
    "drift_band": 0.02,           # absolute weight drift that forces an off-schedule rebalance
    "cost_per_turnover": 0.0005,  # 5 bps of notional traded, one way
    "borrow_spread": 0.0100,      # 100 bps over cash for any gross leverage above 1.0x
    "cash_yield_haircut": 0.0025, # cash earns rf - 25 bps
    "default_rf_annual": 0.02,    # used only if no cash proxy exists in the data
    "rf_candidates": ["^IRX", "IRX", "DTB3", "BIL", "SHV", "USFR", "CASHX"],
}

DEFAULT_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data"


# ----------------------------------------------------------------------------------------------
# ROBUST DATA LOADING  (fixes: "cannot insert Ticker, already exists")
# ----------------------------------------------------------------------------------------------
def _norm(name) -> str:
    return str(name).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def _find_col(columns, candidates):
    lookup = {_norm(c): c for c in columns}
    for cand in candidates:
        if cand in lookup:
            return lookup[cand]
    return None


def _safe_flatten(df: pd.DataFrame) -> pd.DataFrame:
    """
    reset_index() that can never raise "cannot insert X, already exists".
    Any index level whose name collides with an existing column is dropped from the
    columns first (the index level is authoritative). Unnamed levels get safe names.
    """
    df = df.copy()
    idx_names = list(df.index.names)
    if all(n is None for n in idx_names) and not isinstance(df.index, pd.MultiIndex):
        # plain RangeIndex-like: nothing meaningful to promote
        if df.index.name is None and isinstance(df.index, pd.RangeIndex):
            return df.reset_index(drop=True)

    # give unnamed levels deterministic names
    new_names = []
    for i, n in enumerate(idx_names):
        new_names.append(n if n is not None else (f"__level_{i}__"))
    df.index = df.index.set_names(new_names)

    # drop colliding columns so reset_index is always safe
    collisions = [n for n in new_names if n in df.columns]
    if collisions:
        df = df.drop(columns=collisions)

    out = df.reset_index()
    # de-duplicate any remaining duplicate column labels (keep first)
    out = out.loc[:, ~pd.Index(out.columns).duplicated(keep="first")]
    return out


def load_price_panel(data_dir: str, price_file: str) -> pd.DataFrame:
    """
    Returns a wide DataFrame of adjusted prices: index = DatetimeIndex, columns = tickers.
    NaN before inception / after delisting is PRESERVED (never filled with zeros).
    """
    path = os.path.join(data_dir, price_file)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Price file not found: {path}")

    raw = pd.read_parquet(path)
    if raw.empty:
        raise ValueError("Loaded price file is empty.")

    price_fields = ["adjclose", "adjustedclose", "adjclose$", "adj", "close", "price", "nav",
                    "closeadj", "adjustedclose"]

    # ---- Case A: MultiIndex columns e.g. (Field, Ticker) or (Ticker, Field) --------------------
    if isinstance(raw.columns, pd.MultiIndex):
        wide = None
        for lvl in range(raw.columns.nlevels):
            vals = list(pd.unique(raw.columns.get_level_values(lvl)))
            normed = {_norm(v): v for v in vals}
            for pf in price_fields:
                if pf in normed:
                    wide = raw.xs(normed[pf], axis=1, level=lvl, drop_level=True)
                    break
            if wide is not None:
                break
        if wide is None:
            raw.columns = ["__".join(str(x) for x in tup) for tup in raw.columns]
        else:
            if isinstance(wide.columns, pd.MultiIndex):
                wide.columns = wide.columns.get_level_values(-1)
            wide.index = pd.to_datetime(wide.index)
            return _finalize_panel(wide)

    flat = _safe_flatten(raw)

    date_col = _find_col(flat.columns, ["date", "datetime", "timestamp", "dt", "tradedate",
                                        "__level_0__", "index"])
    ticker_col = _find_col(flat.columns, ["ticker", "symbol", "asset", "sid", "security",
                                          "__level_1__"])
    price_col = _find_col(flat.columns, price_fields)

    # ---- Case B: long / tidy format ------------------------------------------------------------
    if date_col is not None and ticker_col is not None and price_col is not None:
        sub = flat[[date_col, ticker_col, price_col]].copy()
        sub.columns = ["Date", "Ticker", "Price"]
        sub["Date"] = pd.to_datetime(sub["Date"])
        sub["Ticker"] = sub["Ticker"].astype(str).str.strip().str.upper()
        sub["Price"] = pd.to_numeric(sub["Price"], errors="coerce")
        wide = sub.pivot_table(index="Date", columns="Ticker", values="Price", aggfunc="last")
        return _finalize_panel(wide)

    # ---- Case C: already wide (one column per ticker) -------------------------------------------
    if date_col is not None:
        flat[date_col] = pd.to_datetime(flat[date_col])
        wide = flat.set_index(date_col)
    else:
        wide = raw.copy()
        wide.index = pd.to_datetime(wide.index)

    wide = wide.select_dtypes(include=[np.number])
    if wide.shape[1] == 0:
        raise ValueError("No numeric price columns could be identified in the price file.")
    return _finalize_panel(wide)


def _finalize_panel(wide: pd.DataFrame) -> pd.DataFrame:
    wide = wide.copy()
    wide.index = pd.to_datetime(wide.index)
    wide = wide[~wide.index.duplicated(keep="last")].sort_index()
    wide.columns = [str(c).strip().upper() for c in wide.columns]
    wide = wide.loc[:, ~pd.Index(wide.columns).duplicated(keep="first")]
    wide = wide.apply(pd.to_numeric, errors="coerce")
    wide = wide.mask(wide <= 0.0)                       # non-positive prices are invalid, not zero-assets
    wide = wide.dropna(axis=1, how="all")
    wide = wide.dropna(axis=0, how="all")
    if wide.empty:
        raise ValueError("Price panel is empty after cleaning.")
    return wide


# ----------------------------------------------------------------------------------------------
# RISK-FREE / CASH SERIES
# ----------------------------------------------------------------------------------------------
def build_risk_free(prices: pd.DataFrame, cfg: dict) -> tuple[pd.Series, str]:
    """
    Daily risk-free (cash) simple return series aligned to `prices.index`.
    Priority: explicit T-bill yield series (^IRX style, in percent) -> bill ETF total return
              -> flat default. Never NaN.
    """
    idx = prices.index
    for cand in cfg["rf_candidates"]:
        key = cand.strip().upper()
        if key not in prices.columns:
            continue
        s = prices[key].dropna()
        if s.empty:
            continue
        if key in ("^IRX", "IRX", "DTB3"):
            # quoted as an annualized percentage yield
            ann = (s.clip(lower=0.0) / 100.0).reindex(idx).ffill()
            ann = ann.fillna(cfg["default_rf_annual"])
            daily = (1.0 + ann) ** (1.0 / TRADING_DAYS) - 1.0
            return daily.astype(float), f"{key} (bill yield)"
        else:
            r = s.pct_change()
            daily = r.reindex(idx).astype(float)
            daily = daily.clip(lower=-0.01, upper=0.01)  # sanity clamp on a cash proxy
            fill = (1.0 + cfg["default_rf_annual"]) ** (1.0 / TRADING_DAYS) - 1.0
            daily = daily.fillna(fill)
            return daily, f"{key} (bill ETF total return)"

    flat = (1.0 + cfg["default_rf_annual"]) ** (1.0 / TRADING_DAYS) - 1.0
    return pd.Series(flat, index=idx, dtype=float), f"flat {cfg['default_rf_annual']*100:.2f}% p.a."


# ----------------------------------------------------------------------------------------------
# SIGNALS
# ----------------------------------------------------------------------------------------------
def build_signals(prices: pd.DataFrame, rf_daily: pd.Series, cfg: dict) -> dict:
    idx = prices.index

    # --- Availability (INCEPTION ALIGNMENT) ----------------------------------------------------
    valid = prices.notna()
    obs_count = valid.cumsum()
    available = valid & (obs_count >= cfg["min_history_days"])

    # --- Regime: price > SMA200 on the regime asset, computed on its own valid history ---------
    reg_key = cfg["regime_asset"].upper()
    if reg_key not in prices.columns:
        raise KeyError(f"Regime asset {reg_key} missing from price panel.")
    reg = prices[reg_key].dropna()
    sma = reg.rolling(cfg["sma_window"], min_periods=cfg["sma_window"]).mean()
    regime_on = pd.Series(np.nan, index=idx, dtype=float)
    raw_on = (reg > sma).astype(float)
    raw_on[sma.isna()] = np.nan
    regime_on.loc[reg.index] = raw_on
    regime_on = regime_on.reindex(idx)  # NaN => signal unknown => stay in cash

    # --- Absolute momentum, measured EXCESS OF CASH over the lookback --------------------------
    lb = cfg["abs_mom_lookback"]
    log_rf = np.log1p(rf_daily.astype(float))
    rf_cum = np.expm1(log_rf.rolling(lb, min_periods=lb).sum())  # cash total return over lookback

    asset_cum = prices / prices.shift(lb) - 1.0
    # invalidate windows that are not fully post-inception
    full_window = valid.rolling(lb, min_periods=lb).sum() >= lb
    asset_cum = asset_cum.where(full_window & valid)

    abs_mom = pd.DataFrame(False, index=idx, columns=prices.columns)
    for c in prices.columns:
        cmp_ = asset_cum[c] - rf_cum
        abs_mom[c] = (cmp_ > 0.0).fillna(False)

    return {"available": available, "regime_on": regime_on, "abs_mom": abs_mom}


def target_weights(t: pd.Timestamp,
                   sig: dict,
                   returns: pd.DataFrame,
                   cfg: dict,
                   scheme: str,
                   cols: list[str]) -> np.ndarray:
    """
    Target portfolio weights (fraction of NAV) decided using information up to and including t.
    Residual (1 - sum) is held in T-bills. Never allocates to a pre-inception asset.
    """
    n = len(cols)
    w = np.zeros(n, dtype=float)

    reg = sig["regime_on"].get(t, np.nan)
    if not np.isfinite(reg):
        return w  # unknown regime -> 100% cash

    avail_row = sig["available"].loc[t]

    if reg >= 0.5:
        sleeve = [a for a in cfg["risk_on_assets"] if a in cols and bool(avail_row.get(a, False))]
    else:
        mom_row = sig["abs_mom"].loc[t]
        sleeve = [a for a in cfg["risk_off_assets"]
                  if a in cols and bool(avail_row.get(a, False)) and bool(mom_row.get(a, False))]

    if not sleeve:
        return w  # nothing eligible -> 100% cash (T-bills)

    if scheme == "equal" or len(sleeve) == 1:
        raw = np.ones(len(sleeve)) / len(sleeve)
    elif scheme == "erc":
        win = returns.loc[:t, sleeve].tail(cfg["cov_window"])
        if len(win) < max(20, cfg["cov_window"] // 2) or win.isna().any().any():
            raw = np.ones(len(sleeve)) / len(sleeve)
        else:
            cov = np.cov(win.values, rowvar=False, ddof=1)
            cov = np.atleast_2d(cov)
            cov = cov + np.eye(cov.shape[0]) * cfg["cov_ridge"]
            raw = erc_weights(cov)
    else:
        raise ValueError(f"Unknown weighting scheme: {scheme}")

    for a, ww in zip(sleeve, raw):
        w[cols.index(a)] = float(ww)
    return w


def erc_weights(cov: np.ndarray, tol: float = 1e-12, max_iter: int = 20000) -> np.ndarray:
    """Equal Risk Contribution weights via damped fixed-point iteration. Long-only, sums to 1."""
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if n == 1:
        return np.ones(1)
    d = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    if not np.all(np.isfinite(d)) or np.any(d <= 0):
        return np.ones(n) / n
    w = (1.0 / d)
    w = w / w.sum()
    for _ in range(max_iter):
        mrc = cov @ w
        if not np.all(np.isfinite(mrc)) or np.any(mrc <= 0):
            return (1.0 / d) / (1.0 / d).sum()
        nxt = 1.0 / mrc
        nxt = nxt / nxt.sum()
        nxt = 0.5 * w + 0.5 * nxt
        nxt = nxt / nxt.sum()
        if np.max(np.abs(nxt - w)) < tol:
            w = nxt
            break
        w = nxt
    if not np.all(np.isfinite(w)) or w.sum() <= 0:
        return np.ones(n) / n
    w = np.clip(w, 0.0, None)
    return w / w.sum()


# ----------------------------------------------------------------------------------------------
# BACKTEST ENGINE  (costs, financing, cash yield, honest drift/turnover)
# ----------------------------------------------------------------------------------------------
def run_backtest(prices: pd.DataFrame,
                 returns: pd.DataFrame,
                 rf_daily: pd.Series,
                 sig: dict,
                 cfg: dict,
                 scheme: str) -> dict:
    cols = list(prices.columns)
    n = len(cols)
    idx = prices.index

    # First decision date: regime known AND some eligible asset exists.
    start_i = None
    for i, t in enumerate(idx):
        if i >= len(idx) - 1:
            break
        w0 = target_weights(t, sig, returns, cfg, scheme, cols)
        if w0.sum() > 0:
            start_i = i
            break
    if start_i is None:
        raise RuntimeError("No date with a valid signal and an investable asset was found.")

    cash_fill = (1.0 + cfg["default_rf_annual"]) ** (1.0 / TRADING_DAYS) - 1.0
    rf = rf_daily.reindex(idx).fillna(cash_fill).astype(float)
    cash_ret = (rf - (1.0 + cfg["cash_yield_haircut"]) ** (1.0 / TRADING_DAYS) + 1.0)
    cash_ret = rf - ((1.0 + cfg["cash_yield_haircut"]) ** (1.0 / TRADING_DAYS) - 1.0)

    ret_vals = returns.values
    holdings = np.zeros(n, dtype=float)
    prev_target_set = None
    pending_cost = 0.0

    dates_out, rets_out, turn_out, cost_out, gross_out = [], [], [], [], []

    last_month = None
    for i in range(start_i, len(idx) - 1):
        t = idx[i]
        t1 = idx[i + 1]

        tgt = target_weights(t, sig, returns, cfg, scheme, cols)
        tgt_set = tuple(np.nonzero(tgt > 0)[0])

        month_key = (t.year, t.month)
        scheduled = (last_month is None) or (month_key != last_month)
        composition_change = (prev_target_set is None) or (tgt_set != prev_target_set)
        drifted = np.max(np.abs(tgt - holdings)) > cfg["drift_band"] if prev_target_set is not None else True

        if scheduled or composition_change or drifted:
            turnover = float(np.abs(tgt - holdings).sum())
            pending_cost += turnover * cfg["cost_per_turnover"]
            holdings = tgt.copy()
            prev_target_set = tgt_set
            last_month = month_key
        else:
            turnover = 0.0

        # ---- realize next-day return -----------------------------------------------------------
        r_next = ret_vals[i + 1, :]
        valid_next = np.isfinite(r_next)

        h_valid = np.where(valid_next, holdings, 0.0)
        # any holding whose return is unavailable (delist/gap) is treated as parked in cash
        stranded = float(holdings[~valid_next].sum())
        invested = float(h_valid.sum())
        cash_w = 1.0 - invested  # includes stranded weight and deliberate cash

        asset_pnl = float(np.dot(h_valid, np.where(valid_next, r_next, 0.0)))

        gross = float(np.abs(holdings).sum())
        borrow = 0.0
        if gross > 1.0:
            fin_rate = rf.iloc[i + 1] + ((1.0 + cfg["borrow_spread"]) ** (1.0 / TRADING_DAYS) - 1.0)
            borrow = (gross - 1.0) * fin_rate

        cash_pnl = cash_w * float(cash_ret.iloc[i + 1]) if cash_w > 0 else cash_w * float(rf.iloc[i + 1])

        cost = pending_cost
        pending_cost = 0.0

        port_ret = asset_pnl + cash_pnl - borrow - cost

        dates_out.append(t1)
        rets_out.append(port_ret)
        turn_out.append(turnover)
        cost_out.append(cost + borrow)
        gross_out.append(gross)

        # ---- drift holdings to next period's start weights -------------------------------------
        nav_growth = 1.0 + port_ret
        if nav_growth <= 1e-12:
            holdings = np.zeros(n, dtype=float)
            prev_target_set = None
        else:
            grown = h_valid * (1.0 + np.where(valid_next, r_next, 0.0))
            holdings = grown / nav_growth
            _ = stranded  # stranded weight has been reclassified to cash, no longer held

    out = pd.DataFrame(
        {"ret": rets_out, "turnover": turn_out, "cost": cost_out, "gross": gross_out},
        index=pd.DatetimeIndex(dates_out, name="Date"),
    )
    return {"series": out, "rf": rf.reindex(out.index).astype(float), "scheme": scheme}


# ----------------------------------------------------------------------------------------------
# PERFORMANCE STATISTICS  (TRUE Sharpe)
# ----------------------------------------------------------------------------------------------
def performance_stats(returns: pd.Series, rf: pd.Series) -> dict:
    r = pd.Series(returns, dtype=float).dropna()
    if r.empty:
        raise ValueError("Empty return series.")
    rf = pd.Series(rf, dtype=float).reindex(r.index).fillna(0.0)

    equity = (1.0 + r).cumprod()
    total_growth = float(equity.iloc[-1])

    days = max((r.index[-1] - r.index[0]).days + 1, 1)
    years = days / CALENDAR_DAYS
    cagr = total_growth ** (1.0 / years) - 1.0 if total_growth > 0 and years > 0 else float("nan")

    vol = float(r.std(ddof=1)) * math.sqrt(TRADING_DAYS)

    excess = r - rf
    ex_sd = float(excess.std(ddof=1))
    sharpe = (float(excess.mean()) / ex_sd) * math.sqrt(TRADING_DAYS) if ex_sd > 0 else float("nan")

    downside = excess.clip(upper=0.0)
    dd_sd = math.sqrt(float((downside ** 2).mean()))
    sortino = (float(excess.mean()) / dd_sd) * math.sqrt(TRADING_DAYS) if dd_sd > 0 else float("nan")

    peak = equity.cummax()
    dd = equity / peak - 1.0
    max_dd = float(dd.min())
    calmar = (cagr / abs(max_dd)) if (max_dd < 0 and np.isfinite(cagr)) else float("nan")

    ann_rf = float((1.0 + rf).prod()) ** (1.0 / years) - 1.0 if years > 0 else float("nan")

    return {
        "start": r.index[0], "end": r.index[-1], "n_days": int(len(r)), "years": years,
        "total_growth": total_growth, "cagr": cagr, "vol": vol,
        "sharpe": sharpe, "sortino": sortino, "max_dd": max_dd, "calmar": calmar,
        "ann_rf": ann_rf, "hit_rate": float((r > 0).mean()),
        "best_day": float(r.max()), "worst_day": float(r.min()),
    }


def buy_and_hold(prices: pd.DataFrame, ticker: str, index: pd.DatetimeIndex) -> pd.Series | None:
    t = ticker.upper()
    if t not in prices.columns:
        return None
    s = prices[t].reindex(index.union(prices.index)).sort_index()
    r = s.pct_change().reindex(index)
    return r.dropna()


def print_report(title: str, st: dict, extra: dict | None = None) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    print(f"  Period            : {st['start'].date()} -> {st['end'].date()} "
          f"({st['years']:.2f}y, {st['n_days']} trading days)")
    print(f"  Total Growth      : {st['total_growth']:.2f}x")
    print(f"  CAGR              : {st['cagr']*100:.2f}%")
    print(f"  Ann. Volatility   : {st['vol']*100:.2f}%")
    print(f"  Sharpe (true, ex-rf): {st['sharpe']:.3f}   [mean(excess)/sd(excess)*sqrt(252)]")
    print(f"  Sortino           : {st['sortino']:.3f}")
    print(f"  Max Drawdown      : {st['max_dd']*100:.2f}%")
    print(f"  Calmar            : {st['calmar']:.3f}")
    print(f"  Avg Risk-Free     : {st['ann_rf']*100:.2f}% p.a.")
    print(f"  Hit Rate          : {st['hit_rate']*100:.2f}%  "
          f"(best {st['best_day']*100:.2f}% / worst {st['worst_day']*100:.2f}%)")
    if extra:
        for k, v in extra.items():
            print(f"  {k:<18}: {v}")


# ----------------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------------
def run_discord_alpha(data_dir: str, cfg: dict = CFG) -> dict:
    prices = load_price_panel(data_dir, cfg["price_file"])

    # simple (arithmetic) returns; NaN wherever a price is missing on either side -> no phantoms
    returns = prices.pct_change()
    returns = returns.where(prices.notna() & prices.shift(1).notna())

    rf_daily, rf_src = build_risk_free(prices, cfg)

    present_on = [a for a in cfg["risk_on_assets"] if a in prices.columns]
    present_off = [a for a in cfg["risk_off_assets"] if a in prices.columns]
    missing = [a for a in cfg["risk_on_assets"] + cfg["risk_off_assets"] if a not in prices.columns]
    if not present_on and not present_off:
        raise KeyError("None of the strategy assets exist in the price panel.")
    cfg = dict(cfg)
    cfg["risk_on_assets"] = present_on
    cfg["risk_off_assets"] = present_off

    sig = build_signals(prices, rf_daily, cfg)

    print("=" * 78)
    print("DISCORD ALPHA :: LEVERAGE FOR THE LONG RUN  --  AUDITED ENGINE")
    print("=" * 78)
    print(f"  Data dir         : {data_dir}")
    print(f"  Universe loaded  : {len(prices.columns)} tickers, "
          f"{prices.index[0].date()} -> {prices.index[-1].date()}")
    print(f"  Risk-on sleeve   : {present_on}")
    print(f"  Risk-off sleeve  : {present_off} (12m absolute momentum vs cash required)")
    print(f"  Regime filter    : {cfg['regime_asset']} vs SMA{cfg['sma_window']} (t-1 signal)")
    print(f"  Risk-free source : {rf_src}")
    print(f"  Costs            : {cfg['cost_per_turnover']*1e4:.1f} bps / unit turnover, "
          f"{cfg['borrow_spread']*1e4:.0f} bps borrow spread, "
          f"{cfg['cash_yield_haircut']*1e4:.0f} bps cash haircut")
    if missing:
        print(f"  [WARN] Missing tickers skipped: {missing}")

    results = {}
    for scheme, label in (("equal", "NAIVE EQUAL WEIGHTED"), ("erc", "DYNAMIC ERC / RISK PARITY")):
        bt = run_backtest(prices, returns, rf_daily, sig, cfg, scheme)
        ser = bt["series"]
        st = performance_stats(ser["ret"], bt["rf"])
        ann_turn = float(ser["turnover"].sum()) / st["years"]
        ann_cost = float(ser["cost"].sum()) / st["years"]
        extra = {
            "Ann. Turnover": f"{ann_turn*100:.1f}% of NAV",
            "Ann. Cost Drag": f"{ann_cost*100:.2f}% (arith. sum of fees+financing)",
            "Avg Gross Expo": f"{float(ser['gross'].mean())*100:.1f}%",
            "Days in Cash": f"{float((ser['gross'] <= 1e-9).mean())*100:.1f}%",
        }
        print_report(f"STRATEGY -- {label}", st, extra)
        results[scheme] = {"stats": st, "series": ser}

    # aligned benchmark
    common_idx = results["equal"]["series"].index
    bh = buy_and_hold(prices, cfg["benchmark"], common_idx)
    if bh is not None and len(bh) > 20:
        st_b = performance_stats(bh, rf_daily.reindex(bh.index))
        print_report(f"BENCHMARK -- {cfg['benchmark']} BUY & HOLD (aligned)", st_b)
        results["benchmark"] = {"stats": st_b, "series": bh}

    print("\n" + "-" * 78)
    print("SUMMARY (net of costs, true excess-return Sharpe)")
    print("-" * 78)
    print(f"{'Strategy':<28}{'CAGR':>10}{'Vol':>10}{'Sharpe':>10}{'MaxDD':>10}{'Growth':>12}")
    rows = [("Naive Equal Weight", results["equal"]["stats"]),
            ("Dynamic ERC", results["erc"]["stats"])]
    if "benchmark" in results:
        rows.append((f"{cfg['benchmark']} Buy & Hold", results["benchmark"]["stats"]))
    for name, s in rows:
        print(f"{name:<28}{s['cagr']*100:>9.2f}%{s['vol']*100:>9.2f}%"
              f"{s['sharpe']:>10.3f}{s['max_dd']*100:>9.2f}%{s['total_growth']:>11.2f}x")
    print("-" * 78)
    return results


def main(argv: list[str]) -> int:
    data_dir = argv[1] if len(argv) > 1 else os.environ.get("OPUS_DATA_DIR", DEFAULT_DATA_DIR)
    try:
        run_discord_alpha(data_dir, CFG)
    except FileNotFoundError as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, RuntimeError) as e:
        print(f"[FATAL] {type(e).__name__}: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))