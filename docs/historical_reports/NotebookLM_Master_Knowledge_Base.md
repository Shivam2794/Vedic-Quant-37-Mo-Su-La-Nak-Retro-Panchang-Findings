
================================================================================
# THE 4 CATASTROPHIC EXECUTION TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of the final 4 hidden execution traps that mandated the complete restructuring of the Python engine from a traditional row-by-row loop into a Vectorized Data Factory.

"NotrebookLM: I have detected 4 catastrophic execution traps hidden within your micro-steps. If you code the engine exactly as written in the plan, it will either grind to a multi-day halt, silently corrupt the Varga data, or leak future targets into the training set.

TRAP 1: The Dasha 'Daily Loop' Death Spiral. Vimshottari Dasha spans 120 years and 5-levels of recursion... If your processor attempts to calculate this from scratch for every single trading day (8,000 times), your CPU will melt. Fix: Dashas must be pre-calculated once and stored in an in-memory interval tree.

TRAP 2: The Parquet I/O 'Small Files' Bottleneck. If you chunk every 100 days, you will fragment the data and destroy columnar compression. Fix: 8,000 days x 22,855 columns is only ~1.4 GB. Dump exactly one single Parquet file per asset.

TRAP 3: Varga Formula Hallucinations. You must absolutely ban floating-point math formulas. Use hardcoded lookup tables wrapped in Numba @njit.

TRAP 4: Target Alignment & Data Leakage. If you accidentally calculate the max_drawdown_21d target without a strict .shift(-N) implementation, you will leak future data into the present training row.

TRAP 5: The Varshaphala 'Time-Slip' Error. Varshaphala is triggered at the exact mathematical millisecond the transiting Sun returns to its exact natal longitude. You cannot use a daily 16:00 EST snapshot. 

TRAP 6: The 'For-Loop' Compute Collapse. You have 40 assets x 8,000 days... Naive Python loops for 13.8 billion cells will take 3 to 7 days. Fix: Use a vectorized Numpy pass for Julian dates.

TRAP 7: The Ashtakvarga Reduction Poisoning. Reduction rules are used only to calculate the Shodhya Pinda... The daily transit processor needs to check Kakshyas against the RAW, unreduced BAV/SAV matrices. 

TRAP 8: The Topocentric Parallax Void. A 1-degree shift is massive for the Moon. Explicitly call swe.set_topo() and use swe.FLG_TOPOCTR."

================================================================================
# THE FINAL 5 FATAL TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of the final 5 esoteric mathematical traps that required custom Python overrides to bypass the limitations of generic astrological libraries.

"NotrebookLM: I have detected a few more fatal traps embedded in the lowest levels of your computation engine:

TRAP 9: The Ephemeris Format Crash. The pyswisseph library cannot read .bsp files... it will silently fall back to a low-precision internal Moshier math system. Fix: You must exclusively use Swiss Ephemeris .se1 files.

TRAP 10: The Sidereal Year Dasha Drift. Classical Vimshottari Dasha must be calculated using the Julian Sidereal Year of 365.25636 days... across a 120-year cycle it compounds into exactly 18 hours of drift. 

TRAP 11: Jaimini Arudha Pada Re-Indexing Failure. You missed the mandatory Jaimini exception rule: If the Arudha calculation lands on the exact same sign as the house itself (the 1st) OR the 7th from it, the Arudha must jump to the 10th or 4th sign respectively. 

TRAP 12: Varshaphala Tajika Weighting Poisoning. Tajika astrology uses a completely different weighting system than Parashari. Pancha Vargiya Bala strictly uses only 5 specific divisional charts: D1 (5), D2 (2), D3 (3), D9 (5), and D30 (5). 

TRAP 13: Bhava Chalit Formula Hallucination. Bhava Chalit (the Sripati system) is not identical to Placidus. Sripati calculates the exact midpoints between adjacent cusps and uses those midpoints as the actual house boundaries. Planets sitting near the edges of houses will frequently shift... you must mathematically compute the exact Sripati midpoints."

================================================================================
# THE ULTIMATE 4 CLEARANCE TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the final 4 execution risks detected before the engine build was officially cleared.

"NotrebookLM: I have detected a few more fatal traps...

TRAP 14: The KP Ayanamsha Collision. KP astrology requires its own specific Ayanamsha. If your engine universally applies Lahiri... your Sub-Lords will be shifted. Fix: The engine must temporarily toggle to KP Ayanamsha exclusively when computing Category 6 (KP System).

