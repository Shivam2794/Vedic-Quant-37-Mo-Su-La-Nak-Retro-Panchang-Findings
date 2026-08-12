# Orion Pipeline Codebase Scan

This report details the findings of a comprehensive scan of the `orion_pipeline` directory, including all `.py`, `.parquet`, and `.json` files. The functionality of each file has been inferred based on its name and location within the pipeline's architecture.

## 1. Root Directory

### Core Execution & Orchestration
- **`orion_data_lake.py`**: Interacts with the foundational data lake, handling IO operations for large datasets.
- **`orion_ephemeris_core.py`** / **`ephemeris_core.py`**: Central processing logic for ephemeris (planetary/astronomical) data.
- **`orion_genetic_combinatorics.py`**: Core combinatorics for the genetic/evolutionary algorithm parts of the system.
- **`orion_gpu_bruteforce.py`**: GPU-accelerated brute-forcing utilities for optimizing parameters or feature searches.
- **`orion_spectral_pruning.py`**: Core logic for pruning features or nodes using spectral methods.
- **`orion_tensor_backtest.py`**: Tensorized backtesting engine to evaluate strategies across multidimensional parameter spaces.
- **`orion_wfo_cpcv.py`**: Implements Walk-Forward Optimization (WFO) and Combinatorial Purged Cross-Validation (CPCV).
- **`run_smart_ml_pipeline.py`**: Main entry point script that orchestrates the `smart_ml` sub-agents.
- **`ray_orchestrator.py`**: Manages distributed computing and task parallelization using Ray.
- **`matrix_compiler.py`**: Compiles large feature sets into optimized matrices.
- **`parallel_logic.py`**: Defines parallel processing configurations and thread safety structures.
- **`kill_switch.py`**: Mechanism to safely terminate long-running backtests or pipelines.
- **`get_imports.py`**: A utility script to list or extract module imports within the project.
- **`integration_test.py`**: Main script for high-level integration testing of the pipeline.

### Trading & Evaluation Logic
- **`paper_trading.py`**: Execution logic for simulated live paper trading.
- **`zero_beta.py`**: Constructs market-neutral (zero-beta) portfolios.
- **`drawdown_penalty.py`**: Calculates penalties during backtests for exceeding maximum drawdown limits.
- **`fitness_sortino.py`**: Sortino-ratio based fitness evaluation for the evolutionary optimizer.
- **`early_termination.py`**: Contains heuristics to terminate unprofitable paths during backtesting early.
- **`enforce_precision.py`**: Ensures numerical stability and precision alignment across float operations.
- **`validation.py`**: Handles out-of-sample validation metrics.
- **`wfo_shifters.py`**: Time-shifting utilities for Walk-Forward Optimization windows.
- **`crash_vectors.py`**: Detects or simulates historical crash regimes (e.g., flash crashes) for stress testing.

### Modeling & Physics Systems
- **`xgboost_multi_obj.py`**: Custom multi-objective function wrapper for XGBoost models.
- **`neural_surrogate.py`**: A neural network model approximating a heavier simulation (surrogate model).
- **`t2n_engine.py` / `t2t_engine.py`**: Transformation engines, potentially Tensor-to-Network and Tensor-to-Tensor mapping layers.
- **`moduli_sync.py`**: Synchronization logic for periodic functions (potentially related to physical/cyclical data).
- **`kinematics.py`**: Applies kinematic physics equations, likely to price velocity and acceleration.
- **`harmonic_oscillator.py`**: Uses harmonic oscillation math to model cyclical price trends.
- **`house_systems.py`**: Computes astrological "house" divisions for ephemeris features.
- **`lunar_metrics.py`**: Specific feature extractors for lunar cycles (phases, nodes).
- **`spy_genesis.py` / `qqq_genesis.py`**: Generation scripts for baseline index behaviors (SPY, QQQ).
- **`numpy_generators.py`**: Synthetic data or sequence generation using NumPy.

