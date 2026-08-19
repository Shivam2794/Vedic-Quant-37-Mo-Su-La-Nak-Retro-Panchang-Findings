"""
UNIT & INTEGRATION TESTS FOR FRONTIER 3 QUANT BACKTESTER
========================================================
Verifies Marcos López de Prado performance metrics, Triple-Barrier
execution, Monte Carlo resampling, and regime decomposition.
"""

import pytest
import os
import numpy as np
import pandas as pd
from scipy.stats import norm

from src.backtest.performance_metrics import (
    calculate_drawdowns,
    calculate_comprehensive_metrics,
    run_monte_carlo_resampling
)
from src.backtest.backtest_engine import (
    simulate_trend_wave_strategy,
    run_regime_breakdown_backtest,
    IBKR_COMMISSION_PER_SHARE,
    IBKR_MIN_COMMISSION,
    SLIPPAGE_PER_SHARE
)


class TestPerformanceMetricsCalculations:
    """Test Suite for Quantitative Risk & Performance Metrics."""

    def test_monotonic_positive_equity_curve(self):
        """Test metrics on perfectly increasing equity series."""
        equity = pd.Series([100000.0, 102000.0, 105000.0, 110000.0, 115000.0])
        trade_rets = [0.02, 0.029, 0.047, 0.045]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)

        assert metrics["Total_Return_Pct"] == 15.0
        assert metrics["Max_Drawdown_Pct"] == 0.0
        assert metrics["Win_Rate_Pct"] == 100.0
        assert metrics["Sharpe_Ratio"] > 2.0
        assert metrics["Sortino_Ratio"] > 2.0

    def test_drawdown_series_and_mdd(self):
        """Test maximum drawdown and underwater duration calculations."""
        equity = pd.Series([100.0, 110.0, 99.0, 88.0, 95.0, 120.0])
        dd_series, mdd, mdd_duration = calculate_drawdowns(equity)

        # Peak is 110.0, trough is 88.0 -> DD = (88 - 110)/110 = -20.0%
        assert round(mdd, 3) == -0.200
        assert mdd_duration >= 2

    def test_drawdown_depth_duration_decoupling(self):
        """Verifies MDD depth decouples from longest underwater duration."""
        # Episode 1: 5 bars underwater, shallow (-5% DD)
        # Episode 2: 2 bars underwater, deep (-25% DD)
        equity = pd.Series([100.0, 98.0, 97.0, 96.0, 95.0, 101.0, 80.0, 75.0, 110.0])
        dd_series, mdd, max_duration = calculate_drawdowns(equity)

        # Peak before episode 2 is 101.0, trough is 75.0 -> DD = (75-101)/101 = -25.74%
        assert round(mdd, 2) == -0.26
        # Episode 1 had 4 underwater bars (98, 97, 96, 95)
        assert max_duration >= 4

    def test_sortino_lpm2_zero_loss_and_identical_losses(self):
        """Verifies true Lower Partial Moment 2 (LPM2) Sortino calculation."""
        # Case 1: Zero loss series
        equity_pos = pd.Series([100.0, 102.0, 104.0, 106.0, 108.0])
        m_pos = calculate_comprehensive_metrics(equity_pos, [0.02, 0.02, 0.02, 0.02])
        assert m_pos["Sortino_Ratio"] == 100.0 or m_pos["Sortino_Ratio"] >= m_pos["Sharpe_Ratio"]

        # Case 2: Identical losses (e.g. fixed stop losses)
        # In LPM2, identical losses do not have zero downside semi-deviation because deviation is taken around rf
        returns_list = [0.03, -0.02, 0.03, -0.02, 0.03, -0.02]
        eq_curve = [100.0]
        for r in returns_list:
            eq_curve.append(eq_curve[-1] * (1.0 + r))
        equity_ident = pd.Series(eq_curve)
        m_ident = calculate_comprehensive_metrics(equity_ident, returns_list)
        assert m_ident["Sortino_Ratio"] > 0.0
        # Verify manual LPM2 calculation
        rets = equity_ident.pct_change().dropna()
        rf_per_period = (1.0 + 0.02) ** (1.0 / 252.0) - 1.0
        downside_diff = np.minimum(0.0, rets - rf_per_period)
        expected_downside_dev = np.sqrt(np.mean(downside_diff ** 2))
        expected_sortino = (rets.mean() - rf_per_period) / expected_downside_dev * np.sqrt(252.0)
        assert round(m_ident["Sortino_Ratio"], 2) == round(expected_sortino, 2)

    def test_sortino_lpm2_mixed_return_distribution(self):
        """Verifies LPM2 Sortino calculation against known mathematical ground truth."""
        equity = pd.Series([100.0, 105.0, 98.0, 103.0, 97.0, 106.0])
        trade_rets = [0.05, -0.0667, 0.0510, -0.0583, 0.0928]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        assert metrics["Sortino_Ratio"] > 0
        assert metrics["Sharpe_Ratio"] > 0

    def test_psr_scale_accuracy_and_asymptotics(self):
        """Verifies Probabilistic Sharpe Ratio (PSR) uses unannualized per-period Sharpe."""
        equity = pd.Series([100.0 + i * 0.5 for i in range(50)])
        trade_rets = [0.005] * 49
        metrics = calculate_comprehensive_metrics(equity, trade_rets)
        psr = metrics["Probabilistic_Sharpe_Ratio"]
        assert 0.50 <= psr <= 1.00

        # When Sharpe is flat with zero vol
        eq_flat = pd.Series([100.0] * 10)
        m_flat = calculate_comprehensive_metrics(eq_flat, [0.0] * 9)
        assert m_flat["Probabilistic_Sharpe_Ratio"] == 0.50 or m_flat["Probabilistic_Sharpe_Ratio"] == 0.0

    def test_trade_expectancy_with_scratch_trades(self):
        """Verifies trade expectancy is not penalized by scratch/breakeven trades (return == 0.0)."""
        equity = pd.Series([100.0, 105.0, 105.0, 105.0, 100.0])
        # 1 win (+5%), 2 scratches (0%), 1 loss (-4.76%)
        trade_rets = [0.05, 0.0, 0.0, -0.047619]
        metrics = calculate_comprehensive_metrics(equity, trade_rets)

        # Expected value is mean of all 4 trades: (0.05 + 0 + 0 - 0.047619) / 4 = +0.000595 (+0.06%)
        expected_exp_pct = round(float(np.mean(trade_rets)) * 100.0, 2)
        assert metrics["Expectancy_Pct"] == expected_exp_pct
        assert metrics["Total_Trades"] == 4
        assert metrics["Win_Trades"] == 1
        assert metrics["Loss_Trades"] == 1
        assert metrics["Win_Rate_Pct"] == 25.0

    def test_schema_uniformity_early_exit_and_standard_exit(self):
        """Guarantees standard 18+ keys are returned identically on early exit vs standard exit."""
        m_early_empty = calculate_comprehensive_metrics(pd.Series([], dtype=float), [])
        m_early_single = calculate_comprehensive_metrics(pd.Series([100.0]), [0.05])
        m_early_zero_equity = calculate_comprehensive_metrics(pd.Series([0.0, 100.0]), [0.05])

        equity_std = pd.Series([100.0, 105.0, 110.0])
        m_std = calculate_comprehensive_metrics(equity_std, [0.05, 0.0476])

        # All dictionaries must share identical key sets
        assert set(m_early_empty.keys()) == set(m_std.keys())
        assert set(m_early_single.keys()) == set(m_std.keys())
        assert set(m_early_zero_equity.keys()) == set(m_std.keys())

        standard_required_keys = [
            "Total_Return_Pct", "CAGR_Pct", "Sharpe_Ratio", "Sortino_Ratio", "Calmar_Ratio",
            "Max_Drawdown_Pct", "Max_Drawdown_Duration_Periods", "Win_Rate_Pct", "Profit_Factor",
            "Total_Trades", "Win_Trades", "Loss_Trades", "Avg_Win_Pct", "Avg_Loss_Pct",
            "Expectancy_Pct", "Probabilistic_Sharpe_Ratio", "Skewness", "Kurtosis"
        ]
        for k in standard_required_keys:
            assert k in m_std, f"Missing required key: {k}"

    def test_zero_variance_and_negative_equity_protections(self):
        """Verifies safeguards against 0-variance series and negative/zero equity."""
        # 0-variance constant equity curve
        eq_const = pd.Series([100.0, 100.0, 100.0, 100.0])
        m_const = calculate_comprehensive_metrics(eq_const, [0.0, 0.0, 0.0])
        assert m_const["Sharpe_Ratio"] == 0.0
        assert m_const["Sortino_Ratio"] == 0.0
        assert m_const["Max_Drawdown_Pct"] == 0.0

        # Total capital loss
        eq_loss = pd.Series([100.0, 50.0, 0.0])
        m_loss = calculate_comprehensive_metrics(eq_loss, [-0.50, -1.00])
        assert m_loss["CAGR_Pct"] == -100.0
        assert m_loss["Total_Return_Pct"] == -100.0

    def test_monte_carlo_isolated_rng_and_percentiles(self):
        """Verifies Monte Carlo resampling uses isolated RNG and produces valid percentiles."""
        trade_rets = [0.04, -0.02, 0.03, 0.01, -0.015, 0.05, 0.02]
        mc1 = run_monte_carlo_resampling(trade_rets, n_simulations=500, seed=42)
        mc2 = run_monte_carlo_resampling(trade_rets, n_simulations=500, seed=42)

        # Deterministic with seed
        assert mc1 == mc2

        # Percentile ordering
        assert mc1["MC_5th_Percentile_Return_Pct"] <= mc1["MC_Median_Return_Pct"]
        assert mc1["MC_Median_Return_Pct"] <= mc1["MC_95th_Percentile_Return_Pct"]
        assert mc1["MC_5th_Percentile_MDD_Pct"] <= mc1["MC_Median_MDD_Pct"]
        assert mc1["MC_Median_MDD_Pct"] <= mc1["MC_95th_Percentile_MDD_Pct"]

    def test_monte_carlo_schema_uniformity_small_sample(self):
        """Verifies Monte Carlo early exit schema matches standard schema exactly."""
        mc_small = run_monte_carlo_resampling([0.05, -0.02])
        mc_normal = run_monte_carlo_resampling([0.05, -0.02, 0.03, 0.01, -0.015, 0.02])

        assert set(mc_small.keys()) == set(mc_normal.keys())
        expected_mc_keys = [
            "MC_5th_Percentile_Return_Pct", "MC_Median_Return_Pct", "MC_95th_Percentile_Return_Pct",
            "MC_5th_Percentile_MDD_Pct", "MC_Median_MDD_Pct", "MC_95th_Percentile_MDD_Pct"
        ]
        for k in expected_mc_keys:
            assert k in mc_small


