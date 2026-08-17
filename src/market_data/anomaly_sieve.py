"""
SPY Candlestick Anomaly Sieve & Non-Lookahead Feature Engineering Engine.

Implements:
- Pure Candlestick Geometry: Real Body, Candle Range, Upper/Lower Wicks, Solid Ratio, Max Wick Ratio
- Zero-lookahead Trailing True Range and ATR(20) with strict prior-bar shift (shift(1))
- Time-of-Day (TOD) Relative Volume (RVOL) to eliminate intraday U-curve distortion
- Big Volatility & Magnitude Outliers with timeframe return percentage floors
- Strict Anomaly Sieve returning filtered DataFrames with 100% mathematical integrity
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

from .data_ingestion import (
    compute_julian_date,
    load_market_data_for_timeframe,
    load_all_spy_timeframes,
)

# Canonical timeframe return floors to protect against false positives in ultra-low volatility regimes
TIMEFRAME_RETURN_FLOORS: Dict[str, float] = {
    "1H": 0.50,
    "2H": 0.80,
    "4H": 1.20,
    "1D": 1.50,
    "1W": 3.00,
    "1MO": 5.00,
    "1M": 5.00,
}


def compute_candlestick_geometry(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes pure physical candlestick geometric attributes:
    - Real Body = |Close - Open|
    - Candle Range = High - Low
    - Upper Wick = High - max(Open, Close)
    - Lower Wick = min(Open, Close) - Low
    - Solid Ratio = Real Body / Range (with eps safeguard for zero range)
    - Max Wick Ratio = max(Upper Wick, Lower Wick) / Range
    - Candle Direction = GREEN (Close > Open), RED (Close < Open), DOJI (Close == Open)
    - Disentangled Returns: Intra-candle Body Return, Overnight Gap Return, Total Economic Return
    """
    df = df.copy()

    # Core Geometry
    real_body = (df["Close"] - df["Open"]).abs()
    candle_range = df["High"] - df["Low"]

    upper_wick = df["High"] - np.maximum(df["Open"], df["Close"])
    lower_wick = np.minimum(df["Open"], df["Close"]) - df["Low"]

    # Safe division protection
    valid_range = candle_range > 1e-6
    solid_ratio = np.where(valid_range, real_body / candle_range, 0.0)
    upper_wick_ratio = np.where(valid_range, upper_wick / candle_range, 0.0)
    lower_wick_ratio = np.where(valid_range, lower_wick / candle_range, 0.0)
    max_wick_ratio = np.maximum(upper_wick_ratio, lower_wick_ratio)

    direction = np.where(
        df["Close"] > df["Open"], "GREEN",
        np.where(df["Close"] < df["Open"], "RED", "DOJI")
    )

    # Return Disentanglement
    body_return_pct = (df["Close"] - df["Open"]) / df["Open"] * 100.0
    abs_body_return_pct = body_return_pct.abs()

    prev_close = df["Close"].shift(1)
    overnight_gap_pct = np.where(prev_close > 0, (df["Open"] - prev_close) / prev_close * 100.0, 0.0)
    total_return_pct = np.where(prev_close > 0, (df["Close"] - prev_close) / prev_close * 100.0, 0.0)

    # Populate canonical columns + aliases
    df["Real_Body"] = real_body
    df["Body"] = real_body
    df["Candle_Range"] = candle_range
    df["Range"] = candle_range
    df["Upper_Wick"] = upper_wick
    df["Lower_Wick"] = lower_wick
    df["Upper_Wick_Ratio"] = upper_wick_ratio
    df["Lower_Wick_Ratio"] = lower_wick_ratio
    df["Solid_Ratio"] = solid_ratio
    df["Max_Wick_Ratio"] = max_wick_ratio
    df["Candle_Direction"] = direction
    df["Direction"] = direction

    df["Body_Return_Pct"] = body_return_pct
    df["Abs_Body_Return_Pct"] = abs_body_return_pct
    df["Overnight_Gap_Pct"] = overnight_gap_pct
    df["Total_Return_Pct"] = total_return_pct

    return df