### Root Testing Scripts
- **`test_ch5_dynamic_size.py`**: Tests chapter 5 dynamic sizing.
- **`test_continuous_target.py`**: Tests predictions against continuous targets.
- **`test_diversity_collapse.py` / `test_diversity_collapse2.py`**: Tests evolutionary genetic diversity collapse.
- **`test_evolve.py` / `test_evolve2.py`**: Tests the genetic evolution loops.
- **`test_fitness_leak.py`**: Detects data leakage in fitness functions.
- **`test_full_pipeline.py`**: End-to-end pipeline test.
- **`test_guided.py` / `test_guided_auto.py`**: Tests guided genetic mutations.
- **`test_house_systems.py`**: Tests ephemeris house system calculations.
- **`test_long_loop.py`**: Tests long-running event loops.
- **`test_mutation.py`**: Tests genomic mutation functions.
- **`test_orion_genetic.py`**: Tests genetic core combinatorics.
- **`test_packed.py`**: Tests memory-packed struct logic.
- **`test_precision.py`**: Tests numerical precision checks.
- **`test_recursion.py`**: Tests recursive algorithms for stack overflows.
- **`test_safe.py`**: Tests execution within safe mode bounds.
- **`test_strict.py`**: Tests pipeline in strict assertion mode.

### Root "Chapter 3" Scripts (Tree Explainers)
- **`chapter3_agent1_dmatrix.py`**: Prepares data into XGBoost DMatrix structures.
- **`chapter3_agent2_monotonic.py`**: Applies monotonic constraints to trees.
- **`chapter3_agent3_objective.py`**: Custom loss objective functions.
- **`chapter3_agent4_evaluation.py`**: Evaluation metric callbacks for training.
- **`chapter3_agent5_regularization.py`**: Implements L1/L2 regularization tuning.
- **`chapter3_agent6_cuda_params.py`**: Optimizes CUDA GPU configurations for training.
- **`chapter3_agent7_json_parser.py`**: Parses XGBoost model JSON representations.
- **`chapter3_agent8_dfs.py`**: Depth-First Search for traversing tree paths.
- **`chapter3_agent9_pairs.py`**: Identifies pair-wise feature interactions.
- **`chapter3_agent10_triplets.py`**: Identifies triplet feature interactions.
- **`chapter3_agent11_counter.py`**: Counts frequency of decision paths.
- **`chapter3_agent12_matrix_out.py`**: Outputs tree structures as matrices.
- **`chapter3_agent13_tree_explainer.py`**: Extracts TreeSHAP logic for explainability.
- **`chapter3_agent14_global_shap.py`**: Computes global SHAP feature importances.
- **`chapter3_agent15_shap_approx.py`**: Computes approximated SHAP values for speed.
- **`chapter3_agent16_dependency_plot.py`**: Generates partial dependence and SHAP plots.
- **`chapter3_agent17_noise_filter.py`**: Filters noisy features based on SHAP values.
- **`chapter3_agent18_additivity.py`**: Ensures additivity rules in tree explainers are met.
- **`chapter3_agent19_master_aggregator.py`**: Aggregates all chapter 3 agent results into a final explainer model.

---

## 2. Ingestion Subdirectory (`ingestion/`)
*Handles the initial acquisition and serialization of raw data.*
- **`market_data.py`**: Fetches historical and live pricing data.
- **`jpl_swisseph.py`**: Interfaces with the Swiss Ephemeris JPL library for planetary coordinates.
- **`arrow_serializer.py`**: Converts raw datasets into Apache Arrow tables for in-memory speed.
- **`parquet_writer.py`**: Commits Arrow tables to disk as Parquet files for the data lake.

---

## 3. Alignment Subdirectory (`alignment/`)
*Responsible for time-series alignment and normalization.*
- **`asof_join.py`**: Uses 'as-of' joins to align ticks and varying frequency time-series cleanly.
- **`clickhouse_index.py`**: Defines sorting keys and index structures for pushing aligned data to ClickHouse.
- **`ephemeris_norm.py`**: Normalizes astrological/ephemeris degrees (0-360) and distances.
- **`market_norm.py`**: Normalizes pricing data (e.g., z-scores, log returns).
- **`test_asof_bias.py`**: Tests the asof join for lookahead bias.

---

## 4. Bucketing Subdirectory (`bucketing/`)
*Aggregates time-series data into discrete temporal bins or tensors.*
- **`intraday_bucketing.py`**: Bins high-frequency data into minute or hourly intraday bars.
- **`short_swing.py`**: Creates buckets for short-term swing trading (e.g., daily/multi-day).
- **`long_swing.py`**: Creates buckets for macro, long-term swings (e.g., weekly/monthly).
- **`spline_interpolation.py`**: Fits splines over empty buckets to impute missing data smoothly.
- **`tensor_aggregator.py`**: Reshapes the buckets into 3D tensors suitable for deep learning.

