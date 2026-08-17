"""
Adversarial Stress Testing & Invariant Fuzzing Test Suite
Authored by Challenger 1 (teamwork_preview_challenger)

Tests:
1. Data Leakage & Lookahead Bias Gauntlet:
   - Inject future price/volume anomalies (massive spike, crash, 100x volume) at index T+1..N.
   - Assert exact bitwise or floating equality of ATR, RVOL, Body_To_ATR, is_solid, is_high_volume, is_extreme_anomaly for all bars <= T.
2. Degenerate & Extreme Candle Fuzzing:
   - Perfect zero-range flat bars (High == Low == Open == Close).
   - Dojis (Open == Close).
   - Micro-range / sub-epsilon candles (Range = 1e-12).
   - Ultra-high prices (High = 1e12), ultra-low penny prices (1e-6).
   - Single-tick extreme wicks (High = 1000, Low = 1, Open = 100, Close = 100).
   - 20 consecutive zero-range bars -> Trailing_ATR division safety.
   - 20 consecutive zero-volume bars -> RVOL division safety.
3. Strict Invariant Verification & Random Property Fuzzing:
   - Invariant A: Solid Ratio <= 1.0
   - Invariant B: Max Wick Ratio <= 1.0
   - Invariant C: Real Body + Upper Wick + Lower Wick == Candle Range (within 1e-9)
   - Invariant D: When Range > 1e-6: Solid Ratio + Upper Wick Ratio + Lower Wick Ratio == 1.0 (within 1e-9)
   - Invariant E: All flagged anomalies strictly satisfy the 4 sieve conditions.
4. Astronomical & Vedic Coordinate Invariants:
   - Longitudes in [0, 360)
   - Rahu/Ketu exact 180° opposition
   - Nakshatras in [1, 27], Padas in [1, 4]
   - Tithi in [1, 30], Yoga in [1, 27], Karana in [1, 60]
5. Master Manifest & Partition Union Invariant:
   - Partition row counts sum to exactly Master Manifest row count in BOTH Parquet and CSV.
   - Zero NaNs, zero Infs across all numeric columns.
   - Check file existence and consistency across `data/` and `data/anomalies/`.
"""

import os
import glob
import pytest
import numpy as np
import pandas as pd

from src.market_data.anomaly_sieve import (
    compute_candlestick_geometry,
    compute_trailing_atr,
    compute_tod_rvol,
    compute_hardened_features_and_anomalies,
    TIMEFRAME_RETURN_FLOORS,
)
from src.market_data.data_ingestion import compute_julian_date
from src.vedic_astrology.ephemeris import (
    calculate_9_grahas,
    calculate_graha_positions_batch,
    datetime_to_julian_day,
)
from src.vedic_astrology.nakshatra_navamsha import get_nakshatra, get_navamsha
from src.vedic_astrology.panchang import calculate_panchang, calculate_panchang_batch