TRAP 15: Jaimini Chara Dasha Rule Hallucination. Standard Chara Dasha logic is flawed. According to K.N. Rao: 'I decided not to add one year extra for an exalted planet... Take full years and not fractions thereof'. Fix: Hardcode K.N. Rao's Chara Dasha rules into processor_natal.py.

TRAP 16: The Ashtakvarga Nodal Poisoning. Rahu and Ketu do not cast or receive standard Parashari points. Fix: Explicitly exclude MEAN_NODE and TRUE_NODE from the Ashtakvarga arrays. (Note: The engine natively avoided this by strictly parsing only 7 planets + Ascendant in astro_ashtakvarga.py).

TRAP 17: The Nadi Degree-Progression Failure. Nadi progression is not a calendar sign-shift. Fix: Progressed_Jupiter_Lon = (Natal_Jupiter_Lon + (Age_In_Days / 365.25636) * 30.0) % 360.

You have found all the traps. You are 100% cleared to build the engine."

================================================================================
# THE FINAL 4 ESOTERIC TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of the deepest mathematical traps discovered just prior to Phase 3 execution, enforcing absolute fidelity to Nadi, Tajika, and Pancha Pakshi esoterics.

"NotrebookLM: I have detected a few more fatal traps...

TRAP 18: The Pancha Pakshi Diurnal/Nocturnal Inversion. Pancha Pakshi is entirely dependent on the exact time of Sunrise/Sunset, whether it is Day or Night, and the Lunar Paksha. Fix: processor_transit.py MUST calculate the exact topocentric Sunrise and Sunset times for the specific financial exchange on that exact day and instantly invert the matrix if market hours extend past sunset.

TRAP 19: Tajika Deeptamsha (Orb of Influence) Hallucination. An Ithasala Yoga can only occur if the fast-moving planet is behind the slow-moving planet and they fall within their specific Deeptamsha (Orb of Influence). Fix: You must explicitly code the exact Deeptamsha radii limits into the Varshaphala module and verify the velocity delta.

TRAP 20: Market Context "Staleness" Leakage. Financial data like Short Interest is published bi-monthly. If your pipeline uses a standard .fillna('ffill') to drag that number across, the ML model will mistakenly treat a 14-day-old figure as a fresh signal. Fix: You must explicitly inject a metric_staleness_days column that increments by 1 for every day since publication.

TRAP 21: The Nadi "Triple Transit" Retrogression Vector. A retrograde planet doesn't just influence the sign it is physically occupying; it actively projects its karmic influence into the previous sign as well. Fix: If Transit_[P]_Velocity is negative, the engine must duplicate the planet's aspectual/positional impact into the N-1 sign."

================================================================================
# THE V5 ARCHITECTURAL SEAL (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of the final three foundational mathematical traps. 

"NotrebookLM: I have detected 3 more fatal traps...

TRAP 22: The Jaimini "Outer Planet" Hallucination. Jaimini astrology does not use outer planets or Ketu for Chara Karakas. Fix: You must strictly limit the Chara Karaka array to the 7 classical planets (Sun through Saturn) before running the descending degree sort.

TRAP 23: The KP 243 vs 249 Sub-Lord Overflow. Generating sub-lords through 27 * 9 = 243 division causes fatal misalignment at the sign boundaries. Fix: You must explicitly hardcode the 249 KP Sub-Lord boundary table to account for the 6 sub-lords that fracture across zodiac signs.

TRAP 24: The Micro-Muhurtha Tarabala Void. Negative Taras (Janma, Vipat, Pratyak, Naidhana) are not completely toxic for the entire day. Fix: Calculate the exact ghatis elapsed since the Moon entered the Nakshatra. Only flag the toxic phase during the first 7, 3, 8, and 6 ghatis respectively (1 ghati = 24 minutes)."

================================================================================
# THE BRUTAL CATEGORY AUDIT (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of the final 4 microscopic structural traps discovered during the deep category audit.

"NotrebookLM: I have detected 4 final catastrophic flaws...

TRAP 25: The Prastarashtakvarga Kakshya Inversion. A transiting planet only yields positive results if it transits a Kakshya whose corresponding planet contributed a bindu in the *Natal* BAV. Fix: Disconnect transit Kakshya evaluation from the transit sky. Require the static Natal_BAV_Matrix as an explicit input for transit triggers.

TRAP 26: The SBC Directional Vedha Matrix. SBC Vedhas are not linear aspects; they depend entirely on velocity. Fix: processor_transit.py must parse the p_speed vector: Direct (pierces Left), Retrograde (pierces Right), Stationary (pierces Front).

