
import os

master_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\NotebookLM_Master_Knowledge_Base.md"

critique9 = """
================================================================================
# THE PHASE 3 DATA PURIFICATION TRAPS (NOTEBOOK LM / ARCHITECT DIRECTIVE)

This section contains the detection of Traps G, H, and I relating to market data extraction.

"NotrebookLM: I have detected 3 more traps in the data generation logic...

TRAP G: The Missing Price Tensors & Intraday Collapse. You missed Open, raw Close, VWAP, Dividends, and Stock_Splits. Fix: Step 3.1 extraction must pull the complete OHLCV+Adj+Dividends+Splits block using yf.Ticker.history(actions=True).

TRAP H: The Daylight Saving Time (DST) Parallax Shift. Appending static 16:00 ignores EST/EDT shifts, drifting the Julian Date by 1 hour. Fix: Use timezone-aware Pandas index via pandas_market_calendars, which inherently handles half-day early closes and DST shifts by returning exact UTC market_close timestamps.

TRAP I: The yfinance Auto-Adjust Split Poisoning. Unadjusted Open/High combined with auto-adjusted Close causes artificial intraday crashes during stock splits. Fix: Pass auto_adjust=False to grab pure historical data, enabling exact intraday and absolute Target generation."
"""

try:
    with open(master_path, 'a', encoding='utf-8') as f:
        f.write(critique9)
    print("Successfully appended Phase 3 Traps G-I to NotebookLM Master Knowledge Base.")
except Exception as e:
    print(f"Error: {e}")
