# Brutal Inspection Report: V10 Apex (Audit 2)

**Grade:** FAILED

**Critical Flaws (Must Fix):**
1. **Missing CPPI Ratchet Reset (Drawdown Governor):** 
   * **Location:** Lines 103-105.
   * **Flaw:** When `nav > prev_high`, the state updates `prev_high = nav` and `days_below_hwm = 0`, but crucially FAILS to reset `curr_floor = 0.86`. Because the regeneration clause lowers `curr_floor` when `days_below_hwm > 60` to prevent cash-lock, the floor permanently ratchets down to 0.83 over the backtest. Once it drops, it never recovers to the intended 14% hard floor. Fable's CPPI ratchet reset bugfix was NOT implemented.

2. **Yield Gap Mismatch in Margin Execution:** 
   * **Location:** Lines 94-97.
   * **Flaw:** Margin borrowing cost is calculated as `cy_arr[i] + (0.015 / 252)`. However, `cy_arr` is scaled by 365 (`(irx_biz / 100) / 365`). Mixing the 365-day Treasury base yield with a 252-day margin spread artificially inflates the daily margin penalty. The math is mathematically disjointed and overcharges the portfolio. It must be `(0.015 / 365)` to align with the yield gap physics.

3. **Alpha Inversion / Logic Mismatch in GLD Trend:** 
   * **Location:** Line 54 vs docstring.
   * **Flaw:** The strategy explicitly dictates a `10/100 trend` for GLD (matching SPY), but the implementation erroneously uses an Exponential Moving Average: `gld_c.ewm(alpha=0.15, adjust=False).mean() > gld_c.rolling(100).mean()`. This is an EMA-SMA mismatch ("alpha inversion") and explicitly violates the stated 10-day SMA physics.

**Structural Weaknesses:**
- The `valid_idx` offset uses `[250:-1]`. The `-1` arbitrarily truncates the final day of the dataset. For exact Mode B physics, truncating the final signal means we miss the final execution step.
- `btc_w` is calculated by shifting `btc_raw` *before* reindexing to the business calendar. This forces Monday's signal to rely on Sunday's Close, breaking the symmetrical 1-bar execution lag applied to GLD and SPY. 

**Micro-Optimizations:**
- Hardcoding `slip_cost` inside the loop initialization is brittle.
- `np.maximum.accumulate` is used for drawdown, but `cum` is calculated on `(1 + port_ret)`. It is correct, but computing Sharpe based on `excess` without dynamically vectorizing `cy_arr * delta_days` strictly can cause array mismatch if indices shift.

**Final Verdict:** REJECTED. The Fable bugfixes and cash yield gap fixes were NOT successfully integrated. The matrix bounds are leaking. Activate repair sequence immediately.