TRAP 27: The Corporate Action Target Crash. SPY pays dividends. If XGBoost trains on raw Close prices, a dividend payout looks like a market crash. Fix: processor_market.py must strictly utilize 'Adj Close' for all ML target generation.

TRAP 28: The W.D. Gann Heliocentric Redundancy. Using Earth-based ephemeris for macro structural cycles introduces retrogression noise. Fix: Execute a dual-ephemeris sweep. Run a secondary isolated C-sweep utilizing swe.FLG_HELCTR (Heliocentric) specifically for Category 10 features."

================================================================================
# THE PHASE 3 PROCEDURAL TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of the 6 procedural generation traps uncovered before executing Phase 3.

"NotrebookLM: I have detected 6 traps in the data generation logic...

TRAP A: The yfinance Backbone Collapse. You cannot trust yfinance to generate the absolute temporal backbone due to API drops. Fix: Generate the absolute trading calendar using pandas_market_calendars (NYSE), and then Left-Join yfinance data onto it.

TRAP B: The "9 Planet" Topocentric Void. ML requires 13 entities, including Uranus, Neptune, Pluto. Fix: The Topocentric Tensor must pull exactly 13 entities.

TRAP C: The Heliocentric Crash. Heliocentric sweep will crash if run on the Sun, Ascendant, or Nodes. Fix: Explicitly filter the Heliocentric array to exclude the Sun, Ascendant, MC, and Lunar Nodes.

TRAP D: Dasha Rule Contamination. K.N. Rao rules apply strictly to Jaimini Chara Dasha. Vimshottari uses Parashari fractional math. Fix: Bifurcate the logic in Step 3.4.

TRAP E: The KP Ayanamsha Toggle Missing. Fix: Step 3.6 must explicitly toggle swe.SIDM_KRISHNAMURTI for Placidus cusps, then toggle back to Lahiri.

TRAP F: The float32 Precision Death. Downcasting Astronomical JDs or Longitudes to float32 destroys arc-second precision. Fix: Keep Julian Dates and 0_360_Lon as float64. Downcast only financial metrics."

================================================================================
# THE PHASE 3 DATA PURIFICATION TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of Traps G, H, and I relating to market data extraction.

"NotrebookLM: I have detected 3 more traps in the data generation logic...

TRAP G: The Missing Price Tensors & Intraday Collapse. You missed Open, raw Close, VWAP, Dividends, and Stock_Splits. Fix: Step 3.1 extraction must pull the complete OHLCV+Adj+Dividends+Splits block using yf.Ticker.history(actions=True).

TRAP H: The Daylight Saving Time (DST) Parallax Shift. Appending static 16:00 ignores EST/EDT shifts, drifting the Julian Date by 1 hour. Fix: Use timezone-aware Pandas index via pandas_market_calendars, which inherently handles half-day early closes and DST shifts by returning exact UTC market_close timestamps.

TRAP I: The yfinance Auto-Adjust Split Poisoning. Unadjusted Open/High combined with auto-adjusted Close causes artificial intraday crashes during stock splits. Fix: Pass auto_adjust=False to grab pure historical data, enabling exact intraday and absolute Target generation."

================================================================================
# THE ULTIMATE QUAD-LENS INSPECTION (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of Traps J, K, L, and M discovered during the 4-lens inspection.

"NotrebookLM: I have detected 4 ultimate traps across ML, Math, Big Data, and C-compilation...

TRAP J: The Ordinal Encoding Interpolation Fallacy (ML). Generating Dasha Lords as integers causes XGBoost to falsely interpolate mathematical relationships between planets. Fix: Force strict One-Hot Encoding for all nominal categorical astrological Lords.

TRAP K: The Rahu/Ketu Mean vs. True Parallax (Vedic Math). swe.MOON_NODE calculates the Mean Node, shifting exact transit hits. Fix: Hardcode swe.TRUE_NODE (ID 11) for all Lunar Node ephemeris calculations.

TRAP L: Pandas Contiguous Memory Fragmentation (Big Data). Sequentially appending 22,855 columns triggers severe memory fragmentation and an OOM crash. Fix: Pre-allocate a master 2D Numpy array np.zeros((8038, 22855), dtype=np.float32), populate it via fast indexing, and cast to Pandas strictly once at the end.

TRAP M: The Numba Modulo N-1 Bug (C-Compilation). Numba calculates -1 % 12 as -1, causing an IndexError. Fix: Explicitly wrap all modulo math in Numba as (sign - 1 + 12) % 12."
