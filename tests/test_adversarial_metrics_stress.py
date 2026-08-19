"""
ADVERSARIAL METRICS STRESS TEST SUITE
=====================================
Rigorous property-based, edge-case, and mathematical invariance tests for:
- calculate_drawdowns
- calculate_comprehensive_metrics
- run_monte_carlo_resampling
"""

import math
import numpy as np
import pandas as pd
import pytest
from scipy.stats import t as student_t, cauchy

from src.backtest.performance_metrics import (
    calculate_drawdowns,
    calculate_comprehensive_metrics,
    run_monte_carlo_resampling,
)

EXPECTED_METRIC_KEYS = {
    "Total_Return_Pct",
    "CAGR_Pct",
    "Sharpe_Ratio",
    "Sortino_Ratio",
    "Calmar_Ratio",
    "Max_Drawdown_Pct",
    "Max_Drawdown_Duration_Bars",
    "Max_Drawdown_Duration_Periods",
    "Total_Trades",
    "Win_Trades",
    "Loss_Trades",
    "Win_Rate_Pct",
    "Profit_Factor",
    "Payoff_Ratio",
    "Expectancy_Pct",
    "Avg_Win_Pct",
    "Avg_Loss_Pct",
    "Probabilistic_Sharpe_Ratio",
    "Skewness",
    "Kurtosis",
}

EXPECTED_MC_KEYS = {
    "MC_5th_Percentile_Return_Pct",
    "MC_Median_Return_Pct",
    "MC_95th_Percentile_Return_Pct",
    "MC_5th_Percentile_MDD_Pct",
    "MC_Median_MDD_Pct",
    "MC_95th_Percentile_MDD_Pct",
}


def assert_metrics_valid_and_finite(metrics: dict):
    """Verifies that all metric dictionary values are finite numbers and keys match schema."""
    assert set(metrics.keys()) == EXPECTED_METRIC_KEYS, f"Schema mismatch: {set(metrics.keys()) ^ EXPECTED_METRIC_KEYS}"
    for k, v in metrics.items():
        assert v is not None, f"Key {k} is None"
        if isinstance(v, (float, np.floating)):
            assert not math.isnan(v), f"Key {k} is NaN"
            assert not math.isinf(v), f"Key {k} is Inf ({v})"
        elif isinstance(v, (int, np.integer)):
            assert True
        else:
            pytest.fail(f"Key {k} has unexpected type: {type(v)} with value {v}")

    # Domain invariants
    assert 0.0 <= metrics["Probabilistic_Sharpe_Ratio"] <= 1.0, f"PSR out of bounds: {metrics['Probabilistic_Sharpe_Ratio']}"
    assert 0.0 <= metrics["Win_Rate_Pct"] <= 100.0, f"Win rate out of bounds: {metrics['Win_Rate_Pct']}"
    assert metrics["Max_Drawdown_Pct"] <= 0.0001, f"MDD must be non-positive: {metrics['Max_Drawdown_Pct']}"
    assert metrics["Max_Drawdown_Duration_Periods"] >= 0, f"Duration must be >= 0: {metrics['Max_Drawdown_Duration_Periods']}"
    assert metrics["Total_Trades"] >= (metrics["Win_Trades"] + metrics["Loss_Trades"]), "Total trades < wins + losses"


def assert_mc_valid_and_finite(mc: dict):
    """Verifies that Monte Carlo outputs are finite numbers and properly ordered."""
    assert set(mc.keys()) == EXPECTED_MC_KEYS, f"MC Schema mismatch: {set(mc.keys()) ^ EXPECTED_MC_KEYS}"
    for k, v in mc.items():
        assert v is not None, f"MC Key {k} is None"
        if isinstance(v, (float, np.floating)):
            assert not math.isnan(v), f"MC Key {k} is NaN"
            assert not math.isinf(v), f"MC Key {k} is Inf ({v})"
        elif isinstance(v, (int, np.integer)):
            assert True
        else:
            pytest.fail(f"MC Key {k} has unexpected type: {type(v)}")

    assert mc["MC_5th_Percentile_Return_Pct"] <= mc["MC_Median_Return_Pct"] + 1e-6
    assert mc["MC_Median_Return_Pct"] <= mc["MC_95th_Percentile_Return_Pct"] + 1e-6
    assert mc["MC_5th_Percentile_MDD_Pct"] <= mc["MC_Median_MDD_Pct"] + 1e-6
    assert mc["MC_Median_MDD_Pct"] <= mc["MC_95th_Percentile_MDD_Pct"] + 1e-6


