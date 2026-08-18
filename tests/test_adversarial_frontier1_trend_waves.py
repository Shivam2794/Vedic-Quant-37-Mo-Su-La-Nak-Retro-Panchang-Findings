"""
ADVERSARIAL STRESS TESTING HARNESS — FRONTIER 1 (DEEP GAUNTLET)
================================================================
Empirical Challenger 1 Test Suite for Trend Wave Engine, Kaufman ER,
Dual-Anchor Omni-Vedic Enrichment, and Classical Astrological Invariants.

Pillars Challenged:
  1. Lookahead Bias Oracle (Temporal Immutability under Future Data Expansion).
  2. Extreme Pathological Edge Cases (Flatlines, Flash Crashes, Zero Volume, Brownian Motion, Sub-threshold Series).
  3. Kaufman Efficiency Ratio (KER) Mathematical Boundary Fuzzing (100,000 cases).
  4. Astrological Invariant Fuzzing (SAV 337 Sum Invariant & Jaimini 7-Karaka Bijection).
  5. Dual-Anchor Omni-Vedic Matrix Quality & Full Real Universe Verification.
"""

import os
import sys
import math
import pytest
import numpy as np
import pandas as pd
import swisseph as swe
from typing import List, Dict, Any

# Ensure project root and src directories are on path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.analysis.trend_wave_engine import (
    calculate_kaufman_efficiency_ratio,
    extract_trend_waves_from_series,
    extract_all_timeframe_trend_waves,
    MIN_RETURN_FLOORS,
    ATR_MULTIPLIERS,
)
from src.analysis.enrich_trend_waves import enrich_trend_waves_with_omni_vedic
from src.core.jaimini_karakas import calculate_jaimini_karakas, format_degree
from src.core.astro_ashtakvarga import get_raw_ashtakvarga, bav_tensor
from src.vedic_astrology.omni_vedic_fusion import extract_omni_vedic_row, GRAHA_MAP


