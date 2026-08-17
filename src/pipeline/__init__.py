"""
Feature Alignment Matrix & Master Manifest Pipeline Module.

Exposes:
- `align_anomalies_with_vedic_astrology`: Astronomical synchronization with Swiss Ephemeris
- `build_66_column_feature_matrix`: Exact canonical 66-column schema generator
- `build_extended_unified_matrix`: 152+ column multi-dimensional research matrix builder
- `extract_and_fuse_timeframe`: Single-timeframe extraction and fusion
- `run_fusion_pipeline`: Complete multi-timeframe pipeline executor
- `export_all_manifests`: Deliverables exporter (.parquet, .csv, .json)
- `validate_manifests`: Forensic validator for union sum and integrity invariants
- `CANONICAL_66_COLUMNS`: Authoritative 66-column schema list
"""

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

__all__ = [
    "CANONICAL_66_COLUMNS",
    "align_anomalies_with_vedic_astrology",
    "build_66_column_feature_matrix",
    "build_extended_unified_matrix",
    "extract_and_fuse_timeframe",
    "run_fusion_pipeline",
    "export_all_manifests",
    "validate_manifests",
]
