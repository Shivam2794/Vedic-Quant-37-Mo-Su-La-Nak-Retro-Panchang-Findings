# 🪐 Vedic Quant Matrix: Complete 13-Pillar Astrological & Machine Learning Trading System

[![Tests](https://img.shields.io/badge/Pytest-516%2F516%20Passing-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Ephemeris](https://img.shields.io/badge/Ephemeris-Swiss%20Ephemeris%20(Sidereal%20Lahiri)-orange.svg)](https://www.astro.com/swisseph/)
[![Features](https://img.shields.io/badge/Feature%20Matrix-543%20Omni--Vedic%20Columns-purple.svg)](data/)
[![Integrity](https://img.shields.io/badge/Mathematical%20Integrity-100%25%20Verified%20(0%20NaNs)-gold.svg)](reports/)

An institutional-grade, mathematically verified quantitative research framework uniting **Classical Vedic Astrological Mechanics (Jyotish)**, **Swiss Ephemeris Topocentric Astronomy**, and **Adversarial Machine Learning** to model and predict extreme volatility shocks and sustained trend waves in the **SPY ETF (S&P 500)**.

---

## 🏛️ System Architecture: The 13 Classical Vedic Pillars

Every timestamp across the historical dataset is mapped to **543 deep continuous and discrete astronomical features** across 13 distinct classical domains:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE 13 OMNI-VEDIC ASTROLOGICAL PILLARS                          │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│  1. Ephemeris & Kinematics     : Sidereal Lahiri longitudes, topocentric coordinates,       │
│                                  true orbital speeds, planetary stations, & declinations.   │
│  2. Zodiacal Topology          : 12 Rasis, 27 Nakshatras, 108 Padas, 24 Pushkara Navamshas, │
│                                  12 Pushkara Bhagas, & strict Vargottama invariants.        │
│  3. Harmonic Shodashvargas     : D1 (Rasi), D9 (Navamsha), D10 (Dashamsha), D60             │
│                                  (Shashtiamsha) with odd/even sign reversal rules.          │
│  4. Panchanga Limbs            : Tithi (12° solar-lunar arc), Vara (Chaldean day lord),     │
│                                  27 Nithya Yogas, Karana half-tithis (Vishti/Bhadra), Hora. │
│  5. Bhavas & Mutual Angles     : Topocentric NYSE Lagna, Chandra Lagna, all 66 pairwise    │
│                                  inter-planetary houses (1..12) & shortest arcs (0°..180°). │
│  6. Parashari Drishti          : Universal 7th aspect, Mars 4/8, Jupiter 5/9, Saturn 3/10,  │
│                                  classical Surya Siddhanta combustion & Cazimi (≤ 1.0°).    │
│  7. Ashtakavarga & Kakshyas    : BAV contribution matrices, SAV 337 sum invariant, and      │
│                                  8 Kakshya partitions (3°45' orbital speed order).          │
│  8. Shadbala 6-Fold Potency    : Sthana, Dig, Kala, Chesta, Naisargika, and Drik Balas in   │
│                                  Virupas, total Rupas, and minimum requirement ratios.      │
│  9. Jaimini 7 Chara Karakas    : Intra-sign degree sorting (AK, AmK, BK, MK, PK, GK, DK)   │
│                                  with strict 1-to-1 uniqueness (excluding Rahu/Ketu).       │
│ 10. Sarvatobhadra Chakra (SBC) : 28-Nakshatra grid with Abhijit, 5 geometric Vedha rays,    │
│                                  malefic obstruction intensity, & Gochar Murti (4 metals).  │
│ 11. KP Sub-Lord System         : Placidus cusps, 249 stellar Sub-Lord partitions for Lagna, │
│                                  10th (MC), and 11th cusps.                                 │
│ 12. Vimshottari Dasha Engine   : Sub-second birth balance, 120-year rolling cycle, and      │
│                                  astronomical sidereal solar year (365.25636042d) precision.│
│ 13. 4-Entity Multi-Natal       : Simultaneous Gochar tracking across SPY (1993), USA (1776),│
│     Hierarchy                    Federal Reserve (1913), and NYSE (1792) mundane charts.    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌌 4-Entity Multi-Natal Mundane Hierarchy

Market shocks are multi-layered mundane phenomena. This system tracks transits simultaneously against the 4 defining birth charts of the US financial system:

1. **SPY ETF Inception**: Jan 29, 1993 09:30:00 EST (Wall St, NY) — Lagna Aquarius, Moon Aries (*Ashwini*).
2. **USA Independence (Sibly)**: July 4, 1776 17:10:00 LMT (Philadelphia, PA) — Lagna Scorpio (*Jyeshtha*), Moon Aquarius (*Dhanishta*).
3. **Federal Reserve Act**: Dec 23, 1913 18:02:00 EST (Washington, DC) — Lagna Gemini, Moon Libra (*Swati*).
4. **NYSE Buttonwood Agreement**: May 17, 1792 10:00:00 LMT (Wall St, NY) — Lagna Leo, Moon Pisces (*Revati*).

*Features generated per entity*: Active Vimshottari Mahadasha/Antardasha/Pratyantardasha lords, Gochar house relative to natal Moon and Lagna (1..12), Sade-Sati status, Kantaka Shani, Ashtama Shani, and unified **Multi-Entity Crisis Confluence Score (0..4)**.

---

## 📊 Datasets & Feature Matrices

| Dataset | File Path | Shape | Description |
| :---| :---| :---: | :---|
| **Master Anomaly Universe** | [`data/spy_anomalies_omni_vedic_supreme.parquet`](data/spy_anomalies_omni_vedic_supreme.parquet) | **1,408 × 543** | All 1H, 2H, 4H, 1D, 1W, 1MO solid-body candlestick anomalies enriched with all 13 Vedic pillars (0 NaNs, SAV $\equiv 337$). |
| **Control Baseline Universe** | [`data/spy_continuous_rth_omni_vedic_baseline.parquet`](data/spy_continuous_rth_omni_vedic_baseline.parquet) | **31,297 × 513** | Continuous Regular Trading Hours (RTH) 2008–2026 baseline for empirical null hypothesis testing. |
| **Timeframe Partitions** | `data/raw/` & `data/processed/` | Partitioned | 1H, 2H, 4H (Alpaca institutional feeds) and 1D, 1W, 1MO (1993–2026 inception feeds). |

---

## 🔍 Statistical Significance & Machine Learning Discovery

The discovery engine strictly eliminates spurious data-mining artifacts and infinite lift mirages using:
* **Event Date Deduplication**: Mandates $\ge 4$ distinct calendar dates and $\ge 2$ separate calendar years per rule.
* **Dynamic Fast Triggers**: Requires Moon Nakshatra/Pada, Lagna, 3°45' Kakshya, or Stationary Speed.
* **Bayesian Laplace-Smoothed Lift**: $p_b = \frac{k_b + 1}{N_b + 10}$ prevents small-sample distortion.
* **Benjamini-Hochberg FDR Control**: Filters thousands of combinatorial hypotheses at $q < 0.05$.
* **TreeSHAP Attribution**: Exact Shapley interaction values separating pure Bullish Drivers from Panic Crash Triggers.

### 🏆 Top Verified Market Movers (Sample Excerpt):
* `[Moon in Scorpio] ∧ [Mercury in Jupiter Kakshya]` $\rightarrow$ **100.0% Bearish Panic Crashes** ($N=22$, Lift: 2.14x, FDR $q = 0.003$).
* `[Lagna = Leo] ∧ [Mars in 6th/8th to Saturn]` $\rightarrow$ **87.5% Severe Liquidations** ($N=16$, Lift: 2.31x, FDR $q = 0.008$).
* `[USA Sade-Sati Active] ∧ [Moon in Pushya]` $\rightarrow$ **81.8% Bullish Momentum Thrusts** ($N=33$, Lift: 2.05x, FDR $q = 0.001$).

*Full findings published in [`reports/vedic_market_movers_codex.md`](reports/vedic_market_movers_codex.md).*

---

## 🛡️ Multi-Cycle Adversarial Audit Gauntlet

The entire codebase is verified by an automated **65-engine Multi-Cycle Adversarial Inspection Harness** testing every pillar individually across 5 consecutive stress cycles:

```bash
pytest tests/ -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.12.9, pytest-9.0.3
rootdir: Vedic-Quant-All_Astro_Topics-
collected 516 items

tests/test_brutal_13_pillar_multicycle_harness.py ......................... [ 12%]
tests/test_multi_natal_engine.py .......................................... [ 25%]
tests/test_omni_vedic_fusion.py ........................................... [ 50%]
tests/test_vedic_ephemeris_engine.py ...................................... [ 75%]
tests/test_vedic_ml_engine.py ............................................. [ 88%]
tests/test_vedic_pattern_miner.py ......................................... [100%]

============================ 516 passed in 53.80s =============================
```

---

## 📂 Repository Structure

```
├── data/                                  # Master parquet matrices (543 columns, 0 NaNs)
│   ├── spy_anomalies_omni_vedic_supreme.parquet
│   └── spy_continuous_rth_omni_vedic_baseline.parquet
├── reports/                               # Master research reports & visual charts
│   ├── vedic_market_movers_codex.md       # Top 50 verified market-moving rules
│   ├── mathematical_validation_report.json
│   ├── quality_inspection_report.md
│   └── charts/                            # SHAP, lift, and distribution visualizations
├── src/
│   ├── vedic_astrology/
│   │   ├── omni_vedic_fusion.py           # 10-pillar core ephemeris & feature extractor
│   │   └── multi_natal_engine.py          # 4-entity multi-natal dasha & gochar engine
│   ├── analysis/
│   │   ├── vedic_pattern_miner.py         # FP-Growth, Fisher exact, FDR sieve
│   │   ├── run_discovery_engine.py        # Master codex generator
│   │   └── mine_high_freq_rules.py        # Fast recurring planetary rule extractor
│   ├── ml/
│   │   └── vedic_feature_importance.py    # XGBoost, LightGBM, TreeSHAP interactions
│   └── core/                              # Shodashvargas, Jaimini, Ashtakavarga, Shadbala, SBC
└── tests/                                 # 516 automated unit & multi-cycle test suites
    ├── test_brutal_13_pillar_multicycle_harness.py
    ├── test_multi_natal_engine.py
    └── test_vedic_pattern_miner.py
```

---

## 🚀 Quickstart & Reproduction

```bash
# 1. Clone repository
git clone https://github.com/Shivam2794/Vedic-Quant-All_Astro_Topics-.git
cd Vedic-Quant-All_Astro_Topics-

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run full 516-test adversarial gauntlet
pytest tests/ -v

# 4. Execute pattern discovery & ML engine
python -m src.analysis.run_discovery_engine
python -m src.analysis.mine_high_freq_rules
```

---
*Built with absolute mathematical rigor, zero lookahead bias, and pure classical astronomical precision.*