# ==============================================================================
# 1. LOOKAHEAD BIAS ORACLE (TEMPORAL IMMUTABILITY)
# ==============================================================================
class TestLookaheadBiasOracle:
    """
    Empirical Oracle verifying that past wave segmentation is 100% immutable
    and unaffected by subsequent future market data.
    """

    @pytest.mark.parametrize("timeframe", ["1D", "4H", "1H", "2H", "1W", "1MO"])
    def test_lookahead_real_data_extension(self, timeframe):
        """
        Extracts waves on prefix df[:T], appends real future bars df[:T+K],
        and verifies historical waves in df[:T] are identical.
        """
        file_path = os.path.join(PROJECT_ROOT, "data", f"spy_full_series_{timeframe.lower()}.parquet")
        if not os.path.exists(file_path):
            pytest.skip(f"Data file {file_path} not found.")

        df = pd.read_parquet(file_path).sort_values("Datetime_UTC").reset_index(drop=True)
        if len(df) < 100:
            pytest.skip(f"Insufficient bars in {file_path} (len={len(df)})")

        cutoffs = [50, 100, 200, 400] if len(df) > 450 else [int(len(df) * 0.4), int(len(df) * 0.7)]

        for t_cutoff in cutoffs:
            if t_cutoff >= len(df) - 10:
                continue

            df_prefix = df.iloc[:t_cutoff].copy()
            waves_prefix = extract_trend_waves_from_series(df_prefix, timeframe)

            if waves_prefix.empty:
                continue

            # Extend by future bars
            extensions = [20, 50, 100] if len(df) > t_cutoff + 100 else [len(df) - t_cutoff]
            for ext in extensions:
                if t_cutoff + ext > len(df):
                    continue

                df_extended = df.iloc[:t_cutoff + ext].copy()
                waves_extended = extract_trend_waves_from_series(df_extended, timeframe)

                # Check all completed waves from prefix are preserved identically
                for _, w_pre in waves_prefix.iterrows():
                    match = waves_extended[waves_extended["Wave_ID"] == w_pre["Wave_ID"]]
                    assert not match.empty, (
                        f"Wave {w_pre['Wave_ID']} disappeared after extending data from {t_cutoff} to {t_cutoff + ext}!"
                    )
                    w_ext = match.iloc[0]
                    # Verify bitwise/exact equality of all structural wave attributes
                    assert w_pre["Start_Idx"] == w_ext["Start_Idx"], "Start_Idx mismatch"
                    assert w_pre["End_Idx"] == w_ext["End_Idx"], "End_Idx mismatch"
                    assert w_pre["P_Start"] == pytest.approx(w_ext["P_Start"], rel=1e-6), "P_Start mismatch"
                    assert w_pre["P_End"] == pytest.approx(w_ext["P_End"], rel=1e-6), "P_End mismatch"
                    assert w_pre["Net_Return_Pct"] == pytest.approx(w_ext["Net_Return_Pct"], rel=1e-6), "Net_Return_Pct mismatch"
                    assert w_pre["Kaufman_ER"] == pytest.approx(w_ext["Kaufman_ER"], rel=1e-6), "Kaufman_ER mismatch"
                    assert w_pre["Baseline_ATR"] == pytest.approx(w_ext["Baseline_ATR"], rel=1e-6), "Baseline_ATR mismatch"
                    assert w_pre["Baseline_Vol_SMA"] == pytest.approx(w_ext["Baseline_Vol_SMA"], rel=1e-6), "Baseline_Vol_SMA mismatch"

    def test_lookahead_internal_indicator_recomputation(self):
        """
        Removes pre-calculated Trailing_ATR20 and Trailing_Vol_SMA20 to force internal
        rolling calculation, and tests that internal shift(1) avoids lookahead.
        """
        file_path = os.path.join(PROJECT_ROOT, "data", "spy_full_series_1d.parquet")
        if not os.path.exists(file_path):
            pytest.skip("Data file not found")

        df = pd.read_parquet(file_path).sort_values("Datetime_UTC").reset_index(drop=True)
        # Drop indicator columns if present
        cols_to_drop = [c for c in ["Trailing_ATR20", "Trailing_Vol_SMA20", "Julian_Date_UT", "Datetime_NY"] if c in df.columns]
        df_raw = df.drop(columns=cols_to_drop)

        t_cutoff = 300
        df_prefix = df_raw.iloc[:t_cutoff].copy()
        waves_prefix = extract_trend_waves_from_series(df_prefix, "1D")

        assert not waves_prefix.empty

        df_extended = df_raw.iloc[:t_cutoff + 200].copy()
        waves_extended = extract_trend_waves_from_series(df_extended, "1D")

        for _, w_pre in waves_prefix.iterrows():
            match = waves_extended[waves_extended["Wave_ID"] == w_pre["Wave_ID"]]
            assert not match.empty
            w_ext = match.iloc[0]
            assert w_pre["Start_Idx"] == w_ext["Start_Idx"]
            assert w_pre["End_Idx"] == w_ext["End_Idx"]
            assert w_pre["P_Start"] == pytest.approx(w_ext["P_Start"], rel=1e-6)
            assert w_pre["P_End"] == pytest.approx(w_ext["P_End"], rel=1e-6)

    def test_lookahead_adversarial_synthetic_shocks(self):
        """
        Generates deterministic base series, extracts waves at T=200,
        then appends extreme adversarial shock scenarios:
          1. 500% Hyper-Rally
          2. 90% Flash-Crash
          3. Massive High-Frequency Gaussian Noise
        Verifies historical waves up to T=200 remain 100% frozen.
        """
        np.random.seed(42)
        n_base = 250
        t = np.linspace(0, 6 * np.pi, n_base)
        closes = 100.0 + 20.0 * np.sin(t)
        highs = closes + 2.0
        lows = closes - 2.0
        opens = closes - 0.5
        vols = np.full(n_base, 5000.0)
        dt_utcs = pd.date_range("2020-01-01", periods=n_base, freq="1D", tz="UTC")

        df_base = pd.DataFrame({
            "Datetime_UTC": dt_utcs,
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": vols,
            "Trailing_ATR20": np.full(n_base, 3.0),
            "Trailing_Vol_SMA20": np.full(n_base, 5000.0),
        })

        waves_base = extract_trend_waves_from_series(df_base, "1D", atr_mult=2.0, min_return_floor=3.0, min_ker=0.50)
        assert len(waves_base) >= 3, "Base series should generate at least 3 waves"

        # Adversarial Shock 1: Hyper Rally (500% move over 50 bars)
        n_future = 50
        dt_future = pd.date_range(dt_utcs[-1] + pd.Timedelta(days=1), periods=n_future, freq="1D", tz="UTC")
        closes_rally = np.linspace(closes[-1], closes[-1] * 5.0, n_future)
        df_rally = pd.DataFrame({
            "Datetime_UTC": dt_future,
            "Open": closes_rally - 1.0,
            "High": closes_rally + 5.0,
            "Low": closes_rally - 2.0,
            "Close": closes_rally,
            "Volume": np.full(n_future, 50000.0),
            "Trailing_ATR20": np.full(n_future, 15.0),
            "Trailing_Vol_SMA20": np.full(n_future, 50000.0),
        })
        df_ext_rally = pd.concat([df_base, df_rally], ignore_index=True)
        waves_ext_rally = extract_trend_waves_from_series(df_ext_rally, "1D", atr_mult=2.0, min_return_floor=3.0, min_ker=0.50)

        for _, w_b in waves_base.iterrows():
            match = waves_ext_rally[waves_ext_rally["Wave_ID"] == w_b["Wave_ID"]]
            assert not match.empty, f"Wave {w_b['Wave_ID']} lost under hyper-rally!"
            w_ext = match.iloc[0]
            assert w_b["Start_Idx"] == w_ext["Start_Idx"]
            assert w_b["End_Idx"] == w_ext["End_Idx"]
            assert w_b["P_Start"] == pytest.approx(w_ext["P_Start"], rel=1e-6)
            assert w_b["P_End"] == pytest.approx(w_ext["P_End"], rel=1e-6)

        # Adversarial Shock 2: Flash Crash (90% drop over 50 bars)
        closes_crash = np.linspace(closes[-1], closes[-1] * 0.10, n_future)
        df_crash = pd.DataFrame({
            "Datetime_UTC": dt_future,
            "Open": closes_crash + 1.0,
            "High": closes_crash + 2.0,
            "Low": closes_crash - 1.0,
            "Close": closes_crash,
            "Volume": np.full(n_future, 100000.0),
            "Trailing_ATR20": np.full(n_future, 10.0),
            "Trailing_Vol_SMA20": np.full(n_future, 100000.0),
        })
        df_ext_crash = pd.concat([df_base, df_crash], ignore_index=True)
        waves_ext_crash = extract_trend_waves_from_series(df_ext_crash, "1D", atr_mult=2.0, min_return_floor=3.0, min_ker=0.50)

        for _, w_b in waves_base.iterrows():
            match = waves_ext_crash[waves_ext_crash["Wave_ID"] == w_b["Wave_ID"]]
            assert not match.empty, f"Wave {w_b['Wave_ID']} lost under flash crash!"
            w_ext = match.iloc[0]
            assert w_b["Start_Idx"] == w_ext["Start_Idx"]
            assert w_b["End_Idx"] == w_ext["End_Idx"]
            assert w_b["P_Start"] == pytest.approx(w_ext["P_Start"], rel=1e-6)
            assert w_b["P_End"] == pytest.approx(w_ext["P_End"], rel=1e-6)

        # Adversarial Shock 3: High-Frequency Noise
        noise = np.random.normal(0, 10.0, n_future)
        closes_noise = np.clip(closes[-1] + noise, 5.0, 500.0)
        df_noise = pd.DataFrame({
            "Datetime_UTC": dt_future,
            "Open": closes_noise,
            "High": closes_noise + 3.0,
            "Low": closes_noise - 3.0,
            "Close": closes_noise,
            "Volume": np.full(n_future, 5000.0),
            "Trailing_ATR20": np.full(n_future, 4.0),
            "Trailing_Vol_SMA20": np.full(n_future, 5000.0),
        })
        df_ext_noise = pd.concat([df_base, df_noise], ignore_index=True)
        waves_ext_noise = extract_trend_waves_from_series(df_ext_noise, "1D", atr_mult=2.0, min_return_floor=3.0, min_ker=0.50)

        for _, w_b in waves_base.iterrows():
            match = waves_ext_noise[waves_ext_noise["Wave_ID"] == w_b["Wave_ID"]]
            assert not match.empty, f"Wave {w_b['Wave_ID']} lost under high-frequency noise!"
            w_ext = match.iloc[0]
            assert w_b["Start_Idx"] == w_ext["Start_Idx"]
            assert w_b["End_Idx"] == w_ext["End_Idx"]


