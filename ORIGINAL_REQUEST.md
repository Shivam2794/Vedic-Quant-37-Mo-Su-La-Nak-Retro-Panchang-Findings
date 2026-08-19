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

## Follow-up — 2026-08-17T19:43:58Z

Build an end-to-end Automated Vedic Planetary Pattern Mining, Statistical Significance Sieve, and Machine Learning Discovery Engine on the 1,408 enriched SPY candlestick anomaly dataset (2008–2026) to uncover the exact, statistically verified planetary configurations, aspects, harmonic vargas, karakas, shadbalas, and dasha alignments that move the market.

Working directory: C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings
Integrity mode: development

## Requirements

### R1. Baseline Distribution Generation & Null Hypothesis Calibration
- Ingest a representative control baseline of non-anomaly historical SPY timestamps (e.g. continuous regular trading hours 2008–2026) enriched with the same 397 Omni-Vedic features.
- Establish empirical null distributions for all categorical (signs, nakshatras, padas, vargas, karakas, kakshya lords, dashas) and continuous (angular distances, declinations, speeds, shadbala rupas, SAV points) features.

### R2. Univariate Statistical Significance & Lift Ratio Engine
- For every planetary position and Vedic parameter across Bullish Anomalies, Bearish Anomalies, and Multi-Timeframe Confluences:
  - Calculate Empirical Lift: Lift = P(Feature | Anomaly) / P(Feature | Baseline).
  - Compute two-tailed statistical significance using Fisher's Exact Test / Chi-Square Test (p < 0.01).
  - Apply Benjamini-Hochberg False Discovery Rate (FDR) correction to eliminate false positives and spurious data-mining artifacts across thousands of hypotheses.
  - Perform Kolmogorov-Smirnov (KS) and Mann-Whitney U tests on continuous distributions (e.g., angular separation, planetary speed, Shadbala rupas).

### R3. Higher-Order Combinatorial Pattern Mining (Multi-Planet Confluences)
- Implement frequent pattern and association rule mining algorithms (FP-Growth / Apriori / Decision Tree Rule Extraction) on discrete Vedic states.
- Extract 2-way, 3-way, and 4-way planetary interacting rules (e.g. [Mars 6/8 to Saturn] AND [Moon in Rahu Nakshatra] AND [Lagna = Leo] -> Bearish Crash Probability >= 80%, Lift >= 3.0x, N >= 15).
- Filter rules strictly by: Minimum Support (N >= 10), Minimum Confidence (>= 70%), Lift (>= 2.0x), and p < 0.005.

### R4. Machine Learning Feature Attribution & Interaction Mining
- Train Gradient Boosted Models (XGBoost, LightGBM, CatBoost) and Random Forests to predict:
  1. Directional Class (Extreme Green Bullish Shock vs. Extreme Red Panic Crash).
  2. Anomaly Magnitude (Solid Body / ATR(20) Multiplier).
- Apply TreeSHAP to calculate exact Shapley feature importance rankings across all 397 columns.
- Extract top 20 global driver features and compute pairwise SHAP Interaction Values to identify non-linear astronomical synergies.

### R5. Deep Vedic 10-Pillar Forensic Drilldown
- Perform targeted statistical hypothesis testing across each of the classical pillars:
  - Pillar 1 (Ephemeris): Out-of-bounds declinations (|delta| > 23.44 deg) and planetary stations (Speed approx 0).
  - Pillar 2 (Aspects): Exact orb clustering for Shadashtaka (6/8), Dwirdwadasa (2/12), and Samasaptaka (1/7).
  - Pillar 3 (Vargas): Pushkara Navamsha and Vargottama resonance frequency on breakout days.
  - Pillar 4 (Jaimini): Gnatikaraka (GK - 6th highest degree) activations during crashes vs. Atmakaraka (AK) activations.
  - Pillar 5 (Ashtakavarga): Extreme SAV thresholds (< 25 vs. > 32 bindus) in transited signs.
  - Pillar 6 (Shadbala): High Chesta Bala vs. Low Kala Bala ratio on trend days.
  - Pillar 7 (SBC & Vedha): Malefic Vedha network intensity and Gochar Murti impact.
  - Pillar 8 (KP Sub-Lords): Star Lord / Sub-Lord rulers of NYSE Lagna and 10th/11th cusps.
  - Pillar 9 (NYSE Vimshottari): Mahadasha / Antardasha / Pratyantardasha lord transit triggers.
  - Pillar 10 (MTF Confluence): Astrological signatures of 4-timeframe simultaneous co-occurrences.

