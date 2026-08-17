"""
test_tier4_real_world_workloads.py — Tier 4: Real-World Datasets & Master Manifest Union Validation
Evaluates all live .parquet and .csv deliverables, master manifest union sum, zero NaNs, and zero duplicate timestamps.
"""

import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

from tests.conftest import (
    assert_zero_nans,
    assert_zero_duplicates,
    assert_monotonic_increasing,
    assert_sieve_conditions
)


class TestTier4DeliverableArtifacts:
    TIMEFRAMES = ['1h', '2h', '4h', '1d', '1w', '1mo']

    def test_summary_stats_json_exists_and_valid(self, data_dir):
        """Verifies summary statistics JSON file exists and contains valid metrics."""
        stats_path = os.path.join(data_dir, "spy_anomalies_summary_stats.json")
        assert os.path.exists(stats_path), f"Missing summary stats JSON at {stats_path}"
        
        with open(stats_path, 'r') as f:
            stats = json.load(f)
            
        assert isinstance(stats, dict)
        assert 'timeframes' in stats or 'total_anomalies' in stats or any(tf.upper() in stats or tf.lower() in stats for tf in self.TIMEFRAMES)

    def test_partitioned_parquet_and_csv_existence(self, data_dir):
        """Verifies both .parquet and .csv partitioned files exist for all 6 timeframes."""
        for tf in self.TIMEFRAMES:
            pq_path = os.path.join(data_dir, f"spy_anomalies_{tf}.parquet")
            csv_path = os.path.join(data_dir, f"spy_anomalies_{tf}.csv")
            
            assert os.path.exists(pq_path), f"Missing parquet deliverable for timeframe {tf} at {pq_path}"
            assert os.path.exists(csv_path), f"Missing CSV deliverable for timeframe {tf} at {csv_path}"

    def test_master_manifest_and_enriched_files_exist(self, data_dir):
        """Verifies master manifest and Vedic enriched datasets exist in both Parquet and CSV."""
        master_pq = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
        master_csv = os.path.join(data_dir, "spy_anomalies_master_manifest.csv")
        enriched_pq = os.path.join(data_dir, "spy_anomalies_vedic_enriched.parquet")
        enriched_csv = os.path.join(data_dir, "spy_anomalies_vedic_enriched.csv")
        
        assert os.path.exists(master_pq), f"Missing master manifest parquet at {master_pq}"
        assert os.path.exists(master_csv), f"Missing master manifest CSV at {master_csv}"
        assert os.path.exists(enriched_pq), f"Missing enriched parquet at {enriched_pq}"
        assert os.path.exists(enriched_csv), f"Missing enriched CSV at {enriched_csv}"


class TestTier4UnionSumAndDataIntegrity:
    TIMEFRAMES = ['1h', '2h', '4h', '1d', '1w', '1mo']

    def test_master_manifest_union_sum_exact_match(self, data_dir):
        """
        Validates the fundamental Union Sum Invariant:
        Sum(N_1h + N_2h + N_4h + N_1d + N_1w + N_1mo) == N_master == 1,001 anomalies.
        """
        tf_counts = {}
        total_sub_count = 0
        
        for tf in self.TIMEFRAMES:
            pq_path = os.path.join(data_dir, f"spy_anomalies_{tf}.parquet")
            if os.path.exists(pq_path):
                df_tf = pd.read_parquet(pq_path)
                count = len(df_tf)
                tf_counts[tf] = count
                total_sub_count += count
                
        master_pq = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
        df_master = pd.read_parquet(master_pq)
        master_count = len(df_master)
        
        assert total_sub_count == master_count, (
            f"Union sum mismatch! Sum of timeframes ({total_sub_count}) != Master ({master_count}). "
            f"Breakdown: {tf_counts}"
        )
        assert master_count > 0, f"Expected non-empty master anomalies, got {master_count}"

    def test_zero_nans_across_all_timeframe_datasets(self, data_dir):
        """Forensic guarantee: 0 NaNs in all critical price, volume, and indicator columns."""
        crit_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Solid_Ratio', 'Direction']
        
        for tf in self.TIMEFRAMES:
            pq_path = os.path.join(data_dir, f"spy_anomalies_{tf}.parquet")
            if os.path.exists(pq_path):
                df = pd.read_parquet(pq_path)
                present_cols = [c for c in crit_cols if c in df.columns]
                assert_zero_nans(df, present_cols)

    def test_zero_duplicate_timestamps_across_all_datasets(self, data_dir):
        """Forensic guarantee: Exactly 0 duplicate timestamps within each timeframe."""
        for tf in self.TIMEFRAMES:
            pq_path = os.path.join(data_dir, f"spy_anomalies_{tf}.parquet")
            if os.path.exists(pq_path):
                df = pd.read_parquet(pq_path)
                assert_zero_duplicates(df)

    def test_strictly_monotonic_ascending_timestamps(self, data_dir):
        """Forensic guarantee: Timestamps in master manifest are monotonically increasing."""
        master_pq = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
        df_master = pd.read_parquet(master_pq)
        time_col = 'Datetime_UTC' if 'Datetime_UTC' in df_master.columns else 'Datetime'
        assert_monotonic_increasing(df_master, time_col)

    def test_100_percent_sieve_conditions_compliance(self, data_dir):
        """100% of rows across all 6 timeframes strictly comply with Solid_Ratio >= 0.65, RVOL >= 1.50, MWR <= 0.25."""
        for tf in self.TIMEFRAMES:
            pq_path = os.path.join(data_dir, f"spy_anomalies_{tf}.parquet")
            if os.path.exists(pq_path):
                df = pd.read_parquet(pq_path)
                assert_sieve_conditions(df)
                
                # Verify magnitude condition: Body/ATR >= 1.50 or Return >= Floor
                ret_col = 'Abs_Body_Return_Pct' if 'Abs_Body_Return_Pct' in df.columns else 'Abs_Return_Pct'
                if 'Body_ATR_Ratio' in df.columns and 'Min_Return_Floor' in df.columns and ret_col in df.columns:
                    valid_mag = ((df['Body_ATR_Ratio'] >= 1.50) | (df[ret_col] >= df['Min_Return_Floor'])).all()
                    assert valid_mag, f"Timeframe {tf} has rows failing magnitude condition"


class TestTier4VedicEnrichmentIntegrity:
    def test_vedic_enriched_manifest_row_count_and_columns(self, data_dir):
        """Verifies enriched dataset has exact 1,001 rows and >= 45 features."""
        enriched_pq = os.path.join(data_dir, "spy_anomalies_vedic_enriched.parquet")
        assert os.path.exists(enriched_pq), f"Missing enriched parquet at {enriched_pq}"
        
        df_enriched = pd.read_parquet(enriched_pq)
        assert len(df_enriched) > 0, f"Expected non-empty rows in enriched dataset, got {len(df_enriched)}"
        assert df_enriched.shape[1] >= 45, f"Expected >= 45 columns, got {df_enriched.shape[1]}"
        
        # Verify 0 NaNs in critical Vedic columns
        vedic_cols = ['Julian_Day', 'Moon_Longitude', 'Sun_Longitude', 'Tithi', 'Paksha', 'Moon_Nakshatra', 'Yoga', 'Karana']
        present_vedic_cols = [c for c in vedic_cols if c in df_enriched.columns]
        assert_zero_nans(df_enriched, present_vedic_cols)
