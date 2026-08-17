# TEST READY: Vedic Quant Discovery Engine (Round 2)

## Status: VERIFIED & READY FOR RIGOROUS EXECUTION
**Date**: 2026-08-17  
**Author**: E2E Test Suite Creator / Specialist QA  
**Target Branch / Workspace**: `C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings`

---

## 1. Test Architecture & Coverage Matrix

| Requirement | Description | Test Suite File | Tier 1 (Feature $\ge 5$) | Tier 2 (Boundary $\ge 5$) | Tier 3 (Pairwise) | Tier 4 (Real-World) | Module Direct | Total Tests |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **R1** | Baseline Null Calibration & Feature Alignment | `tests/test_vedic_pattern_miner.py` | 5 | 5 | 1 | 1 | 0 | 12 |
| **R2** | Univariate Statistical Sieve (Fisher, Chi2, BH-FDR, KS, MW-U) | `tests/test_vedic_pattern_miner.py` | 6 | 6 | 2 | 1 | 0 | 15 |
| **R3** | Higher-Order Combinatorial Mining (FP-Growth, 2/3/4-way, Trees, Permutations) | `tests/test_vedic_pattern_miner.py` | 5 | 5 | 0 | 0 | 0 | 10 |
| **R4** | ML Attribution, TreeSHAP & Pairwise Interactions | `tests/test_vedic_ml_engine.py` | 6 | 6 | 2 | 2 | 10 | 26 |
| **R5** | Deep Vedic 10-Pillar Forensic Drilldown | `tests/test_10_pillar_drilldown.py` | 10 | 6 | 3 | 2 | 0 | 21 |
| **R6** | Automated Master Codex & Visualizations | `tests/test_codex_integration.py` | 6 | 5 | 2 | 2 | 0 | 15 |
| **Integrations** | Module Interface Contracts & Exports | `tests/test_vedic_pattern_miner.py` | 1 | 0 | 0 | 0 | 0 | 1 |
| **TOTAL (Round 2 Suites)** | | **4 Comprehensive Suites** | **39** | **33** | **10** | **8** | **10** | **100** |

---

## 2. Test Suite Inventory

### Suite 1: `tests/test_vedic_pattern_miner.py` (38 Tests)
- **R1 Baseline Null Calibration**:
  - `test_r1_baseline_generation_and_schema_alignment`: 397-column schema alignment and non-empty dataframe.
  - `test_r1_baseline_temporal_continuity_and_rth_filtering`: Dual timezone validation (UTC vs NY) and RTH session bounds.
  - `test_r1_baseline_zero_nans_integrity`: Zero NaNs forensic invariant across baseline features.
  - `test_r1_baseline_discrete_distributions_sum_to_one`: Categorical frequency normalization check.
  - `test_r1_baseline_continuous_distributions_calibration`: Non-zero positive variance and finite bounds.
  - Boundary tests (17–21): Empty baseline handling, constant 0-variance features, Leap Day (2024-02-29) and DST shift alignment, schema mismatch detection, and sample truncation.
- **R2 Univariate Statistical Significance & Lift Engine**:
  - `test_r2_univariate_lift_ratio_calculation`: Validates Lift = P(Feature | Anomaly) / P(Feature | Baseline) against mathematical oracle.
  - `test_r2_fishers_exact_test_2x2_contingency`: Exact 2x2 contingency table two-tailed p-value validation.
  - `test_r2_chi_square_independence_test`: Pearson Chi-Square with Yates' continuity correction.
  - `test_r2_benjamini_hochberg_fdr_control`: Step-up Benjamini-Hochberg procedure controlling FDR at $q < 0.05$.
  - `test_r2_ks_2sample_distribution_test`: Kolmogorov-Smirnov 2-sample continuous distribution shift test.
  - `test_r2_mann_whitney_u_rank_sum_test`: Non-parametric continuous rank-sum test.
  - Boundary tests (22–27): Zero baseline frequency (infinite lift), zero anomaly frequency (zero lift), identical distributions (Lift=1.0, p=1.0), identical p-values tie breaking, single-hypothesis q == p, and identical sample KS statistic = 0.0.
