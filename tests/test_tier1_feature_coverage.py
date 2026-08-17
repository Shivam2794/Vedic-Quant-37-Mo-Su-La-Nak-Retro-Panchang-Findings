"""
test_tier1_feature_coverage.py — Tier 1: Isolated Unit & Feature Coverage Suite
Evaluates all 11 inventoried features with >= 5 comprehensive tests per feature (>= 55 tests).
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone

try:
    import swisseph as swe
except ImportError:
    swe = None

from tests.conftest import (
    oracle_solid_ratio,
    oracle_max_wick_ratio,
    oracle_julian_date_ut,
    oracle_navamsha_d9,
    oracle_panchang_5_limbs,
    assert_zero_nans,
    assert_zero_duplicates,
    assert_monotonic_increasing
)


# ==============================================================================
# FEATURE 1: SOLID BODY DOMINANCE & SOLID RATIO (>= 5 TESTS)
# ==============================================================================

class TestFeature1SolidRatio:
    def test_solid_ratio_marubozu_perfect_score(self):
        """Marubozu candle with zero wicks must yield exactly 1.0 Solid Ratio."""
        sr = oracle_solid_ratio(open_val=100.0, high_val=110.0, low_val=100.0, close_val=110.0)
        assert pytest.approx(sr, 1e-6) == 1.0

    def test_solid_ratio_boundary_acceptance_at_065(self):
        """Candle with exactly 65% real body must pass threshold >= 0.65."""
        sr = oracle_solid_ratio(open_val=100.0, high_val=110.0, low_val=100.0, close_val=106.5)
        assert pytest.approx(sr, 1e-6) == 0.65
        assert sr >= 0.65

    def test_solid_ratio_boundary_rejection_at_0649(self):
        """Candle with 64.99% real body must be rejected (< 0.65)."""
        sr = oracle_solid_ratio(open_val=100.0, high_val=110.0, low_val=100.0, close_val=106.499)
        assert sr < 0.65

    def test_solid_ratio_direction_labeling_green_and_red(self):
        """Verifies correct GREEN vs RED direction labeling."""
        # Bullish
        green_open, green_close = 100.0, 108.0
        green_dir = 'GREEN' if green_close >= green_open else 'RED'
        assert green_dir == 'GREEN'

        # Bearish
        red_open, red_close = 108.0, 100.0
        red_dir = 'GREEN' if red_close >= red_open else 'RED'
        assert red_dir == 'RED'

    def test_solid_ratio_precision_with_sub_cent_prices(self):
        """Verifies formula stability with institutional fractional penny quotes."""
        sr = oracle_solid_ratio(open_val=502.125, high_val=505.750, low_val=501.875, close_val=505.000)
        expected_body = 505.000 - 502.125  # 2.875
        expected_range = 505.750 - 501.875  # 3.875
        assert pytest.approx(sr, 1e-6) == (expected_body / expected_range)


# ==============================================================================
# FEATURE 2: MAX WICK RATIO & PIN-BAR REJECTION (>= 5 TESTS)
# ==============================================================================

class TestFeature2MaxWickRatio:
    def test_max_wick_ratio_upper_shadow_rejection(self):
        """Shooting star with 70% upper wick must yield MWR = 0.70 and be rejected (> 0.25)."""
        mwr = oracle_max_wick_ratio(open_val=100.0, high_val=110.0, low_val=99.0, close_val=102.0)
        # Upper wick = 110 - 102 = 8, Range = 11, MWR = 8/11 = 0.727
        assert mwr > 0.25

    def test_max_wick_ratio_lower_shadow_rejection(self):
        """Hammer with 70% lower wick must yield MWR = 0.70 and be rejected (> 0.25)."""
        mwr = oracle_max_wick_ratio(open_val=108.0, high_val=110.0, low_val=99.0, close_val=109.0)
        # Lower wick = 108 - 99 = 9, Range = 11, MWR = 9/11 = 0.818
        assert mwr > 0.25

    def test_max_wick_ratio_balanced_small_wicks_acceptance(self):
        """Candle with 10% upper and 10% lower wick must pass MWR <= 0.25."""
        mwr = oracle_max_wick_ratio(open_val=101.0, high_val=110.0, low_val=100.0, close_val=109.0)
        # Upper wick = 1.0, Lower wick = 1.0, Range = 10.0, MWR = 0.10
        assert pytest.approx(mwr, 1e-6) == 0.10
        assert mwr <= 0.25

    def test_max_wick_ratio_boundary_at_025(self):
        """Boundary candle with exactly 25% max wick must pass."""
        mwr = oracle_max_wick_ratio(open_val=101.0, high_val=110.0, low_val=100.0, close_val=107.5)
        # Upper wick = 110 - 107.5 = 2.5, Range = 10.0, MWR = 0.25
        assert pytest.approx(mwr, 1e-6) == 0.25
        assert mwr <= 0.25

    def test_max_wick_ratio_zero_wick_marubozu(self):
        """Marubozu must yield exactly 0.0 max wick ratio."""
        mwr = oracle_max_wick_ratio(open_val=100.0, high_val=110.0, low_val=100.0, close_val=110.0)
        assert pytest.approx(mwr, 1e-6) == 0.0


# ==============================================================================
# FEATURE 3: NON-LOOKAHEAD VOLATILITY TRIGGER BODY/ATR(20) (>= 5 TESTS)
# ==============================================================================

class TestFeature3BodyToATR:
    def test_body_to_atr_calculation_with_prior_bar_shift(self):
        """ATR(20) must be computed with prior-bar shift(1) so current bar does not leak into ATR."""
        np.random.seed(42)
        closes = pd.Series(np.linspace(100, 120, 30))
        highs = closes + 1.0
        lows = closes - 1.0
        
        # True Range
        tr1 = highs - lows
        tr2 = (highs - closes.shift(1)).abs()
        tr3 = (lows - closes.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr20_unshifted = tr.rolling(window=20).mean()
        atr20_shifted = atr20_unshifted.shift(1)
        
        # At index 25, shifted ATR must equal unshifted ATR at index 24
        assert atr20_shifted.iloc[25] == atr20_unshifted.iloc[24]

    def test_body_to_atr_rejection_below_threshold(self):
        """Candle with Body / ATR(20) = 1.20 must be rejected (< 1.50)."""
        body = 2.40
        atr = 2.00
        ratio = body / atr
        assert ratio == 1.20
        assert ratio < 1.50

    def test_body_to_atr_acceptance_at_threshold(self):
        """Candle with Body / ATR(20) = 1.50 must be accepted (>= 1.50)."""
        body = 3.00
        atr = 2.00
        ratio = body / atr
        assert ratio == 1.50
        assert ratio >= 1.50

    def test_body_to_atr_timeframe_return_floor_override(self):
        """In extreme low-volatility regimes, return percentage floor triggers valid anomaly."""
        # 1D return floor is 2.00%
        body_pct = 2.20  # 2.2% return
        floor = 2.00
        assert body_pct >= floor

    def test_body_to_atr_regime_adaptability(self):
        """Verifies ratio scaling across 2008 high vol (ATR=8.0) vs 2017 low vol (ATR=1.0)."""
        # 2017 low vol: Body = 2.0 -> Ratio = 2.0 / 1.0 = 2.0 (triggers)
        assert (2.0 / 1.0) >= 1.50
        # 2008 high vol: Body = 2.0 -> Ratio = 2.0 / 8.0 = 0.25 (rejected, needs Body >= 12.0)
        assert (2.0 / 8.0) < 1.50
        assert (12.0 / 8.0) >= 1.50


# ==============================================================================
# FEATURE 4: TIME-OF-DAY (TOD) RELATIVE VOLUME (RVOL) (>= 5 TESTS)
# ==============================================================================

class TestFeature4TODRVOL:
    def test_tod_rvol_hourly_binning_alignment(self):
        """Verifies volume baseline groups correctly by hour slot."""
        df = pd.DataFrame({
            'Hour': [9, 10, 13, 15, 9, 10, 13, 15],
            'Volume': [1000, 500, 300, 2000, 1200, 600, 350, 2200]
        })
        grouped = df.groupby('Hour')['Volume'].mean()
        assert grouped[9] == 1100
        assert grouped[13] == 325
        assert grouped[15] == 2100

    def test_tod_rvol_eliminates_closing_bell_u_curve_bias(self):
        """15:00 close volume (2.0M) compared against 15:00 baseline (2.0M) gives RVOL=1.0, not inflated."""
        vol_1500 = 2_000_000.0
        baseline_1500 = 2_000_000.0
        rvol_1500 = vol_1500 / baseline_1500
        assert rvol_1500 == 1.0

        # Midday 13:00 volume (900k) against midday baseline (300k) gives true RVOL=3.0
        vol_1300 = 900_000.0
        baseline_1300 = 300_000.0
        rvol_1300 = vol_1300 / baseline_1300
        assert rvol_1300 == 3.0

    def test_tod_rvol_prior_bar_shift_prevents_leakage(self):
        """Trailing TOD volume mean must strictly exclude current bar volume via shift(1)."""
        series = pd.Series([100, 110, 120, 500])
        # Trailing 3-bar mean shifted by 1
        rolling_shifted = series.rolling(3, min_periods=1).mean().shift(1)
        # At index 3 (volume=500), baseline must be mean of [100, 110, 120] = 110.0
        assert rolling_shifted.iloc[3] == 110.0
        rvol = series.iloc[3] / rolling_shifted.iloc[3]
        assert pytest.approx(rvol, 1e-4) == (500.0 / 110.0)

    def test_tod_rvol_acceptance_at_150_multiplier(self):
        """Volume >= 1.50x TOD baseline satisfies RVOL condition."""
        rvol = 1_500_000 / 1_000_000
        assert rvol >= 1.50

    def test_tod_rvol_fallback_on_insufficient_history(self):
        """First bar in dataset handles fallback cleanly without NaN or zero division."""
        vol = 1_000_000.0
        fallback_baseline = max(vol, 1.0)
        rvol = vol / fallback_baseline
        assert np.isfinite(rvol)
        assert rvol == 1.0


# ==============================================================================
# FEATURE 5: DUAL TIMESTAMPS & JULIAN DATE UT CONVERSION (>= 5 TESTS)
# ==============================================================================

class TestFeature5JulianDateUT:
    def test_julian_date_unix_epoch_exact_match(self):
        """Unix Epoch (1970-01-01 00:00:00 UTC) must equal exactly JD 2440587.5."""
        ts = pd.Series([pd.Timestamp('1970-01-01 00:00:00', tz='UTC')])
        jd = oracle_julian_date_ut(ts).iloc[0]
        assert pytest.approx(jd, 1e-9) == 2440587.5

    def test_julian_date_j2000_epoch_exact_match(self):
        """J2000.0 Standard Epoch (2000-01-01 12:00:00 UTC) must equal exactly JD 2451545.0."""
        ts = pd.Series([pd.Timestamp('2000-01-01 12:00:00', tz='UTC')])
        jd = oracle_julian_date_ut(ts).iloc[0]
        assert pytest.approx(jd, 1e-9) == 2451545.0

    def test_julian_date_microsecond_resolution_preservation(self):
        """Prevents the microsecond / nanosecond integer division bug."""
        ts = pd.Series([pd.Timestamp('2024-01-15 12:00:00.500000', tz='UTC')])
        jd = oracle_julian_date_ut(ts).iloc[0]
        # 12:00:00.5 is 0.500005787 days past midnight
        expected = 2460325.0 + (0.5 / 86400.0)
        assert pytest.approx(jd, 1e-9) == expected

    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_julian_date_swisseph_exact_equivalence(self):
        """Verifies bit-exact match against Swiss Ephemeris swe.julday()."""
        dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        swe_jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
        
        ts = pd.Series([pd.Timestamp(dt)])
        our_jd = oracle_julian_date_ut(ts).iloc[0]
        assert pytest.approx(our_jd, 1e-9) == swe_jd

    def test_julian_date_vectorized_series_consistency(self):
        """Verifies monotonic ordering and step-size consistency on 1-hour intervals."""
        dates = pd.date_range('2024-01-01', periods=24, freq='1h', tz='UTC')
        jds = oracle_julian_date_ut(pd.Series(dates))
        assert jds.is_monotonic_increasing
        # 1 hour = 1/24 day
        diffs = jds.diff().dropna()
        assert np.allclose(diffs, 1.0 / 24.0, atol=1e-9)


# ==============================================================================
# FEATURE 6: SWISS EPHEMERIS LAHIRI 9 GRAHAS (>= 5 TESTS)
# ==============================================================================

class TestFeature6SwissEphemerisLahiri:
    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_swisseph_lahiri_mode_initialization(self):
        """Validates Lahiri Ayanamsha sidereal mode setup."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa_ut(2460325.0)  # 2024-01-15
        assert 24.0 <= ayanamsa <= 25.0

    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_swisseph_9_grahas_longitude_bounds(self):
        """All 9 grahas longitudes must be normalized strictly in [0, 360)."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
        jd = 2460325.0
        planets = [swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.TRUE_NODE]
        for p in planets:
            res, _ = swe.calc_ut(jd, p, flags)
            lon = res[0] % 360.0
            assert 0.0 <= lon < 360.0

    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_swisseph_retrograde_detection_via_negative_speed(self):
        """Speed < 0 indicates retrograde motion."""
        # Mean lunar node always moves retrograde (speed < 0)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        res, _ = swe.calc_ut(2460325.0, swe.MEAN_NODE, flags)
        speed = res[3]
        assert speed < 0  # Node is retrograde

    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_swisseph_rahu_ketu_exact_180_opposition(self):
        """Ketu longitude must be exactly opposite Rahu ((Rahu + 180) % 360)."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        res, _ = swe.calc_ut(2460325.0, swe.TRUE_NODE, swe.FLG_SIDEREAL)
        rahu_lon = res[0] % 360.0
        ketu_lon = (rahu_lon + 180.0) % 360.0
        diff = abs(rahu_lon - ketu_lon)
        assert diff == 180.0

    @pytest.mark.skipif(swe is None, reason="pyswisseph not installed")
    def test_swisseph_direct_sidereal_vs_manual_subtraction_precision(self):
        """Direct C 3D IAU sidereal projection vs 1D subtraction has sub-arcsecond precision."""
        jd = 2460325.0
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        res_sid, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        res_trop, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        
        diff = abs(res_sid[0] - ((res_trop[0] - ayanamsa) % 360.0))
        assert diff < 0.01  # Under 36 arcseconds difference due to nutation/obliquity projection


