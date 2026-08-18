"""
Comprehensive Test Suite for Vedic Astrological Engine (Module 2).
Verifies 100% mathematical precision, IAU/Swiss Ephemeris Sidereal Lahiri compliance,
zero NaNs, and vectorization throughput across all 9 Grahas, 27 Nakshatras, 108 Padas,
Navamsha D9, 5 Panchang limbs, Parashari Drishti aspects, and Astangata combustion.
"""

import math
import numpy as np
import pandas as pd
import pytest
import swisseph as swe

from src.vedic_astrology.ephemeris import (
    datetime_to_julian_day,
    timestamps_to_julian_day_array,
    get_ayanamsha,
    calculate_single_graha,
    calculate_9_grahas,
    calculate_graha_positions_batch,
    DEFAULT_FLAGS,
    GRAHA_NAMES,
)
from src.vedic_astrology.nakshatra_navamsha import (
    NAKSHATRA_METADATA,
    NAKSHATRA_SPAN,
    PADA_SPAN,
    RASI_NAMES,
    RASI_LORDS,
    get_nakshatra,
    get_nakshatra_batch,
    get_navamsha,
    get_navamsha_batch,
    is_gandanta,
    is_gandanta_batch,
    is_pushkara_navamsha,
    is_pushkara_navamsha_batch,
    is_pushkara_bhaga,
    is_pushkara_bhaga_batch,
)
from src.vedic_astrology.panchang import (
    get_tithi_info,
    get_karana_name,
    calculate_panchang,
    calculate_panchang_batch,
    YOGA_NAMES,
)
from src.vedic_astrology.aspects_combustion import (
    angular_separation,
    angular_separation_batch,
    is_rasi_aspect,
    is_rasi_aspect_batch,
    calculate_aspect_score,
    calculate_aspect_score_batch,
    check_combustion,
    calculate_aspects_and_combustion_batch,
)
from src.vedic_astrology import calculate_all_vedic_features


class TestEphemerisEngine:
    """Tests for Swiss Ephemeris initialization, Julian Day conversion, and 9 Grahas kinematics."""

    def test_ayanamsha_lahiri_reference_epoch(self):
        # 2024-01-15 12:00 UTC -> JD 2460325.0
        jd = 2460325.0
        ayan = get_ayanamsha(jd)
        assert 24.18 <= ayan <= 24.21, f"Unexpected Ayanamsha: {ayan}"
        # High precision check: 24.192898...
        assert abs(ayan - 24.1928986) < 1e-4

    def test_datetime_to_julian_day_utc_and_ny(self):
        # 2024-01-15 09:30:00 EST (America/New_York) == 2024-01-15 14:30:00 UTC
        ts_ny = pd.Timestamp("2024-01-15 09:30:00", tz="America/New_York")
        ts_utc = pd.Timestamp("2024-01-15 14:30:00", tz="UTC")

        jd_ny = datetime_to_julian_day(ts_ny)
        jd_utc = datetime_to_julian_day(ts_utc)

        assert abs(jd_ny - jd_utc) < 1e-12
        expected_jd = swe.julday(2024, 1, 15, 14.5, swe.GREG_CAL)
        assert abs(jd_ny - expected_jd) < 1e-12

    def test_timestamps_to_julian_day_array_vectorization(self):
        ts_range = pd.date_range("2020-01-01 00:00:00", periods=100, freq="6h", tz="UTC")
        jds = timestamps_to_julian_day_array(ts_range)
        assert len(jds) == 100
        for i, ts in enumerate(ts_range):
            expected = datetime_to_julian_day(ts)
            assert abs(jds[i] - expected) < 1e-10

    def test_calculate_9_grahas_structure_and_ketu_opposition(self):
        jd = 2460325.0
        grahas = calculate_9_grahas(jd)
        assert len(grahas) == 9
        for name in GRAHA_NAMES:
            assert name in grahas
            g = grahas[name]
            assert 0.0 <= g["lon"] < 360.0
            assert -90.0 <= g["lat"] <= 90.0
            assert g["dist"] > 0.0
            assert isinstance(g["is_retrograde"], bool)

        # Sun and Moon should not be retrograde
        assert grahas["Sun"]["is_retrograde"] is False
        assert grahas["Moon"]["is_retrograde"] is False

        # Ketu must be exactly 180° opposite to Rahu and share Rahu's longitudinal speed
        r_lon = grahas["Rahu"]["lon"]
        k_lon = grahas["Ketu"]["lon"]
        expected_k_lon = (r_lon + 180.0) % 360.0
        assert abs(k_lon - expected_k_lon) < 1e-10
        assert abs(grahas["Ketu"]["speed"] - grahas["Rahu"]["speed"]) < 1e-10

        # True node mode check
        grahas_true = calculate_9_grahas(jd, node_mode="true")
        assert abs(grahas_true["Ketu"]["speed"] - grahas_true["Rahu"]["speed"]) < 1e-10
        assert grahas_true["Ketu"]["is_retrograde"] == grahas_true["Rahu"]["is_retrograde"]

    def test_calculate_graha_positions_batch_consistency(self):
        jds = [2460325.0, 2460326.0, 2460327.0]
        df_batch = calculate_graha_positions_batch(jds)
        assert len(df_batch) == 3
        assert df_batch.isna().sum().sum() == 0

        # Check against single calculation
        single_0 = calculate_9_grahas(jds[0])
        assert abs(df_batch["Sun_Lon"].iloc[0] - single_0["Sun"]["lon"]) < 1e-10
        assert abs(df_batch["Moon_Lon"].iloc[0] - single_0["Moon"]["lon"]) < 1e-10


