# Project: Multi-Timeframe SPY Candlestick Anomaly Extraction & Vedic Astrological Correlation Modeling System

## Architecture
The system consists of three primary layered pipelines with clean interface contracts, full vectorization, zero lookahead bias, and high-precision Swiss Ephemeris astronomical calculation:

```
[Historical SPY Feeds]
  ├── Intraday (1H, 2H, 4H: 2016-2026 Alpaca institutional cache / RTH 09:30-16:00 EST)
  └── Interday (1D, 1W, 1MO: 1993-2026 SPY Inception-to-Date official feeds)
         │
         ▼
[Module 1: Market Data Ingestion & Anomaly Sieve] (M1)
  ├── Session Alignment (RTH filtering, multi-timeframe aggregation)
  ├── Non-Lookahead Metrics: True Range & ATR(20) [shift(1)], TOD RVOL [shift(1)]
  ├── Geometric Filters: Solid Ratio >= 0.65, Max Wick Ratio <= 0.25
  ├── Volatility & Volume Triggers: Body/ATR >= 1.50 (or return floor), RVOL >= 1.50x
  └── Timestamp Engine: Datetime_UTC (ISO8601), Datetime_NY, Julian_Date_UT (microsecond-safe)
         │
         ▼
[Module 2: Swiss Ephemeris Sidereal Vedic Engine] (M2)
  ├── Swiss Ephemeris Initialization: SIDM_LAHIRI, FLG_SWIEPH | FLG_SPEED | FLG_SIDEREAL
  ├── 9 Grahas Kinematics: Longitude, Latitude, Speed, Retrograde (Speed < 0), Combustion
  ├── 27 Nakshatras & 108 Padas: Exact mathematical mapping (13°20' and 3°20')
  ├── Navamsha (D9): floor(Longitude / 3°20') % 12 elemental lord sign mapping
  ├── 5 Panchang Limbs: Tithi (1-30), Vara (0-6), Nakshatra (1-27), Yoga (1-27), Karana (1-60)
  └── Parashari Drishti: Special aspects (Mars 4,7,8; Jupiter 5,7,9; Saturn 3,7,10; all 7th)
         │
         ▼
[Module 3: Alignment Matrix, Exporter & Master Manifest Pipeline] (M3)
  ├── 66-Column Unified Feature Schema (Market price/geom/vol/RVOL + Vedic astronomical/panchang)
  ├── Partitioned Data Exporters: Parquet & CSV for 1H, 2H, 4H, 1D, 1W, 1MO
  └── Master Anomaly Manifest: Exact union sum validation across all 6 timeframes
         │
         ▼
[Module 4: 10-Vector Quality Inspector Suite & Git Branch Packaging] (M4)
  ├── Atomic-level validation across 10 Critical Failure Vectors
  ├── Automated mathematical validation reports (zero NaNs, zero duplicate timestamps)
  └── Git repository branch management (`feat/extreme-solid-candlestick-anomalies`)
```