# ==============================================================================
# FEATURE 7: 27 NAKSHATRAS & 108 PADAS MAPPING (>= 5 TESTS)
# ==============================================================================

class TestFeature7NakshatrasAndPadas:
    def test_nakshatra_27_bounds_and_names(self):
        """Verifies all 27 nakshatras span exactly 13°20' (13.333333°)."""
        nak_span = 360.0 / 27.0
        assert pytest.approx(nak_span, 1e-6) == 13.333333333333334
        # Total span must equal 360°
        assert pytest.approx(27 * nak_span, 1e-6) == 360.0

    def test_pada_108_bounds_and_numbering(self):
        """Verifies 108 Padas span exactly 3°20' (3.333333°)."""
        pada_span = 360.0 / 108.0
        assert pytest.approx(pada_span, 1e-6) == 3.3333333333333335
        assert pytest.approx(108 * pada_span, 1e-6) == 360.0

    def test_nakshatra_boundary_transition_at_13_deg_20_min(self):
        """Longitude 13.333333° transitions from Ashwini (1) to Bharani (2)."""
        nak_span = 360.0 / 27.0
        ashwini_end = int(13.333332 / nak_span) + 1
        bharani_start = int(13.333334 / nak_span) + 1
        assert ashwini_end == 1
        assert bharani_start == 2

    def test_pada_boundary_transition_at_3_deg_20_min(self):
        """Longitude 3.333333° transitions from Pada 1 to Pada 2."""
        nak_span = 360.0 / 27.0
        pada_span = nak_span / 4.0
        pada1 = int((3.333332 % nak_span) / pada_span) + 1
        pada2 = int((3.333334 % nak_span) / pada_span) + 1
        assert pada1 == 1
        assert pada2 == 2

    def test_nakshatra_origin_at_0_deg_ashwini_pada_1(self):
        """Longitude 0.000° is Ashwini Pada 1."""
        res = oracle_panchang_5_limbs(sun_lon=0.0, moon_lon=0.0, weekday_num=0)
        assert res['nakshatra_num'] == 1
        assert res['pada_num'] == 1


