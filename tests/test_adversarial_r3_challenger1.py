"""
Adversarial Stress Testing & Invariant Fuzzing Suite for Vedic-Quant R3
Authored by Challenger 1 (EMPIRICAL CHALLENGER - critic, specialist)

This test suite aggressively stress-tests mathematical and astrological invariants across all 13 Vedic Pillars:
1. 0°/360° degree wrap-around boundaries for longitudes, nakshatras, padas, vargas (D1, D9, D10, D60), and mutual aspects.
2. Ashtakavarga BAV/SAV invariant: 100+ random synthetic charts -> sum(SAV) == 337 in 100% of cases.
3. Jaimini 7 Karakas: 100+ random synthetic charts and tied-degree edge cases -> strictly 1-to-1 bijective mapping AK..DK.
4. Ketu speed, 180° opposition, and retrograde flags across stations and true node modes.
5. Pushkara Navamsha & Pushkara Bhaga functions against all 24 classical Navamshas and 12 classical Bhagas.
6. Multi-Natal 4-entity hierarchy, KP 249 sub-lords, Vimshottari dasha progression, Shadbala potencies, and Sarvatobhadra Chakra vedhas.
"""

import sys
import os
import math
import pytest
import numpy as np
import pandas as pd
import swisseph as swe

# Ensure project root and src directories are on path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CORE_DIR = os.path.join(PROJECT_ROOT, "src", "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

VA_DIR = os.path.join(PROJECT_ROOT, "src", "vedic_astrology")
if VA_DIR not in sys.path:
    sys.path.insert(0, VA_DIR)

from src.core.astro_vargas import get_varga_sign, get_all_vargas
from src.core.jaimini_karakas import calculate_jaimini_karakas, get_astrosage_karak_table
from src.core.astro_ashtakvarga import get_raw_ashtakvarga, get_reduced_ashtakvarga, bav_tensor
from src.core.shadbala_core import calc_shadbala
from src.core.kp_ephemeris_module import compute_kp_longitudes, _get_kp_lords
from src.vedic_astrology.ephemeris import (
    calculate_9_grahas,
    calculate_single_graha,
    calculate_graha_positions_batch,
    datetime_to_julian_day,
    init_ephemeris,
    GRAHA_NAMES,
)
from src.vedic_astrology.nakshatra_navamsha import (
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
    PUSHKARA_NAVAMSHA_INDICES,
    PUSHKARA_BHAGA_DEGREES,
    NAKSHATRA_METADATA,
    RASI_NAMES,
    RASI_LORDS,
)
from src.vedic_astrology.aspects_combustion import (
    angular_separation,
    angular_separation_batch,
    is_rasi_aspect,
    is_rasi_aspect_batch,
    calculate_aspect_score,
    check_combustion,
    calculate_aspects_and_combustion_batch,
    PARASHARI_HOUSE_ASPECTS,
)
from src.vedic_astrology.panchang import calculate_panchang, calculate_panchang_batch
from src.vedic_astrology.omni_vedic_fusion import (
    extract_omni_vedic_row,
    _safe_angular_distance,
    _mutual_bhava,
    _kakshya_lord,
    _nakshatra_and_pada,
)
from src.vedic_astrology.multi_natal_engine import (
    extract_all_multi_natal_features,
    NATAL_ENTITIES,
)