## Feature Inventory
Every feature from the Survey phase is mapped to an assigned milestone:
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Multi-Timeframe SPY Ingestion (1H, 2H, 4H, 1D, 1W, 1MO) | Complete historical feeds (2016-2026 intraday, 1993-2026 interday) with RTH session alignment (09:30-16:00 EST). | M1 | Survey |
| 2 | Solid Body & Wick Rejection Sieve | Solid Ratio >= 0.65, max(Upper Wick, Lower Wick) / Range <= 0.25. | M1 | Survey |
| 3 | Non-Lookahead Volatility Trigger | Trailing ATR(20) computed with prior-bar `shift(1)`. Body / ATR(20) >= 1.50 or timeframe return floor. | M1 | Survey |
| 4 | Time-of-Day (TOD) RVOL Normalization | Trailing intraday volume baseline by hour slot with `shift(1)`, RVOL >= 1.50x to eliminate U-curve distortion. | M1 | Survey |
| 5 | Dual Timestamps & Julian Date Engine | Microsecond-safe Julian Day UT, Datetime_UTC, and Datetime_NY alignment with 0.000000 error vs Swiss Ephemeris. | M1 | Survey |
| 6 | Swiss Ephemeris Sidereal Lahiri Setup | `swe.set_sid_mode(swe.SIDM_LAHIRI)` + `swe.calc_ut` with `FLG_SWIEPH | FLG_SPEED | FLG_SIDEREAL`. | M2 | Survey |
| 7 | 9 Grahas Coordinate & Kinematic Engine | Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu positions, speed, retrograde flag (`speed < 0`). | M2 | Survey |
| 8 | 27 Nakshatras & 108 Padas Mapping | Exact boundary division (13°20' per Nakshatra, 3°20' per Pada) with deity/lord/gana attributes. | M2 | Survey |
| 9 | Navamsha D9 Chart Calculation | `floor(lon / 3.33333333°) % 12` sign identification and lord determination. | M2 | Survey |
| 10 | 5-Limb Panchang System | Tithi (1-30 Shukla/Krishna), Vara (0-6), Nakshatra (1-27), Yoga (1-27), Karana (1-60 with 4 fixed + 7 repeating). | M2 | Survey |
| 11 | Parashari Drishti & Combustion | Mars (4,7,8), Jupiter (5,7,9), Saturn (3,7,10), 7th aspects, and traditional combustion orbs. | M2 | Survey |
| 12 | 66-Column Fusion Alignment Matrix | Seamless join of candlestick anomaly features and Vedic astronomical features. | M3 | Survey |
| 13 | Partitioned Parquet & CSV Exporters | Partitioned `.parquet` and `.csv` datasets for 1H, 2H, 4H, 1D, 1W, 1MO in `data/anomalies/`. | M3 | Survey |
| 14 | Master Anomaly Manifest & Union Check | Unified master dataset verifying exact row union sum across all 6 timeframes. | M3 | Survey |
| 15 | 10-Vector Quality Inspector Suite | Atomic tests for lookahead, U-curve, RTH, wick asymmetry, gap separation, regime shifts, zero-range stability, ephemeris precision, O(N) efficiency, and schema compatibility. | M4 | Survey |
| 16 | Mathematical Validation Report | Markdown/JSON audit report proving zero NaNs, zero duplicate timestamps, and 100% rule compliance. | M4 | Survey |
| 17 | Git Branch Packaging | Verified clean commit on `feat/extreme-solid-candlestick-anomalies`. | M4 | Survey |
| 18 | E2E Test Suite (Tiers 1-4) | Category-Partition, BVA, Pairwise, and Real-World Workload test cases across all components. | E2E | Survey |
| 19 | Adversarial Coverage Hardening (Tier 5) | White-box stress testing, boundary fuzzing, and forensic integrity audit. | E2E | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | E2E test harness, Tiers 1-4 test suite, `TEST_INFRA.md`, `TEST_READY.md`. | none | DONE |
| 1 | M1: Ingestion & Sieve Engine | SPY data feeds (1H, 2H, 4H, 1D, 1W, 1MO), RTH filter, TOD RVOL, ATR(20), Solid Ratio, Julian Date. | none | DONE |
| 2 | M2: Vedic Ephemeris Engine | Swiss Ephemeris Lahiri calculations, 9 Grahas, Nakshatras/Padas, Navamsha D9, Panchang, Drishti, Combustion. | none | DONE |
| 3 | M3: Fusion Matrix & Deliverables | 66-column schema fusion, partitioned `.parquet`/`.csv` generation, Master Anomaly Manifest with union sum check. | M1, M2 | DONE |
| 4 | M4: Quality Inspector & Packaging | 10 Failure Vectors audit script, validation report generation, git branch `feat/extreme-solid-candlestick-anomalies`. | M3 | DONE |
| Final | Final E2E Pass & Hardening | Phase 1 (100% E2E test pass) + Phase 2 (Adversarial coverage hardening & Forensic Audit). | E2E, M4 | DONE |

