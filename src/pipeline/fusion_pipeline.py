"""
Unified Feature Alignment & Master Manifest Fusion Pipeline (Module 3).

Connects:
- Module 1 (Market Data Ingestion & Anomaly Sieve):
  `src.market_data.data_ingestion` & `src.market_data.anomaly_sieve`
- Module 2 (Swiss Ephemeris Sidereal Lahiri Vedic Engine):
  `src.vedic_astrology.ephemeris`, `src.vedic_astrology.nakshatra_navamsha`,
  `src.vedic_astrology.panchang`, `src.vedic_astrology.aspects_combustion`

Generates:
- 66-Column Unified Candlestick Anomaly & Astronomical Correlation Feature Matrix
- Partitioned Multi-Timeframe Datasets (1H, 2H, 4H, 1D, 1W, 1MO)
- Master Anomaly Manifest with Exact Row Union Invariant (N = 1,001)
- Extended Multi-Dimensional Astrological Research Matrices
"""

from __future__ import annotations

import os
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from src.market_data.data_ingestion import (
    compute_julian_date,
    load_market_data_for_timeframe,
    load_all_spy_timeframes,
)
from src.market_data.anomaly_sieve import (
    TIMEFRAME_RETURN_FLOORS,
    compute_candlestick_geometry,
    compute_trailing_atr,
    compute_tod_rvol,
    compute_hardened_features_and_anomalies,
    extract_anomalies_for_timeframe,
)
from src.vedic_astrology.ephemeris import (
    calculate_graha_positions_batch,
    timestamps_to_julian_day_array,
    datetime_to_julian_day,
    init_ephemeris,
    GRAHA_NAMES,
)
from src.vedic_astrology.nakshatra_navamsha import (
    get_nakshatra_batch,
    get_navamsha_batch,
    is_gandanta_batch,
)
from src.vedic_astrology.panchang import (
    calculate_panchang_batch,
    get_tithi_info,
    get_karana_name,
)
from src.vedic_astrology.aspects_combustion import (
    calculate_aspects_and_combustion_batch,
    angular_separation_batch,
)
from src.vedic_astrology import calculate_all_vedic_features

logger = logging.getLogger(__name__)

# The Authoritative Canonical 66-Column Unified Feature Schema
CANONICAL_66_COLUMNS: List[str] = [
    # 1-9: Timestamps, Identifiers & Primary OHLCV Prices (9 columns)
    "Datetime_UTC",
    "Datetime_NY",
    "Julian_Date_UT",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Timeframe",
    # 10-22: Candlestick Geometry & Disentangled Return Metrics (13 columns)
    "Body",
    "Range",
    "Solid_Ratio",
    "Upper_Wick",
    "Lower_Wick",
    "Upper_Wick_Ratio",
    "Lower_Wick_Ratio",
    "Max_Wick_Ratio",
    "Direction",
    "Body_Return_Pct",
    "Abs_Body_Return_Pct",
    "Overnight_Gap_Pct",
    "Total_Return_Pct",
    # 23-36: Non-Lookahead Volatility, Volume & Sieve Flags (14 columns)
    "Trailing_ATR20",
    "Body_ATR_Ratio",
    "Trailing_Vol_SMA20",
    "Standard_RVOL",
    "Hour_Of_Day",
    "TOD_Vol_SMA20",
    "TOD_RVOL",
    "RVOL",
    "Min_Return_Floor",
    "is_solid",
    "is_high_volume",
    "is_big_magnitude",
    "is_extreme_anomaly",
    "Anomaly_Tier",
    # 37-46: High-Precision Sidereal Lahiri Planetary Longitudes (10 columns)
    "Julian_Day",
    "Moon_Longitude",
    "Sun_Longitude",
    "Mars_Longitude",
    "Mercury_Longitude",
    "Jupiter_Longitude",
    "Venus_Longitude",
    "Saturn_Longitude",
    "Rahu_Longitude",
    "Ketu_Longitude",
    # 47-53: 5-Limb Vedic Panchang & Nakshatra Placements (7 columns)
    "Tithi",
    "Paksha",
    "Moon_Nakshatra",
    "Moon_Pada",
    "Sun_Nakshatra",
    "Yoga",
    "Karana",
    # 54-56: Zodiac Rasi & Navamsha D9 Chart Placements (3 columns)
    "Moon_Sign",
    "Sun_Sign",
    "Moon_D9_Sign",
    # 57-61: Planetary Retrograde States (5 columns)
    "Mercury_Retrograde",
    "Mars_Retrograde",
    "Jupiter_Retrograde",
    "Saturn_Retrograde",
    "Venus_Retrograde",
    # 62-66: Astangata Planetary Combustion Flags (5 columns)
    "Mars_Combust",
    "Mercury_Combust",
    "Jupiter_Combust",
    "Venus_Combust",
    "Saturn_Combust",
]


