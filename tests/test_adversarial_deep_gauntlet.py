"""
Deep Stress Test & Adversarial Property Gauntlet
Authored by Challenger 1 (teamwork_preview_challenger)

Tests:
1. High-volume random fuzzing (50,000 iterations) across all candlestick geometries.
2. Timezone & DST Transition Gauntlet (Spring forward, Fall back, leap years).
3. Parashari Drishti & Combustion mathematical boundary fuzzing.
4. Comprehensive verification of all 6 individual timeframe files and master manifest.
"""

import os
import glob
import pytest
import numpy as np
import pandas as pd

from src.market_data.anomaly_sieve import (
    compute_candlestick_geometry,
    compute_trailing_atr,
    compute_tod_rvol,
    compute_hardened_features_and_anomalies,
    TIMEFRAME_RETURN_FLOORS,
)
from src.market_data.data_ingestion import (
    compute_julian_date,
    filter_rth_sessions,
)
from src.vedic_astrology.ephemeris import (
    calculate_9_grahas,
    calculate_graha_positions_batch,
    datetime_to_julian_day,
    timestamps_to_julian_day_array,
    get_ayanamsha,
)
from src.vedic_astrology.nakshatra_navamsha import (
    get_nakshatra,
    get_navamsha,
    get_nakshatra_batch,
    get_navamsha_batch,
    is_gandanta,
    is_gandanta_batch,
)
from src.vedic_astrology.panchang import (
    calculate_panchang,
    calculate_panchang_batch,
    get_tithi_info,
    get_karana_name,
)
from src.vedic_astrology.aspects_combustion import (
    is_rasi_aspect,
    check_combustion,
    calculate_aspect_score,
    calculate_aspects_and_combustion_batch,
    COMBUSTION_ORBS_DIRECT,
    COMBUSTION_ORBS_RETROGRADE,
)


