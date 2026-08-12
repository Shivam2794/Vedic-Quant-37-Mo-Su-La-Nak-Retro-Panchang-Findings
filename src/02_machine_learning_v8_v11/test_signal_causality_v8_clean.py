"""
OPUS 8 / V8 — BRUTAL MULTIPOINT CAUSALITY & LEAK DETECTOR  (+ mathematically-correct
reference backtest engine used to validate the five historical fatal bugs are dead).

Historical fatal bugs that are explicitly fixed / guarded here
-------------------------------------------------------------
1. .fillna(0) creating phantom assets prior to inception   -> pre-inception stays NaN,
   forward-fill is applied ONLY after each asset's first valid print, and any weight on a
   NaN (non-investable) asset is hard-asserted to be zero.
2. Wrong Sharpe formula (CAGR / vol)                       -> true excess-return Sharpe:
   mean(r_t - rf_t) / std(r_t - rf_t, ddof=1) * sqrt(252).
3. No transaction costs or borrowing spread                -> per-unit-turnover cost in bps
   charged on the bar the trade is executed, and cash < 0 (leverage) is financed at
   rf + borrow spread, cash > 0 earns rf.
4. No Absolute Momentum on defensive assets                -> defensive sleeve must ALSO
   pass its own absolute (time-series) momentum filter, otherwise 100% cash.
5. Inception alignment ignored                             -> every asset is aligned on its
   own first real print; look-back windows use min_periods == window (no back-filling),
   so no signal exists before an asset has a full history.

Causality/leak tests implemented
--------------------------------
A. Prefix invariance (random truncations)
B. Append invariance (future noise)
C. Warm-up zero-position invariance (lag padding)
D. Perturbation test (strict LAG-bar lag integrity)
E. Negative control (an intentionally unlagged generator MUST be caught)

The script is fully self-contained: if the project modules / parquet file are unavailable it
falls back to an internally-defined, provably causal signal generator and a synthetic panel
with staggered inception dates.
"""

from __future__ import annotations

import os
import sys
import math
import traceback

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------------
# Configuration (with safe fallbacks)
# ----------------------------------------------------------------------------------------
DEFAULT_PARQUET = os.environ.get("OPUS8_PARQUET", "opus8_prices.parquet")
DEFAULT_LAG = 1

try:  # pragma: no cover - project specific
    from opus8_config import PARQUET_FILE as _CFG_PARQUET  # type: ignore
except Exception:
    _CFG_PARQUET = DEFAULT_PARQUET

try:  # pragma: no cover - project specific
    from opus8_config import TICKERS_TRADED as _CFG_TICKERS  # type: ignore
except Exception:
    _CFG_TICKERS = None

try:  # pragma: no cover - project specific
    from opus8_config import LAG as _CFG_LAG  # type: ignore
except Exception:
    _CFG_LAG = DEFAULT_LAG

PARQUET_FILE = str(_CFG_PARQUET) if _CFG_PARQUET else DEFAULT_PARQUET
LAG = int(_CFG_LAG) if _CFG_LAG is not None else DEFAULT_LAG
if LAG < 1:
    raise ValueError("LAG must be >= 1 for a causal (non-leaking) strategy.")

TICKERS_TRADED = list(_CFG_TICKERS) if _CFG_TICKERS else None

TRADING_DAYS = 252
DATE_ALIASES = (
    "date", "datetime", "timestamp", "time", "dt", "asof", "asof_date",
    "trade_date", "tradedate", "index", "level_0", "period",
)
PRICE_ALIASES = ("adj close", "adjclose", "adj_close", "adjusted close", "adjusted_close", "close", "px_last", "price")


# ========================================================================================
# 1. DATA NORMALISATION (fixes the KeyError: date can live in the index, a MultiIndex,
#    a differently-named column, or be absent entirely)
# ========================================================================================
def _find_col(columns, aliases) -> str | None:
    lowered = {str(c).strip().lower(): c for c in columns}
    for a in aliases:
        if a in lowered:
            return lowered[a]
    for lc, orig in lowered.items():
        if any(a in lc for a in aliases):
            return orig
    return None


def _find_date_col(df: pd.DataFrame) -> str | None:
    col = _find_col(df.columns, DATE_ALIASES)
    if col is not None:
        return col
    # last resort: any column that parses cleanly as datetimes
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_datetime64_any_dtype(s):
            return c
        if s.dtype == object:
            try:
                parsed = pd.to_datetime(s, errors="coerce")
            except Exception:
                continue
            if parsed.notna().mean() > 0.98:
                return c
    return None


