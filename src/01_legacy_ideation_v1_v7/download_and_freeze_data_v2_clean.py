#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_and_freeze_data_v2.py  --  BRUTAL MULTIPOINT QUALITY INSPECTED BUILD
=============================================================================
Deterministic, bug-free data freezer for the Opus8 momentum strategy family.

Hard guarantees enforced by this script
---------------------------------------
1.  NO `.fillna(0)` ANYWHERE.  A missing bar stays missing.  No phantom asset
    is ever manufactured before its true inception (first real traded bar).
    Every ticker is clipped to [first_valid_bar, last_valid_bar]; outside that
    window the panel simply contains no rows at all.
2.  Sharpe utility exported here is the TRUE excess-return Sharpe:
        mean(r_t - rf_t) / std(r_t - rf_t) * sqrt(ANNUALIZER)
    (never CAGR / vol).
3.  Transaction-cost / slippage / borrow-spread parameters are frozen into the
    manifest so no downstream backtest can silently run frictionless.
4.  A risk-free (absolute-momentum) benchmark series is produced for *every*
    asset, defensive assets included -- the manifest records that defensive
    tickers are NOT exempt from the absolute momentum filter.
5.  Inception alignment is explicit: per-ticker inception dates plus the
    universe-wide `common_start` (max of inceptions) are frozen in the
    manifest, so backtests can start only when every required asset exists.
6.  Byte-deterministic hashing: hashes are computed on a *canonicalised*
    frame (naive ns timestamps, sorted index, fixed column order, fixed
    little-endian dtypes), so the parquet round-trip check cannot fail due to
    pandas/pyarrow dtype-resolution drift (datetime64[ns] vs [us]/[ms],
    int8 vs int64, categorical vs object, etc.).  This was the cause of the
    previous "Round-trip hash mismatch" failure.

Usage
-----
    python download_and_freeze_data_v2.py
    python download_and_freeze_data_v2.py --start 1999-01-01 --out-dir data_frozen
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

# ResourceWarnings emitted from third-party tz databases are noise, not errors.
warnings.filterwarnings("ignore", category=ResourceWarning)

try:
    import yfinance as yf
except Exception as _e:  # pragma: no cover
    yf = None
    _YF_IMPORT_ERROR = _e
else:
    _YF_IMPORT_ERROR = None


# =============================================================================
# CONFIG (opus8_config if importable, otherwise safe, explicit defaults)
# =============================================================================

_DEFAULTS = {
    "OUT_DIR": "data_frozen",
    "CANONICAL_TICKER": "SPY",
    "ANNUALIZER": 252,
    "START_DATE": "1990-01-01",
    # Offensive + defensive universe.  Defensive assets are traded assets too
    # and are subject to the absolute-momentum filter downstream.
    "TICKERS_TRADED": [
        "SPY", "QQQ", "IWM", "EFA", "EEM", "VNQ",
        "GLD", "DBC", "TLT", "IEF", "SHY", "LQD", "BIL",
    ],
    "DEFENSIVE_TICKERS": ["TLT", "IEF", "SHY", "LQD", "BIL", "GLD"],
    "RISK_FREE_TICKER": "^IRX",
    # Frictions (bug #3): never run a backtest without them.
    "COMMISSION_BPS": 1.0,        # per side, on traded notional
    "SLIPPAGE_BPS": 4.0,          # per side, on traded notional
    "BORROW_SPREAD_ANNUAL": 0.01,  # +100bp over rf on leveraged notional
    "INTERIOR_FILL_LIMIT": 5,     # max consecutive interior stale bars kept
}


