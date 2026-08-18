# 🪐 Vedic Quant Matrix: Complete 13-Pillar Astrological & Machine Learning Trading System

[![Tests](https://img.shields.io/badge/Pytest-574%2F574%20Passing-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Ephemeris](https://img.shields.io/badge/Ephemeris-Swiss%20Ephemeris%20(Sidereal%20Lahiri)-orange.svg)](https://www.astro.com/swisseph/)
[![Features](https://img.shields.io/badge/Omni--Vedic%20Matrix-1%2C032%20Dual--Anchor%20Features-purple.svg)](data/)
[![Integrity](https://img.shields.io/badge/Mathematical%20Integrity-100%25%20Verified%20(0%20NaNs)-gold.svg)](reports/)

An institutional-grade, mathematically verified quantitative research framework uniting **Classical Vedic Astrological Mechanics (Jyotish)**, **Swiss Ephemeris Topocentric Astronomy**, and **Adversarial Machine Learning** to model and predict extreme single-candle volatility shocks and sustained multi-candle trend waves in the **SPY ETF (S&P 500)**.

---

## 🌊 FRONTIER 1: MULTI-CANDLE TREND WAVE ENGINE (NEW)

> **Dedicated Module Directory**: [👉 `frontier_1_trend_waves/`](frontier_1_trend_waves/)

Frontier 1 expands the system beyond isolated single-candle anomalies to extract and model sustained **multi-candle trend waves** across all 6 timeframes (**1H, 2H, 4H, 1D, 1W, 1MO**) in SPY (1993–2026).

### Key Frontier 1 Capabilities:
* **Non-Lookahead Dynamic ATR ZigZag**: Volatility thresholds shifted by $\text{ATR}(20)_{t-1}$.
* **Perry Kaufman's Efficiency Ratio (KER)**: Quantifies directional displacement against total path length ($\text{KER} \ge 0.50$).
* **Dual-Anchor Omni-Vedic Matrix (1,032 Features)**: Captures exact planetary states at both **Wave Inception ($T_{\text{start}}$)** and **Wave Climax ($T_{\text{climax}}$)** plus intra-wave transit kinematics.
* **Master Codex Deliverable**: [👉 `frontier_1_trend_waves/reports/vedic_trend_wave_codex.md`](frontier_1_trend_waves/reports/vedic_trend_wave_codex.md).

### Top Verified Macro Trend Movers (FDR $q < 0.05$, Laplace Lift $\ge 1.60\text{x}$):
| Direction | Planetary Signature (Inception Trigger) | N | Win Rate | Laplace Lift | FDR q-val | Avg Move |
| :---| :---| :---: | :---: | :---: | :---: | :---: |
| **🐂 Bull Thrust** | `[Mars in 1st to Rahu] ∧ [AmK is Jupiter]` | 19 | **100.0%** | **2.23x** | `0.0000` | **+8.44%** |
| **🐂 Bull Thrust** | `[Moon in P.Phalguni] ∧ [DK is Venus]` | 17 | **100.0%** | **2.22x** | `0.0000` | **+7.64%** |
| **🐂 Bull Thrust** | `[AmK is Jupiter] ∧ [KP Mars Star is Jupiter]` | 16 | **100.0%** | **2.21x** | `0.0000` | **+9.67%** |
| **🐂 Bull Thrust** | `[Mars in P.Bhadrapada] ∧ [Venus in 12th to Saturn]` | 14 | **100.0%** | **2.20x** | `0.0001` | **+10.50%** |
| **🩸 Bear Crash** | `[Mercury in Ashlesha Nakshatra (Gandanta)]` | 13 | **100.0%** | **1.67x** | `0.0059` | **-5.61%** |
| **🩸 Bear Crash** | `[Venus in Pushya] ∧ [Mercury in Cancer]` | 13 | **100.0%** | **1.67x** | `0.0059` | **-5.01%** |
| **🩸 Bear Crash** | `[Sun in 7th to Rahu] ∧ [Venus in Capricorn]` | 11 | **100.0%** | **1.65x** | `0.0059` | **-6.04%** |
| **🩸 Bear Crash** | `[Venus in 7th to Rahu] ∧ [Sun in 7th to Rahu]` | 10 | **100.0%** | **1.64x** | `0.0077` | **-7.32%** |

---

## 🏛️ System Architecture: The 13 Classical Vedic Pillars

Every timestamp across the historical dataset is mapped to **deep continuous and discrete astronomical features** across 13 distinct classical domains:

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

---

## 📊 Dataset Demographics & Manifest

All datasets are saved in binary columnar Parquet and CSV formats in `data/`:

| Dataset | Granularity | Rows | Columns | Verified Invariants |
| :---| :---: | :---: | :---: | :---|
| `spy_trend_waves_omni_vedic_supreme.parquet` | Multi-TF Waves (1H..1MO) | **522** | **1,032** | $\sum \text{SAV} \equiv 337$, Jaimini 1-to-1, 0 NaNs |
| `spy_anomalies_omni_vedic_supreme.parquet` | Single Candles (1H..1MO) | **1,408** | **543** | $\sum \text{SAV} \equiv 337$, Jaimini 1-to-1, 0 NaNs |
| `raw_spy_1h_unified_2008_2026.parquet` | 1-Hour SPY Bars | **30,240** | **8** | Continuous RTH Alignment (9:30–16:00 EST) |

---

## 🚀 Quickstart & Pipeline Execution

```bash
# 1. Clone the repository
git clone https://github.com/Shivam2794/Vedic-Quant-All_Astro_Topics-.git
cd Vedic-Quant-All_Astro_Topics-

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Frontier 1 Trend Wave Engine & Pattern Miner
python -m src.analysis.trend_wave_engine
python -m src.analysis.enrich_trend_waves
python -m src.analysis.mine_trend_wave_rules

# 4. Run the Full Test Gauntlet (574 passing tests)
pytest tests/ -v
```

---

## 🧪 Comprehensive Automated Test Suites

```bash
pytest tests/ -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.12.9, pytest-9.0.3
rootdir: Vedic-Quant-All_Astro_Topics-
collected 574 items

tests/test_brutal_13_pillar_multicycle_harness.py ......................... [ 11%]
tests/test_multi_natal_engine.py .......................................... [ 22%]
tests/test_omni_vedic_fusion.py ........................................... [ 47%]
tests/test_trend_wave_engine.py ........................................... [ 57%]
tests/test_vedic_ephemeris_engine.py ...................................... [ 80%]
tests/test_vedic_ml_engine.py ............................................. [ 89%]
tests/test_vedic_pattern_miner.py ......................................... [100%]

======================= 574 passed in 65.72s (0:01:05) ========================
```

---
*Maintained with mathematical rigor by the Vedic Quant Architecture System.*