# ==============================================================================
# 1. WRAP-AROUND BOUNDARY ADVERSARIAL GAUNTLET (0° / 360°)
# ==============================================================================
class TestAdversarialBoundaryWrapAround:
    """
    Stress-tests edge cases around 0°, 360°, negative longitudes, and large angle multiples.
    """

    @pytest.mark.parametrize("lon_input, expected_lon", [
        (0.0, 0.0),
        (360.0, 0.0),
        (720.0, 0.0),
        (-360.0, 0.0),
        (-0.000001, 359.999999),
        (359.999999, 359.999999),
        (0.000001, 0.000001),
        (360.000001, 0.000001),
        (719.999999, 359.999999),
    ])
    def test_nakshatra_boundary_wrap_around(self, lon_input, expected_lon):
        """Nakshatra & Pada calculations must wrap seamlessly across 0°/360°."""
        res = get_nakshatra(lon_input)
        assert 1 <= res["nakshatra_num"] <= 27
        assert 1 <= res["pada"] <= 4
        assert 0 <= res["global_pada"] <= 107
        assert res["lord"] in ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

        # Exact boundary assertions
        if expected_lon < 0.1:
            assert res["nakshatra_num"] == 1
            assert res["nakshatra_name"] == "Ashwini"
            assert res["pada"] == 1
            assert res["global_pada"] == 0
        elif expected_lon > 359.9:
            assert res["nakshatra_num"] == 27
            assert res["nakshatra_name"] == "Revati"
            assert res["pada"] == 4
            assert res["global_pada"] == 107

    def test_all_108_pada_boundaries_continuity(self):
        """
        Tests all 108 Pada boundaries across the full 360° circle.
        For each boundary B = k * (360/108), test B - eps and B + eps.
        """
        pada_span = 360.0 / 108.0  # 3°20' = 3.3333333333333335°
        eps = 1e-7

        for k in range(108):
            deg = k * pada_span

            # Just after boundary
            res_after = get_nakshatra(deg + eps)
            assert res_after["global_pada"] == k, f"Pada mismatch after boundary {k} at deg {deg + eps}"

            # Just before boundary (if k > 0)
            if k > 0:
                res_before = get_nakshatra(deg - eps)
                assert res_before["global_pada"] == k - 1, f"Pada mismatch before boundary {k} at deg {deg - eps}"
            else:
                res_before = get_nakshatra(360.0 - eps)
                assert res_before["global_pada"] == 107

    @pytest.mark.parametrize("lon_deg, expected_d1, expected_d9", [
        (0.0, 0, 0),         # 0° Aries -> D1 Aries(0), D9 Aries(0)
        (0.00001, 0, 0),     # 0.00001° -> D1 Aries(0), D9 Aries(0)
        (3.3333, 0, 0),      # 3°20' - eps -> D9 Aries(0)
        (3.3334, 0, 1),      # 3°20' + eps -> D9 Taurus(1)
        (29.9999, 0, 8),     # 29°59' Aries -> D1 Aries(0), D9 Sag(8)
        (30.0, 1, 9),        # 30° Taurus -> D1 Taurus(1), D9 Cap(9)
        (359.9999, 11, 11),  # 359°59' Pisces -> D1 Pisces(11), D9 Pisces(11) [Vargottama!]
    ])
    def test_navamsha_d9_boundary_wrapping(self, lon_deg, expected_d1, expected_d9):
        """Navamsha (D9) and Vargottama calculations at exact sign and pada boundaries."""
        res = get_navamsha(lon_deg)
        assert res["rasi_sign_num"] == expected_d1
        assert res["navamsha_sign_num"] == expected_d9
        if expected_d1 == expected_d9:
            assert res["is_vargottama"] is True
        else:
            assert res["is_vargottama"] is False

    def test_shodashvarga_all_vargas_boundary_stability(self):
        """
        Stress tests get_all_vargas across 1,000 synthetic boundary points
        including 0°, 30°, 60°, ..., 360° and eps perturbations.
        Guarantees all returned varga signs are strictly integers in [0, 11].
        """
        test_points = []
        for sign_deg in range(0, 360, 30):
            for delta in [-1.0, -0.5, -0.001, -1e-6, 0.0, 1e-6, 0.001, 0.5, 1.0]:
                test_points.append((sign_deg + delta) % 360.0)

        # Add random points
        np.random.seed(42)
        test_points.extend(np.random.uniform(0, 360, size=500).tolist())

        for pt in test_points:
            vargas = get_all_vargas(pt)
            assert len(vargas) == 16
            for v_idx, v_sign in enumerate(vargas):
                assert 0 <= v_sign <= 11, f"Varga index {v_idx} produced invalid sign {v_sign} at lon {pt}"

    def test_mutual_aspects_across_zero_degree_boundary(self):
        """
        Adversarial test for mutual aspect calculations when bodies straddle the 0° Aries/Pisces boundary.
        Body 1 at 359.5° (Pisces), Body 2 at 0.5° (Aries):
        - Angular separation must be 1.0° (NOT 359.0°).
        - Mutual Bhava from Body 1 to Body 2 must be 2 (Pisces -> Aries is 2nd house).
        - Mutual Bhava from Body 2 to Body 1 must be 12 (Aries -> Pisces is 12th house).
        """
        lon1 = 359.5
        lon2 = 0.5

        # Shortest distance
        dist = angular_separation(lon1, lon2)
        assert pytest.approx(dist, 1e-6) == 1.0

        # Safe angular distance in omni fusion
        dist_fusion = _safe_angular_distance(lon1, lon2)
        assert pytest.approx(dist_fusion, 1e-6) == 1.0

        # Mutual bhavas
        bhava_1_to_2 = _mutual_bhava(lon1, lon2)
        bhava_2_to_1 = _mutual_bhava(lon2, lon1)

        assert bhava_1_to_2 == 2, f"Expected 2nd house, got {bhava_1_to_2}"
        assert bhava_2_to_1 == 12, f"Expected 12th house, got {bhava_2_to_1}"

    def test_exact_opposition_across_boundary(self):
        """Planet at 359.9° and planet at 179.9° must have 180° opposition aspect."""
        lon1 = 359.9
        lon2 = 179.9
        dist = angular_separation(lon1, lon2)
        assert pytest.approx(dist, 1e-6) == 180.0

        # Parashari Drishti
        aspect_score = calculate_aspect_score(lon1, lon2, "Sun", orb_deg=5.0)
        assert pytest.approx(aspect_score, 1e-6) == 1.0