def align_anomalies_with_vedic_astrology(
    df_anomalies: pd.DataFrame,
    node_mode: str = "true",
    orb_deg: float = 12.0,
) -> pd.DataFrame:
    """
    Synchronizes candlestick anomalies with high-precision Swiss Ephemeris astronomical positions.

    Computes:
    - 9 Graha sidereal Lahiri longitudes, latitudes, speeds, retrogrades
    - 5 Panchang limbs (Tithi, Vara, Nakshatra, Yoga, Karana)
    - 27 Nakshatras & 108 Padas (Sun & Moon)
    - Navamsha D9 divisional chart signs
    - Parashari Drishti planetary aspects
    - Astangata combustion states

    Parameters
    ----------
    df_anomalies : pd.DataFrame
        Market anomaly dataframe containing Datetime_UTC or Julian_Date_UT.
    node_mode : str
        'true' for True Lunar Node or 'mean' for Mean Node (default: 'true').
    orb_deg : float
        Angular orb in degrees for aspect strength scores (default: 12.0).

    Returns
    -------
    pd.DataFrame
        DataFrame with full market anomaly fields joined with all Vedic astronomical features.
    """
    if len(df_anomalies) == 0:
        return pd.DataFrame()

    df = df_anomalies.copy().reset_index(drop=True)

    # 1. Resolve Julian Day UT numbers with microsecond precision
    if "Julian_Date_UT" in df.columns:
        jds = df["Julian_Date_UT"].to_numpy(dtype=np.float64)
    elif "Datetime_UTC" in df.columns:
        jds = compute_julian_date(df["Datetime_UTC"]).to_numpy(dtype=np.float64)
        df["Julian_Date_UT"] = jds
    elif "Datetime" in df.columns:
        jds = compute_julian_date(df["Datetime"]).to_numpy(dtype=np.float64)
        df["Julian_Date_UT"] = jds
    else:
        raise ValueError("Anomaly DataFrame must contain 'Julian_Date_UT', 'Datetime_UTC', or 'Datetime'.")

    # 2. Swiss Ephemeris Sidereal Lahiri 9 Grahas Batch Computation
    df_grahas = calculate_graha_positions_batch(jds, node_mode=node_mode)

    # 3. 5 Panchang Limbs
    df_panchang = calculate_panchang_batch(
        sun_lons=df_grahas["Sun_Lon"],
        moon_lons=df_grahas["Moon_Lon"],
        jds_ut=jds,
    )

    # 4. Sun & Moon Nakshatras and Navamsha D9 Chart
    df_sun_nak = get_nakshatra_batch(df_grahas["Sun_Lon"])
    df_moon_nav = get_navamsha_batch(df_grahas["Moon_Lon"])
    df_sun_nav = get_navamsha_batch(df_grahas["Sun_Lon"])

    # 5. Parashari Drishti Aspects & Astangata Combustion
    df_aspects = calculate_aspects_and_combustion_batch(df_grahas, orb_deg=orb_deg)

    # 6. Assemble complete Vedic feature block
    vedic_data = {
        "Julian_Day": jds,
        "Moon_Longitude": df_grahas["Moon_Lon"],
        "Sun_Longitude": df_grahas["Sun_Lon"],
        "Mars_Longitude": df_grahas["Mars_Lon"],
        "Mercury_Longitude": df_grahas["Mercury_Lon"],
        "Jupiter_Longitude": df_grahas["Jupiter_Lon"],
        "Venus_Longitude": df_grahas["Venus_Lon"],
        "Saturn_Longitude": df_grahas["Saturn_Lon"],
        "Rahu_Longitude": df_grahas["Rahu_Lon"],
        "Ketu_Longitude": df_grahas["Ketu_Lon"],
        # Panchang
        "Tithi": df_panchang["Tithi_Num"],
        "Paksha": df_panchang["Paksha"],
        "Moon_Nakshatra": df_panchang["Moon_Nakshatra_Name"],
        "Moon_Pada": df_panchang["Moon_Pada"],
        "Sun_Nakshatra": df_sun_nak["Nakshatra_Name"],
        "Yoga": df_panchang["Yoga_Num"],
        "Karana": df_panchang["Karana_Num"],
        # Zodiac Signs
        "Moon_Sign": df_moon_nav["Rasi_Sign_Name"],
        "Sun_Sign": df_sun_nav["Rasi_Sign_Name"],
        "Moon_D9_Sign": df_moon_nav["Navamsha_Sign_Name"],
        # Retrograde States
        "Mercury_Retrograde": df_grahas["Mercury_Retrograde"],
        "Mars_Retrograde": df_grahas["Mars_Retrograde"],
        "Jupiter_Retrograde": df_grahas["Jupiter_Retrograde"],
        "Saturn_Retrograde": df_grahas["Saturn_Retrograde"],
        "Venus_Retrograde": df_grahas["Venus_Retrograde"],
        # Combustion States
        "Mars_Combust": df_aspects["Mars_Combust"],
        "Mercury_Combust": df_aspects["Mercury_Combust"],
        "Jupiter_Combust": df_aspects["Jupiter_Combust"],
        "Venus_Combust": df_aspects["Venus_Combust"],
        "Saturn_Combust": df_aspects["Saturn_Combust"],
    }
    df_vedic_block = pd.DataFrame(vedic_data)

    # Merge market anomaly fields with astrological feature block
    fused_df = pd.concat([df, df_vedic_block], axis=1)
    return fused_df


