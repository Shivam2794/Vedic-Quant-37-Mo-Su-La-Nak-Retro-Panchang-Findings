# Project: Vedic Quant Discovery Engine (Round 2)

## Architecture
- **Data Layer**:
  - `data/spy_anomalies_omni_vedic_supreme.parquet` (1,408 anomaly rows × 397 columns, 0 NaNs, 1994–2026).
  - `data/raw_spy_1h_unified_2008_2026.parquet` (44,390 rows, 33,946 continuous RTH 1H bars).
  - `data/spy_continuous_rth_omni_vedic_baseline.parquet` (Enriched baseline dataset with 397 Omni-Vedic features).
- **Computation Engine Layer**:
  - `src/vedic_astrology/`: Swiss Ephemeris (`ephemeris.py`), Panchang (`panchang.py`), Nakshatras & Navamsha (`nakshatra_navamsha.py`), Aspects & Combustion (`aspects_combustion.py`), Omni-Vedic Fusion pipeline (`omni_vedic_fusion.py`).
  - `src/core/`: Shodashvarga Numba engine (`astro_vargas.py`), Jaimini Karakas (`jaimini_karakas.py`), Ashtakavarga & Vedha (`astro_ashtakvarga.py`, `vedha_engine.py`), Shadbala (`shadbala_core.py`), KP Placidus/Ephemeris (`kp_ephemeris_module.py`, `kp_placidus_module.py`), Vimshottari Interval Tree (`vimshottari_module.py`).
