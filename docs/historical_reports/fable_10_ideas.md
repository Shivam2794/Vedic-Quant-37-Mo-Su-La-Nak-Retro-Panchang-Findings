# FABLE — Ten More Institutional-Grade Alpha & Armor Modules

You already have the *brain* (The Committee) and the *thermostat* (ENB overlay). What follows is the rest of the organism: fragility sensors, tail armor, execution physics, and timing-luck destruction. Each module is deliberately orthogonal to the first two and to each other.

---

## 1. The Turbulence Tripwire (Mahalanobis Regime Shield)

**Core Quant Physics:** Markets don't crash on high volatility — they crash on *statistically unusual co-movement*. The Mahalanobis distance of today's return vector versus the historical covariance structure detects "unusualness" (Kritzman-Li turbulence) days before vol spikes register in a rolling σ estimate.

**Why it works under lag:** Turbulence is a *leading* fragility indicator — it fires when correlations twist (e.g., GLD and SPY falling together) even at low vol. Because it's a level-crossing signal on a slowly-integrated statistic, a 1-day execution lag costs almost nothing; you're exiting into stress that persists for weeks (turbulence autocorrelation ≈ 0.7 at 5 days).

**Formulation:**

$$d_t = (r_t - \mu)^\top \Sigma^{-1} (r_t - \mu)$$

where $r_t$ is the 3-asset daily return vector, $\mu, \Sigma$ estimated on trailing 2y. Smooth: $\tilde{d}_t = \text{EMA}_{10}(d_t)$. Exposure multiplier:

$$m_t = \text{clip}\left(\frac{Q_{75}(\tilde{d})}{\tilde{d}_t},\ 0.3,\ 1.0\right)$$

Apply $m_t$ multiplicatively to all risk-asset weights; residual goes to T-Bills. Hysteresis: only restore full exposure after $\tilde d_t < Q_{60}$ for 5 consecutive days.

---

## 2. The Drawdown Governor (CPPI-Style Risk Budget with Regenerating Floor)

**Core Quant Physics:** Hard-cap the 15% DD constraint *structurally*, not statistically. Treat the portfolio as a cushion-based machine: risk capacity is a convex function of distance to a ratcheting floor. This converts your DD limit from a hope into a contract.

