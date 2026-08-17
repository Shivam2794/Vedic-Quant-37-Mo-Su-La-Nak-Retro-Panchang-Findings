"""
Unit & Integration Tests for Module 4 Quality Inspector Suite.
Verifies programmatic execution, 10-vector checks, and report generators.
"""

import os
import json
import pytest
from src.quality.failure_vectors_inspector import (
    QualityInspector,
    FailureVectorResult,
    run_full_quality_audit,
    generate_all_reports,
)


class TestQualityInspectorSuite:
    """Test suite for the QualityInspector engine."""

    def test_inspector_initialization(self, data_dir, project_root):
        """Tests that QualityInspector initializes with valid directories."""
        inspector = QualityInspector(data_dir=data_dir)
        assert inspector.data_dir == data_dir
        assert os.path.exists(inspector.anomalies_dir)
        assert os.path.exists(inspector.reports_dir)

    def test_full_quality_audit_execution(self, data_dir):
        """Tests that run_full_quality_audit executes all 10 vectors with 100% pass."""
        results = run_full_quality_audit(data_dir=data_dir)
        assert len(results) == 10

        for vid in range(1, 11):
            assert vid in results
            r = results[vid]
            assert isinstance(r, FailureVectorResult)
            assert r.vector_id == vid
            assert r.status == "PASSED", f"Vector {vid} ({r.vector_name}) failed: {r.errors}"
            assert r.score == 100.0
            assert r.checks_failed == 0
            assert r.checks_passed == r.checks_run
            assert len(r.mathematical_proof) > 0

    def test_quality_inspection_markdown_report_generation(self, data_dir, project_root):
        """Tests generating quality_inspection_report.md and verifies key sections."""
        inspector = QualityInspector(data_dir=data_dir)
        report_path = os.path.join(project_root, "reports", "quality_inspection_report.md")
        content = inspector.generate_quality_inspection_report(output_path=report_path)

        assert os.path.exists(report_path)
        assert "PASSED (100% COMPLIANT)" in content
        assert "Total Master Anomalies Extracted Across All Timeframes**:" in content
        assert "Vector 1: Lookahead Bias" in content
        assert "Vector 10: Downstream 66-Column Schema Compatibility" in content

    def test_mathematical_validation_json_report_generation(self, data_dir, project_root):
        """Tests generating mathematical_validation_report.json and verifies JSON schema."""
        inspector = QualityInspector(data_dir=data_dir)
        report_path = os.path.join(project_root, "reports", "mathematical_validation_report.json")
        json_report = inspector.generate_mathematical_validation_report(output_path=report_path)

        assert os.path.exists(report_path)
        assert json_report["overall_status"] == "PASSED"
        assert json_report["failed_atomic_checks"] == 0
        assert json_report["union_sum_invariant"]["invariant_satisfied"] is True
        assert json_report["union_sum_invariant"]["master_manifest_count"] > 0

        # Check SHA-256 checksums exist
        checksums = json_report["file_checksums_provenance"]
        assert "data/anomalies/master_anomaly_manifest.parquet" in checksums
        assert checksums["data/anomalies/master_anomaly_manifest.parquet"]["exists"] is True
        assert len(checksums["data/anomalies/master_anomaly_manifest.parquet"]["sha256"]) == 64

    def test_generate_all_reports_convenience_helper(self, data_dir):
        """Tests generate_all_reports helper."""
        md_text, json_dict = generate_all_reports(data_dir=data_dir)
        assert isinstance(md_text, str)
        assert isinstance(json_dict, dict)
        assert json_dict["overall_status"] == "PASSED"
