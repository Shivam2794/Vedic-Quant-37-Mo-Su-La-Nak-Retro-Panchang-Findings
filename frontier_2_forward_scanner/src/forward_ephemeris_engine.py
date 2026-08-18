"""
FORWARD 2026–2027 EPHEMERIS ENGINE
==================================
Generates high-precision Swiss Ephemeris 13-pillar Omni-Vedic feature matrices
for all NYSE trading days and intraday market sessions across 2026–2027.

Key Capabilities:
  1. Generates continuous RTH timestamps (Daily @ 09:30 EST and Hourly RTH sessions).
  2. Filters US market holidays (NYSE calendar).
  3. Computes 543 continuous & discrete 13-pillar features per timestamp.
  4. Guarantees 100% mathematical invariants (SAV=337, Jaimini 1-to-1, 0 NaNs).
  5. Outputs data/forward_ephemeris_2026_2027_supreme.parquet.
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
import datetime
from tqdm import tqdm

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.vedic_astrology.omni_vedic_fusion import extract_omni_vedic_row
from src.market_data.data_ingestion import compute_julian_date

# US NYSE Official Market Holidays (2026 & 2027)
NYSE_HOLIDAYS = {
    # 2026
    datetime.date(2026, 1, 1),   # New Year's Day
    datetime.date(2026, 1, 19),  # Martin Luther King Jr. Day
    datetime.date(2026, 2, 16),  # Washington's Birthday (Presidents' Day)
    datetime.date(2026, 4, 3),   # Good Friday
    datetime.date(2026, 5, 25),  # Memorial Day
    datetime.date(2026, 6, 19),  # Juneteenth National Independence Day
    datetime.date(2026, 7, 3),   # Independence Day (Observed)
    datetime.date(2026, 9, 7),   # Labor Day
    datetime.date(2026, 11, 26), # Thanksgiving Day
    datetime.date(2026, 12, 25), # Christmas Day
    # 2027
    datetime.date(2027, 1, 1),   # New Year's Day
    datetime.date(2027, 1, 18),  # Martin Luther King Jr. Day
    datetime.date(2027, 2, 15),  # Washington's Birthday
    datetime.date(2027, 3, 26),  # Good Friday
    datetime.date(2027, 5, 31),  # Memorial Day
    datetime.date(2027, 6, 18),  # Juneteenth (Observed)
    datetime.date(2027, 7, 5),   # Independence Day (Observed)
    datetime.date(2027, 9, 6),   # Labor Day
    datetime.date(2027, 11, 25), # Thanksgiving Day
    datetime.date(2027, 12, 24), # Christmas Day (Observed)
}


def generate_nyse_forward_timestamps(
    start_date: str = "2026-01-01",
    end_date: str = "2027-12-31",
    include_hourly: bool = True,
) -> pd.DataFrame:
    """
    Generates regular trading hours (RTH) timestamps for all NYSE trading days
    in 2026 and 2027, localized to America/New_York and converted to UTC.
    """
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    all_dates = pd.date_range(start_dt, end_dt, freq="D")

    trading_dates = [d.date() for d in all_dates if d.weekday() < 5 and d.date() not in NYSE_HOLIDAYS]
    logger.info(f"Generated {len(trading_dates)} active NYSE trading days for {start_date} to {end_date}.")

    timestamps_ny = []
    horizons = []

    for d in trading_dates:
        daily_dt = pd.Timestamp(f"{d} 09:30:00", tz="America/New_York")
        timestamps_ny.append(daily_dt)
        horizons.append("Daily_Open")

        if include_hourly:
            for hour_str in ["10:30:00", "11:30:00", "12:30:00", "13:30:00", "14:30:00", "15:30:00"]:
                hourly_dt = pd.Timestamp(f"{d} {hour_str}", tz="America/New_York")
                timestamps_ny.append(hourly_dt)
                horizons.append("Intraday_RTH")

    df_time = pd.DataFrame({
        "Datetime_NY": timestamps_ny,
        "Horizon_Type": horizons,
    })
    df_time["Datetime_UTC"] = df_time["Datetime_NY"].dt.tz_convert("UTC")
    df_time["Julian_Date_UT"] = compute_julian_date(df_time["Datetime_UTC"])
    df_time["Year"] = df_time["Datetime_NY"].dt.year
    df_time["Month"] = df_time["Datetime_NY"].dt.month
    df_time["Day"] = df_time["Datetime_NY"].dt.day
    df_time["Hour"] = df_time["Datetime_NY"].dt.hour
    df_time["Date_Str"] = df_time["Datetime_NY"].dt.strftime("%Y-%m-%d")
    df_time["Time_Str"] = df_time["Datetime_NY"].dt.strftime("%H:%M:%S")

    return df_time.sort_values("Datetime_UTC").reset_index(drop=True)


def build_forward_ephemeris_matrix(
    output_path: str = "data/forward_ephemeris_2026_2027_supreme.parquet",
    include_hourly: bool = True,
) -> pd.DataFrame:
    """
    Generates and enriches the full forward 2026–2027 ephemeris matrix with all 13 Vedic pillars.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logger.info("Generating forward NYSE trading timestamps (2026–2027)...")

    df_base = generate_nyse_forward_timestamps(start_date="2026-01-01", end_date="2027-12-31", include_hourly=include_hourly)
    logger.info(f"Generated {len(df_base)} forward timestamps. Invoking extract_omni_vedic_row...")

    enriched_records: List[Dict[str, Any]] = []

    for _, row in tqdm(df_base.iterrows(), total=len(df_base), desc="Computing 2026-2027 Ephemeris"):
        rec = row.to_dict()
        jd = float(rec["Julian_Date_UT"])
        astro_feats = extract_omni_vedic_row(jd)
        rec.update(astro_feats)
        enriched_records.append(rec)

    df_enriched = pd.DataFrame(enriched_records)

    # Invariant checks
    assert df_enriched.isnull().sum().sum() == 0, f"Forward matrix contains NaNs! {df_enriched.isnull().sum()[df_enriched.isnull().sum() > 0]}"
    assert (df_enriched["SAV_Total"] == 337).all(), "SAV Total != 337 invariant failure in forward matrix!"

    # Jaimini 1-to-1 uniqueness check
    karaka_cols = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    for _, row in df_enriched.iterrows():
        karakas = [row[f"Jaimini_{k}"] for k in karaka_cols]
        assert len(set(karakas)) == 7, f"Jaimini Karakas not 1-to-1 unique at {row['Datetime_UTC']}"

    df_enriched.to_parquet(output_path, compression="snappy", index=False)
    logger.info(f"Forward Ephemeris Matrix successfully written to {output_path} ({df_enriched.shape[0]} rows x {df_enriched.shape[1]} cols).")
    return df_enriched


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    build_forward_ephemeris_matrix()
