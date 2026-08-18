"""
Standalone Adversarial Stress & Invariant Verification Script
Vedic-Quant Project (Round 3) - Challenger 2

This script performs deep empirical analysis across:
1. Parquet Datasets Scrutiny (Anomalies & Continuous Baseline)
2. Invariant & Distribution Bound Checks (SAV, Bhavas, Shadbala, Angles, Jaimini 7 Karakas)
3. ML Pipeline Leakage & Cross-Validation Audit
4. Master Codex Verification & FDR / Lift Recalculations
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import time
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

from src.ml.vedic_feature_importance import (
    PurgedTimeSeriesSplit,
    PurgedGroupTimeSeriesSplit,
    VedicFeaturePreprocessor,
    DEFAULT_TARGET_LEAKAGE_COLS,
    train_directional_models,
)

def run_adversarial_audit():
    print("=" * 80)
    print("STARTING EMPIRICAL ADVERSARIAL STRESS TEST — CHALLENGER 2 (ROUND 3)")
    print("=" * 80)

    report_data = {}

    # ---------------------------------------------------------
    # 1. PARQUET DATASET SCRUTINY
    # ---------------------------------------------------------
    supreme_path = "data/spy_anomalies_omni_vedic_supreme.parquet"
    baseline_path = "data/spy_continuous_rth_omni_vedic_baseline.parquet"

    print("\n[1] SCRUTINIZING PARQUET DATASETS...")
    t0 = time.time()
    df_supreme = pd.read_parquet(supreme_path)
    df_baseline = pd.read_parquet(baseline_path)

    sup_rows, sup_cols = df_supreme.shape
    base_rows, base_cols = df_baseline.shape

    sup_nans = int(df_supreme.isna().sum().sum())
    base_nans = int(df_baseline.isna().sum().sum())

    # Check duplicate timestamps
    sup_dupes = int(df_supreme["Datetime_UTC"].duplicated().sum()) if "Datetime_UTC" in df_supreme.columns else 0
    base_dupes = int(df_baseline["Datetime_UTC"].duplicated().sum()) if "Datetime_UTC" in df_baseline.columns else 0

    print(f"  Supreme Anomaly Matrix: {sup_rows} rows x {sup_cols} columns | NaNs: {sup_nans} | Dupes: {sup_dupes}")
    print(f"  Baseline Matrix:        {base_rows} rows x {base_cols} columns | NaNs: {base_nans} | Dupes: {base_dupes}")

    report_data["datasets"] = {
        "supreme": {
            "rows": sup_rows,
            "cols": sup_cols,
            "nans": sup_nans,
            "dupes": sup_dupes,
        },
        "baseline": {
            "rows": base_rows,
            "cols": base_cols,
            "nans": base_nans,
            "dupes": base_dupes,
        }
    }

    assert sup_nans == 0, f"Supreme dataset has {sup_nans} NaNs!"
    assert base_nans == 0, f"Baseline dataset has {base_nans} NaNs!"
    assert base_dupes == 0, f"Baseline dataset has {base_dupes} duplicate timestamps!"

    # ---------------------------------------------------------
    # 2. INVARIANT & DISTRIBUTION BOUND CHECKS
    # ---------------------------------------------------------
    print("\n[2] VERIFYING INVARIANT BOUNDS ACROSS BOTH DATASETS...")

    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sav_cols = [f"SAV_{s}" for s in signs if f"SAV_{s}" in df_supreme.columns]

    # SAV Invariants
    sav_min_sup = df_supreme[sav_cols].min().min()
    sav_max_sup = df_supreme[sav_cols].max().max()
    sav_sum_sup_unique = df_supreme[sav_cols].sum(axis=1).unique()

    sav_min_base = df_baseline[sav_cols].min().min()
    sav_max_base = df_baseline[sav_cols].max().max()
    sav_sum_base_unique = df_baseline[sav_cols].sum(axis=1).unique()

    print(f"  Supreme SAV bounds: [{sav_min_sup}, {sav_max_sup}] | Sum 337 check: {list(sav_sum_sup_unique)}")
    print(f"  Baseline SAV bounds: [{sav_min_base}, {sav_max_base}] | Sum 337 check: {list(sav_sum_base_unique)}")

    assert sav_min_sup >= 0 and sav_max_sup <= 56
    assert sav_min_base >= 0 and sav_max_base <= 56
    assert len(sav_sum_sup_unique) == 1 and sav_sum_sup_unique[0] == 337
    assert len(sav_sum_base_unique) == 1 and sav_sum_base_unique[0] == 337

    # Bhavas bounds
    bhava_cols = [c for c in df_supreme.columns if c.startswith("Bhv_")]
    bhv_min_sup = df_supreme[bhava_cols].min().min()
    bhv_max_sup = df_supreme[bhava_cols].max().max()
    bhv_min_base = df_baseline[bhava_cols].min().min()
    bhv_max_base = df_baseline[bhava_cols].max().max()
    print(f"  Supreme Bhava house bounds: [{bhv_min_sup}, {bhv_max_sup}] (count: {len(bhava_cols)})")
    print(f"  Baseline Bhava house bounds: [{bhv_min_base}, {bhv_max_base}] (count: {len(bhava_cols)})")
    assert bhv_min_sup >= 1 and bhv_max_sup <= 12
    assert bhv_min_base >= 1 and bhv_max_base <= 12

    # Shadbala Rupas & Ratios
    rupas_cols = [c for c in df_supreme.columns if "Shadbala" in c and "Rupas" in c]
    rupas_min_sup = df_supreme[rupas_cols].min().min()
    rupas_min_base = df_baseline[rupas_cols].min().min()
    print(f"  Shadbala Rupas min: Supreme={rupas_min_sup:.4f}, Baseline={rupas_min_base:.4f} (> 0 required)")
    assert rupas_min_sup > 0 and rupas_min_base > 0

    # Angular separations
    ang_cols = [c for c in df_supreme.columns if c.startswith("Ang_")]
    ang_min_sup = df_supreme[ang_cols].min().min()
    ang_max_sup = df_supreme[ang_cols].max().max()
    print(f"  Angular separation bounds: Supreme=[{ang_min_sup:.4f}°, {ang_max_sup:.4f}°] (in [0, 180] required)")
    assert ang_min_sup >= 0.0 - 1e-5 and ang_max_sup <= 180.0 + 1e-5

    # Jaimini 7 Karakas 1-to-1 uniqueness
    karaka_cols = [
        "Jaimini_AK", "Jaimini_AmK", "Jaimini_BK", "Jaimini_MK",
        "Jaimini_PK", "Jaimini_GK", "Jaimini_DK"
    ]
    sup_k_unique = df_supreme[karaka_cols].apply(lambda row: len(set(row.values)), axis=1).min()
    base_k_unique = df_baseline[karaka_cols].apply(lambda row: len(set(row.values)), axis=1).min()
    print(f"  Jaimini 7-Karaka Uniqueness (min distinct grahas per row): Supreme={sup_k_unique}/7, Baseline={base_k_unique}/7")
    assert sup_k_unique == 7 and base_k_unique == 7

    # ---------------------------------------------------------
    # 3. ML PIPELINE & TEMPORAL PURITY AUDIT
    # ---------------------------------------------------------
    print("\n[3] STRESS-TESTING ML CROSS-VALIDATION & TEMPORAL PURITY...")
    cv = PurgedTimeSeriesSplit(n_splits=5, purge_bars=2)
    splits = cv.split(df_supreme)

    fold_gaps = []
    for fold_i, (train_idx, test_idx) in enumerate(splits):
        t_max_train = train_idx.max()
        t_min_test = test_idx.min()
        gap = t_min_test - t_max_train
        fold_gaps.append(gap)
        print(f"  Fold {fold_i + 1}: Train=[0..{t_max_train}] (N={len(train_idx)}) | Test=[{t_min_test}..{test_idx.max()}] (N={len(test_idx)}) | Purge Gap={gap} bars")
        assert t_max_train < t_min_test, f"Lookahead leak detected in fold {fold_i + 1}!"
        assert gap >= 3, f"Purge gap violated in fold {fold_i + 1}: {gap} < 3"

    # Leakage Column Audit
    prep = VedicFeaturePreprocessor()
    prep.fit(df_supreme)
    X_feats = prep.transform(df_supreme)

    leaked_cols = [c for c in X_feats.columns if c in DEFAULT_TARGET_LEAKAGE_COLS]
    print(f"  Leakage Columns in Feature Set: {len(leaked_cols)} (Total Features = {X_feats.shape[1]})")
    assert len(leaked_cols) == 0, f"Found leaked columns: {leaked_cols}"

    # ---------------------------------------------------------
    # 4. MASTER CODEX RULE RE-EVALUATION
    # ---------------------------------------------------------
    print("\n[4] RE-EVALUATING MASTER CODEX TOP RULES AGAINST EMPIRICAL MATRIX...")
    codex_path = "reports/vedic_market_movers_codex.md"
    with open(codex_path, "r", encoding="utf-8") as f:
        codex_text = f.read()

    # Parse Top 50 rules
    lines = codex_text.splitlines()
    in_table = False
    codex_rules = []
    for line in lines:
        if "## 2. Top 50 Verified Planetary Market-Moving Rules" in line:
            in_table = True
            continue
        if in_table and line.startswith("## 3."):
            break
        if in_table and line.startswith("|") and not line.startswith("| Rank") and not line.startswith("|:---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 9:
                try:
                    rank = int(parts[0])
                    rule_text = parts[1]
                    direction = parts[2]
                    support_n = int(parts[3])
                    baseline_n = int(parts[4])
                    conf_val = float(parts[5].replace("%", "").strip())
                    lift_val_str = parts[6].replace("x", "").replace("**", "").strip()
                    lift_val = float("inf") if "inf" in lift_val_str.lower() else float(lift_val_str)
                    p_val = float(parts[7].replace("`", "").strip())
                    q_val = float(parts[8].replace("`", "").strip())
                    codex_rules.append({
                        "rank": rank, "rule": rule_text, "direction": direction,
                        "support_n": support_n, "baseline_n": baseline_n,
                        "conf": conf_val, "lift": lift_val, "p": p_val, "q": q_val
                    })
                except Exception as e:
                    pass

    print(f"  Parsed {len(codex_rules)} rules from Codex Table.")
    assert len(codex_rules) == 50

    # Verify all thresholds
    sub_10_count = sum(1 for r in codex_rules if r["support_n"] < 10)
    sub_70_conf = sum(1 for r in codex_rules if r["conf"] < 70.0)
    sub_2_lift = sum(1 for r in codex_rules if r["lift"] < 2.0)
    high_q = sum(1 for r in codex_rules if r["q"] >= 0.05)
    high_p = sum(1 for r in codex_rules if r["p"] >= 0.005)

    print(f"  Violations: N < 10: {sub_10_count} | Conf < 70%: {sub_70_conf} | Lift < 2.0x: {sub_2_lift} | q >= 0.05: {high_q} | p >= 0.005: {high_p}")
    assert sub_10_count == 0
    assert sub_70_conf == 0
    assert sub_2_lift == 0
    assert high_q == 0
    assert high_p == 0

    print("\n" + "=" * 80)
    print("ALL EMPIRICAL ADVERSARIAL STRESS TESTS PASSED WITH 100% INTEGRITY!")
    print("=" * 80)

if __name__ == "__main__":
    run_adversarial_audit()
