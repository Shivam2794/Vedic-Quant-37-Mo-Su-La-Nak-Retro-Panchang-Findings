# E2E Test Infra: Vedic Quant Neural Network Pipeline

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Financial Market Data Ingestion | PROJECT.md Data Layer, R2 | 5 | 5 | ✓ |
| 2 | Astrological Z-Axis Feature Compiler | PROJECT.md Data Layer, R1 | 5 | 5 | ✓ |
| 3 | Sparse Autoencoder (SAE) Representation Layer | PROJECT.md Model Layer, R1 | 5 | 5 | ✓ |
| 4 | Deep MLP Prediction Head | PROJECT.md Model Layer, R1, R2 | 5 | 5 | ✓ |
| 5 | Purged & Embargoed Walk-Forward CV | PROJECT.md Validation Layer, R3 | 5 | 5 | ✓ |
| 6 | Unified Evaluation & Baseline Benchmark Suite | PROJECT.md Evaluation Layer, R4 | 5 | 5 | ✓ |

### Feature Descriptions and Contracts

#### 1. Financial Market Data Ingestion
- **Description**: Ingests daily market data for SPY, QQQ, and DIA from yfinance or local parquet cache.
- **Input Parameters**:
  - `tickers`: List of string tickers (e.g., `["SPY", "QQQ", "DIA"]`).
  - `start_date`, `end_date`: ISO-8601 strings (e.g., `"2006-01-01"`, `"2026-01-01"`).
- **Expected Output Behavior**: Returns a daily-indexed Pandas DataFrame containing OHLCV and Adjusted Close with zero NaNs or missing records.
- **Tier 1 (Happy Path)**: Downloads/reads daily ETF records, verifies columns (`Open`, `High`, `Low`, `Close`, `Volume`), and validates shapes.
- **Tier 2 (Boundary)**: Mismatched dates, missing periods, zero volume, API timeouts, and invalid symbols.
- **Tier 3 (Combinatorial)**: Validates alignment across multiple frequencies (daily vs weekly) and multiple timeframes.

#### 2. Astrological Z-Axis Feature Compiler
- **Description**: Compiles continuous astronomical features (planetary speed, longitude, declination, aspects) for 9 planets.
- **Input Parameters**:
  - `timestamps`: Pandas DatetimeIndex matching financial data.
  - `planets`: List of 9 celestial bodies.
  - `ayanamsha`: Sidereal correction mode.
- **Expected Output Behavior**: Returns a Pandas DataFrame with planetary positions and Z-axis components, shape `(N_days, 9 * 4)`.
- **Tier 1 (Happy Path)**: Calculates planetary longitudinal degrees and speeds, Nakshatra indices [0-26], Rasi indices [0-11], and maps them to timestamps.
- **Tier 2 (Boundary)**: Handling of retrograde transitions (speeds crossing zero), zodiac cross-over bounds (0°/360°), and empty/NaN indices.
- **Tier 3 (Combinatorial)**: Validates the combined output dataset aligner under varying combinations of ayanamsha settings (Lahiri vs. Tropical) and planetary subsets.

#### 3. Sparse Autoencoder (SAE) Representation Layer
- **Description**: PyTorch neural network that regularizes and compresses planetary features into sparse activations.
- **Input Parameters**:
  - `input_dim`: Input feature size (e.g., 36).
  - `bottleneck_dim`: Dimension of latent representation (e.g., 16).
  - `sparsity_weight` (L1 penalty), `weight_decay` (L2 penalty).
- **Expected Output Behavior**: Outputs sparse tensors of shape `(Batch_size, bottleneck_dim)` with target sparsity activation > 50%.
- **Tier 1 (Happy Path)**: Runs forward pass, verifies output shape, confirms reconstruction loss, and checks weight decay application.
- **Tier 2 (Boundary)**: Massive/empty inputs, zero weight gradients, extreme sparsity penalties causing dead neurons, and scaling behavior with batch size of 1.
- **Tier 3 (Combinatorial)**: Combinations of bottleneck dimensions (8, 16, 32) and L1 weight penalties (0.0, 1e-4, 1e-3).

#### 4. Deep MLP Prediction Head
- **Description**: Neural network head that predicts next-day return direction (Long/Short/Hold) or volatility clusters from fused features.
- **Input Parameters**:
  - `input_dim`: Size of combined inputs.
  - `hidden_dims`: List of layer sizes (e.g., `[64, 32]`).
  - `dropout`: Dropout rate (e.g., 0.3).
- **Expected Output Behavior**: Outputs logits of shape `(Batch_size, 3)` summing to 1.0 via Softmax.
- **Tier 1 (Happy Path)**: Generates 3-class predictions, runs backward pass, computes cross-entropy loss, and updates weights.
- **Tier 2 (Boundary)**: Extreme logit outputs, checks that dropout is deactivated in `eval()` mode, and handles singular target inputs.
- **Tier 3 (Combinatorial)**: Combinations of hidden layer configurations (e.g., `[64]`, `[128, 64]`) with varying dropout (0.1, 0.3, 0.5) and learning rates.