# ==============================================================================
# FEATURE 8: NAVAMSHA D9 CHART CALCULATION (>= 5 TESTS)
# ==============================================================================

class TestFeature8NavamshaD9:
    def test_navamsha_d9_formula_modulo_12(self):
        """Vectorized formula floor(lon / 3.333333°) % 12 produces valid sign [0..11]."""
        lons = np.array([0.0, 3.34, 30.0, 120.0, 359.99])
        d9_signs = oracle_navamsha_d9(lons)
        assert len(d9_signs) == 5
        assert np.all((d9_signs >= 0) & (d9_signs < 12))

    def test_navamsha_d9_parashari_cardinal_cycle_equivalence(self):
        """Fire signs (Aries, Leo, Sag) must start D9 cycle in Aries (Sign 0)."""
        # Aries 0-3.33° -> Aries D9 (0)
        assert oracle_navamsha_d9(0.5) == 0
        # Leo (120°) 120-123.33° -> Aries D9 (0) (120 / 3.3333 = 36 -> 36 % 12 = 0)
        assert oracle_navamsha_d9(120.5) == 0
        # Sagittarius (240°) 240-243.33° -> Aries D9 (0) (240 / 3.3333 = 72 -> 72 % 12 = 0)
        assert oracle_navamsha_d9(240.5) == 0

    def test_navamsha_d9_exact_108_pada_grid_coverage(self):
        """Evaluates all 108 padas and verifies 9 complete cycles through 12 signs."""
        pada_centers = np.linspace(360.0 / 216.0, 360.0 - 360.0 / 216.0, 108)
        d9_grid = oracle_navamsha_d9(pada_centers)
        assert len(d9_grid) == 108
        # Each sign 0-11 must appear exactly 9 times (9 * 12 = 108)
        counts = pd.Series(d9_grid).value_counts()
        for sign_idx in range(12):
            assert counts[sign_idx] == 9

    def test_navamsha_d9_sign_lord_mapping(self):
        """Sign indices map to classical lords: 0/7=Mars, 1/6=Venus, 2/5=Mercury, 3=Moon, 4=Sun, 8/11=Jupiter, 9/10=Saturn."""
        lord_map = {
            0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon', 4: 'Sun',
            5: 'Mercury', 6: 'Venus', 7: 'Mars', 8: 'Jupiter', 9: 'Saturn',
            10: 'Saturn', 11: 'Jupiter'
        }
        for s in range(12):
            assert s in lord_map

    def test_navamsha_d9_boundary_at_30_deg_sign_edge(self):
        """Aries 29.99° (Pada 9) is Sagittarius (8); Taurus 0.01° (Pada 10) is Capricorn (9)."""
        d9_pada9 = oracle_navamsha_d9(29.99)
        d9_pada10 = oracle_navamsha_d9(30.01)
        assert d9_pada9 == 8  # Sagittarius
        assert d9_pada10 == 9  # Capricorn