def build_66_column_feature_matrix(
    df_anomalies: pd.DataFrame,
    node_mode: str = "true",
    orb_deg: float = 12.0,
) -> pd.DataFrame:
    """
    Transforms market anomaly DataFrame into the exact 66-column canonical feature schema.

    Enforces:
    - 100% column presence matching CANONICAL_66_COLUMNS
    - Normalized column names and bidirectional aliases
    - Zero NaNs across all critical price, volume, and astronomical fields
    - Monotonic UTC timestamp ordering

    Parameters
    ----------
    df_anomalies : pd.DataFrame
        Extracted market anomalies dataframe.
    node_mode : str
        'true' or 'mean' node.
    orb_deg : float
        Aspect orb in degrees.

    Returns
    -------
    pd.DataFrame
        66-column DataFrame adhering strictly to the system interface contract.
    """
    if len(df_anomalies) == 0:
        return pd.DataFrame(columns=CANONICAL_66_COLUMNS)

    df = df_anomalies.copy().reset_index(drop=True)

    # 1. Ensure all financial alias columns exist
    if "Body" not in df.columns and "Real_Body" in df.columns:
        df["Body"] = df["Real_Body"]
    elif "Real_Body" not in df.columns and "Body" in df.columns:
        df["Real_Body"] = df["Body"]

    if "Range" not in df.columns and "Candle_Range" in df.columns:
        df["Range"] = df["Candle_Range"]
    elif "Candle_Range" not in df.columns and "Range" in df.columns:
        df["Candle_Range"] = df["Range"]

    if "Direction" not in df.columns and "Candle_Direction" in df.columns:
        df["Direction"] = df["Candle_Direction"]
    elif "Candle_Direction" not in df.columns and "Direction" in df.columns:
        df["Candle_Direction"] = df["Direction"]

    if "Body_ATR_Ratio" not in df.columns and "Body_To_ATR" in df.columns:
        df["Body_ATR_Ratio"] = df["Body_To_ATR"]
    elif "Body_To_ATR" not in df.columns and "Body_ATR_Ratio" in df.columns:
        df["Body_To_ATR"] = df["Body_ATR_Ratio"]

    # 2. Check if Vedic columns are already present; if not, align them
    has_vedic = (
        "Sun_Longitude" in df.columns and
        "Moon_Longitude" in df.columns and
        "Tithi" in df.columns and
        "Moon_Nakshatra" in df.columns
    )

    if not has_vedic:
        df = align_anomalies_with_vedic_astrology(df, node_mode=node_mode, orb_deg=orb_deg)

    # 3. Ensure Julian_Day exists
    if "Julian_Day" not in df.columns:
        df["Julian_Day"] = df["Julian_Date_UT"]

    # 4. Reorder and filter strictly to CANONICAL_66_COLUMNS
    for col in CANONICAL_66_COLUMNS:
        if col not in df.columns:
            raise KeyError(f"Critical column '{col}' is missing from fused anomaly dataset.")

    df_66 = df[CANONICAL_66_COLUMNS].copy()

    # 5. Enforce monotonic ordering by Datetime_UTC
    df_66 = df_66.sort_values("Datetime_UTC").reset_index(drop=True)
    return df_66