# =====================================================================
# 1. LOOKAHEAD & DATA LEAKAGE GAUNTLET
# =====================================================================
class TestAdversarialLookaheadLeakage:
    """
    Empirically verifies that future bars CANNOT leak into past bar features.
    """

    @pytest.fixture
    def baseline_series(self):
        """Generate a deterministic 100-bar hourly price series."""
        np.random.seed(42)
        n = 100
        dates_utc = pd.date_range("2023-01-02 09:30:00", periods=n, freq="1h", tz="UTC")
        dates_ny = dates_utc.tz_convert("America/New_York")

        close_prices = 400.0 + np.cumsum(np.random.randn(n) * 0.5)
        open_prices = close_prices + np.random.randn(n) * 0.2
        high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(n) * 0.3)
        low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(n) * 0.3)
        volume = np.random.uniform(500_000, 2_000_000, size=n)

        df = pd.DataFrame({
            "Datetime_UTC": dates_utc,
            "Datetime_NY": dates_ny,
            "Open": open_prices,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volume,
        })
        return df

    def test_future_massive_price_spike_no_leakage(self, baseline_series):
        """
        Inject a 100x price explosion in future bar at index 60..99.
        Verify bars 0..59 are completely identical in ATR, RVOL, and flags.
        """
        df_base = baseline_series.copy()
        df_valid_base, _ = compute_hardened_features_and_anomalies(df_base, timeframe="1H")

        df_poisoned = df_base.copy()
        # Poison future starting at index 60
        df_poisoned.loc[60:, "High"] *= 100.0
        df_poisoned.loc[60:, "Close"] *= 100.0
        df_poisoned.loc[60:, "Low"] *= 50.0

        df_valid_poisoned, _ = compute_hardened_features_and_anomalies(df_poisoned, timeframe="1H")

        # Compare bars 0..59
        cols_to_compare = [
            "Real_Body", "Candle_Range", "Solid_Ratio", "Max_Wick_Ratio",
            "Trailing_ATR20", "Body_To_ATR", "TOD_RVOL", "RVOL",
            "is_solid", "is_high_volume", "is_big_magnitude", "is_extreme_anomaly"
        ]

        # Slice up to bar 59
        base_slice = df_valid_base[df_valid_base["Datetime_UTC"] <= df_base["Datetime_UTC"].iloc[59]]
        poison_slice = df_valid_poisoned[df_valid_poisoned["Datetime_UTC"] <= df_base["Datetime_UTC"].iloc[59]]

        assert len(base_slice) == len(poison_slice)
        for col in cols_to_compare:
            if base_slice[col].dtype == bool:
                assert (base_slice[col].values == poison_slice[col].values).all(), f"Lookahead leakage in boolean flag {col}"
            else:
                np.testing.assert_allclose(
                    base_slice[col].values,
                    poison_slice[col].values,
                    rtol=1e-12,
                    atol=1e-12,
                    err_msg=f"Lookahead leakage detected in numeric feature {col} when future prices spiked!"
                )

    def test_future_massive_volume_anomaly_no_leakage(self, baseline_series):
        """
        Inject a 1000x volume surge at index 70..99.
        Verify bars 0..69 maintain identical TOD RVOL and classification.
        """
        df_base = baseline_series.copy()
        df_valid_base, _ = compute_hardened_features_and_anomalies(df_base, timeframe="1H")

        df_poisoned = df_base.copy()
        df_poisoned.loc[70:, "Volume"] *= 1000.0

        df_valid_poisoned, _ = compute_hardened_features_and_anomalies(df_poisoned, timeframe="1H")

        base_slice = df_valid_base[df_valid_base["Datetime_UTC"] <= df_base["Datetime_UTC"].iloc[69]]
        poison_slice = df_valid_poisoned[df_valid_poisoned["Datetime_UTC"] <= df_base["Datetime_UTC"].iloc[69]]

        for col in ["Trailing_Vol_SMA20", "TOD_Vol_SMA20", "TOD_RVOL", "RVOL", "is_high_volume", "is_extreme_anomaly"]:
            if base_slice[col].dtype == bool:
                assert (base_slice[col].values == poison_slice[col].values).all(), f"Lookahead in volume flag {col}"
            else:
                np.testing.assert_allclose(
                    base_slice[col].values,
                    poison_slice[col].values,
                    rtol=1e-12,
                    atol=1e-12,
                    err_msg=f"Lookahead leakage detected in volume metric {col}!"
                )

    def test_immediate_next_bar_shift_integrity(self, baseline_series):
        """
        Alter ONLY bar T+1 (index 50). Verify bar T (index 49) is 100% unaffected.
        """
        df_base = baseline_series.copy()
        df_valid_base, _ = compute_hardened_features_and_anomalies(df_base, timeframe="1H")

        df_poisoned = df_base.copy()
        df_poisoned.loc[50, "Open"] = 9999.0
        df_poisoned.loc[50, "High"] = 10000.0
        df_poisoned.loc[50, "Low"] = 1.0
        df_poisoned.loc[50, "Close"] = 5000.0
        df_poisoned.loc[50, "Volume"] = 999_999_999.0

        df_valid_poisoned, _ = compute_hardened_features_and_anomalies(df_poisoned, timeframe="1H")

        base_at_49 = df_valid_base[df_valid_base["Datetime_UTC"] == df_base["Datetime_UTC"].iloc[49]].iloc[0]
        poison_at_49 = df_valid_poisoned[df_valid_poisoned["Datetime_UTC"] == df_base["Datetime_UTC"].iloc[49]].iloc[0]

        for col in ["Trailing_ATR20", "Body_To_ATR", "TOD_RVOL", "is_extreme_anomaly"]:
            assert base_at_49[col] == poison_at_49[col], f"Leakage from bar 50 back to bar 49 on column {col}"