class TestAdversarialMetricsStress:
    """Adversarial stress testing for performance metrics."""

    # =========================================================================
    # 1. Zero-variance equity curves (flat equity)
    # =========================================================================
    @pytest.mark.parametrize("equity_val", [100000.0, 1.0, 1e-5, 1e8])
    def test_zero_variance_flat_equity(self, equity_val):
        equity = pd.Series([equity_val] * 100)
        trade_rets = [0.0] * 50
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

        assert metrics["Total_Return_Pct"] == 0.0
        assert metrics["CAGR_Pct"] == 0.0
        assert metrics["Sharpe_Ratio"] == 0.0
        assert metrics["Sortino_Ratio"] == 0.0
        assert metrics["Calmar_Ratio"] == 0.0
        assert metrics["Max_Drawdown_Pct"] == 0.0
        assert metrics["Max_Drawdown_Duration_Periods"] == 0

        dd_series, mdd, mdd_dur = calculate_drawdowns(equity)
        assert mdd == 0.0
        assert mdd_dur == 0
        assert (dd_series == 0.0).all()

    # =========================================================================
    # 2. Monotonically increasing equity (zero losses)
    # =========================================================================
    def test_monotonically_increasing_linear(self):
        equity = pd.Series(np.linspace(100.0, 200.0, 252))
        trade_rets = [0.01] * 50
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

        assert metrics["Total_Return_Pct"] == 100.0
        assert metrics["Max_Drawdown_Pct"] == 0.0
        assert metrics["Max_Drawdown_Duration_Periods"] == 0
        assert metrics["Win_Rate_Pct"] == 100.0
        assert metrics["Win_Trades"] == 50
        assert metrics["Loss_Trades"] == 0
        assert metrics["Sharpe_Ratio"] > 0
        assert metrics["Sortino_Ratio"] > 0

    def test_monotonically_increasing_exponential(self):
        equity = pd.Series(np.geomspace(100.0, 10000.0, 500))
        trade_rets = [0.05] * 100
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

        assert metrics["Total_Return_Pct"] == 9900.0
        assert metrics["Max_Drawdown_Pct"] == 0.0
        assert metrics["Win_Rate_Pct"] == 100.0
        assert metrics["Sharpe_Ratio"] > 0

    # =========================================================================
    # 3. Monotonically decreasing equity (100% losses)
    # =========================================================================
    def test_monotonically_decreasing_to_zero(self):
        equity = pd.Series([100.0, 80.0, 60.0, 40.0, 20.0, 0.0])
        trade_rets = [-0.20, -0.25, -0.33, -0.50, -1.00]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

        assert metrics["Total_Return_Pct"] == -100.0
        assert metrics["CAGR_Pct"] == -100.0
        assert metrics["Max_Drawdown_Pct"] == -100.0
        assert metrics["Win_Rate_Pct"] == 0.0
        assert metrics["Win_Trades"] == 0
        assert metrics["Loss_Trades"] == 5

    def test_monotonically_decreasing_near_zero(self):
        equity = pd.Series([100.0, 10.0, 1.0, 0.1, 0.01, 0.001])
        trade_rets = [-0.90, -0.90, -0.90, -0.90, -0.90]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

        assert metrics["Total_Return_Pct"] == -100.0
        assert metrics["Max_Drawdown_Pct"] == -100.0

    # =========================================================================
    # 4. Alternating +/- extreme spikes (+1000%, -99%)
    # =========================================================================
    def test_extreme_alternating_spikes(self):
        # Spikes: 100 -> 1100 (+1000%) -> 11 (-99%) -> 121 (+1000%) -> 1.21 (-99%)
        equity = pd.Series([100.0, 1100.0, 11.0, 121.0, 1.21, 13.31])
        trade_rets = [10.0, -0.99, 10.0, -0.99, 10.0]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

        assert metrics["Total_Trades"] == 5
        assert metrics["Win_Trades"] == 3
        assert metrics["Loss_Trades"] == 2

    def test_hyper_explosive_spikes(self):
        equity = pd.Series([100.0, 1e7, 10.0, 1e8, 1.0, 1e9])
        trade_rets = [99999.0, -0.999999, 9999999.0, -0.9999999, 999999999.0]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert_metrics_valid_and_finite(metrics)

    # =========================================================================
    # 5. Heavy fat-tail distributions (Student-t, Cauchy-like kurtosis)
    # =========================================================================
    def test_cauchy_and_heavy_tail_distribution(self):
        rng = np.random.default_rng(12345)
        # Generate heavy tailed returns using Student-t df=2
        raw_rets = rng.standard_t(df=2, size=1000) * 0.02
        # Bound returns so 1 + r > 0 to maintain positive equity
        bounded_rets = np.clip(raw_rets, -0.80, 5.0)
        eq = 100000.0 * np.cumprod(1.0 + np.insert(bounded_rets, 0, 0.0))
        equity = pd.Series(eq)

        metrics = calculate_comprehensive_metrics(equity, bounded_rets.tolist())
        assert_metrics_valid_and_finite(metrics)
        assert metrics["Kurtosis"] > 3.0 or metrics["Kurtosis"] >= 1.0

    def test_extreme_skewness_and_kurtosis(self):
        # 99 zero returns and 1 massive outlier +1000%
        rets = [0.0] * 99 + [10.0]
        eq = 100000.0 * np.cumprod(1.0 + np.insert(np.array(rets), 0, 0.0))
        equity = pd.Series(eq)

        metrics = calculate_comprehensive_metrics(equity, rets)
        assert_metrics_valid_and_finite(metrics)
        assert metrics["Skewness"] > 0

        # 99 zero returns and 1 massive loss -90%
        rets_neg = [0.0] * 99 + [-0.90]
        eq_neg = 100000.0 * np.cumprod(1.0 + np.insert(np.array(rets_neg), 0, 0.0))
        equity_neg = pd.Series(eq_neg)
        metrics_neg = calculate_comprehensive_metrics(equity_neg, rets_neg)
        assert_metrics_valid_and_finite(metrics_neg)
        assert metrics_neg["Skewness"] < 0

    # =========================================================================
    # 6. Single-element, 2-element, empty series, and NaN/Inf series
    # =========================================================================
    def test_empty_series_and_returns(self):
        m1 = calculate_comprehensive_metrics(pd.Series([], dtype=float), [])
        assert_metrics_valid_and_finite(m1)

        m2 = calculate_comprehensive_metrics(pd.Series([100.0]), [])
        assert_metrics_valid_and_finite(m2)

        m3 = calculate_comprehensive_metrics(pd.Series([]), [0.05, -0.02])
        assert_metrics_valid_and_finite(m3)

        dd, mdd, dur = calculate_drawdowns(pd.Series([], dtype=float))
        assert len(dd) == 0
        assert mdd == 0.0
        assert dur == 0

    def test_single_element_series(self):
        m = calculate_comprehensive_metrics(pd.Series([100.0]), [0.05])
        assert_metrics_valid_and_finite(m)

        dd, mdd, dur = calculate_drawdowns(pd.Series([100.0]))
        assert len(dd) == 1
        assert mdd == 0.0
        assert dur == 0

    def test_two_element_series(self):
        m = calculate_comprehensive_metrics(pd.Series([100.0, 105.0]), [0.05])
        assert_metrics_valid_and_finite(m)
        assert m["Total_Return_Pct"] == 5.0

    # =========================================================================
    # 7. Zero and negative initial equity
    # =========================================================================
    def test_zero_initial_equity(self):
        m = calculate_comprehensive_metrics(pd.Series([0.0, 10.0, 20.0]), [0.05])
        assert_metrics_valid_and_finite(m)
        assert m["Total_Return_Pct"] == 0.0

    def test_negative_initial_equity(self):
        m = calculate_comprehensive_metrics(pd.Series([-100.0, -50.0, 10.0]), [0.05])
        assert_metrics_valid_and_finite(m)
        assert m["Total_Return_Pct"] == 0.0

    # =========================================================================
    # 8. Monte Carlo resampling stress scenarios
    # =========================================================================
    def test_monte_carlo_empty_and_small_returns(self):
        mc0 = run_monte_carlo_resampling([])
        assert_mc_valid_and_finite(mc0)
        assert mc0["MC_Median_Return_Pct"] == 0.0

        mc4 = run_monte_carlo_resampling([0.01, 0.02, -0.01, 0.03])
        assert_mc_valid_and_finite(mc4)
        assert mc4["MC_Median_Return_Pct"] == 0.0

    def test_monte_carlo_all_losses(self):
        mc_loss = run_monte_carlo_resampling([-0.05, -0.10, -0.02, -0.08, -0.04, -0.03])
        assert_mc_valid_and_finite(mc_loss)
        assert mc_loss["MC_Median_Return_Pct"] < 0.0
        assert mc_loss["MC_Median_MDD_Pct"] < 0.0

    def test_monte_carlo_all_wins(self):
        mc_win = run_monte_carlo_resampling([0.05, 0.10, 0.02, 0.08, 0.04, 0.03])
        assert_mc_valid_and_finite(mc_win)
        assert mc_win["MC_Median_Return_Pct"] > 0.0
        assert mc_win["MC_Median_MDD_Pct"] == 0.0

    def test_monte_carlo_total_wipeout_return(self):
        # Contains -1.0 (100% loss)
        mc_wipe = run_monte_carlo_resampling([0.05, -1.0, 0.02, 0.08, 0.04, 0.03], n_simulations=500)
        assert_mc_valid_and_finite(mc_wipe)
        assert mc_wipe["MC_5th_Percentile_Return_Pct"] == -100.0

    def test_monte_carlo_extreme_sample_size(self):
        rng = np.random.default_rng(999)
        large_rets = rng.normal(0.001, 0.02, size=5000).tolist()
        mc_large = run_monte_carlo_resampling(large_rets, n_simulations=200, seed=42)
        assert_mc_valid_and_finite(mc_large)

    # =========================================================================
    # 9. Property-Based Stress Generator (Fuzzing 500 Random Regimes)
    # =========================================================================
    def test_property_based_fuzzing_gauntlet(self):
        rng = np.random.default_rng(424242)
        for trial in range(500):
            n_bars = rng.integers(2, 300)
            initial_cap = float(rng.uniform(100.0, 1000000.0))
            
            # Generate random returns from various distributions
            dist_type = trial % 5
            if dist_type == 0:
                # Normal returns
                step_rets = rng.normal(0.0005, 0.02, size=n_bars - 1)
            elif dist_type == 1:
                # Heavy tailed Student-t
                step_rets = rng.standard_t(df=2.5, size=n_bars - 1) * 0.015
            elif dist_type == 2:
                # Asymmetric skewed
                step_rets = rng.exponential(0.02, size=n_bars - 1) - 0.015
            elif dist_type == 3:
                # High volatility extreme
                step_rets = rng.uniform(-0.5, 1.5, size=n_bars - 1)
            else:
                # Flat or near-flat
                step_rets = np.zeros(n_bars - 1)

            step_rets = np.clip(step_rets, -0.999, 10.0)
            eq_curve = initial_cap * np.cumprod(1.0 + np.insert(step_rets, 0, 0.0))
            equity_series = pd.Series(eq_curve)

            n_trades = rng.integers(1, 50)
            trade_rets = rng.choice(step_rets, size=n_trades).tolist()

            ann_factor = float(rng.choice([12.0, 52.0, 252.0, 365.0]))
            rf = float(rng.uniform(0.0, 0.10))

            metrics = calculate_comprehensive_metrics(
                equity_series, trade_rets, annualization_factor=ann_factor, risk_free_rate=rf
            )
            assert_metrics_valid_and_finite(metrics)

            if len(trade_rets) >= 5:
                mc = run_monte_carlo_resampling(trade_rets, n_simulations=100, seed=trial)
                assert_mc_valid_and_finite(mc)
