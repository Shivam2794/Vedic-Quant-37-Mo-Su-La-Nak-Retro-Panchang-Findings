# E2E Test Infra: Vedic Quant Discovery Engine (Round 2)

## Test Philosophy
- Opaque-box, requirement-driven testing covering R1–R6.
- Zero data leakage, strict statistical significance verification ($p < 0.01$, FDR $q < 0.05$), non-zero empirical lift validation ($Lift \ge 2.0$), 0 NaNs across all matrices.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workloads.

## Feature Inventory
| # | Feature / Requirement | Source | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Real-World) |
|---|---|---|:---:|:---:|:---:|:---:|
| 1 | R1: Baseline Null Calibration | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 2 | R2: Univariate Statistical Sieve | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 3 | R3: Higher-Order Combinatorial Mining | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 4 | R4: ML Attribution & TreeSHAP | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |
| 5 | R5: Deep Vedic 10-Pillar Drilldown | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ | ✓ |
| 6 | R6: Master Codex & Visualizations | ORIGINAL_REQUEST §R6 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test runner: `pytest -v tests/`
- Test suites:
  - `tests/test_vedic_pattern_miner.py`: Tests baseline null generation, univariate lift, Fisher/Chi2, FDR correction, continuous tests (KS/Mann-Whitney), FP-Growth, conjunction mining.
  - `tests/test_vedic_ml_engine.py`: Tests XGBoost/LightGBM/RF models, Purged TimeSeriesSplit CV, TreeSHAP values, and pairwise interactions.
  - `tests/test_10_pillar_drilldown.py`: Tests all 10 classical forensic pillars (OOB, Aspects, Vargas, Karakas, SAV, Shadbala, SBC/Vedha, KP Sub-Lords, Vimshottari, MTF).
  - `tests/test_codex_integration.py`: Tests end-to-end codex generation, table formats, chart outputs, zero missing values, and file integrity.

## Coverage Thresholds
- Tier 1: $\ge 5$ tests per feature (30 total)
- Tier 2: $\ge 5$ tests per feature (30 total)
- Tier 3: Pairwise coverage across major feature interactions ($\ge 6$ tests)
- Tier 4: Real-world stress testing ($\ge 5$ tests)
- Total tests: $\ge 71$ tests