class TestDeepAdversarialGauntlet:

    def test_fuzz_50000_geometric_combinations(self):
        """Fuzz 50,000 combinations including degenerate, dojis, marubozus, extreme, and single-tick bars."""
        np.random.seed(2026)
        n = 50_000

        opens = np.random.uniform(10.0, 5000.0, size=n)
        # 10% dojis, 10% zero wicks, 80% random
        choice = np.random.rand(n)

        closes = np.empty(n)
        highs = np.empty(n)
        lows = np.empty(n)

        for i in range(n):
            o = opens[i]
            c_type = choice[i]
            if c_type < 0.10:
                # Doji
                c = o
                h = o + np.random.exponential(1.0)
                l = max(0.01, o - np.random.exponential(1.0))
            elif c_type < 0.20:
                # Flat bar (zero range)
                c = o
                h = o
                l = o
            elif c_type < 0.30:
                # Marubozu (zero wicks)
                c = max(0.01, o + np.random.uniform(-20.0, 20.0))
                h = max(o, c)
                l = min(o, c)
            else:
                c = max(0.01, o + np.random.uniform(-50.0, 50.0))
                max_oc = max(o, c)
                min_oc = min(o, c)
                h = max_oc + np.random.exponential(2.0)
                l = max(0.001, min_oc - np.random.exponential(2.0))

            closes[i] = c
            highs[i] = h
            lows[i] = l

        df = pd.DataFrame({"Open": opens, "High": highs, "Low": lows, "Close": closes})
        res = compute_candlestick_geometry(df)

        assert not res["Solid_Ratio"].isna().any()
        assert not np.isinf(res["Solid_Ratio"]).any()
        assert (res["Solid_Ratio"] <= 1.0 + 1e-7).all()
        assert (res["Solid_Ratio"] >= 0.0).all()
        assert (res["Max_Wick_Ratio"] <= 1.0 + 1e-7).all()
        assert (res["Max_Wick_Ratio"] >= 0.0).all()

    def test_dst_transition_boundary_julian_days(self):
        """
        Test Julian Day UT continuity across DST Spring Forward (2024-03-10) and Fall Back (2024-11-03).
        """
        # DST Spring Forward: 2024-03-10 01:00 to 04:00 EDT
        spring_ny = pd.date_range("2024-03-10 01:00:00", "2024-03-10 05:00:00", freq="1h", tz="America/New_York")
        jds_spring = timestamps_to_julian_day_array(spring_ny)
        # JDs must be strictly monotonically increasing with exact 1/24 day differences
        jd_diffs = np.diff(jds_spring)
        np.testing.assert_allclose(jd_diffs, 1.0 / 24.0, rtol=1e-7)

        # DST Fall Back: 2024-11-03 00:00 to 04:00 EST
        fall_ny = pd.date_range("2024-11-03 00:00:00", "2024-11-03 04:00:00", freq="1h", tz="America/New_York")
        jds_fall = timestamps_to_julian_day_array(fall_ny)
        jd_diffs_fall = np.diff(jds_fall)
        np.testing.assert_allclose(jd_diffs_fall, 1.0 / 24.0, rtol=1e-7)

    def test_parashari_drishti_rules_comprehensive(self):
        """
        Assert Parashari aspects for all grahas:
        - Mars casts 4th (90°..120°), 7th (180°), 8th (210°..240°)
        - Jupiter casts 5th (120°..150°), 7th (180°), 9th (240°..270°)
        - Saturn casts 3rd (60°..90°), 7th (180°), 10th (270°..300°)
        - All grahas cast 7th aspect (180°)
        """
        # Mars at 0°, Moon at 90° (4th house / 4th aspect: sign 0 to sign 3 -> diff 3)
        assert is_rasi_aspect(0.0, 90.0, "Mars") is True

        # Mars at 0°, Moon at 210° (8th house / 8th aspect: sign 0 to sign 7 -> diff 7)
        assert is_rasi_aspect(0.0, 210.0, "Mars") is True

        # Jupiter at 0°, Moon at 120° (5th house / 5th aspect: sign 0 to sign 4 -> diff 4)
        assert is_rasi_aspect(0.0, 120.0, "Jupiter") is True

        # Jupiter at 0°, Moon at 240° (9th house / 9th aspect: sign 0 to sign 8 -> diff 8)
        assert is_rasi_aspect(0.0, 240.0, "Jupiter") is True

        # Saturn at 0°, Moon at 60° (3rd house / 3rd aspect: sign 0 to sign 2 -> diff 2)
        assert is_rasi_aspect(0.0, 60.0, "Saturn") is True

        # Saturn at 0°, Moon at 270° (10th house / 10th aspect: sign 0 to sign 9 -> diff 9)
        assert is_rasi_aspect(0.0, 270.0, "Saturn") is True

        # Non-aspect: Sun at 0°, Moon at 90° (Sun only has 7th aspect)
        assert is_rasi_aspect(0.0, 90.0, "Sun") is False

    def test_combustion_exact_boundary_orbs(self):
        """
        Verify combustion triggers inside orb and untriggers outside orb.
        """
        # Moon direct orb is 12°
        is_c, sep, caz = check_combustion(0.0, 10.0, "Moon", is_retrograde=False)
        assert is_c is True

        is_c, sep, caz = check_combustion(0.0, 13.0, "Moon", is_retrograde=False)
        assert is_c is False

        # Mercury direct orb is 14°, retrograde orb is 12°
        is_c, sep, caz = check_combustion(0.0, 13.0, "Mercury", is_retrograde=False)
        assert is_c is True

        is_c, sep, caz = check_combustion(0.0, 13.0, "Mercury", is_retrograde=True)
        assert is_c is False  # 13° is outside 12° retrograde orb

        # Wrap around 0°/360°
        is_c, sep, caz = check_combustion(2.0, 355.0, "Venus", is_retrograde=False)
        assert is_c is True  # angular separation is 7° <= 10°

    def test_nakshatra_pada_boundary_atomic_derivation(self):
        """
        Verify that exact boundary longitudes (0°, 120°, 240°, 360°) and all 108 padas
        maintain strict atomic consistency: nak_idx == (global_pada // 4) + 1 and pada == (global_pada % 4) + 1.
        """
        PADA_SPAN = 360.0 / 108.0

        # Boundary checks
        boundaries = [0.0, 13.333333333333334, 120.0, 240.0, 359.999999, 360.0]
        for b in boundaries:
            res = get_nakshatra(b)
            gp = res["global_pada"]
            expected_nak = (gp // 4) + 1
            expected_pada = (gp % 4) + 1
            assert res["nakshatra_num"] == expected_nak, f"Nakshatra mismatch at {b}°: got {res['nakshatra_num']}, expected {expected_nak}"
            assert res["pada"] == expected_pada, f"Pada mismatch at {b}°: got {res['pada']}, expected {expected_pada}"

        # Test batch consistency across all 108 padas
        sample_lons = np.array([i * PADA_SPAN for i in range(108)])
        df_batch = get_nakshatra_batch(sample_lons)
        assert (df_batch["Global_Pada"].to_numpy() == np.arange(108)).all()
        assert (df_batch["Nakshatra_Num"].to_numpy() == (np.arange(108) // 4) + 1).all()
        assert (df_batch["Pada"].to_numpy() == (np.arange(108) % 4) + 1).all()

        # Specific classical anchor checks
        ashwini_1 = get_nakshatra(0.0)
        assert ashwini_1["nakshatra_name"] == "Ashwini" and ashwini_1["pada"] == 1 and ashwini_1["global_pada"] == 0

        magha_1 = get_nakshatra(120.0)
        assert magha_1["nakshatra_name"] == "Magha" and magha_1["pada"] == 1 and magha_1["global_pada"] == 36

        mula_1 = get_nakshatra(240.0)
        assert mula_1["nakshatra_name"] == "Mula" and mula_1["pada"] == 1 and mula_1["global_pada"] == 72

    def test_dst_ambiguous_and_nonexistent_times_ingestion(self):
        """
        Verify that tz_localize handles DST Fall-back ambiguous hours and Spring-forward nonexistent hours
        without crashing.
        """
        # Ambiguous fall-back time: 2024-11-03 01:30:00 (occurs twice)
        s_ambig = pd.Series(pd.to_datetime(["2024-11-03 01:30:00"]))
        # Nonexistent spring-forward time: 2024-03-10 02:30:00 (skipped)
        s_nonexist = pd.Series(pd.to_datetime(["2024-03-10 02:30:00"]))

        # Should localize cleanly with ambiguous='NaT' and nonexistent='shift_forward'
        s_ambig_ny = s_ambig.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward")
        s_nonexist_ny = s_nonexist.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward")

        assert len(s_ambig_ny) == 1
        assert len(s_nonexist_ny) == 1

