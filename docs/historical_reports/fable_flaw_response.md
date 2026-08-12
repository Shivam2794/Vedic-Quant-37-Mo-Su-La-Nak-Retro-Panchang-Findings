# Fable's Response to the 6 Math Flaws

# The Plea

Line them up. I'll take each count standing, because a grinder that can't survive its own grinding deserves the scrap heap. But I'm not signing a confession with six counts when your subagents padded the indictment. Let's be precise.

---

## Count 1 — Deflated Sharpe Ratio: **GUILTY**

No defense. Bailey & López de Prado are unambiguous: `SR0` is derived from the **cross-sectional variance of Sharpe ratios across the trial set**, scaled by the expected maximum of N draws. I fed it the sampling variance of a single track record, which decays as ~1/T — so a 10-year backtest faced a hurdle asymptoting to zero. That's not a bug, that's a DSR that deflates nothing. It converts the test into a rubber stamp. This is the most serious count because it's the one flaw that biased *toward approval*. Guilty, no mitigation.

## Count 2 — `port - base` Active Return: **GUILTY**

Correct diagnosis. `port - base` is an information-ratio construction that implicitly assumes β = 1. Under leverage, `2β - β = β`, and I'd have congratulated a levered index fund for generating "alpha." Jensen regression → residualize → Appraisal Ratio is the only defensible construction when the strategy's beta is unconstrained. Your subagents fixed it exactly the way I should have built it.

## Counts 3 & 6 — **GUILTY ONCE. Your subagents double-billed.**

These are the *same flaw*: additive shift in log space compresses arithmetic variance multiplicatively by `e^(2s)`, applied to the strategy leg (Count 3) and benchmark leg (Count 6). One mechanism, two instantiations, counted twice to inflate the indictment from 5 to 6. I'd have flagged that in *their* code review.

On materiality: for a daily shift of −10bps, the vol compression is ~0.1% — the Sharpe inflation is second-order. Guilty on the mathematics; the correct haircut is applied to arithmetic drift with variance held fixed, or via a proper geometric adjustment. But don't pretend this moved the verdict. It didn't.

## Count 4 — 25.2% Annualized Drag & Crypto Slippage on SPY: **GUILTY OF NEGLIGENCE, not authorship**

Read your own filing: "*You allowed **my** 10bps daily gap penalty to remain.*" That parameter was yours. My crime is failing the sanity check — 10bps × 252 = 25.2%/yr is a number that should have tripped an assertion, and any cost model that charges 55bps slippage on SPY (a market that trades at sub-1bp spreads) is miscalibrated on its face. Costs must be per-asset, per-liquidity-tier. I plead guilty to rubber-stamping your input. A grinder that doesn't grind its own parameters is theater.

## Count 5 — Circular Block Bootstrap: **NOT GUILTY AS CHARGED**

Here your subagents overreached. `(starts + offsets) % T` is not a bug — it's the *definition* of the circular block bootstrap (Politis & Romano, 1992), and the wrap exists to correct the endpoint-underweighting bias of the moving block bootstrap. If your "fix" was simply removing circularity, you traded a published estimator for a biased one.

The **real** flaw — which they gestured at but misdiagnosed — is that *every* block seam is a synthetic regime splice, not just the wrap-around. Gluing a 2022 block to a 2017 block is exactly as fictional as gluing 2024 to 2014. For path-dependent metrics like CPPI gap risk and max drawdown, the correct answer isn't "unwrap the circle" — it's a stationary bootstrap with regime-conditional block sampling, or abandoning resampling for those metrics entirely. Guilty of the lesser included offense: using any block bootstrap for path-dependent statistics without a regime model. Not guilty of the charge as written.

---

## The Verdict That Matters

Tally the bias directions: Counts 1, 2, 3/6 all made the Grinder *too lenient*. Count 4 made it too harsh. You corrected all of them — three fixes in the strategy's favor, one against — and it **still** produced a negative appraisal ratio and 100% Bitcoin beta dependency.

That's the only result worth writing down: the verdict was robust to the errors of the judge. Your 1.91 Sharpe was a mirage under broken math and a mirage under fixed math.

Your subagents did good work. Tell them 6 counts was really 5, and Count 5 was really a different crime. Then have them grind their own fix for endpoint bias — because I guarantee they introduced one.