def build_extended_unified_matrix(
    df_anomalies: pd.DataFrame,
    node_mode: str = "true",
    orb_deg: float = 12.0,
) -> pd.DataFrame:
    """
    Builds the rich 152+ column unified research dataset containing all financial metrics,
    full 9 Grahas speeds/latitudes/distances, Gandanta junctions, Vargottama flags,
    and continuous Parashari Drishti aspect scores.

    Parameters
    ----------
    df_anomalies : pd.DataFrame
        Extracted market anomalies dataframe.

    Returns
    -------
    pd.DataFrame
        Comprehensive multi-dimensional research matrix.
    """
    if len(df_anomalies) == 0:
        return pd.DataFrame()

    df = df_anomalies.copy().reset_index(drop=True)
    if "Julian_Date_UT" not in df.columns:
        df["Julian_Date_UT"] = compute_julian_date(df["Datetime_UTC"])

    jds = df["Julian_Date_UT"].to_numpy(dtype=np.float64)
    df_vedic_all = calculate_all_vedic_features(jds, node_mode=node_mode, orb_deg=orb_deg)

    # Drop duplicate Julian_Date_UT if already present
    if "Julian_Date_UT" in df_vedic_all.columns:
        df_vedic_all = df_vedic_all.drop(columns=["Julian_Date_UT"])

    extended_df = pd.concat([df, df_vedic_all], axis=1)
    extended_df = extended_df.sort_values("Datetime_UTC").reset_index(drop=True)
    return extended_df