### R6. Automated Master Codex of Market Movers & Visualizations
- Generate the executive report vedic_market_movers_codex.md detailing:
  - Top 50 verified, non-spurious planetary rules that move SPY, with sample counts (N), win rate (confidence), lift, p-value, and historical dates.
  - Directional taxonomy separating Pure Bullish Planetary Drivers from Pure Bearish Crash Triggers.
  - Visual summary tables, distribution charts, and actionable quantitative rule definitions.

---

## Acceptance Criteria

### Statistical & Mathematical Rigor
- [ ] Every reported planetary rule or feature must have a calculated Lift Ratio, Sample Size (N >= 10), and FDR-adjusted p-value < 0.01.
- [ ] No self-fulfilling or spurious claims: all anomalies must be rigorously benchmarked against the empirical baseline distribution.
- [ ] ML feature attribution must report Cross-Validated Out-of-Sample AUC-ROC / F1 / Precision metrics with zero data leakage.

### Comprehensive Deliverables
- [ ] Full statistical discovery engine module (src/analysis/vedic_pattern_miner.py) executed cleanly.
- [ ] ML attribution module (src/ml/vedic_feature_importance.py) generating SHAP values and feature rankings.
- [ ] Master findings report (reports/vedic_market_movers_codex.md) published and committed to git branch feat/extreme-solid-candlestick-anomalies.

## Follow-up — 2026-08-18T00:39:46Z

Execute an eternal, continuous multi-agent brutal multipoint inspection and self-correcting development loop across all 13 Vedic astrological pillars, mathematical formulas, ephemeris calculations, and code chunks until achieving a completely error-free cycle with 100% mathematical, canonical, and quantitative integrity.

Working directory: C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings
Integrity mode: development

## Requirements

### R1. Deep Atom-by-Atom Multipoint Forensic Audit of All 13 Astrological Pillars
- Inspect every single line of code, formula, and boundary condition in:
  - src/vedic_astrology/omni_vedic_fusion.py (10-pillar core ephemeris extractor)
  - src/vedic_astrology/multi_natal_engine.py (SPY, USA, Fed, NYSE 4-natal dasha & gochar engine)
  - src/core/astro_vargas.py, jaimini_karakas.py, astro_ashtakvarga.py, shadbala_core.py, vedha_engine.py, kp_ephemeris_module.py
  - src/analysis/vedic_pattern_miner.py, run_discovery_engine.py, mine_high_freq_rules.py
  - src/ml/vedic_feature_importance.py