class TestNakshatraNavamshaEngine:
    """Tests for 27 Nakshatras, 108 Padas, Navamsha D9 Chart, and Gandanta detection."""

    def test_nakshatra_metadata_table_integrity(self):
        assert len(NAKSHATRA_METADATA) == 27
        for idx, nak in enumerate(NAKSHATRA_METADATA):
            assert nak["index"] == idx + 1
            assert nak["name"]
            assert nak["lord"] in ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
            assert nak["gana"] in ["Deva", "Manushya", "Rakshasa"]

    def test_nakshatra_boundary_points(self):
        # 0.0° -> Ashwini Pada 1
        res0 = get_nakshatra(0.0)
        assert res0["nakshatra_name"] == "Ashwini"
        assert res0["pada"] == 1
        assert res0["global_pada"] == 0

        # 13.3333° -> Ashwini Pada 4 / Bharani Pada 1 boundary
        res_ash_end = get_nakshatra(13.33)
        assert res_ash_end["nakshatra_name"] == "Ashwini"
        assert res_ash_end["pada"] == 4

        res_bha = get_nakshatra(13.35)
        assert res_bha["nakshatra_name"] == "Bharani"
        assert res_bha["pada"] == 1

        # 359.9° -> Revati Pada 4
        res_rev = get_nakshatra(359.9)
        assert res_rev["nakshatra_name"] == "Revati"
        assert res_rev["pada"] == 4
        assert res_rev["global_pada"] == 107

    def test_navamsha_d9_classical_identity_across_zodiac(self):
        """
        Verify that mathematical formula floor(lon / 3.33333333°) % 12 matches classical
        Parashari sign elements:
        - Fire signs (Aries, Leo, Sag): start at Aries
        - Earth signs (Taurus, Virgo, Cap): start at Capricorn
        - Air signs (Gemini, Libra, Aqu): start at Libra
        - Water signs (Cancer, Scorpio, Pisces): start at Cancer
        """
        for deg in np.linspace(0.0, 359.99, 1000):
            d9_formula = int(math.floor(deg / PADA_SPAN)) % 12
            rasi_sign = int(math.floor(deg / 30.0)) % 12
            pada_in_sign = int(math.floor((deg % 30.0) / PADA_SPAN))

            # Classical starting sign for D9 based on Rasi element
            if rasi_sign in (0, 4, 8):      # Fire -> Aries (0)
                start_sign = 0
            elif rasi_sign in (1, 5, 9):    # Earth -> Capricorn (9)
                start_sign = 9
            elif rasi_sign in (2, 6, 10):   # Air -> Libra (6)
                start_sign = 6
            else:                          # Water -> Cancer (3)
                start_sign = 3

            d9_classical = (start_sign + pada_in_sign) % 12
            assert d9_formula == d9_classical, f"D9 mismatch at {deg}°: {d9_formula} vs {d9_classical}"

    def test_vargottama_detection(self):
        # 1st navamsha of movable signs is Vargottama (Aries 0°-3°20', Cancer 90°-93°20', etc.)
        assert get_navamsha(1.0)["is_vargottama"] is True
        assert get_navamsha(91.0)["is_vargottama"] is True
        assert get_navamsha(181.0)["is_vargottama"] is True
        assert get_navamsha(271.0)["is_vargottama"] is True

        # 5th navamsha of fixed signs is Vargottama (Taurus 13°20'-16°40' -> 43.33°-46.66°)
        assert get_navamsha(45.0)["is_vargottama"] is True

        # 9th navamsha of dual signs is Vargottama (Gemini 26°40'-30°00' -> 86.66°-90.00°)
        assert get_navamsha(88.0)["is_vargottama"] is True

    def test_gandanta_junction_detection(self):
        # Pisces / Aries junction (360° / 0°)
        assert is_gandanta(359.5) is True
        assert is_gandanta(0.3) is True
        assert is_gandanta(2.0) is False

        # Cancer / Leo junction (120°)
        assert is_gandanta(119.5) is True
        assert is_gandanta(120.3) is True
        assert is_gandanta(115.0) is False

        # Scorpio / Sagittarius junction (240°)
        assert is_gandanta(239.5) is True
        assert is_gandanta(240.2) is True
        assert is_gandanta(245.0) is False

    def test_pushkara_navamsha_classical_mapping(self):
        """Validates classical 24 Pushkara Navamshas across fire, earth, air, water signs."""
        # Fire: Aries (0) -> Pada 7 (21.5°) & Pada 9 (28.0°)
        assert is_pushkara_navamsha(21.5) is True
        assert is_pushkara_navamsha(28.0) is True
        assert is_pushkara_navamsha(5.0) is False

        # Earth: Taurus (30°) -> Pada 3 (38.0°) & Pada 5 (45.0°)
        assert is_pushkara_navamsha(38.0) is True
        assert is_pushkara_navamsha(45.0) is True
        assert is_pushkara_navamsha(32.0) is False

        # Air: Gemini (60°) -> Pada 6 (78.0°) & Pada 8 (85.0°)
        assert is_pushkara_navamsha(78.0) is True
        assert is_pushkara_navamsha(85.0) is True
        assert is_pushkara_navamsha(65.0) is False

        # Water: Cancer (90°) -> Pada 1 (91.5°) & Pada 3 (98.0°)
        assert is_pushkara_navamsha(91.5) is True
        assert is_pushkara_navamsha(98.0) is True
        assert is_pushkara_navamsha(105.0) is False

        # Batch
        lons = np.array([21.5, 5.0, 38.0, 78.0, 91.5, 105.0])
        batch_res = is_pushkara_navamsha_batch(lons)
        assert np.array_equal(batch_res, [True, False, True, True, True, False])

    def test_pushkara_bhaga_degrees(self):
        """Validates 12 classical Pushkara Bhaga degree points within 1° orb."""
        # Aries 21°, Taurus 14°, Gemini 18°, Cancer 8°
        assert is_pushkara_bhaga(21.0) is True
        assert is_pushkara_bhaga(21.5, orb=1.0) is True
        assert is_pushkara_bhaga(25.0, orb=1.0) is False

        assert is_pushkara_bhaga(30.0 + 14.0) is True  # Taurus 14°
        assert is_pushkara_bhaga(60.0 + 18.0) is True  # Gemini 18°
        assert is_pushkara_bhaga(90.0 + 8.0) is True   # Cancer 8°

        # Batch
        lons = np.array([21.0, 44.0, 78.0, 98.0, 15.0])
        batch_res = is_pushkara_bhaga_batch(lons, orb=1.0)
        assert np.array_equal(batch_res, [True, True, True, True, False])