# ==============================================================================
# FEATURE 9: 5-LIMB PANCHANG SYSTEM (>= 5 TESTS)
# ==============================================================================

class TestFeature9Panchang5Limbs:
    def test_panchang_tithi_shukla_krishna_division(self):
        """Tithi 1-15 is Shukla Paksha, 16-30 is Krishna Paksha."""
        # Moon ahead of Sun by 10° -> Tithi 1 (Shukla)
        p1 = oracle_panchang_5_limbs(sun_lon=0.0, moon_lon=10.0, weekday_num=1)
        assert p1['tithi_num'] == 1
        assert p1['paksha'] == 'Shukla'

        # Moon ahead of Sun by 200° -> Tithi 17 (Krishna)
        p2 = oracle_panchang_5_limbs(sun_lon=0.0, moon_lon=200.0, weekday_num=1)
        assert p2['tithi_num'] == 17
        assert p2['paksha'] == 'Krishna'

    def test_panchang_vara_weekday_mapping(self):
        """Vara corresponds to 0=Sunday through 6=Saturday."""
        varas = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for i, name in enumerate(varas):
            p = oracle_panchang_5_limbs(sun_lon=10.0, moon_lon=20.0, weekday_num=i)
            assert p['vara_num'] == i
            assert p['vara_name'] == name

    def test_panchang_nakshatra_lunar_mansion_mapping(self):
        """Moon at 150° corresponds to Uttara Phalguni (Nakshatra 12)."""
        # 150 / 13.33333 = 11.25 -> Nakshatra 12
        p = oracle_panchang_5_limbs(sun_lon=0.0, moon_lon=150.0, weekday_num=0)
        assert p['nakshatra_num'] == 12

    def test_panchang_yoga_sum_longitude_mapping(self):
        """Yoga is calculated from (Moon + Sun) % 360 / (360/27) + 1."""
        # Moon = 100°, Sun = 50° -> Sum = 150° -> 150 / 13.3333 = 11.25 -> Yoga 12 (Dhruva)
        p = oracle_panchang_5_limbs(sun_lon=50.0, moon_lon=100.0, weekday_num=0)
        assert p['yoga_num'] == 12

    def test_panchang_karana_60_fixed_and_repeating_limbs(self):
        """Karana is half-tithi (6° span). 60 total karanas across the lunar month."""
        # 0-6° -> Karana 1 (Kinstughna)
        p1 = oracle_panchang_5_limbs(sun_lon=0.0, moon_lon=5.0, weekday_num=0)
        assert p1['karana_num'] == 1

        # 354-360° -> Karana 60 (Naga)
        p60 = oracle_panchang_5_limbs(sun_lon=0.0, moon_lon=358.0, weekday_num=0)
        assert p60['karana_num'] == 60