- Audit the exact mathematical equations and scriptural canonical fidelity across all 13 domains:
  1. Ephemeris & Speeds: Sidereal Lahiri precession, topocentric Wall Street coordinates, planetary stations (Speed ≈ 0), retrograde flags, declinations, OOB (|δ| > 23.44°), combustion orbs, Gandanta boundaries.
  2. Zodiac & Nakshatras: 12 Rasis, 27 Nakshatras, 108 Padas, Pushkara Navamsha/Bhaga, Vargottama invariants.
  3. Harmonic Shodashvargas: Exact division mappings for D1, D9, D10, D60 (including odd vs even sign reverse rules).
  4. Panchanga Limbs: Tithi 12° increments, Vara Chaldean sequence, Nithya Yoga formulas, Karana Vishti/Bhadra triggers, Hora planetary hours.
  5. Bhavas & Angles: Topocentric Lagna, Chandra Lagna, all 66 mutual inter-planetary houses, and exact angular distance arcs (0°..180°).
  6. Parashari Drishti: Full 7th aspect, Mars 4/8, Jupiter 5/9, Saturn 3/10 special aspects, and continuous degree-to-degree orbs.
  7. Ashtakavarga & Kakshyas: BAV bindu allocation, SAV 337 total points invariant across all 12 signs, 8 Kakshya 3°45' partitions.
  8. Shadbala 6-Fold Potencies: Sthana, Dig, Kala, Chesta, Naisargika, Drik Balas, total Rupas, and strength ratios.
  9. Jaimini 7 Karakas: Degrees in sign sorting (excluding Rahu/Ketu), AK, AmK, BK, MK, PK, GK, DK strict 1-to-1 uniqueness.
  10. Sarvatobhadra Chakra: 28-Nakshatra grid with Abhijit, 5 Vedha ray intersections, and Gochar Murti 4-metal allocations.
  11. KP System: Placidus cusp boundaries, 249 sub-lord divisions for Lagna, 10th (MC), and 11th cusps.
  12. Vimshottari Dasha Engine: Sub-second fractional elapsed arc balance at birth, 120-year rolling cycle for MD, AD, and PD.
  13. 4-Entity Multi-Natal Hierarchy: SPY ETF (1993), USA (1776), Fed (1913), NYSE (1792) birth charts, Gochar Bhavas (1..12), Sade-Sati, Kantaka Shani, Ashtama Shani, and multi-entity crisis counts.

### R2. Eternal Self-Correcting Continuous Audit Loop
- Deploy continuous adversarial inspection loops checking for:
  - Numerical instability, division-by-zero, negative square roots, NaN/Inf generation.
  - Lookahead bias & data leakage in rolling baselines and ML preprocessors.
  - Angular degree wrap-around edge cases (0° / 360° boundary jumps).
  - Multi-year robustness and event-time deduplication across all anomaly clusters.
- If ANY error, inconsistency, or logical flaw is detected at ANY point in the inspection, the agent must autonomously rewrite the faulty code, re-execute the test suite, and restart the full inspection cycle from step 1.
- The loop continues grinding indefinitely until a complete, 100% flawless inspection cycle is achieved with ZERO errors, ZERO warnings, and ZERO logic flaws.

### R3. Programmatic Verification & Artifact Publishing
- Execute the full automated pytest suite across all 7 test engines (pytest tests/ -v).
- Re-run the Master Discovery Engine (python -m src.analysis.run_discovery_engine) on the enriched 498-column matrix.
- Generate a comprehensive, line-by-line inspection ledger verifying the mathematical proof of every pillar.
- Commit all verified deliverables cleanly to git branch feat/extreme-solid-candlestick-anomalies.

## Acceptance Criteria

### Mathematical & Astrological Invariants
- [ ] 100% of all 13 Vedic pillars strictly adhere to classical BPHS, Jaimini, C.S. Patel, and KP standards.
- [ ] SAV bindu sum strictly equals 337 across all 12 signs in every row.
- [ ] Jaimini 7-Karaka mapping strictly maintains 1-to-1 uniqueness (no duplicate AK/GK) in every row.
- [ ] Vimshottari MD/AD/PD dasha walkers have zero time drift across 33+ years.
- [ ] Zero NaNs, zero duplicate timestamps, and zero outer-planet leakage across all 498 columns.

### Continuous Loop & Quality Verification
- [ ] Continuous inspection loop runs to completion with a 100% error-free final pass.
- [ ] Full automated test suite (pytest tests/ -v) executes with 100% passing tests (zero failures, zero errors).
- [ ] Full end-to-end discovery engine produces valid, multi-year verified rules with Laplace-smoothed lift and BH-FDR q < 0.05.
- [ ] All code refactors, test scripts, and reports committed to git branch feat/extreme-solid-candlestick-anomalies.

