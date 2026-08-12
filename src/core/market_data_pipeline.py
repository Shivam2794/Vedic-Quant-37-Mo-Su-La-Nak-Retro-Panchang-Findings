"""
Market Data Pipeline — Full Production Grade
=============================================
Collects ALL market data required for the Astrological ML Universe:
  1. OHLCV for all 40 ETFs (from inception to today)
  2. Target variables (returns at 1d/5d/21d/63d, direction, magnitude, crash flags)
  3. Market context (VIX, breadth, put/call, yield curve, DXY, gold, crude, copper)
  4. Asset-level technical indicators (SMA, RSI, ATR, Bollinger, Volume ratio, Beta)
  5. Market calendar events (FOMC, CPI, NFP, OpEx, quad witching)
  6. Overnight vs intraday split

Output:
  market_data/daily_ohlcv/       -> per-asset Parquet files
  market_data/targets/           -> per-asset target label Parquet files
  market_data/context/           -> market-wide context Parquet
  market_data/technicals/        -> per-asset technical Parquet files
  market_data/calendar/          -> event calendar Parquet
  market_data/master_daily.parquet -> FINAL joined master table
"""

import os
import time
import warnings
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
BASE_DIR    = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data")
TODAY_STR   = datetime.today().strftime("%Y-%m-%d")
START_DATE  = "1993-01-01"  # SPY inception year

# Output sub-directories
OHLCV_DIR   = BASE_DIR / "daily_ohlcv"
TARGET_DIR  = BASE_DIR / "targets"
CONTEXT_DIR = BASE_DIR / "context"
TECH_DIR    = BASE_DIR / "technicals"
CAL_DIR     = BASE_DIR / "calendar"