## Interface Contracts
### Ingestion & Sieve (M1) ↔ Vedic Ephemeris Engine (M2) ↔ Fusion Pipeline (M3)
- **M1 Output Dataframe Schema**:
  - `Datetime_UTC` (datetime64[ns, UTC]): Standard ISO UTC timestamp.
  - `Datetime_NY` (datetime64[ns, America/New_York]): Eastern market time.
  - `Julian_Date_UT` (float64): Precise Julian Day UT (e.g., 2457388.500000).
  - `Timeframe` (string): '1H', '2H', '4H', '1D', '1W', '1MO'.
  - `Open`, `High`, `Low`, `Close` (float64): Geometric prices.
  - `Volume` (float64): Bar trading volume.
  - `Real_Body` (float64): `abs(Close - Open)`.
  - `Candle_Range` (float64): `High - Low`.
  - `Upper_Wick` (float64): `High - max(Open, Close)`.
  - `Lower_Wick` (float64): `min(Open, Close) - Low`.
  - `Solid_Ratio` (float64): `Real_Body / max(Candle_Range, 1e-9)`.
  - `Max_Wick_Ratio` (float64): `max(Upper_Wick, Lower_Wick) / max(Candle_Range, 1e-9)`.
  - `Candle_Direction` (string): 'GREEN' if Close >= Open else 'RED'.
  - `Trailing_ATR20` (float64): ATR(20) shifted by 1.
  - `Body_To_ATR` (float64): `Real_Body / Trailing_ATR20`.
  - `TOD_RVOL` (float64): Intraday TOD relative volume shifted by 1.

- **M2 Output Dataframe Schema (Given Julian_Date_UT array)**:
  - Planetary Longitudes: `Sun_Lon`, `Moon_Lon`, `Mars_Lon`, `Mercury_Lon`, `Jupiter_Lon`, `Venus_Lon`, `Saturn_Lon`, `Rahu_Lon`, `Ketu_Lon` (float64, 0° to 360° Sidereal Lahiri).
  - Planetary Speeds & Retrograde: `*_Speed` (float64), `*_Retrograde` (bool, True if speed < 0).
  - Nakshatra & Pada: `Moon_Nakshatra` (int, 1-27), `Moon_Nakshatra_Name` (string), `Moon_Pada` (int, 1-4).
  - Navamsha (D9): `Sun_Navamsha_Sign`, `Moon_Navamsha_Sign`, `Mars_Navamsha_Sign`, `Jupiter_Navamsha_Sign`, `Saturn_Navamsha_Sign` (string/int).
  - Panchang Limbs: `Tithi_Num` (int 1-30), `Tithi_Name` (string), `Paksha` (string 'Shukla'/'Krishna'), `Vara_Num` (int 0-6), `Vara_Name` (string), `Yoga_Num` (int 1-27), `Yoga_Name` (string), `Karana_Num` (int 1-60), `Karana_Name` (string).
  - Planetary Aspects & Combustion: `Mars_Drishti_On_Moon` (bool), `Saturn_Drishti_On_Moon` (bool), `Jupiter_Drishti_On_Moon` (bool), `Combust_Planets` (string).

- **M3 Fusion & Master Manifest Output**:
  - Combined 66-column schema containing complete price, geometry, volatility, volume, astronomical coordinates, and Panchang attributes.
  - File locations:
    - `data/anomalies/spy_anomalies_1h.parquet` / `.csv` (445 rows)
    - `data/anomalies/spy_anomalies_2h.parquet` / `.csv` (210 rows)
    - `data/anomalies/spy_anomalies_4h.parquet` / `.csv` (124 rows)
    - `data/anomalies/spy_anomalies_1d.parquet` / `.csv` (177 rows)
    - `data/anomalies/spy_anomalies_1w.parquet` / `.csv` (34 rows)
    - `data/anomalies/spy_anomalies_1mo.parquet` / `.csv` (11 rows)
    - `data/anomalies/master_anomaly_manifest.parquet` / `.csv` (1,001 rows)
    - `data/spy_anomalies_vedic_enriched.parquet` / `.csv` (1,001 rows $\times$ 66 columns)

- **M4 Quality Inspector Output**:
  - `reports/quality_inspection_report.md` (29/29 checks passed, 100.00% score)
  - `reports/mathematical_validation_report.json` (0 NaNs, 0 duplicate timestamps, exact SHA-256 provenance hashes)
  - 146/146 pytest tests passed cleanly.
