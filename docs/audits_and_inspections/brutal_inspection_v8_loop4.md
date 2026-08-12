# OMNI-ALLOCATOR V8 - BRUTAL INSPECTION REPORT (LOOP 4/5)

**STATUS: FAILED**

I have subjected `omni_allocator_v8.py` to a ruthless, adversarial, atomic-level audit. While the structural lookahead bias is entirely eliminated and the intraday drift physics are a masterclass in mathematical precision, the script contains a catastrophic logic flaw regarding the calendar index, and a secondary hidden leak regarding margin abuse.

## 1. THE `biz_idx` ILLUSION (FATAL LOGIC BUG / METRIC DISTORTION)
You attempted to eliminate the "weekend blind spot" by applying `.ffill()` to the entire raw dataset. But you applied it **before** extracting the SPY calendar:
```python
df_raw = yf.download(['BTC-USD', 'SPY', '^IRX'], start="2014-01-01", end="2024-01-01", progress=False)
df_raw = df_raw.ffill()
spy_close = df_raw['Close']['SPY'].dropna() 
biz_idx = spy_close.index
```
**The Flaw:** By forward-filling `df_raw` globally, `SPY` prices on Saturday and Sunday are no longer `NaN` (they are filled with Friday's close). Consequently, `.dropna()` on `spy_close` does absolutely nothing over the weekends! 
Your `biz_idx` is NOT a 252-day business calendar. It is a full 365-day calendar. 

**The Impact:** 
1. The strategy is rebalancing every single Saturday and Sunday, violating the premise of "Filter to 252-day business calendar".
2. **Severe Metric Deflation:** Your `valid_idx` has ~3,400 days (365 days/year). But your CAGR exponent is hardcoded to `252 / len(final_port_ret)` and Sharpe is multiplied by `np.sqrt(252)`. You are calculating annualized returns assuming a year has 365 days but dividing by 252, severely *suppressing* and *deflating* your own CAGR and Sharpe Ratio.

## 2. STATIC MARGIN ABUSE (WEEKEND BORROW COST LEAK)
If you fix the `biz_idx` bug (by extracting the SPY index *before* the `.ffill()`), you will immediately activate a hidden margin leak.
```python
cy_arr[i] = (irx / 100) / 252
...
c_ret = cash * (cy_arr[i] + (0.015 / 252))
```
When the loop steps from Friday Open to Monday Open, **3 calendar days** elapse. The simulation holds the leveraged position through the entire weekend. However, the script only charges exactly 1 day of `cy_arr[i]` interest.
You are getting 2 days of free leverage every single weekend. Over 10 years, you are skipping ~1,040 days of borrow costs, structurally inflating your net returns.

**The Fix:** You must compute the `delta_days` between `valid_idx[i]` and `valid_idx[i+1]` and multiply `c_ret` by `delta_days`.

## 3. EXACT INTRADAY DRIFT SIMULATION PHYSICS: PASSED
Your intraday drift physics are flawless.
```python
drift_factor = (1.0 + r_mat[i]) / (1.0 + port_ret)
prev_actual_w = w * drift_factor
```
This is mathematically sound. It perfectly accounts for the contraction/expansion of the asset's weight relative to the total portfolio equity (even after slippage and cash interest drag), and it naturally handles the inverted math for short positions (where the liability expands but equity contracts). **100% Validated.**

## 4. LOOKAHEAD BIAS: CLEAR
The `.shift(1)` logic correctly maps the $T-1$ Close to the $T$ Open execution. Because crypto runs 24/7, Sunday's Close (23:59 UTC) happens exactly 1 minute before Monday's Open (00:00 UTC). Information flows purely forward. No time warps detected. **100% Validated.**

## REQUIRED FIXES FOR LOOP 5:
1. Extract `spy_close` and define `biz_idx` **before** running `df_raw.ffill()`.
2. Add a `delta_days` multiplier (e.g., `(biz_idx[i+1] - biz_idx[i]).days`) to the `c_ret` calculation to charge accurate interest over weekends and holidays.
3. Once fixed, your CAGR and Sharpe will explode upwards because the math will properly scale to 252 days instead of punishing the strategy with a 365-day denominator mismatch.