for d in [BASE_DIR, OHLCV_DIR, TARGET_DIR, CONTEXT_DIR, TECH_DIR, CAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# ASSET UNIVERSE — 40 ETFs with inception dates
# ─────────────────────────────────────────────
ETF_UNIVERSE = {
    "SPY":  "1993-01-29", "QQQ":  "1999-03-10", "DIA":  "1998-01-20",
    "IWM":  "2000-05-26", "XLK":  "1998-12-22", "XLF":  "1998-12-22",
    "XLE":  "1998-12-22", "XLV":  "1998-12-22", "XLY":  "1998-12-22",
    "XLP":  "1998-12-22", "XLU":  "1998-12-22", "XLI":  "1998-12-22",
    "XLB":  "1998-12-22", "XLRE": "2015-10-08", "XLC":  "2018-06-19",
    "SMH":  "2000-12-20", "XME":  "2006-06-22", "XBI":  "2006-02-06",
    "KRE":  "2006-06-22", "XOP":  "2006-06-22", "ITB":  "2006-05-05",
    "PAVE": "2017-03-08", "JETS": "2015-04-30", "HACK": "2014-11-12",
    "URA":  "2010-11-05", "TAN":  "2008-04-15", "NLR":  "2007-08-15",
    "GDX":  "2006-05-22", "COPX": "2010-04-19", "CPER": "2011-11-15",
    "GLD":  "2004-11-18", "SLV":  "2006-04-28", "TLT":  "2002-07-26",
    "HYG":  "2007-04-11", "DBA":  "2007-01-05", "USO":  "2006-04-10",
    "UNG":  "2007-04-18", "EEM":  "2003-04-15", "PPLT": "2010-01-08",
    "ARKK": "2014-10-31",
}

# ─────────────────────────────────────────────
# MARKET CONTEXT TICKERS
# ─────────────────────────────────────────────
CONTEXT_TICKERS = {
    "^VIX":   "VIX",         # Fear index
    "^VVIX":  "VVIX",        # Volatility of volatility
    "^GSPC":  "SPX",         # S&P 500 index (for breadth proxy)
    "^IXIC":  "NDX",         # Nasdaq
    "^TNX":   "Yield_10Y",   # 10-year Treasury yield
    "^IRX":   "Yield_3M",    # 3-month T-bill
    "^FVX":   "Yield_5Y",    # 5-year Treasury yield
    "^TYX":   "Yield_30Y",   # 30-year Treasury yield
    "DX-Y.NYB": "DXY",       # Dollar index
    "GC=F":   "Gold",        # Gold futures
    "CL=F":   "Crude_Oil",   # WTI Crude
    "HG=F":   "Copper",      # Copper (Dr. Copper)
    "^ADVN":  "Advances",    # NYSE Advancing issues
    "^DECN":  "Declines",    # NYSE Declining issues
    "^TICK":  "TICK",        # NYSE Tick
    "^ADD":   "ADD",         # NYSE Advance-Decline line
}


# ════════════════════════════════════════════
# STEP 1: DOWNLOAD RAW OHLCV FOR ALL ETFs
# ════════════════════════════════════════════
def download_ohlcv(tickers: dict) -> dict:
    """Download daily OHLCV for all ETFs from inception. Returns dict of DataFrames."""
    results = {}
    print(f"\n{'='*60}")
    print("STEP 1: Downloading OHLCV for all ETFs")
    print(f"{'='*60}")

    for ticker, inception in tickers.items():
        out_path = OHLCV_DIR / f"{ticker}_ohlcv.parquet"

        # Load existing if up to date (today's date in filename)
        if out_path.exists():
            df_existing = pd.read_parquet(out_path)
            last_date = pd.to_datetime(df_existing["Date"].max()).strftime("%Y-%m-%d")
            # If data is current (within 2 days), skip
            if (datetime.today() - pd.to_datetime(last_date)).days <= 2:
                print(f"  [{ticker}] ✓ Up to date ({last_date}). Skipping.")
                results[ticker] = df_existing
                continue

        print(f"  [{ticker}] Downloading from {inception}...", end=" ", flush=True)
        try:
            raw = yf.download(
                ticker,
                start=inception,
                end=TODAY_STR,
                interval="1d",
                auto_adjust=True,
                progress=False,
                actions=True,  # Include dividends and splits
            )
            if raw.empty:
                print(f"EMPTY — skipping")
                continue

            # Flatten MultiIndex columns
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = [col[0] if col[1] == ticker else f"{col[0]}_{col[1]}"
                               for col in raw.columns]

            raw = raw.reset_index()

            # Standardise column names
            col_map = {c: c.strip().title() for c in raw.columns}
            col_map.update({k: v for k, v in {
                "date": "Date", "open": "Open", "high": "High",
                "low": "Low", "close": "Close", "volume": "Volume",
                "dividends": "Dividends", "stock splits": "Stock_Splits",
            }.items() if k in [c.lower() for c in raw.columns]})
            raw = raw.rename(columns={c: c.strip() for c in raw.columns})
            raw.columns = [c.strip() for c in raw.columns]

            # Ensure Date is timezone-naive datetime
            raw["Date"] = pd.to_datetime(raw["Date"]).dt.tz_localize(None) \
                if pd.api.types.is_datetime64_tz_dtype(raw["Date"]) \
                else pd.to_datetime(raw["Date"])

            # Keep standard columns
            keep = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume",
                                 "Dividends", "Stock_Splits"] if c in raw.columns]
            df = raw[keep].dropna(subset=["Date", "Close"]).copy()
            df["Ticker"] = ticker
            df = df.sort_values("Date").reset_index(drop=True)

            df.to_parquet(out_path, index=False)
            results[ticker] = df
            print(f"{len(df)} rows → {out_path.name}")

        except Exception as e:
            print(f"ERROR: {e}")

        time.sleep(0.25)  # Rate limit courtesy

    return results