## Follow-up — 2026-08-18T21:29:42Z

Execute an unyielding, continuous multi-agent brutal multipoint inspection and self-correcting development loop across all Frontier 1 (Multi-Candle Trend Wave & Swing Impulse Engine) codes, astrological formulas, and dataset pipelines until achieving an absolute 100% error-free cycle with zero bugs, zero logic gaps, and zero statistical flaws.

Working directory: C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings
Integrity mode: development

## Requirements

### R1. Deep Atom-by-Atom Multipoint Forensic Audit of Frontier 1 Codebase
- Inspect every single line of code, formula, boundary condition, and edge case in:
  1. src/analysis/trend_wave_engine.py:
     - Dynamic ATR ZigZag thresholding: verify prior-bar shift (shift(1)) to guarantee zero lookahead bias.
     - Kaufman Efficiency Ratio (KER): verify bounds (0 <= KER <= 1), path length division-by-zero protection (1e-8), and directional consistency.
     - Wave boundaries: ensure start index < end index, no overlapping or inverted indices, and correct timeframe displacement floors.
     - Volume expansion ratio: verify baseline calculation against prior Volume SMA(20).
  2. src/analysis/enrich_trend_waves.py:
     - Dual-anchor synchronization: verify T_start (Inception) and T_end (Climax) Swiss Ephemeris Julian Date accuracy.
     - Column naming & prefix isolation: verify Inception_ vs Climax_ feature separation across all 543 columns.
     - Astrological invariants: prove sum(SAV) == 337 across all 12 signs in 100% of rows for both Inception and Climax.
     - Jaimini 7-Karaka uniqueness: prove AK != AmK != BK != MK != PK != GK != DK across 100% of rows.
     - Intra-wave transit kinematics: verify lunar degrees traversed (0°..360°), sign ingress counts, and stationary turn counts.
     - Zero NaNs: verify zero missing values across all 1,032 columns.
  3. src/analysis/mine_trend_wave_rules.py:
     - Feature space purity: strictly verify that modern outer planets (Uranus, Neptune, Pluto) are 100% purged from candidate features.
     - Combinatorial indexing: verify 1-way, 2-way, and 3-way feature conjunctions.
     - Contingency table math: verify Fisher's exact 2x2 contingency matrix [[k, N_r - k], [K - k, (N - K) - (N_r - k)]].
     - Benjamini-Hochberg FDR control: verify sorted p-value ranking (p_(i) <= i/m * Q) at q < 0.05.
     - Bayesian Laplace-smoothed lift: verify p_rule = (k + 1)/(N_r + 2) and p_base = (K + 1)/(N + 10).
     - Multi-year & distinct date mandates: verify >= 2 calendar years and >= 3 distinct dates.
  4. reports/vedic_trend_wave_codex.md:
     - Verify markdown table rendering, sample date accuracy, and numerical synchronization with parquet data.
  5. tests/test_trend_wave_engine.py:
     - Verify complete coverage of segmentation, enrichment, invariants, and pattern mining.

### R2. Eternal Self-Correcting Continuous Audit Loop
- Deploy continuous adversarial inspection agents (Reviewers, Challengers, and Forensic Auditor) checking for:
  - Lookahead bias & data leakage.
  - Off-by-one index shifts at session or timeframe boundaries.
  - Division-by-zero, negative square roots, NaN/Inf generation.
  - Astrological coordinate precision and transit boundary stability.
- If ANY error, inconsistency, or logical flaw is detected at ANY point, the builder agent must autonomously rewrite the faulty code, re-execute the full test suite, and restart the full inspection cycle from step 1.
- The loop continues grinding indefinitely until a complete, 100% flawless inspection cycle is achieved with ZERO errors, ZERO warnings, and ZERO logic flaws.

