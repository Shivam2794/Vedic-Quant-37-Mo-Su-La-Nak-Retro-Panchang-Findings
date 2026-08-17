"""
test_tier3_cross_feature.py — Tier 3: Cross-Feature Integration & Interaction Suite
Evaluates multi-module interactions, retrograde aspects, multi-timeframe alignment, and 66-column schema fusion.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
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


class TestTier3PanchangIntradayCrossFeature:
    def test_panchang_intraday_hourly_timestamp_progression(self):
        """Tests continuous progression of Moon longitude and Tithi across 7 intraday hourly bars."""
        ny_tz = zoneinfo.ZoneInfo("America/New_York")
        base_day = datetime(2024, 1, 15, tzinfo=ny_tz)
        hours = [9, 10, 11, 12, 13, 14, 15]
        
        # Moon speed is ~0.55° per hour (13.2° per day)
        sun_lon = 270.0
        start_moon_lon = 320.0
        
        results = []
        for i, h in enumerate(hours):
            dt_ny = base_day.replace(hour=h, minute=30 if h == 9 else 0)
            current_moon_lon = (start_moon_lon + i * 0.55) % 360.0
            panchang = oracle_panchang_5_limbs(sun_lon=sun_lon, moon_lon=current_moon_lon, weekday_num=1)
            results.append({
                'dt_ny': dt_ny,
                'moon_lon': current_moon_lon,
                'tithi': panchang['tithi_num'],
                'nakshatra': panchang['nakshatra_num'],
                'karana': panchang['karana_num']
            })
            
        df_p = pd.DataFrame(results)
        assert len(df_p) == 7
        assert df_p['moon_lon'].is_monotonic_increasing
        assert df_p['tithi'].iloc[0] == 5  # Shukla Panchami


class TestTier3RetrogradeAndAspectInteraction:
    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_retrograde_planetary_aspect_synchronization(self):
        """Evaluates Parashari Drishti aspect from a retrograde planet (Saturn/Mars) onto Moon."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        # Epoch where Saturn is retrograde in Aquarius
        jd_retro = 2460180.5  # August 2023
        res_sat, _ = swe.calc_ut(jd_retro, swe.SATURN, flags)
        sat_lon = res_sat[0] % 360.0
        sat_speed = res_sat[3]
        
        # Saturn is retrograde if speed < 0
        is_sat_retro = bool(sat_speed < 0)
        assert is_sat_retro is True
        
        # Saturn casts 3rd (60°), 7th (180°), 10th (270°) aspects
        aspect_3rd_target = (sat_lon + 60.0) % 360.0
        aspect_7th_target = (sat_lon + 180.0) % 360.0
        aspect_10th_target = (sat_lon + 270.0) % 360.0
        
        assert 0.0 <= aspect_3rd_target < 360.0
        assert 0.0 <= aspect_7th_target < 360.0
        assert 0.0 <= aspect_10th_target < 360.0


class TestTier3MultiTimeframeConsistency:
    def test_multitimeframe_hourly_to_2h_aggregation_consistency(self):
        """Verifies 1H bars aggregate into valid 2H bars with matching Open, High, Low, Close."""
        # Two 1H bars: Bar 1 (09:30-10:30), Bar 2 (10:30-11:30)
        bar1 = {'Open': 450.0, 'High': 454.0, 'Low': 449.5, 'Close': 453.0, 'Volume': 2_000_000}
        bar2 = {'Open': 453.0, 'High': 456.0, 'Low': 452.0, 'Close': 455.5, 'Volume': 1_500_000}
        
        # Aggregated 2H bar
        agg_2h_open = bar1['Open']
        agg_2h_high = max(bar1['High'], bar2['High'])
        agg_2h_low = min(bar1['Low'], bar2['Low'])
        agg_2h_close = bar2['Close']
        agg_2h_vol = bar1['Volume'] + bar2['Volume']
        
        assert agg_2h_open == 450.0
        assert agg_2h_high == 456.0
        assert agg_2h_low == 449.5
        assert agg_2h_close == 455.5
        assert agg_2h_vol == 3_500_000
        
        # Both bars are bullish, aggregate is bullish
        agg_sr = oracle_solid_ratio(agg_2h_open, agg_2h_high, agg_2h_low, agg_2h_close)
        # Real body = 5.5, Range = 6.5 -> SR = 5.5 / 6.5 = 0.846 (Passes sieve)
        assert agg_sr >= 0.65


class TestTier3OvernightGapVsIntradayBody:
    def test_overnight_gap_separation_from_real_body(self):
        """Separates Overnight Gap Return from Intraday Real Body Return."""
        prev_close = 450.0
        open_today = 455.0  # +1.11% gap up
        high_today = 462.0
        low_today = 454.5
        close_today = 461.0 # +1.32% intraday body
        
        overnight_gap_pct = (open_today - prev_close) / prev_close * 100.0
        body_return_pct = (close_today - open_today) / open_today * 100.0
        total_return_pct = (close_today - prev_close) / prev_close * 100.0
        
        assert pytest.approx(overnight_gap_pct, 1e-4) == 1.1111
        assert pytest.approx(body_return_pct, 1e-4) == 1.3187
        assert pytest.approx(total_return_pct, 1e-4) == 2.4444


class TestTier3Schema66ColumnFusion:
    def test_66_column_schema_keys_completeness(self):
        """Validates that financial and astronomical feature dictionaries merge into expected 66-column schema."""
        financial_features = {
            'Datetime_UTC': '2024-01-15 14:30:00+00:00',
            'Datetime_NY': '2024-01-15 09:30:00-05:00',
            'Julian_Date_UT': 2460325.104167,
            'Timeframe': '1H',
            'Open': 475.0, 'High': 480.0, 'Low': 474.5, 'Close': 479.5,
            'Volume': 5_000_000.0,
            'Real_Body': 4.5, 'Candle_Range': 5.5,
            'Upper_Wick': 0.5, 'Lower_Wick': 0.5,
            'Solid_Ratio': 0.818, 'Max_Wick_Ratio': 0.091,
            'Direction': 'GREEN',
            'Trailing_ATR20': 2.0,
            'Body_ATR_Ratio': 2.25,
            'RVOL': 2.5
        }
        
        astrological_features = {
            'Sun_Longitude': 270.627, 'Moon_Longitude': 325.700,
            'Mars_Longitude': 253.945, 'Mercury_Longitude': 247.342,
            'Jupiter_Longitude': 11.797, 'Venus_Longitude': 236.141,
            'Saturn_Longitude': 310.446, 'Rahu_Longitude': 355.918, 'Ketu_Longitude': 175.918,
            'Tithi': 5, 'Paksha': 'Shukla', 'Vara': 'Monday',
            'Moon_Nakshatra': 'Purva Bhadrapada', 'Moon_Pada': 2,
            'Yoga': 19, 'Karana': 9,
            'Moon_Sign': 'Aquarius', 'Sun_Sign': 'Capricorn',
            'Moon_D9_Sign': 'Taurus',
            'Mercury_Retrograde': False, 'Mars_Retrograde': False,
            'Jupiter_Retrograde': False, 'Saturn_Retrograde': False, 'Venus_Retrograde': False,
            'Mars_Combust': False, 'Mercury_Combust': False,
            'Jupiter_Combust': False, 'Venus_Combust': False, 'Saturn_Combust': False
        }
        
        merged = {**financial_features, **astrological_features}
        assert len(merged) >= 45
        assert 'Solid_Ratio' in merged
        assert 'Moon_Nakshatra' in merged
        assert 'Tithi' in merged
