# OPUS-5R: STRUCTURAL AUDIT & NEURAL INTEGRATION MANDATE

**Verdict: The plan is 70% correct in citation and 40% correct in implementation logic. It reads like someone who has read *Advances in Financial Machine Learning* but has not yet been burned by it. Below is the teardown, then the neural network answer you asked for — including where NNs earn a seat at the table and where they would destroy you.**

---

## PART I: EPISTEMIC FAILURES (Fix These Before Writing Code)

### 1.1 The "100% success-guaranteed" language is a system-level bug
Any architecture document that says "flawless" or "guarantees structural alpha" has already failed the de Prado test, because the entire CPCV/DSR framework exists precisely because *nothing is guaranteed* and every backtest is a biased estimator of live performance. This isn't pedantry — it predicts behavior. A team that believes the framework guarantees success will skip the lockbox holdout, skip PBO estimation, and deploy on the first green Sharpe. Strike the language; add the missing falsification machinery (Part III).

### 1.2 The -999.0 Sharpe sentinel is actively poisoning your optimizer
This is the single most important bug in the document and you buried it in a footnote.

Optuna's TPESampler builds a density model over the objective landscape. When you return `-999.0` for zero-trade trials, you inject a massive artificial cliff into that density. TPE then spends its entire budget learning the boundary of the cliff instead of the structure of the alpha surface. **Zero-trade trials must raise `optuna.TrialPruned` (excluded from the surrogate), not return a sentinel value.** Additionally, log *why* zero trades occurred (threshold never crossed? data pipeline returned NaNs? signal logic inverted?). If 2000/2000 trials produced zero trades, the prior probability that this is a search-space width problem rather than a **pipeline bug** is low. Audit the signal generation with a hand-picked parameter set known to trade before you touch the search space.

### 1.3 "Massively widen the search space" is the overfitting engine you claim to be eradicating
Every trial you run is a draw from the multiple-testing distribution. The Deflated Sharpe Ratio's deflation term is a function of **N = number of trials and the variance of trial Sharpes**. Widening the space and loosening the pruner increases N and increases the expected maximum Sharpe under the null (pure noise): E[max SR] ≈ σ_SR · [(1−γ)Z⁻¹(1−1/N) + γZ⁻¹(1−1/(Ne))]. You cannot cite DSR in Phase 4 and then propose the exact behavior DSR punishes in your closing question. The correct move: **fix the pipeline bug, keep the space tight and economically motivated, and log every trial ever run (including dead ones) because they all count toward N in the deflation.**

---

## PART II: PHASE-BY-PHASE TEARDOWN

### Phase 1 — Fractional Differentiation: three unstated leaks

1. **Look-ahead in d-estimation.** If you compute the minimal `d` achieving ADF p < 0.05 on the *full 10-year series*, you have leaked the future into every training fold. `d` must be estimated **inside each CPCV training fold only**, or fixed a priori from a pre-2015 burn-in period that never enters evaluation.
2. **Fixed-Width Window (FFD) vs. expanding window.** The plan doesn't specify. The expanding-window formulation has drift; you must use FFD with an explicit weight-tolerance cutoff (τ ≈ 1e-4), and the resulting warm-up region must be excluded from labels — another interaction with your purge accounting that the plan ignores.
3. **Stationarity ≠ predictability, and not all features want fracdiff.** RSI is already a bounded oscillator; fractionally differencing prices *before* computing RSI changes its semantics entirely and is not obviously an improvement. Fracdiff the *price/level features*; leave bounded oscillators on raw prices with your Phase 2 Z-scoring. Also: **volume, VIX, and spread features are non-stationary too** and the plan is silent on them.

### Phase 2 — Volatility Normalization: correct idea, undercooked estimator

