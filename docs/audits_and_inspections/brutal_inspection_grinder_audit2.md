# BRUTAL MULTIPOINT QUALITY INSPECTION - AUDIT 2
**TARGET:** `fable_generated_grinder.py` & `fable_10_module_grinder.py`
**GRADE:** REJECTED (CRITICAL MATHEMATICAL & STRUCTURAL FLAWS)

## 1. The Circular Block Bootstrap Illusion & Time-Travel Bias
**Location:** `block_bootstrap_sharpe` -> `(starts[:, :, None] + offsets[None, None, :]) % T`

You asked if this operates correctly and if it introduces lookahead bias. The answer is **YES, it introduces a catastrophic structural time-travel anomaly.** 

By using the modulo operator (`% T`), you are executing a "circular" wrap-around. If a 20-day block begins at index `T-5` (e.g., the last week of 2024), the sequence generated is `[T-5, T-4, T-3, T-2, T-1, 0, 1, 2, ...]`. 
This forcibly splices the very end of your out-of-sample data (2024) directly into the beginning of your in-sample data (2014) *within a single continuous block*. 

**Why this is brutal:**
1. **Lookahead / Time-Travel:** You are injecting the past (2014) as the immediate sequential future of the present (2024). In any path-dependent context (like the CPPI, VoV Brake, or Patience Dial strategies inside your 10-module grinder), traversing this boundary means the portfolio's internal state (leverage, high-water marks) built up in 2024 is now interacting directly with 2014 price action. That is blatant time-travel and violates causality.
2. **Synthetic Regime Shocks:** 2024 Bitcoin volatility and price action are structurally distinct from 2014. Forcing an overnight gap from Dec 2024 to Jan 2014 creates a massive, synthetic volatility shock that never existed in physical reality, destroying the core purpose of a block bootstrap (which is to preserve actual historical joint distributions).
3. **The Order-Invariance Mask:** Right now, you are only calculating the Sharpe Ratio on these paths (`mu / sd`). Because Sharpe is order-invariant, this flaw is currently mathematically masked (scrambling the returns doesn't change the path's overall `mu` or `sd`, only the sampling variance). But the moment you or anyone else extends this grinder to measure path-dependent metrics (like Max Drawdown, Calmar Ratio, or Compounded CAGR), this circular wrap-around will completely invalidate the backtest. 

**The Fix:** Use a strict, non-circular overlapping block bootstrap. Restrict your `starts` sampling to `rng.integers(0, T - block + 1)`. End-effects are a small price to pay to maintain absolute causality.

---

## 2. The Drift Haircut Fraud (Volatility is NOT Preserved)
**Location:** `drift_haircut` -> `btc_hc = np.expm1(log_b + shift)`

You asked if scaling the target log-drift actually preserves daily volatility in linear return space correctly. The answer is **ABSOLUTELY NOT. It is mathematically flawed and artificially crushes volatility.**

The comment explicitly claims: `vol preserved in log space`. While true in log space, the Sharpe ratio evaluation (`sharpe(port_hc)`) is executed in **linear return space**. 

**The Proof:**
Let $r$ be the daily log return and $R$ be the linear return where $R = \exp(r) - 1$.
You apply a shift: $r_{new} = r + c$, where $c = \text{shift}$.
The new linear return is:
$R_{new} = \exp(r + c) - 1 = \exp(r)\exp(c) - 1 = (1 + R)\exp(c) - 1$.

Now, calculate the variance of the new linear return:
$Var(R_{new}) = Var((1 + R)\exp(c) - 1) = \exp(2c) \times Var(R)$

The standard deviation (volatility) in linear space is scaled by exactly $\exp(c)$. 
Since historical BTC CAGR is massive (~60%+) and your target CAGR is 10%, your `shift` is deeply negative. Therefore, $\exp(c) < 1$. 

**Why this is brutal:**
You are systematically shrinking the linear volatility of the benchmark asset. Because `port_hc = p + beta * delta` (where `delta` is derived from this volatility-crushed benchmark), you are subtly suppressing the variance of the portfolio's returns. 
By artificially shrinking the denominator of the Sharpe ratio, **you are artificially pumping the strategy's post-haircut Sharpe.** This completely undermines the "grinder" philosophy. You are giving the strategy an unearned mathematical advantage.

**The Fix:**
If you want to preserve linear volatility perfectly while shifting the mean, you must apply the additive shift in linear space, not log space:
`btc_hc = df["b"] - (df["b"].mean() - target_linear_mean)`
(Note: You must handle the edge case where a linear shift pushes a daily return below -1.0). Alternatively, if log-normality is strictly required, you must explicitly scale the standard deviation in log space by solving for the log-normal moments to perfectly offset the linear compression. 

## FINAL VERDICT:
**FAILED.** The Grinder itself is flawed. The physical-reality stress test is currently leaking causality in its bootstrap and artificially crushing benchmark volatility in its haircut, inadvertently providing a softer grading curve for the strategies it evaluates. Fix the math.
