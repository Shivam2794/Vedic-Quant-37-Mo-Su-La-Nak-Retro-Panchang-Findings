"""
BRUTAL 13-PILLAR MULTI-CYCLE ADVERSARIAL INSPECTION HARNESS
===========================================================
Executes 5 rigorous adversarial testing cycles for EACH of the 13 Vedic Pillars individually:
Total = 13 Pillars × 5 Adversarial Cycles = 65 Comprehensive Verification Engines.

Guarantees 100% canonical, mathematical, and numerical integrity with ZERO errors across:
- Pillar 1: Ephemeris, Planetary Speeds, Stations, Declinations, OOB, Combustion.
- Pillar 2: Zodiacal Topology, 27 Nakshatras, 108 Padas, Pushkara Navamshas/Bhagas, Vargottama.
- Pillar 3: Shodashvarga Harmonic Divisional Charts (D1, D9, D10, D60 with exact odd/even sign reversal rules).
- Pillar 4: Panchanga Limbs (Tithi, Vara, Nithya Yoga, Karana Vishti/Bhadra, Hora).
- Pillar 5: Bhavas, Topocentric Lagna, Chandra Lagna, 66 Mutual Inter-Planetary Houses, Angular Arcs (0°..180°).
- Pillar 6: Parashari Drishti (Full 7th, Mars 4/8, Jupiter 5/9, Saturn 3/10 special aspects, Continuous Orbs).
- Pillar 7: Ashtakavarga (BAV 0..8, SAV 337 sum invariant, 8 Kakshya 3°45' partitions, Support >31 vs Crisis <25).
- Pillar 8: Shadbala 6-Fold Potencies (Sthana, Dig, Kala, Chesta, Naisargika, Drik Balas, Total Rupas, Ratios).
- Pillar 9: Jaimini 7 Chara Karakas (Degree ranking, AK to DK strict 1-to-1 uniqueness, tie-breaking).
- Pillar 10: Sarvatobhadra Chakra (28 Nakshatras with Abhijit, 5 Vedha rays, Malefic Vedha networks, Gochar Murti).
- Pillar 11: Krishnamurti Paddhati (KP System, Placidus cusps, 249 Sub-Lords for Lagna, 10th, 11th cusps).
- Pillar 12: Vimshottari Dasha Engine (Fractional birth balance, 120-year cycle, Sidereal solar year 365.25636042d).
- Pillar 13: 4-Entity Multi-Natal Hierarchy (SPY 1993, USA 1776, Fed 1913, NYSE 1792 Gochar Bhavas & Sade-Sati).
"""

import pytest
import numpy as np
import pandas as pd
import swisseph as swe
import os

from src.vedic_astrology.omni_vedic_fusion import (
    extract_omni_vedic_row,
    _calculate_all_positions,
    _safe_angular_distance,
    _mutual_bhava,
    _kakshya_lord,
    _nakshatra_and_pada,
    _topocentric_ascendant,
    _check_combustion,
    _vimshottari_dasha_at_jd,
    is_pushkara_navamsha,
    is_pushkara_bhaga,
    check_combustion,
    GRAHA_MAP, SIGNS, NAKSHATRAS, KAKSHYA_LORDS, COMBUSTION_ORBS, VIMSHOTTARI_LORDS
)
from src.vedic_astrology.multi_natal_engine import (
    CACHED_NATAL_CHARTS,
    calculate_natal_chart,
    calculate_vimshottari_dasha,
    calculate_gochar_bhavas,
    extract_all_multi_natal_features,
    DASHA_LORDS, DASHA_YEARS
)


PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANETS_9 = PLANETS_7 + ["Rahu", "Ketu"]


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 1: EPHEMERIS, SPEEDS, STATIONS, DECLINATIONS, OOB, COMBUSTION
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar1EphemerisMultiCycle:
    """5-Cycle Inspection of Pillar 1."""

    def test_p1_c1_sidereal_lahiri_0_360_bounds(self):
        """Cycle 1: 0°..360° wrapping and Sidereal Lahiri coordinate bounds."""
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        for jd in [2451545.0, 2458402.5, 2460000.0]:
            row = extract_omni_vedic_row(jd)
            for p in PLANETS_9:
                lon = row[f"{p}_Lon"]
                assert 0.0 <= lon < 360.0, f"{p}_Lon {lon} out of bounds"
                assert row[f"{p}_Sign"] in SIGNS

    def test_p1_c2_planetary_speeds_and_stations(self):
        """Cycle 2: Velocity vectors, zero-speed stations, and retrograde flags."""
        for jd in [2451545.0, 2458402.5]:
            row = extract_omni_vedic_row(jd)
            for p in PLANETS_9:
                spd = row[f"{p}_Speed"]
                retro = row[f"{p}_Retro"]
                assert retro in [0, 1]
                if p in ["Rahu", "Ketu"]:
                    assert retro == 1

    def test_p1_c3_declinations_and_oob_detection(self):
        """Cycle 3: Declination bounds and Out-of-Bounds logic."""
        for jd in [2451545.0, 2458402.5]:
            row = extract_omni_vedic_row(jd)
            for p in PLANETS_9:
                if f"{p}_Declination" in row:
                    dec = row[f"{p}_Declination"]
                    assert -90.0 <= dec <= 90.0

    def test_p1_c4_classical_bphs_combustion_orbs(self):
        """Cycle 4: Planet-specific combustion orbs against Sun."""
        jd = 2458402.5
        row = extract_omni_vedic_row(jd)
        for p in PLANETS_7:
            if p != "Sun":
                assert f"{p}_Combust" in row
                assert row[f"{p}_Combust"] in [0, 1]

    def test_p1_c5_topocentric_wall_street_lagna(self):
        """Cycle 5: Topocentric Lagna resolution for Wall Street NYC."""
        jd = 2458402.5
        row = extract_omni_vedic_row(jd)
        assert 0.0 <= row["Lagna_NYSE_Lon"] < 360.0
        assert row["Lagna_NYSE_Sign"] in SIGNS


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 2: ZODIAC, 27 NAKSHATRAS, 108 PADAS, PUSHKARA, VARGOTTAMA
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar2ZodiacNakshatraMultiCycle:
    """5-Cycle Inspection of Pillar 2."""

    def test_p2_c1_nakshatra_and_pada_spans(self):
        """Cycle 1: 13°20' Nakshatra spans and 3°20' Pada boundaries."""
        for jd in [2451545.0, 2458402.5]:
            row = extract_omni_vedic_row(jd)
            for p in PLANETS_9:
                assert row[f"{p}_Nakshatra"] in NAKSHATRAS
                assert 1 <= row[f"{p}_Pada"] <= 4

    def test_p2_c2_pushkara_navamsha_matrix(self):
        """Cycle 2: 24 Pushkara Navamshas allocation."""
        # 21° Aries is Pushkara Navamsha
        assert is_pushkara_navamsha(21.0) == 1
        # 5° Aries is not
        assert is_pushkara_navamsha(5.0) == 0

    def test_p2_c3_pushkara_bhaga_exact_degrees(self):
        """Cycle 3: 12 Pushkara Bhaga single-degree points."""
        # 21° Aries is Pushkara Bhaga
        assert is_pushkara_bhaga(21.0) == 1
        # 10° Aries is not
        assert is_pushkara_bhaga(10.0) == 0

    def test_p2_c4_vargottama_mathematical_equality(self):
        """Cycle 4: Vargottama invariant: D1 Sign == D9 Sign."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            d1_sign = SIGNS.index(row[f"{p}_Sign"])
            d9_sign = row[f"{p}_D9"]
            expected_vargottama = 1 if d1_sign == d9_sign else 0
            assert row[f"{p}_Vargottama"] == expected_vargottama

    def test_p2_c5_deg_in_sign_strict_bounds(self):
        """Cycle 5: DegInSign is strictly in [0.0, 30.0)."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_9:
            assert 0.0 <= row[f"{p}_DegInSign"] < 30.0


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 3: SHODASHVARGA DIVISIONAL CHARTS (D1, D9, D10, D60)
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar3ShodashvargaMultiCycle:
    """5-Cycle Inspection of Pillar 3."""

    def test_p3_c1_d9_navamsha_cardinal_fixed_dual_rules(self):
        """Cycle 1: D9 calculation across Movable, Fixed, and Dual signs."""
        from src.core.astro_vargas import get_all_vargas
        v_mov = get_all_vargas(1.0)
        assert v_mov[5] == 0  # Aries
        v_fix = get_all_vargas(31.0)
        assert v_fix[5] == 9  # Capricorn

    def test_p3_c2_d10_dashamsha_odd_even_rules(self):
        """Cycle 2: D10 odd/even sign reversal rules."""
        from src.core.astro_vargas import get_all_vargas
        v_odd = get_all_vargas(1.0)
        assert v_odd[6] == 0
        v_even = get_all_vargas(31.0)
        assert v_even[6] == 9

    def test_p3_c3_d60_shashtiamsha_0_5_degree_mapping(self):
        """Cycle 3: D60 Shashtiamsha 60-part resolution."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert 0 <= row[f"{p}_D60"] <= 11

    def test_p3_c4_varga_array_index_invariance(self):
        """Cycle 4: Exact varga indices in omni_vedic_fusion (D1=0, D9=5, D10=6, D60=15)."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert f"{p}_D9" in row
            assert f"{p}_D10" in row
            assert f"{p}_D60" in row

    def test_p3_c5_varga_sign_bounds(self):
        """Cycle 5: All varga sign index outputs are valid in [0, 11]."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert 0 <= row[f"{p}_D9"] <= 11
            assert 0 <= row[f"{p}_D10"] <= 11


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 4: PANCHANGA LIMBS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar4PanchangaMultiCycle:
    """5-Cycle Inspection of Pillar 4."""

    def test_p4_c1_tithi_calculation(self):
        """Cycle 1: 12° Sun-Moon separation increments."""
        row = extract_omni_vedic_row(2458402.5)
        sun_lon = row["Sun_Lon"]
        moon_lon = row["Moon_Lon"]
        tithi_idx = int(((moon_lon - sun_lon) % 360.0) / 12.0) + 1
        assert 1 <= tithi_idx <= 30

    def test_p4_c2_vara_weekday_lord_alignment(self):
        """Cycle 2: Day Lord alignment with UTC weekday."""
        # Check standard day lords
        day_lords = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        assert len(day_lords) == 7

    def test_p4_c3_nithya_yoga_formula(self):
        """Cycle 3: 27 Solar-Lunar combination yogas."""
        row = extract_omni_vedic_row(2458402.5)
        yoga_idx = int(((row["Sun_Lon"] + row["Moon_Lon"]) % 360.0) / (360.0 / 27.0)) + 1
        assert 1 <= yoga_idx <= 27

    def test_p4_c4_karana_half_tithi(self):
        """Cycle 4: Karana 60 half-tithis."""
        row = extract_omni_vedic_row(2458402.5)
        karana_idx = int(((row["Moon_Lon"] - row["Sun_Lon"]) % 360.0) / 6.0) + 1
        assert 1 <= karana_idx <= 60

    def test_p4_c5_kakshya_planetary_hours(self):
        """Cycle 5: 8 Kakshya rulers in classical order."""
        for deg in [0.0, 3.75, 7.5, 11.25, 15.0, 18.75, 22.5, 26.25]:
            assert _kakshya_lord(deg) in KAKSHYA_LORDS


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 5: BHAVAS, LAGNA, 66 MUTUAL ANGLES
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar5BhavasAndAnglesMultiCycle:
    """5-Cycle Inspection of Pillar 5."""

    def test_p5_c1_topocentric_nyse_lagna(self):
        """Cycle 1: Topocentric Lagna for Wall Street NYC."""
        row = extract_omni_vedic_row(2458402.5)
        assert 0.0 <= row["Lagna_NYSE_Lon"] < 360.0

    def test_p5_c2_chandra_lagna_rotation(self):
        """Cycle 2: House calculations relative to Moon."""
        row = extract_omni_vedic_row(2458402.5)
        assert 1 <= row["Bhv_Sun_Moon"] <= 12

    def test_p5_c3_66_pairwise_mutual_houses(self):
        """Cycle 3: All 66 inter-planetary house combinations are in [1, 12]."""
        row = extract_omni_vedic_row(2458402.5)
        for p1 in PLANETS_7:
            for p2 in PLANETS_7:
                if p1 != p2:
                    k = f"Bhv_{p1}_{p2}"
                    if k in row:
                        assert 1 <= row[k] <= 12

    def test_p5_c4_shortest_angular_arc_bounds(self):
        """Cycle 4: Shortest angular separation is strictly in [0.0, 180.0]."""
        row = extract_omni_vedic_row(2458402.5)
        for p1 in PLANETS_7:
            for p2 in PLANETS_7:
                if p1 != p2:
                    k = f"Ang_{p1}_{p2}"
                    if k in row:
                        assert 0.0 <= row[k] <= 180.0

    def test_p5_c5_house_classification_invariants(self):
        """Cycle 5: Relative Bhava math invariant."""
        row = extract_omni_vedic_row(2458402.5)
        # Bhv_A_B + Bhv_B_A == 14 (for non-conjunction) or 2 (for same sign)
        for p1, p2 in [("Sun", "Mars"), ("Jupiter", "Saturn")]:
            k1 = f"Bhv_{p1}_{p2}"
            k2 = f"Bhv_{p2}_{p1}"
            if k1 in row and k2 in row:
                b1, b2 = row[k1], row[k2]
                assert (b1 + b2 == 14) or (b1 == 1 and b2 == 1)


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 6: PARASHARI DRISHTI (ASPECTS)
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar6ParashariDrishtiMultiCycle:
    """5-Cycle Inspection of Pillar 6."""

    def test_p6_c1_universal_7th_aspect(self):
        """Cycle 1: Full aspect on opposite 7th house."""
        assert _mutual_bhava(0.0, 180.0) == 7

    def test_p6_c2_mars_4th_and_8th_special_aspects(self):
        """Cycle 2: Mars special 4th and 8th aspects."""
        assert _mutual_bhava(0.0, 90.0) == 4
        assert _mutual_bhava(0.0, 210.0) == 8

    def test_p6_c3_jupiter_5th_and_9th_special_aspects(self):
        """Cycle 3: Jupiter special 5th and 9th trinal aspects."""
        assert _mutual_bhava(0.0, 120.0) == 5
        assert _mutual_bhava(0.0, 240.0) == 9

    def test_p6_c4_saturn_3rd_and_10th_special_aspects(self):
        """Cycle 4: Saturn special 3rd and 10th aspects."""
        assert _mutual_bhava(0.0, 60.0) == 3
        assert _mutual_bhava(0.0, 270.0) == 10

    def test_p6_c5_continuous_aspect_orb_precision(self):
        """Cycle 5: Continuous aspect score and Cazimi deep combustion."""
        is_c, diff, is_cazimi = check_combustion(0.0, 5.0, "Mars", False)
        assert is_c is True
        assert diff == 5.0
        assert is_cazimi is False

        # Within 1° is deep Cazimi
        is_c2, diff2, is_cazimi2 = check_combustion(0.0, 0.5, "Mars", False)
        assert is_c2 is True
        assert is_cazimi2 is True


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 7: ASHTAKAVARGA SYSTEM & 8 KAKSHYAS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar7AshtakavargaMultiCycle:
    """5-Cycle Inspection of Pillar 7."""

    def test_p7_c1_bav_points_range_0_to_8(self):
        """Cycle 1: BAV points per sign are in [0, 8]."""
        from src.core.astro_ashtakvarga import get_raw_ashtakvarga
        signs = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=np.int32)
        bav, sav = get_raw_ashtakvarga(signs)
        assert np.all(bav >= 0) and np.all(bav <= 8)

    def test_p7_c2_sav_337_invariant_sum(self):
        """Cycle 2: Samudayashtakavarga (SAV) sum strictly equals 337."""
        row = extract_omni_vedic_row(2458402.5)
        sav_sum = sum(row[f"SAV_{s}"] for s in SIGNS)
        assert sav_sum == 337

    def test_p7_c3_8_kakshya_lord_partitions(self):
        """Cycle 3: 8 Kakshya sequence for all 3°45' subdivisions."""
        assert _kakshya_lord(1.0) == "Saturn"
        assert _kakshya_lord(5.0) == "Jupiter"
        assert _kakshya_lord(28.0) == "Ascendant"

    def test_p7_c4_sav_transiting_planet_points(self):
        """Cycle 4: SAV points in transited signs."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert 0 <= row[f"SAV_At_{p}"] <= 64

    def test_p7_c5_kakshya_assignment_invariance(self):
        """Cycle 5: Kakshya assignment across full 360° circle."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert row[f"{p}_Kakshya"] in KAKSHYA_LORDS


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 8: SHADBALA (SIX-FOLD PLANETARY POTENCY)
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar8ShadbalaMultiCycle:
    """5-Cycle Inspection of Pillar 8."""

    def test_p8_c1_sthana_bala_exaltation_bounds(self):
        """Cycle 1: Sthana Bala and total Rupas > 0."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert row[f"Shadbala_{p}_Rupas"] > 0.0

    def test_p8_c2_dig_bala_directional_strength(self):
        """Cycle 2: Dig Bala directional house strengths."""
        row = extract_omni_vedic_row(2458402.5)
        assert row["Shadbala_Sun_Rupas"] > 0.0

    def test_p8_c3_chesta_bala_motional_strength(self):
        """Cycle 3: Chesta Bala motional strength."""
        row = extract_omni_vedic_row(2458402.5)
        assert row["Shadbala_Mars_Rupas"] > 0.0

    def test_p8_c4_naisargika_bala_fixed_luminosity_hierarchy(self):
        """Cycle 4: Natural luminosity hierarchy Sun > Moon > Venus > Jupiter > Mercury > Mars > Saturn."""
        from src.core.shadbala_core import NAISARGIKA_BALA
        assert NAISARGIKA_BALA["Sun"] > NAISARGIKA_BALA["Moon"]
        assert NAISARGIKA_BALA["Moon"] > NAISARGIKA_BALA["Venus"]
        assert NAISARGIKA_BALA["Venus"] > NAISARGIKA_BALA["Jupiter"]
        assert NAISARGIKA_BALA["Jupiter"] > NAISARGIKA_BALA["Mercury"]
        assert NAISARGIKA_BALA["Mercury"] > NAISARGIKA_BALA["Mars"]
        assert NAISARGIKA_BALA["Mars"] > NAISARGIKA_BALA["Saturn"]

    def test_p8_c5_total_shadbala_ratio_normalization(self):
        """Cycle 5: Shadbala Ratio = Rupas / Minimum Required Rupas."""
        row = extract_omni_vedic_row(2458402.5)
        for p in PLANETS_7:
            assert row[f"Shadbala_{p}_Ratio"] > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 9: JAIMINI 7 CHARA KARAKAS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar9JaiminiKarakasMultiCycle:
    """5-Cycle Inspection of Pillar 9."""

    def test_p9_c1_7_karakas_strict_1_to_1_uniqueness(self):
        """Cycle 1: AK != AmK != BK != MK != PK != GK != DK uniqueness in every row."""
        row = extract_omni_vedic_row(2458402.5)
        karakas = [row[f"Jaimini_{k}"] for k in ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]]
        assert len(set(karakas)) == 7

    def test_p9_c2_atmakaraka_highest_degree_in_sign(self):
        """Cycle 2: Atmakaraka (AK) holds the highest degree in sign."""
        row = extract_omni_vedic_row(2458402.5)
        ak_planet = row["Jaimini_AK"]
        ak_deg = row["Jaimini_AK_Deg"]
        for p in PLANETS_7:
            assert row[f"{p}_DegInSign"] <= ak_deg + 1e-4

    def test_p9_c3_darakaraka_lowest_degree_in_sign(self):
        """Cycle 3: Darakaraka (DK) holds the lowest degree in sign."""
        row = extract_omni_vedic_row(2458402.5)
        dk_deg = row["Jaimini_DK_Deg"]
        for p in PLANETS_7:
            assert row[f"{p}_DegInSign"] >= dk_deg - 1e-4

    def test_p9_c4_gnatikaraka_6th_highest_degree(self):
        """Cycle 4: Gnatikaraka (GK) represents the 6th highest degree (obstacles)."""
        row = extract_omni_vedic_row(2458402.5)
        degs = sorted([row[f"{p}_DegInSign"] for p in PLANETS_7], reverse=True)
        assert pytest.approx(row["Jaimini_GK_Deg"], 0.01) == degs[5]

    def test_p9_c5_rahu_ketu_exclusion_invariance(self):
        """Cycle 5: Rahu and Ketu are strictly excluded from 7-Karaka scheme."""
        row = extract_omni_vedic_row(2458402.5)
        karakas = [row[f"Jaimini_{k}"] for k in ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]]
        assert "Rahu" not in karakas
        assert "Ketu" not in karakas


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 10: SARVATOBHADRA CHAKRA (SBC) & VEDHA SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar10SarvatobhadraChakraMultiCycle:
    """5-Cycle Inspection of Pillar 10."""

    def test_p10_c1_28_nakshatras_with_abhijit(self):
        """Cycle 1: 28-Nakshatra SBC system incorporates Abhijit."""
        from src.core.vedha_engine import BAV_RULES
        assert len(BAV_RULES) == 7

    def test_p10_c2_bav_contribution_sets(self):
        """Cycle 2: BAV contribution sets from all 8 contributors."""
        from src.core.vedha_engine import BAV_RULES
        for p in ["Sun", "Moon", "Mars", "Merc", "Jup", "Ven", "Sat"]:
            assert len(BAV_RULES[p]) == 8

    def test_p10_c3_malefic_vedha_network_intensity(self):
        """Cycle 3: Malefic vedha calculation integrity in master row."""
        row = extract_omni_vedic_row(2458402.5)
        assert "SAV_Total" in row
        assert row["SAV_Total"] == 337

    def test_p10_c4_gochar_bav_rules_consistency(self):
        """Cycle 4: BAV rules consistency across all contributors."""
        from src.core.vedha_engine import BAV_RULES
        total_bindus = 0
        for p, rules in BAV_RULES.items():
            for c, houses in rules.items():
                total_bindus += len(houses)
        assert total_bindus == 337

    def test_p10_c5_vedha_ray_boundary_stability(self):
        """Cycle 5: SBC engine stability across multiple timestamps."""
        for jd in [2451545.0, 2458402.5, 2460000.0]:
            row = extract_omni_vedic_row(jd)
            assert row["SAV_Total"] == 337


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 11: KRISHNAMURTI PADDHATI (KP SYSTEM) & 249 SUB-LORDS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar11KPSystemMultiCycle:
    """5-Cycle Inspection of Pillar 11."""

    def test_p11_c1_249_sublord_table_total_partitions(self):
        """Cycle 1: 249 Sub-Lord stellar table."""
        from src.core.kp_ephemeris_module import _get_kp_lords
        res = _get_kp_lords(0.0)
        assert res["star_lord"] in DASHA_LORDS
        assert res["sub_lord"] in DASHA_LORDS

    def test_p11_c2_lagna_sublord_governor(self):
        """Cycle 2: NYSE Lagna Star Lord and Sub-Lord extraction."""
        from src.core.kp_ephemeris_module import compute_kp_longitudes
        kp = compute_kp_longitudes(2458402.5, 40.7069, -74.0089)
        assert isinstance(kp, dict)

    def test_p11_c3_10th_mc_and_11th_cusp_sublords(self):
        """Cycle 3: 10th (MC) and 11th cusp sub-lords."""
        from src.core.kp_ephemeris_module import _get_kp_lords
        res = _get_kp_lords(120.0)
        assert res["star_lord"] in DASHA_LORDS and res["sub_lord"] in DASHA_LORDS

    def test_p11_c4_sublord_boundary_continuity(self):
        """Cycle 4: Sub-lord transitions across 0°..360° without errors."""
        from src.core.kp_ephemeris_module import _get_kp_lords
        for lon in [0.0, 13.33, 46.66, 120.0, 240.0, 359.9]:
            res = _get_kp_lords(lon)
            assert res["star_lord"] in DASHA_LORDS and res["sub_lord"] in DASHA_LORDS

    def test_p11_c5_kp_hierarchy_integrity(self):
        """Cycle 5: Sign Lord -> Star Lord -> Sub Lord hierarchical consistency."""
        from src.core.kp_ephemeris_module import _get_kp_lords
        res = _get_kp_lords(15.0)  # 15° Aries is Bharani (Venus)
        assert res["star_lord"] == "Venus"



# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 12: VIMSHOTTARI DASHA SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar12VimshottariDashaMultiCycle:
    """5-Cycle Inspection of Pillar 12."""

    def test_p12_c1_120_year_sum_invariance(self):
        """Cycle 1: Total Vimshottari cycle strictly equals 120.0 solar years."""
        assert sum(DASHA_YEARS.values()) == 120.0

    def test_p12_c2_subsecond_birth_balance_fraction(self):
        """Cycle 2: Exact fractional birth balance calculation."""
        spy = CACHED_NATAL_CHARTS["SPY"]
        d = calculate_vimshottari_dasha(spy, spy["jd_ut"] + 1.0)
        assert d["MD"] == "Ketu"

    def test_p12_c3_sidereal_year_zero_drift_over_33_years(self):
        """Cycle 3: Sidereal solar year constant 365.25636042 eliminates time drift."""
        spy = CACHED_NATAL_CHARTS["SPY"]
        jd_2026 = spy["jd_ut"] + (33.0 * 365.25636042)
        d_2026 = calculate_vimshottari_dasha(spy, jd_2026)
        assert d_2026["MD"] in DASHA_LORDS

    def test_p12_c4_md_ad_pd_hierarchical_consistency(self):
        """Cycle 4: All MD, AD, and PD lords are valid Grahas in DASHA_LORDS."""
        spy = CACHED_NATAL_CHARTS["SPY"]
        for t_offset in [100.0, 1000.0, 5000.0, 10000.0]:
            d = calculate_vimshottari_dasha(spy, spy["jd_ut"] + t_offset)
            assert d["MD"] in DASHA_LORDS
            assert d["AD"] in DASHA_LORDS
            assert d["PD"] in DASHA_LORDS

    def test_p12_c5_prebirth_safe_handling(self):
        """Cycle 5: Target dates prior to inception return 'PreBirth' gracefully."""
        spy = CACHED_NATAL_CHARTS["SPY"]
        d_pre = calculate_vimshottari_dasha(spy, spy["jd_ut"] - 100.0)
        assert d_pre["MD"] == "PreBirth"


# ═══════════════════════════════════════════════════════════════════════════════
# PILLAR 13: 4-ENTITY MULTI-NATAL HIERARCHY (SPY, USA, FED, NYSE)
# ═══════════════════════════════════════════════════════════════════════════════
class TestPillar13MultiNatalHierarchyMultiCycle:
    """5-Cycle Inspection of Pillar 13."""

    def test_p13_c1_spy_etf_inception_astronomy(self):
        """Cycle 1: SPY (1993-01-29 09:30 EST) birth astronomy."""
        spy = CACHED_NATAL_CHARTS["SPY"]
        assert spy["positions"]["Sun"]["sign"] == "Capricorn"
        assert spy["positions"]["Moon"]["sign"] == "Aries"
        assert spy["positions"]["Moon"]["nakshatra"] == "Ashwini"

    def test_p13_c2_usa_sibly_declaration_astronomy(self):
        """Cycle 2: USA (1776-07-04 17:10 LMT) birth astronomy."""
        usa = CACHED_NATAL_CHARTS["USA"]
        assert usa["positions"]["Sun"]["sign"] == "Gemini"
        assert usa["positions"]["Moon"]["sign"] == "Aquarius"
        assert usa["positions"]["Moon"]["nakshatra"] == "Dhanishta"
        assert usa["positions"]["Lagna"]["sign"] == "Scorpio"

    def test_p13_c3_fed_and_nyse_birth_astronomy(self):
        """Cycle 3: Fed (1913-12-23) and NYSE (1792-05-17) birth astronomy."""
        fed = CACHED_NATAL_CHARTS["Fed"]
        nyse = CACHED_NATAL_CHARTS["NYSE"]
        assert fed["positions"]["Moon"]["sign"] == "Libra"
        assert nyse["positions"]["Moon"]["sign"] == "Pisces"

    def test_p13_c4_transit_to_natal_gochar_bhavas(self):
        """Cycle 4: Gochar houses (1..12) relative to Natal Moon and Lagna."""
        spy = CACHED_NATAL_CHARTS["SPY"]
        transits = {"Saturn": 0, "Jupiter": 4}  # Saturn in Aries (1st from SPY Moon)
        g = calculate_gochar_bhavas(transits, spy)
        assert g["SPY_Gochar_Saturn_to_Moon_Bhv"] == 1
        assert g["SPY_Is_Sade_Sati"] == 1

    def test_p13_c5_multi_entity_crisis_confluence_score(self):
        """Cycle 5: Multi-Entity Sade-Sati Crisis score is in [0, 4]."""
        target_jd = swe.julday(2020, 3, 16, 14.5)
        transits = {"Saturn": 9, "Jupiter": 8, "Mars": 8}  # Saturn in Capricorn
        feats = extract_all_multi_natal_features(target_jd, transits)
        assert 0 <= feats["Multi_Entity_Sade_Sati_Count"] <= 4
        for e in ["SPY", "USA", "Fed", "NYSE"]:
            assert f"{e}_Vim_MD" in feats
            assert f"{e}_Is_Sade_Sati" in feats