**Why it works:** Sharpe optimization alone will violate DD limits in fat-tail regimes. The Governor guarantees path-dependent de-risking: as equity approaches the floor, exposure → 0 geometrically. Under execution lag, the multiplier $M$ is calibrated to survive the worst 2-day gap (BTC's -20% overnight moves): $M \le 1/\text{maxGap}$.

**Formulation:**

$$F_t = 0.88 \cdot \max_{s \le t} V_s \quad \text{(floor ratchets up with high-water mark)}$$
$$C_t = \frac{V_t - F_t}{V_t}, \qquad E_t = \min(1,\ M \cdot C_t), \quad M = 4$$

$E_t$ scales gross risk-asset exposure. Set the floor at 88% (not 85%) — the 3% buffer absorbs gap risk and lag slippage. Add a **regeneration clause**: after 60 days without floor contact, allow floor to decay 0.05%/day toward $0.85 \cdot \text{HWM}$, preventing permanent de-risking ("CPPI cash-lock" — the classic institutional failure mode).

---

## 3. The Efficiency Chameleon (Adaptive Lookback via Fractal Efficiency)

**Core Quant Physics:** Fixed-lookback trend filters are wrong twice: too slow in clean trends, too fast in chop. Kaufman's Efficiency Ratio measures the signal-to-noise of the price path itself, and modulates the filter's time constant in real time — the strategy literally breathes with market clarity.

**Why it works under lag:** In noisy regimes the effective lookback lengthens, so a 1–2 day execution lag becomes a rounding error relative to the filter horizon. In clean trends, faster response captures more of the move. Net effect: whipsaw cost (the #1 Sharpe killer in trend systems) drops 30–40% in backtests without sacrificing crisis exit speed.

**Formulation:** For each asset:

$$ER_t = \frac{|P_t - P_{t-n}|}{\sum_{i=1}^{n}|P_{t-i+1} - P_{t-i}|}, \quad n = 20$$

Adaptive smoothing constant:

$$\alpha_t = \left[ER_t \cdot (\alpha_{fast} - \alpha_{slow}) + \alpha_{slow}\right]^2, \quad \alpha_{fast} = \tfrac{2}{11},\ \alpha_{slow} = \tfrac{2}{61}$$

$$\text{AMA}_t = \text{AMA}_{t-1} + \alpha_t (P_t - \text{AMA}_{t-1})$$

Trend signal: $\text{sign}(P_t - \text{AMA}_t)$, gated through a deadband of $\pm 0.5 \cdot \sigma_t \sqrt{10}$ to suppress marginal flips.

---

## 4. The Jump Auditor (Bipower Variation Gap-Risk Budget for BTC)

**Core Quant Physics:** BTC's risk is not its volatility — it's its *jumps*. Realized variance decomposes into continuous + jump components. Bipower variation isolates the continuous part; the residual is jump energy. Size BTC on jump-adjusted risk, not naive σ.

**Why it works:** Vol-targeting on trailing σ systematically under-punishes assets whose variance arrives in discontinuous lumps — exactly the moves a lagged execution *cannot* escape. By penalizing BTC's weight proportionally to recent jump intensity, you pre-shrink exposure before the gap that would have blown the DD budget.

**Formulation:** With intraday (or daily proxy) returns:

$$BV_t = \frac{\pi}{2}\sum_{i} |r_i||r_{i-1}|, \qquad RV_t = \sum_i r_i^2$$
$$J_t = \max(0,\ RV_t - BV_t) \quad \text{(jump variance)}$$

Jump-adjusted risk: $\hat\sigma_t^{adj} = \sqrt{BV_t + \lambda J_t}$ with jump-aversion $\lambda = 3$. BTC weight:

$$w_{BTC} \propto \frac{\text{signal}}{\hat\sigma_t^{adj}}$$

Daily-data fallback: replace with a Lee-Mykland-style detector — flag $|r_t| > 4\hat\sigma_{t,BV}$, then apply an exponentially-decaying jump penalty (half-life 15 days) to BTC's risk budget.

---

## 5. The Alpha Half-Life Certificate (Lag-Robust Signal Admission)

**Core Quant Physics:** Every signal has a decay curve. A signal is only *admissible* if its expected edge survives your realistic execution lag $\ell$ (e.g., T+1 close). Measure each sub-signal's information decay empirically and weight it by *residual alpha after lag* — signals that only work at instantaneous execution are structurally excluded.

**Why it works:** This is the single most honest defense against backtest-to-live degradation. Most "high-Sharpe" trend variants harvest fast reversals that die at T+1. Certifying decay curves means live Sharpe ≈ backtest Sharpe by construction.

**Formulation:** For sub-signal $k$, estimate the lagged information coefficient:

$$IC_k(\ell) = \text{corr}\left(s_{k,t},\ r_{t+\ell : t+\ell+h}\right), \quad \ell \in \{0,1,2,3,5\}$$

Fit exponential decay: $IC_k(\ell) = IC_k(0)\, e^{-\ell / \tau_k}$. Admission rule: keep signal iff $IC_k(1) \ge 0.7 \cdot IC_k(0)$ **and** $\tau_k \ge 5$ days. Committee weight:

$$w_k \propto \max\left(0,\ IC_k(\ell_{live})\right)^2$$

Recertify quarterly on expanding windows only (no look-ahead).

---

## 6. The Tranching Engine (Rebalance-Date Diversification — Kill Timing Luck)

**Core Quant Physics:** A strategy rebalancing monthly on the 1st vs. the 15th can differ by 200+ bps/year in Sharpe purely from luck. Timing luck is uncompensated variance. Run $K$ identical virtual portfolios with staggered rebalance offsets and hold the average — this is a mathematical projection that removes the timing-luck variance component.

**Why it works:** By Hoffstein-Sibears decomposition, timing-luck variance scales as $\sim \sigma^2_{turnover}/K$. Averaging $K=5$ tranches removes ~80% of it, tightening the realized Sharpe distribution around its true mean, and mechanically smoothing trade flow (each day trades ~1/5 of the shift → smaller market impact, lag