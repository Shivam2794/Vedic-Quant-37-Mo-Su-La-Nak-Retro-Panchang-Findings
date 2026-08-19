# Project: Frontier 3 Institutional Quant Backtester & Strategy Simulator

## Architecture
- Module Boundaries:
  - `src/backtest/performance_metrics.py`: Mathematical calculations for hedge-fund grade risk/return metrics (Sharpe, Sortino, Calmar, MDD, PSR, Monte Carlo resampling).
  - `src/backtest/backtest_engine.py`: Event-driven execution engine with Next-Bar Open filling, IBKR commission/slippage friction, Ashtakavarga dynamic position sizing, and macro volatility regime breakdown.
  - `tests/test_frontier_3_backtester.py`: Comprehensive test suite verifying backtester mechanics, risk formulas, boundary conditions, and accounting.
  - `reports/frontier_3_institutional_backtest_ledger.md`: Generated institutional ledger report.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | Sortino Ratio LPM2 Math | Implement standard Lower Partial Moment 2 (LPM2) dividing squared downside deviations by total N | M1 | Survey Explorer 1 |
| 2 | PSR Asymptotic Scaling | Fix Probabilistic Sharpe Ratio scaling using per-period sample Sharpe | M1 | Survey Explorer 1 |
| 3 | Trade Expectancy Calculation | Fix scratch/breakeven trade penalty in expectancy math | M1 | Survey Explorer 1 |
| 4 | Metric & MC Schema Uniformity | Guarantee identical dictionary keys across all early exit and full execution paths | M1 | Survey Explorer 1 |
| 5 | Isolated RNG in Monte Carlo | Replace global `np.random.seed` with isolated `np.random.default_rng` | M1 | Survey Explorer 1 |
| 6 | Boundary & Zero-Equity Safeguards | Add robust guards for zero/negative equity, constant series, and sub-year CAGR | M1 | Survey Explorer 1 |
| 7 | Macro Regime 2021 Gap Fix | Reconcile 2021 regime partition in backtest engine so all 197 trades are allocated | M2 | Survey Explorers 2 & 3 |
| 8 | Friction & Sizing Verification | Verify Next-Bar Open, IBKR $0.005/sh ($1 min), $0.01/sh slippage, SAV 0.75-1.25x sizing, 25% cap | M2 | Survey Explorer 2 |
| 9 | Comprehensive Unit Tests Expansion | Expand `tests/test_frontier_3_backtester.py` with 10+ new boundary/statistical unit tests | M3 | Survey Explorer 3 |
| 10 | Full Pytest Suite Validation | Execute full 638+ test suite and ensure 100% pass with 0 failures and 0 warnings | M3 | Survey Explorer 3 |
| 11 | Backtester Ledger Regeneration | Execute backtest engine and regenerate institutional ledger matching exact trade manifests | M3 | Survey Explorer 3 |
| 12 | Git Publication | Commit and push all verified changes cleanly to GitHub | M4 | User Request R3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Performance Metrics Refinement | Fix Sortino LPM2, PSR scaling, expectancy, schema uniformity, isolated RNG, boundary guards in `src/backtest/performance_metrics.py` | none | DONE |
| M2 | Backtest Engine Regime & Accounting | Fix 2021 regime partition, verify friction, SAV sizing, and ledger output in `src/backtest/backtest_engine.py` | M1 | DONE |
| M3 | Comprehensive Test Suite & Ledger Verification | Expand unit tests in `tests/test_frontier_3_backtester.py`, run full 684 pytest suite, regenerate ledger | M1, M2 | DONE |
| M4 | Forensic Audit, Verification & Git Publication | Multi-agent review, adversarial challenge, forensic integrity audit, git commit & push | M1, M2, M3 | IN_PROGRESS (Git Publication Pending) |

## Interface Contracts
### `calculate_comprehensive_metrics(equity_curve, trade_returns, annualization_factor=252, rf=0.0)`
- Inputs: `equity_curve` (pd.Series or array-like), `trade_returns` (list or pd.Series of float returns per trade), `annualization_factor` (float, default 252), `rf` (float, default 0.0).
- Output: `dict` with uniform keys: `Total_Return_Pct`, `CAGR_Pct`, `Sharpe_Ratio`, `Sortino_Ratio`, `Calmar_Ratio`, `Max_Drawdown_Pct`, `Max_Drawdown_Duration_Periods`, `Max_Drawdown_Duration_Bars`, `Win_Rate_Pct`, `Profit_Factor`, `Total_Trades`, `Win_Trades`, `Loss_Trades`, `Avg_Win_Pct`, `Avg_Loss_Pct`, `Expectancy_Pct`, `Probabilistic_Sharpe_Ratio`, `Skewness`, `Kurtosis`.

### `run_monte_carlo_resampling(trade_returns, n_simulations=1000, seed=42)`
- Inputs: `trade_returns` (list or array-like), `n_simulations` (int), `seed` (int).
- Output: `dict` with keys: `MC_5th_Percentile_Return_Pct`, `MC_Median_Return_Pct`, `MC_95th_Percentile_Return_Pct`, `MC_5th_Percentile_MDD_Pct`, `MC_Median_MDD_Pct`, `MC_95th_Percentile_MDD_Pct`.

## Code Layout
- `src/backtest/performance_metrics.py` (and mirror `frontier_3_backtester/src/performance_metrics.py`)
- `src/backtest/backtest_engine.py` (and mirror `frontier_3_backtester/src/backtest_engine.py`)
- `tests/test_frontier_3_backtester.py`
- `tests/test_adversarial_metrics_stress.py`
- `tests/test_adversarial_frontier3_challenger2.py`
- `reports/frontier_3_institutional_backtest_ledger.md`
- `data/backtest_trades_manifest.parquet`