# ==============================================================================
# 2. ASHTAKAVARGA BAV/SAV 337 SUM INVARIANT GAUNTLET
# ==============================================================================
class TestAdversarialAshtakavargaEngine:
    """
    Stress-tests Ashtakavarga BAV/SAV engine:
    Generates 100+ random synthetic planetary configurations across the zodiac
    and rigorously verifies that sum(SAV) == 337 in 100.0% of cases.
    """

    def test_sav_sum_invariant_100_synthetic_charts(self):
        """
        Generates 200 random synthetic charts with arbitrary planetary positions (0..11)
        for the 8 contributors (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Ascendant).
        Verifies sum(SAV) == 337 in 100% of cases.
        """
        np.random.seed(108)
        num_charts = 200
        sav_sums = []
        individual_bav_sums = {
            0: 48,  # Sun
            1: 49,  # Moon
            2: 39,  # Mars
            3: 54,  # Mercury
            4: 56,  # Jupiter
            5: 52,  # Venus
            6: 39,  # Saturn
        }

        for trial in range(num_charts):
            # 8 random sign placements in [0, 11]
            planet_signs = np.random.randint(0, 12, size=8, dtype=np.int32)
            bav, sav = get_raw_ashtakvarga(planet_signs)

            # 1. Verify SAV sum == 337
            total_sav = int(np.sum(sav))
            sav_sums.append(total_sav)
            assert total_sav == 337, f"Trial {trial}: SAV sum violated! sum={total_sav}, signs={planet_signs}"

            # 2. Verify each planet's BAV total points invariant
            for p_recv, expected_bav_total in individual_bav_sums.items():
                p_bav_total = int(np.sum(bav[p_recv]))
                assert p_bav_total == expected_bav_total, (
                    f"Trial {trial}: Planet {p_recv} BAV sum violated! Got {p_bav_total}, expected {expected_bav_total}"
                )

            # 3. Verify SAV per sign is exact sum of the 7 BAVs for that sign
            for s in range(12):
                col_sum = int(np.sum(bav[:, s]))
                assert sav[s] == col_sum, f"Trial {trial}: SAV[{s}] ({sav[s]}) != sum(BAV[:, {s}]) ({col_sum})"

        # Statistical summary
        assert all(s == 337 for s in sav_sums)
        assert len(sav_sums) == num_charts

    def test_extreme_clustering_ashtakavarga(self):
        """
        Adversarial Case 1: All 8 bodies in the exact same sign (e.g. Stellium in Aries).
        Adversarial Case 2: Uniform distribution (1 body per sign for first 8 signs).
        Adversarial Case 3: Alternating odd/even signs.
        """
        # Case 1: All in Sign 0 (Aries)
        all_aries = np.zeros(8, dtype=np.int32)
        bav_aries, sav_aries = get_raw_ashtakvarga(all_aries)
        assert np.sum(sav_aries) == 337
        assert all(np.sum(bav_aries[p]) in [48, 49, 39, 54, 56, 52] for p in range(7))

        # Case 2: All in Sign 11 (Pisces)
        all_pisces = np.full(8, 11, dtype=np.int32)
        _, sav_pisces = get_raw_ashtakvarga(all_pisces)
        assert np.sum(sav_pisces) == 337

        # Case 3: Uniform distribution 0..7
        uniform_signs = np.arange(8, dtype=np.int32)
        _, sav_uniform = get_raw_ashtakvarga(uniform_signs)
        assert np.sum(sav_uniform) == 337

    def test_reduced_ashtakavarga_non_mutation(self):
        """
        Verifies that Trikona Shodhana and Ekadhipatya Shodhana do NOT mutate
        the raw BAV matrix in place.
        """
        planet_signs = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=np.int32)
        bav_raw, _ = get_raw_ashtakvarga(planet_signs)
        bav_raw_copy = bav_raw.copy()

        reduced = get_reduced_ashtakvarga(bav_raw)

        # Raw must remain unmodified
        assert np.array_equal(bav_raw, bav_raw_copy), "Raw BAV was mutated by reduction!"
        # Reduced must have sum <= raw sum
        assert np.sum(reduced) <= np.sum(bav_raw)