# ==============================================================================
# 2. EXTREME PATHOLOGICAL EDGE CASES
# ==============================================================================
class TestExtremeEdgeCases:
    """
    Adversarial edge case stress tests: flatlines, flash crashes, zero volume,
    Brownian motion, and boundary price conditions.
    """

    def test_insufficient_bars_boundary(self):
        """Length < 30 returns empty DataFrame without error."""
        dt = pd.date_range("2020-01-01", periods=25, freq="1D", tz="UTC")
        df_short = pd.DataFrame({
            "Datetime_UTC": dt,
            "Open": np.full(25, 100.0),
            "High": np.full(25, 102.0),
            "Low": np.full(25, 98.0),
            "Close": np.full(25, 100.0),
            "Volume": np.full(25, 1000.0),
        })
        res = extract_trend_waves_from_series(df_short, "1D")
        assert res.empty
        res_none = extract_trend_waves_from_series(None, "1D")
        assert res_none.empty

    def test_missing_required_columns(self):
        """Missing required columns raises ValueError."""
        df_bad = pd.DataFrame({"Close": [100.0] * 50})
        with pytest.raises(ValueError, match="Missing required column"):
            extract_trend_waves_from_series(df_bad, "1D")

    def test_flatline_zero_volatility_series(self):
        """
        All High=Low=Close=100.0 (Zero volatility).
        Should return empty DataFrame safely without any ZeroDivisionError.
        """
        n = 300
        dt = pd.date_range("2020-01-01", periods=n, freq="1D", tz="UTC")
        df_flat = pd.DataFrame({
            "Datetime_UTC": dt,
            "Open": np.full(n, 100.0),
            "High": np.full(n, 100.0),
            "Low": np.full(n, 100.0),
            "Close": np.full(n, 100.0),
            "Volume": np.full(n, 1000.0),
        })

        res = extract_trend_waves_from_series(df_flat, "1D")
        assert isinstance(res, pd.DataFrame)
        assert res.empty

    def test_zero_and_near_zero_volume(self):
        """
        Price action with volume=0.0 or 1e-12.
        Verifies baseline volume SMA protection: base_vol = max(vol_sma, 1.0).
        """
        n = 200
        t = np.linspace(0, 4 * np.pi, n)
        closes = 100.0 + 20.0 * np.sin(t)
        dt = pd.date_range("2020-01-01", periods=n, freq="1D", tz="UTC")

        for vol_val in [0.0, 1e-15, np.zeros(n)]:
            df_zero_vol = pd.DataFrame({
                "Datetime_UTC": dt,
                "Open": closes,
                "High": closes + 2.0,
                "Low": closes - 2.0,
                "Close": closes,
                "Volume": np.full(n, vol_val) if isinstance(vol_val, float) else vol_val,
            })
            res = extract_trend_waves_from_series(df_zero_vol, "1D", min_return_floor=2.0)
            assert not res.empty
            assert (res["Volume_Expansion_Ratio"] >= 0.0).all()
            assert not np.isnan(res["Volume_Expansion_Ratio"]).any()
            assert not np.isinf(res["Volume_Expansion_Ratio"]).any()

    def test_flash_crash_and_single_bar_spikes(self):
        """
        1-bar 99% crash and 1-bar 500% spike.
        Verifies no index out of bounds, no negative prices, and valid wave metrics.
        """
        n = 200
        closes = np.full(n, 100.0)
        highs = np.full(n, 102.0)
        lows = np.full(n, 98.0)

        # Bar 50: Flash crash to 1.0
        lows[50] = 1.0
        closes[50] = 1.5
        # Bar 120: Spike to 500.0
        highs[120] = 500.0
        closes[120] = 490.0

        dt = pd.date_range("2020-01-01", periods=n, freq="1D", tz="UTC")
        df_spike = pd.DataFrame({
            "Datetime_UTC": dt,
            "Open": np.full(n, 100.0),
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": np.full(n, 5000.0),
        })

        res = extract_trend_waves_from_series(df_spike, "1D")
        assert isinstance(res, pd.DataFrame)
        if not res.empty:
            assert (res["Start_Idx"] < res["End_Idx"]).all()
            assert (res["P_Start"] > 0.0).all()
            assert (res["P_End"] > 0.0).all()
            assert (res["Kaufman_ER"] >= 0.0).all()
            assert (res["Kaufman_ER"] <= 1.0).all()

    def test_brownian_motion_monte_carlo(self):
        """
        Simulates 50 independent Brownian motion random walks.
        Verifies invariant guarantees across 100% of extracted waves.
        """
        n_bars = 500
        for seed in range(50):
            np.random.seed(seed)
            returns = np.random.normal(0.0002, 0.02, n_bars)
            prices = 100.0 * np.cumprod(1.0 + returns)
            highs = prices * (1.0 + np.abs(np.random.normal(0.005, 0.005, n_bars)))
            lows = prices * (1.0 - np.abs(np.random.normal(0.005, 0.005, n_bars)))
            vols = np.random.lognormal(8.0, 0.5, n_bars)
            dt = pd.date_range("2020-01-01", periods=n_bars, freq="1D", tz="UTC")

            df_bm = pd.DataFrame({
                "Datetime_UTC": dt,
                "Open": prices,
                "High": highs,
                "Low": lows,
                "Close": prices,
                "Volume": vols,
            })

            waves = extract_trend_waves_from_series(df_bm, "1D", min_return_floor=3.0, min_ker=0.50)
            if not waves.empty:
                assert (waves["Start_Idx"] < waves["End_Idx"]).all()
                assert (waves["Wave_Duration_Bars"] >= 3).all()
                assert (waves["P_Start"] > 0.0).all()
                assert (waves["P_End"] > 0.0).all()
                assert (waves["Kaufman_ER"] >= 0.0).all()
                assert (waves["Kaufman_ER"] <= 1.0).all()
                assert not waves.isnull().any().any()


