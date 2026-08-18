"""
UNIT & INTEGRATION TESTS FOR FRONTIER 2 FORWARD SIGNAL SCANNER
==============================================================
Verifies forward timestamp generation, NYSE holiday exclusion,
13-pillar Swiss Ephemeris forward invariants (SAV=337, Jaimini 1-to-1),
and forward predictive signal rule projection.
"""

import pytest
import os
import datetime
import pandas as pd
import numpy as np

from src.calendar.forward_ephemeris_engine import (
    generate_nyse_forward_timestamps,
    build_forward_ephemeris_matrix,
    NYSE_HOLIDAYS
)
from src.calendar.forward_signal_scanner import scan_forward_signals_2026_2027


class TestForwardTimestampEngine:
    """Test Suite for NYSE Forward Calendar Generation."""

    def test_nyse_holiday_and_weekend_exclusion(self):
        """Verifies no weekends or official NYSE holidays are in the timestamp schedule."""
        df_time = generate_nyse_forward_timestamps("2026-01-01", "2026-12-31", include_hourly=False)
        for dt in df_time["Datetime_NY"]:
            assert dt.weekday() < 5, f"Weekend found in trading schedule: {dt}"
            assert dt.date() not in NYSE_HOLIDAYS, f"NYSE Holiday found in trading schedule: {dt.date()}"

    def test_rth_session_hours(self):
        """Verifies hourly session bars fall strictly within NYSE regular trading hours."""
        df_time = generate_nyse_forward_timestamps("2026-01-05", "2026-01-09", include_hourly=True)
        valid_hours = {9, 10, 11, 12, 13, 14, 15}
        for dt in df_time["Datetime_NY"]:
            assert dt.hour in valid_hours, f"Non-RTH hour found: {dt}"

    def test_strictly_monotonic_timestamps(self):
        """Verifies timestamps are strictly increasing with zero duplicates."""
        df_time = generate_nyse_forward_timestamps("2026-01-01", "2026-03-31", include_hourly=True)
        assert df_time["Datetime_UTC"].is_monotonic_increasing
        assert df_time["Datetime_UTC"].duplicated().sum() == 0


class TestForwardEphemerisInvariants:
    """Test Suite for 13-Pillar Forward Ephemeris Matrix."""

    @pytest.fixture(scope="class")
    def forward_matrix(self):
        path = "data/forward_ephemeris_2026_2027_supreme.parquet"
        if not os.path.exists(path):
            return build_forward_ephemeris_matrix(output_path=path, include_hourly=True)
        return pd.read_parquet(path)

    def test_forward_zero_nans(self, forward_matrix):
        """Verifies 100% complete dataset with zero missing values."""
        assert forward_matrix.isnull().sum().sum() == 0

    def test_forward_sav_337_invariant(self, forward_matrix):
        """Verifies total SAV bindu sum equals 337 in 100% of forward timestamps."""
        assert (forward_matrix["SAV_Total"] == 337).all()

    def test_forward_jaimini_7_karaka_uniqueness(self, forward_matrix):
        """Verifies Jaimini 7 Chara Karakas maintain strict 1-to-1 uniqueness."""
        karaka_cols = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        for _, row in forward_matrix.iterrows():
            karakas = [row[f"Jaimini_{k}"] for k in karaka_cols]
            assert len(set(karakas)) == 7

    def test_forward_topocentric_lagna_bounds(self, forward_matrix):
        """Verifies Lagna degree is within 0.0 to 360.0 degrees."""
        assert (forward_matrix["Lagna_NYSE_Lon"] >= 0.0).all()
        assert (forward_matrix["Lagna_NYSE_Lon"] < 360.0).all()


class TestForwardSignalScanner:
    """Test Suite for Forward Rule Projection & Signal Scanner."""

    def test_scanner_generates_valid_signals(self):
        """Verifies scanner produces non-empty, high-conviction forward trading signals."""
        df_sig = scan_forward_signals_2026_2027()
        assert not df_sig.empty
        assert len(df_sig) >= 10
        assert (df_sig["Conviction_Pct"] >= 50.0).all()
        assert (df_sig["Conviction_Pct"] <= 100.0).all()
        assert os.path.exists("reports/forward_2026_2027_astro_quant_calendar.md")
        assert os.path.exists("data/forward_signals_2026_2027_manifest.parquet")