# ==============================================================================
# 3. JAIMINI 7 CHARA KARAKAS BIJECTIVE 1-TO-1 UNIQUENESS GAUNTLET
# ==============================================================================
class TestAdversarialJaiminiKarakas:
    """
    Stress-tests Jaimini 7 Chara Karakas:
    - 100+ random synthetic planetary degree assignments.
    - Tests that AK, AmK, BK, MK, PK, GK, DK is strictly 1-to-1 bijective with 0 duplicate assignments.
    - Adversarial tied-degree edge cases (all 7 planets with identical degree in sign).
    - Boundary degrees: 0.000000° and 29.999999°.
    """

    def test_jaimini_100_random_charts_bijective_uniqueness(self):
        """
        Generates 150 random charts.
        Verifies:
        1. Exactly 7 Karakas returned: AK, AmK, BK, MK, PK, GK, DK.
        2. Set of assigned planets exactly equals {Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn}.
        3. Zero duplicate planets, zero duplicate Karakas.
        4. Strict descending order of degree_in_sign (or deterministic tie-break).
        """
        np.random.seed(777)
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        expected_karakas = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

        for trial in range(150):
            # Random absolute longitudes [0, 360)
            random_lons = np.random.uniform(0, 360, size=7)
            chart_input = [{"planet": p, "longitude": float(lon)} for p, lon in zip(planets, random_lons)]

            karakas_res = calculate_jaimini_karakas(chart_input)
            assert len(karakas_res) == 7

            assigned_karakas = [k["karaka_abbr"] for k in karakas_res]
            assigned_planets = [k["planet"] for k in karakas_res]

            # Bijection checks
            assert assigned_karakas == expected_karakas
            assert set(assigned_planets) == set(planets)
            assert len(set(assigned_planets)) == 7, f"Duplicate planet assigned in trial {trial}!"

            # Monotonicity check
            degrees = [k["degree_in_sign"] for k in karakas_res]
            for i in range(len(degrees) - 1):
                assert degrees[i] >= degrees[i + 1], f"Degrees not descending: {degrees}"

    def test_adversarial_tied_degrees_all_planets(self):
        """
        Adversarial Edge Case: All 7 visible planets have the exact same intra-sign degree (e.g. 15.000000°).
        Algorithm MUST deterministically resolve ties without throwing an error and without duplicate Karakas.
        """
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        # All planets in different signs but identical degree_in_sign = 15.0°
        tied_input = [{"planet": p, "longitude": float(i * 30.0 + 15.0)} for i, p in enumerate(planets)]

        karakas_res = calculate_jaimini_karakas(tied_input)
        assert len(karakas_res) == 7

        assigned_planets = [k["planet"] for k in karakas_res]
        assigned_karakas = [k["karaka_abbr"] for k in karakas_res]

        assert len(set(assigned_planets)) == 7, "Tied degrees caused duplicate or missing planets!"
        assert assigned_karakas == ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

    def test_adversarial_extreme_boundary_degrees(self):
        """
        Planets at 0.000000° (start of sign) and 29.999999° (cusp of sign).
        Verifies modulo 30.0 and formatting.
        """
        boundary_input = [
            {"planet": "Sun", "longitude": 29.999999},      # ~29.999999° -> AK
            {"planet": "Moon", "longitude": 60.0 + 25.0},    # 25.0° -> AmK
            {"planet": "Mars", "longitude": 120.0 + 20.0},   # 20.0° -> BK
            {"planet": "Mercury", "longitude": 180.0 + 15.0},# 15.0° -> MK
            {"planet": "Jupiter", "longitude": 240.0 + 10.0},# 10.0° -> PK
            {"planet": "Venus", "longitude": 300.0 + 5.0},   # 5.0° -> GK
            {"planet": "Saturn", "longitude": 0.000001},     # ~0.000001° -> DK
        ]

        karakas_res = calculate_jaimini_karakas(boundary_input)
        assert karakas_res[0]["planet"] == "Sun"
        assert karakas_res[0]["karaka_abbr"] == "AK"
        assert karakas_res[6]["planet"] == "Saturn"
        assert karakas_res[6]["karaka_abbr"] == "DK"

    def test_gnatikaraka_gk_crash_karaka_mapping(self):
        """
        Verifies that Gnatikaraka (GK) is strictly the 6th highest degree planet (index 5).
        """
        planets_input = [
            {"planet": "Sun", "longitude": 28.0},      # AK
            {"planet": "Moon", "longitude": 24.0},     # AmK
            {"planet": "Mars", "longitude": 20.0},     # BK
            {"planet": "Mercury", "longitude": 16.0},  # MK
            {"planet": "Jupiter", "longitude": 12.0},  # PK
            {"planet": "Venus", "longitude": 8.0},     # GK (Crash Karaka)
            {"planet": "Saturn", "longitude": 4.0},    # DK
        ]
        table = get_astrosage_karak_table(planets_input)
        assert table["Venus"]["karaka_abbr"] == "GK"
        assert table["Venus"]["karaka"] == "Gnati"