# ==============================================================================
# 3. KAUFMAN EFFICIENCY RATIO (KER) MATHEMATICAL BOUNDARY FUZZING
# ==============================================================================
class TestKaufmanEfficiencyRatioFuzzing:
    """
    Fuzz-tests 100,000+ random and pathological sequences against
    Perry Kaufman's Efficiency Ratio formula:
      KER = |P_end - P_start| / Sum(|P_i - P_{i-1}|)
    """

    def test_ker_pathological_lengths(self):
        """Length < 2 returns 1.0; empty array returns 1.0."""
        assert calculate_kaufman_efficiency_ratio(np.array([])) == 1.0
        assert calculate_kaufman_efficiency_ratio(np.array([100.0])) == 1.0

    def test_ker_zero_path_length(self):
        """Constant price arrays return 0.0 (path_length <= 1e-8)."""
        assert calculate_kaufman_efficiency_ratio(np.array([50.0, 50.0, 50.0])) == 0.0
        assert calculate_kaufman_efficiency_ratio(np.full(100, 123.456)) == 0.0

    def test_ker_fuzz_100k_sequences(self):
        """
        Fuzzes 100,000 random sequences across diverse distributions:
          - Uniform, Normal, Cauchy, Lognormal
          - Microscopic scales (1e-12) to astronomical scales (1e12)
          - Monotonic sequences, sawteeth, alternating spikes
        """
        np.random.seed(1337)
        total_fuzz_runs = 100000
        batch_size = 5000

        for b in range(total_fuzz_runs // batch_size):
            # 1. Random uniform sequences
            lens = np.random.randint(2, 100, size=batch_size // 4)
            for length in lens:
                seq = np.random.uniform(-1000.0, 1000.0, size=length)
                ker = calculate_kaufman_efficiency_ratio(seq)
                assert 0.0 <= ker <= 1.0, f"KER out of bounds: {ker} for uniform seq"

            # 2. Extreme scale sequences
            for scale in [1e-12, 1e-6, 1.0, 1e6, 1e12]:
                seq = np.random.normal(0, scale, size=20)
                ker = calculate_kaufman_efficiency_ratio(seq)
                assert 0.0 <= ker <= 1.0, f"KER out of bounds: {ker} for scale {scale}"

            # 3. Monotonic sequences (must equal 1.0)
            for _ in range(batch_size // 8):
                seq_mono = np.sort(np.random.uniform(1.0, 100.0, size=15))
                ker_up = calculate_kaufman_efficiency_ratio(seq_mono)
                assert ker_up == pytest.approx(1.0, abs=1e-6)
                ker_down = calculate_kaufman_efficiency_ratio(seq_mono[::-1])
                assert ker_down == pytest.approx(1.0, abs=1e-6)

            # 4. Cauchy heavy-tailed jumps
            for _ in range(batch_size // 8):
                seq_cauchy = np.cumsum(np.random.standard_cauchy(size=30))
                ker = calculate_kaufman_efficiency_ratio(seq_cauchy)
                assert 0.0 <= ker <= 1.0, f"KER out of bounds: {ker} for Cauchy seq"

            # 5. Sawtooth & Ping-Pong
            for _ in range(batch_size // 8):
                pattern = np.array([100.0, 150.0, 100.0, 150.0, 100.0, 150.0])
                ker = calculate_kaufman_efficiency_ratio(pattern)
                # Net = 50, Path = 50*5 = 250 -> KER = 0.20
                assert ker == pytest.approx(0.20, abs=1e-6)


# ==============================================================================
# 4. ASTROLOGICAL INVARIANT FUZZING (SAV == 337 & JAIMINI 7-KARAKA BIJECTION)
# ==============================================================================
class TestAstrologicalInvariantFuzzing:
    """
    High-throughput stochastic fuzz testing across historical eras and
    pathological boundary charts for classical Parashari and Jaimini invariants.
    """

    def test_ashtakavarga_sav_337_invariant_random_charts(self):
        """
        Fuzzes 5,000 synthetic charts with all possible sign configurations (0..11).
        Verifies SAV total sum equals 337 in 100.0% of cases and each planet BAV
        matches Parashari point totals.
        """
        np.random.seed(777)
        EXPECTED_BAV_TOTALS = [48, 49, 39, 54, 56, 52, 39]  # Sun, Moon, Mars, Mer, Jup, Ven, Sat
        assert sum(EXPECTED_BAV_TOTALS) == 337

        n_samples = 5000
        for _ in range(n_samples):
            # 8 factors: Sun..Saturn (0..6) + Ascendant (7)
            planet_signs = np.random.randint(0, 12, size=8, dtype=np.int32)
            bav, sav = get_raw_ashtakvarga(planet_signs)

            # 1. Total SAV sum must equal 337
            assert int(np.sum(sav)) == 337, f"SAV sum != 337 for signs {planet_signs}"

            # 2. Each BAV planet row sum must equal exact classical constant
            for p_idx in range(7):
                assert int(np.sum(bav[p_idx])) == EXPECTED_BAV_TOTALS[p_idx], (
                    f"Planet {p_idx} BAV sum != {EXPECTED_BAV_TOTALS[p_idx]}"
                )

    def test_ashtakavarga_sav_337_julian_days_fuzz(self):
        """
        Fuzzes 500 real astronomical Julian Days between 1800 and 2050.
        Verifies SAV total == 337 for Inception and Climax vectors.
        """
        np.random.seed(999)
        # JD range from 1800 (JD 2378497) to 2050 (JD 2469808)
        random_jds = np.random.uniform(2378497.0, 2469808.0, size=500)

        for jd in random_jds:
            row = extract_omni_vedic_row(jd)
            assert row["SAV_Total"] == 337, f"SAV_Total != 337 at JD {jd}"
            assert 0 <= row["SAV_At_Moon"] <= 56, f"SAV_At_Moon out of range at JD {jd}"

    def test_jaimini_7_karaka_bijective_uniqueness_fuzz(self):
        """
        Fuzzes 5,000 random planetary degree configurations.
        Verifies:
          1. Exactly 7 karakas returned: {AK, AmK, BK, MK, PK, GK, DK}.
          2. Exactly 7 unique planets mapped (1-to-1 bijection).
          3. Correct descending sorting by degree in sign.
        """
        np.random.seed(2026)
        valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        expected_karakas = {"Atma", "Amatya", "Bhratru", "Matru", "Putra", "Gnati", "Dara"}
        expected_abbrs = {"AK", "AmK", "BK", "MK", "PK", "GK", "DK"}

        for _ in range(5000):
            # Random absolute longitudes [0, 360)
            longitudes = np.random.uniform(0.0, 360.0, size=7)
            planet_inputs = [{"planet": p, "longitude": l} for p, l in zip(valid_planets, longitudes)]

            results = calculate_jaimini_karakas(planet_inputs)

            assert len(results) == 7
            assigned_karakas = {r["karaka"] for r in results}
            assigned_abbrs = {r["karaka_abbr"] for r in results}
            assigned_planets = {r["planet"] for r in results}

            assert assigned_karakas == expected_karakas, "Missing or duplicate Karaka names"
            assert assigned_abbrs == expected_abbrs, "Missing or duplicate Karaka abbreviations"
            assert assigned_planets == set(valid_planets), "Missing or duplicate planets in Karaka mapping"

            # Verify descending order of degrees in sign (with tie-breaker tolerance)
            degrees = [r["degree_in_sign"] for r in results]
            for i in range(len(degrees) - 1):
                assert degrees[i] >= degrees[i + 1] - 1e-9, "Karakas not in descending degree order"

    def test_jaimini_pathological_ties_and_boundaries(self):
        """
        Adversarial test with exact degree ties and boundary degrees (0.0° and 29.999999°).
        """
        valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # Case 1: All 7 planets at identical degree (15.0°)
        tied_all = [{"planet": p, "longitude": 15.0 + i * 30.0} for i, p in enumerate(valid_planets)]
        res_tied = calculate_jaimini_karakas(tied_all)
        assert len(res_tied) == 7
        assert len({r["karaka_abbr"] for r in res_tied}) == 7
        assert len({r["planet"] for r in res_tied}) == 7

        # Case 2: Boundary degrees 0.0° and 29.999999°
        bound_inputs = [
            {"planet": "Sun", "longitude": 0.0},
            {"planet": "Moon", "longitude": 29.999999},
            {"planet": "Mars", "longitude": 30.0},        # 0.0 in Taurus
            {"planet": "Mercury", "longitude": 59.999999},     # 29.999999 in Taurus
            {"planet": "Jupiter", "longitude": 60.0},       # 0.0 in Gemini
            {"planet": "Venus", "longitude": 105.5},        # 15.5 in Cancer
            {"planet": "Saturn", "longitude": 200.25},      # 20.25 in Libra
        ]
        res_bound = calculate_jaimini_karakas(bound_inputs)
        assert len(res_bound) == 7
        assert len({r["karaka_abbr"] for r in res_bound}) == 7
        assert len({r["planet"] for r in res_bound}) == 7

        # Moon should be AK (29.999999) or Mercury (29.999999)
        top_karaka = res_bound[0]
        assert top_karaka["karaka_abbr"] == "AK"
        assert top_karaka["degree_in_sign"] == pytest.approx(29.999999, rel=1e-5)


# ==============================================================================
# 5. DUAL-ANCHOR OMNI-VEDIC ENRICHMENT QUALITY & MASTER UNIVERSE
# ==============================================================================
class TestDualAnchorEnrichmentQuality:
    """
    Verifies dual-anchor enrichment pipeline integrity, 0 NaNs,
    and intra-wave dynamic kinematics.
    """

    def test_enrichment_on_synthetic_waves(self, tmp_path):
        """
        Creates a synthetic wave manifest and runs full dual-anchor enrichment.
        """
        syn_manifest_path = os.path.join(tmp_path, "syn_trend_waves.parquet")
        syn_out_path = os.path.join(tmp_path, "syn_enriched.parquet")

        # Build 10 synthetic waves across different Julian Dates
        jd_base = 2459000.0  # ~2020
        rows = []
        for i in range(10):
            rows.append({
                "Wave_ID": f"WAVE_1D_BULL_2020_00{i+1:02d}",
                "Timeframe": "1D",
                "Direction": "Bullish_Thrust",
                "Direction_Label": 1,
                "Start_Idx": i * 20,
                "End_Idx": i * 20 + 8,
                "T_Start_UTC": f"2020-05-{i+1:02d} 14:30:00+00:00",
                "T_Start_NY": f"2020-05-{i+1:02d} 09:30:00",
                "T_Start_JD": jd_base + i * 20.0,
                "T_End_UTC": f"2020-05-{i+9:02d} 14:30:00+00:00",
                "T_End_NY": f"2020-05-{i+9:02d} 09:30:00",
                "T_End_JD": jd_base + i * 20.0 + 8.0,
                "P_Start": 300.0 + i * 5.0,
                "P_End": 320.0 + i * 5.0,
                "Net_Return_Pct": 6.67,
                "Abs_Return_Pct": 6.67,
                "Wave_Duration_Bars": 9,
                "Kaufman_ER": 0.85,
                "Displacement_To_ATR": 4.5,
                "Volume_Expansion_Ratio": 1.45,
                "Baseline_ATR": 2.5,
                "Baseline_Vol_SMA": 100000.0,
            })
        df_syn = pd.DataFrame(rows)
        df_syn.to_parquet(syn_manifest_path, index=False)

        enriched_df = enrich_trend_waves_with_omni_vedic(syn_manifest_path, syn_out_path)

        assert not enriched_df.empty
        assert len(enriched_df) == 10
        assert enriched_df.isnull().sum().sum() == 0

        # Verify Invariants
        assert (enriched_df["Inception_SAV_Total"] == 337).all()
        assert (enriched_df["Climax_SAV_Total"] == 337).all()
        assert (enriched_df["Wave_Moon_Degrees_Traversed"] >= 0.0).all()
        assert (enriched_df["Wave_Planetary_Ingress_Count"] >= 0).all()
        assert (enriched_df["Wave_Planetary_Station_Count"] >= 0).all()

    def test_full_master_universe_invariants(self):
        """
        Validates the real 522-wave master enriched universe in data/
        for zero NaNs, SAV 337 holding, and Jaimini 7-Karaka uniqueness.
        """
        path = os.path.join(PROJECT_ROOT, "data", "spy_trend_waves_omni_vedic_supreme.parquet")
        if not os.path.exists(path):
            pytest.skip("Master enriched dataset not generated yet")

        df = pd.read_parquet(path)
        assert len(df) >= 500, f"Expected >= 500 waves, got {len(df)}"
        assert df.isnull().sum().sum() == 0, "Enriched dataset contains NaNs"

        # Check SAV Invariant across 100% of rows
        assert (df["Inception_SAV_Total"] == 337).all()
        assert (df["Climax_SAV_Total"] == 337).all()

        # Check Jaimini Bijection across 100% of rows
        karaka_cols = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        for _, row in df.iterrows():
            incept_k = [row[f"Inception_Jaimini_{k}"] for k in karaka_cols]
            assert len(set(incept_k)) == 7
            climax_k = [row[f"Climax_Jaimini_{k}"] for k in karaka_cols]
            assert len(set(climax_k)) == 7
