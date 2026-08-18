"""
ADVERSARIAL EMPIRICAL STRESS TEST SUITE: FORWARD EPHEMERIS & CALENDAR ENGINE
=============================================================================
Executed by Challenger 1 (Adversarial Stress Tester)
Target: src/calendar/forward_ephemeris_engine.py and data/forward_ephemeris_2026_2027_supreme.parquet

Probes:
  1. Daylight Savings Time (DST) transitions (March & November for 2026 and 2027) + RTH alignment.
  2. Holiday edge cases (Good Friday, Juneteenth, July 4th, Christmas, New Year's) & 0 weekend leaks.
  3. Invariant Stress Test: sum(SAV) == 337, Jaimini 7-Karaka set size == 7, Topocentric Lagna in [0, 360).
  4. Boundary/NaN probe: 0 NaNs, 0 Infs, 0 uninitialized values across all 512+ columns.
"""

import pytest
import os
import datetime
import numpy as np
import pandas as pd

from src.calendar.forward_ephemeris_engine import (
    generate_nyse_forward_timestamps,
    build_forward_ephemeris_matrix,
    NYSE_HOLIDAYS,
)
from src.market_data.data_ingestion import compute_julian_date


@pytest.fixture(scope="module")
def ephemeris_df():
    path = "data/forward_ephemeris_2026_2027_supreme.parquet"
    if not os.path.exists(path):
        return build_forward_ephemeris_matrix(output_path=path, include_hourly=True)
    return pd.read_parquet(path)