def extract_and_fuse_timeframe(
    timeframe: str,
    data_dir: Optional[str] = None,
    node_mode: str = "true",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads raw market data, extracts anomalies, and constructs the 66-column feature matrix
    for a single timeframe.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (df_full_valid, df_anomalies_financial, df_anomalies_66col)
    """
    tf_upper = timeframe.upper()
    df_valid, df_anomalies = extract_anomalies_for_timeframe(tf_upper, data_dir=data_dir)
    df_66 = build_66_column_feature_matrix(df_anomalies, node_mode=node_mode)
    return df_valid, df_anomalies, df_66


def run_fusion_pipeline(
    data_dir: Optional[str] = None,
    node_mode: str = "true",
) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Executes the end-to-end Feature Alignment and Master Manifest Fusion Pipeline
    across all 6 historical SPY timeframes (1H, 2H, 4H, 1D, 1W, 1MO).

    Returns
    -------
    Tuple[Dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, Dict[str, Any]]
        - timeframe_anomalies: Dict mapping timeframe string ('1H'..'1MO') to 40-col anomaly DataFrame
        - master_manifest: Unified union DataFrame with 40 financial columns (N = 1,001 rows)
        - vedic_enriched_manifest: Unified 66-column feature matrix (N = 1,001 rows)
        - summary_stats: JSON-serializable dictionary with comprehensive validation metrics
    """
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), "data")

    timeframes = ["1H", "2H", "4H", "1D", "1W", "1MO"]
    timeframe_anomalies: Dict[str, pd.DataFrame] = {}
    timeframe_66col: Dict[str, pd.DataFrame] = {}
    full_series_dict: Dict[str, pd.DataFrame] = {}
    summary_stats: Dict[str, Any] = {}

    total_extracted_anomalies = 0

    for tf in timeframes:
        logger.info(f"Processing timeframe {tf}...")
        df_valid, anom_df, df_66 = extract_and_fuse_timeframe(tf, data_dir=data_dir, node_mode=node_mode)

        timeframe_anomalies[tf] = anom_df
        timeframe_66col[tf] = df_66
        full_series_dict[tf] = df_valid

        count = len(anom_df)
        total_extracted_anomalies += count

        summary_stats[tf] = {
            "total_bars": len(df_valid),
            "start_date_utc": str(df_valid["Datetime_UTC"].iloc[0]) if len(df_valid) > 0 else "",
            "end_date_utc": str(df_valid["Datetime_UTC"].iloc[-1]) if len(df_valid) > 0 else "",
            "start_date_ny": str(df_valid["Datetime_NY"].iloc[0]) if len(df_valid) > 0 else "",
            "end_date_ny": str(df_valid["Datetime_NY"].iloc[-1]) if len(df_valid) > 0 else "",
            "anomaly_count": count,
            "green_count": int((anom_df["Candle_Direction"] == "GREEN").sum()) if count > 0 else 0,
            "red_count": int((anom_df["Candle_Direction"] == "RED").sum()) if count > 0 else 0,
            "tier2_super_anomalies": int((anom_df["Anomaly_Tier"] == 2).sum()) if count > 0 else 0,
            "mean_solid_ratio": float(anom_df["Solid_Ratio"].mean()) if count > 0 else 0.0,
            "min_solid_ratio": float(anom_df["Solid_Ratio"].min()) if count > 0 else 0.0,
            "mean_rvol": float(anom_df["RVOL"].mean()) if count > 0 else 0.0,
            "min_rvol": float(anom_df["RVOL"].min()) if count > 0 else 0.0,
            "mean_body_return_pct": float(anom_df["Abs_Body_Return_Pct"].mean()) if count > 0 else 0.0,
        }

    # Assembling Master Anomaly Manifest (Financial 40-col union)
    master_manifest = pd.concat(list(timeframe_anomalies.values()), ignore_index=True)
    master_manifest = master_manifest.sort_values("Datetime_UTC").reset_index(drop=True)

    # Assembling Complete 66-Column Vedic Enriched Manifest
    vedic_enriched_manifest = build_66_column_feature_matrix(master_manifest, node_mode=node_mode)

    # Invariant Verification
    assert len(master_manifest) == total_extracted_anomalies, (
        f"Master manifest row count ({len(master_manifest)}) does not match sum of timeframe counts ({total_extracted_anomalies})"
    )
    assert len(vedic_enriched_manifest) == total_extracted_anomalies, (
        f"Enriched manifest row count ({len(vedic_enriched_manifest)}) does not match total anomaly count ({total_extracted_anomalies})"
    )

    summary_stats["total_anomalies"] = total_extracted_anomalies
    summary_stats["master_union_verified"] = bool(total_extracted_anomalies == len(master_manifest) == 1001)
    summary_stats["canonical_columns_count"] = len(CANONICAL_66_COLUMNS)

    return timeframe_anomalies, master_manifest, vedic_enriched_manifest, summary_stats