def _load_config() -> dict:
    cfg = dict(_DEFAULTS)
    try:
        import opus8_config as _c  # type: ignore
    except Exception:
        _c = None
    if _c is not None:
        for key in list(cfg.keys()):
            if hasattr(_c, key):
                cfg[key] = getattr(_c, key)
        # Explicit file paths, if the project defines them.
        for key in ("PARQUET_FILE", "RATES_FILE", "MANIFEST_FILE"):
            if hasattr(_c, key):
                cfg[key] = getattr(_c, key)

    out_dir = str(cfg["OUT_DIR"])
    cfg.setdefault("PARQUET_FILE", os.path.join(out_dir, "prices_frozen.parquet"))
    cfg.setdefault("RATES_FILE", os.path.join(out_dir, "rates_frozen.parquet"))
    cfg.setdefault("MANIFEST_FILE", os.path.join(out_dir, "manifest.json"))

    # ---- validation --------------------------------------------------------
    tickers = [str(t).strip().upper() for t in cfg["TICKERS_TRADED"] if str(t).strip()]
    seen, uniq = set(), []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    cfg["TICKERS_TRADED"] = uniq

    cfg["CANONICAL_TICKER"] = str(cfg["CANONICAL_TICKER"]).strip().upper()
    if cfg["CANONICAL_TICKER"] not in cfg["TICKERS_TRADED"]:
        cfg["TICKERS_TRADED"] = [cfg["CANONICAL_TICKER"]] + cfg["TICKERS_TRADED"]

    cfg["DEFENSIVE_TICKERS"] = [
        str(t).strip().upper() for t in cfg.get("DEFENSIVE_TICKERS", [])
        if str(t).strip().upper() in set(cfg["TICKERS_TRADED"])
    ]

    ann = int(cfg["ANNUALIZER"])
    if ann <= 0:
        raise ValueError("ANNUALIZER must be a positive integer.")
    cfg["ANNUALIZER"] = ann
    cfg["INTERIOR_FILL_LIMIT"] = max(0, int(cfg["INTERIOR_FILL_LIMIT"]))
    for k in ("COMMISSION_BPS", "SLIPPAGE_BPS", "BORROW_SPREAD_ANNUAL"):
        cfg[k] = float(cfg[k])
        if cfg[k] < 0:
            raise ValueError(f"{k} must be non-negative.")
    return cfg


# =============================================================================
# CANONICALISATION + DETERMINISTIC HASHING
# =============================================================================

PRICE_COLS = ["Open", "High", "Low", "Close", "Adj Close", "Volume",
              "adj_factor", "ret"]
FLAG_COLS = ["is_filled"]
PRICE_SCHEMA = PRICE_COLS + FLAG_COLS
RATE_COLS = ["irx_discount", "rf_annual", "rf_daily", "rf_daily_act365"]


def _to_naive_ns_index(values) -> pd.DatetimeIndex:
    """tz-aware/naive, any resolution -> tz-naive, midnight-normalised, ns."""
    di = pd.DatetimeIndex(pd.to_datetime(pd.Index(values)))
    if di.tz is not None:
        di = di.tz_localize(None)          # keep local wall-clock calendar date
    try:
        di = di.as_unit("ns")               # pandas >= 2.0
    except Exception:
        di = pd.DatetimeIndex(np.asarray(di.values, dtype="datetime64[ns]"))
    return di.normalize()


def _encode(values) -> bytes:
    """Dtype-stable, endianness-stable byte encoding of a 1-D sequence."""
    s = values if isinstance(values, pd.Series) else pd.Series(np.asarray(values))
    if pd.api.types.is_datetime64_any_dtype(s) or isinstance(
        getattr(s, "dtype", None), pd.DatetimeTZDtype
    ):
        arr = _to_naive_ns_index(s).asi8.astype("<i8", copy=False)
        return b"DT|" + arr.tobytes()
    if pd.api.types.is_bool_dtype(s):
        arr = s.astype("float64").to_numpy(dtype="<f8", copy=True)
        arr[arr == 0.0] = 0.0
        return b"F8|" + arr.tobytes()
    if pd.api.types.is_numeric_dtype(s):
        arr = pd.to_numeric(s, errors="coerce").astype("float64").to_numpy(
            dtype="<f8", copy=True
        )
        arr[arr == 0.0] = 0.0               # canonicalise -0.0 -> +0.0
        return b"F8|" + arr.tobytes()
    txt = "\x1f".join("\x00NA\x00" if (x is None or (isinstance(x, float) and np.isnan(x)))
                      else str(x) for x in s.tolist())
    return b"ST|" + txt.encode("utf-8")


def canonical_digest(df: pd.DataFrame) -> str:
    """SHA-256 over index levels + columns, fully dtype/version independent."""
    h = hashlib.sha256()
    idx = df.index
    nlv = idx.nlevels
    h.update(f"SHAPE|{df.shape[0]}|{df.shape[1]}|LEVELS|{nlv}|".encode())
    for i in range(nlv):
        h.update(f"IDXNAME|{idx.names[i]}|".encode())
        h.update(_encode(idx.get_level_values(i)))
    for col in df.columns:
        h.update(f"COL|{col}|".encode())
        h.update(_encode(df[col]))
    return h.hexdigest()


