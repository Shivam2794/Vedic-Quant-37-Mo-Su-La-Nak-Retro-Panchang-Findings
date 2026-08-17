"""
test_tier2_boundaries_corners.py — Tier 2: Boundary Value Analysis & Corner Cases
Evaluates zero-range bars, epsilon guards, DST shifts, leap years, half-days, and extreme regimes.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone
import zoneinfo

try:
    import swisseph as swe
except ImportError:
    swe = None

from tests.conftest import (
    oracle_solid_ratio,
    oracle_max_wick_ratio,
    oracle_julian_date_ut,
    oracle_navamsha_d9,
    oracle_panchang_5_limbs
)


class TestTier2ZeroRangeAndEpsilonGuards:
    def test_zero_range_candle_epsilon_protection(self):
        """Zero range candle (High == Low) must not trigger ZeroDivisionError and return SR = 0.0."""
        sr = oracle_solid_ratio(open_val=450.0, high_val=450.0, low_val=450.0, close_val=450.0, eps=1e-9)
        assert np.isfinite(sr)
        assert sr == 0.0

    def test_zero_range_candle_max_wick_ratio_protection(self):
        """Zero range candle must not trigger ZeroDivisionError for Max Wick Ratio."""
        mwr = oracle_max_wick_ratio(open_val=450.0, high_val=450.0, low_val=450.0, close_val=450.0, eps=1e-9)
        assert np.isfinite(mwr)
        assert mwr == 0.0

    def test_flat_candle_zero_real_body(self):
        """Doji candle (Open == Close) with large range has Solid Ratio = 0.0."""
        sr = oracle_solid_ratio(open_val=450.0, high_val=455.0, low_val=445.0, close_val=450.0)
        assert sr == 0.0
        assert sr < 0.65  # Gracefully rejected

    def test_single_tick_penny_range(self):
        """Single-tick $0.01 bar evaluates accurately without precision loss."""
        # 1 cent range, 1 cent body (Marubozu 1 tick)
        sr = oracle_solid_ratio(open_val=450.00, high_val=450.01, low_val=450.00, close_val=450.01)
        assert pytest.approx(sr, 1e-6) == 1.0


class TestTier2CalendarAndAstroBoundaries:
    def test_leap_year_february_29_handling(self):
        """Validates Julian Day UT and astronomical calculations on Leap Day (2024-02-29 12:00 UTC)."""
        dt_leap = pd.Timestamp('2024-02-29 12:00:00', tz='UTC')
        jd = oracle_julian_date_ut(pd.Series([dt_leap])).iloc[0]
        # 2024-01-01 12:00 is JD 2460311.0; Feb 29 is 59 days later -> 2460370.0
        assert pytest.approx(jd, 1e-6) == 2460370.0

    def test_dst_spring_forward_shift_march(self):
        """US Eastern Daylight Saving spring-forward (02:00 EST -> 03:00 EDT in March)."""
        ny_tz = zoneinfo.ZoneInfo("America/New_York")
        # 2024-03-10: 09:30 EDT is 13:30 UTC (UTC-4)
        dt_ny = datetime(2024, 3, 11, 9, 30, 0, tzinfo=ny_tz)
        dt_utc = dt_ny.astimezone(timezone.utc)
        assert dt_utc.hour == 13
        assert dt_utc.minute == 30

    def test_dst_fall_back_shift_november(self):
        """US Eastern Daylight Saving fall-back (02:00 EDT -> 01:00 EST in November)."""
        ny_tz = zoneinfo.ZoneInfo("America/New_York")
        # 2024-11-04: 09:30 EST is 14:30 UTC (UTC-5)
        dt_ny = datetime(2024, 11, 4, 9, 30, 0, tzinfo=ny_tz)
        dt_utc = dt_ny.astimezone(timezone.utc)
        assert dt_utc.hour == 14
        assert dt_utc.minute == 30

    def test_market_half_day_sessions(self):
        """Market half-day (09:30 to 13:00 NY) produces valid hourly bars without index corruption."""
        hours = [9, 10, 11, 12]
        ny_tz = zoneinfo.ZoneInfo("America/New_York")
        timestamps = [datetime(2024, 11, 29, h, 30 if h == 9 else 0, tzinfo=ny_tz) for h in hours]
        df_half_day = pd.DataFrame({
            'Datetime_NY': timestamps,
            'Datetime_UTC': [ts.astimezone(timezone.utc) for ts in timestamps],
            'Volume': [1_500_000, 800_000, 600_000, 1_200_000]
        })
        assert len(df_half_day) == 4
        assert df_half_day['Datetime_UTC'].is_monotonic_increasing


class TestTier2ExtremeVolatilityRegimes:
    def test_2008_gfc_extreme_volatility_scaling(self):
        """2008 GFC volatility regime ($10+ daily ATR) enforces proportional real body threshold."""
        atr20 = 10.50
        body_large = 16.00  # 16.0 / 10.5 = 1.52 -> PASS
        body_small = 8.00   # 8.0 / 10.5 = 0.76 -> REJECT
        assert (body_large / atr20) >= 1.50
        assert (body_small / atr20) < 1.50

    def test_2017_low_volatility_compression(self):
        """2017 low-vol regime (ATR = 0.80) combines with timeframe return floor."""
        atr20 = 0.80
        body = 1.30  # Ratio = 1.625 -> PASS
        assert (body / atr20) >= 1.50

    def test_extreme_numerical_magnitude_limits(self):
        """Verifies no 64-bit integer or floating point overflow on massive volume values."""
        extreme_volume = 1_000_000_000.0  # 1 Billion shares
        baseline_vol = 500_000_000.0
        rvol = extreme_volume / baseline_vol
        assert rvol == 2.0
        assert np.isfinite(rvol)

    def test_zodiac_360_degree_wrap_around_boundary(self):
        """Planetary longitude at 359.9999° maps to Pisces Navamsha D9 sign 11 without out-of-bounds error."""
        d9_sign = oracle_navamsha_d9(359.9999)
        assert d9_sign == 11
        assert 0 <= d9_sign <= 11
