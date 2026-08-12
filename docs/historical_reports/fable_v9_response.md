# FABLE Review: "Omni-Allocator V9 (Tri-Asset Institutional Holy Grail)"

**Model:** `~anthropic/claude-fable-latest` (OpenRouter Genuine High-Reasoning Model)  
**Date:** 2026-07-08  
**Subject:** Institutional Autopsy of `omni_allocator_v9_tri_asset.py` (50% BTC / 25% GLD / 25% SPY)

---

## Executive Summary of Fable's Reasoning Autopsy

Fable performed a deep-dive structural audit on Omni-Allocator V9, analyzing its multi-asset diversification, execution lag mechanics (Mode A vs Mode B), and statistical robustness. Below is Fable's direct reasoning breakdown:

---

### 1. Execution Latency & Lookahead Evaluation
> *"For BTC, the signal at time t uses close data through t-1, and when reindexed to the business-day calendar, Monday's row corresponds to Sunday's close (roughly Monday's open price), so trading at Monday's open creates zero lag without lookahead — though this requires instant execution. The SMA(2) fast versus SMA(40) is essentially yesterday-close momentum with 20bps slippage accounted for... Mode B trades at open with the prior business day's signal weight, which is legitimate."*
>
> *"Mode B shifts weights on the business calendar, so Monday uses Friday's signal, which means the strategy can't react to weekend moves until Tuesday."*

---

### 2. Critique of Tri-Asset Diversification & Short-Horizon Momentum
> *"The 2014–2024 backtest period is a massive BTC bull run, and with 50% allocation to trend-following on BTC, the diversification story is weak — BTC drives nearly all the CAGR, and all three assets trended upward. The parameters (SMA(2)/40 for BTC, SMA(10)/100 for TradFi, vt=0.15, clip 1.5) look suspiciously tuned to this specific period with no out-of-sample validation, and using different lookbacks per asset class screams overfitting."*
>
> *"Mode B's degradation is telling: Sharpe drops 11% and max drawdown balloons 50% with just one day of lag, suggesting the SMA(2) signal captures fragile short-horizon momentum that evaporates within hours — the low drawdown in Mode A might be an artifact of near-instant exits during crashes rather than genuine robustness."*

---

### 3. Execution Physics & Return Accounting
> *"For the execution mechanics: the signals use close prices but trade at the next open, which works for TradFi (overnight gap is legitimate) and is semi-implementable for BTC (assuming exactly 00:00 UTC daily execution), though the reindex and ffill logic checks out since BTC trades every day. Cash is simply 1 minus the signal weight."*
>
> *"On the Sharpe calculation, the excess return already deducts borrowing costs on leveraged days, and using raw return volatility rather than excess volatility is standard practice."*

---

### 4. Remaining Statistical & Correlation Vulnerabilities
> *"The real gap is the lack of statistical rigor: no bootstrap confidence intervals, no deflated Sharpe, no walk-forward validation, and critically, no comparison to a simple 50/25/25 buy-and-hold vol-targeted baseline, which would likely deliver 1.0-1.2 Sharpe versus the claimed 19% CAGR. The correlation assumption of three uncorrelated assets also doesn't hold — BTC and SPY have drifted toward 0.4-0.6 correlation post-2020."*

---

## Key Takeaways for Institutional Deployment

1. **Plumbing & Mechanics Check Out:** Fable confirmed that the SPY calendar reindexing, forward-filling, cash borrowing deductions, and Mode B execution lag logic are mathematically sound.
2. **Sensitivity of SMA(2/40):** The `SMA(2)` vs `SMA(40)` signal on Bitcoin relies heavily on fast exits. When forced to wait 24 hours (Mode B), Max Drawdown increases from `-11.39%` to `-17.10%` (still below `< 20%`).
3. **Correlation Drift:** Post-2020, Bitcoin and SPY have become more positively correlated (`0.4 to 0.6`), meaning Gold (`GLD`) remains the primary true non-correlated diversifier during equity market sell-offs.