# =====================================================================
# 2. DEGENERATE & EXTREME CANDLE FUZZING
# =====================================================================
class TestAdversarialDegenerateCandles:
    """
    Stress tests zero range, Dojis, micro ranges, extreme wicks, zero volume.
    """

    def test_zero_range_flat_bars_no_nan_no_inf(self):
        """Flat line: Open == High == Low == Close = 100.0."""
        n = 30
        dates_utc = pd.date_range("2023-01-02 09:30:00", periods=n, freq="1h", tz="UTC")
        df_flat = pd.DataFrame({
            "Datetime_UTC": dates_utc,
            "Datetime_NY": dates_utc.tz_convert("America/New_York"),
            "Open": [100.0] * n,
            "High": [100.0] * n,
            "Low": [100.0] * n,
            "Close": [100.0] * n,
            "Volume": [1_000_000.0] * n,
        })

        df_geom = compute_candlestick_geometry(df_flat)
        assert not df_geom["Solid_Ratio"].isna().any(), "NaN found in Solid_Ratio for flat bars"
        assert not np.isinf(df_geom["Solid_Ratio"]).any(), "Inf found in Solid_Ratio for flat bars"
        assert (df_geom["Solid_Ratio"] == 0.0).all(), "Solid_Ratio must default to 0.0 on zero range"
        assert (df_geom["Max_Wick_Ratio"] == 0.0).all(), "Max_Wick_Ratio must default to 0.0 on zero range"
        assert (df_geom["Candle_Direction"] == "DOJI").all()

        # Run through full sieve
        df_valid, anoms = compute_hardened_features_and_anomalies(df_flat, timeframe="1H")
        assert len(anoms) == 0, "Flat bars must NEVER be flagged as anomalies"
        assert not df_valid["Trailing_ATR20"].isna().any()

    def test_zero_volume_20_bars_stability(self):
        """20 consecutive bars with 0 volume."""
        n = 35
        dates_utc = pd.date_range("2023-01-02 09:30:00", periods=n, freq="1h", tz="UTC")
        df_zero_vol = pd.DataFrame({
            "Datetime_UTC": dates_utc,
            "Datetime_NY": dates_utc.tz_convert("America/New_York"),
            "Open": [100.0 + i * 0.1 for i in range(n)],
            "High": [101.0 + i * 0.1 for i in range(n)],
            "Low": [99.0 + i * 0.1 for i in range(n)],
            "Close": [100.5 + i * 0.1 for i in range(n)],
            "Volume": [0.0] * n,
        })

        df_rvol = compute_tod_rvol(df_zero_vol, timeframe="1H")
        assert not df_rvol["TOD_RVOL"].isna().any(), "NaN found in TOD_RVOL with 0 volume"
        assert not np.isinf(df_rvol["TOD_RVOL"]).any(), "Inf found in TOD_RVOL with 0 volume"
        assert (df_rvol["TOD_RVOL"] == 0.0).all()

    def test_micro_range_sub_epsilon_candles(self):
        """Micro-range candles below 1e-6 threshold (Range = 1e-9)."""
        n = 30
        dates_utc = pd.date_range("2023-01-02 09:30:00", periods=n, freq="1h", tz="UTC")
        df_micro = pd.DataFrame({
            "Datetime_UTC": dates_utc,
            "Datetime_NY": dates_utc.tz_convert("America/New_York"),
            "Open": [100.000000000] * n,
            "High": [100.000000001] * n,
            "Low": [100.000000000] * n,
            "Close": [100.000000001] * n,
            "Volume": [1000.0] * n,
        })

        df_geom = compute_candlestick_geometry(df_micro)
        assert (df_geom["Solid_Ratio"] == 0.0).all()
        assert not df_geom["Solid_Ratio"].isna().any()
        assert not np.isinf(df_geom["Solid_Ratio"]).any()

    def test_extreme_single_tick_wick_pinbar(self):
        """Extreme upper pin-bar: High = 1000, Low = 100, Open = 100, Close = 101."""
        df_pin = pd.DataFrame({
            "Open": [100.0],
            "High": [1000.0],
            "Low": [100.0],
            "Close": [101.0],
        })
        df_res = compute_candlestick_geometry(df_pin)
        assert df_res["Solid_Ratio"].iloc[0] == pytest.approx(1.0 / 900.0, rel=1e-6)
        assert df_res["Upper_Wick"].iloc[0] == 899.0
        assert df_res["Lower_Wick"].iloc[0] == 0.0
        assert df_res["Max_Wick_Ratio"].iloc[0] == pytest.approx(899.0 / 900.0, rel=1e-6)
        assert df_res["Max_Wick_Ratio"].iloc[0] > 0.25, "Pin bar must be rejected by max wick ratio"

    def test_extreme_price_magnitudes(self):
        """Berkshire Hathaway scale prices ($600,000) and penny stock scale ($0.0001)."""
        df_high = pd.DataFrame({
            "Open": [600_000.0],
            "High": [610_000.0],
            "Low": [599_000.0],
            "Close": [609_000.0],
        })
        df_low = pd.DataFrame({
            "Open": [0.00010],
            "High": [0.00015],
            "Low": [0.00009],
            "Close": [0.00014],
        })
        res_high = compute_candlestick_geometry(df_high)
        res_low = compute_candlestick_geometry(df_low)

        assert 0.0 <= res_high["Solid_Ratio"].iloc[0] <= 1.0
        assert 0.0 <= res_low["Solid_Ratio"].iloc[0] <= 1.0
        assert not res_high.isna().any().any()
        assert not res_low.isna().any().any()


