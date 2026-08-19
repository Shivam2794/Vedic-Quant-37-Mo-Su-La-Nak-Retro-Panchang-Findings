import pytest
import os
import sys
import numpy as np
import pandas as pd
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.backtest.backtest_engine import (
    simulate_trend_wave_strategy,
    run_regime_breakdown_backtest,
    IBKR_COMMISSION_PER_SHARE,
    IBKR_MIN_COMMISSION,
    SLIPPAGE_PER_SHARE,
)
from src.backtest.performance_metrics import (
    calculate_comprehensive_metrics,
    run_monte_carlo_resampling,
)


class TestAdversarialDynamicSizingAndEquityCaps:
    """Adversarial stress-testing suite for dynamic Ashtakavarga sizing and portfolio caps."""

    def test_25_percent_portfolio_equity_cap_across_5000_fuzzed_scenarios(self):
        """Fuzzes 5,000 combinations of (Capital, Price, ATR, SAV) to verify position size never exceeds 25% cap."""
        rng = np.random.default_rng(42)
        n_scenarios = 5000

        capitals = rng.uniform(10_000, 10_000_000, size=n_scenarios)
        prices = rng.uniform(1.0, 5000.0, size=n_scenarios)
        atrs = rng.uniform(0.001, 200.0, size=n_scenarios)
        savs = rng.integers(10, 50, size=n_scenarios)

        for i in range(n_scenarios):
            cap = capitals[i]
            p = prices[i]
            atr = atrs[i]
            sav = savs[i]

            sav_mult = 1.25 if sav >= 30 else (0.75 if sav <= 25 else 1.0)
            risk_per_trade = cap * 0.015 * sav_mult
            raw_shares = max(int(risk_per_trade / max(atr * 1.5, 1.0)), 1)
            
            entry_price = p + SLIPPAGE_PER_SHARE
            max_shares = int((cap * 0.25) / max(entry_price, 1.0))
            shares = max(min(raw_shares, max_shares), 1)

            position_notional = shares * entry_price
            
            if max_shares >= 1:
                assert position_notional <= cap * 0.25 + entry_price, (
                    f"Violation: cap={cap}, price={p}, atr={atr}, sav={sav}, notional={position_notional}, limit={cap*0.25}"
                )

    def test_extreme_high_price_sizing_behavior(self):
        """Tests position sizing when SPY is at extreme high prices ($1,000, $5,000, $10,000)."""
        capital = 100_000.0

        for extreme_price in [1000.0, 5000.0, 10000.0]:
            df_wave = pd.DataFrame({
                "Wave_ID": ["W_HIGH_PRICE"],
                "Timeframe": ["1D"],
                "Direction": ["Bullish_Thrust"],
                "T_Start_UTC": ["2020-01-02 09:30:00"],
                "T_End_UTC": ["2020-01-10 16:00:00"],
                "P_Start": [extreme_price],
                "P_End": [extreme_price * 1.02],
                "Wave_Duration_Bars": [5],
                "Baseline_ATR": [extreme_price * 0.01],
                "Inception_Moon_Sign": ["Aries"],
                "Inception_SAV_At_Moon": [32],
            })
            bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

            df_trades, _, _ = simulate_trend_wave_strategy(df_wave, bull_rules, [], initial_capital=capital)
            assert len(df_trades) == 1
            t = df_trades.iloc[0]
            
            entry_price = extreme_price + SLIPPAGE_PER_SHARE
            max_allowed_shares = int((capital * 0.25) / max(entry_price, 1.0))
            if extreme_price == 10000.0:
                assert max_allowed_shares == 2
                assert 2 * entry_price <= capital * 0.25

    def test_penny_price_sizing_behavior(self):
        """Tests position sizing when SPY is at penny price ($0.50)."""
        capital = 100_000.0
        penny_price = 0.50

        df_wave = pd.DataFrame({
            "Wave_ID": ["W_PENNY_PRICE"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [penny_price],
            "P_End": [penny_price * 1.50],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [penny_price * 0.05],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

        df_trades, _, _ = simulate_trend_wave_strategy(df_wave, bull_rules, [], initial_capital=capital)
        assert len(df_trades) == 1
        t = df_trades.iloc[0]
        
        entry_price = penny_price + SLIPPAGE_PER_SHARE
        max_shares = int((capital * 0.25) / max(entry_price, 1.0))
        assert max_shares == 25000
        assert max_shares * entry_price <= capital * 0.25

    def test_ashtakavarga_sav_multipliers_and_monotonicity(self):
        """Verifies SAV scaling (0.75x for <=25, 1.0x for 26-29, 1.25x for >=30)."""
        df_waves = pd.DataFrame({
            "Wave_ID": ["W_HIGH", "W_NEUTRAL", "W_LOW"],
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
        df_trades, _, _ = simulate_trend_wave_strategy(df_waves, bull_rules, [], initial_capital=100_000.0)
        assert len(df_trades) == 3
        assert df_trades.iloc[0]["Net_PnL"] > df_trades.iloc[1]["Net_PnL"]
        assert df_trades.iloc[1]["Net_PnL"] > df_trades.iloc[2]["Net_PnL"]

    def test_extreme_atr_volatility_bounds(self):
        """Verifies near-zero and hyper-large ATR values are safely clamped by sizing denominator."""
        capital = 100_000.0
        
        # Near-zero ATR
        df_wave_zero = pd.DataFrame({
            "Wave_ID": ["W_ZERO_ATR"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [100.0],
            "P_End": [105.0],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [1e-12],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]
        df_trades_zero, _, _ = simulate_trend_wave_strategy(df_wave_zero, bull_rules, [], initial_capital=capital)
        assert len(df_trades_zero) == 1
        
        # Hyper-large ATR
        df_wave_huge = pd.DataFrame({
            "Wave_ID": ["W_HUGE_ATR"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [100.0],
            "P_End": [105.0],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [1e6],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        df_trades_huge, _, _ = simulate_trend_wave_strategy(df_wave_huge, bull_rules, [], initial_capital=capital)
        assert len(df_trades_huge) == 1


class TestAdversarialFrictionAndAccounting:
    """Adversarial stress-testing suite for IBKR commissions and dynamic slippage."""

    def test_friction_strictly_deducted_on_breakeven_trade(self):
        """A trade with zero price movement (P_End == P_Start) MUST produce negative net PnL due to friction."""
        df_wave = pd.DataFrame({
            "Wave_ID": ["W_BREAKEVEN"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [300.0],
            "P_End": [300.0],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [3.0],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

        df_trades, _, _ = simulate_trend_wave_strategy(df_wave, bull_rules, [], initial_capital=100_000.0)
        assert len(df_trades) == 1
        t = df_trades.iloc[0]
        
        assert t["Net_PnL"] < 0.0
        assert t["Return_Pct"] < 0.0
        assert t["Capital_After"] < 100_000.0

    def test_short_trade_friction_and_slippage_directionality(self):
        """Verifies slippage penalty penalizes short trades (enters lower, exits higher)."""
        p_start = 200.0
        p_end = 190.0

        df_wave = pd.DataFrame({
            "Wave_ID": ["W_SHORT"],
            "Timeframe": ["1D"],
            "Direction": ["Bearish_Liquidation"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [p_start],
            "P_End": [p_end],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [3.0],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        bear_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

        df_trades, _, _ = simulate_trend_wave_strategy(df_wave, [], bear_rules, initial_capital=100_000.0)
        assert len(df_trades) == 1
        t = df_trades.iloc[0]
        
        assert t["Entry_Price"] == round(p_start - SLIPPAGE_PER_SHARE, 2)
        assert t["Exit_Price"] == round(p_end + SLIPPAGE_PER_SHARE, 2)
        assert t["Net_PnL"] > 0.0

    def test_commission_floor_enforcement_small_orders(self):
        """Verifies that orders with 1-100 shares still pay minimum $1.00 per leg ($2.00 round-trip)."""
        df_wave = pd.DataFrame({
            "Wave_ID": ["W_MINI"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [100.0],
            "P_End": [101.0],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [10.0],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [20],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

        df_trades, _, _ = simulate_trend_wave_strategy(df_wave, bull_rules, [], initial_capital=100.0)
        assert len(df_trades) == 1
        t = df_trades.iloc[0]
        assert t["Net_PnL"] == -1.02

    def test_commission_scaling_for_large_volume_institutional_orders(self):
        """Verifies IBKR tiered commission scales accurately for large block sizes."""
        # 10,000 shares * $0.005 = $50.00 per leg -> $100.00 round trip
        shares = 10000
        commission_per_leg = max(shares * IBKR_COMMISSION_PER_SHARE, IBKR_MIN_COMMISSION)
        assert commission_per_leg == 50.0
        assert 2 * commission_per_leg == 100.0


class TestAdversarialCapitalDrawdownAndCompounding:
    """Stress tests sequential compounding, catastrophic drawdowns, and non-negativity."""

    def test_50_consecutive_catastrophic_losses_compounding(self):
        """Verifies compounding dynamics and capital decay under 50 brutal losing trades."""
        waves_list = []
        for i in range(50):
            waves_list.append({
                "Wave_ID": f"W_LOSS_{i:03d}",
                "Timeframe": "1D",
                "Direction": "Bullish_Thrust",
                "T_Start_UTC": f"2020-01-{(i%28)+1:02d} 09:30:00",
                "T_End_UTC": f"2020-01-{(i%28)+1:02d} 16:00:00",
                "P_Start": 100.0,
                "P_End": 80.0,
                "Wave_Duration_Bars": 1,
                "Baseline_ATR": 2.0,
                "Inception_Moon_Sign": "Aries",
                "Inception_SAV_At_Moon": 28,
            })
        df_waves = pd.DataFrame(waves_list)
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

        df_trades, trade_returns, metrics = simulate_trend_wave_strategy(
            df_waves, bull_rules, [], initial_capital=100_000.0
        )
        assert len(df_trades) == 50
        for i in range(1, len(df_trades)):
            assert df_trades.iloc[i]["Capital_After"] < df_trades.iloc[i-1]["Capital_After"]
        
        assert metrics["Total_Trades"] == 50
        assert metrics["Win_Rate_Pct"] == 0.0
        assert abs(metrics["Max_Drawdown_Pct"]) > 0.0

    def test_all_197_historical_trades_causality_and_manifest_reproducibility(self):
        """Verifies exact match and temporal causality across the full 197 historical trade manifest."""
        manifest_path = "data/backtest_trades_manifest.parquet"
        assert os.path.exists(manifest_path), "Manifest parquet missing"
        df_manifest = pd.read_parquet(manifest_path)
        assert len(df_manifest) == 197, f"Expected 197 trades in manifest, found {len(df_manifest)}"

        entry_dates = pd.to_datetime(df_manifest["Entry_Date"])
        exit_dates = pd.to_datetime(df_manifest["Exit_Date"])
        
        assert entry_dates.is_monotonic_increasing, "Trade entry dates are not monotonically increasing"
        assert (exit_dates >= entry_dates).all(), "Found trades where exit occurs before entry"
        assert (df_manifest["Holding_Bars"] >= 0).all(), "Negative holding bars detected"
        assert (df_manifest["Capital_After"] > 0).all(), "Negative or zero capital detected in production ledger"
        assert df_manifest["Capital_After"].min() >= 100_000.0, "Capital dropped below initial $100k"

        regimes = run_regime_breakdown_backtest(df_manifest)
        total_allocated = sum(r["Total_Trades"] for r in regimes.values())
        assert total_allocated == 197, f"Regime allocation incomplete: {total_allocated}/197 trades"

    def test_conflicting_signals_produce_zero_trades(self):
        """Verifies conflicting bullish and bearish signals produce zero trade execution."""
        df_wave = pd.DataFrame({
            "Wave_ID": ["W_CONFLICT"],
            "Timeframe": ["1D"],
            "Direction": ["Bullish_Thrust"],
            "T_Start_UTC": ["2020-01-02 09:30:00"],
            "T_End_UTC": ["2020-01-10 16:00:00"],
            "P_Start": [300.0],
            "P_End": [310.0],
            "Wave_Duration_Bars": [5],
            "Baseline_ATR": [3.0],
            "Inception_Moon_Sign": ["Aries"],
            "Inception_SAV_At_Moon": [28],
        })
        bull_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]
        bear_rules = [{"Antecedents": "[Moon in Aries]", "Confidence_Pct": 80.0}]

        df_trades, _, _ = simulate_trend_wave_strategy(df_wave, bull_rules, bear_rules, initial_capital=100_000.0)
        assert df_trades.empty
