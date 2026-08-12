# Brutal Review: Gigantic Grid Search Engine

Verdict up front: **the Numba kernels are mechanically sound, but the experiment as designed will produce a confidently wrong answer.** There are two residual lookahead vectors, one silent pandas bug, a degenerate-Sharpe exploit that the argmax *will* find, a compute budget that may be physically infeasible, and — most importantly — zero statistical protection against the fact that the max over ~10⁸–10¹¹ trials is noise by construction. Point by point:

---

## 1. CRITICAL — Correctness & Bias

### 1.1 The asset signals are (probably) still lookahead-biased
You shifted `risk_on_macro` and `vix_crash` by 1 — good. But **nothing in this file shifts `mat_a..mat_e`, `sig_mr`, `sig_regime`, `sig_sma`, or `sig_rsi`.** If the `.npz` generation script computes a signal from close `t` and this engine applies it to `rets[t]` (which *is* the move into close `t`), every single one of your millions of results carries same-bar lookahead. The macro fix is cosmetic if the primary signals leak.

**Action:** Verify the generator, or defensively shift here and accept a 1-day double-lag in the worst case (double-lag costs a little alpha; lookahead costs your career):

```python
def lag1(x):
    y = np.roll(x, 1, axis=0); y[0] = False; return y
```

Apply to every signal array unless you can *prove* the npz is pre-shifted. Put an assertion or a provenance flag inside the npz (`data['shifted'] = True`) so this can never be ambiguous again.

### 1.2 `fillna(True)` is a silent no-op — your stated intent is broken
```python
credit_risk_on = (hyg_lqd > hyg_lqd_ma).fillna(True).values
```
In pandas, `NaN > NaN` evaluates to **`False`**, not `NaN`. The comparison output is a pure boolean Series with no NaNs, so `.fillna(True)` does nothing. Pre-HYG-inception (2007) and during the 50-day warm-up, `credit_risk_on` is `False`, not `True` as intended. You're saved only by the `|` with `econ_risk_on` — which has the *same* bug and is `False` for its first 50 days. Net effect: `apply_macro` tickers are structurally flat/blocked in early history for a reason you didn't choose.

**Fix:**
```python
mask = hyg_lqd_ma.isna()
credit_risk_on = (hyg_lqd > hyg_lqd_ma) | mask   # explicit "no data = risk-on"
```

### 1.3 BTC-USD is being evaluated on a corrupted return series
- `dates.npy` is presumably an equity trading calendar. Reindexing BTC to it **silently discards weekend returns** (Fri→Mon compressed into one bar) — then you annualize with `√252` on an asset that trades 365 days.
- `.ffill().bfill()`: `bfill` backfills 1999–2014 with BTC's first traded price → 15 years of exact-zero returns. Sharpe scales roughly by `√(active_fraction)`, so every BTC result is deflated by ~√(11/26) ≈ 0.65 and **cross-ticker Sharpe comparison in the output CSV is meaningless.** Worse: whatever indicators the npz generator computed on that flat bfilled prefix are garbage.

**Fix:** per-ticker valid window — find first real (non-bfilled) index, slice `rets`, all signal arrays, and all overlays to `[t0:]` before the kernels. Use per-asset annualization factor.

### 1.4 The Sharpe argmax will select degenerate near-zero-variance strategies
Max-over-millions **actively hunts** the pathology: an AND-of-5 ensemble that's in the market 4 days, all positive, produces a tiny `m2` and an astronomical Sharpe. Your only guard is `m2 > 0`. The winners in your CSV will be dominated by low-exposure flukes, not tradeable strategies.

**Fix:** track exposure inside the kernel and gate the output:

```python
n_active = 0
...
if t0 > 0.0: n_active += 1   # per-logic counters, or approximate with one
...
if m2_0 > 0 and n_active_0 >= MIN_ACTIVE_DAYS:  # e.g. 250
    sharpes_out[i, 0] = ...
```

Without this, the entire run's output is dominated by exactly the strategies you least want.

### 1.5 `ASYMMETRIC` logic is order-biased and incompletely searched
`if a: t4 = votes / K` gates on the **first** family in the tuple. `itertools.combinations` emits exactly one ordering (list order in `FAMILIES`), so the "leader" is always the alphabetically-earlier family — MACD leads everything, ADX never leads. You are not searching "all ensemble techniques"; you're searching one arbitrary rotation of the asymmetric family. Either loop the leader over all K positions (multiply work by K), or drop the claim.

### 1.6 `MAJORITY` for size 2 is identical to `OR`
`votes >= 1` with K=2 ≡ `votes > 0`. You will report two rows with identical Sharpes and different labels — wasted compute and misleading output. For K=2 either define majority as `==2` (then it duplicates AND) or skip the logic.

---

## 2. CRITICAL — Statistical methodology (the biggest gap)

There is **no train/test split, no walk-forward, no multiple-testing correction.** Do the math on what the max of the null looks like: with ~26 years of daily data, the sampling std of an annualized Sharpe estimate is ≈ 1/√26 ≈ 0.20. The expected maximum over N effectively-independent trials scales like `0.20·√(2·ln N)`. At N = 10⁸ that's ≈ **1.2 Sharpe from pure noise**, before counting the residual lookahead in §1.1. Your top-of-CSV winners are guaranteed to look spectacular and are guaranteed to be substantially fake.

Minimum acceptable remediation:
1. **Split**: optimize on e.g. 1999–2016, report 2017–present untouched OOS, or proper walk-forward/CPCV.
2. **Deflated Sharpe Ratio** (Bailey & López de Prado) using the trial count you actually ran — you have the exact N, use it.
3. **Report the distribution**, not just the max: keep top-100 per combo, plus median, so you can see whether a family is broadly good or one param cell got lucky.
4. **Transaction costs**: zero costs + daily-flipping OR-ensembles = fantasy. Even a flat 2–5 bps per position change reorders the leaderboard dramatically. Trivial to add in-kernel: track previous weight, subtract `cost·|w_t − w_{t−1}|` from `ra`.