# =============================================================================
# 1. DAYLIGHT SAVINGS TIME (DST) STRESS TESTS
# =============================================================================
class TestAdversarialDSTTransitions:
    """Stress tests exact boundary transitions in March and November for 2026 and 2027."""

    def test_dst_transition_march_2026(self, ephemeris_df):
        """
        DST Starts Sunday, March 8, 2026.
        Prior trading day: Friday, March 6, 2026 (EST, UTC-5).
        Next trading day: Monday, March 9, 2026 (EDT, UTC-4).
        """
        df_pre = ephemeris_df[ephemeris_df["Date_Str"] == "2026-03-06"].sort_values("Hour")
        df_post = ephemeris_df[ephemeris_df["Date_Str"] == "2026-03-09"].sort_values("Hour")

        assert len(df_pre) == 7, f"Expected 7 bars on 2026-03-06, found {len(df_pre)}"
        assert len(df_post) == 7, f"Expected 7 bars on 2026-03-09, found {len(df_post)}"

        # Pre-DST: 09:30 EST = 14:30 UTC
        open_pre = df_pre[df_pre["Hour"] == 9].iloc[0]
        dt_pre_utc = pd.to_datetime(open_pre["Datetime_UTC"])
        assert dt_pre_utc.hour == 14 and dt_pre_utc.minute == 30, (
            f"Pre-DST Open mismatch: expected 14:30 UTC, got {dt_pre_utc}"
        )

        # Post-DST: 09:30 EDT = 13:30 UTC
        open_post = df_post[df_post["Hour"] == 9].iloc[0]
        dt_post_utc = pd.to_datetime(open_post["Datetime_UTC"])
        assert dt_post_utc.hour == 13 and dt_post_utc.minute == 30, (
            f"Post-DST Open mismatch: expected 13:30 UTC, got {dt_post_utc}"
        )

    def test_dst_transition_november_2026(self, ephemeris_df):
        """
        DST Ends Sunday, November 1, 2026.
        Prior trading day: Friday, October 30, 2026 (EDT, UTC-4).
        Next trading day: Monday, November 2, 2026 (EST, UTC-5).
        """
        df_pre = ephemeris_df[ephemeris_df["Date_Str"] == "2026-10-30"].sort_values("Hour")
        df_post = ephemeris_df[ephemeris_df["Date_Str"] == "2026-11-02"].sort_values("Hour")

        assert len(df_pre) == 7, f"Expected 7 bars on 2026-10-30, found {len(df_pre)}"
        assert len(df_post) == 7, f"Expected 7 bars on 2026-11-02, found {len(df_post)}"

        # Pre-switch: 09:30 EDT = 13:30 UTC
        open_pre = df_pre[df_pre["Hour"] == 9].iloc[0]
        dt_pre_utc = pd.to_datetime(open_pre["Datetime_UTC"])
        assert dt_pre_utc.hour == 13 and dt_pre_utc.minute == 30, (
            f"Pre-Fall-Back Open mismatch: expected 13:30 UTC, got {dt_pre_utc}"
        )

        # Post-switch: 09:30 EST = 14:30 UTC
        open_post = df_post[df_post["Hour"] == 9].iloc[0]
        dt_post_utc = pd.to_datetime(open_post["Datetime_UTC"])
        assert dt_post_utc.hour == 14 and dt_post_utc.minute == 30, (
            f"Post-Fall-Back Open mismatch: expected 14:30 UTC, got {dt_post_utc}"
        )

    def test_dst_transition_march_2027(self, ephemeris_df):
        """
        DST Starts Sunday, March 14, 2027.
        Prior trading day: Friday, March 12, 2027 (EST, UTC-5).
        Next trading day: Monday, March 15, 2027 (EDT, UTC-4).
        """
        df_pre = ephemeris_df[ephemeris_df["Date_Str"] == "2027-03-12"].sort_values("Hour")
        df_post = ephemeris_df[ephemeris_df["Date_Str"] == "2027-03-15"].sort_values("Hour")

        assert len(df_pre) == 7
        assert len(df_post) == 7

        # Pre-DST: 09:30 EST = 14:30 UTC
        open_pre = df_pre[df_pre["Hour"] == 9].iloc[0]
        dt_pre_utc = pd.to_datetime(open_pre["Datetime_UTC"])
        assert dt_pre_utc.hour == 14 and dt_pre_utc.minute == 30

        # Post-DST: 09:30 EDT = 13:30 UTC
        open_post = df_post[df_post["Hour"] == 9].iloc[0]
        dt_post_utc = pd.to_datetime(open_post["Datetime_UTC"])
        assert dt_post_utc.hour == 13 and dt_post_utc.minute == 30

    def test_dst_transition_november_2027(self, ephemeris_df):
        """
        DST Ends Sunday, November 7, 2027.
        Prior trading day: Friday, November 5, 2027 (EDT, UTC-4).
        Next trading day: Monday, November 8, 2027 (EST, UTC-5).
        """
        df_pre = ephemeris_df[ephemeris_df["Date_Str"] == "2027-11-05"].sort_values("Hour")
        df_post = ephemeris_df[ephemeris_df["Date_Str"] == "2027-11-08"].sort_values("Hour")

        assert len(df_pre) == 7
        assert len(df_post) == 7

        # Pre-switch: 09:30 EDT = 13:30 UTC
        open_pre = df_pre[df_pre["Hour"] == 9].iloc[0]
        dt_pre_utc = pd.to_datetime(open_pre["Datetime_UTC"])
        assert dt_pre_utc.hour == 13 and dt_pre_utc.minute == 30

        # Post-switch: 09:30 EST = 14:30 UTC
        open_post = df_post[df_post["Hour"] == 9].iloc[0]
        dt_post_utc = pd.to_datetime(open_post["Datetime_UTC"])
        assert dt_post_utc.hour == 14 and dt_post_utc.minute == 30

    def test_rth_hours_and_minute_alignment_all_rows(self, ephemeris_df):
        """Asserts all 3,514 rows strictly align to RTH minutes (30) and hours [9..15]."""
        dt_ny = pd.to_datetime(ephemeris_df["Datetime_NY"])
        assert (dt_ny.dt.minute == 30).all(), "Non-30 minute timestamp detected!"
        assert (dt_ny.dt.second == 0).all(), "Non-00 second timestamp detected!"
        valid_hours = {9, 10, 11, 12, 13, 14, 15}
        assert set(dt_ny.dt.hour).issubset(valid_hours), f"Invalid hours detected: {set(dt_ny.dt.hour) - valid_hours}"

    def test_strictly_monotonic_utc_timestamps(self, ephemeris_df):
        """Asserts Datetime_UTC is strictly monotonic increasing with zero duplicates."""
        dt_utc = pd.to_datetime(ephemeris_df["Datetime_UTC"])
        assert dt_utc.is_monotonic_increasing, "Datetime_UTC is not monotonically increasing!"
        assert dt_utc.duplicated().sum() == 0, f"Found {dt_utc.duplicated().sum()} duplicate timestamps!"