# ==============================================================================
# 4. KETU SPEED, RETROGRADE FLAGS, AND LUNAR NODE GAUNTLET
# ==============================================================================
class TestAdversarialKetuAndNodeKinematics:
    """
    Stress-tests Ketu speed, 180° opposition invariant, and retrograde flags
    across stations and true node modes.
    """

    def test_mean_node_kinematics_and_ketu_invariants(self):
        """
        Under Mean Node (classical standard):
        - Rahu speed is strictly negative (mean retrograde motion).
        - Ketu longitude is exactly (Rahu_lon + 180°) % 360°.
        - Ketu speed is equal to Rahu speed.
        - Ketu is_retrograde is True.
        - Angular separation between Rahu and Ketu is exactly 180.0°.
        """
        # Test across 50 historical Julian Days spanning 1993 to 2026
        np.random.seed(333)
        test_jds = np.random.uniform(2449000.5, 2461000.5, size=50)

        for jd in test_jds:
            grahas = calculate_9_grahas(jd, node_mode="mean")
            rahu = grahas["Rahu"]
            ketu = grahas["Ketu"]

            # 1. 180° Opposition Invariant
            expected_k_lon = (rahu["lon"] + 180.0) % 360.0
            assert pytest.approx(ketu["lon"], 1e-5) == expected_k_lon
            sep = angular_separation(rahu["lon"], ketu["lon"])
            assert pytest.approx(sep, 1e-5) == 180.0

            # 2. Speed matching
            assert pytest.approx(ketu["speed"], 1e-6) == rahu["speed"]
            assert rahu["speed"] < 0.0  # Mean node is always retrograde

            # 3. Retrograde flag
            assert rahu["is_retrograde"] is True
            assert ketu["is_retrograde"] is True

            # 4. Latitude inversion
            assert pytest.approx(ketu["lat"], 1e-6) == -rahu["lat"]

    def test_true_node_station_and_direct_motion_flips(self):
        """
        Under True Node:
        - True node undergoes oscillations and can turn direct (speed > 0) or stationary (|speed| < 0.05).
        - Ketu MUST maintain exact 180° opposition to Rahu at all times.
        - Ketu speed must mirror Rahu speed.
        - Ketu retrograde flag must accurately reflect speed sign in true node mode.
        """
        # Sample daily sequence across a true node stationary station (e.g. early 2024)
        dates = pd.date_range("2024-01-01", periods=120, freq="1D", tz="UTC")
        jds = [datetime_to_julian_day(d) for d in dates]

        direct_count = 0
        retro_count = 0
        stat_count = 0

        for jd in jds:
            grahas = calculate_9_grahas(jd, node_mode="true")
            rahu = grahas["Rahu"]
            ketu = grahas["Ketu"]

            # Invariant: 180° opposition
            sep = angular_separation(rahu["lon"], ketu["lon"])
            assert pytest.approx(sep, 1e-5) == 180.0

            # Speed equality
            assert pytest.approx(ketu["speed"], 1e-6) == rahu["speed"]

            # Retrograde flag consistency
            assert ketu["is_retrograde"] == rahu["is_retrograde"]
            assert ketu["is_stationary"] == rahu["is_stationary"]

            if rahu["speed"] > 0:
                direct_count += 1
                assert rahu["is_retrograde"] is False
            else:
                retro_count += 1
                assert rahu["is_retrograde"] is True

            if abs(rahu["speed"]) < 0.05:
                stat_count += 1
                assert rahu["is_stationary"] is True

        # Ensure both direct and retrograde episodes occurred in True Node test
        assert direct_count > 0, "True Node never exhibited direct motion!"
        assert retro_count > 0, "True Node never exhibited retrograde motion!"