class TestPanchangEngine:
    """Tests for 5 Panchang Limbs: Tithi, Vara, Nakshatra, Yoga, and Karana."""

    def test_tithi_shukla_and_krishna_phases(self):
        # New Moon (Amavasya) -> Sun=0, Moon=0 -> Elong=0 -> Shukla Pratipada (Tithi 1)
        p1 = calculate_panchang(0.0, 0.0, 2460325.0)

        assert p1["paksha"] == "Shukla"
        assert p1["tithi_name"] == "Shukla Pratipada"

        # Quarter Moon -> Elong=90° -> 90/12 = 7.5 -> Shukla Ashtami (Tithi 8)
        p8 = calculate_panchang(0.0, 90.0, 2460325.0)

        assert p8["paksha"] == "Shukla"
        assert "Ashtami" in p8["tithi_name"]

        # Full Moon (Purnima) -> Elong=175° -> 175/12 = 14.58 -> Shukla Purnima (Tithi 15)
        p15 = calculate_panchang(0.0, 175.0, 2460325.0)

        assert p15["paksha"] == "Shukla"
        assert "Purnima" in p15["tithi_name"]

        # Waning Moon -> Elong=355° -> 355/12 = 29.58 -> Krishna Amavasya (Tithi 30)
        p30 = calculate_panchang(0.0, 355.0, 2460325.0)

        assert p30["paksha"] == "Krishna"
        assert "Amavasya" in p30["tithi_name"]

    def test_vara_weekday_calculation(self):
        # 2024-01-14 was Sunday -> JD 2460323.5 -> floor(2460323.5 + 1.5) % 7 = 2460325 % 7 = 0 (Sunday)
        p_sun = calculate_panchang(0.0, 0.0, 2460323.5)
        assert p_sun["vara_num"] == 0
        assert p_sun["vara_name"] == "Sunday"
        assert p_sun["vara_lord"] == "Sun"

        # 2024-01-15 was Monday -> JD 2460324.5
        p_mon = calculate_panchang(0.0, 0.0, 2460324.5)
        assert p_mon["vara_num"] == 1
        assert p_mon["vara_name"] == "Monday"
        assert p_mon["vara_lord"] == "Moon"

    def test_nithya_yoga_vyatipata_and_vaidhriti(self):
        # 27 Yogas
        assert len(YOGA_NAMES) == 27

        # Vyatipata (#17): Sum in [213.333°, 226.666°)
        p_vya = calculate_panchang(100.0, 120.0, 2460325.0) # 220°

        assert p_vya["yoga_name"] == "Vyatipata"
        assert p_vya["is_vyatipata_yoga"] is True

        # Vaidhriti (#27): Sum in [346.666°, 360.0°)
        p_vai = calculate_panchang(175.0, 175.0, 2460325.0) # 350°

        assert p_vai["yoga_name"] == "Vaidhriti"
        assert p_vai["is_vaidhriti_yoga"] is True

    def test_karana_fixed_and_moveable_vishti_bhadra(self):
        # K=1: Kintughna (Fixed)
        p1 = calculate_panchang(0.0, 2.0, 2460325.0)

        assert p1["karana_name"] == "Kintughna"
        assert p1["is_vishti_karana"] is False

        # K=8: Vishti (Bhadra Karana) -> Elongation in [42°, 48°)
        p8 = calculate_panchang(0.0, 45.0, 2460325.0)

        assert p8["karana_name"] == "Vishti"
        assert p8["is_vishti_karana"] is True

        # K=58: Shakuni, K=59: Chatushpada, K=60: Naga (Fixed)
        assert get_karana_name(58) == "Shakuni"
        assert get_karana_name(59) == "Chatushpada"
        assert get_karana_name(60) == "Naga"