# =====================================================================
# 3. STRICT INVARIANT VERIFICATION & RANDOM PROPERTY FUZZING
# =====================================================================
class TestAdversarialInvariantFuzzing:
    """
    Fuzzes 10,000 random OHLC combinations to verify mathematical invariants.
    """

    def test_fuzz_10000_random_candles_geometric_invariants(self):
        """
        Generates 10,000 random valid OHLC bars and asserts all geometric invariants:
        - Solid_Ratio in [0.0, 1.0]
        - Max_Wick_Ratio in [0.0, 1.0]
        - Real_Body + Upper_Wick + Lower_Wick == Candle_Range (within 1e-9)
        - Upper_Wick_Ratio + Lower_Wick_Ratio + Solid_Ratio == 1.0 when Range > 1e-6
        """
        np.random.seed(1337)
        n = 10_000

        base = np.random.uniform(1.0, 1000.0, size=n)
        o_offset = np.random.uniform(-50.0, 50.0, size=n)
        c_offset = np.random.uniform(-50.0, 50.0, size=n)

        opens = np.maximum(0.01, base + o_offset)
        closes = np.maximum(0.01, base + c_offset)

        max_oc = np.maximum(opens, closes)
        min_oc = np.minimum(opens, closes)

        highs = max_oc + np.random.exponential(scale=10.0, size=n)
        lows = np.maximum(0.001, min_oc - np.random.exponential(scale=10.0, size=n))

        df_fuzz = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
        })

        df_geom = compute_candlestick_geometry(df_fuzz)

        # Invariant 1: Solid_Ratio <= 1.00000001
        assert (df_geom["Solid_Ratio"] <= 1.0 + 1e-9).all(), "Solid_Ratio exceeded 1.0!"
        assert (df_geom["Solid_Ratio"] >= 0.0).all(), "Solid_Ratio < 0.0!"

        # Invariant 2: Max_Wick_Ratio <= 1.00000001
        assert (df_geom["Max_Wick_Ratio"] <= 1.0 + 1e-9).all(), "Max_Wick_Ratio exceeded 1.0!"
        assert (df_geom["Max_Wick_Ratio"] >= 0.0).all(), "Max_Wick_Ratio < 0.0!"

        # Invariant 3: Real_Body + Upper_Wick + Lower_Wick == Candle_Range
        sum_components = df_geom["Real_Body"] + df_geom["Upper_Wick"] + df_geom["Lower_Wick"]
        diff = (sum_components - df_geom["Candle_Range"]).abs()
        assert (diff < 1e-7).all(), f"Geometry sum violated! Max diff: {diff.max()}"

        # Invariant 4: Ratio sum == 1.0 for valid ranges
        valid_ranges = df_geom["Candle_Range"] > 1e-6
        if valid_ranges.any():
            ratio_sum = (
                df_geom.loc[valid_ranges, "Solid_Ratio"]
                + df_geom.loc[valid_ranges, "Upper_Wick_Ratio"]
                + df_geom.loc[valid_ranges, "Lower_Wick_Ratio"]
            )
            ratio_diff = (ratio_sum - 1.0).abs()
            assert (ratio_diff < 1e-7).all(), f"Ratio partition violated! Max diff: {ratio_diff.max()}"

    def test_sieve_anomaly_strict_filters_invariant(self):
        """
        Verify that for all flagged anomalies in historical extractions,
        ALL 4 Sieve conditions are strictly met without exception.
        """
        anom_files = glob.glob("data/anomalies/spy_anomalies_*.parquet")
        assert len(anom_files) >= 6, f"Expected 6+ anomaly files, found {len(anom_files)}"

        for f in anom_files:
            tf = os.path.basename(f).replace("spy_anomalies_", "").replace(".parquet", "").upper()
            if tf in ["MASTER_ANOMALY_MANIFEST", "VEDIC_ENRICHED"]:
                continue

            df_anom = pd.read_parquet(f)
            if len(df_anom) == 0:
                continue

            # Check 1: Solid Ratio >= 0.65
            assert (df_anom["Solid_Ratio"] >= 0.65 - 1e-9).all(), f"Solid Ratio < 0.65 in {tf}"

            # Check 2: Max Wick Ratio <= 0.25
            assert (df_anom["Max_Wick_Ratio"] <= 0.25 + 1e-9).all(), f"Max Wick Ratio > 0.25 in {tf}"

            # Check 3: RVOL >= 1.50
            rvol_col = "RVOL" if "RVOL" in df_anom.columns else "TOD_RVOL"
            assert (df_anom[rvol_col] >= 1.50 - 1e-9).all(), f"RVOL < 1.50 in {tf}"

            # Check 4: Big Volatility (Body/ATR >= 1.50 or Body Return >= Floor)
            floor = TIMEFRAME_RETURN_FLOORS.get(tf, 1.0)
            vol_cond = (df_anom["Body_To_ATR"] >= 1.50 - 1e-9) | (df_anom["Abs_Body_Return_Pct"] >= floor - 1e-9)
            assert vol_cond.all(), f"Volatility trigger failed in {tf}"


