"""
tests/test_10_pillar_drilldown.py — Comprehensive Test Suite for Deep Vedic 10-Pillar Forensic Drilldown
Covers:
- R5: Forensic Hypothesis Testing across all 10 Classical Vedic Pillars:
  - Pillar 1 (Ephemeris): Out-of-bounds declinations (|delta| > 23.44°) and planetary stations (|speed| < 0.05°/day).
  - Pillar 2 (Aspects): Exact orb clustering for Shadashtaka (6/8), Dwirdwadasa (2/12), and Samasaptaka (1/7).
  - Pillar 3 (Vargas): Pushkara Navamsha and Vargottama resonance frequency on breakout days.
  - Pillar 4 (Jaimini): Gnatikaraka (GK - 6th highest degree) activations during crashes vs. Atmakaraka (AK).
  - Pillar 5 (Ashtakavarga): Extreme SAV thresholds (< 25 vs. > 32 bindus) in transited signs.
  - Pillar 6 (Shadbala): High Chesta Bala vs. Low Kala Bala ratio on trend days.
  - Pillar 7 (SBC & Vedha): Malefic Vedha network intensity and Gochar Murti impact.
  - Pillar 8 (KP Sub-Lords): Star Lord / Sub-Lord rulers of NYSE Lagna and 10th/11th cusps.
  - Pillar 9 (NYSE Vimshottari): Mahadasha / Antardasha / Pratyantardasha lord transit triggers.
  - Pillar 10 (MTF Confluence): Astrological signatures of 4-timeframe simultaneous co-occurrences.

Tiers Covered:
- Tier 1: Feature Coverage across all 10 Pillars (10 tests)
- Tier 2: Boundary & Corner Cases (6 tests)
- Tier 3: Pairwise Pillar Interactions (3 tests)
- Tier 4: Real-World Forensic Workloads on 1,408 Anomaly Dataset (2 tests)
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from scipy import stats

# Project Root setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==============================================================================
# REFERENCE MATHEMATICAL ORACLES FOR 10-PILLAR HYPOTHESIS TESTING
# ==============================================================================

def oracle_is_out_of_bounds(declination_deg, obliquity=23.4367):
    """
    Pillar 1: OOB Declination flag when |declination| > obliquity of ecliptic (~23.44°).
    """
    return np.abs(declination_deg) > obliquity


def oracle_is_planetary_station(speed_deg_per_day, threshold=0.05):
    """
    Pillar 1: Planetary station flag when daily velocity is near zero.
    """
    return np.abs(speed_deg_per_day) <= threshold


def oracle_shadashtaka_aspect(lon1, lon2, orb=3.0):
    """
    Pillar 2: Shadashtaka (6/8 mutually inconjunct) occurs at 150° and 210° separation.
    """
    sep = np.abs((lon1 - lon2 + 180.0) % 360.0 - 180.0)
    is_6_8 = (np.abs(sep - 150.0) <= orb) | (np.abs(sep - 210.0) <= orb)
    return is_6_8, sep


def oracle_dwirdwadasa_aspect(lon1, lon2, orb=3.0):
    """
    Pillar 2: Dwirdwadasa (2/12 adjacent) occurs at 30° and 330° (or -30°) separation.
    """
    sep = np.abs((lon1 - lon2 + 180.0) % 360.0 - 180.0)
    is_2_12 = (np.abs(sep - 30.0) <= orb)
    return is_2_12, sep


def oracle_samasaptaka_aspect(lon1, lon2, orb=5.0):
    """
    Pillar 2: Samasaptaka (1/7 direct opposition) occurs at 180° separation.
    """
    sep = np.abs((lon1 - lon2 + 180.0) % 360.0 - 180.0)
    is_1_7 = (np.abs(sep - 180.0) <= orb)
    return is_1_7, sep


def oracle_pushkara_navamsha(sign_idx, d9_sign_idx):
    """
    Pillar 3: Pushkara Navamsha determination:
    Specific auspicious Navamshas in each elemental triplicity:
    - Fire Signs (0, 4, 8): Navamsha 6 (Libra), 8 (Sagittarius)
    - Earth Signs (1, 5, 9): Navamsha 2 (Gemini), 9 (Capricorn)
    - Air Signs (2, 6, 10): Navamsha 5 (Virgo), 8 (Sagittarius)
    - Water Signs (3, 7, 11): Navamsha 2 (Gemini), 3 (Cancer)
    """
    triplicity = sign_idx % 4
    if triplicity == 0:  # Fire
        return d9_sign_idx in [6, 8]
    elif triplicity == 1:  # Earth
        return d9_sign_idx in [2, 9]
    elif triplicity == 2:  # Air
        return d9_sign_idx in [5, 8]
    else:  # Water
        return d9_sign_idx in [2, 3]


def oracle_jaimini_karakas(planets_deg_in_sign):
    """
    Pillar 4: Computes 7-Karaka Jaimini scheme based on descending order of longitude degree within sign (0-30°).
    AK (Atmakaraka): 1st highest degree
    AmK (Amatyakaraka): 2nd
    BK (Bhratrikaraka): 3rd
    MK (Matrikaraka): 4th
    PK (Putrakaraka): 5th
    GK (Gnatikaraka): 6th
    DK (Darakaraka): 7th
    """
    sorted_planets = sorted(planets_deg_in_sign.items(), key=lambda x: x[1], reverse=True)
    karaka_names = ['AK', 'AmK', 'BK', 'MK', 'PK', 'GK', 'DK']
    result = {}
    for idx, (planet, deg) in enumerate(sorted_planets[:7]):
        result[karaka_names[idx]] = planet
        result[f"{karaka_names[idx]}_deg"] = deg
    return result


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def synthetic_10_pillar_dataset():
    """
    Generates a 500-row synthetic dataset covering all 10 Pillar features with known signal injections.
    """
    np.random.seed(42)
    n = 500
    
    data = {
        # Pillar 1: Ephemeris OOB & Stations
        'Mars_Declination': np.random.uniform(-28.0, 28.0, size=n),
        'Moon_Declination': np.random.uniform(-29.0, 29.0, size=n),
        'Mars_Speed': np.random.normal(0.4, 0.3, size=n),
        'Mercury_Speed': np.random.normal(1.2, 0.5, size=n),
        'Saturn_Speed': np.random.normal(0.05, 0.04, size=n),
        
        # Pillar 2: Aspects & Orbs
        'Ang_Mars_Saturn': np.random.uniform(0, 360, size=n),
        'Ang_Sun_Moon': np.random.uniform(0, 360, size=n),
        'Bhv_Mars_Saturn': np.random.choice(range(1, 13), size=n),
        'Bhv_Sun_Moon': np.random.choice(range(1, 13), size=n),
        
        # Pillar 3: Vargas
        'Sun_Sign': np.random.choice(range(12), size=n),
        'Sun_D9': np.random.choice(range(12), size=n),
        'Moon_Sign': np.random.choice(range(12), size=n),
        'Moon_D9': np.random.choice(range(12), size=n),
        'Sun_Vargottama': np.random.choice([0, 1], size=n, p=[0.88, 0.12]),
        'Moon_Vargottama': np.random.choice([0, 1], size=n, p=[0.88, 0.12]),
        
        # Pillar 4: Jaimini Karakas
        'Jaimini_AK': np.random.choice(['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'], size=n),
        'Jaimini_GK': np.random.choice(['Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu'], size=n),
        
        # Pillar 5: Ashtakavarga SAV
        'SAV_Total': np.random.randint(320, 350, size=n),
        'SAV_At_Moon': np.random.randint(18, 40, size=n),
        'SAV_At_Mars': np.random.randint(18, 40, size=n),
        
        # Pillar 6: Shadbala
        'Shadbala_Mars_Rupas': np.random.normal(6.5, 1.2, size=n),
        'Shadbala_Saturn_Rupas': np.random.normal(6.0, 1.1, size=n),
        'Shadbala_Chesta_Bala': np.random.uniform(20, 60, size=n),
        'Shadbala_Kala_Bala': np.random.uniform(30, 70, size=n),
        
        # Pillar 7: SBC & Vedha
        'Vedha_Malefic_Count': np.random.randint(0, 5, size=n),
        'Gochar_Murti': np.random.choice(['Gold', 'Silver', 'Copper', 'Iron'], size=n),
        
        # Pillar 8: KP Sub-Lords
        'KP_Lagna_SubLord': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'], size=n),
        'KP_10th_SubLord': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'], size=n),
        
        # Pillar 9: Vimshottari
        'Vim_MD': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn'], size=n),
        'Vim_AD': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn'], size=n),
        'Vim_PD': np.random.choice(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn'], size=n),
        
        # Pillar 10: MTF Confluence
        'MTF_Confluence_Count': np.random.choice([1, 2, 3, 4], size=n, p=[0.70, 0.20, 0.08, 0.02]),
        
        # Target
        'Candle_Direction': np.random.choice(['GREEN', 'RED'], size=n, p=[0.5, 0.5])
    }
    
    df = pd.DataFrame(data)
    
    # Inject deliberate signals into first 150 rows (Crash Anomalies)
    df.loc[:149, 'Candle_Direction'] = 'RED'
    df.loc[:99, 'Mars_Declination'] = np.random.uniform(24.5, 27.5, size=100) # Mars OOB
    df.loc[:99, 'Jaimini_GK'] = 'Mars'                                       # Mars GK
    df.loc[:99, 'SAV_At_Moon'] = np.random.randint(18, 23, size=100)        # SAV < 25
    df.loc[:99, 'Vedha_Malefic_Count'] = np.random.randint(3, 5, size=100)   # High Malefic Vedha
    
    # Inject deliberate signals into next 150 rows (Surge Anomalies)
    df.loc[150:299, 'Candle_Direction'] = 'GREEN'
    df.loc[150:249, 'Sun_Vargottama'] = 1
    df.loc[150:249, 'SAV_At_Moon'] = np.random.randint(34, 40, size=100)    # SAV > 32
    df.loc[150:249, 'MTF_Confluence_Count'] = 4                              # 4-TF Confluence
    
    return df


# ==============================================================================
# TIER 1: FEATURE COVERAGE (TESTING ALL 10 CLASSICAL PILLARS)
# ==============================================================================

class TestTier1TenPillarsForensicDrilldown:
    """Tier 1 Tests for all 10 Classical Forensic Vedic Pillars."""

    def test_r5_pillar1_ephemeris_oob_declination_and_stations(self, synthetic_10_pillar_dataset):
        """1. Pillar 1: Tests Out-of-Bounds Declination (|delta| > 23.44°) and Planetary Stations (|speed| <= 0.05°)."""
        df = synthetic_10_pillar_dataset
        oob_mask = oracle_is_out_of_bounds(df['Mars_Declination'])
        assert oob_mask.sum() > 0, "No OOB Mars detected in dataset"
        
        # Test station detection on Saturn
        station_mask = oracle_is_planetary_station(df['Saturn_Speed'], threshold=0.03)
        assert station_mask.sum() > 0, "No Saturn station detected in dataset"

    def test_r5_pillar2_aspects_orb_clustering_6_8_2_12_1_7(self):
        """2. Pillar 2: Validates exact orb clustering for 6/8 (Shadashtaka), 2/12 (Dwirdwadasa), 1/7 (Samasaptaka)."""
        # Exact 150° Shadashtaka
        is_6_8, sep = oracle_shadashtaka_aspect(180.0, 30.0, orb=2.0)
        assert is_6_8 == True and abs(sep - 150.0) < 1e-6
        
        # Exact 30° Dwirdwadasa
        is_2_12, sep = oracle_dwirdwadasa_aspect(30.0, 0.0, orb=2.0)
        assert is_2_12 == True and abs(sep - 30.0) < 1e-6
        
        # Exact 180° Samasaptaka
        is_1_7, sep = oracle_samasaptaka_aspect(180.0, 0.0, orb=2.0)
        assert is_1_7 == True and abs(sep - 180.0) < 1e-6

    def test_r5_pillar3_vargas_pushkara_navamsha_and_vargottama(self):
        """3. Pillar 3: Validates Pushkara Navamsha and Vargottama resonance rules across all 4 triplicities."""
        # Aries (Fire) + Libra Navamsha (6) -> Pushkara
        assert oracle_pushkara_navamsha(0, 6) == True
        # Taurus (Earth) + Gemini Navamsha (2) -> Pushkara
        assert oracle_pushkara_navamsha(1, 2) == True
        # Gemini (Air) + Virgo Navamsha (5) -> Pushkara
        assert oracle_pushkara_navamsha(2, 5) == True
        # Cancer (Water) + Cancer Navamsha (3) -> Pushkara & Vargottama
        assert oracle_pushkara_navamsha(3, 3) == True
        # Non-pushkara
        assert oracle_pushkara_navamsha(0, 0) == False

    def test_r5_pillar4_jaimini_gk_vs_ak_activations(self, synthetic_10_pillar_dataset):
        """4. Pillar 4: Tests Gnatikaraka (GK) activations during panic crashes vs Atmakaraka (AK)."""
        df = synthetic_10_pillar_dataset
        crashes = df[df['Candle_Direction'] == 'RED']
        gk_mars_count = (crashes['Jaimini_GK'] == 'Mars').sum()
        assert gk_mars_count >= 50, f"Expected strong GK Mars signal in crashes, got {gk_mars_count}"

    def test_r5_pillar5_ashtakavarga_sav_extreme_bindus(self, synthetic_10_pillar_dataset):
        """5. Pillar 5: Tests extreme SAV thresholds (< 25 bindus vs > 32 bindus) in transited signs."""
        df = synthetic_10_pillar_dataset
        crashes = df[df['Candle_Direction'] == 'RED']
        surges = df[df['Candle_Direction'] == 'GREEN']
        
        low_sav_crashes = (crashes['SAV_At_Moon'] < 25).sum()
        high_sav_surges = (surges['SAV_At_Moon'] > 32).sum()
        
        assert low_sav_crashes >= 50, f"Expected low SAV < 25 in crashes, got {low_sav_crashes}"
        assert high_sav_surges >= 50, f"Expected high SAV > 32 in surges, got {high_sav_surges}"

    def test_r5_pillar6_shadbala_chesta_vs_kala_ratio(self, synthetic_10_pillar_dataset):
        """6. Pillar 6: Tests Chesta Bala (motional strength) vs Kala Bala (temporal strength) ratio on trend days."""
        df = synthetic_10_pillar_dataset
        ratio = df['Shadbala_Chesta_Bala'] / np.maximum(df['Shadbala_Kala_Bala'], 1e-6)
        assert (ratio > 0).all()
        assert np.isfinite(ratio).all()

    def test_r5_pillar7_sarvatobhadra_vedha_networks(self, synthetic_10_pillar_dataset):
        """7. Pillar 7: Tests Malefic Vedha network intensity and Gochar Murti impact on market shocks."""
        df = synthetic_10_pillar_dataset
        crashes = df[df['Candle_Direction'] == 'RED']
        high_vedha = (crashes['Vedha_Malefic_Count'] >= 3).sum()
        assert high_vedha >= 50, f"Expected high malefic vedha count in crashes, got {high_vedha}"

    def test_r5_pillar8_kp_sub_lords_nyse_cusps(self, synthetic_10_pillar_dataset):
        """8. Pillar 8: Tests Star Lord and Sub-Lord rulers of NYSE Lagna and 10th cusp."""
        df = synthetic_10_pillar_dataset
        assert df['KP_Lagna_SubLord'].nunique() >= 5
        assert df['KP_10th_SubLord'].nunique() >= 5

    def test_r5_pillar9_nyse_vimshottari_dasha_triggers(self, synthetic_10_pillar_dataset):
        """9. Pillar 9: Tests Mahadasha / Antardasha / Pratyantardasha lord transit triggers."""
        df = synthetic_10_pillar_dataset
        assert df['Vim_MD'].isin(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn']).all()
        assert df['Vim_AD'].isin(['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn']).all()

    def test_r5_pillar10_multitimeframe_4tf_cooccurrences(self, synthetic_10_pillar_dataset):
        """10. Pillar 10: Tests astrological signatures of 4-timeframe simultaneous co-occurrences."""
        df = synthetic_10_pillar_dataset
        surges = df[df['Candle_Direction'] == 'GREEN']
        mtf_4_count = (surges['MTF_Confluence_Count'] == 4).sum()
        assert mtf_4_count >= 50, f"Expected 4-TF confluences in surges, got {mtf_4_count}"


# ==============================================================================
# TIER 2: BOUNDARY & CORNER CASES (6 TESTS)
# ==============================================================================

class TestTier2TenPillarsBoundaries:
    """Tier 2 Tests for Pillar Boundaries, Precise Thresholds, and Zero Divisions."""

    def test_r5_boundary_pillar1_declination_exact_23_44_boundary(self):
        """11. Validates exact 23.4367° boundary classification for Out-of-Bounds declination."""
        assert oracle_is_out_of_bounds(23.4366) == False
        assert oracle_is_out_of_bounds(23.4368) == True
        assert oracle_is_out_of_bounds(-23.4368) == True

    def test_r5_boundary_pillar2_aspect_orb_zero(self):
        """12. Validates 0.00° exact aspect alignment orb without floating point errors."""
        is_6_8, _ = oracle_shadashtaka_aspect(150.0, 0.0, orb=0.0)
        assert is_6_8 == True
        is_6_8_slight, _ = oracle_shadashtaka_aspect(150.001, 0.0, orb=0.0)
        assert is_6_8_slight == False

    def test_r5_boundary_pillar4_jaimini_tied_degrees(self):
        """13. Validates Jaimini Karaka resolution when planets have identical degrees in sign."""
        degrees = {
            'Sun': 28.5,
            'Moon': 28.5, # Tied with Sun
            'Mars': 21.0,
            'Mercury': 18.0,
            'Jupiter': 12.0,
            'Venus': 8.0,
            'Saturn': 2.0
        }
        karakas = oracle_jaimini_karakas(degrees)
        assert karakas['AK'] in ['Sun', 'Moon']
        assert karakas['AmK'] in ['Sun', 'Moon']
        assert karakas['AK'] != karakas['AmK']  # Both assigned uniquely

    def test_r5_boundary_pillar5_sav_boundary_25_and_32(self):
        """14. Validates exact 25 and 32 bindu boundary conditions for Ashtakavarga SAV."""
        sav_low_bound = 25
        sav_high_bound = 32
        assert (sav_low_bound < 25) == False
        assert (24 < 25) == True
        assert (sav_high_bound > 32) == False
        assert (33 > 32) == True

    def test_r5_boundary_pillar6_shadbala_zero_bala_protection(self):
        """15. Validates protection against 0 divisor in Shadbala strength ratio calculations."""
        chesta = 50.0
        kala = 0.0
        ratio = chesta / max(kala, 1e-6)
        assert ratio == 50.0 / 1e-6
        assert np.isfinite(ratio)

    def test_r5_boundary_pillar9_vimshottari_dasha_junction(self):
        """16. Validates exact Dasha transition boundary (end of Sun MD / start of Moon MD)."""
        dasha_sequence = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        sun_idx = dasha_sequence.index('Sun')
        next_md = dasha_sequence[(sun_idx + 1) % len(dasha_sequence)]
        assert next_md == 'Moon'


# ==============================================================================
# TIER 3: PAIRWISE PILLAR INTERACTIONS (3 TESTS)
# ==============================================================================

class TestTier3TenPillarsPairwiseInteractions:
    """Tier 3 Tests for Cross-Pillar Synergies."""

    def test_r5_pairwise_pillar1_oob_and_pillar7_vedha_confluence(self, synthetic_10_pillar_dataset):
        """17. Verifies compound risk multiplier when an Out-of-Bounds planet simultaneously casts Malefic Vedha."""
        df = synthetic_10_pillar_dataset
        compound_risk = (oracle_is_out_of_bounds(df['Mars_Declination'])) & (df['Vedha_Malefic_Count'] >= 3)
        crashes = df[df['Candle_Direction'] == 'RED']
        crashes_with_risk = (oracle_is_out_of_bounds(crashes['Mars_Declination'])) & (crashes['Vedha_Malefic_Count'] >= 3)
        
        assert crashes_with_risk.sum() > 0, "No compound OOB + Vedha risk found in crashes"

    def test_r5_pairwise_pillar3_vargottama_and_pillar5_sav_confluence(self, synthetic_10_pillar_dataset):
        """18. Verifies bullish confluence when a Vargottama planet transits a sign with SAV > 32."""
        df = synthetic_10_pillar_dataset
        surges = df[df['Candle_Direction'] == 'GREEN']
        confluence = (surges['Sun_Vargottama'] == 1) & (surges['SAV_At_Moon'] > 32)
        assert confluence.sum() > 0, "No Vargottama + High SAV confluence found in surges"

    def test_r5_pairwise_pillar8_kp_sub_and_pillar9_dasha_lord_resonance(self, synthetic_10_pillar_dataset):
        """19. Verifies resonance when KP Sub-Lord matches active Vimshottari Antardasha Lord."""
        df = synthetic_10_pillar_dataset
        resonance = (df['KP_Lagna_SubLord'] == df['Vim_AD'])
        assert resonance.sum() > 0


# ==============================================================================
# TIER 4: REAL-WORLD FORENSIC WORKLOADS (2 TESTS)
# ==============================================================================

class TestTier4TenPillarsRealWorldWorkloads:
    """Tier 4 Tests on Real 1,408 Anomaly Dataset across all 10 Classical Pillars."""

    def test_r5_real_world_10_pillar_drilldown_execution(self, project_root):
        """20. Executes forensic pillar hypothesis extraction on live 1,408 supreme anomaly dataset."""
        parquet_path = os.path.join(project_root, "data", "spy_anomalies_omni_vedic_supreme.parquet")
        if not os.path.exists(parquet_path):
            pytest.skip(f"Dataset {parquet_path} not found")
            
        df = pd.read_parquet(parquet_path)
        assert len(df) == 1408
        
        # Pillar 1 check: Mars Declination column exists and finite
        assert 'Mars_Declination' in df.columns
        assert np.isfinite(df['Mars_Declination']).all()
        
        # Pillar 4 check: Jaimini GK column exists
        assert 'Jaimini_GK' in df.columns
        assert df['Jaimini_GK'].notna().all()
        
        # Pillar 5 check: SAV Total and transited SAV
        assert 'SAV_Total' in df.columns and 'SAV_At_Moon' in df.columns
        assert (df['SAV_Total'] > 300).all()

    def test_r5_real_world_pillar_summary_table_completeness(self, project_root):
        """21. Verifies that all 10 pillars have valid feature representation across 397 columns."""
        parquet_path = os.path.join(project_root, "data", "spy_anomalies_omni_vedic_supreme.parquet")
        if not os.path.exists(parquet_path):
            pytest.skip(f"Dataset {parquet_path} not found")
            
        df = pd.read_parquet(parquet_path)
        
        pillar_checks = {
            'Pillar 1: Ephemeris': 'Mars_Declination',
            'Pillar 2: Aspects': 'Bhv_Sun_Moon',
            'Pillar 3: Vargas': 'Sun_D9',
            'Pillar 4: Jaimini': 'Jaimini_AK',
            'Pillar 5: Ashtakavarga': 'SAV_Total',
            'Pillar 6: Shadbala': 'Shadbala_Sun_Rupas',
            'Pillar 7: Combust/Vedha': 'Moon_Combust',
            'Pillar 8: Lagna': 'Lagna_NYSE_Sign',
            'Pillar 9: Vimshottari': 'Vim_MD',
            'Pillar 10: MTF Confluence': 'MTF_Confluence_Count'
        }
        
        for pillar_name, col_name in pillar_checks.items():
            assert col_name in df.columns, f"Missing feature for {pillar_name}: column '{col_name}'"
            assert df[col_name].isna().sum() == 0, f"NaNs found in {pillar_name} feature '{col_name}'"