- ATR-14 is a retail-grade volatility estimator with severe lag. For barrier placement use an **exponentially weighted realized volatility** (span ~ your holding horizon) or **Yang-Zhang** (uses OHLC, ~7x more efficient than close-to-close). At minimum, make the estimator a *design decision*, not a default.
- Every rolling Z-score introduces a **window hyperparameter**. Three Z-scored indicators × window × threshold = combinatorial explosion feeding the multiple-testing problem in §1.3. Fix windows to economically meaningful horizons (e.g., 21/63/252 days) and *do not let Optuna touch them*.

### Phase 3 — Triple Barrier + Meta-Labeling: four omissions, one fatal

1. **FATAL — Double-dipping between Optuna and the meta-model.** Your protocol optimizes the primary strategy on CPCV folds, then trains the meta-labeler... on the same data. The meta-model's training labels (did the optimized primary signal hit TP or SL?) are conditioned on parameters *selected using that same data's out-of-sample performance*. The meta-model will learn the residue of your selection bias and report fantasy precision. **You need nested separation: an outer temporal split (or nested CPCV) where the meta-model only ever trains on primary-model signals generated with parameters frozen before that data was seen.**
2. **Overlapping labels → non-IID samples.** With a 5-day vertical barrier on daily data, consecutive labels share up to 4 days of returns. XGBoost trained without **uniqueness-based sample weights** and (ideally) **sequential bootstrapping** will hallucinate confidence. This is Chapter 4 of the very book you're citing, and it's absent.
3. **The vertical barrier should be volatility-scaled, not "5 days."** In a vol regime shift, 5 calendar days is a different economic horizon. Express it in vol-time or make it σ-dependent.
4. **Kelly on raw classifier probabilities is account suicide.** XGBoost probabilities are miscalibrated by construction. You must apply **isotonic or Platt calibration on a purged validation set**, then use **fractional Kelly (¼ to ½)** because your probability estimates carry estimation error that full Kelly amplifies into ruin. Also cap position size by a portfolio-level vol target — Kelly sizing without a drawdown governor is not institutional, it's a prop-firm blowup memoir.

### Phase 4 — CPCV: you got the math wrong

- **"15 out-of-sample paths" is incorrect.** With N=6 groups and k=2 test groups you get C(6,2) = **15 splits**, which recombine into **φ = k·C(N,k)/N = 5 backtest paths**. Your objective function description ("Sharpe across 15 CPCV paths") conflates splits and paths. This matters: the variance penalty in `mean/std` is computed over 5 path-level Sharpes, not 15 split-level Sharpes, and the two give materially different rankings.
- **Purge length must exceed the maximum label horizon.** Your vertical barrier is 5 days, but your labels also depend on rolling features (Z-score windows up to 63+ days, fracdiff FFD window). A 10-day purge does not cover a 63-day feature lookback bleeding across the boundary. Purge ≥ max(label horizon) and be honest that feature lookback contamination is only partially addressable.
- **DSR is being misused.** DSR is a *post-selection deflation* — a function of the number of trials, trial-Sharpe variance, skew, and kurtosis of returns. You cannot "maximize DSR in the objective" coherently, because N grows with every trial. Correct architecture: **optimize `mean(path Sharpes) / std(path Sharpes)` (a PSR-flavored objective) inside the loop, then compute DSR once at the end using the full trial ledger, then compute PBO via CSCV.** If PBO > ~30% or DSR's implied p-value fails, the strategy is dead regardless of the headline Sharpe.
- **No lockbox.** Reserve the most recent 12–18 months, touched exactly once, after all optimization and meta-model training is frozen. No lockbox = no institution will ever allocate to this.

---

## PART III: MISSING SUBSYSTEMS (Not Mentioned Anywhere)

