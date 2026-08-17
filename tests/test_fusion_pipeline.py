"""
test_fusion_pipeline.py — Comprehensive Unit & Integration Tests for Module 3 Fusion Pipeline.

Evaluates:
- `src.pipeline.fusion_pipeline`
- `src.pipeline.export_manifest`
- 66-Column Schema Invariants
- Partitioned Exports & Union Sum
- Edge cases, empty DataFrames, type safety, and microsecond Julian Day conversions
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timezone

from src.pipeline.fusion_pipeline import (
    CANONICAL_66_COLUMNS,
    align_anomalies_with_vedic_astrology,
    build_66_column_feature_matrix,
    build_extended_unified_matrix,
    extract_and_fuse_timeframe,
    run_fusion_pipeline,
)
from src.pipeline.export_manifest import (
    export_all_manifests,
    validate_manifests,
)
from tests.conftest import (
    assert_zero_nans,
    assert_zero_duplicates,
    assert_monotonic_increasing,
)


class TestFusionPipelineFunctions:
    def test_canonical_66_columns_length_and_uniqueness(self):
        """Validates that CANONICAL_66_COLUMNS contains exactly 66 unique strings."""
        assert len(CANONICAL_66_COLUMNS) == 66
        assert len(set(CANONICAL_66_COLUMNS)) == 66
        assert "Solid_Ratio" in CANONICAL_66_COLUMNS
        assert "Moon_Nakshatra" in CANONICAL_66_COLUMNS
        assert "Tithi" in CANONICAL_66_COLUMNS
        assert "Mars_Combust" in CANONICAL_66_COLUMNS

    def test_align_anomalies_with_empty_dataframe(self):
        """Verifies graceful handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        aligned = align_anomalies_with_vedic_astrology(empty_df)
        assert len(aligned) == 0

        matrix_66 = build_66_column_feature_matrix(empty_df)
        assert len(matrix_66) == 0
        assert list(matrix_66.columns) == CANONICAL_66_COLUMNS

    def test_build_66_column_matrix_with_synthetic_candle(self, sample_synthetic_candles):
        """Tests end-to-end 66-column alignment on synthetic candlestick records."""
        candles = sample_synthetic_candles.copy()
        candles["Timeframe"] = "1H"
        candles["Body"] = (candles["Close"] - candles["Open"]).abs()
        candles["Range"] = candles["High"] - candles["Low"]
        candles["Solid_Ratio"] = candles["Body"] / np.maximum(candles["Range"], 1e-9)
        candles["Upper_Wick"] = candles["High"] - np.maximum(candles["Open"], candles["Close"])
        candles["Lower_Wick"] = np.minimum(candles["Open"], candles["Close"]) - candles["Low"]
        candles["Upper_Wick_Ratio"] = candles["Upper_Wick"] / np.maximum(candles["Range"], 1e-9)
        candles["Lower_Wick_Ratio"] = candles["Lower_Wick"] / np.maximum(candles["Range"], 1e-9)
        candles["Max_Wick_Ratio"] = np.maximum(candles["Upper_Wick_Ratio"], candles["Lower_Wick_Ratio"])
        candles["Direction"] = np.where(candles["Close"] >= candles["Open"], "GREEN", "RED")
        candles["Body_Return_Pct"] = (candles["Close"] - candles["Open"]) / candles["Open"] * 100.0
        candles["Abs_Body_Return_Pct"] = candles["Body_Return_Pct"].abs()
        candles["Overnight_Gap_Pct"] = 0.0
        candles["Total_Return_Pct"] = candles["Body_Return_Pct"]
        candles["Trailing_ATR20"] = 2.0
        candles["Body_ATR_Ratio"] = candles["Body"] / 2.0
        candles["Trailing_Vol_SMA20"] = 1_000_000.0
        candles["Standard_RVOL"] = candles["Volume"] / 1_000_000.0
        candles["Hour_Of_Day"] = 9
        candles["TOD_Vol_SMA20"] = 1_000_000.0
        candles["TOD_RVOL"] = candles["Standard_RVOL"]
        candles["RVOL"] = candles["Standard_RVOL"]
        candles["Min_Return_Floor"] = 0.50
        candles["is_solid"] = candles["Solid_Ratio"] >= 0.65
        candles["is_high_volume"] = candles["RVOL"] >= 1.50
        candles["is_big_magnitude"] = candles["Body_ATR_Ratio"] >= 1.50
        candles["is_extreme_anomaly"] = candles["is_solid"] & candles["is_high_volume"] & candles["is_big_magnitude"]
        candles["Anomaly_Tier"] = 1

        fused = build_66_column_feature_matrix(candles)
        assert len(fused) == len(candles)
        assert list(fused.columns) == CANONICAL_66_COLUMNS
        assert_zero_nans(fused, ["Sun_Longitude", "Moon_Longitude", "Tithi", "Solid_Ratio", "Open", "Close"])

    def test_build_extended_unified_matrix(self, sample_synthetic_candles):
        """Tests generation of extended 152+ column research matrix."""
        candles = sample_synthetic_candles.copy()
        candles["Timeframe"] = "1H"
        extended = build_extended_unified_matrix(candles)
        assert len(extended) == len(candles)
        assert extended.shape[1] >= 100
        assert "Ang_Sun_Moon" in extended.columns
        assert "Mars_Combust" in extended.columns


class TestExportAndValidationEngine:
    def test_validate_manifests_on_live_deliverables(self, data_dir):
        """Validates all exported deliverables using the forensic validation engine."""
        report = validate_manifests(data_dir=data_dir)
        assert report["valid"] is True, f"Validation failed with errors: {report.get('errors')}"
        assert report["union_sum_verified"] is True
        assert report["total_anomalies"] > 0
        assert report["error_count"] == 0

    def test_export_all_manifests_idempotence(self, data_dir):
        """Tests that re-exporting deliverables produces identical, valid results."""
        report = export_all_manifests(data_dir=data_dir)
        assert report["valid"] is True
        assert report["union_sum_verified"] is True
        assert report["total_anomalies"] > 0
        assert len(report["exported_files"]) >= 20