#### 5. Purged & Embargoed Walk-Forward CV
- **Description**: Strict time-series validation splitter to prevent lookahead data leakage.
- **Input Parameters**:
  - `n_splits`: Number of sliding folds.
  - `purge_window`: Number of overlapping days to delete.
  - `embargo_pct`: Embargo fraction.
- **Expected Output Behavior**: Yields `(train_indices, val_indices)` iterators where `max(train_indices) < min(val_indices)` and gap >= `purge_window + embargo_days`.
- **Tier 1 (Happy Path)**: Generates splits, verifies split bounds, and confirms training windows expand sequentially.
- **Tier 2 (Boundary)**: Insufficient sample size (dataset smaller than purge + embargo), zero splits requested, and boundary index overlaps.
- **Tier 3 (Combinatorial)**: Varies splits (3, 5, 10) against embargo sizes (0.01, 0.05, 0.10) to verify strict boundaries are maintained.

#### 6. Unified Evaluation & Baseline Benchmark Suite
- **Description**: Calculates portfolio returns and compares performance against Buy-and-Hold and Monte Carlo baselines.
- **Input Parameters**:
  - `strategy_returns`: Array of strategy returns.
  - `market_returns`: Array of Buy-and-Hold returns.
  - `mc_paths`: Number of Monte Carlo simulations (1000).
- **Expected Output Behavior**: Computes CAGR, Max Drawdown, Sharpe ratio, Monte Carlo p-value, and generates `evaluation_report.json`.
- **Tier 1 (Happy Path)**: Computes metrics, compares against Buy-and-Hold, verifies Monte Carlo p-value calculations, and writes the JSON schema.
- **Tier 2 (Boundary)**: Constant zero returns, empty series, extreme losses (-100%), and cases where p-value is exactly 1.0 or 0.0.
- **Tier 3 (Combinatorial)**: Validates baseline calculations across SPY, QQQ, and DIA under different historical periods and Monte Carlo simulation paths (100 to 1000).

## Test Architecture
- **Test Runner**: Pytest-based framework. Invocation: `pytest -p no:seleniumbase tests/`.
- **Pass/Fail Semantics**: Exit code 0 on all tests passing.
- **Directory Layout**:
  - `tests/test_e2e_pipeline.py`: Comprehensive test suite implementing Tiers 1-4.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Bull Market Regime (SPY) | Data Ingestion, Ephemeris, SAE, MLP, CV, Evaluation | Medium |
| 2 | Bear Market Regime (QQQ) | Data Ingestion, Ephemeris, SAE, MLP, CV, Evaluation | Medium |
| 3 | Extreme Volatility Event (DIA) | Data Ingestion, Ephemeris, SAE, MLP, CV, Evaluation | High |
| 4 | Varying Frequencies & Horizons | Data Ingestion, Ephemeris, SAE, MLP, CV, Evaluation | High |
| 5 | Varying Training Window Configurations | Data Ingestion, Ephemeris, SAE, MLP, CV, Evaluation | High |

### Detailed Tier 4 Workload Specs

1. **Bull Market Regime (SPY 2012-2015)**
   - *Inputs*: SPY daily data and ephemeris features from 2012-01-01 to 2015-12-31.
   - *Expected Output*: Processes daily alignment, runs PyTorch training, performs purged walk-forward CV, and validates that metrics (CAGR, Sharpe, Max Drawdown) compared to Buy-and-Hold baseline are correctly exported to `evaluation_report.json`.

2. **Bear Market Regime (QQQ 2008-2009)**
   - *Inputs*: QQQ daily data and ephemeris features from 2008-01-01 to 2009-12-31.
   - *Expected Output*: Runs model training and CV through high-volatility regimes, verifying the model handles downside drawdowns without numeric instability.

3. **Extreme Volatility Event (DIA 2020 COVID Crash)**
   - *Inputs*: DIA daily data and ephemeris features from 2019-06-01 to 2020-06-01.
   - *Expected Output*: Verifies that the embargo windows correctly segment the high-volatility crash period to ensure zero training leakage.

4. **Varying Frequencies & Horizons (Multi-Decade Ingestion)**
   - *Inputs*: SPY, QQQ, and DIA from 2006-01-01 to 2026-01-01.
   - *Expected Output*: Evaluates pipeline stability and memory scaling over ~5000 trading days, ensuring successful E2E execution and report writing.

5. **Out-of-Sample Failure Mode & Baseline Verification**
   - *Inputs*: Shuffled target labels with no real correlation.
   - *Expected Output*: The evaluation suite runs correctly, produces a high Monte Carlo p-value (e.g. > 0.05), and successfully writes `"beats_random": false` to the report.

## Coverage Thresholds
- Tier 1: ≥5 tests per feature (achieved: 30 tests total)
- Tier 2: ≥5 tests per feature (achieved: 30 tests total)
- Tier 3: Pairwise coverage of major feature interactions (achieved: 6 tests total)
- Tier 4: ≥5 realistic application scenarios (achieved: 5 tests total)