1. **Transaction cost model.** No spread, slippage, or impact model appears in the document. A mean-reversion strategy's edge lives and dies in the half-spread. Sharpe computed gross of costs is fiction. Model: half-spread + f(participation rate) impact + commissions, stress-tested at 2x.
2. **Feature importance with substitution effects.** No MDA/clustered-MDA/Shapley analysis. Without it you cannot distinguish structural alpha from a lucky feature, and you cannot detect when live decay begins.
3. **Regime layer.** Everything is vol-normalized but nothing is regime-*aware*. Minimum viable: 2–3 state HMM on vol/returns as a meta-model feature.
4. **Data hygiene.** Point-in-time alignment of VIX (settlement vs. close), dividend adjustment policy, corporate actions if universe expands. Silent, and silently fatal.
5. **Live operations.** No model decay monitoring (rolling live-vs-backtest Sharpe drift, PSR degradation alarms), no retraining cadence, no kill-switch drawdown threshold. The plan ends at the backtest, which is where institutional systems *begin*.

---

## PART IV: THE NEURAL NETWORK ANSWER

### Why the plan (correctly) didn't reach for NNs first — and why that instinct is incomplete

The honest reason NNs were omitted: **financial time series have a signal-to-noise ratio near zero, and a single asset's daily history (~2,500 samples, heavily overlapping labels, maybe 3–4 genuinely independent regimes) is catastrophically insufficient to fit a high-capacity function approximator.** An LSTM with 50k parameters trained on 2,500 autocorrelated daily bars will memorize noise with near-certainty, and standard NN validation (random split early stopping) is *exactly* the leakage CPCV exists to kill. Gradient boosting dominates NNs on small tabular financial data — this is empirically robust and de Prado himself defaults to it.

**But** the blanket omission throws away three places where NNs provide a *mathematically distinct* capability that XGBoost cannot replicate — provided we enforce a brutal parameter-budget and validation discipline. Here is the integration:

### Phase 1.5 [NEW] — Denoising Autoencoder Feature Compression ("The Latent Market State")