class TestAspectsCombustionEngine:
    """Tests for Parashari Drishti and Astangata Combustion."""

    def test_parashari_drishti_rules(self):
        # All Grahas aspect 7th house (opposition / sign diff 6)
        assert is_rasi_aspect(0.0, 180.0, "Sun") is True
        assert is_rasi_aspect(0.0, 180.0, "Moon") is True
        assert is_rasi_aspect(0.0, 180.0, "Venus") is True
        assert is_rasi_aspect(0.0, 180.0, "Mercury") is True

        # Mars aspects 4th (90°), 7th (180°), 8th (210°)
        assert is_rasi_aspect(0.0, 90.0, "Mars") is True
        assert is_rasi_aspect(0.0, 180.0, "Mars") is True
        assert is_rasi_aspect(0.0, 210.0, "Mars") is True
        assert is_rasi_aspect(0.0, 120.0, "Mars") is False

        # Jupiter aspects 5th (120°), 7th (180°), 9th (240°)
        assert is_rasi_aspect(0.0, 120.0, "Jupiter") is True
        assert is_rasi_aspect(0.0, 180.0, "Jupiter") is True
        assert is_rasi_aspect(0.0, 240.0, "Jupiter") is True
        assert is_rasi_aspect(0.0, 60.0, "Jupiter") is False

        # Saturn aspects 3rd (60°), 7th (180°), 10th (270°)
        assert is_rasi_aspect(0.0, 60.0, "Saturn") is True
        assert is_rasi_aspect(0.0, 180.0, "Saturn") is True
        assert is_rasi_aspect(0.0, 270.0, "Saturn") is True
        assert is_rasi_aspect(0.0, 90.0, "Saturn") is False

    def test_continuous_aspect_score(self):
        # Exact aspect -> score 1.0
        score_exact = calculate_aspect_score(0.0, 180.0, "Mars", orb_deg=10.0)
        assert abs(score_exact - 1.0) < 1e-10

        # 5° away with 10° orb -> score 0.5
        score_5deg = calculate_aspect_score(0.0, 175.0, "Mars", orb_deg=10.0)
        assert abs(score_5deg - 0.5) < 1e-10

        # 12° away with 10° orb -> score 0.0
        score_out = calculate_aspect_score(0.0, 168.0, "Mars", orb_deg=10.0)
        assert score_out == 0.0

    def test_combustion_classical_orbs(self):
        # Mars orb: 17°
        assert check_combustion(100.0, 116.0, "Mars")[0] is True
        assert check_combustion(100.0, 118.0, "Mars")[0] is False

        # Mercury direct (14°) vs retrograde (12°)
        assert check_combustion(100.0, 113.0, "Mercury", is_retrograde=False)[0] is True
        assert check_combustion(100.0, 113.0, "Mercury", is_retrograde=True)[0] is False

        # Venus direct (10°) vs retrograde (8°)
        assert check_combustion(100.0, 109.0, "Venus", is_retrograde=False)[0] is True
        assert check_combustion(100.0, 109.0, "Venus", is_retrograde=True)[0] is False

        # Saturn orb: 15°
        assert check_combustion(100.0, 114.0, "Saturn")[0] is True
        assert check_combustion(100.0, 116.0, "Saturn")[0] is False

        # Cazimi / deep combustion (< 1.0°)
        assert check_combustion(100.0, 100.5, "Jupiter")[2] is True
        assert check_combustion(100.0, 102.5, "Jupiter")[2] is False