---

## 3. HIGH — Feasibility: did anyone compute the budget?

Total evaluations per ticker = Σₖ C(15,k)·p̄ᵏ where p̄ is the geometric-mean param count per family. C(15,5) alone is 3003:

| p̄ per family | size-5 combos | ×T(~6900) point-ops | Realistic wall-clock/ticker |
|---|---|---|---|
| 10 | 3.0×10⁸ | 2×10¹² | ~1–2 hours ✅ |
| 30 | 7.3×10¹⁰ | 5×10¹⁴ | **days–weeks** ⚠️ |
| 50 | 9.4×10¹¹ | 6.5×10¹⁵ | **months** ❌ |

The code never prints `total` across all combos or an ETA. If your GJR-GARCH/ALMA grids have 40+ param sets each, this run will not finish. **Print the grand total and a measured ops/sec estimate after the first chunk, before committing to the run.** If infeasible: prune per-family params to the top-quartile single-signal performers first (yes, that adds selection bias — control it with the §2 split).

---

## 4. MEDIUM — Numerical & Numba

- **`fastmath=True` + Welford + `nanargmax`**: fastmath licenses the compiler to assume no NaNs and reorder FP ops. Your `m2 > 0` guard makes NaN Sharpes unlikely, but `np.nanargmax` is then a lie — and if a NaN *does* sneak through under fastmath, behavior is undefined. Use plain `np.argmax` (sentinel −999 already handles empties) and consider dropping fastmath from the accumulation (keep it, if benchmarks show it matters, but know the tradeoff).
- **Variance divisor**: T−1 samples ⇒ sample variance should be `m2/(T−2)`. Immaterial at T≈6900, but if you claim "brutally meticulous," be correct.
- **`sig_mr = data['RSI'][:, 0]`** — strided view, non-contiguous into the kernel; wrap in `np.ascontiguousarray`. Also: why column 0? The overlay meta-parameters (RSI cell, AUTOCORR cell, SMA cell) are **hard-coded to the first grid cell** while everything else is exhaustively searched. Arbitrary and undocumented.
- **`id` shadows the builtin** in `eval_chunk_4/5`. Works in nopython mode; still sloppy.
- **`sig_rsi = sig_mr` aliasing**: the same array serves as mean-reversion entry AND the safe-haven RSI gate. If intentional, name it once; if not, it's a bug waiting to be misread.

---

## 5. MEDIUM — Design/logic questions you should be forced to answer

1. **VIX>25 blocks TLT and GLD.** That's exactly when safe havens earn their keep. `vix_crash` is applied unconditionally before the `is_safe` branch — for safe havens this is likely backwards.
2. **MR branch bypasses macro entirely**: when `sig_regime` is off, you go 100% long on `sig_mr` even if credit is risk-off — and the MR position is identical (1.0) across all five logics, so it dilutes the very ensemble comparison you're running. All 5 logic columns share a common return floor; differences you measure are only from the trend regime.
3. **Macro overlay ordering**: you compute the votes, then zero them if `not macro_overlay[t]` — dead compute; hoist the check. Trivial, but in a loop executed 10¹²+ times, trivial matters.

---

## 6. LOW — Engineering hygiene

- **No resume logic**: rerun after a crash appends duplicates to the CSV with no way to tell which rows are stale. Write per-(ticker,size) completion markers or a done-set keyed on `(ticker,size,families)` read at startup.
- **CSV injection**: param strings from `params.txt` containing a comma will silently corrupt columns. Use `csv.writer` with quoting, or a TSV.
- **Silent alignment assumption**: `fam_params[f]` ordering must match npz column order. One assertion buys you safety: `assert len(fam_params[f]) == data[f].shape[1]` — add it, and ideally store params inside the npz itself. (Prefix matching is fine — the `|` saves `RSI` vs `RSI_CUMRET` — but that's luck, not design.)
- **yfinance in a production grid search**: no retry, no cache, no validation that all 6 MACRO columns actually downloaded. A partial download here silently changes every result. Cache to disk, assert `macro_df.columns` completeness and non-NaN coverage after the expected inception dates.
- Five near-identical kernels: acceptable for Numba perf (avoids reflected-list issues), but generate them from a template string or at least test them against a single slow reference implementation — right now a typo in one unrolled accumulator line of `eval_chunk_4` would be undetectable.

---

## Priority queue

| # | Item | Severity |
|---|---|---|
| 1 | Verify/enforce 1-bar lag on **all** asset signals (§1.1) | Fatal if present |
| 2 | Min-exposure gate in kernels (§1.4) | Fatal to output quality |
| 3 | OOS split + Deflated Sharpe + trial count (§2) | Fatal to conclusions |
| 4 | Transaction costs in-kernel (§2.4) | Critical |
| 5 | BTC calendar/bfill/annualization (§1.3) | Critical for BTC rows |
| 6 | `fillna(True)` no-op (§1.2) | High |
| 7 | Compute-budget print + ETA before the run (§3) | High |
| 8 | ASYMMETRIC leader search, size-2 MAJORITY dedupe (§1.5–1.6) | Medium |
| 9 | VIX gate on safe havens, MR-macro bypass — justify or fix (§5) | Medium |
| 10 | Resume, CSV quoting, param-alignment assert, `nanargmax`→`argmax` | Low |

The kernels will run fast and produce a beautiful CSV. Fix items 1–5 or that CSV is a ranked list of the luckiest lookahead artifacts in your search space — the more compute you throw at it, the *more* wrong the top row gets.