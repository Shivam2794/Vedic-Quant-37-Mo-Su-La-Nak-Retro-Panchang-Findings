
import os

master_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\NotebookLM_Master_Knowledge_Base.md"

critique8 = """
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
"""

try:
    with open(master_path, 'a', encoding='utf-8') as f:
        f.write(critique8)
    print("Successfully appended Phase 3 Traps A-F to NotebookLM Master Knowledge Base.")
except Exception as e:
    print(f"Error: {e}")