### R3. Automated Test Execution & Git Publication
- Execute the full automated pytest suite (525+ tests) with 100% passing tests (zero failures, zero warnings).
- Re-run the Trend Wave Discovery Engine (python -m src.analysis.mine_trend_wave_rules) and verify report generation.
- Commit and push all verified deliverables cleanly to GitHub.

---

## Acceptance Criteria

### Mathematical & Quantitative Integrity
- [ ] Zero lookahead bias across all wave segmentation and indicator baselines.
- [ ] 100% of rows in spy_trend_waves_omni_vedic_supreme.parquet (522 × 1,032) satisfy sum(SAV) == 337 and Jaimini 1-to-1 uniqueness.
- [ ] Zero NaNs, zero duplicate wave IDs, zero outer planet leakage.
- [ ] All reported rules in vedic_trend_wave_codex.md have BH-FDR q < 0.05, support N >= 8, confidence >= 68%, and multi-year spans.

### Multi-Agent Inspection & Quality Bar
- [ ] Continuous inspection gauntlet runs to completion with a 100% error-free final pass.
- [ ] Full automated test suite (pytest tests/ -v) executes with 100% passing tests (zero failures, zero errors, zero warnings).
- [ ] All deliverables committed and pushed cleanly to git repository.



## Follow-up — 2026-08-19T02:15:06.224100+00:00

<USER_REQUEST>
Execute an unyielding, continuous multi-agent brutal multipoint inspection and self-correcting development loop across all Frontier 2 (Forward 2026–2027 Ephemeris Calendar & Predictive Signal Scanner) and Frontier 3 (Institutional Quant Backtester & Strategy Simulator) codes, astrological formulas, risk formulas, friction models, and portfolio accounting pipelines until achieving an absolute 100% error-free cycle with zero bugs, zero logic gaps, and zero statistical flaws.

Working directory: C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings
Integrity mode: development

## Requirements

### R1. Deep Atom-by-Atom Multipoint Forensic Audit of Frontier 2 Codebase
- Inspect every single line of code, formula, boundary condition, and edge case in:
  1. src/calendar/forward_ephemeris_engine.py & frontier_2_forward_scanner/src/forward_ephemeris_engine.py:
     - NYSE trading day generation: verify complete exclusion of all weekends and official US market holidays (2026 & 2027).
     - RTH session timestamps: verify correct America/New_York localization and UTC conversion (09:30, 10:30, 11:30, 12:30, 13:30, 14:30, 15:30 EST/EDT).
     - Swiss Ephemeris Julian Date calculation: verify sub-second precision.
     - Astrological invariants: prove sum(SAV) == 337 across all 12 signs in 100% of forward timestamps (3,514/3,514).
     - Jaimini 7-Karaka uniqueness: prove AK != AmK != BK != MK != PK != GK != DK across 100% of forward rows.
     - Zero NaNs: verify zero missing values across all 512 columns.
  2. src/calendar/forward_signal_scanner.py & frontier_2_forward_scanner/src/forward_signal_scanner.py:
     - Feature space parity: verify forward candidate discrete features exactly match the training representation in mine_trend_wave_rules.py.
     - Rule parsing & template matching: verify multi-antecedent conjunction logic (all(feat_matrix[i, idx] for idx in indices)).
     - Confluence scoring & classification: verify directional classification (Bullish_Inception, Bearish_Liquidation, Conflict, Equilibrium).
     - Output datasets: verify data/forward_signals_2026_2027_manifest.parquet and reports/forward_2026_2027_astro_quant_calendar.md.
  3. tests/test_frontier_2_forward_scanner.py:
     - Verify complete coverage of holiday exclusion, RTH session hours, invariants, and signal scanner output.