**What:** Train a small **denoising autoencoder** (input: ~40–80 vol-normalized, fracdiff'd features; bottleneck: 6–10 latent dimensions; total parameters < 15k) to compress the daily feature vector into a low-dimensional latent state. Feed the *latent coordinates* — not the raw 80 features — to the meta-labeler alongside a handful of hand-picked economic features.

**Why this is rigorous, not fashionable:** The AE is trained on **reconstruction loss, which is unsupervised — it never sees labels or returns.** This means it cannot overfit the *target*; it can only overfit the input distribution, which is a far more benign failure mode. It functions as a **nonlinear PCA** that collapses the substitution-effect-riddled feature space, directly attacking the multiple-testing explosion (fewer effective features → tighter DSR deflation → more of your Sharpe survives deflation). The denoising corruption (mask 15–20% of inputs) is a regularizer with a Bayesian interpretation.

**Discipline:** AE fit inside training folds only. Latent dimension chosen by reconstruction-error elbow, *never* by downstream Sharpe. If latent features don't beat clustered-PCA baseline on meta-model precision at equal deflation, the AE is deleted. NNs must *earn* their compute.

### Phase 3.5 [NEW] — Sequence-Aware Meta-Labeling: The Hybrid Stack

**What:** The meta-labeler becomes a two-head ensemble:
- **Head A (retained):** XGBoost on tabular features (AE latents, VIX percentile, HMM regime posterior, signal-side features) with uniqueness sample weights. This remains the backbone — do not fight the tabular-data empirics.
- **Head B (new):** A **small causal Transformer or single-layer LSTM** (embedding dim ≤ 32, 1–2 attention heads, context window 60 bars, parameters < 30k, dropout ≥ 0.3) that consumes the *sequence* of the last 60 bars of latent states and outputs a fixed **"regime context embedding"** (8 dims). This embedding is appended to Head A's feature vector.

**Why:** XGBoost is order-blind — it sees a snapshot, never the *path*. Whether volatility compressed gradually or spiked-and-decayed into today's identical snapshot is precisely the information a mean-reversion filter needs, and it is representable *only* by a sequence model. The attention mechanism (or LSTM gate) is the correct inductive bias for "which part of the recent path matters." This is the one job description NNs are uniquely qualified for here.

**Anti-overfitting protocol (non-negotiable):**
1. Parameter budget hard-capped at 30k; if it can't work small, it doesn't work.
2. Early stopping on a **purged, embargoed** validation slice — never a random split.
3. **Ensemble of 5 seeds**, average the embeddings — single-seed NN results in finance are noise.
4. Train on **cross-sectional data the moment the universe expands** (see Part VI). NNs become defensible when N_assets × T grows; on QQQ alone, Head B ships in shadow mode only.
5. **Ablation gate:** Head B survives only if (XGB + embedding) beats (XGB alone) on out-of-fold meta-precision *and* the final DSR — with Head B's tuning trials counted in the deflation N. Otherwise it is deleted without sentiment.

### Phase 3.6 [OPTIONAL, HIGH-RIGOR] — Quantile Network for Barrier Placement

Instead of symmetric σ-multiplier barriers, a tiny **quantile regression network** (pinball loss, quantiles 0.1/0.5/0.9, <10k params) forecasts the conditional return distribution over the label horizon; barriers are placed at conditional quantiles. This makes TP/SL *distribution-aware* (skew-sensitive) rather than merely vol-scaled. Ship this only after the core stack is validated — it multiplies model risk.

### What is explicitly BANNED
- End-to-end "LSTM predicts tomorrow's price" architectures. Non-stationary target, ~0 SNR, guaranteed overfit.
- Large Transformers / pretrained time-series foundation models on a single asset. Capacity without data is a random number generator with a GPU bill.
- Any NN whose validation touched the lockbox. One violation contaminates the entire program.

---

## PART V: REVISED FILE ARCHITECTURE

```
[MODIFY] master_data_pipeline.py    → FFD fracdiff (per-fold d), Yang-Zhang vol, PIT alignment, cost fields
[NEW]    label_engine.py            → Triple barrier (vol-scaled vertical), uniqueness weights, seq. bootstrap
[NEW]    latent_encoder.py          → Denoising AE, fold-scoped fit, elbow-selected bottleneck
[NEW]    master_grinder_v15_opus.py → TPE + TrialPruned (no sentinels), CPCV(6,2)=15 splits/5 PATHS,
                                       objective = mean/std of PATH Sharpes NET of costs, full trial ledger
[NEW]    meta_label_trainer.py      → Nested split, XGB + calibration (isotonic) + fractional Kelly + vol cap
[NEW]    seq_context_model.py       → LSTM/causal Transformer embedding head, 5-seed ensemble, ablation gate
[NEW]    falsification_suite.py     → DSR (using full ledger N), PBO via CSCV, lockbox single-shot eval
[NEW]    live_monitor.py            → PSR drift alarms, decay detection, kill-switch
```

---

## PART VI: ANSWERS TO YOUR THREE DECISIONS

**1. Meta-labeling now or CPCV first?** Sequence, don't choose: CPCV + fracdiff + cost model + falsification suite first (the *evaluation* layer must exist before anything is worth evaluating). Meta-labeling second, with the nested-split fix from §II-3.1. Neural heads (Phase 1.5/3.5) third, gated by ablation.

**2. Asset universe?** Validate the *code* on QQQ, but understand: statistical validity requires the cross-section. Expand to 8–15 liquid, structurally distinct assets before drawing any conclusion — and note this is also the precondition that makes the neural components defensible (§IV). One asset = one draw from the regime distribution.

**3. V14 pruning fix?** **Denied as stated.** Fix the sentinel bug (§1.2), audit the pipeline with a known-trading parameter set, and only then adjust the space — *narrowly and with economic justification*, logging every trial for the final DSR deflation. Widening the space to "make trials pass" is manufacturing the exact selection bias this entire architecture exists to kill.

**Authorization withheld until the sentinel bug, the path-count error, the nested-split leak, and the cost model are acknowledged in the revised spec. Then we grind.**