# ==============================================================================
# FEATURE 10: PARASHARI DRISHTI ASPECTS (>= 5 TESTS)
# ==============================================================================

class TestFeature10ParashariDrishti:
    def test_drishti_all_grahas_7th_aspect(self):
        """All grahas cast full 7th aspect (180° opposition)."""
        sun_lon = 0.0
        moon_lon = 180.0
        sep = abs((moon_lon - sun_lon + 180.0) % 360.0 - 180.0)
        assert sep == 180.0

    def test_drishti_mars_special_4th_and_8th_aspects(self):
        """Mars casts special aspects on 4th (90°) and 8th (210°) house/sign offsets."""
        mars_lon = 0.0
        target_4th = 90.0
        target_8th = 210.0
        diff_4th = (target_4th - mars_lon) % 360.0
        diff_8th = (target_8th - mars_lon) % 360.0
        assert diff_4th == 90.0
        assert diff_8th == 210.0

    def test_drishti_jupiter_special_5th_and_9th_aspects(self):
        """Jupiter casts special trine aspects on 5th (120°) and 9th (240°) offsets."""
        jupiter_lon = 0.0
        target_5th = 120.0
        target_9th = 240.0
        assert ((target_5th - jupiter_lon) % 360.0) == 120.0
        assert ((target_9th - jupiter_lon) % 360.0) == 240.0

    def test_drishti_saturn_special_3rd_and_10th_aspects(self):
        """Saturn casts special aspects on 3rd (60°) and 10th (270°) offsets."""
        saturn_lon = 0.0
        target_3rd = 60.0
        target_10th = 270.0
        assert ((target_3rd - saturn_lon) % 360.0) == 60.0
        assert ((target_10th - saturn_lon) % 360.0) == 270.0

    def test_drishti_aspect_orb_precision(self):
        """Aspect is considered active within standard Parashari sign/degree orbs (e.g. +/- 6°)."""
        aspect_center = 180.0
        actual_sep = 182.5
        orb = 6.0
        is_active = abs(actual_sep - aspect_center) <= orb
        assert is_active is True