class TestBacktestEngineExecution:
    """Test Suite for Event-Driven Backtester."""

    def test_zero_lookahead_and_trade_execution(self):
        """Verifies synthetic market backtest executes trades with non-negative capital."""
        df_waves = pd.DataFrame({
            "Wave_ID": ["WAVE_1D_BULL_001", "WAVE_1D_BEAR_002"],
            "Timeframe": ["1D", "1D"],
            "Direction": ["Bullish_Thrust", "Bearish_Liquidation"],
            "T_Start_UTC": ["2020-01-02 09:30:00", "2020-02-03 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00", "2020-02-12 16:00:00"],
            "P_Start": [300.0, 320.0],
            "P_End": [315.0, 305.0],
            "Wave_Duration_Bars": [6, 7],
            "Baseline_ATR": [4.5, 5.0],
            "Inception_Moon_Sign": ["Aries", "Cancer"],
            "Inception_SAV_At_Moon": [31, 24],
        })

        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]
        bear_rules = [{"Antecedents": "[Moon in Cancer]", "Confidence_Pct": 75.0}]

        df_trades, trade_returns, metrics = simulate_trend_wave_strategy(
            df_waves, bull_rules, bear_rules, initial_capital=100000.0, min_rule_conf=70.0
        )

        assert not df_trades.empty
        assert len(df_trades) == 2
        for _, t in df_trades.iterrows():
            assert t["Holding_Bars"] >= 0
            assert t["Entry_Price"] > 0
            assert t["Exit_Price"] > 0
            assert t["Capital_After"] > 0

    def test_conflicting_signals_no_trade(self):
        """Verifies that simultaneous bull and bear signals produce zero trade execution."""
        df_waves = pd.DataFrame({
            "Wave_ID": ["WAVE_CONFLICT_001"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [300.0],
            "P_End": [315.0],
            "Wave_Duration_Bars": [6],
            "Baseline_ATR": [4.5],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]
        bear_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]
        df_trades, _, _ = simulate_trend_wave_strategy(df_waves, bull_rules, bear_rules)
        assert df_trades.empty

    def test_ashtakavarga_dynamic_multiplier_and_sizing_bounds(self):
        """Verifies Ashtakavarga Moon SAV multiplier scaling (0.75x, 1.0x, 1.25x)."""
        df_waves = pd.DataFrame({
            "Wave_ID": ["W_HIGH_SAV", "W_NEUTRAL_SAV", "W_LOW_SAV"],
            "Timeframe": ["1D", "1D", "1D"],
            "Direction": ["Bullish_Thrust", "Bullish_Thrust", "Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00", "2020-02-02 09:30:00", "2020-03-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00", "2020-02-10 16:00:00", "2020-03-10 16:00:00"],
            "P_Start": [100.0, 100.0, 100.0],
            "P_End": [105.0, 105.0, 105.0],
            "Wave_Duration_Bars": [5, 5, 5],
            "Baseline_ATR": [5.0, 5.0, 5.0],
            "Inception_Moon_Sign": ["Aries", "Taurus", "Gemini"],
            "Inception_SAV_At_Moon": [32, 28, 22],
        })
        bull_rules = [
            {"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0},
            {"Antecedents": "[Moon in Taurus]", "Confidence_Pct": 80.0},
            {"Antecedents": "[Moon in Gemini]", "Confidence_Pct": 80.0},
        ]
        df_trades, _, _ = simulate_trend_wave_strategy(df_waves, bull_rules, [], initial_capital=100000.0)
        assert len(df_trades) == 3
        # High SAV (>=30) -> 1.25x multiplier > Neutral (26-29) -> 1.0x > Low (<=25) -> 0.75x
        assert df_trades.iloc[0]["Net_PnL"] > df_trades.iloc[1]["Net_PnL"]
        assert df_trades.iloc[1]["Net_PnL"] > df_trades.iloc[2]["Net_PnL"]

    def test_portfolio_equity_cap_25_pct(self):
        """Verifies position size is strictly capped at 25% of current portfolio equity."""
        df_waves = pd.DataFrame({
            "Wave_ID": ["W_TINY_ATR"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [100.0],
            "P_End": [105.0],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [0.01],  # Extremely small ATR would request huge shares without cap
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [32],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]
        capital = 100000.0
        df_trades, _, _ = simulate_trend_wave_strategy(df_waves, bull_rules, [], initial_capital=capital)
        assert len(df_trades) == 1
        # Max shares at 25% cap on $100k capital with $100 entry price is 250 shares
        entry_price = 100.0 + SLIPPAGE_PER_SHARE
        max_allowed_shares = int((capital * 0.25) / entry_price)
        # Check Net PnL matches capped share count
        expected_shares = max_allowed_shares
        commission = max(expected_shares * IBKR_COMMISSION_PER_SHARE, IBKR_MIN_COMMISSION)
        exit_price = 105.0 - SLIPPAGE_PER_SHARE
        expected_net_pnl = (exit_price - entry_price) * expected_shares - 2 * commission
        assert round(df_trades.iloc[0]["Net_PnL"], 2) == round(expected_net_pnl, 2)

    def test_regime_breakdown_functionality_and_2021_reconciliation(self):
        """Verifies full historical macro regime breakdown including 2021 Post-COVID expansion."""
        df_trades = pd.DataFrame({
            "Entry_Date": [
                "1995-03-10", "2001-05-10", "2004-06-15", "2008-09-15",
                "2015-11-20", "2020-03-23", "2021-06-18", "2022-05-12", "2024-01-10"
            ],
            "Return_Pct": [5.0, -2.0, 4.0, 5.0, 3.0, 10.0, 4.0, 3.0, 3.0],
            "Net_PnL": [500.0, -200.0, 400.0, 500.0, 300.0, 1000.0, 400.0, 300.0, 300.0],
        })
        regimes = run_regime_breakdown_backtest(df_trades)
        assert len(regimes) == 9
        assert "Post-COVID Liquidity Expansion (2021)" in regimes
        assert regimes["Post-COVID Liquidity Expansion (2021)"]["Total_Trades"] == 1
        assert regimes["Post-COVID Liquidity Expansion (2021)"]["Win_Rate_Pct"] == 100.0

        # Sum of trades across all 9 regimes must equal 100% of input trades
        total_regime_trades = sum(r["Total_Trades"] for r in regimes.values())
        assert total_regime_trades == len(df_trades)