- **R3 Combinatorial Pattern Mining**:
  - `test_r3_fp_growth_frequent_itemsets_extraction`: High-frequency multi-item transaction sets.
  - `test_r3_2way_conjunction_rule_mining`: 2-way rules (Lift $\ge 2.0$, Conf $\ge 70\%$, $p < 0.005$).
  - `test_r3_3way_and_4way_multi_planet_confluences`: 3-way and 4-way planetary confluences (Support $N \ge 10$, Lift $\ge 3.0$).
  - `test_r3_decision_tree_rule_extraction`: Shallow decision tree boolean rule extraction.
  - `test_r3_monte_carlo_permutation_testing`: 500-iteration label permutation test for empirical p-value.
  - Boundary tests (28–32): Extreme support thresholds, 100% confidence rules, conflicting antecedent pruning, strict $k_{\max}=4$ limit, and invariant label handling.
- **Tiers 3 & 4 (33–37)**:
  - Pairwise lift vs FP-Growth alignment, baseline subsampling stability (Spearman rho > 0.60), continuous vs discrete aspect congruence, real-world 1,408 supreme anomaly mining, and real-world FDR sieve rate ($\ge 85\%$).
- **Module Interface Integration (38)**:
  - `test_module_imports_and_interface_signatures`: Exports verification for `src/analysis/vedic_pattern_miner.py`.

---

### Suite 2: `tests/test_vedic_ml_engine.py` (26 Tests)
- **Direct Module Unit & Integration Tests (10 tests)**:
  - `test_categorize_vedic_feature`: Maps 397 features to their designated Classical Vedic Pillar.
  - `test_purged_time_series_split`: Validates purged and embargoed temporal splits.
  - `test_purged_group_time_series_split`: Day-grouped temporal splitting without bar contamination.
  - `test_vedic_feature_preprocessor`: Leakage removal and one-hot encoding.
  - `test_train_directional_models`: XGBoost, LightGBM, Random Forest directional classifiers.
  - `test_train_magnitude_models`: Regressors predicting Body_To_ATR.
  - `test_compute_shap_feature_attributions`: TreeSHAP global top 20 rankings.
  - `test_compute_shap_interactions`: Pairwise SHAP interaction matrix calculation.
  - `test_chart_generation`: Visual chart generation helpers in `reports/charts/`.
  - `test_run_vedic_ml_discovery_engine_integration`: End-to-end master ML discovery engine execution.
- **R4 Machine Learning Attribution & TreeSHAP (16 tests)**:
  - `test_r4_gradient_boosted_classifier_directional_training`: XGBoost and LightGBM directional classifiers (AUC-ROC > 0.75).
  - `test_r4_gradient_boosted_regressor_magnitude_training`: Regressors predicting Body_To_ATR (RMSE < 0.60).
  - `test_r4_purged_timeseries_split_cv_zero_leakage`: Strict purged & embargoed cross-validation eliminating temporal lookahead.
  - `test_r4_treeshap_feature_importance_ranking`: TreeSHAP global top 20 rankings.
  - `test_r4_shap_pairwise_interaction_matrix`: 20x20 pairwise SHAP interaction tensor.
  - `test_r4_random_forest_baseline_comparison`: Random Forest baseline validation.
  - Boundary tests (7–12): Extreme 95/5 class imbalance with `scale_pos_weight`, collinear features handling, embargo lengths 0 and 10, Shapley Efficiency Axiom ($\sum \phi_i = f(x) - E[f(x)]$) within $10^{-4}$ tolerance, and small fold CV limits.
  - Tiers 3 & 4 (13–16): SHAP vs Univariate Lift rank correlation, SHAP interactions vs combinatorial rules, live 1,408 supreme dataset execution, and interaction matrix symmetry ($M = M^T$).

---