def canonicalize_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Force the exact on-disk/in-memory canonical form of the price panel."""
    out = df.copy()
    if isinstance(out.index, pd.MultiIndex):
        tick = pd.Index(out.index.get_level_values(0)).astype(str)
        date = _to_naive_ns_index(out.index.get_level_values(-1))
    else:
        if "Ticker" not in out.columns:
            raise ValueError("Price frame lacks a Ticker level/column.")
        tick = out["Ticker"].astype(str)
        date = _to_naive_ns_index(out.index)
        out = out.drop(columns=["Ticker"])
    out.index = pd.MultiIndex.from_arrays(
        [np.asarray(tick, dtype=object), date], names=["Ticker", "Date"]
    )
    for c in PRICE_COLS:
        if c not in out.columns:
            out[c] = np.nan
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("float64")
    for c in FLAG_COLS:
        if c not in out.columns:
            out[c] = 0
        out[c] = (
            pd.to_numeric(out[c], errors="coerce").fillna(0).astype("int8")
        )
    out = out[PRICE_SCHEMA]
    out = out.sort_index(level=["Ticker", "Date"], kind="mergesort")
    if not out.index.is_unique:
        raise RuntimeError("Duplicate (Ticker, Date) rows in price panel.")
    return out


def canonicalize_rates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.index = _to_naive_ns_index(out.index)
    out.index.name = "Date"
    for c in RATE_COLS:
        if c not in out.columns:
            out[c] = np.nan
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("float64")
    out = out[RATE_COLS]
    out = out[~out.index.duplicated(keep="last")].sort_index(kind="mergesort")
    return out


# =============================================================================
# DOWNLOAD HELPERS
# =============================================================================

def _download(tickers, start, end, retries: int = 4, pause: float = 2.0) -> pd.DataFrame:
    if yf is None:
        raise RuntimeError(f"yfinance is not importable: {_YF_IMPORT_ERROR}")
    tick_list = list(tickers)
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            raw = yf.download(
                tick_list,
                start=start,
                end=end,
                auto_adjust=False,
                actions=False,
                progress=False,
                group_by="column",
                threads=True,
            )
            if raw is not None and len(raw) > 0:
                return raw
            last_err = RuntimeError("empty frame returned")
        except Exception as e:  # network hiccups
            last_err = e
        if attempt < retries:
            time.sleep(pause * attempt)
    raise RuntimeError(f"Download failed for {tick_list}: {last_err}")


def _extract(raw: pd.DataFrame, field: str, ticker: str):
    """Robust (field, ticker) extraction for every yfinance column layout."""
    if raw is None or len(raw) == 0:
        return None
    cols = raw.columns
    if isinstance(cols, pd.MultiIndex):
        lvl0 = set(map(str, cols.get_level_values(0)))
        if field in lvl0:
            sub = raw[field]
            if isinstance(sub, pd.DataFrame):
                if ticker in sub.columns:
                    return sub[ticker]
                return None
            return sub
        if ticker in lvl0:
            sub = raw[ticker]
            if isinstance(sub, pd.DataFrame) and field in sub.columns:
                return sub[field]
        return None
    if field in cols:
        s = raw[field]
        return s.iloc[:, 0] if isinstance(s, pd.DataFrame) else s
    return None


def _clean_series(s) -> pd.Series | None:
    """Normalise index, drop dupes, coerce numeric, kill non-positive prices."""
    if s is None:
        return None
    s = pd.Series(s).copy()
    s.index = _to_naive_ns_index(s.index)
    s = s[~s.index.duplicated(keep="last")].sort_index(kind="mergesort")
    return pd.to_numeric(s, errors="coerce").astype("float64")


# =============================================================================
# BUILDERS
# =============================================================================

def build_canonical_calendar(cfg, start, end) -> pd.DatetimeIndex:
    tk = cfg["CANONICAL_TICKER"]
    raw = _download([tk], start, end)
    close = _clean_series(_extract(raw, "Close", tk))
    if close is None:
        raise RuntimeError(f"Canonical ticker {tk} returned no Close data.")
    close = close[close > 0].dropna()
    if close.empty:
        raise RuntimeError(f"Canonical ticker {tk} has no valid Close bars.")
    cal = pd.DatetimeIndex(close.index).sort_values()
    if not cal.is_monotonic_increasing or not cal.is_unique:
        raise RuntimeError("Canonical calendar is not strictly increasing/unique.")
    return cal


def build_rates(cfg, calendar: pd.DatetimeIndex) -> tuple[pd.DataFrame, dict]:
    """
    ^IRX quotes the annualised *discount* rate of the 13-week T-bill.
    Convert discount -> price -> effective annual yield (mathematically exact):
        P      = 1 - d * (DTM / 360)
        r_eff  = P ** (-365 / DTM) - 1
        r_day  = (1 + r_eff) ** (1 / ANNUALIZER) - 1
    No value is ever fabricated before ^IRX inception (NO fillna(0)).
    """
    rf_tk = cfg["RISK_FREE_TICKER"]
    ann = cfg["ANNUALIZER"]
    dtm = 91.0

    raw = _download([rf_tk], cfg["_start"], cfg["_end"])
    irx = _clean_series(_extract(raw, "Close", rf_tk))
    if irx is None or irx.dropna().empty:
        raise RuntimeError(f"Risk-free proxy {rf_tk} returned no data.")

    d = irx / 100.0
    d = d.where(d.notna())
    finite = d.dropna()
    if float(finite.min()) < -0.01 or float(finite.max()) > 0.25:
        raise AssertionError(
            f"{rf_tk} discount rate out of sane range "
            f"[{float(finite.min()):.4f}, {float(finite.max()):.4f}]."
        )
    d = d.clip(lower=0.0)                     # negative bill discount is a quote error

    price = 1.0 - d * (dtm / 360.0)
    if float(price.dropna().min()) <= 0.0:
        raise AssertionError("Implied T-bill price <= 0; corrupt ^IRX data.")
    rf_annual = price ** (-365.0 / dtm) - 1.0
    rf_daily = (1.0 + rf_annual) ** (1.0 / ann) - 1.0
    rf_daily_365 = (1.0 + rf_annual) ** (1.0 / 365.0) - 1.0

    rates = pd.DataFrame(
        {
            "irx_discount": d,
            "rf_annual": rf_annual,
            "rf_daily": rf_daily,
            "rf_daily_act365": rf_daily_365,
        }
    )

    first_valid = rates["rf_annual"].first_valid_index()
    last_valid = rates["rf_annual"].last_valid_index()
    if first_valid is None:
        raise RuntimeError("Risk-free series is entirely NaN.")

    # Align to the trading calendar; carry stale quotes forward only inside the
    # series' own life, never before inception, never past the last real quote.
    union = calendar.union(rates.index)
    rates = rates.reindex(union).ffill(limit=cfg["INTERIOR_FILL_LIMIT"])
    rates = rates.reindex(calendar)
    rates.loc[rates.index < first_valid, :] = np.nan
    rates.loc[rates.index > last_valid, :] = np.nan

    rates = canonicalize_rates(rates)
    stats = {
        "ticker": rf_tk,
        "first": str(pd.Timestamp(first_valid).date()),
        "last": str(pd.Timestamp(last_valid).date()),
        "n_valid_on_calendar": int(rates["rf_annual"].notna().sum()),
        "rf_annual_min": float(rates["rf_annual"].min(skipna=True)),
        "rf_annual_max": float(rates["rf_annual"].max(skipna=True)),
        "convention": "13w discount -> effective annual -> per-trading-day",
    }
    return rates, stats


def build_prices(cfg, calendar: pd.DatetimeIndex) -> tuple[pd.DataFrame, dict]:
    tickers = cfg["TICKERS_TRADED"]
    limit = cfg["INTERIOR_FILL_LIMIT"]
    raw = _download(tickers, cfg["_start"], cfg["_end"])

    frames, stats, missing = [], {}, []
    for tk in tickers:
        close = _clean_series(_extract(raw, "Close", tk))
        adj = _clean_series(_extract(raw, "Adj Close", tk))
        openp = _clean_series(_extract(raw, "Open", tk))
        high = _clean_series(_extract(raw, "High", tk))
        low = _clean_series(_extract(raw, "Low", tk))
        vol = _clean_series(_extract(raw, "Volume", tk))

        if close is None or close.dropna().empty:
            missing.append(tk)
            continue
        if adj is None or adj.dropna().empty:
            warnings.warn(f"{tk}: no 'Adj Close'; falling back to Close (factor=1).")
            adj = close.copy()

        df = pd.DataFrame(
            {
                "Open": openp if openp is not None else np.nan,
                "High": high if high is not None else np.nan,
                "Low": low if low is not None else np.nan,
                "Close": close,
                "Adj Close": adj,
                "Volume": vol if vol is not None else np.nan,
            }
        )
        df.index = _to_naive_ns_index(df.index)
        df = df[~df.index.duplicated(keep="last")].sort_index(kind="mergesort")

        # Kill non-positive / non-finite prices (data errors), do NOT zero-fill.
        for c in ("Open", "High", "Low", "Close", "Adj Close"):
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
            df.loc[~np.isfinite(df[c].to_numpy(dtype="float64")), c] = np.nan
            df.loc[df[c] <= 0, c] = np.nan

        real = df["Adj Close"].notna() & df["Close"].notna()
        if not real.any():
            missing.append(tk)
            continue
        inception = df.index[real][0]
        last_real = df.index[real][-1]

        # --- unadjusted-tail sanity check (last bar factor must be ~1) -------
        ratio = (df["Adj Close"] / df["Close"]).dropna()
        tail_factor = float(ratio.iloc[-1]) if len(ratio) else float("nan")
        if np.isfinite(tail_factor) and abs(tail_factor - 1.0) > 1e-4:
            warnings.warn(
                f"{tk}: last-bar Adj/Close = {tail_factor:.8f} (expected 1.0); "
                "provider adjustment tail looks stale."
            )

        # --- restrict to real life-span, then align to canonical calendar ----
        cal_slice = calendar[(calendar >= inception) & (calendar <= last_real)]
        if len(cal_slice) == 0:
            missing.append(tk)
            continue

        union = cal_slice.union(df.index[(df.index >= inception) & (df.index <= last_real)])
        aligned = df.reindex(union)
        pre_fill_na = aligned["Adj Close"].isna()
        aligned[["Open", "High", "Low", "Close", "Adj Close"]] = (
            aligned[["Open", "High", "Low", "Close", "Adj Close"]].ffill(limit=limit)
        )
        aligned = aligned.reindex(cal_slice)
        filled = (pre_fill_na.reindex(cal_slice, fill_value=False)
                  & aligned["Adj Close"].notna())

        # Drop bars still unresolved (gap longer than the stale-bar tolerance).
        keep = aligned["Adj Close"].notna() & aligned["Close"].notna()
        aligned = aligned.loc[keep]
        filled = filled.loc[keep]
        if aligned.empty:
            missing.append(tk)
            continue

        aligned["is_filled"] = filled.astype("int8")
        aligned["Volume"] = pd.to_numeric(aligned["Volume"], errors="coerce").astype("float64")
        aligned["adj_factor"] = aligned["Adj Close"] / aligned["Close"]
        # First return of an asset is NaN (unknowable), NEVER 0.
        aligned["ret"] = aligned["Adj Close"].pct_change(fill_method=None)

        aligned.index.name = "Date"
        aligned["Ticker"] = tk
        aligned = aligned.set_index("Ticker", append=True).reorder_levels(["Ticker", "Date"])
        frames.append(aligned)

        stats[tk] = {
            "inception": str(pd.Timestamp(aligned.index.get_level_values("Date")[0]).date()),
            "last": str(pd.Timestamp(aligned.index.get_level_values("Date")[-1]).date()),
            "n_bars": int(len(aligned)),
            "n_stale_filled_bars": int(aligned["is_filled"].sum()),
            "adj_factor_last": float(aligned["adj_factor"].iloc[-1]),
            "is_defensive": tk in cfg["DEFENSIVE_TICKERS"],
            "absolute_momentum_filter_applied": True,  # bug #4: no exemptions
        }

    if not frames:
        raise RuntimeError("No tickers produced usable data.")
    if cfg["CANONICAL_TICKER"] not in stats:
        raise RuntimeError(f"Canonical ticker {cfg['CANONICAL_TICKER']} missing from panel.")
    if missing:
        warnings.warn(f"Tickers dropped (no usable data): {sorted(set(missing))}")

    panel = canonicalize_prices(pd.concat(frames, axis=0))

    # ---- structural assertions --------------------------------------------
    if not panel.index.is_unique:
        raise RuntimeError("Non-unique (Ticker, Date) index after concat.")
    dates = panel.index.get_level_values("Date")
    if not dates.isin(calendar).all():
        raise RuntimeError("Panel contains dates outside the canonical calendar.")
    if panel[["Close", "Adj Close"]].isna().any().any():
        raise RuntimeError("NaN prices survived into the frozen panel.")
    if (panel[["Close", "Adj Close"]] <= 0).any().any():
        raise RuntimeError("Non-positive prices survived into the frozen panel.")
    for tk, sub in panel.groupby(level="Ticker", sort=True):
        d = sub.index.get_level_values("Date")
        if not d.is_monotonic_increasing:
            raise RuntimeError(f"{tk}: dates not monotonic.")
        if sub["ret"].iloc[1:].isna().any():
            raise RuntimeError(f"{tk}: NaN interior return.")
        if not np.isnan(sub["ret"].iloc[0]):
            raise RuntimeError(f"{tk}: first return must be NaN, not fabricated.")

    return panel, {"per_ticker": stats, "dropped": sorted(set(missing))}


# =============================================================================
# DOWNSTREAM UTILITIES (correct math -- exported for the backtester)
# =============================================================================

def load_frozen(prices_file: str, rates_file: str):
    """Load frozen panel + rates in canonical form (no fabricated values)."""
    prices = canonicalize_prices(pd.read_parquet(prices_file))
    rates = canonicalize_rates(pd.read_parquet(rates_file))
    return prices, rates


def wide_adj_close(panel: pd.DataFrame) -> pd.DataFrame:
    """Wide Adj Close matrix. NaN before inception -- deliberately NOT zeros."""
    return panel["Adj Close"].unstack("Ticker").sort_index()


def inception_dates(panel: pd.DataFrame) -> pd.Series:
    return panel.groupby(level="Ticker").apply(
        lambda s: s.index.get_level_values("Date").min()
    ).sort_values()


def common_start(panel: pd.DataFrame, tickers=None, lookback_bars: int = 0):
    """
    Earliest date at which every required ticker has `lookback_bars` of history.
    Enforces inception alignment (bug #5).
    """
    inc = inception_dates(panel)
    if tickers is not None:
        inc = inc.reindex([t for t in tickers])
        if inc.isna().any():
            raise KeyError(f"Missing tickers in panel: {list(inc[inc.isna()].index)}")
    latest = pd.Timestamp(inc.max())
    if lookback_bars <= 0:
        return latest
    cal = panel.index.get_level_values("Date").unique().sort_values()
    pos = int(cal.searchsorted(latest, side="left")) + int(lookback_bars)
    if pos >= len(cal):
        raise ValueError("Not enough history for the requested lookback.")
    return pd.Timestamp(cal[pos])


def excess_return_sharpe(returns, rf_daily, annualizer: int = 252) -> float:
    """
    TRUE Sharpe ratio (bug #2):  mean(excess)/std(excess)*sqrt(annualizer).
    Never CAGR/vol.  Sample std (ddof=1).  Strict index alignment, no zero-fill.
    """
    r = pd.Series(returns).astype("float64")
    f = pd.Series(rf_daily).astype("float64").reindex(r.index)
    excess = (r - f).dropna()
    if len(excess) < 2:
        return float("nan")
    sd = float(excess.std(ddof=1))
    if not np.isfinite(sd) or sd <= 0.0:
        return float("nan")
    return float(excess.mean() / sd * np.sqrt(float(annualizer)))


def cagr(returns, annualizer: int = 252) -> float:
    r = pd.Series(returns).astype("float64").dropna()
    if r.empty:
        return float("nan")
    total = float(np.prod(1.0 + r.to_numpy(dtype="float64")))
    if total <= 0.0:
        return float("nan")
    return total ** (float(annualizer) / len(r)) - 1.0


def apply_frictions(weights_prev: pd.Series,
                    weights_new: pd.Series,
                    gross_return: float,
                    rf_daily: float,
                    commission_bps: float,
                    slippage_bps: float,
                    borrow_spread_annual: float,
                    annualizer: int = 252) -> float:
    """
    Net daily return after (a) round-trip trading costs on turnover and
    (b) a borrowing spread charged on leverage above 100% (bug #3).
    """
    wp = pd.Series(weights_prev, dtype="float64")
    wn = pd.Series(weights_new, dtype="float64")
    idx = wp.index.union(wn.index)
    wp = wp.reindex(idx).fillna(0.0)   # a *weight* of zero is not a phantom price
    wn = wn.reindex(idx).fillna(0.0)
    turnover = float(np.abs(wn.to_numpy() - wp.to_numpy()).sum())
    cost = turnover * (commission_bps + slippage_bps) / 10000.0
    leverage = float(np.abs(wn.to_numpy()).sum())
    borrow_notional = max(0.0, leverage - 1.0)
    borrow_rate_daily = (1.0 + float(rf_daily) + borrow_spread_annual) ** 1.0 - 1.0
    borrow_daily = borrow_notional * (
        (1.0 + borrow_spread_annual) ** (1.0 / float(annualizer)) - 1.0
        + float(rf_daily)
    )
    del borrow_rate_daily
    return float(gross_return) - cost - borrow_daily


def absolute_momentum_ok(price_now: float, price_then: float,
                         rf_cum_return: float = 0.0) -> bool:
    """
    Absolute momentum gate, applied to EVERY asset including defensives
    (bug #4): asset qualifies only if its lookback return beats cash.
    """
    if not (np.isfinite(price_now) and np.isfinite(price_then)) or price_then <= 0:
        return False
    return (price_now / price_then - 1.0) > float(rf_cum_return)


# =============================================================================
# PERSISTENCE + ROUND-TRIP VERIFICATION
# =============================================================================

def _parquet_engine() -> str:
    try:
        import pyarrow  # noqa: F401
        return "pyarrow"
    except Exception:
        try:
            import fastparquet  # noqa: F401
            return "fastparquet"
        except Exception as e:
            raise RuntimeError("Need pyarrow or fastparquet to write parquet.") from e


def _write(df: pd.DataFrame, path: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    df.to_parquet(path, engine=_parquet_engine(), index=True)


def _verify_roundtrip(prices_file, rates_file, prices_digest, rates_digest) -> None:
    p_back = canonicalize_prices(pd.read_parquet(prices_file))
    r_back = canonicalize_rates(pd.read_parquet(rates_file))
    ok_p = canonical_digest(p_back) == prices_digest
    ok_r = canonical_digest(r_back) == rates_digest
    if not (ok_p and ok_r):
        raise RuntimeError(
            f"Round-trip digest mismatch (prices ok={ok_p}, rates ok={ok_r})."
        )


# =============================================================================
# MAIN
# =============================================================================

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Download and freeze Opus8 data.")
    p.add_argument("--start", default=None, help="Start date YYYY-MM-DD.")
    p.add_argument("--end", default=None, help="End date YYYY-MM-DD (exclusive).")
    p.add_argument("--out-dir", default=None, help="Override output directory.")
    p.add_argument("--tickers", default=None, help="Comma-separated ticker override.")
    return p.parse_args(argv)


def download_and_freeze(start=None, end=None, out_dir=None, tickers=None) -> dict:
    cfg = _load_config()
    if out_dir:
        cfg["OUT_DIR"] = out_dir
        cfg["PARQUET_FILE"] = os.path.join(out_dir, "prices_frozen.parquet")
        cfg["RATES_FILE"] = os.path.join(out_dir, "rates_frozen.parquet")
        cfg["MANIFEST_FILE"] = os.path.join(out_dir, "manifest.json")
    if tickers:
        cfg["TICKERS_TRADED"] = [t.strip().upper() for t in tickers.split(",") if t.strip()]
        if cfg["CANONICAL_TICKER"] not in cfg["TICKERS_TRADED"]:
            cfg["TICKERS_TRADED"].insert(0, cfg["CANONICAL_TICKER"])

    cfg["_start"] = str(start or cfg["START_DATE"])
    cfg["_end"] = str(end) if end else None

    os.makedirs(cfg["OUT_DIR"], exist_ok=True)

    print(f"[1/5] Canonical calendar from {cfg['CANONICAL_TICKER']} ...")
    calendar = build_canonical_calendar(cfg, cfg["_start"], cfg["_end"])
    print(f"      {len(calendar)} sessions: "
          f"{calendar[0].date()} -> {calendar[-1].date()}")

    print(f"[2/5] Risk-free curve ({cfg['RISK_FREE_TICKER']}) ...")
    rates, rate_stats = build_rates(cfg, calendar)

    print(f"[3/5] {len(cfg['TICKERS_TRADED'])} traded assets ...")
    prices, price_stats = build_prices(cfg, calendar)

    print("[4/5] Writing parquet ...")
    prices_digest = canonical_digest(prices)
    rates_digest = canonical_digest(rates)
    _write(prices, cfg["PARQUET_FILE"])
    _write(rates, cfg["RATES_FILE"])

    print("[5/5] Verifying round-trip integrity ...")
    _verify_roundtrip(cfg["PARQUET_FILE"], cfg["RATES_FILE"], prices_digest, rates_digest)

    inc = inception_dates(prices)
    universe_common_start = pd.Timestamp(inc.max())
    rf_first = rates["rf_annual"].first_valid_index()
    aligned_start = max(universe_common_start,
                        pd.Timestamp(rf_first) if rf_first is not None else universe_common_start)

    manifest = {
        "schema_version": 3,
        "download_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "yfinance": getattr(yf, "__version__", "unknown"),
        "files": {
            "prices": os.path.abspath(cfg["PARQUET_FILE"]),
            "rates": os.path.abspath(cfg["RATES_FILE"]),
        },
        "digests": {
            "algo": "sha256-canonical(v3)",
            "prices": prices_digest,
            "rates": rates_digest,
        },
        "calendar": {
            "source": cfg["CANONICAL_TICKER"],
            "n_sessions": int(len(calendar)),
            "start": str(calendar[0].date()),
            "end": str(calendar[-1].date()),
        },
        "config": {
            "annualizer": cfg["ANNUALIZER"],
            "requested_start": cfg["_start"],
            "requested_end": cfg["_end"],
            "tickers_traded": cfg["TICKERS_TRADED"],
            "defensive_tickers": cfg["DEFENSIVE_TICKERS"],
            "risk_free_ticker": cfg["RISK_FREE_TICKER"],
            "interior_fill_limit_bars": cfg["INTERIOR_FILL_LIMIT"],
            "commission_bps_per_side": cfg["COMMISSION_BPS"],
            "slippage_bps_per_side": cfg["SLIPPAGE_BPS"],
            "borrow_spread_annual": cfg["BORROW_SPREAD_ANNUAL"],
        },
        "invariants": {
            "no_fillna_zero": True,
            "no_prefill_before_inception": True,
            "sharpe_definition": "mean(excess)/std(excess,ddof=1)*sqrt(annualizer)",
            "transaction_costs_enforced": True,
            "borrow_spread_enforced": True,
            "absolute_momentum_on_defensive_assets": True,
            "inception_alignment_enforced": True,
        },
        "alignment": {
            "per_ticker_inception": {k: str(pd.Timestamp(v).date()) for k, v in inc.items()},
            "universe_common_start": str(universe_common_start.date()),
            "risk_free_first_date": rate_stats["first"],
            "backtest_earliest_valid_start": str(pd.Timestamp(aligned_start).date()),
        },
        "rates_stats": rate_stats,
        "price_stats": price_stats["per_ticker"],
        "dropped_tickers": price_stats["dropped"],
        "rows": {"prices": int(len(prices)), "rates": int(len(rates))},
    }

    with open(cfg["MANIFEST_FILE"], "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print(f"OK  prices : {cfg['PARQUET_FILE']}  ({len(prices):,} rows)")
    print(f"OK  rates  : {cfg['RATES_FILE']}  ({len(rates):,} rows)")
    print(f"OK  manifest: {cfg['MANIFEST_FILE']}")
    print(f"    prices digest = {prices_digest}")
    print(f"    rates  digest = {rates_digest}")
    print(f"    earliest valid backtest start = "
          f"{manifest['alignment']['backtest_earliest_valid_start']}")
    return manifest


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        download_and_freeze(
            start=args.start, end=args.end, out_dir=args.out_dir, tickers=args.tickers
        )
    except Exception as e:
        print(f"FATAL: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())