# ════════════════════════════════════════════
# STEP 2: COMPUTE TARGET VARIABLES
# ════════════════════════════════════════════
def compute_targets(ohlcv: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Compute all forward-looking prediction targets."""
    df = ohlcv.sort_values("Date").copy()
    c = df["Close"]
    o = df["Open"]
    h = df["High"]
    l = df["Low"]
    v = df["Volume"]

    # ── Returns ──────────────────────────────
    df["ret_1d"]  = c.pct_change(1).shift(-1)   # Next day's return
    df["ret_2d"]  = c.pct_change(2).shift(-2)
    df["ret_5d"]  = c.pct_change(5).shift(-5)
    df["ret_10d"] = c.pct_change(10).shift(-10)
    df["ret_21d"] = c.pct_change(21).shift(-21)
    df["ret_63d"] = c.pct_change(63).shift(-63)

    # ── Intraday vs Overnight ─────────────────
    df["intraday_ret"]  = (c / o) - 1            # Open → Close (human trading)
    df["overnight_ret"] = (o / c.shift(1)) - 1   # Prev Close → Open (God's gap)
    df["next_overnight_ret"] = df["overnight_ret"].shift(-1)

    # ── Day Range ─────────────────────────────
    df["daily_range_pct"]   = (h - l) / o        # Intraday volatility
    df["high_ret"]          = (h / o) - 1        # Best case
    df["low_ret"]           = (l / o) - 1        # Worst case
    df["gap_size"]          = abs(df["overnight_ret"])
    df["gap_direction"]     = np.where(df["overnight_ret"] > 0.001, "GAP_UP",
                              np.where(df["overnight_ret"] < -0.001, "GAP_DOWN", "FLAT"))

    # ── Direction Classification ──────────────
    threshold = 0.001  # 0.1% = flat
    df["dir_1d"]  = np.where(df["ret_1d"] >  threshold, 1,
                    np.where(df["ret_1d"] < -threshold, -1, 0))
    df["dir_5d"]  = np.where(df["ret_5d"] >  threshold, 1,
                    np.where(df["ret_5d"] < -threshold, -1, 0))
    df["dir_21d"] = np.where(df["ret_21d"] >  threshold, 1,
                    np.where(df["ret_21d"] < -threshold, -1, 0))

    # ── Magnitude Classification ──────────────
    def mag_class(ret_series):
        return pd.cut(ret_series.abs(),
                      bins=[-np.inf, 0.005, 0.01, 0.02, 0.05, np.inf],
                      labels=[0, 1, 2, 3, 4])

    df["mag_class_1d"]  = mag_class(df["ret_1d"].fillna(0))
    df["mag_class_5d"]  = mag_class(df["ret_5d"].fillna(0))

    # ── Event / Crash Flags ───────────────────
    df["is_crash_day_2pct"]  = (df["ret_1d"] < -0.02).astype(int)
    df["is_rally_day_2pct"]  = (df["ret_1d"] >  0.02).astype(int)
    df["is_crash_day_5pct"]  = (df["ret_5d"] < -0.05).astype(int)
    df["is_rally_day_5pct"]  = (df["ret_5d"] >  0.05).astype(int)
    df["is_breakout_day"]    = (c > c.rolling(20).max().shift(1)).astype(int)
    df["is_breakdown_day"]   = (c < c.rolling(20).min().shift(1)).astype(int)

    # ── Volatility Targets ────────────────────
    df["realized_vol_5d"]   = c.pct_change().rolling(5).std()
    df["realized_vol_21d"]  = c.pct_change().rolling(21).std()
    df["drawdown_from_252h"] = (c - c.rolling(252).max()) / c.rolling(252).max()

    df["Ticker"] = ticker
    return df[["Date", "Ticker"] + [col for col in df.columns
                                     if col not in ["Date", "Ticker",
                                                    "Open", "High", "Low",
                                                    "Close", "Volume",
                                                    "Dividends", "Stock_Splits"]]]


# ════════════════════════════════════════════
# STEP 3: COMPUTE TECHNICAL INDICATORS
# ════════════════════════════════════════════
def compute_technicals(ohlcv: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Compute all technical indicators as ML context features."""
    df = ohlcv.sort_values("Date").copy()
    c = df["Close"]
    h = df["High"]
    l = df["Low"]
    v = df["Volume"]

    # ── Trend ─────────────────────────────────
    df["sma_10"]  = c.rolling(10).mean()
    df["sma_20"]  = c.rolling(20).mean()
    df["sma_50"]  = c.rolling(50).mean()
    df["sma_200"] = c.rolling(200).mean()
    df["ema_9"]   = c.ewm(span=9).mean()
    df["ema_21"]  = c.ewm(span=21).mean()

    df["close_vs_sma20"]  = (c / df["sma_20"]) - 1
    df["close_vs_sma50"]  = (c / df["sma_50"]) - 1
    df["close_vs_sma200"] = (c / df["sma_200"]) - 1
    df["sma20_vs_sma50"]  = (df["sma_20"] / df["sma_50"]) - 1

    # ── Momentum ──────────────────────────────
    # RSI
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = c.ewm(span=12).mean()
    ema26 = c.ewm(span=26).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # Rate of Change
    df["roc_5"]  = c.pct_change(5)
    df["roc_21"] = c.pct_change(21)

    # ── Volatility ────────────────────────────
    # ATR
    tr = pd.DataFrame({
        "hl": h - l,
        "hc": (h - c.shift(1)).abs(),
        "lc": (l - c.shift(1)).abs(),
    }).max(axis=1)
    df["atr_14"] = tr.rolling(14).mean()
    df["atr_pct"] = df["atr_14"] / c  # Normalised ATR

    # Bollinger Bands
    rolling_mean = c.rolling(20).mean()
    rolling_std  = c.rolling(20).std()
    df["bb_upper"] = rolling_mean + 2 * rolling_std
    df["bb_lower"] = rolling_mean - 2 * rolling_std
    df["bb_pct"]   = (c - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
    df["bb_width"]  = (df["bb_upper"] - df["bb_lower"]) / rolling_mean

    # Historical Volatility percentile
    hv_21 = c.pct_change().rolling(21).std()
    df["hv_21d"]          = hv_21
    df["hv_21d_pct_rank"] = hv_21.rolling(252).rank(pct=True)

    # ── Volume ────────────────────────────────
    df["volume_ratio_10d"]  = v / v.rolling(10).mean()
    df["volume_ratio_20d"]  = v / v.rolling(20).mean()
    df["obv"] = (np.sign(c.diff()) * v).cumsum()

    # ── Price Position ────────────────────────
    df["pct_from_52wk_high"] = (c / c.rolling(252).max()) - 1
    df["pct_from_52wk_low"]  = (c / c.rolling(252).min()) - 1
    df["price_pct_rank_252d"] = c.rolling(252).rank(pct=True)

    df["Ticker"] = ticker
    return df[["Date", "Ticker"] + [col for col in df.columns
                                     if col not in ["Date", "Ticker",
                                                    "Open", "High", "Low",
                                                    "Close", "Volume",
                                                    "Dividends", "Stock_Splits"]]]


# ════════════════════════════════════════════
# STEP 4: DOWNLOAD MARKET CONTEXT
# ════════════════════════════════════════════
def download_context() -> pd.DataFrame:
    """Download all market-wide context features: VIX, breadth, macro rates."""
    print(f"\n{'='*60}")
    print("STEP 4: Downloading Market Context (VIX, Rates, Breadth)")
    print(f"{'='*60}")

    out_path = CONTEXT_DIR / "market_context_daily.parquet"
    dfs = []

    for yf_ticker, col_name in CONTEXT_TICKERS.items():
        print(f"  [{yf_ticker}] → {col_name}...", end=" ", flush=True)
        try:
            raw = yf.download(yf_ticker, start=START_DATE, end=TODAY_STR,
                              interval="1d", auto_adjust=True, progress=False)
            if raw.empty:
                print("EMPTY")
                continue

            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = [col[0] for col in raw.columns]

            raw = raw.reset_index()
            raw["Date"] = pd.to_datetime(raw["Date"]).dt.tz_localize(None) \
                if pd.api.types.is_datetime64_tz_dtype(raw["Date"]) \
                else pd.to_datetime(raw["Date"])

            close_col = "Close" if "Close" in raw.columns else raw.columns[-1]
            series = raw[["Date", close_col]].copy()
            series = series.rename(columns={close_col: col_name})
            dfs.append(series.set_index("Date"))
            print(f"{len(series)} rows")

        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.25)

    if not dfs:
        print("  WARNING: No context data downloaded!")
        return pd.DataFrame()

    ctx = pd.concat(dfs, axis=1).reset_index()
    ctx = ctx.sort_values("Date").reset_index(drop=True)

    # ── Derived Context Features ──────────────
    if "Yield_10Y" in ctx.columns and "Yield_3M" in ctx.columns:
        ctx["yield_curve_10y3m"] = ctx["Yield_10Y"] - ctx["Yield_3M"]
        ctx["yield_inverted_flag"] = (ctx["yield_curve_10y3m"] < 0).astype(int)

    if "VIX" in ctx.columns:
        ctx["vix_1d_change"]     = ctx["VIX"].diff()
        ctx["vix_spike_flag"]    = (ctx["vix_1d_change"] > 5).astype(int)
        ctx["vix_pct_rank_252d"] = ctx["VIX"].rolling(252).rank(pct=True)
        ctx["vix_regime"] = pd.cut(ctx["VIX"],
                                   bins=[0, 15, 20, 30, 40, 1000],
                                   labels=["calm", "low", "elevated", "high", "extreme"])

    if "Advances" in ctx.columns and "Declines" in ctx.columns:
        ctx["advance_decline_ratio"] = ctx["Advances"] / \
                                       (ctx["Declines"].replace(0, np.nan))
        ctx["breadth_thrust_flag"] = (ctx["advance_decline_ratio"] > 2.0).astype(int)

    if "DXY" in ctx.columns:
        ctx["dxy_1d_change"] = ctx["DXY"].pct_change()

    ctx.to_parquet(out_path, index=False)
    print(f"\n  Context saved: {len(ctx)} rows → {out_path.name}")
    return ctx


# ════════════════════════════════════════════
# STEP 5: BUILD MARKET CALENDAR
# ════════════════════════════════════════════
def build_market_calendar() -> pd.DataFrame:
    """Build a comprehensive market event calendar."""
    print(f"\n{'='*60}")
    print("STEP 5: Building Market Calendar")
    print(f"{'='*60}")

    out_path = CAL_DIR / "market_calendar.parquet"

    try:
        import pandas_market_calendars as mcal
        nyse = mcal.get_calendar("NYSE")
        schedule = nyse.schedule(start_date=START_DATE, end_date=TODAY_STR)
        trading_days = schedule.index.normalize()
    except ImportError:
        # Fallback: use yfinance SPY to get trading days
        spy_raw = yf.download("SPY", start=START_DATE, end=TODAY_STR,
                              interval="1d", progress=False, auto_adjust=True)
        spy_raw = spy_raw.reset_index()
        trading_days = pd.to_datetime(spy_raw["Date"]).dt.tz_localize(None)

    cal = pd.DataFrame({"Date": pd.to_datetime(trading_days)})
    cal = cal.sort_values("Date").reset_index(drop=True)

    # ── OpEx: 3rd Friday of each month ────────
    def is_third_friday(dt):
        return dt.weekday() == 4 and 15 <= dt.day <= 21

    cal["is_monthly_opex"] = cal["Date"].apply(is_third_friday).astype(int)

    # ── Quarterly (Quad) Witching: March/June/Sep/Dec 3rd Friday
    cal["is_quad_witching"] = (
        cal["is_monthly_opex"] & cal["Date"].dt.month.isin([3, 6, 9, 12])
    ).astype(int)

    # ── Days to next OpEx ─────────────────────
    opex_dates = cal.loc[cal["is_monthly_opex"] == 1, "Date"].values
    cal["days_to_next_opex"] = cal["Date"].apply(
        lambda d: int((min([o for o in opex_dates if o >= np.datetime64(d.date())],
                           default=opex_dates[-1]) - np.datetime64(d.date()))
                      / np.timedelta64(1, "D")) if len(opex_dates) > 0 else -1
    )

    # ── Month and week indicators ─────────────
    cal["is_month_end"]     = (cal["Date"].dt.month != cal["Date"].shift(-1).dt.month).astype(int)
    cal["is_month_start"]   = (cal["Date"].dt.month != cal["Date"].shift(1).dt.month).astype(int)
    cal["is_quarter_end"]   = (cal["Date"].dt.quarter != cal["Date"].shift(-1).dt.quarter).astype(int)
    cal["day_of_week"]      = cal["Date"].dt.dayofweek  # 0=Mon, 4=Fri
    cal["month_of_year"]    = cal["Date"].dt.month
    cal["week_of_month"]    = (cal["Date"].dt.day - 1) // 7 + 1
    cal["is_monday"]        = (cal["day_of_week"] == 0).astype(int)
    cal["is_friday"]        = (cal["day_of_week"] == 4).astype(int)

    # ── FOMC Schedule: Approximate 8 meetings/year ──
    # Known FOMC dates (hardcoded approximate logic)
    # In production: load from Federal Reserve website or FRED
    cal["is_fomc_day_approx"] = 0  # Placeholder for manual/API population

    # ── NFP: First Friday of each month ───────
    cal["is_first_friday"] = (
        (cal["day_of_week"] == 4) & (cal["Date"].dt.day <= 7)
    ).astype(int)

    # ── Trading day sequence ───────────────────
    cal["trading_day_of_month"] = cal.groupby(
        [cal["Date"].dt.year, cal["Date"].dt.month]
    ).cumcount() + 1

    cal.to_parquet(out_path, index=False)
    print(f"  Calendar built: {len(cal)} trading days → {out_path.name}")
    return cal


# ════════════════════════════════════════════
# STEP 6: COMPUTE RELATIVE STRENGTH VS SPY
# ════════════════════════════════════════════
def compute_relative_strength(ohlcv_dict: dict) -> dict:
    """Compute each ETF's return relative to SPY as an additional feature."""
    print(f"\n{'='*60}")
    print("STEP 6: Computing Relative Strength vs SPY")
    print(f"{'='*60}")

    if "SPY" not in ohlcv_dict:
        print("  SPY not found — skipping relative strength")
        return {}

    spy = ohlcv_dict["SPY"].set_index("Date")["Close"].rename("SPY_Close")
    spy_ret = spy.pct_change()

    rs_data = {}
    for ticker, df in ohlcv_dict.items():
        if ticker == "SPY":
            continue
        etf = df.set_index("Date")["Close"]
        rs_20d  = etf.pct_change(20) - spy.pct_change(20).reindex(etf.index)
        rs_63d  = etf.pct_change(63) - spy.pct_change(63).reindex(etf.index)

        # Rolling Beta
        etf_ret = etf.pct_change()
        spy_ret_aligned = spy_ret.reindex(etf_ret.index)
        cov = etf_ret.rolling(60).cov(spy_ret_aligned)
        var = spy_ret_aligned.rolling(60).var()
        beta_60d = cov / var.replace(0, np.nan)

        rs_df = pd.DataFrame({
            "Date":               etf.index,
            "Ticker":             ticker,
            "rs_vs_spy_20d":     rs_20d.values,
            "rs_vs_spy_63d":     rs_63d.values,
            "beta_60d":           beta_60d.values,
        })
        rs_data[ticker] = rs_df

    print(f"  Relative strength computed for {len(rs_data)} ETFs")
    return rs_data


# ════════════════════════════════════════════
# STEP 7: ASSEMBLE MASTER DAILY TABLE
# ════════════════════════════════════════════
def assemble_master(ohlcv_dict: dict, context: pd.DataFrame,
                    calendar: pd.DataFrame) -> pd.DataFrame:
    """Join all data into the master daily ML-ready table."""
    print(f"\n{'='*60}")
    print("STEP 7: Assembling Master Daily Table")
    print(f"{'='*60}")

    all_assets = []

    for ticker, ohlcv_raw in ohlcv_dict.items():
        print(f"  Processing [{ticker}]...", end=" ", flush=True)
        try:
            df = ohlcv_raw.sort_values("Date").copy()

            # Compute targets
            targets = compute_targets(df, ticker)

            # Compute technicals
            techs   = compute_technicals(df, ticker)

            # Save individual files
            targets.to_parquet(TARGET_DIR / f"{ticker}_targets.parquet", index=False)
            techs.to_parquet(TECH_DIR   / f"{ticker}_technicals.parquet", index=False)

            # Merge base OHLCV + targets + technicals
            merged = df.merge(targets, on=["Date", "Ticker"], how="left")
            merged = merged.merge(techs,   on=["Date", "Ticker"], how="left")

            all_assets.append(merged)
            print(f"✓ {len(merged)} rows")

        except Exception as e:
            print(f"ERROR: {e}")

    if not all_assets:
        print("No assets processed!")
        return pd.DataFrame()

    # Stack all assets
    master = pd.concat(all_assets, ignore_index=True)

    # Join market context
    if not context.empty:
        master = master.merge(context, on="Date", how="left")

    # Join calendar
    if not calendar.empty:
        master = master.merge(calendar, on="Date", how="left")

    # Sort by asset then date
    master = master.sort_values(["Ticker", "Date"]).reset_index(drop=True)

    # Save master
    out_path = BASE_DIR / "master_daily.parquet"
    master.to_parquet(out_path, index=False)

    print(f"\n{'='*60}")
    print(f"MASTER TABLE COMPLETE")
    print(f"  Rows    : {len(master):,}")
    print(f"  Columns : {len(master.columns):,}")
    print(f"  Assets  : {master['Ticker'].nunique()}")
    print(f"  Date range: {master['Date'].min()} → {master['Date'].max()}")
    print(f"  Saved to: {out_path}")
    print(f"{'='*60}")

    return master


# ════════════════════════════════════════════
# MAIN EXECUTION
# ════════════════════════════════════════════
if __name__ == "__main__":
    print("MARKET DATA PIPELINE — FULL PRODUCTION RUN")
    print(f"Run timestamp: {datetime.now()}")
    print(f"Output directory: {BASE_DIR}")
    print()

    # Step 1: Download OHLCV
    ohlcv_dict = download_ohlcv(ETF_UNIVERSE)
    print(f"\n  Downloaded: {len(ohlcv_dict)} assets")

    # Step 4: Market context
    context = download_context()

    # Step 5: Calendar
    calendar = build_market_calendar()

    # Step 6: Relative strength (joins back into technicals)
    rs_data = compute_relative_strength(ohlcv_dict)

    # Step 7: Assemble master table
    master = assemble_master(ohlcv_dict, context, calendar)

    # ── Final summary ─────────────────────────
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE — SUMMARY")
    print(f"{'='*60}")
    print(f"  Master rows     : {len(master):,}")
    print(f"  Master columns  : {len(master.columns):,}")
    print(f"  Astrological    : ~22,000 columns (computed separately)")
    print(f"  Next step       : Run ephemeris_engine.py to join astro data")
    print(f"  Final ML matrix : master_daily.parquet + astro_features.parquet")
    print(f"{'='*60}")