# =============================================================================
# 2. HOLIDAY & WEEKEND EDGE CASES
# =============================================================================
class TestAdversarialHolidayEdgeCases:
    """Stress tests holiday exclusions, observation rules, and weekend leak prevention."""

    def test_zero_weekend_leaks(self, ephemeris_df):
        """Asserts exactly 0 Saturdays and 0 Sundays across all 3,514 forward rows."""
        dt_ny = pd.to_datetime(ephemeris_df["Datetime_NY"])
        weekdays = dt_ny.dt.dayofweek
        weekend_rows = ephemeris_df[weekdays >= 5]
        assert len(weekend_rows) == 0, f"CRITICAL: Found {len(weekend_rows)} weekend rows in forward matrix!"

    def test_good_friday_exclusion(self, ephemeris_df):
        """Good Friday 2026 (Apr 3) and 2027 (Mar 26) must be strictly absent."""
        dates = set(ephemeris_df["Date_Str"])
        assert "2026-04-03" not in dates, "Good Friday 2026 leaked into schedule!"
        assert "2027-03-26" not in dates, "Good Friday 2027 leaked into schedule!"

    def test_juneteenth_observed_exclusion(self, ephemeris_df):
        """
        Juneteenth 2026: Fri Jun 19 (actual) -> absent.
        Juneteenth 2027: Sat Jun 19 (actual) -> Fri Jun 18 (observed) -> absent.
        """
        dates = set(ephemeris_df["Date_Str"])
        assert "2026-06-19" not in dates, "Juneteenth 2026 leaked!"
        assert "2027-06-18" not in dates, "Juneteenth Observed 2027 leaked!"
        assert "2027-06-19" not in dates, "Juneteenth Saturday 2027 leaked!"

    def test_independence_day_observed_exclusion(self, ephemeris_df):
        """
        July 4 2026: Saturday -> observed Friday July 3 -> absent.
        July 4 2027: Sunday -> observed Monday July 5 -> absent.
        """
        dates = set(ephemeris_df["Date_Str"])
        assert "2026-07-03" not in dates, "July 4th Observed 2026 (Fri) leaked!"
        assert "2026-07-04" not in dates, "July 4th Saturday 2026 leaked!"
        assert "2027-07-04" not in dates, "July 4th Sunday 2027 leaked!"
        assert "2027-07-05" not in dates, "July 4th Observed 2027 (Mon) leaked!"

    def test_christmas_observed_exclusion(self, ephemeris_df):
        """
        Christmas 2026: Friday Dec 25 -> absent.
        Christmas 2027: Saturday Dec 25 -> observed Friday Dec 24 -> absent.
        """
        dates = set(ephemeris_df["Date_Str"])
        assert "2026-12-25" not in dates, "Christmas 2026 leaked!"
        assert "2027-12-24" not in dates, "Christmas Observed 2027 (Fri) leaked!"
        assert "2027-12-25" not in dates, "Christmas Saturday 2027 leaked!"

    def test_new_years_day_exclusion(self, ephemeris_df):
        """New Year's Day 2026 (Jan 1, Thu) and 2027 (Jan 1, Fri) must be absent."""
        dates = set(ephemeris_df["Date_Str"])
        assert "2026-01-01" not in dates, "New Year's 2026 leaked!"
        assert "2027-01-01" not in dates, "New Year's 2027 leaked!"

    def test_all_official_nyse_holidays_omitted(self, ephemeris_df):
        """Asserts all 20 NYSE holidays defined in NYSE_HOLIDAYS are 100% excluded."""
        dates = set(pd.to_datetime(ephemeris_df["Date_Str"]).dt.date)
        leaks = dates.intersection(NYSE_HOLIDAYS)
        assert len(leaks) == 0, f"Found {len(leaks)} NYSE holidays in trading matrix: {leaks}"

    def test_exact_trading_day_and_row_counts(self, ephemeris_df):
        """
        Asserts exactly 251 trading days in 2026 and 251 in 2027.
        Total trading days = 502.
        Total forward rows = 502 * 7 = 3,514.
        """
        df_2026 = ephemeris_df[ephemeris_df["Year"] == 2026]
        df_2027 = ephemeris_df[ephemeris_df["Year"] == 2027]

        days_2026 = df_2026["Date_Str"].nunique()
        days_2027 = df_2027["Date_Str"].nunique()

        assert days_2026 == 251, f"Expected 251 trading days in 2026, got {days_2026}"
        assert days_2027 == 251, f"Expected 251 trading days in 2027, got {days_2027}"
        assert len(ephemeris_df) == 3514, f"Expected 3,514 total rows, got {len(ephemeris_df)}"