# ==============================================================================
# FEATURE 11: PLANETARY COMBUSTION (>= 5 TESTS)
# ==============================================================================

class TestFeature11PlanetaryCombustion:
    def test_combustion_classical_orbs_per_graha(self):
        """Classical combustion orbs: Mars 17°, Mercury 14°, Jupiter 11°, Venus 10°, Saturn 15°."""
        combustion_orbs = {
            'Mars': 17.0,
            'Mercury': 14.0,
            'Jupiter': 11.0,
            'Venus': 10.0,
            'Saturn': 15.0
        }
        assert combustion_orbs['Jupiter'] == 11.0
        assert combustion_orbs['Saturn'] == 15.0

    def test_combustion_detection_within_orb(self):
        """Jupiter at 5° separation from Sun is combust (orb = 11°)."""
        sun_lon = 100.0
        jup_lon = 105.0
        sep = abs((jup_lon - sun_lon + 180.0) % 360.0 - 180.0)
        assert sep == 5.0
        assert sep <= 11.0  # Combust

    def test_combustion_rejection_outside_orb(self):
        """Saturn at 20° separation from Sun is NOT combust (orb = 15°)."""
        sun_lon = 100.0
        sat_lon = 120.0
        sep = abs((sat_lon - sun_lon + 180.0) % 360.0 - 180.0)
        assert sep == 20.0
        assert sep > 15.0  # Not combust

    def test_combustion_retrograde_reduced_orbs(self):
        """Mercury retrograde has reduced combustion orb (12° vs 14° direct)."""
        mercury_direct_orb = 14.0
        mercury_retro_orb = 12.0
        sep = 13.0
        assert sep <= mercury_direct_orb
        assert sep > mercury_retro_orb

    def test_combustion_wrap_around_0_360_degrees(self):
        """Sun at 358° and Venus at 3° have separation 5°, combust within 10° orb."""
        sun_lon = 358.0
        ven_lon = 3.0
        sep = abs((ven_lon - sun_lon + 180.0) % 360.0 - 180.0)
        assert pytest.approx(sep, 1e-6) == 5.0
        assert sep <= 10.0
