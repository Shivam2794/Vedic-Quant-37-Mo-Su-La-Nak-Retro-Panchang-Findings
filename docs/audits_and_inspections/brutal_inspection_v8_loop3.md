# BRUTAL INSPECTION REPORT: OMNI-ALLOCATOR V8 (LOOP 3/5)

**STATUS: FAILED**

## ADVERSARIAL AUDIT FINDINGS

### 1. NATIVE 365-DAY MOVING AVERAGES & NAN DROPPING: FAILED ❌
**The Flaw:** 
```python
close_prices = df_raw['Close']['BTC-USD'].dropna()
```
You are using `.dropna()` on the raw BTC price series before calculating the moving averages. If Yahoo Finance has a missing day (e.g., a glitch dropping a Wednesday), that entire row is deleted from the time series. When you compute `rolling(10).mean()`, pandas simply grabs the last 10 *available* rows. This means a 10-day SMA will silently expand its time window to 11 or 12 calendar days to bridge the missing gap. You are warping the 365-day calendar integrity and distorting the volatility calculation. 

**The Fix:** 
Use `.ffill()` instead of `.dropna()`. This preserves the true chronological grid (since `df_raw` contains all days mapped by the SPY/BTC union) and simply carries the last traded price forward across missing gaps, ensuring `rolling(10)` strictly represents 10 calendar days.

### 2. INDEX INTERSECTION LOGIC (`reindex` vs `loc`): FAILED ❌
**The Flaw:**
```python
weights_biz = target_weights_365.reindex(biz_idx).ffill()
```
This is a lethal logic bug caused by the `.dropna()` mistake above. If BTC is missing data on a Monday, `.reindex(biz_idx)` inserts a `NaN` for that Monday. Then, `.ffill()` forward-fills the value from **Friday** (because it looks back in the newly created `biz_idx` series). This completely ignores the perfectly valid target weights that were computed for **Saturday** and **Sunday**! You have created a weekend-blind spot.

**The Fix:**
Once you fix the upstream series by using `.ffill()` instead of `.dropna()`, the arrays will perfectly intersect. You can aggressively and safely use `.loc[biz_idx]` because `target_weights_365` will natively contain every single business day. Alternatively, if relying on `reindex`, use `target_weights_365.reindex(biz_idx, method='ffill')` to force pandas to look backwards in the true 365-day calendar grid to grab Sunday's weight.

### 3. LOOKAHEAD BIAS: PASSED ✅
* You correctly shifted `trend`, `vol_w`, and `irx` by 1.
* Trading at Monday's `Open` uses signals computed from Sunday's `Close` (which is technically Monday 00:00 UTC). This represents zero lookahead bias. You trade exactly on the boundary where information becomes available.

### 4. WEIGHT DRIFT & SLIPPAGE: PASSED ✅
* **Slippage Execution:** Slippage is correctly mapped strictly to `turnover` and properly deducted from `port_ret = a_ret + c_ret - slip`.
* **Drift Factor:** The calculation `drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)` mathematically isolates the exact drift of the asset's weight prior to the next rebalancing event. Flawless representation of portfolio dynamics.

### 5. STATIC MARGIN ABUSE: PASSED ✅
* Margin borrowing dynamically tracks the Fed Funds proxy (`cy_arr[i]`) + 1.5% premium. No static 2% infinite-borrow assumptions are used.

## VERDICT
**Loop 3 of 5 FAILED.** The core backtest engine is mathematically pure regarding slippage, lookahead bias, and portfolio drift. However, the pandas indexing mechanisms (`.dropna()` and `.reindex().ffill()`) are structurally flawed and compromise the integrity of the 365-day calendar mapping. 

Implement `.ffill()` on the raw series and transition to `.loc` intersection. Submit Loop 4 for audit when resolved.