def compute_trailing_atr(df: pd.DataFrame, window: int = 20, min_periods: int = 5) -> pd.DataFrame:
    """
    Computes Trailing True Range and ATR(20) with STRICT shift(1) prior-bar lagging.
    Guarantees zero lookahead bias ($O(1)$ temporal causality).
    """
    df = df.copy()
    prev_close = df["Close"].shift(1)

    tr1 = df["High"] - df["Low"]
    tr2 = (df["High"] - prev_close).abs()
    tr3 = (df["Low"] - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Handle Real_Body if geometry not pre-computed
    if "Real_Body" in df.columns:
        real_body = df["Real_Body"]
    elif "Body" in df.columns:
        real_body = df["Body"]
    elif "Close" in df.columns and "Open" in df.columns:
        real_body = (df["Close"] - df["Open"]).abs()
    else:
        real_body = pd.Series(0.0, index=df.index)

    # STRICT SHIFT(1) BEFORE ROLLING MEAN
    trailing_atr = true_range.shift(1).rolling(window=window, min_periods=min_periods).mean()
    body_atr_ratio = np.where(trailing_atr > 1e-6, real_body / trailing_atr, 0.0)

    df["Trailing_ATR20"] = trailing_atr
    df["Body_To_ATR"] = body_atr_ratio
    df["Body_ATR_Ratio"] = body_atr_ratio

    return df


def compute_tod_rvol(df: pd.DataFrame, timeframe: str = "1H", window: int = 20, min_periods: int = 3) -> pd.DataFrame:
    """
    Computes Time-of-Day (TOD) Relative Volume (RVOL) for intraday sessions (1H, 2H, 4H)
    and standard trailing volume for interday sessions (1D, 1W, 1MO).
    All rolling volume statistics strictly utilize shift(1) to eliminate lookahead bias.
    """
    df = df.copy()
    tf_upper = timeframe.upper()

    # Standard volume SMA (shifted by 1)
    trailing_vol_sma = df["Volume"].shift(1).rolling(window=window, min_periods=max(min_periods, 5)).mean()
    standard_rvol = np.where(trailing_vol_sma > 0, df["Volume"] / trailing_vol_sma, 0.0)

    df["Trailing_Vol_SMA20"] = trailing_vol_sma
    df["Standard_RVOL"] = standard_rvol

    if tf_upper in ["1H", "2H", "4H"]:
        if "Datetime_NY" in df.columns:
            df["Hour_Of_Day"] = df["Datetime_NY"].dt.hour
        elif "Datetime_UTC" in df.columns:
            df["Hour_Of_Day"] = df["Datetime_UTC"].dt.tz_convert("America/New_York").dt.hour
        else:
            df["Hour_Of_Day"] = 0

        # Group by hour slot and compute shifted rolling average
        tod_vol_sma = df.groupby("Hour_Of_Day")["Volume"].transform(
            lambda s: s.shift(1).rolling(window=window, min_periods=min_periods).mean()
        )
        tod_vol_sma_clean = np.where(tod_vol_sma > 0, tod_vol_sma, trailing_vol_sma)
        tod_rvol = np.where(tod_vol_sma_clean > 0, df["Volume"] / tod_vol_sma_clean, standard_rvol)

        df["TOD_Vol_SMA20"] = tod_vol_sma_clean
        df["TOD_RVOL"] = tod_rvol
        df["RVOL"] = tod_rvol
    else:
        df["Hour_Of_Day"] = 0
        df["TOD_Vol_SMA20"] = trailing_vol_sma
        df["TOD_RVOL"] = standard_rvol
        df["RVOL"] = standard_rvol

    return df


def compute_hardened_features_and_anomalies(
    df: pd.DataFrame,
    timeframe: str,
    min_solid_ratio: float = 0.65,
    max_wick_ratio: float = 0.25,
    min_atr_ratio: float = 1.50,
    min_rvol: float = 1.50,
    min_return_floor: Optional[float] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executes end-to-end non-lookahead feature extraction and candlestick anomaly filtering.

    Criteria for Extreme Candlestick Anomaly:
    1. Solid Body Dominance: Solid_Ratio >= 0.65 AND Max_Wick_Ratio <= 0.25
    2. High Volume Outlier: RVOL (TOD RVOL for intraday) >= 1.50x
    3. Big Volatility Outlier: Body_To_ATR >= 1.50 OR Abs_Body_Return_Pct >= Min_Return_Floor
    4. Valid Direction: Candle_Direction in ['GREEN', 'RED']

    Returns:
        (df_full_valid, df_anomalies)
    """
    df = df.copy()
    tf_upper = timeframe.upper()
    df["Timeframe"] = tf_upper

    # Ensure Julian_Date_UT exists
    if "Julian_Date_UT" not in df.columns:
        df["Julian_Date_UT"] = compute_julian_date(df["Datetime_UTC"])

    # 1. Geometry
    df = compute_candlestick_geometry(df)

    # 2. Trailing ATR (Shifted by 1)
    df = compute_trailing_atr(df, window=20, min_periods=5)

    # 3. TOD RVOL (Shifted by 1)
    df = compute_tod_rvol(df, timeframe=tf_upper, window=20, min_periods=3)

    # 4. Return Floor
    if min_return_floor is None:
        min_return_floor = TIMEFRAME_RETURN_FLOORS.get(tf_upper, 1.0)
    df["Min_Return_Floor"] = min_return_floor

    # 5. Sieve Boolean Masks
    df["is_solid"] = (df["Solid_Ratio"] >= min_solid_ratio) & (df["Max_Wick_Ratio"] <= max_wick_ratio)
    df["is_high_volume"] = df["RVOL"] >= min_rvol
    df["is_big_magnitude"] = (df["Body_To_ATR"] >= min_atr_ratio) | (df["Abs_Body_Return_Pct"] >= min_return_floor)

    df["is_extreme_anomaly"] = (
        df["is_solid"] &
        df["is_high_volume"] &
        df["is_big_magnitude"] &
        df["Candle_Direction"].isin(["GREEN", "RED"])
    )

    # 6. Tier Stratification
    # Tier 2: Super Institutional Thrust (SR >= 0.75, RVOL >= 2.0x, Body/ATR >= 2.0x)
    tier2_mask = (
        df["is_extreme_anomaly"] &
        (df["Solid_Ratio"] >= 0.75) &
        (df["RVOL"] >= 2.0) &
        (df["Body_To_ATR"] >= 2.0)
    )
    df["Anomaly_Tier"] = np.where(tier2_mask, 2, np.where(df["is_extreme_anomaly"], 1, 0))

    # 7. Drop warmup burn-in bars where rolling stats are uninitialized
    valid_mask = df["Trailing_ATR20"].notna() & (df["RVOL"] > 0)
    df_valid = df[valid_mask].copy().reset_index(drop=True)

    anomalies = df_valid[df_valid["is_extreme_anomaly"]].copy().reset_index(drop=True)

    return df_valid, anomalies


def extract_anomalies_for_timeframe(timeframe: str, data_dir: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads market data and extracts anomalies for a single timeframe.
    """
    df_raw = load_market_data_for_timeframe(timeframe, data_dir=data_dir)
    return compute_hardened_features_and_anomalies(df_raw, timeframe=timeframe)


def run_market_data_pipeline(data_dir: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Executes the entire Module 1 pipeline across all 6 timeframes (1H, 2H, 4H, 1D, 1W, 1MO),
    persisting individual timeframe datasets, the master manifest, and summary JSON report.
    """
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    anomalies_dir = os.path.join(data_dir, "anomalies")
    os.makedirs(anomalies_dir, exist_ok=True)

    timeframes = ["1H", "2H", "4H", "1D", "1W", "1MO"]
    all_anomalies = []
    summary_stats = {}

    for tf in timeframes:
        full_df, anom_df = extract_anomalies_for_timeframe(tf, data_dir=data_dir)

        # Save partitioned files in data/ and data/anomalies/ for full compatibility
        tf_lower = tf.lower()
        
        # In data/
        anom_parquet_1 = os.path.join(data_dir, f"spy_anomalies_{tf_lower}.parquet")
        anom_csv_1 = os.path.join(data_dir, f"spy_anomalies_{tf_lower}.csv")
        full_parquet_1 = os.path.join(data_dir, f"spy_full_series_{tf_lower}.parquet")
        
        anom_df.to_parquet(anom_parquet_1, index=False)
        anom_df.to_csv(anom_csv_1, index=False)
        full_df.to_parquet(full_parquet_1, index=False)

        # In data/anomalies/
        anom_parquet_2 = os.path.join(anomalies_dir, f"spy_anomalies_{tf_lower}.parquet")
        anom_csv_2 = os.path.join(anomalies_dir, f"spy_anomalies_{tf_lower}.csv")
        anom_df.to_parquet(anom_parquet_2, index=False)
        anom_df.to_csv(anom_csv_2, index=False)

        all_anomalies.append(anom_df)

        summary_stats[tf] = {
            "total_bars": len(full_df),
            "start_date_ny": str(full_df["Datetime_NY"].iloc[0]),
            "end_date_ny": str(full_df["Datetime_NY"].iloc[-1]),
            "anomaly_count": len(anom_df),
            "green_count": int((anom_df["Candle_Direction"] == "GREEN").sum()) if len(anom_df) > 0 else 0,
            "red_count": int((anom_df["Candle_Direction"] == "RED").sum()) if len(anom_df) > 0 else 0,
            "tier2_super_anomalies": int((anom_df["Anomaly_Tier"] == 2).sum()) if len(anom_df) > 0 else 0,
            "mean_solid_ratio": float(anom_df["Solid_Ratio"].mean()) if len(anom_df) > 0 else 0.0,
            "mean_rvol": float(anom_df["RVOL"].mean()) if len(anom_df) > 0 else 0.0,
            "mean_body_return_pct": float(anom_df["Abs_Body_Return_Pct"].mean()) if len(anom_df) > 0 else 0.0,
        }

    master_manifest = pd.concat(all_anomalies, ignore_index=True)
    master_manifest = master_manifest.sort_values("Datetime_UTC").reset_index(drop=True)

    master_parquet_1 = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
    master_csv_1 = os.path.join(data_dir, "spy_anomalies_master_manifest.csv")
    master_json_1 = os.path.join(data_dir, "spy_anomalies_summary_stats.json")

    master_parquet_2 = os.path.join(anomalies_dir, "master_anomaly_manifest.parquet")
    master_csv_2 = os.path.join(anomalies_dir, "master_anomaly_manifest.csv")

    master_manifest.to_parquet(master_parquet_1, index=False)
    master_manifest.to_csv(master_csv_1, index=False)
    master_manifest.to_parquet(master_parquet_2, index=False)
    master_manifest.to_csv(master_csv_2, index=False)

    with open(master_json_1, "w") as f:
        json.dump(summary_stats, f, indent=2)

    return master_manifest, summary_stats