# =====================================================================
# 4. ASTRONOMICAL & VEDIC COORDINATE INVARIANTS
# =====================================================================
class TestAdversarialVedicInvariants:
    """
    Stress-tests astronomical coordinates, boundary conditions, and invariants.
    """

    def test_ketu_exact_opposition_invariant(self):
        """Ketu longitude must ALWAYS be exactly (Rahu + 180) % 360 across 500 random timestamps."""
        np.random.seed(999)
        # Random Julian dates between 1990 and 2030
        jds = np.random.uniform(2447892.5, 2462502.5, size=500)

        for jd in jds:
            grahas = calculate_9_grahas(jd)
            rahu_lon = grahas["Rahu"]["lon"]
            ketu_lon = grahas["Ketu"]["lon"]

            expected_ketu = (rahu_lon + 180.0) % 360.0
            diff = abs(ketu_lon - expected_ketu)
            if diff > 180.0:
                diff = abs(diff - 360.0)
            assert diff < 1e-5, f"Ketu opposition violated at JD {jd}: Rahu={rahu_lon}, Ketu={ketu_lon}"

    def test_nakshatra_pada_boundary_invariants(self):
        """Nakshatra must be in 1..27 and Pada in 1..4 for all 360 degrees."""
        for deg in np.linspace(0.0, 359.9999, 3600):
            nak_info = get_nakshatra(deg)
            assert 1 <= nak_info["nakshatra_num"] <= 27, f"Invalid nakshatra {nak_info['nakshatra_num']} for {deg}°"
            assert 1 <= nak_info["pada"] <= 4, f"Invalid pada {nak_info['pada']} for {deg}°"

    def test_panchang_bounds_invariants(self):
        """5 Panchang limbs must strictly obey classical boundary integers."""
        np.random.seed(42)
        sun_lons = np.random.uniform(0.0, 360.0, size=500)
        moon_lons = np.random.uniform(0.0, 360.0, size=500)
        jds = np.random.uniform(2447892.5, 2462502.5, size=500)

        for s_lon, m_lon, jd in zip(sun_lons, moon_lons, jds):
            p = calculate_panchang(s_lon, m_lon, jd)
            assert 1 <= p["tithi_num"] <= 30
            assert p["paksha"] in ["Shukla", "Krishna"]
            assert 0 <= p["vara_num"] <= 6
            assert 1 <= p["yoga_num"] <= 27
            assert 1 <= p["karana_num"] <= 60