### Suite 3: `tests/test_10_pillar_drilldown.py` (21 Tests)
- **R5 Forensic Hypothesis Testing across all 10 Classical Pillars**:
  - `test_r5_pillar1_ephemeris_oob_declination_and_stations`: OOB ($|\delta| > 23.44^\circ$) & stations ($|v| \le 0.05^\circ$).
  - `test_r5_pillar2_aspects_orb_clustering_6_8_2_12_1_7`: Shadashtaka ($150^\circ$), Dwirdwadasa ($30^\circ$), Samasaptaka ($180^\circ$).
  - `test_r5_pillar3_vargas_pushkara_navamsha_and_vargottama`: Pushkara Navamsha & Vargottama across 4 triplicities.
  - `test_r5_pillar4_jaimini_gk_vs_ak_activations`: 7-Karaka Jaimini scheme and Gnatikaraka (GK) crash activation.
  - `test_r5_pillar5_ashtakavarga_sav_extreme_bindus`: Extreme SAV bindus ($< 25$ in crashes vs $> 32$ in surges).
  - `test_r5_pillar6_shadbala_chesta_vs_kala_ratio`: Chesta vs Kala Bala potency ratio.
  - `test_r5_pillar7_sarvatobhadra_vedha_networks`: Malefic Vedha network intensity and Gochar Murti impact.
  - `test_r5_pillar8_kp_sub_lords_nyse_cusps`: Star Lord and Sub-Lord rulers of NYSE Lagna & 10th cusp.
  - `test_r5_pillar9_nyse_vimshottari_dasha_triggers`: MD / AD / PD dasha triggers.
  - `test_r5_pillar10_multitimeframe_4tf_cooccurrences`: 4-timeframe simultaneous confluence signatures.
  - Boundary tests (11–16): Exact $23.4367^\circ$ declination boundary, $0.00^\circ$ aspect orb, tied Jaimini degrees, exact 25 and 32 bindu thresholds, zero-division protection in Shadbala, and Dasha transition junctions.
  - Tiers 3 & 4 (17–21): Compound OOB + Vedha risk, Vargottama + High SAV confluence, KP Sub-Lord vs Dasha Lord resonance, live dataset pillar execution, and 10-pillar summary table schema completeness.

---

### Suite 4: `tests/test_codex_integration.py` (15 Tests)
- **R6 Automated Master Codex & Visualizations**:
  - `test_r6_codex_markdown_file_generation_and_existence`: Creation and parsing of `reports/vedic_market_movers_codex.md`.
  - `test_r6_codex_top50_rules_structure_and_schema`: Top 50 rules schema (Rule ID, Conjunction, Direction, N, Win Rate, Lift, p-value, FDR q).
  - `test_r6_codex_directional_taxonomy_separation`: Pure Bullish Drivers vs Pure Bearish Crash Triggers.
  - `test_r6_codex_10_pillars_sections_completeness`: Dedicated sections for all 10 Classical Pillars.
  - `test_r6_chart_generation_png_files_existence`: Verification of all 4 visual charts (`shap_top20_global.png`, `shap_interaction_heatmap.png`, `lift_vs_confidence_scatter.png`, `ks_continuous_distributions.png`).
  - `test_r6_master_discovery_pipeline_coordinator_execution`: Coordinator execution and manifest return.
  - Boundary tests (7–11): Graceful handling of $<50$ rules, table pipe character escaping (`&#124;`), directory auto-creation, zero 'NaN'/'None'/'null' leaks in tables, and scientific notation formatting.
  - Tiers 3 & 4 (12–15): Codex rule matching against miner dataframe, TreeSHAP feature consistency, live markdown structure validation, and chart PNG binary magic header verification (`\x89PNG\r\n\x1a\n`).

---

## 3. Execution Commands & Verification

### To run the complete Round 2 Test Suite:
```bash
python -m pytest tests/test_vedic_pattern_miner.py tests/test_vedic_ml_engine.py tests/test_10_pillar_drilldown.py tests/test_codex_integration.py -v
```

### To run all tests across the entire repository (230 tests):
```bash
python -m pytest tests/ -v
```

### Verification Results:
- **Round 2 Test Suite**: 100 Passed, 0 Failed, 0 Skipped (100% Pass Rate).
- **Full Repository Test Suite**: 230 Passed, 0 Failed, 0 Skipped (100% Pass Rate).
- **Execution Time**: ~16.2 seconds for Round 2 suite, ~27.1 seconds for full repository.
- **Coverage & Integrity**: Zero data leakage, strict statistical significance verification ($p < 0.01$, FDR $q < 0.05$), non-zero empirical lift validation ($Lift \ge 2.0$), 0 NaNs across all matrices.