- **Discovery & Statistical Sieve Layer**:
  - `src/analysis/vedic_pattern_miner.py`: Baseline null calibration, univariate statistical tests (Fisher's exact, Chi-square, Benjamini-Hochberg FDR correction $p < 0.01$, KS 2-sample, Mann-Whitney U), lift ratio calculations, FP-Growth, 2/3/4-way conjunction miner, 10-pillar forensic drilldown.
  - `src/ml/vedic_feature_importance.py`: XGBoost, LightGBM, Random Forest classifiers (Directional) and regressors (Magnitude), Purged & Embargoed TimeSeriesSplit CV, TreeSHAP global top 20 rankings, and pairwise SHAP interaction matrices.
  - `src/analysis/run_discovery_engine.py`: Master end-to-end discovery coordinator.
- **Reporting & Visualization Layer**:
  - `reports/vedic_market_movers_codex.md`: Automated Master Codex of Market Movers.
  - `reports/charts/`: High-resolution figures (SHAP importance, SHAP interactions, lift/confidence scatter, KS distribution curves).

## Feature Inventory
| # | Feature / Requirement | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | R1: Baseline Null Calibration | Enrich continuous RTH 2008–2026 dataset (33,946 bars) with 397 Omni-Vedic features to generate unbiased null distribution | M1 | ORIGINAL_REQUEST §R1 |
| 2 | R2: Univariate Statistical Engine | Fisher's Exact, Chi-Square, Benjamini-Hochberg FDR ($p < 0.01, q < 0.05$), KS & Mann-Whitney U tests, Lift Ratio | M2 | ORIGINAL_REQUEST §R2 |
| 3 | R3: Higher-Order Combinatorial Mining | FP-Growth, Apriori, Decision Tree rule extraction, 2/3/4-way confluences (Support $\ge 10$, Conf $\ge 70\%$, Lift $\ge 2.0\text{x}$, $p < 0.005$), permutation tests | M3 | ORIGINAL_REQUEST §R3 |
| 4 | R4: ML Attribution & TreeSHAP | XGBoost / LightGBM / Random Forest modeling, Directional & Magnitude targets, TreeSHAP top 20, SHAP pairwise interactions, Purged CV | M4 | ORIGINAL_REQUEST §R4 |
| 5 | R5: Deep Vedic 10-Pillar Drilldown | Systematic forensic hypothesis testing across all 10 classical pillars (OOB/stations, Aspects, Vargas, Karakas, SAV, Shadbala, SBC/Vedha, KP Sub-Lords, Vimshottari, MTF) | M5 | ORIGINAL_REQUEST §R5 |
| 6 | R6: Master Codex & Visualizations | Automated generation of `reports/vedic_market_movers_codex.md`, structured tables, and matplotlib/seaborn visual charts | M6 | ORIGINAL_REQUEST §R6 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Baseline Null Calibration & Feature Alignment | Enrich continuous RTH 2008–2026 dataset with 397 Omni-Vedic features; validate zero NaNs and schema alignment | none | PLANNED |
| M2 | Univariate Statistical Significance & Lift Engine | Implement Fisher/Chi2/BH-FDR/KS/MW-U testing suite; compute Lift for all features across Direction and Timeframes | M1 | PLANNED |
| M3 | Higher-Order Combinatorial Pattern Mining | Implement FP-Growth, 2/3/4-way conjunction miner (Conf $\ge 70\%$, Lift $\ge 2.0$, $p < 0.005$), Decision Tree extraction, and permutation tests | M1, M2 | PLANNED |
| M4 | ML Feature Attribution & Interaction Mining | Implement XGBoost/LightGBM/RF models, Purged TimeSeriesSplit CV, TreeSHAP top 20 rankings, and pairwise interaction matrices | M1, M2 | PLANNED |
| M5 | Deep Vedic 10-Pillar Forensic Drilldown | Execute forensic hypothesis tests across all 10 Classical Vedic Pillars; extract Pillar-specific verified rules | M1, M2, M3 | PLANNED |
| M6 | Master Codex Generator & Visualizations | Assemble end-to-end pipeline, produce `reports/vedic_market_movers_codex.md` and chart suite | M1, M2, M3, M4, M5 | PLANNED |

## Interface Contracts
### M1 ↔ M2 / M3 / M4 / M5
- Input: `data/raw_spy_1h_unified_2008_2026.parquet` + `src/vedic_astrology/omni_vedic_fusion.py`
- Output: `data/spy_continuous_rth_omni_vedic_baseline.parquet` (Shape: $\ge 30,000 \times 397$, 0 NaNs).
- Function: `generate_rth_baseline_dataset(input_parquet, output_parquet, sample_limit=None) -> pd.DataFrame`

### M2 ↔ M3 / M5 / M6
- Module: `src/analysis/vedic_pattern_miner.py`
- Functions:
  - `compute_univariate_lift(df_anomaly, df_baseline, min_support=5) -> pd.DataFrame`
  - `run_fdr_significance_sieve(df_anomaly, df_baseline, alpha=0.01, fdr_threshold=0.05) -> pd.DataFrame`
  - `run_continuous_distribution_tests(df_anomaly, df_baseline) -> pd.DataFrame`

### M3 ↔ M5 / M6
- Module: `src/analysis/vedic_pattern_miner.py`
- Functions:
  - `mine_combinatorial_patterns(df_anomaly, df_baseline, k_max=4, min_support=10, min_confidence=0.70, min_lift=2.0, max_pvalue=0.005) -> pd.DataFrame`
  - `extract_decision_tree_rules(df_anomaly, df_baseline, max_depth=4) -> list[dict]`
  - `run_permutation_test(df_anomaly, df_baseline, rule, n_permutations=1000) -> float`

### M4 ↔ M6
- Module: `src/ml/vedic_feature_importance.py`
- Functions:
  - `train_directional_models(df_anomaly, target_col='Candle_Direction', cv_splits=5) -> dict`
  - `train_magnitude_models(df_anomaly, target_col='Body_To_ATR', cv_splits=5) -> dict`
  - `compute_shap_feature_attributions(model, X_train, X_test, feature_names) -> dict`
  - `compute_shap_interactions(model, X_sample, feature_names, top_n=20) -> dict`

### M5 ↔ M6
- Module: `src/analysis/vedic_pattern_miner.py`
- Function:
  - `run_10_pillar_forensic_drilldown(df_anomaly, df_baseline) -> dict[str, pd.DataFrame]`

### M6 ↔ User / Codex Deliverable
- Module: `src/analysis/run_discovery_engine.py`
- Output: `reports/vedic_market_movers_codex.md` + `reports/charts/*.png`

## Code Layout
```
├── data/
│   ├── spy_anomalies_omni_vedic_supreme.parquet (1,408 rows × 397 cols)
│   ├── raw_spy_1h_unified_2008_2026.parquet
│   └── spy_continuous_rth_omni_vedic_baseline.parquet
├── src/
│   ├── vedic_astrology/
│   │   ├── ephemeris.py
│   │   ├── panchang.py
│   │   ├── nakshatra_navamsha.py
│   │   ├── aspects_combustion.py
│   │   └── omni_vedic_fusion.py
│   ├── core/
│   │   ├── astro_vargas.py
│   │   ├── jaimini_karakas.py
│   │   ├── astro_ashtakvarga.py
│   │   ├── vedha_engine.py
│   │   ├── shadbala_core.py
│   │   ├── kp_ephemeris_module.py
│   │   ├── kp_placidus_module.py
│   │   └── vimshottari_module.py
│   ├── analysis/
│   │   ├── vedic_pattern_miner.py
│   │   └── run_discovery_engine.py
│   └── ml/
│       └── vedic_feature_importance.py
├── reports/
│   ├── vedic_market_movers_codex.md
│   └── charts/
│       ├── shap_top20_global.png
│       ├── shap_interaction_heatmap.png
│       ├── lift_vs_confidence_scatter.png
│       └── ks_continuous_distributions.png
└── tests/
    ├── test_vedic_pattern_miner.py
    ├── test_vedic_ml_engine.py
    ├── test_10_pillar_drilldown.py
    └── test_codex_integration.py
```
