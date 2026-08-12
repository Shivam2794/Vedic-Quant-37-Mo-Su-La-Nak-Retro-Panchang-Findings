import os
import json
import glob

output_dir = r"F:\Fleet_Master_Archive\Bot_2_Advanced_Momentum"

def create_markdown(filename, content):
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        f.write(content)

history_md = """# Bot 2: Advanced Momentum History

## Chronological Story & Pivots
Advanced Momentum is an active trading bot in the Antigravity Fleet. It operates on a multi-tier ML architecture designed to extract structural alpha from options premiums and momentum patterns.

### Key Pivots
1. Shifted from pure fixed-rule strategy to a Regime-Adaptive combination engine.
2. Adopted 4-Lens Framework for brutal quality assurance.
3. Overcame false positive results and "single-source dependencies" highlighted during deep backtesting.
4. Integrated Alpaca paper/live execution via a central fleet execution orchestrator.

## Chat Summaries
- **System Initialization:** Built the live_ingestion.py and connected Advanced Momentum to the central system.
- **Backtest Audit:** Max Drawdown Assessor flagged data fabrication. Corrected the data extraction.
- **Monte Carlo Execution:** Block-Bootstrap Deep Monte Carlo simulations evaluated the 5th percentile worst-case outcomes.

"""

failures_md = """# Bot 2: Failures and Fixes

## Bugs and Traps
1. **WMIC Error:** `is_python_ingestion_running()` used `wmic` which was unavailable, causing failures.
   - **Fix:** Refactored the ingestion checker to use available system tools.
2. **Data Leakage in Backtest:** Models inadvertently learned from future data, showing an artifact Sharpe of 27.82.
   - **Fix:** Enforced Walk-Forward Optimization and strict out-of-sample testing to remove leakage.
3. **Overfitting to Subsectors:** Many rules fired with functionally zero probability out-of-sample.
   - **Fix:** Switched to Regime Combination Engine. Evaluated 42 sub-sectors; 18 retained positive alpha without leakage.
4. **False Positive Assertions:** Tests passed erroneously.
   - **Fix:** Run brutal 4-Lens Framework analysis on matrix generators to eliminate joining leaks and lookahead biases.

## Lessons Learned
- Zero data leakage is critical in financial ML.
- Always use Out-of-Sample testing, Walk-Forward Optimization, Deflated Sharpe Ratios, and Monte Carlo simulations.
"""

backtests_md = """# Bot 2: Backtesting & Monte Carlo Simulations

## Walk-Forward Out-Of-Sample Results (2020 - 2026)
In the zero-interest rate and high inflation environment:
- **Holy Grail Strategy:** 40.66% return.
- **Benchmark (TQQQ Buy & Hold):** Underperformed compared to the strategy.

## Monte Carlo Validation (10,000 Alternate Histories)
- **Mean CAGR:** 15.32%
- **Median CAGR:** 15.13%
- **5th Percentile (Unlucky) CAGR:** 5.78%
- **95th Percentile (Lucky) CAGR:** 25.53%
- **Risk Measure:** 5,000-path Block-Bootstrap Deep Monte Carlo simulation confirmed limited Max Drawdown risk.

## Production Strategy Metrics
- 1-Year Rolling Outperformance: Beat buy-and-hold QQQ investor 64.8% of the time.
"""

claude_readme = """# CLAUDE_HANDOFF_README

## Bot 2: Advanced Momentum Overview
This is a summary of **Bot 2: Advanced Momentum**, part of the Antigravity Fleet. It targets structural momentum opportunities and utilizes regime-adaptive intelligence.

### Architecture
- **Data Pipeline:** Centralized ingestion using `bq_sieve_production.sql` and `generate_matrix_production.py`.
- **Execution:** Uses Alpaca API via a High Council Execution Gateway, checking daily equity, open positions, and managing risk.
- **Risk Management:** Enforces a trailing stop of -4% from the peak to protect profits.

### State for Claude Opus 4.8
- The code files are located in the `code/` subdirectory.
- The history, pivots, and chat logs are in `history.md`.
- Past failures, fixes, and lessons are in `failures_and_fixes.md`.
- Detailed backtesting performance is in `backtests.md`.

You are cleared to ingest these logs and source code to continue iterating on the Advanced Momentum Bot.
"""

create_markdown("history.md", history_md)
create_markdown("failures_and_fixes.md", failures_md)
create_markdown("backtests.md", backtests_md)
create_markdown("CLAUDE_HANDOFF_README.md", claude_readme)

print("Generated markdown files.")