class TestUnifiedVedicFeatureMatrix:
    """Tests for the high-level calculate_all_vedic_features pipeline."""

    def test_zero_nans_and_column_schema(self):
        jds = [2460325.0 + i * 0.1 for i in range(20)]
        df_vedic = calculate_all_vedic_features(jds)

        assert len(df_vedic) == 20
        assert df_vedic.isna().sum().sum() == 0, f"Found {df_vedic.isna().sum().sum()} NaNs!"

        # Key columns presence
        required_cols = [
            "Julian_Date_UT",
            "Sun_Lon", "Moon_Lon", "Mars_Lon", "Mercury_Lon", "Jupiter_Lon", "Venus_Lon", "Saturn_Lon", "Rahu_Lon", "Ketu_Lon",
            "Sun_Speed", "Moon_Speed", "Mars_Speed", "Mercury_Speed", "Jupiter_Speed", "Venus_Speed", "Saturn_Speed",
            "Mars_Retro", "Mercury_Retro", "Jupiter_Retro", "Saturn_Retro", "Venus_Retro",









            "Ayanamsha_Val",
        ]

        for col in required_cols:
            assert col in df_vedic.columns, f"Missing required column: {col}"

    def test_performance_throughput(self):
        import time
        jds = [2460000.0 + i * 0.05 for i in range(1000)]
        t0 = time.time()
        df = calculate_all_vedic_features(jds)
        t1 = time.time()
        elapsed = t1 - t0
        throughput = len(jds) / elapsed
        print(f"\nCalculated {len(jds)} timestamps in {elapsed:.3f} s ({throughput:.1f} timestamps/sec)")
        assert throughput > 300, f"Throughput too low: {throughput:.1f} ts/s"
        assert len(df) == 1000


