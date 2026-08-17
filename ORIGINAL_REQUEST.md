# Original User Request

## Initial Request — 2026-08-17T15:43:35Z

Build an end-to-end multi-timeframe SPY candlestick anomaly extraction engine and Vedic astrology correlation modeling system with continuous, eternal brutal multipoint quality inspection across all code chunks and logic phases until achieving a 100% error-free cycle.

Working directory: C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings
Integrity mode: development

## Requirements

### R1. Multi-Timeframe Historical Data Ingestion & Anomaly Sieve
- Ingest complete historical SPY market data across 6 timeframes:
  - 1H, 2H, 4H: 2016 to Present (Alpaca institutional hourly feed + RTH session-aligned aggregation).
  - 1D, 1W, 1MO: 1993 to Present (Full 33+ year SPY inception-to-date history via official market feeds).
- Implement non-lookahead feature extraction:
  - Solid Body Dominance: Solid Ratio = |Close - Open| / (High - Low) >= 0.65 with strict wick rejection limits (max(Upper Wick, Lower Wick) / Range <= 0.25).
  - Big Volatility Outlier: Adaptive Trailing Body / ATR(20) >= 1.50 (shifted by 1) plus timeframe percentage floors.
  - Abnormal Volume: Time-of-Day (TOD) Relative Volume RVOL >= 1.50x to eliminate opening/closing bell U-curve bias.
  - Timestamp Precision: Dual Datetime_UTC, Datetime_NY, and Julian_Date_UT for exact astronomical alignment.

### R2. Eternal Multi-Agent Brutal Multipoint Quality Inspection Loop
- Deploy continuous adversarial inspection agents executing atomic-level scrutiny across 10 critical failure vectors:
  1. Lookahead bias & data leakage in rolling baselines.
  2. Intraday volume U-curve distortion.
  3. Session boundary alignment (RTH vs. ETH).
  4. Wick/Shadow asymmetry and pin-bar misclassifications.
  5. Overnight gap vs. intraday real body separation.
  6. Historical volatility regime shifts (1990s vs 2008 vs 2020 vs modern).
  7. Numerical stability, zero-range handling, and division-by-zero protection.
  8. Astrological ephemeris coordinate and timezone precision.
  9. Computational efficiency (O(N) vectorized processing).
  10. Downstream compatibility with Vedic Panchang/Transit tables.
- If ANY flaw or edge-case failure is detected, automatically route back to builder agents to refactor and re-verify in an autonomous, infinite self-correcting loop until a 100% clean cycle is verified.

### R3. Vedic Astrological Alignment & Feature Matrix Generation
- Synchronize all extracted anomaly datetimes against Swiss Ephemeris astronomical calculations:
  - Sidereal Zodiac (Lahiri Ayanamsha) planetary longitudes (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu).
  - 27 Nakshatras & 108 Padas.
  - Panchang elements (Tithi, Vara, Nakshatra, Yoga, Karana).
  - Retrograde motions, combustion, planetary aspects (Drishti), and Navamsha (D9).
- Generate structured tabular datasets linking extreme market movements directly to astrological states.

### R4. Automated Verification & Artifact Deliverables
- Output partitioned datasets (.parquet and .csv) for every timeframe along with a unified master anomaly manifest.
- Provide comprehensive automated test suites and mathematical validation reports proving zero NaNs, zero duplicate timestamps, and 100% condition compliance.

## Acceptance Criteria

### Data & Mathematical Integrity
- [ ] 100% of extracted rows across 1H, 2H, 4H, 1D, 1W, 1MO strictly satisfy Solid Ratio >= 0.65, RVOL >= 1.50x, and Body/ATR >= 1.50 (or minimum return floor).
- [ ] Master manifest contains exact union sum of all individual timeframe anomaly rows.
- [ ] Zero duplicate timestamps and zero NaNs in all critical price, volume, and indicator columns.
- [ ] All trailing statistics (ATR, Volume SMA, RVOL) are strictly computed with prior-bar shift (shift(1)) with zero lookahead bias.

### Multi-Agent Inspection & Fix Verification
- [ ] Continuous inspection test suite executes without a single assertion error or unhandled exception.
- [ ] Full summary report generated documenting exact counts, green vs. red distributions, and average metrics per timeframe.
- [ ] All deliverables committed and pushed cleanly to git branch feat/extreme-solid-candlestick-anomalies.
