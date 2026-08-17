"""
Market Data Ingestion and Anomaly Sieve Module (Module 1).

Provides:
- Multi-timeframe SPY data ingestion (1H, 2H, 4H, 1D, 1W, 1MO)
- RTH session filtering and resampling
- Microsecond-safe Julian Date UT conversion bit-exact to Swiss Ephemeris
- Non-lookahead Candlestick Geometry Sieve (Solid Ratio, Wick Ratio)
- Trailing Volatility (ATR-20 shifted by 1) & Time-of-Day (TOD) RVOL
- Extreme Candlestick Anomaly Extraction Engine
"""

from .data_ingestion import (
    compute_julian_date,
    fetch_alpaca_1h_cached,
    filter_rth_sessions,
    resample_rth_ohlcv,
    fetch_yfinance_bars,
    load_market_data_for_timeframe,
    load_all_spy_timeframes,
)

from .anomaly_sieve import (
    compute_candlestick_geometry,
    compute_trailing_atr,
    compute_tod_rvol,
    compute_hardened_features_and_anomalies,
    extract_anomalies_for_timeframe,
    run_market_data_pipeline,
)

__all__ = [
    "compute_julian_date",
    "fetch_alpaca_1h_cached",
    "filter_rth_sessions",
    "resample_rth_ohlcv",
    "fetch_yfinance_bars",
    "load_market_data_for_timeframe",
    "load_all_spy_timeframes",
    "compute_candlestick_geometry",
    "compute_trailing_atr",
    "compute_tod_rvol",
    "compute_hardened_features_and_anomalies",
    "extract_anomalies_for_timeframe",
    "run_market_data_pipeline",
]