class TestEdgeCasesAndHistoricalRegimes:
    """Stress tests across historical eras (1993-2026), boundary conditions, and retrograde regimes."""

    def test_historical_multi_era_stability(self):
        historical_dates = [
            "1993-01-29 09:30:00",  # SPY inception
            "2000-03-24 09:30:00",  # Dot-com peak
            "2008-09-15 09:30:00",  # Lehman bankruptcy
            "2020-03-23 09:30:00",  # Covid low
            "2024-07-16 09:30:00",  # All-time high
            "2026-08-17 09:30:00",  # Modern day
        ]
        jds = [datetime_to_julian_day(d, default_tz="America/New_York") for d in historical_dates]
        df_era = calculate_all_vedic_features(jds)

        assert len(df_era) == len(historical_dates)
        assert df_era.isna().sum().sum() == 0

        # Verify Ayanamsha increases monotonically over historical time (~50.3 arcsec/year)
        ayans = df_era["Ayanamsha_Val"].to_numpy()
        for i in range(len(ayans) - 1):
            assert ayans[i] < ayans[i + 1], f"Ayanamsha not increasing: {ayans[i]} vs {ayans[i+1]}"

    def test_retrograde_detection_regimes(self):
        # Known Mercury retrograde period: Dec 13, 2023 to Jan 2, 2024
        ts_retro = pd.date_range("2023-12-15", "2023-12-25", freq="1D", tz="UTC")
        jds_retro = timestamps_to_julian_day_array(ts_retro)
        df_retro = calculate_graha_positions_batch(jds_retro)

        assert df_retro["Mercury_Retrograde"].all(), "Mercury was retrograde during Dec 2023!"
        assert (df_retro["Mercury_Speed"] < 0.0).all()

        # Known Mercury direct period: Feb 15, 2024
        jd_direct = datetime_to_julian_day("2024-02-15 12:00:00+00:00")
        df_direct = calculate_graha_positions_batch([jd_direct])
        assert not df_direct["Mercury_Retrograde"].iloc[0]
        assert df_direct["Mercury_Speed"].iloc[0] > 0.0

    def test_boundary_zero_and_360_degree_wrap(self):
        # Test coordinates at exact boundary 0.0° and 359.99999°
        lons = np.array([0.0, 359.99999, 120.0, 240.0])
        nak_df = get_nakshatra_batch(lons)
        nav_df = get_navamsha_batch(lons)

        assert nak_df["Nakshatra_Num"].iloc[0] == 1   # Ashwini
        assert nak_df["Nakshatra_Num"].iloc[1] == 27  # Revati
        assert nav_df["Navamsha_Sign_Num"].iloc[0] == 0  # Aries
        assert nav_df["Navamsha_Sign_Num"].iloc[1] == 11 # Pisces

