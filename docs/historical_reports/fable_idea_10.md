# IDEA 10 — "CHRONOS": Lag-Robust Alpha via Laplace-Transform Shrinkage + Distributionally Robust Latency Sizing

The final piece of the ten. Ideas 1–9 generate edge; Idea 10 guarantees the edge **survives the journey from decision to fill**. Most live-vs-backtest Sharpe collapse is not alpha death — it is *unmodeled signal aging during the execution queue*. CHRONOS makes latency a first-class random variable in the optimizer.

---

## 1. Setup

- Signal at decision time: $s_t$, with conditional alpha $\mathbb{E}[r_{t+\tau} \mid s_t] = \phi(\tau)\, s_t$
- **Decay kernel** (calibrated per-alpha): $\phi(\tau) = e^{-\lambda \tau}$, where $\lambda = \ln 2 / h$ and $h$ = alpha half-life
- **Execution latency** $\tau \sim P_\tau$, *unknown*, living in a Wasserstein ambiguity ball around the empirical fill-time distribution:

$$\mathcal{U}_\epsilon = \{ P : W_1(P, \hat{P}_\tau) \le \epsilon \}$$

Crucially, $\epsilon$ is made **state-dependent**: $\epsilon_t = \epsilon_0 (1 + \beta \cdot \text{QueueDepth}_t + \gamma \cdot \text{VIX}_t)$ — latency uncertainty widens exactly when markets stress.

## 2. The Key Object: Worst-Case Laplace Transform

Expected realized alpha per unit signal is the **Laplace transform of the latency distribution evaluated at the decay rate**:

$$\bar{\phi}(P) = \mathbb{E}_{P}\!\left[e^{-\lambda \tau}\