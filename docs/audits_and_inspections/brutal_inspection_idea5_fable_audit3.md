# ADVERSARIAL AUDIT: OMNI-ALLOCATOR IDEA 5 — VOL-OF-VOL BRAKE

**Verdict: FAILED.** No fatal lookahead in the classic `shift(-1)` sense, but the code contains a zero-effective-lag execution assumption on BTC, a docstring/logic contradiction, calendar-convention bugs, an understated drawdown metric, and severe methodological rot. Itemized below by severity.

---

## 🔴 CRITICAL

### C1. "Mode B 1-bar lag" is effectively **ZERO lag for BTC** — borderline lookahead
Trace the timeline: signals are `.shift(1)` on the **BTC daily calendar**, so the weight at day *t* uses data through **close of t−1**. Execution is at `r_open[t]` = Open(t) → Open(t+1), i.e., fill at **Open(t)**.

For BTC on Yahoo daily bars, Close(t−1) is stamped ~23:59:59 UTC and Open(t) is 00:00:00 UTC — **the same instant, effectively the same price**. Your "institutional lag" is zero seconds for the asset carrying **60% of the risk budget**. You are computing a 20d vol, 60d vol-of-vol, and 365d rolling quantile, and assuming the order is filled at the exact price the signal was computed from. The docstring claims "trade fills at Open t+1" — the code fills at Open t. For SPY/GLD (close 4pm → open 9:30am next day) this is implementable; for BTC it is a fantasy fill. This alone will flatter Sharpe on a fast 2/40 crossover.

### C2. Docstring lies about the mechanism
> *"scales down BTC exposure when its 60-day Vol-of-Vol exceeds the 90th percentile"*

The code does not scale — it multiplies by a **binary 0/1 gate**, liquidating up to a 0.90 portfolio weight in a single bar. And because the threshold is a **rolling relative quantile**, the brake fires on ~10% of days **by construction, in every regime** — including calm ones. It's not a risk brake; it's a scheduled 10%-duty-cycle kill switch. If VoV were uniformly low for a year, you'd still zero out BTC 10% of the time.

### C3. Massive multiple-testing / selection bias
This is explicitly "IDEA 5." You are running a family of ideas over the **same single 2014–2023 sample** — the greatest BTC bull run in history, with 60% BTC allocation — and will presumably keep the winner. Free parameters everywhere (20d vol, 60d VoV, 365d window, 0.90 quantile, 0.15 vol target, 1.5 cap, 2/40 vs 10/100 trends) with zero walk-forward, zero OOS holdout, zero parameter-sensitivity sweep. Any reported Sharpe is an upper bound on nothing.

---

## 🟠 HIGH

### H1. Total-return vs price-return ambiguity (yfinance version-dependent)
No `auto_adjust` argument to `yf.download`. On older yfinance, `Close`/`Open` are **unadjusted** → SPY returns silently drop ~1.3–1.9%/yr in dividends; on newer versions they're adjusted. The backtest result is **not reproducible across environments** and may understate the SPY sleeve. Pin the behavior explicitly.

### H2. Drawdown computation understates MaxDD
```python
cum = np.cumprod(1 + port_ret)
cummax = np.maximum.accumulate(cum)
```
No initial `1.0` prepended. If the equity curve dips below 1.0 from bar zero, `cummax[0] = cum[0] < 1` and the initial drawdown from par is **invisible**. Prepend `1.0` to `cum` before accumulating.

### H3. Financing model is fictional for the leveraged case
Gross exposure can reach **1.5×** (0.90 BTC + 0.30 + 0.30). Negative cash is charged `cy + 1.5%/yr`. Nobody finances levered BTC exposure at T-bills + 150bp. Crypto perp funding or margin borrow runs multiples of that, and there is no margin-call / forced-deleveraging logic. Also note the unit bug: `0.015/252` (trading-day spread) is multiplied by `delta_days` (**calendar** days), so weekend borrow is overcharged 3× on the spread while `cy/365` is calendar-consistent. Two conventions in one line.

### H4. Yahoo BTC-USD pre-2017 data is garbage
2014–2016 Yahoo crypto daily bars contain known bad prints, thin volume, and stale opens. Your 20d vol, VoV, and trend signals in the first ~2 years of the backtest are built on noise, and the `[250:-1]` warmup does not cover it: the VoV brake needs 20+60+365 ≈ **445 BTC days**; with BTC data starting Sept 2014, `fillna(np.inf)` leaves the brake **inert until roughly December 2015** while the headline claims the brake was active the whole period.

---

## 🟡 MEDIUM

### M1. Sharpe computation inconsistencies
- `std` uses **raw** `port_ret`, numerator uses **excess** returns. Use excess for both.
- Annualization by `sqrt(252)` while BTC weekend variance is clumped into Monday bars (open-to-open across 3 calendar days) → heteroskedastic bar returns treated as iid daily.
- `cy_arr.fillna(0.0001)` — a magic 0.0001/day ≈ **3.65% annualized** filler for missing ^IRX, when 2014 bills yielded ~0.02%. Small n affected, but it's an invented number.

### M2. Slippage model too thin for this turnover profile
A 2/40 crossover on BTC flips a 0.90 weight binary; combined with the 10%-duty brake, turnover is enormous. Flat 20bp linear slippage with no spread widening, no impact scaling with size, no exchange fees. GLD/SPY at 3bp is fine; BTC at 20bp flat over 2014–2016 order books is generous.

### M3. `btc_vw` division hazard
`0.15 / btc_vol` → `inf` when a stale/duplicated BTC print gives zero 20d vol; the `clip(upper=1.5)` silently converts a data error into a max-leverage signal instead of flagging it.

### M4. No error handling on the download
If `^IRX` or `BTC-USD` returns empty (Yahoo throttling — a daily occurrence), the code either raises a cryptic KeyError or silently propagates NaN columns through `ffill`. No shape/NaN assertions anywhere. `warnings.filterwarnings('ignore')` at module scope suppresses exactly the pandas warnings that would catch chained-indexing surprises.

---

## 🟢 LOW / STYLE

- **L1.** Redundant double-ffill: `df_raw = df_raw.ffill()` then `open_p.ffill()`, `irx.ffill()`, `gld_c ... .ffill()` again. Harmless, but signals the author doesn't know the state of their own frame.
- **L2.** Copy-pasted GLD/SPY blocks (identical logic, three times) — should be one function. `w_exec = w_target[i]` copy: fine, since numpy row views aren't mutated, but fragile if the loop is ever edited.
- **L3.** Loop is O(n) over ~2,300 bars — acceptable, but the entire execution loop is vectorizable except the compounding of `prev_w`; not a performance issue at this scale, so noted, not flagged.
- **L4.** `prev_w` drift divides by `(1+ret)` which includes slippage and cash carry — weights drift slightly wrong vs. asset-only NAV. Second-order, but sloppy.
- **L5.** `biz_idx[250:-1]` hardcoded warmup with zero relation to the actual longest lookback (see H4).

---

## FINAL VERDICT

**FAILED.** 
The backtest is mechanically mostly leak-free, but the BTC fill assumption (C1) is economically equivalent to a lookahead. The strategy's headline mechanism doesn't do what's claimed (C2), the drawdown is understated (H2), and the research process is un-salvageable in-sample curve-fitting on one BTC bull cycle (C3). 
Fix C1 by executing BTC at Open(t+1) or a VWAP band with realistic slippage, replace the binary quantile gate with an actual scaling function on an **absolute** VoV threshold, prepend 1.0 to the equity curve, pin `auto_adjust`, and re-run with a 2024+ holdout before any performance number leaves this file.