# =============================================================================
# 3. MATHEMATICAL & ASTRONOMICAL INVARIANT STRESS TESTS
# =============================================================================
class TestAdversarialMathematicalInvariants:
    """Stress tests SAV=337, Jaimini 7-Karaka set size=7, Topocentric Lagna bounds."""

    def test_sav_337_invariant_all_3514_rows(self, ephemeris_df):
        """Asserts SAV_Total is strictly 337 on all 3,514 rows."""
        assert (ephemeris_df["SAV_Total"] == 337).all(), (
            f"SAV_Total != 337 failure! Found values: {ephemeris_df['SAV_Total'].unique()}"
        )

        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_cols = [f"SAV_{s}" for s in signs]
        for sc in sign_cols:
            assert sc in ephemeris_df.columns, f"Missing SAV column: {sc}"
            assert (ephemeris_df[sc] >= 0).all() and (ephemeris_df[sc] <= 56).all()
        sign_sum = ephemeris_df[sign_cols].sum(axis=1)
        assert (sign_sum == 337).all(), f"Sum of 12 SAV signs != 337! Found sums: {sign_sum.unique()}"

    def test_jaimini_7_karaka_distinctness_all_3514_rows(self, ephemeris_df):
        """Asserts Jaimini 7-Karaka set size == 7 on all 3,514 rows."""
        karaka_cols = ["Jaimini_AK", "Jaimini_AmK", "Jaimini_BK", "Jaimini_MK", "Jaimini_PK", "Jaimini_GK", "Jaimini_DK"]
        expected_planets = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}

        for idx, row in ephemeris_df.iterrows():
            karakas = [row[col] for col in karaka_cols]
            karaka_set = set(karakas)
            assert len(karaka_set) == 7, (
                f"Row {idx} ({row['Datetime_UTC']}) Jaimini Karakas not distinct: {karakas}"
            )
            assert karaka_set == expected_planets, (
                f"Row {idx} Karaka set mismatch: expected {expected_planets}, got {karaka_set}"
            )

    def test_topocentric_lagna_bounds_and_motion(self, ephemeris_df):
        """Asserts Topocentric Lagna is strictly in [0.0, 360.0) and advances ~15 deg/hr."""
        assert (ephemeris_df["Lagna_NYSE_Lon"] >= 0.0).all(), "Lagna < 0 deg detected!"
        assert (ephemeris_df["Lagna_NYSE_Lon"] < 360.0).all(), "Lagna >= 360 deg detected!"

        # Check intraday direct progression
        for date_str, group in ephemeris_df.groupby("Date_Str"):
            lons = group.sort_values("Hour")["Lagna_NYSE_Lon"].values
            assert len(lons) == 7
            for i in range(len(lons) - 1):
                delta = (lons[i + 1] - lons[i]) % 360.0
                # Lagna advances ~11-26 deg/hr due to Short and Long Ascension at NYC latitude
                assert 5.0 < delta < 30.0, (
                    f"Abnormal intraday Lagna step on {date_str} bar {i}->{i+1}: delta={delta:.2f} deg"
                )

    def test_planetary_longitudes_and_nodal_axis(self, ephemeris_df):
        """Asserts all planetary longitudes in [0, 360) and Rahu-Ketu exact 180 deg opposition."""
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        for p in planets:
            col = f"{p}_Lon"
            assert col in ephemeris_df.columns, f"Missing column: {col}"
            assert (ephemeris_df[col] >= 0.0).all()
            assert (ephemeris_df[col] < 360.0).all()

        # Nodal Axis opposition
        nodal_diff = (ephemeris_df["Ketu_Lon"] - ephemeris_df["Rahu_Lon"]) % 360.0
        assert np.allclose(nodal_diff, 180.0, atol=1e-3), (
            f"Rahu-Ketu not 180 deg opposite! Max diff: {np.max(np.abs(nodal_diff - 180.0))}"
        )


# =============================================================================
# 4. BOUNDARY / NAN / INF PROBE
# =============================================================================
class TestAdversarialBoundaryNaNProbe:
    """Probes all 512+ columns for NaNs, Infs, and uninitialized data."""

    def test_zero_nans_across_entire_matrix(self, ephemeris_df):
        """Asserts 0 NaNs across all columns and rows."""
        total_nans = ephemeris_df.isnull().sum().sum()
        if total_nans > 0:
            nan_cols = ephemeris_df.isnull().sum()[ephemeris_df.isnull().sum() > 0]
            pytest.fail(f"CRITICAL: Found {total_nans} NaNs in columns:\n{nan_cols}")
        assert total_nans == 0

    def test_zero_infs_across_numeric_columns(self, ephemeris_df):
        """Asserts 0 Infs/-Infs across all numeric columns."""
        numeric_df = ephemeris_df.select_dtypes(include=[np.number])
        inf_count = np.isinf(numeric_df.values).sum()
        assert inf_count == 0, f"CRITICAL: Found {inf_count} Inf values in numeric columns!"

    def test_column_count_meets_or_exceeds_specification(self, ephemeris_df):
        """Asserts matrix column count >= 512."""
        assert len(ephemeris_df.columns) >= 512, (
            f"Expected at least 512 columns, found {len(ephemeris_df.columns)}"
        )

    def test_no_uninitialized_string_columns(self, ephemeris_df):
        """Asserts string/object columns contain no empty strings or whitespace-only values."""
        obj_df = ephemeris_df.select_dtypes(include=["object", "string"])
        for col in obj_df.columns:
            empty_count = (obj_df[col] == "").sum()
            assert empty_count == 0, f"Found {empty_count} empty strings in column {col}"