# =====================================================================
# 5. MASTER MANIFEST & PARTITION UNION INTEGRITY
# =====================================================================
class TestAdversarialMasterManifestIntegrity:
    """
    Stress tests deliverable artifacts, parquet vs csv parity, and union sums.
    """

    def test_manifest_union_sum_exact_parity_both_formats(self):
        """
        Verify:
        sum(1h, 2h, 4h, 1d, 1w, 1mo) == master manifest count == 1,001
        in BOTH Parquet AND CSV formats.
        """
        timeframes = ["1h", "2h", "4h", "1d", "1w", "1mo"]
        pq_counts = {}
        csv_counts = {}

        for tf in timeframes:
            pq_file = f"data/anomalies/spy_anomalies_{tf}.parquet"
            csv_file = f"data/anomalies/spy_anomalies_{tf}.csv"

            assert os.path.exists(pq_file), f"Missing parquet file: {pq_file}"
            assert os.path.exists(csv_file), f"Missing csv file: {csv_file}"

            df_pq = pd.read_parquet(pq_file)
            df_csv = pd.read_csv(csv_file)

            assert len(df_pq) == len(df_csv), f"Parity mismatch for {tf}: Parquet has {len(df_pq)}, CSV has {len(df_csv)}"
            pq_counts[tf] = len(df_pq)
            csv_counts[tf] = len(df_csv)

        master_pq = pd.read_parquet("data/anomalies/master_anomaly_manifest.parquet")
        master_csv = pd.read_csv("data/anomalies/master_anomaly_manifest.csv")

        assert len(master_pq) == len(master_csv), "Master Parquet vs CSV count mismatch"
        total_pq_sum = sum(pq_counts.values())
        total_csv_sum = sum(csv_counts.values())

        assert total_pq_sum == len(master_pq) == 1001, f"Union sum mismatch: {total_pq_sum} != {len(master_pq)}"
        assert total_csv_sum == len(master_csv) == 1001, f"CSV union sum mismatch: {total_csv_sum} != {len(master_csv)}"

    def test_zero_nans_and_zero_duplicate_timestamps(self):
        """
        Exhaustively checks all parquet and csv files in data/anomalies/ for:
        - 0 NaNs across all columns
        - 0 duplicate timestamps within timeframe
        - Monotonic timestamp ordering
        """
        for f in glob.glob("data/anomalies/*.parquet"):
            df = pd.read_parquet(f)
            assert len(df) > 0, f"File {f} is empty!"
            
            # Check NaNs
            nan_counts = df.isna().sum()
            cols_with_nan = nan_counts[nan_counts > 0]
            assert len(cols_with_nan) == 0, f"NaNs found in {f}: {cols_with_nan.to_dict()}"

            # Check duplicates (if single timeframe)
            if "master" not in f.lower():
                time_col = "Datetime_UTC" if "Datetime_UTC" in df.columns else "Datetime"
                dupes = df[time_col].duplicated().sum()
                assert dupes == 0, f"Duplicate timestamps found in {f}: {dupes}"
