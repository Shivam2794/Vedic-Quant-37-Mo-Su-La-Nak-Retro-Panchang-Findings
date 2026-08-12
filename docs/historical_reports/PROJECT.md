# Project: Vedic Quant Neural Network Pipeline

## Architecture
- **Data Layer**: Standardized downloading of ETF daily market data (SPY, QQQ, DIA) from `market_data/` and alignment with continuous Z-Axis Vedic astrological features from Swiss Ephemeris and `UltimateVedicEngine`.
- **Model Layer**: PyTorch model combining a Sparse Autoencoder (SAE) representation layer and a Deep Multi-Layer Perceptron (MLP) classification/regression head, regularized via dropout, weight decay, and early stopping.
- **Validation Layer**: Strict Purged and Embargoed Walk-Forward Cross Validation (Expanding training window, purging overlapping labels, embargoing validation horizon) to guarantee zero time-series data leakage.
- **Evaluation Layer**: Metrics calculation (CAGR, Max Drawdown, Sharpe Ratio) compared against a Buy and Hold baseline and a Monte Carlo randomized predictor baseline (N=1000 paths) producing a statistical p-value.
- **Output Layer**: Save final outputs including the trained model, feature weights, and a structured `evaluation_report.json` and `evaluation_report.md`.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Exploration | Analyze datasets and target assets | None | DONE |
| M2 | Test Infra Setup | Create E2E test cases (Tiers 1-4) and `TEST_READY.md` | M1 | PLANNED |
| M3 | Model & Data Pipeline | Implement data downloading/alignment, PyTorch SAE+MLP models | M1 | PLANNED |
| M4 | Validation & Training | Implement Purged/Embargoed Walk-Forward CV & baseline comparison | M3 | PLANNED |
| M5 | E2E Integration | Run pipeline, select best asset, pass E2E tests | M2, M4 | PLANNED |
| M6 | Forensic Audit | Perform integrity forensics and verify no violations | M5 | PLANNED |

## Interface Contracts
- **CLI Entry Point**: `python src/main.py` runs the entire pipeline end-to-end (training and evaluating SPY, QQQ, and DIA), selects the best asset, and generates the outputs.
- **Output Report Path**: The pipeline must write `evaluation_report.json` to the project root.
- **Report Schema**:
  ```json
  {
    "best_asset": "SPY",
    "assets": {
      "SPY": {
        "cagr": 0.125,
        "max_drawdown": -0.182,
        "sharpe_ratio": 1.15,
        "bh_sharpe_ratio": 0.75,
        "random_p_value": 0.032,
        "beats_bh": true,
        "beats_random": true
      },
      "QQQ": { ... },
      "DIA": { ... }
    }
  }
  ```
- **Code Layout**:
  - `src/data/` - data processing (e.g. yfinance downloading, ephemeris feature compiler, alignment)
  - `src/models/` - PyTorch MLP and Sparse Autoencoder (SAE)
  - `src/validation/` - Walk-Forward CV (Purged & Embargoed)
  - `src/evaluation/` - metric calculations (CAGR, Max Drawdown, Sharpe, baselines)
  - `src/main.py` - main execution pipeline
  - `tests/` - unit and integration tests