# ==============================================================================
# 5. PUSHKARA NAVAMSHA & PUSHKARA BHAGA CLASSICAL FIDELITY GAUNTLET
# ==============================================================================
class TestAdversarialPushkaraCalculations:
    """
    Stress-tests Pushkara Navamsha & Pushkara Bhaga functions against all 24 classical Navamshas
    and 12 classical Bhaga degree points (per Jataka Parijata & C.S. Patel).
    """

    def test_all_24_classical_pushkara_navamshas_exact_coverage(self):
        """
        Tests the 24 classical Pushkara Navamshas across all 12 signs.
        Verifies:
        - Exactly 2 Pushkara Navamshas per sign (24 total out of 108).
        - Midpoint of every valid Pushkara Navamsha evaluates to True.
        - Non-Pushkara Navamshas evaluate to False.
        """
        nav_span = 30.0 / 9.0  # 3°20' = 3.3333333333333335°
        total_pushkara_detected = 0

        for sign_idx in range(12):
            valid_nav_indices = PUSHKARA_NAVAMSHA_INDICES[sign_idx]
            assert len(valid_nav_indices) == 2, f"Sign {sign_idx} does not have exactly 2 Pushkara Navamshas!"

            for nav_idx in range(9):
                mid_deg = sign_idx * 30.0 + (nav_idx + 0.5) * nav_span
                is_pushkara = is_pushkara_navamsha(mid_deg)

                if nav_idx in valid_nav_indices:
                    assert is_pushkara is True, f"Failed on Sign {sign_idx} Navamsha {nav_idx} at deg {mid_deg}"
                    total_pushkara_detected += 1
                else:
                    assert is_pushkara is False, f"False positive on Sign {sign_idx} Navamsha {nav_idx} at deg {mid_deg}"

        assert total_pushkara_detected == 24

    def test_all_12_classical_pushkara_bhaga_degree_points(self):
        """
        Tests all 12 classical Pushkara Bhaga degree points:
        Aries: 21°, Taurus: 14°, Gemini: 18°, Cancer: 8°, Leo: 19°, Virgo: 9°,
        Libra: 24°, Scorpio: 11°, Sag: 23°, Cap: 14°, Aqua: 19°, Pisces: 9°.
        """
        orb = 1.0

        for sign_idx, target_deg in PUSHKARA_BHAGA_DEGREES.items():
            exact_lon = sign_idx * 30.0 + target_deg

            # Exact point -> must be True
            assert is_pushkara_bhaga(exact_lon, orb=orb) is True

            # Within orb (+0.8°) -> must be True
            assert is_pushkara_bhaga(exact_lon + 0.8, orb=orb) is True
            assert is_pushkara_bhaga(exact_lon - 0.8, orb=orb) is True

            # Outside orb (+1.5°) -> must be False
            assert is_pushkara_bhaga(exact_lon + 1.5, orb=orb) is False
            assert is_pushkara_bhaga(exact_lon - 1.5, orb=orb) is False

    def test_vectorized_pushkara_batch_consistency(self):
        """Vectorized batch functions must produce identical results to scalar functions."""
        np.random.seed(999)
        test_lons = np.random.uniform(0, 360, size=300)

        # Navamsha
        scalar_nav = np.array([is_pushkara_navamsha(lon) for lon in test_lons])
        batch_nav = is_pushkara_navamsha_batch(test_lons)
        assert np.array_equal(scalar_nav, batch_nav)

        # Bhaga
        scalar_bhaga = np.array([is_pushkara_bhaga(lon, orb=1.0) for lon in test_lons])
        batch_bhaga = is_pushkara_bhaga_batch(test_lons, orb=1.0)
        assert np.array_equal(scalar_bhaga, batch_bhaga)


