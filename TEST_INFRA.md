# TEST_INFRA — End-to-End Test Architecture & Quality Infrastructure

**Project**: Multi-Timeframe SPY Candlestick Anomaly Extraction & Vedic Astrological Correlation Modeling System  
**Branch**: `feat/extreme-solid-candlestick-anomalies`  
**Test Suite Architect**: E2E Test Architect (`test_writer_e2e`)  
**Standard**: Marcos Lopez de Prado Quant Standards, Swiss Ephemeris IAU Rigor, 10 Critical Failure Vectors  

---

## 1. Test Methodology & Strategy

The E2E test infrastructure employs four structured testing methodologies combined with continuous adversarial verification to enforce 100% mathematical precision, zero data leakage, and astronomical exactness:

### 1.1 Category-Partition Method
Input spaces and domain states are partitioned into mutually exclusive categories:
- **Candlestick Geometries**: Marubozu (100% solid), Standard solid ($SR \ge 0.65$), Pin-bars/Hammers (heavy wick, rejected), Flat candles ($Range = 0$), Doji candles ($SR \approx 0$).
- **Volume Regimes**: Morning open rush (09:30–10:00), Midday liquidity trough (12:00–13:00), Closing bell cross (15:00–16:00), Overnight ETH (rejected).
- **Market Volatility Regimes**: 1990s low-dollar high-vol, 2008 GFC extreme ATR, 2017 low-vol compression, 2020 COVID spike, 2022+ modern regimes.
- **Astronomical Epochs**: Solar/Lunar eclipses, Planetary stationary points (Direct $\leftrightarrow$ Retrograde), Combustion zones ($\le \text{orb}^\circ$), Sign and Nakshatra cusps ($0^\circ, 13^\circ20', 30^\circ$).

### 1.2 Boundary Value Analysis (BVA)
Tests systematically probe critical mathematical threshold boundaries:
- **Solid Ratio ($SR = \frac{\text{Real Body}}{\text{Range}}$)**: Probed at $0.649999$ (Fail) vs $0.650000$ (Pass), and $1.000000$ (Full Marubozu).
- **Max Wick Ratio ($MWR = \frac{\max(UW, LW)}{\text{Range}}$)**: Probed at $0.250000$ (Pass) vs $0.250001$ (Fail).
- **Relative Volume ($RVOL$)**: Probed at $1.499999x$ (Fail) vs $1.500000x$ (Pass).
- **Volatility Trigger ($\frac{\text{Body}}{ATR(20)}$)**: Probed at $1.499999$ vs $1.500000$ alongside timeframe-specific return percentage floors ($0.80\%$ for 1H, $1.20\%$ for 2H, $1.50\%$ for 4H, $2.00\%$ for 1D, $3.50\%$ for 1W, $5.00\%$ for 1MO).
- **Epsilon Denominator Guards**: Evaluated at $\Delta = 0.0$ and $\Delta = 10^{-12}$ to ensure $\epsilon = 10^{-6}$ (or $10^{-9}$) prevents `ZeroDivisionError` and `NaN` propagation.

### 1.3 Pairwise / Combinatorial Testing
Interaction matrices test cross-module state combinations:
- Green and Red candlestick anomalies crossed with Bullish/Bearish Tithis (Shukla vs Krishna).
- Planetary retrogrades (Mercury, Mars, Jupiter, Saturn, Venus) crossed with Parashari Drishti aspects (3rd, 4th, 5th, 7th, 8th, 9th, 10th).
- Daylight Saving Time (EDT $\leftrightarrow$ EST) shifts crossed with Time-of-Day (TOD) hourly bins.
- Half-day market sessions (13:00 close) crossed with multi-timeframe aggregations (2H, 4H).

### 1.4 Real-World Workload & Union Manifest Validation
Tests execute against the complete SPY historical dataset (1993–2026 for daily/weekly/monthly; 2016–2026 for 1H/2H/4H):
- Full manifest union sum consistency: $\sum_{TF} N_{TF} \equiv N_{\text{Master}}$.
- Column completeness: All 66 columns present, schema validated.
- Forensic zero-defect guarantees: Exactly 0 duplicate timestamps, exactly 0 NaNs across all critical price, volume, and astrological columns.

---

## 2. Test Suite Architecture (Tiers 1–5)

```
tests/
├── conftest.py                        # Fixtures, synthetic generators, ephemeris baselines, assertion helpers
├── test_tier1_feature_coverage.py     # Tier 1: Feature isolation tests (>= 5 tests per inventoried feature)
├── test_tier2_boundaries_corners.py   # Tier 2: Boundaries, edge cases, zero-range stability, DST, leap years
├── test_tier3_cross_feature.py        # Tier 3: Pairwise combinations, retrogrades, aspects, schema fusion
├── test_tier4_real_world_workloads.py # Tier 4: Master manifest validation, union sums, artifact parquet/csv checks
└── test_10_failure_vectors.py         # Dedicated 10 Critical Failure Vectors audit suite
```

### Tier Descriptions & Responsibilities:

| Test Tier | Module File | Focus & Coverage Scope |
|-----------|-------------|------------------------|
| **Tier 1: Feature Isolation** | `test_tier1_feature_coverage.py` | Dedicated unit tests for each of the 11 core engine features (Solid Ratio, Max Wick, Body/ATR, TOD RVOL, Julian Date, Lahiri 9 Grahas, 27 Nakshatras/108 Padas, Navamsha D9, 5 Panchang Limbs, Drishti Aspects, Combustion). Minimum 5 tests per feature ($> 55$ tests). |
| **Tier 2: Boundaries & Corners** | `test_tier2_boundaries_corners.py` | Zero-range candles, single-tick bars, floating-point epsilon guards, leap years (Feb 29), DST transitions (March/November), market half-days (13:00 closes), historical volatility regime shifts (1990s vs 2008 vs 2020). |
| **Tier 3: Cross-Feature Combinations** | `test_tier3_cross_feature.py` | Pairwise integration between market timestamps and Swiss Ephemeris transits, aspect calculations under retrograde planetary conditions, overnight gap vs intraday body separation, multi-timeframe timestamp consistency. |
| **Tier 4: Real-World Workloads** | `test_tier4_real_world_workloads.py` | End-to-end dataset validation on live `.parquet` and `.csv` deliverables across all 6 timeframes (1H, 2H, 4H, 1D, 1W, 1MO), verifying master manifest union sum ($N=1,001$), zero NaNs, zero duplicates, and summary stats. |
| **Tier 5: 10 Failure Vectors** | `test_10_failure_vectors.py` | Atomic-level audit enforcing compliance with all 10 Critical Failure Vectors from the user request and quality inspection guidelines. |

---

## 3. The 10 Critical Failure Vectors Audit Matrix

| Vector # | Failure Vector Description | Mitigation in Architecture | Verification Test in `test_10_failure_vectors.py` |
|:--------:|----------------------------|----------------------------|---------------------------------------------------|
| **V1** | **Lookahead Bias & Data Leakage** | All rolling indicators (ATR(20), Volume SMA, RVOL) strictly use prior-bar `.shift(1)`. Current bar values never enter baseline calculations. | `test_v1_no_lookahead_bias_in_rolling_baselines` |
| **V2** | **Intraday Volume U-Curve Distortion** | RVOL is stratified by `Hour_Of_Day` prior-bar historical rolling distributions to prevent 15:00 close volume from distorting 13:00 midday bars. | `test_v2_intraday_volume_u_curve_normalization` |
| **V3** | **Session Boundary & RTH Alignment** | Strict Regular Trading Hours mask ($09:30 - 16:00$ US/Eastern) applied before resampling, eliminating illiquid pre/post market noise. | `test_v3_session_boundary_rth_filtering` |
| **V4** | **Wick Asymmetry & Pin-Bar Misclassification** | $Max\_Wick\_Ratio \le 0.25$ rejects long upper/lower shadows (shooting stars, hammers, dragonfly dojis) even if real body is large. | `test_v4_wick_dominance_and_pin_bar_rejection` |
| **V5** | **Overnight Gap vs Intraday Real Body** | Disentangles `Body_Return_Pct` ($|Close - Open| / Open$) from `Overnight_Gap_Pct` ($(Open - PrevClose) / PrevClose$) and `Total_Return_Pct`. | `test_v5_overnight_gap_vs_intraday_real_body` |
| **V6** | **Historical Volatility Regime Shifts** | Dynamic $Body/ATR(20) \ge 1.50$ baseline paired with timeframe return floors adapts smoothly across 1993, 2008, 2020, and modern regimes. | `test_v6_volatility_regime_adaptability_and_floors` |
| **V7** | **Numerical Stability & Zero-Range Guards** | All denominators enforce $\max(Range, 1e-9)$ or $\max(ATR, 1e-6)$ to eliminate `ZeroDivisionError` and `inf`/`NaN` outputs on flat bars. | `test_v7_numerical_stability_and_zero_division` |
| **V8** | **Astrological Coordinate & Timezone Precision** | `swe.set_sid_mode(swe.SIDM_LAHIRI)` + `swe.FLG_SIDEREAL` with microsecond-safe UTC Julian Date UT conversion eliminates ephemeris drift. | `test_v8_astrological_coordinate_and_timezone_precision` |
| **V9** | **Computational Efficiency & Vectorization** | Vectorized NumPy/Pandas processing processes $50,000+$ bars in $< 5$ seconds ($O(N)$ linear complexity). | `test_v9_computational_efficiency_and_vectorization` |
| **V10** | **Downstream Schema Compatibility** | Full 66-column schema seamlessly integrates financial and Vedic features for ML/quant backtesting with zero nulls. | `test_v10_schema_downstream_compatibility` |

---

## 4. Coverage Thresholds & Quality Gates

The test suite enforces the following strict acceptance criteria:
1. **Pass Rate**: 100% of all tests across Tiers 1–5 must pass without a single failure or unhandled exception.
2. **Feature Coverage**: Each of the 11 core features contains $\ge 5$ isolated unit tests.
3. **Data Integrity Gates**:
   - Zero `NaN` values across all critical numeric and astrological columns.
   - Zero duplicate timestamps in any timeframe dataset.
   - Monotonic datetime ordering ($dt_i \le dt_{i+1}$).
   - Master manifest row count must equal the exact sum of individual timeframes:
     $$N_{\text{Master}} = N_{1H} + N_{2H} + N_{4H} + N_{1D} + N_{1W} + N_{1MO} = 1,001$$
4. **Sieve Condition Compliance**:
   - $Solid\_Ratio \ge 0.650000$ (100% of rows).
   - $Max\_Wick\_Ratio \le 0.250000$ (100% of rows).
   - $RVOL \ge 1.500000x$ (100% of rows).
   - $\frac{\text{Real Body}}{ATR(20)} \ge 1.50$ OR $|Body\_Return\_Pct| \ge \text{Min\_Floor}$ (100% of rows).
   - Direction strictly $\in \{\text{'GREEN'}, \text{'RED'}\}$.

---

## 5. Test Execution Commands

```powershell
# Run the complete test suite across all tiers
pytest tests/ -v

# Run individual test tiers
pytest tests/test_tier1_feature_coverage.py -v
pytest tests/test_tier2_boundaries_corners.py -v
pytest tests/test_tier3_cross_feature.py -v
pytest tests/test_tier4_real_world_workloads.py -v
pytest tests/test_10_failure_vectors.py -v

# Run with full traceback on failure
pytest tests/ --tb=short -v
```