---

## 5. Chapter 4 Subdirectory (`chapter4/`)
*Focuses on feature selection via spectral clustering and submodular maximization.*
- **`affinity_matrix.py`**: Calculates affinity/similarity matrices across features.
- **`mic_proxy.py`**: Calculates the Maximal Information Coefficient (MIC) to gauge non-linear dependencies.
- **`spectral_clustering.py`**: Clusters features to identify redundant groups using graph laplacians.
- **`submodular_maximization.py`**: Selects the optimal set of features by maximizing a submodular diversity function.
- **`test_laplacian.py` / `test_laplacian2.py`**: Tests laplacian matrix construction.
- **`test_mic_proxy.py`**: Tests the MIC computation.
- **`test_psd.py`**: Validates positive semi-definite properties of matrices.
- **`test_qa1.py` / `test_qa1_brutal.py`**: Various QA testing for the clustering logic.

---

## 6. Chapter 5 Subdirectory (`chapter5/`)
*Focuses on Evolutionary Algorithms and Sparse Autoencoders (SAE).*
- **`evolutionary_loop.py`**: Main loop for evaluating generations of trading strategies/features.
- **`crossover.py`**: Handles genetic crossover mechanics.
- **`mutation.py`**: Standard genetic mutation rules.
- **`guided_mutation.py`**: Applies heuristically guided mutations to bypass local minima.
- **`selection.py`**: Evaluates and selects the fittest surviving genomes.
- **`fitness_evaluator.py`**: Custom scoring system combining return, risk, and structural metrics.
- **`complexity_penalty.py`**: Penalizes overly complex models to enforce parsimony.
- **`cv_wrapper.py`**: Cross-validation wrapper tailored for evolutionary individuals.
- **`sae_training.py`**: Trains Sparse Autoencoders on selected subsets.
- **`sae_weights.py`**: Manages extraction and processing of SAE layer weights.
- **`encoder.py`**: Latent encoder pipeline for standardizing feature inputs.
- **`final_compiler.py`**: Compiles the winning genome and SAE into a deployable format.
- **`best_subsets_compiled.json`**: Stored configuration output of the best-performing feature sets discovered during the evolutionary run.

---

## 7. Smart ML Subdirectory (`smart_ml/`)
*Multi-agent architecture for automated machine learning strategies.*
- **`alpha_agent1_basket_filter.py`**: Filters out low-variance or highly correlated asset baskets.
- **`alpha_agent2_binarizer.py`**: Discretizes continuous signals into binary sequences.
- **`alpha_agent3_fpgrowth.py`**: Runs FP-Growth algorithm to find frequent pattern itemsets in the binary sequences.
- **`alpha_agent4_assoc_rules.py`**: Extracts association rules from frequent patterns.
- **`alpha_agent5_signal_filter.py`**: Final filter to discard weak association rules.
- **`beta_agent6_transformer.py`**: Initializes transformer-based attention models.
- **`beta_agent7_attention_pool.py`**: Applies pooling operations over transformer attention heads.
- **`beta_agent8_attn_baseline.py`**: Establishes baseline comparisons for attention scores.
- **`beta_agent9_train_transformer.py`**: Training loop for the transformer models.
- **`beta_agent10_attn_mapper.py`**: Maps high-attention tokens back to the original feature names.
- **`gamma_agent11_base_encoder.py`**: Base neural encoder for advanced state representation.
- **`gamma_agent12_sae.py`**: Implements Sparse Autoencoders for anomaly detection.
- **`gamma_agent13_sae_pipeline.py`**: Pipeline manager for SAE training and inference.
- **`gamma_agent14_latent_decoder.py`**: Decodes latent spaces into actionable predictions.
- **`gamma_agent15_master_aggregator.py`**: Aggregates inputs from Alpha (FP-Growth), Beta (Transformers), and Gamma (SAE) agents into the master signal.

---

## 8. Output Subdirectory (`output/`)
- **`stage3_xgb_interactions.json`**: Cached output defining interaction effects and node metrics extracted from the XGBoost models (likely tied to Chapter 3 results).
