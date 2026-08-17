"""
Export Manifest & Deliverable Artifacts Exporter Module.

Exports:
- Partitioned datasets (.parquet and .csv) for each timeframe to `data/anomalies/` and `data/`
- Unified Master Anomaly Manifest (.parquet and .csv)
- Vedic-Enriched 66-Column Feature Matrix (.parquet and .csv)
- Comprehensive Summary Statistics (.json)

Validates:
- Exact Union Sum Invariant: N_1h + N_2h + N_4h + N_1d + N_1w + N_1mo == N_master == 1,001
- Zero NaNs across all critical price, volume, and astronomical indicator columns
- Zero duplicate timestamps within each timeframe
- Monotonic ascending datetime ordering
- 100% Sieve Condition compliance (Solid Ratio >= 0.65, RVOL >= 1.50x, MWR <= 0.25)
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.pipeline.fusion_pipeline import (
    CANONICAL_66_COLUMNS,
    run_fusion_pipeline,
    build_66_column_feature_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def export_all_manifests(
    data_dir: Optional[str] = None,
    anomalies_dir: Optional[str] = None,
    node_mode: str = "true",
) -> Dict[str, Any]:
    """
    Executes the fusion pipeline and persists all deliverable files to disk in both Parquet and CSV formats.

    Parameters
    ----------
    data_dir : Optional[str]
        Root data directory path (default: <project_root>/data).
    anomalies_dir : Optional[str]
        Anomalies deliverable directory path (default: <project_root>/data/anomalies).
    node_mode : str
        'true' or 'mean' lunar node mode for Swiss Ephemeris calculations.

    Returns
    -------
    Dict[str, Any]
        Summary validation report of exported files and statistics.
    """
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), "data")
    if anomalies_dir is None:
        anomalies_dir = os.path.join(data_dir, "anomalies")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(anomalies_dir, exist_ok=True)

    logger.info(f"Running Fusion Pipeline from data_dir: {data_dir}")
    timeframe_anomalies, master_manifest, vedic_enriched, summary_stats = run_fusion_pipeline(
        data_dir=data_dir,
        node_mode=node_mode,
    )

    exported_files: List[str] = []

    # 1. Export Partitioned Timeframe Files
    for tf, df_tf in timeframe_anomalies.items():
        tf_lower = tf.lower()

        # In data/anomalies/
        pq_anom = os.path.join(anomalies_dir, f"spy_anomalies_{tf_lower}.parquet")
        csv_anom = os.path.join(anomalies_dir, f"spy_anomalies_{tf_lower}.csv")
        df_tf.to_parquet(pq_anom, index=False)
        df_tf.to_csv(csv_anom, index=False)
        exported_files.extend([pq_anom, csv_anom])

        # In data/ (for legacy compatibility)
        pq_root = os.path.join(data_dir, f"spy_anomalies_{tf_lower}.parquet")
        csv_root = os.path.join(data_dir, f"spy_anomalies_{tf_lower}.csv")
        df_tf.to_parquet(pq_root, index=False)
        df_tf.to_csv(csv_root, index=False)
        exported_files.extend([pq_root, csv_root])

        logger.info(f"Exported {tf} anomalies ({len(df_tf)} rows) -> {pq_anom} & {csv_anom}")

    # 2. Export Master Anomaly Manifest
    master_pq_1 = os.path.join(anomalies_dir, "master_anomaly_manifest.parquet")
    master_csv_1 = os.path.join(anomalies_dir, "master_anomaly_manifest.csv")
    master_pq_2 = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
    master_csv_2 = os.path.join(data_dir, "spy_anomalies_master_manifest.csv")

    master_manifest.to_parquet(master_pq_1, index=False)
    master_manifest.to_csv(master_csv_1, index=False)
    master_manifest.to_parquet(master_pq_2, index=False)
    master_manifest.to_csv(master_csv_2, index=False)
    exported_files.extend([master_pq_1, master_csv_1, master_pq_2, master_csv_2])

    logger.info(f"Exported Master Manifest ({len(master_manifest)} rows) -> {master_pq_1}")

    # 3. Export Vedic Enriched 66-Column Manifest
    enriched_pq = os.path.join(data_dir, "spy_anomalies_vedic_enriched.parquet")
    enriched_csv = os.path.join(data_dir, "spy_anomalies_vedic_enriched.csv")

    vedic_enriched.to_parquet(enriched_pq, index=False)
    vedic_enriched.to_csv(enriched_csv, index=False)
    exported_files.extend([enriched_pq, enriched_csv])

    logger.info(f"Exported Vedic Enriched 66-Column Matrix ({len(vedic_enriched)} rows, {vedic_enriched.shape[1]} cols) -> {enriched_pq}")

    # 4. Export Summary Stats JSON
    stats_json_path = os.path.join(data_dir, "spy_anomalies_summary_stats.json")
    with open(stats_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=2)
    exported_files.append(stats_json_path)

    logger.info(f"Exported Summary Statistics JSON -> {stats_json_path}")

    # 5. Run Forensic Validation on exported deliverables
    validation_report = validate_manifests(data_dir=data_dir, anomalies_dir=anomalies_dir)
    validation_report["exported_files"] = exported_files
    validation_report["summary_stats"] = summary_stats

    return validation_report


def validate_manifests(
    data_dir: Optional[str] = None,
    anomalies_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Performs comprehensive forensic validation on all deliverable files:
    - Master Manifest Union Invariant ($N = 1,001$)
    - Zero NaNs across all critical columns
    - Zero duplicate timestamps within each timeframe
    - Monotonic ascending timestamp order
    - 100% Sieve Condition compliance

    Returns
    -------
    Dict[str, Any]
        Dictionary of validation results and boolean pass/fail status.
    """
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), "data")
    if anomalies_dir is None:
        anomalies_dir = os.path.join(data_dir, "anomalies")

    timeframes = ["1h", "2h", "4h", "1d", "1w", "1mo"]
    tf_counts: Dict[str, int] = {}
    total_sub_count = 0
    errors: List[str] = []

    # 1. Check partitioned timeframe files
    for tf in timeframes:
        pq_path = os.path.join(anomalies_dir, f"spy_anomalies_{tf}.parquet")
        csv_path = os.path.join(anomalies_dir, f"spy_anomalies_{tf}.csv")

        if not os.path.exists(pq_path):
            errors.append(f"Missing parquet deliverable: {pq_path}")
            continue
        if not os.path.exists(csv_path):
            errors.append(f"Missing CSV deliverable: {csv_path}")
            continue

        df = pd.read_parquet(pq_path)
        count = len(df)
        tf_counts[tf] = count
        total_sub_count += count

        # Zero NaNs in critical price/volume/geometry columns
        crit_cols = ["Open", "High", "Low", "Close", "Volume", "Solid_Ratio", "Direction"]
        present_cols = [c for c in crit_cols if c in df.columns]
        for c in present_cols:
            n_nan = df[c].isna().sum()
            if n_nan > 0:
                errors.append(f"Timeframe {tf} column '{c}' has {n_nan} NaNs")

        # Zero duplicate timestamps
        time_col = "Datetime_UTC" if "Datetime_UTC" in df.columns else "Datetime"
        dupes = df[time_col].duplicated().sum()
        if dupes > 0:
            errors.append(f"Timeframe {tf} has {dupes} duplicate timestamps in '{time_col}'")

        # Sieve compliance
        if "Solid_Ratio" in df.columns:
            invalid_sr = (df["Solid_Ratio"] < 0.65).sum()
            if invalid_sr > 0:
                errors.append(f"Timeframe {tf} has {invalid_sr} rows with Solid_Ratio < 0.65")

        if "Max_Wick_Ratio" in df.columns:
            invalid_mwr = (df["Max_Wick_Ratio"] > 0.25).sum()
            if invalid_mwr > 0:
                errors.append(f"Timeframe {tf} has {invalid_mwr} rows with Max_Wick_Ratio > 0.25")

        rvol_col = "RVOL" if "RVOL" in df.columns else ("TOD_RVOL" if "TOD_RVOL" in df.columns else None)
        if rvol_col and rvol_col in df.columns:
            invalid_rvol = (df[rvol_col] < 1.50).sum()
            if invalid_rvol > 0:
                errors.append(f"Timeframe {tf} has {invalid_rvol} rows with {rvol_col} < 1.50")

    # 2. Check Master Anomaly Manifest
    master_pq = os.path.join(anomalies_dir, "master_anomaly_manifest.parquet")
    if not os.path.exists(master_pq):
        errors.append(f"Missing master manifest: {master_pq}")
        master_count = 0
    else:
        df_master = pd.read_parquet(master_pq)
        master_count = len(df_master)
        time_col = "Datetime_UTC" if "Datetime_UTC" in df_master.columns else "Datetime"

        # Monotonic ordering
        if not df_master[time_col].is_monotonic_increasing:
            errors.append("Master manifest timestamps are not monotonically increasing")

        # Union sum check
        if total_sub_count != master_count:
            errors.append(f"Union sum mismatch: Subtotal ({total_sub_count}) != Master ({master_count})")
        if master_count != 1001:
            errors.append(f"Expected exactly 1,001 total master anomalies, got {master_count}")

    # 3. Check Vedic Enriched 66-Column Matrix
    enriched_pq = os.path.join(data_dir, "spy_anomalies_vedic_enriched.parquet")
    if not os.path.exists(enriched_pq):
        errors.append(f"Missing enriched manifest: {enriched_pq}")
    else:
        df_enriched = pd.read_parquet(enriched_pq)
        if len(df_enriched) != 1001:
            errors.append(f"Enriched manifest row count ({len(df_enriched)}) != 1,001")
        if df_enriched.shape[1] != 66:
            errors.append(f"Enriched manifest column count ({df_enriched.shape[1]}) != 66")

        # Check all 66 columns present
        for col in CANONICAL_66_COLUMNS:
            if col not in df_enriched.columns:
                errors.append(f"Missing required 66-schema column: '{col}'")

        # Zero NaNs in Vedic critical columns
        vedic_cols = [
            "Julian_Day", "Moon_Longitude", "Sun_Longitude", "Tithi", "Paksha",
            "Moon_Nakshatra", "Yoga", "Karana", "Moon_Sign", "Sun_Sign", "Moon_D9_Sign"
        ]
        for c in vedic_cols:
            if c in df_enriched.columns:
                n_nan = df_enriched[c].isna().sum()
                if n_nan > 0:
                    errors.append(f"Enriched column '{c}' has {n_nan} NaNs")

    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "total_anomalies": master_count,
        "timeframe_counts": tf_counts,
        "union_sum_verified": total_sub_count == master_count == 1001,
        "error_count": len(errors),
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="SPY Candlestick Anomaly Deliverable Exporter")
    parser.add_argument("--data-dir", type=str, default=None, help="Root data directory")
    parser.add_argument("--anomalies-dir", type=str, default=None, help="Anomalies export directory")
    parser.add_argument("--node-mode", type=str, default="true", choices=["true", "mean"], help="Lunar node mode")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation checks")

    args = parser.parse_args()

    if args.validate_only:
        report = validate_manifests(data_dir=args.data_dir, anomalies_dir=args.anomalies_dir)
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["valid"] else 1)
    else:
        report = export_all_manifests(
            data_dir=args.data_dir,
            anomalies_dir=args.anomalies_dir,
            node_mode=args.node_mode,
        )
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