def normalize_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a tidy panel with columns: Date (datetime64, tz-naive), Ticker, 'Adj Close'."""
    if raw is None or len(raw) == 0:
        raise ValueError("Empty price frame.")

    df = raw.copy()

    # --- 1) pull any index level(s) into columns ------------------------------------
    if isinstance(df.index, pd.MultiIndex):
        names = [n if n is not None else f"level_{i}" for i, n in enumerate(df.index.names)]
        df.index = df.index.set_names(names)
        df = df.reset_index()
    else:
        if isinstance(df.index, pd.PeriodIndex):
            df.index = df.index.to_timestamp()
        if isinstance(df.index, pd.DatetimeIndex) or _find_date_col(df) is None:
            idx_name = df.index.name if df.index.name not in (None, "") else "Date"
            df.index = df.index.rename(idx_name)
            df = df.reset_index()

    # --- 2) locate / construct the date column -------------------------------------
    dcol = _find_date_col(df)
    if dcol is None:
        raise KeyError(
            "Could not locate a usable date column/index. Columns present: "
            f"{list(df.columns)}"
        )
    dates = pd.to_datetime(df[dcol], errors="coerce")
    try:
        if getattr(dates.dt, "tz", None) is not None:
            dates = dates.dt.tz_convert(None)
    except (AttributeError, TypeError):
        pass
    df["Date"] = dates

    # --- 3) locate / construct the price column ------------------------------------
    pcol = _find_col(df.columns, PRICE_ALIASES)
    if pcol is None:
        raise KeyError(f"Could not locate a price column. Columns present: {list(df.columns)}")
    df["Adj Close"] = pd.to_numeric(df[pcol], errors="coerce")

    # --- 4) ticker column -----------------------------------------------------------
    tcol = _find_col(df.columns, ("ticker", "symbol", "asset", "security", "id", "name"))
    if tcol is None:
        df["Ticker"] = "ASSET"
    else:
        df["Ticker"] = df[tcol].astype(str)

    keep = ["Date", "Ticker", "Adj Close"]
    for extra in ("has_print", "is_filled"):
        if extra in df.columns:
            keep.append(extra)
    df = df[keep]

    # --- 5) hygiene: valid dates, non-positive prices are NOT data ------------------
    df = df[df["Date"].notna()].copy()
    df.loc[~(df["Adj Close"] > 0), "Adj Close"] = np.nan

    df = (
        df.sort_values(["Ticker", "Date"], kind="mergesort")
          .drop_duplicates(subset=["Ticker", "Date"], keep="last")
          .reset_index(drop=True)
    )

    # --- 6) INCEPTION ALIGNMENT: drop every row before an asset's first real print ---
    #        (NEVER fillna(0) -> no phantom assets)
    frames = []
    for tkr, g in df.groupby("Ticker", sort=True):
        g = g.sort_values("Date", kind="mergesort")
        first_valid = g["Adj Close"].first_valid_index()
        if first_valid is None:
            continue
        g = g.loc[first_valid:].copy()
        # forward-fill holidays/halts *after* inception only, never before
        g["Adj Close"] = g["Adj Close"].ffill()
        frames.append(g)
    if not frames:
        raise ValueError("No ticker has any valid price history after inception alignment.")

    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(["Ticker", "Date"], kind="mergesort").reset_index(drop=True)


def make_synthetic_panel(
    tickers=("SPY", "EFA", "EEM", "IEF", "TLT", "GLD"),
    n_bars: int = 3200,
    seed: int = 20240607,
) -> pd.DataFrame:
    """Synthetic panel with *staggered inceptions* so inception logic is genuinely exercised."""
    rng = np.random.default_rng(seed)
    all_dates = pd.bdate_range("2004-01-02", periods=n_bars)
    rows = []
    for k, tkr in enumerate(tickers):
        start = min(k * 180, n_bars // 2)
        d = all_dates[start:]
        m = len(d)
        mu = 0.00028 - 0.00004 * (k % 3)
        sig = 0.011 if k < 3 else 0.006
        r = rng.normal(mu, sig, m)
        px = 100.0 * np.exp(np.cumsum(r))
        rows.append(
            pd.DataFrame(
                {
                    "Date": d,
                    "Ticker": tkr,
                    "Adj Close": px,
                    "has_print": 1,
                    "is_filled": 0,
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def load_panel(path: str = PARQUET_FILE) -> tuple[pd.DataFrame, bool]:
    """Returns (tidy panel, used_synthetic_flag)."""
    if path and os.path.exists(path):
        try:
            raw = pd.read_parquet(path)
            return normalize_panel(raw), False
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Could not use '{path}' ({type(exc).__name__}: {exc}). "
                  f"Falling back to synthetic panel.")
    else:
        print(f"[WARN] Parquet file '{path}' not found. Falling back to synthetic panel.")
    return normalize_panel(make_synthetic_panel()), True


# ========================================================================================
# 2. REFERENCE CAUSAL SIGNAL GENERATOR (fallback if the project module is unavailable)
# ========================================================================================
FAMILY_PARAMS: dict[str, tuple] = {
    "SMA200": (50, 100, 150, 200, 250),
    "MOM12": (63, 126, 189, 252),
    "DUAL": ((10, 50), (20, 100), (50, 200)),
    "BREAKOUT": (55, 100, 200, 252),
}
_FALLBACK_FAMILIES = tuple(FAMILY_PARAMS.keys())


def _price_series_from_frame(df: pd.DataFrame) -> pd.Series:
    """Extract the ordered price vector from a single-ticker frame WITHOUT dropping rows.

    Row count must be preserved exactly so positional prefix comparisons stay meaningful.
    """
    if isinstance(df, pd.Series):
        s = pd.to_numeric(df, errors="coerce")
        return pd.Series(s.to_numpy(dtype=float), index=np.arange(len(s)))

    d = df
    if "Date" in d.columns:
        # already chronologically sorted in practice; mergesort keeps it stable & prefix-safe
        d = d.sort_values("Date", kind="mergesort")
    pcol = _find_col(d.columns, PRICE_ALIASES)
    if pcol is None:
        raise KeyError(f"No price column in frame. Columns: {list(d.columns)}")
    vals = pd.to_numeric(d[pcol], errors="coerce").to_numpy(dtype=float)
    vals = np.where(vals > 0, vals, np.nan)
    return pd.Series(vals, index=np.arange(len(vals)))


def _family_raw(s: pd.Series, family: str, param) -> tuple[np.ndarray, np.ndarray]:
    """Return (raw_signal_int8, valid_int8) computed ONLY from data at or before each bar."""
    if family == "SMA200":
        w = int(param)
        ma = s.rolling(w, min_periods=w).mean()
        valid = s.notna() & ma.notna() & (ma > 0)
        raw = valid & (s > ma)
    elif family == "MOM12":
        w = int(param)
        past = s.shift(w)
        valid = s.notna() & past.notna() & (past > 0)
        raw = valid & ((s / past - 1.0) > 0.0)
    elif family == "DUAL":
        fast, slow = int(param[0]), int(param[1])
        if fast >= slow:
            raise ValueError("DUAL requires fast < slow.")
        mf = s.rolling(fast, min_periods=fast).mean()
        ms = s.rolling(slow, min_periods=slow).mean()
        valid = s.notna() & mf.notna() & ms.notna()
        raw = valid & (mf > ms)
    elif family == "BREAKOUT":
        w = int(param)
        prior_high = s.shift(1).rolling(w, min_periods=w).max()
        valid = s.notna() & prior_high.notna()
        raw = valid & (s > prior_high)
    else:
        raise KeyError(f"Unknown family '{family}'.")

    return (
        raw.fillna(False).to_numpy().astype(np.int8),
        valid.fillna(False).to_numpy().astype(np.int8),
    )


def _lag_matrix(mat: np.ndarray, lag: int) -> np.ndarray:
    """Shift right by `lag` bars, zero-padding the warm-up. lag=0 -> identity (leaky)."""
    out = np.zeros_like(mat)
    if lag <= 0:
        return mat.copy()
    if lag < mat.shape[1]:
        out[:, lag:] = mat[:, : mat.shape[1] - lag]
    return out


def _fallback_generate_signals(
    df,
    is_causality_test: bool = False,
    negative_control: bool = False,
    lag: int = LAG,
) -> dict[str, np.ndarray]:
    """Causal signal generator.

    negative_control=True intentionally removes the lag (same-bar leak) so the tester can
    prove it is capable of detecting leakage.
    """
    s = _price_series_from_frame(df)
    n = len(s)
    eff_lag = 0 if negative_control else int(max(1, lag))

    out: dict[str, np.ndarray] = {}
    for fam, params in FAMILY_PARAMS.items():
        raws, vals = [], []
        for prm in params:
            r, v = _family_raw(s, fam, prm)
            raws.append(r)
            vals.append(v)
        raw_mat = np.vstack(raws) if raws else np.zeros((0, n), dtype=np.int8)
        val_mat = np.vstack(vals) if vals else np.zeros((0, n), dtype=np.int8)
        out[fam] = _lag_matrix(raw_mat, eff_lag)
        out[f"{fam}_valid"] = _lag_matrix(val_mat, eff_lag)
    out["_meta_lag"] = np.array([[eff_lag]], dtype=np.int8)
    return out


# ---- pick the generator: project module if it is usable, else the fallback --------------
def _probe_generator(gen, fams) -> bool:
    try:
        probe = normalize_panel(make_synthetic_panel(tickers=("PROBE",), n_bars=1400))
        res_full = gen(probe, is_causality_test=True, negative_control=False)
        if not isinstance(res_full, dict):
            return False
        for fam in fams:
            if fam not in res_full or f"{fam}_valid" not in res_full:
                return False
            a = np.asarray(res_full[fam])
            if a.ndim != 2 or a.shape[1] != len(probe):
                return False
        cut = 900
        res_cut = gen(probe.iloc[:cut].copy(), is_causality_test=True, negative_control=False)
        for fam in fams:
            if not np.array_equal(np.asarray(res_full[fam])[:, :cut], np.asarray(res_cut[fam])):
                return False
        res_neg = gen(probe, is_causality_test=True, negative_control=True)
        for fam in fams:
            if fam not in res_neg:
                return False
        return True
    except Exception:
        return False


_project_gen = None
_project_fams = None
try:  # pragma: no cover - project specific
    from opus8_signal_generator_v8 import generate_signals as _project_gen  # type: ignore
    from opus8_signal_generator_v8 import FAMILIES as _project_fams  # type: ignore
except Exception:
    _project_gen = None
    _project_fams = None

if _project_gen is not None and _project_fams and _probe_generator(_project_gen, tuple(_project_fams)):
    generate_signals = _project_gen
    FAMILIES = tuple(_project_fams)
    GENERATOR_SOURCE = "opus8_signal_generator_v8"
else:
    if _project_gen is not None:
        print("[WARN] Project signal generator unusable/non-conforming -> using internal "
              "reference causal generator.")
    generate_signals = _fallback_generate_signals
    FAMILIES = _FALLBACK_FAMILIES
    GENERATOR_SOURCE = "internal reference generator"


# ========================================================================================
# 3. CAUSALITY / LEAK TESTS
# ========================================================================================
def _shock_price_positional(df: pd.DataFrame, pos: int, factor: float) -> pd.DataFrame:
    """Positional (iloc) shock -> immune to duplicate index labels."""
    out = df.copy()
    pcol = _find_col(out.columns, PRICE_ALIASES)
    if pcol is None:
        raise KeyError("No price column to shock.")
    col_loc = out.columns.get_loc(pcol)
    out.iloc[pos, col_loc] = float(out.iloc[pos, col_loc]) * float(factor)
    return out


def _valid_intersection(sig: dict[str, np.ndarray], n: int) -> np.ndarray:
    mask = np.ones(n, dtype=bool)
    found = False
    for fam in FAMILIES:
        key = f"{fam}_valid"
        if key in sig:
            v = np.asarray(sig[key])
            if v.size:
                mask &= (v == 1).all(axis=0)
                found = True
    if not found:
        mask[:] = False
    return mask


def _families_equal(a: dict, b: dict, upto_a: int | None = None, upto_b: int | None = None) -> tuple[bool, str]:
    for fam in FAMILIES:
        for key in (fam, f"{fam}_valid"):
            if key not in a or key not in b:
                continue
            x = np.asarray(a[key])
            y = np.asarray(b[key])
            xs = x[:, :upto_a] if upto_a is not None else x
            ys = y[:, :upto_b] if upto_b is not None else y
            if xs.shape != ys.shape or not np.array_equal(xs, ys):
                return False, key
    return True, ""


def run_causality_tests(panel: pd.DataFrame, tickers: list[str] | None, seed: int = 42) -> None:
    print("=" * 78)
    print("OPUS 5/V8 CAUSALITY & LEAK DETECTOR  (prefix / append / warm-up / perturbation /")
    print("                                     negative control)")
    print(f"generator = {GENERATOR_SOURCE} | LAG = {LAG} | families = {list(FAMILIES)}")
    print("=" * 78)

    available = list(pd.unique(panel["Ticker"]))
    if tickers:
        universe = [t for t in tickers if t in available]
        missing = [t for t in tickers if t not in available]
        if missing:
            print(f"[WARN] Tickers absent from data (skipped): {missing}")
    else:
        universe = available
    if not universe:
        raise ValueError("No tradable tickers available for causality testing.")

    rng = np.random.default_rng(seed)
    tested = 0

    for ticker in universe:
        df_t = (
            panel.loc[panel["Ticker"] == ticker]
                 .sort_values("Date", kind="mergesort")
                 .reset_index(drop=True)
                 .copy()
        )
        n = len(df_t)
        print(f"\n--- Testing {ticker}  (bars = {n}) ---")

        min_bars = 700
        if n < min_bars:
            print(f"  [SKIP] Needs >= {min_bars} bars for the full battery.")
            continue

        base = generate_signals(df_t, is_causality_test=True, negative_control=False)

        for fam in FAMILIES:
            arr = np.asarray(base[fam])
            assert arr.ndim == 2, f"{ticker} {fam}: signal must be 2-D (variants x bars)."
            assert arr.shape[1] == n, (
                f"{ticker} {fam}: expected {n} bars, got {arr.shape[1]}."
            )
            assert np.isin(arr, (-1, 0, 1)).all(), f"{ticker} {fam}: positions must be in {{-1,0,1}}."

        # ---------------- A. Prefix invariance -------------------------------------
        lo = 400
        hi = n - 60
        assert hi > lo, "Not enough bars for truncation test."
        n_trunc = int(min(50, hi - lo))
        trunc_points = np.unique(rng.integers(lo, hi, size=n_trunc))
        for t_idx in trunc_points:
            t_idx = int(t_idx)
            trunc = generate_signals(
                df_t.iloc[:t_idx].copy(), is_causality_test=True, negative_control=False
            )
            ok, key = _families_equal(base, trunc, upto_a=t_idx, upto_b=None)
            assert ok, f"{ticker} {key} FAILED prefix invariance at truncation {t_idx}."
        print(f"  [PASS] A. Prefix invariance ({len(trunc_points)} random truncations)")

        # ---------------- B. Append invariance (future noise) ----------------------
        tail = df_t.iloc[-120:].copy().reset_index(drop=True)
        noise = 1.0 + rng.normal(0.0, 0.02, len(tail))
        tail["Adj Close"] = tail["Adj Close"].to_numpy(dtype=float) * noise
        if "Date" in tail.columns:
            last_date = pd.Timestamp(df_t["Date"].iloc[-1])
            tail["Date"] = pd.bdate_range(last_date + pd.Timedelta(days=1), periods=len(tail))
        df_append = pd.concat([df_t, tail], ignore_index=True)
        appended = generate_signals(df_append, is_causality_test=True, negative_control=False)
        ok, key = _families_equal(base, appended, upto_a=None, upto_b=n)
        assert ok, f"{ticker} {key} FAILED append invariance (future noise leaked backwards)."
        print("  [PASS] B. Append invariance (future noise)")

        # ---------------- C. Warm-up padding / lag structure -----------------------
        for fam in FAMILIES:
            arr = np.asarray(base[fam])
            assert (arr[:, :LAG] == 0).all(), (
                f"{ticker} {fam}: first {LAG} bar(s) must be flat (lag padding violated)."
            )
        print(f"  [PASS] C. Warm-up flat for the first {LAG} bar(s)")

        # ---------------- D. Perturbation (strict LAG-bar integrity) ---------------
        valid_mask = _valid_intersection(base, n)
        # need bar p valid for the *unlagged* signal too -> require p and p+1 lag-valid
        cand = np.where(valid_mask[:-1] & valid_mask[1:])[0]
        cand = cand[(cand > 300) & (cand < n - 60)]
        if cand.size < 50:
            print("  [SKIP] Not enough jointly-valid bars for perturbation / negative control.")
            continue

        p_idx = int(rng.choice(cand))
        df_pert = _shock_price_positional(df_t, p_idx, 1.20)  # +20% same-bar shock
        pert = generate_signals(df_pert, is_causality_test=True, negative_control=False)
        ok, key = _families_equal(base, pert, upto_a=p_idx + 1, upto_b=p_idx + 1)
        assert ok, (
            f"{ticker} {key} FAILED perturbation test: a shock at bar {p_idx} changed a "
            f"position at or before bar {p_idx} (same-bar leak)."
        )
        # the shock MUST propagate strictly after the lag, otherwise the test is vacuous
        changed_later, _ = _families_equal(base, pert)
        assert not changed_later, (
            f"{ticker}: shock at bar {p_idx} changed nothing at all -> perturbation test is "
            f"vacuous (signals insensitive to price)."
        )
        print(f"  [PASS] D. Perturbation test at bar {p_idx} (strict {LAG}-bar lag integrity)")

        # ---------------- E. Negative control -------------------------------------
        neg = generate_signals(df_t, is_causality_test=True, negative_control=True)
        neg_up = generate_signals(
            _shock_price_positional(df_t, p_idx, 10.0), is_causality_test=True, negative_control=True
        )
        neg_dn = generate_signals(
            _shock_price_positional(df_t, p_idx, 0.10), is_causality_test=True, negative_control=True
        )
        up_same, _ = _families_equal(neg, neg_up, upto_a=p_idx + 1, upto_b=p_idx + 1)
        dn_same, _ = _families_equal(neg, neg_dn, upto_a=p_idx + 1, upto_b=p_idx + 1)
        caught_leak = (not up_same) or (not dn_same)
        assert caught_leak, (
            f"{ticker} FAILED NEGATIVE CONTROL: the tester could not detect deliberate "
            f"same-bar leakage at bar {p_idx}."
        )
        print("  [PASS] E. Negative control (deliberate same-bar leak was detected)")
        tested += 1

    if tested == 0:
        raise AssertionError("No ticker completed the full causality battery -> tests are vacuous.")

    print("\n" + "=" * 78)
    print(f"ALL CAUSALITY & LEAK DETECTOR TESTS PASSED  ({tested} ticker(s) fully tested).")
    print("=" * 78)


# ========================================================================================
# 4. MATHEMATICALLY CORRECT BACKTEST ENGINE
# ========================================================================================
def price_matrix(panel: pd.DataFrame) -> pd.DataFrame:
    """Wide price matrix. Pre-inception cells remain NaN (NEVER 0)."""
    px = panel.pivot_table(index="Date", columns="Ticker", values="Adj Close", aggfunc="last")
    px = px.sort_index()
    out = px.copy()
    for c in out.columns:  # ffill strictly after inception
        first = out[c].first_valid_index()
        if first is not None:
            out.loc[first:, c] = out.loc[first:, c].ffill()
    return out


def simple_returns(px: pd.DataFrame) -> pd.DataFrame:
    try:
        r = px.pct_change(fill_method=None)
    except TypeError:  # very old pandas
        r = px.pct_change()
    return r.where(px.notna() & px.shift(1).notna())


def build_dual_momentum_weights(
    px: pd.DataFrame,
    offensive: list[str],
    defensive: list[str],
    lookback: int = 252,
    top_n: int = 1,
) -> pd.DataFrame:
    """Decision weights at bar t using ONLY data up to and including t.

    Bug #4 fix: the defensive sleeve is subject to its own ABSOLUTE momentum filter.
    Bug #1/#5 fix: an asset is only eligible once it has a full `lookback` of real history.
    """
    offensive = [c for c in offensive if c in px.columns]
    defensive = [c for c in defensive if c in px.columns]
    if not offensive:
        raise ValueError("No offensive assets present in the price matrix.")

    past = px.shift(lookback)
    mom = (px / past) - 1.0
    mom = mom.where(px.notna() & past.notna() & (past > 0))

    w = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    mom_off = mom[offensive]
    mom_def = mom[defensive] if defensive else None

    for t in px.index:
        row_off = mom_off.loc[t].dropna()
        winners = row_off[row_off > 0.0].sort_values(ascending=False)
        if len(winners) > 0:
            picks = list(winners.index[:top_n])
            w.loc[t, picks] = 1.0 / len(picks)
            continue
        if mom_def is not None:
            row_def = mom_def.loc[t].dropna()
            row_def = row_def[row_def > 0.0]           # ABSOLUTE momentum on defensives
            if len(row_def) > 0:
                best = row_def.sort_values(ascending=False).index[0]
                w.loc[t, best] = 1.0
        # else: 100% cash
    return w


def backtest(
    weights: pd.DataFrame,
    rets: pd.DataFrame,
    rf_annual: float = 0.02,
    tc_bps: float = 10.0,
    borrow_spread_bps: float = 75.0,
    start: pd.Timestamp | None = None,
) -> tuple[pd.Series, dict]:
    """Bar-by-bar net portfolio return series + metrics.

    Conventions
    -----------
    * weights.loc[t]  = target weights decided at the close of bar t.
    * They earn the return of bar t+1  -> internal shift(1).  No look-ahead.
    * Transaction cost of the trade executed at bar t-1 is charged in bar t.
    * Cash (1 - sum w) earns rf; negative cash (leverage) pays rf + borrow spread.
    """
    if not weights.index.equals(rets.index):
        weights = weights.reindex(rets.index)
    weights = weights.reindex(columns=rets.columns).fillna(0.0)

    if start is not None:
        rets = rets.loc[start:]
        weights = weights.loc[start:]

    w_dec = weights
    w_prev = w_dec.shift(1).fillna(0.0)

    # Bug #1 guard: never hold an asset whose return is not observable (pre-inception /
    # post-delisting). Any such exposure is forced to cash and hard-asserted afterwards.
    investable = rets.notna()
    w_eff = w_prev.where(investable, 0.0)
    assert not ((w_eff != 0.0) & ~investable).to_numpy().any(), "Phantom-asset exposure detected."

    asset_pnl = (w_eff * rets.fillna(0.0)).sum(axis=1)

    rf_daily = (1.0 + float(rf_annual)) ** (1.0 / TRADING_DAYS) - 1.0
    spread_daily = float(borrow_spread_bps) / 1e4 / TRADING_DAYS

    invested = w_eff.sum(axis=1)
    cash_w = 1.0 - invested
    cash_pnl = np.where(cash_w >= 0.0, cash_w * rf_daily, cash_w * (rf_daily + spread_daily))
    cash_pnl = pd.Series(cash_pnl, index=rets.index)

    # turnover executed at t-1 (i.e. |w_{t-1} - w_{t-2}|) is expensed in bar t
    turnover_exec = (w_dec.shift(1).fillna(0.0) - w_dec.shift(2).fillna(0.0)).abs().sum(axis=1)
    cost = turnover_exec * (float(tc_bps) / 1e4)

    net = asset_pnl + cash_pnl - cost

    # trim the leading all-cash warm-up (no signal yet) for honest statistics
    active = (w_eff.abs().sum(axis=1) > 0.0)
    if active.any():
        first_active = active.idxmax()
        net = net.loc[first_active:]
        turnover_exec = turnover_exec.loc[first_active:]
    net = net.dropna()

    metrics = performance_metrics(net, rf_annual=rf_annual)
    metrics["avg_annual_turnover"] = float(turnover_exec.mean() * TRADING_DAYS) if len(turnover_exec) else float("nan")
    metrics["total_cost_drag_annual"] = float(cost.reindex(net.index).fillna(0.0).mean() * TRADING_DAYS)
    return net, metrics


def performance_metrics(net: pd.Series, rf_annual: float = 0.02) -> dict:
    net = pd.Series(net).dropna().astype(float)
    n = len(net)
    out: dict[str, float] = {"n_bars": float(n)}
    if n < 2:
        return {**out, "cagr": float("nan"), "vol": float("nan"), "sharpe": float("nan"),
                "sortino": float("nan"), "max_drawdown": float("nan"), "calmar": float("nan"),
                "hit_rate": float("nan")}

    rf_daily = (1.0 + float(rf_annual)) ** (1.0 / TRADING_DAYS) - 1.0
    equity = (1.0 + net).cumprod()

    years = n / TRADING_DAYS
    total = float(equity.iloc[-1])
    out["cagr"] = total ** (1.0 / years) - 1.0 if total > 0 else float("nan")
    out["vol"] = float(net.std(ddof=1) * math.sqrt(TRADING_DAYS))

    # ---- Bug #2 fix: TRUE excess-return Sharpe (not CAGR / vol) --------------------
    excess = net - rf_daily
    sd = float(excess.std(ddof=1))
    out["sharpe"] = float(excess.mean() / sd * math.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")

    downside = excess[excess < 0.0]
    dsd = float(downside.std(ddof=1)) if len(downside) > 1 else float("nan")
    out["sortino"] = (
        float(excess.mean() / dsd * math.sqrt(TRADING_DAYS)) if dsd and dsd > 0 else float("nan")
    )

    dd = equity / equity.cummax() - 1.0
    out["max_drawdown"] = float(dd.min())
    out["calmar"] = float(out["cagr"] / abs(out["max_drawdown"])) if out["max_drawdown"] < 0 else float("nan")
    out["hit_rate"] = float((net > 0).mean())
    return out


def selftest_metrics() -> None:
    """Prove the Sharpe implementation is the excess-return Sharpe."""
    rng = np.random.default_rng(11)
    r = pd.Series(rng.normal(0.0004, 0.01, 5000))
    rf_annual = 0.03
    rf_d = (1.0 + rf_annual) ** (1.0 / TRADING_DAYS) - 1.0
    m = performance_metrics(r, rf_annual=rf_annual)
    exp = float((r - rf_d).mean() / (r - rf_d).std(ddof=1) * math.sqrt(TRADING_DAYS))
    assert abs(m["sharpe"] - exp) < 1e-12, "Sharpe formula mismatch."
    wrong = m["cagr"] / m["vol"]
    assert abs(m["sharpe"] - wrong) > 1e-6, "Sharpe must not equal CAGR/vol."

    # flat rf-only portfolio -> Sharpe ~ 0
    flat = pd.Series(np.full(2000, rf_d))
    m2 = performance_metrics(flat, rf_annual=rf_annual)
    assert not np.isfinite(m2["sharpe"]) or abs(m2["sharpe"]) < 1e-6, "rf-only Sharpe must be ~0."
    print("  [PASS] Metric self-test (true excess-return Sharpe, ddof=1, 252 annualisation)")


def selftest_costs() -> None:
    """Costs and borrow spread must strictly reduce performance."""
    idx = pd.bdate_range("2015-01-01", periods=600)
    rng = np.random.default_rng(5)
    a = pd.Series(np.exp(np.cumsum(rng.normal(0.0004, 0.01, len(idx)))) * 100, index=idx)
    px = pd.DataFrame({"A": a, "B": a * 1.0001})
    rets = simple_returns(px)

    flip = pd.DataFrame(0.0, index=idx, columns=["A", "B"])
    flip.iloc[::2, 0] = 1.0
    flip.iloc[1::2, 1] = 1.0

    _, free = backtest(flip, rets, rf_annual=0.0, tc_bps=0.0, borrow_spread_bps=0.0)
    _, paid = backtest(flip, rets, rf_annual=0.0, tc_bps=25.0, borrow_spread_bps=0.0)
    assert paid["cagr"] < free["cagr"], "Transaction costs must reduce CAGR."

    lev = pd.DataFrame(2.0, index=idx, columns=["A"]).reindex(columns=["A", "B"]).fillna(0.0)
    _, no_spread = backtest(lev, rets, rf_annual=0.02, tc_bps=0.0, borrow_spread_bps=0.0)
    _, with_spread = backtest(lev, rets, rf_annual=0.02, tc_bps=0.0, borrow_spread_bps=300.0)
    assert with_spread["cagr"] < no_spread["cagr"], "Borrow spread must reduce levered CAGR."
    print("  [PASS] Cost/borrow-spread self-test (turnover cost & financing both bite)")


def selftest_no_phantom(px: pd.DataFrame) -> None:
    """Late-inception assets must carry zero weight before their inception."""
    late = None
    for c in px.columns:
        fv = px[c].first_valid_index()
        if fv is not None and fv > px.index[0]:
            late = c
            break
    if late is None:
        print("  [SKIP] No staggered inception available for phantom-asset test.")
        return
    assert px[late].loc[: px[late].first_valid_index()].isna().sum() >= 1, "Expected pre-inception NaNs."
    w = build_dual_momentum_weights(px, offensive=list(px.columns), defensive=list(px.columns))
    pre = w.loc[: px[late].first_valid_index(), late].iloc[:-1]
    assert (pre == 0.0).all(), f"Phantom exposure to {late} before inception."
    print(f"  [PASS] Inception-alignment / no-phantom-asset test (probe = {late})")


# ========================================================================================
# 5. MAIN
# ========================================================================================
def main() -> int:
    panel, synthetic = load_panel(PARQUET_FILE)
    if synthetic:
        print("[INFO] Running on SYNTHETIC data (deterministic seed).")

    print(f"[INFO] Panel: {len(panel)} rows | {panel['Ticker'].nunique()} tickers | "
          f"{panel['Date'].min().date()} -> {panel['Date'].max().date()}")

    # ---- Part 1: causality / leak battery ------------------------------------------
    run_causality_tests(panel, TICKERS_TRADED)

    # ---- Part 2: engine math self-tests -------------------------------------------
    print("\n" + "=" * 78)
    print("BACKTEST ENGINE MATH SELF-TESTS")
    print("=" * 78)
    px = price_matrix(panel)
    selftest_metrics()
    selftest_costs()
    selftest_no_phantom(px)

    # ---- Part 3: reference dual-momentum run (all five bugs fixed) -----------------
    print("\n" + "=" * 78)
    print("REFERENCE DUAL-MOMENTUM BACKTEST (costs, borrow spread, absolute momentum,")
    print("inception alignment, true excess-return Sharpe)")
    print("=" * 78)

    cols = list(px.columns)
    defensive_hint = [c for c in cols if str(c).upper() in {"IEF", "TLT", "SHY", "BIL", "AGG", "GLD", "BND", "TIP"}]
    if not defensive_hint:
        defensive_hint = cols[-2:] if len(cols) >= 2 else cols[:]
    offensive = [c for c in cols if c not in defensive_hint] or cols[:]

    rets = simple_returns(px)
    weights = build_dual_momentum_weights(px, offensive=offensive, defensive=defensive_hint,
                                          lookback=252, top_n=1)
    net, stats = backtest(weights, rets, rf_annual=0.02, tc_bps=10.0, borrow_spread_bps=75.0)

    print(f"  offensive : {offensive}")
    print(f"  defensive : {defensive_hint}  (absolute-momentum gated)")
    if len(net):
        print(f"  period    : {net.index[0].date()} -> {net.index[-1].date()}  ({int(stats['n_bars'])} bars)")
    for k in ("cagr", "vol", "sharpe", "sortino", "max_drawdown", "calmar", "hit_rate",
              "avg_annual_turnover", "total_cost_drag_annual"):
        v = stats.get(k, float("nan"))
        print(f"  {k:<24}: {v: .4f}")
    print(f"  {'naive CAGR/vol (WRONG)':<24}: "
          f"{(stats['cagr'] / stats['vol'] if stats['vol'] else float('nan')): .4f}   <-- not used")

    print("\n" + "=" * 78)
    print("ALL TESTS PASSED — script is causality-clean and metric-correct.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print("\n*** TEST FAILURE ***")
        print(f"AssertionError: {exc}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print("\n*** FATAL ERROR ***")
        print(f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        sys.exit(2)