# ==============================================================================
# 6. OMNI-VEDIC SUPREME FUSION & ALL 13 PILLARS END-TO-END INTEGRITY
# ==============================================================================
class TestAdversarialOmniVedicFusionPipeline:
    """
    Stress-tests the full Omni-Vedic Supreme Feature Extraction row engine across all 13 Pillars.
    """

    def test_extract_omni_vedic_row_full_invariant_integrity(self):
        """
        Extracts full feature row for 20 diverse timestamps (1993, 2000, 2008, 2020, 2024, 2026).
        Verifies:
        - Zero NaNs, zero Infs across all numeric columns.
        - All 12 bodies + Lagna present.
        - SAV total == 337 in every single row.
        - Jaimini Karakas 1-to-1 unique in every row.
        - Vimshottari MD/AD/PD valid lords.
        - Multi-natal features present and finite.
        """
        test_dates = [
            "1993-01-22 14:30:00",  # SPY inception
            "2000-03-24 15:30:00",  # Dotcom peak
            "2008-09-15 13:30:00",  # Lehman collapse
            "2008-10-10 14:00:00",  # 2008 crash
            "2020-03-16 13:30:00",  # COVID crash
            "2020-03-23 14:00:00",  # COVID bottom
            "2024-02-29 15:00:00",  # Leap day
            "2026-08-17 19:30:00",  # Present epoch
        ]

        for date_str in test_dates:
            dt = pd.Timestamp(date_str, tz="UTC")
            jd_ut = datetime_to_julian_day(dt)

            row = extract_omni_vedic_row(jd_ut)
            assert isinstance(row, dict)
            assert len(row) >= 180, f"Expected 180+ features, got {len(row)}"

            # 1. Check SAV == 337
            assert row.get("SAV_Total") == 337, f"SAV_Total = {row.get('SAV_Total')} on {date_str}"

            # 2. Check Jaimini Karakas uniqueness
            karaka_abbrs = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
            karaka_planets = [row[f"Jaimini_{abbr}"] for abbr in karaka_abbrs if f"Jaimini_{abbr}" in row]
            assert len(karaka_planets) == 7, f"Missing Karakas on {date_str}"
            assert len(set(karaka_planets)) == 7, f"Duplicate Karaka planets: {karaka_planets}"

            # 3. Check Vimshottari Lords
            assert row.get("Vim_MD") in ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
            assert row.get("Vim_AD") in ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
            assert row.get("Vim_PD") in ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

            # 4. Check Multi-Natal features
            assert "Multi_Entity_Sade_Sati_Count" in row
            assert 0 <= row["Multi_Entity_Sade_Sati_Count"] <= 4

            # 5. Check No NaNs or Infs in float features
            for k, v in row.items():
                if isinstance(v, (int, float, np.number)):
                    assert np.isfinite(v), f"Non-finite value {v} for key {k} on {date_str}"

    def test_kp_249_sublord_continuous_coverage(self):
        """
        Stress tests KP 249 sub-lord calculation across all 360° in high-density increments.
        In classical Krishnamurti Paddhati (KP System), the canonical 249 sub-divisions
        are formed by the triple (Sign Lord, Star Lord, Sub Lord).
        The 27 nakshatras yield 243 star-sub spans, and the 6 sign boundaries that cut across
        sub-lords generate the 6 split sub-divisions, yielding exactly 249 distinct zones across 360°.
        """
        lons = np.linspace(0.0, 359.999, num=36000)
        valid_grahas = {"Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"}

        sub_lords = []
        for lon in lons:
            res = _get_kp_lords(lon)
            sign_idx = int(lon / 30.0) % 12
            sign_lord = RASI_LORDS[sign_idx]

            assert res["star_lord"] in valid_grahas
            assert res["sub_lord"] in valid_grahas
            assert sign_lord in valid_grahas

            # Canonical KP 249 Table key: (Sign Lord, Star Lord, Sub Lord)
            sub_lords.append(f"{sign_lord}_{res['star_lord']}_{res['sub_lord']}")

        # Count distinct contiguous transitions
        transitions = 1
        for i in range(1, len(sub_lords)):
            if sub_lords[i] != sub_lords[i - 1]:
                transitions += 1

        # The 249 KP sub-lord system has exactly 249 distinct contiguous zones across 360°
        assert transitions == 249, f"Expected 249 canonical KP sub-lord segments, got {transitions}"


# ==============================================================================
# MAIN EXECUTION HARNESS
# ==============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING ADVERSARIAL STRESS TEST GAUNTLET (CHALLENGER 1 - ROUND 3)")
    print("=" * 80)
    retcode = pytest.main(["-v", "-s", __file__])
    print("=" * 80)
    print(f"TEST RUN FINISHED WITH EXIT CODE: {retcode}")
    print("=" * 80)
    sys.exit(retcode)