### R2. Deep Atom-by-Atom Multipoint Forensic Audit of Frontier 3 Codebase
- Inspect every single line of code, formula, boundary condition, and edge case in:
  1. src/backtest/performance_metrics.py & frontier_3_backtester/src/performance_metrics.py:
     - Sharpe Ratio & LPM2 Sortino Ratio: verify annualization factor sqrt(252), downside deviation thresholding, and risk-free rate adjustment.
     - Maximum Drawdown (MDD): verify high-water mark tracking and duration calculations.
     - Calmar Ratio: verify division by zero protection and CAGR alignment.
     - Probabilistic Sharpe Ratio (PSR): verify Marcos López de Prado asymptotic standard error with skewness and kurtosis adjustments.
     - Trade Expectancy: verify decoupled win/loss probability handling for scratch trades (R=0).
     - Monte Carlo Resampling: verify bootstrap permutation math, isolated RNG seeds, and percentile ranking (5th, 50th, 95th).
  2. src/backtest/backtest_engine.py & frontier_3_backtester/src/backtest_engine.py:
     - Execution timing: verify Next-Bar Open fill and zero lookahead bias (T_fill > T_signal).
     - Transaction friction: verify Interactive Brokers commission (.005/share, .00 min) and dynamic slippage (.01/share) deductions across 100% of trades.
     - Ashtakavarga dynamic position sizing: verify SAV bindu strength multipliers (0.75x ... 1.25x) and maximum position cap (25% of equity).
     - Macro regime breakdown: verify accurate historical date partitions (1993–2026) reconciling 100% of trades.
  3. tests/test_frontier_3_backtester.py:
     - Verify complete coverage of metric calculations, drawdown series, Monte Carlo stability, and backtest execution.

### R3. Eternal Self-Correcting Continuous Audit Loop
- Deploy continuous adversarial inspection agents (Reviewers, Challengers, and Forensic Auditor) checking for:
  - Timezone shift / DST ambiguity errors between EDT and EST.
  - Numerical instability, division-by-zero, negative equity, NaN/Inf generation.
  - Lookahead bias & data leakage in signal, ephemeris, and fill timestamps.
  - File parity between root src/ / tests/ / reports/ and dedicated frontier_2_forward_scanner/ & frontier_3_backtester/ packages.
- If ANY error, inconsistency, or logical flaw is detected at ANY point, the builder agent must autonomously rewrite the faulty code, re-execute the full test suite, and restart the full inspection cycle from step 1.
- The loop continues grinding indefinitely until a complete, 100% flawless inspection cycle is achieved with ZERO errors, ZERO warnings, and ZERO logic flaws.

### R4. Automated Test Execution & Git Publication
- Execute the full automated pytest suite (684+ tests) with 100% passing tests (zero failures, zero warnings).
- Re-run the Forward Scanner and Institutional Backtester and verify report generation.
- Commit and push all verified deliverables cleanly to GitHub.

---

## Acceptance Criteria

### Mathematical & Quantitative Integrity
- [ ] 100% of NYSE trading sessions in 2026–2027 are strictly valid RTH market hours without holiday or weekend contamination.
- [ ] 100% of rows in forward_ephemeris_2026_2027_supreme.parquet satisfy sum(SAV) == 337 and Jaimini 1-to-1 uniqueness.
- [ ] Zero lookahead bias across all trade signal, ephemeris, and execution events.
- [ ] 100% of trades have realistic commissions and slippage deducted from net PnL.
- [ ] Cash equity curves and capital compounding are strictly positive and non-explosive.
- [ ] All reported backtest metrics in frontier_3_institutional_backtest_ledger.md match exact underlying trade manifests.

### Multi-Agent Inspection & Quality Bar
- [ ] Continuous inspection gauntlet runs to completion with a 100% error-free final pass.
- [ ] Full automated test suite (pytest tests/ -v) executes with 100% passing tests (zero failures, zero errors, zero warnings).
- [ ] All deliverables committed and pushed cleanly to git repository.
</USER_REQUEST>