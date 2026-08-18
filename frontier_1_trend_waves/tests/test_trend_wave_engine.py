"""
UNIT & INTEGRATION TESTS FOR TREND WAVE ENGINE & PATTERN MINER
==============================================================
Verifies mathematical integrity, non-lookahead wave segmentation,
dual-anchor Omni-Vedic enrichment, and FDR statistical significance.
"""

import pytest
import os
import numpy as np
import pandas as pd

from src.analysis.trend_wave_engine import (
    calculate_kaufman_efficiency_ratio,
    extract_trend_waves_from_series,
    extract_all_timeframe_trend_waves,
    MIN_RETURN_FLOORS,
    ATR_MULTIPLIERS
)
from src.analysis.enrich_trend_waves import enrich_trend_waves_with_omni_vedic
from src.analysis.mine_trend_wave_rules import (
    load_and_prepare_trend_wave_dataset,
    build_candidate_pure_vedic_features,
    mine_trend_wave_rules_vectorized
)


class TestTrendWaveSegmentation:
    """Test Suite for Mathematical Wave Segmentation."""

    def test_kaufman_efficiency_ratio_monotonic(self):
        """Test KER equals 1.0 for strictly monotonic sequences."""
        mono_up = np.array([100.0, 102.0, 105.0, 110.0, 115.0])
        assert calculate_kaufman_efficiency_ratio(mono_up) == 1.0

        mono_down = np.array([115.0, 110.0, 105.0, 102.0, 100.0])
        assert calculate_kaufman_efficiency_ratio(mono_down) == 1.0

    def test_kaufman_efficiency_ratio_oscillating(self):
        """Test KER drops significantly for noisy oscillating price action."""
        oscillating = np.array([100.0, 105.0, 101.0, 106.0, 102.0, 107.0, 103.0])
        ker = calculate_kaufman_efficiency_ratio(oscillating)
        # Net change = 3, Total path = 5+4+5+4+5+4 = 27 -> KER = 3/27 = 0.111
        assert ker < 0.25

    def test_kaufman_efficiency_ratio_zero_division(self):
        """Test KER handles flat zero-change series gracefully."""
        flat = np.array([100.0, 100.0, 100.0, 100.0])
        assert calculate_kaufman_efficiency_ratio(flat) == 0.0

    def test_wave_segmentation_synthetic_data(self):
        """Test wave extraction on synthetic deterministic zigzag series."""
        # Create 200 bars with clear swing peaks and troughs
        t = np.linspace(0, 4 * np.pi, 200)
        closes = 100.0 + 15.0 * np.sin(t)
        highs = closes + 1.0
        lows = closes - 1.0
        opens = closes - 0.5
        vols = np.full(200, 1000.0)
        dt_utcs = pd.date_range("2020-01-01", periods=200, freq="1D", tz="UTC")

        df_syn = pd.DataFrame({
            "Datetime_UTC": dt_utcs,
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": vols,
            "Trailing_ATR20": np.full(200, 2.0),
            "Trailing_Vol_SMA20": np.full(200, 1000.0),
        })

        waves = extract_trend_waves_from_series(df_syn, "1D", atr_mult=2.0, min_return_floor=3.0, min_ker=0.50)
        assert not waves.empty
        assert len(waves) >= 3
        for _, w in waves.iterrows():
            assert w["Start_Idx"] < w["End_Idx"]
            assert w["Wave_Duration_Bars"] >= 3
            assert 0.0 <= w["Kaufman_ER"] <= 1.0
            assert w["P_Start"] > 0
            assert w["P_End"] > 0


class TestTrendWaveEnrichmentAndInvariants:
    """Test Suite for Dual-Anchor Omni-Vedic Enriched Matrix."""

    @pytest.fixture(scope="class")
    def enriched_dataset(self):
        path = "data/spy_trend_waves_omni_vedic_supreme.parquet"
        if not os.path.exists(path):
            enrich_trend_waves_with_omni_vedic()
        return pd.read_parquet(path)

    def test_zero_nans_across_all_columns(self, enriched_dataset):
        """Verifies 100% complete dataset with zero missing values."""
        assert enriched_dataset.isnull().sum().sum() == 0

    def test_sav_337_invariant_inception_and_climax(self, enriched_dataset):
        """Verifies SAV total sum equals 337 across all rows for both Inception and Climax."""
        assert (enriched_dataset["Inception_SAV_Total"] == 337).all()
        assert (enriched_dataset["Climax_SAV_Total"] == 337).all()

    def test_jaimini_7_karakas_1_to_1_uniqueness(self, enriched_dataset):
        """Verifies Jaimini 7 Karakas maintain strict 1-to-1 uniqueness in 100% of rows."""
        karaka_cols = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        for _, row in enriched_dataset.iterrows():
            incept_k = [row[f"Inception_Jaimini_{k}"] for k in karaka_cols]
            assert len(set(incept_k)) == 7
            climax_k = [row[f"Climax_Jaimini_{k}"] for k in karaka_cols]
            assert len(set(climax_k)) == 7

    def test_intra_wave_astrological_metrics(self, enriched_dataset):
        """Verifies intra-wave lunar degrees, ingress count, and station count."""
        assert (enriched_dataset["Wave_Moon_Degrees_Traversed"] >= 0.0).all()
        assert (enriched_dataset["Wave_Planetary_Ingress_Count"] >= 0).all()
        assert (enriched_dataset["Wave_Planetary_Station_Count"] >= 0).all()


class TestTrendWavePatternMiner:
    """Test Suite for Vectorized Pattern Miner & FDR Sieve."""

    def test_mine_bullish_and_bearish_fdr_rules(self):
        """Verifies pattern miner produces valid FDR-significant rules."""
        df = load_and_prepare_trend_wave_dataset()
        bull_rules = mine_trend_wave_rules_vectorized(
            df, target_direction="Bullish_Thrust", min_support=8, min_confidence=0.68, min_lift=1.60
        )
        assert len(bull_rules) > 0
        for r in bull_rules:
            assert r["Confidence_Pct"] >= 68.0
            assert r["FDR_PValue"] < 0.05
            assert r["Unique_Years"] >= 2
            assert r["Matches_N"] >= 8

        bear_rules = mine_trend_wave_rules_vectorized(
            df, target_direction="Bearish_Liquidation", min_support=8, min_confidence=0.68, min_lift=1.10
        )
        assert len(bear_rules) > 0
        for r in bear_rules:
            assert r["Confidence_Pct"] >= 68.0
            assert r["FDR_PValue"] < 0.05
            assert r["Unique_Years"] >= 2
            assert r["Matches_N"] >= 8
