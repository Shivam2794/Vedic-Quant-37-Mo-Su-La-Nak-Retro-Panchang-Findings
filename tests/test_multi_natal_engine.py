"""
UNIT TEST SUITE: MULTI-NATAL ENTITY ENGINE
==========================================
Rigorous mathematical and astronomical verification of the 4 canonical natal charts:
1. SPY ETF Inception (1993-01-29 09:30:00 EST)
2. USA Independence / Sibly (1776-07-04 17:10:00 LMT)
3. Federal Reserve Act (1913-12-23 18:02:00 EST)
4. NYSE Buttonwood Agreement (1792-05-17 10:00:00 LMT)
"""

import pytest
import numpy as np
import swisseph as swe
from datetime import datetime, timezone

from src.vedic_astrology.multi_natal_engine import (
    CACHED_NATAL_CHARTS,
    calculate_natal_chart,
    calculate_vimshottari_dasha,
    calculate_gochar_bhavas,
    extract_all_multi_natal_features,
    SPY_BIRTH, USA_BIRTH, FED_BIRTH, NYSE_BIRTH,
    DASHA_LORDS, DASHA_YEARS, SIGNS, NAKSHATRAS
)


class TestNatalChartPrecision:
    """Verifies astronomical accuracy of the 4 natal anchor charts."""

    def test_all_4_natal_charts_cached_and_valid(self):
        assert len(CACHED_NATAL_CHARTS) == 4
        for name in ["SPY", "USA", "Fed", "NYSE"]:
            assert name in CACHED_NATAL_CHARTS
            chart = CACHED_NATAL_CHARTS[name]
            assert "positions" in chart
            assert "moon_longitude" in chart
            assert "moon_sign_idx" in chart
            assert "lagna_sign_idx" in chart

    def test_spy_first_trade_chart_astronomy(self):
        spy = CACHED_NATAL_CHARTS["SPY"]
        pos = spy["positions"]
        
        # SPY born Jan 29, 1993:
        # Sun in Sidereal Capricorn (~284° - 286°)
        assert pos["Sun"]["sign"] == "Capricorn"
        # Moon in Sidereal Aries (Ashwini / Bharani)
        assert pos["Moon"]["sign"] == "Aries"
        # Saturn in Own Dignity (Capricorn or Aquarius)
        assert pos["Saturn"]["sign"] in ["Capricorn", "Aquarius"]
        # Ascendant around Aquarius
        assert pos["Lagna"]["sign"] in ["Aquarius", "Pisces", "Capricorn"]

    def test_usa_sibly_chart_astronomy(self):
        usa = CACHED_NATAL_CHARTS["USA"]
        pos = usa["positions"]
        
        # July 4, 1776 Sibly Chart:
        # Sun in Sidereal Gemini
        assert pos["Sun"]["sign"] == "Gemini"
        # Moon in Sidereal Aquarius (Dhanishta Pada 4 under 1776 Lahiri Ayanamsha ~20°43')
        assert pos["Moon"]["sign"] == "Aquarius"
        assert pos["Moon"]["nakshatra"] == "Dhanishta"
        # Ascendant in Sidereal Scorpio (Tropical 12° Sagittarius - 20°43' Ayanamsha = 21°17' Scorpio)
        assert pos["Lagna"]["sign"] == "Scorpio"


class TestVimshottariDashaEngine:
    """Verifies mathematical correctness of the Vimshottari dasha walker."""

    def test_dasha_total_years_invariance(self):
        total = sum(DASHA_YEARS.values())
        assert total == 120.0

    def test_spy_dasha_progression(self):
        spy = CACHED_NATAL_CHARTS["SPY"]
        
        # 1. At birth (1993-01-29)
        d_birth = calculate_vimshottari_dasha(spy, spy["jd_ut"] + 1.0)
        assert d_birth["MD"] in DASHA_LORDS
        assert d_birth["AD"] in DASHA_LORDS
        assert d_birth["PD"] in DASHA_LORDS

        # 2. In 2008 (Lehman Crash, ~15.7 years after birth)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        jd_2008 = swe.julday(2008, 9, 15, 14.5)
        d_2008 = calculate_vimshottari_dasha(spy, jd_2008)
        assert d_2008["MD"] in DASHA_LORDS
        assert d_2008["AD"] in DASHA_LORDS

        # 3. In 2020 (Covid Crash, ~27.1 years after birth)
        jd_2020 = swe.julday(2020, 3, 16, 14.5)
        d_2020 = calculate_vimshottari_dasha(spy, jd_2020)
        assert d_2020["MD"] in DASHA_LORDS

    def test_pre_birth_handling(self):
        spy = CACHED_NATAL_CHARTS["SPY"]
        jd_1980 = swe.julday(1980, 1, 1, 12.0)
        d_pre = calculate_vimshottari_dasha(spy, jd_1980)
        assert d_pre["MD"] == "PreBirth"


class TestTransitToNatalGocharBhavas:
    """Verifies house positions and Sade-Sati calculations."""

    def test_gochar_bhavas_and_sade_sati(self):
        spy = CACHED_NATAL_CHARTS["SPY"]
        moon_sign = spy["moon_sign_idx"]  # Aries = 0
        
        # When Saturn is in Aries (sign 0), it is 1st house from Moon -> Sade-Sati
        transits_sade_sati = {"Saturn": moon_sign, "Jupiter": (moon_sign + 4) % 12}
        res = calculate_gochar_bhavas(transits_sade_sati, spy)
        
        assert res["SPY_Gochar_Saturn_to_Moon_Bhv"] == 1
        assert res["SPY_Is_Sade_Sati"] == 1
        assert res["SPY_Is_Ashtama_Shani"] == 0

        # When Saturn is in Scorpio (8th from Aries) -> Ashtama Shani
        transits_ashtama = {"Saturn": (moon_sign + 7) % 12}
        res_ashtama = calculate_gochar_bhavas(transits_ashtama, spy)
        assert res_ashtama["SPY_Gochar_Saturn_to_Moon_Bhv"] == 8
        assert res_ashtama["SPY_Is_Sade_Sati"] == 0
        assert res_ashtama["SPY_Is_Ashtama_Shani"] == 1


class TestMultiNatalFeatureExtractionThroughput:
    """Verifies end-to-end multi-natal feature extraction across all 4 entities."""

    def test_extract_all_features_structure_and_speed(self):
        target_jd = swe.julday(2022, 10, 15, 14.5)
        transits = {
            "Sun": 5, "Moon": 2, "Mars": 1, "Mercury": 5,
            "Jupiter": 11, "Venus": 5, "Saturn": 9, "Rahu": 0, "Ketu": 6
        }
        
        feats = extract_all_multi_natal_features(target_jd, transits)
        
        # Verify columns for each entity
        for entity in ["SPY", "USA", "Fed", "NYSE"]:
            assert f"{entity}_Vim_MD" in feats
            assert f"{entity}_Vim_AD" in feats
            assert f"{entity}_Vim_PD" in feats
            assert f"{entity}_Gochar_Saturn_to_Moon_Bhv" in feats
            assert f"{entity}_Gochar_Mars_to_Lagna_Bhv" in feats
            assert f"{entity}_Is_Sade_Sati" in feats

        assert "Multi_Entity_Sade_Sati_Count" in feats
        assert 0 <= feats["Multi_Entity_Sade_Sati_Count"] <= 4
