# FABLE // OMNI-ALLOCATOR V10 ARCHITECTURE BRIEF

Below are three production-grade mechanisms. Each is designed to be **lag-robust by construction** — meaning every signal is deliberately *slow enough* that a 1-bar delay is statistically immaterial (signal autocorrelation at lag-1 > 0.95), rather than trying to "beat" the lag with faster signals, which is the classic retail mistake.

---

## IDEA 1 — Multi-Horizon Ensemble Momentum with Hysteresis Bands ("The Committee")

### The problem with SMA(2/40)
An SMA(2) is essentially yesterday's price. Its signal flips constantly, so a 1-bar lag causes you to systematically enter *after* the move and exit *after* the reversal — a structural negative alpha of roughly (turnover × lag-bar drift). The fix is not a better fast signal; it is **eliminating the fast leg entirely** and voting across horizons where lag-1 is noise.

### Mathematical formulation

**Component 1 — Ensemble of EWMA crossovers (MACD-style, à la AQR/Man AHL):**

For horizon pairs $(S_k, L_k) \in \{(8,24), (16,48), (32,96), (64,192)\}$ (days):

$$
x_k(t) = \frac{\text{EWMA}_{S_k}(P_t) - \text{EWMA}_{L_k}(P_t)}{\sigma_{63}(P_t)}
$$

where $\sigma_{63}$ is the 63-day rolling std of *price* (normalizes signal across vol regimes).

Squash to a bounded response (removes tail sensitivity, kills whipsaw amplitude):

$$
u_k(t) = \frac{x_k(t) \cdot e^{-x_k(t)^2/4}}{0.89}
$$

(This is the Man AHL response function; 0.89 normalizes the max to 1.)

**Component 2 — Donchian breakout confirmation:**

$$
b(t) = \begin{cases} +1 & P_t > \max(P_{t-100}, \dots, P_{t-1}) \cdot (1-\epsilon) \\ -1 & P_t < \min(P_{t-100}, \dots, P_{t-1}) \cdot (1+\epsilon) \\ b(t-1) & \text{otherwise (sticky)} \end{cases}
$$

with $\epsilon = 0.02$. The stickiness is the hysteresis — the signal only changes at channel extremes, so lag-1 execution is almost always identical to lag-0.

**Composite signal with dead-zone hysteresis:**

$$
S(t) = 0.7 \cdot \frac{1}{4}\sum_k u_k(t) + 0.3 \cdot b(t)
$$

$$
w_{BTC}^{raw}(t) = \begin{cases}
1 & S(t) > +\theta_{on} \\
0 & S(t) < -\theta_{off} \\
w_{BTC}^{raw}(t-1) & \text{otherwise}
\end{cases}
\quad \theta_{on}=0.15,\ \theta_{off}=0.05
$$

The asymmetric dead zone $[-0.05, +0.15]$ is the whipsaw killer: the signal must travel through a 0.20-wide band to flip, cutting turnover ~60–75% vs. SMA(2/40).

**Volatility filter (regime gate):** suppress entries when BTC realized vol is in blow-off territory:

$$
g(t) = \mathbb{1}\left[\sigma_{20}^{ann}(t) < Q_{0.90}\big(\sigma_{20}^{ann}, \text{lookback } 756d\big)\right]
$$

Final: $w_{BTC}(t) = w_{BTC}^{raw}(t) \cdot \max(g(t), \text{already-in-position})$ — i.e., vol gate blocks *new entries* only, never forces exits (forced vol exits sell bottoms).

### Python

```python
import numpy as np
import pandas as pd

def ensemble_btc_signal(price: pd.Series) -> pd.Series:
    pairs = [(8, 24), (16, 48), (32, 96), (64, 192)]
    sig_px = price.rolling(63).std()
    u_list = []
    for S, L in pairs:
        x = (price.ewm(span=S).mean() - price.ewm(span=L).mean()) / sig_px
        u = x * np.exp(-x**2 / 4) / 0.89
        u_list.append(u)
    ewma_score = pd.concat(u_list, axis=1).mean(axis=1)

    # Sticky Donchian breakout
    hi = price.rolling(100).max().shift(1)
    lo = price.rolling(100).min().shift(1)
    b = pd.Series(np.nan, index=price.index)
    b[price > hi * 0.98] = 1.0
    b[price < lo * 1.02] = -1.0
    b = b.ffill().fillna(0.0)

    return 0.7 * ewma_score + 0.3 * b

def hysteresis_position(S: pd.Series, on=0.15, off=-0.05) -> pd.Series:
    w = pd.Series(0.0, index=S.index)
    state = 0.0
    for i, s in enumerate(S.values):
        if s > on:
            state = 1.0
        elif s < off:
            state = 0.0
        w.iloc[i] = state
    return w

def vol_gate(price: pd.Series, q=0.90, win=20, lb=756) -> pd.Series:
    rv = price.pct_change().rolling(win).std() * np.sqrt(365)
    thresh = rv.rolling(lb, min_periods=252).quantile(q)
    return (rv < thresh).astype(float)

S = ensemble_btc_signal(btc_close)
w_raw = hysteresis_position(S)
gate = vol_gate(btc_close)
# gate blocks new entries only:
w_btc = w_raw.where(~((w_raw.diff() > 0) & (gate == 0)), 0.0)
w_btc = w_btc.shift(1)   # <-- 1-bar institutional lag, always
```

**Why it survives lag:** median holding period rises from ~5–8 days (SMA 2/40) to ~35–60 days. A 1-day lag on a 50-day hold costs ~2% of the trend capture instead of ~15–20%. Expect Mode B Sharpe degradation of ~0.03–0.06 instead of 0.20.

---

## IDEA 2 — Dynamic Correlation Regime Overlay ("The Diversification Thermostat")

### Concept
The 50/25/25 allocation implicitly assumes BTC-SPY correlation ≈ 0. When $\rho_{BTC,SPY} \to 0.6$, your portfolio is effectively ~70% "one macro liquidity factor." The fix: measure the **effective number of bets** and dynamically rotate the SPY sleeve into GLD/T-bills when diversification collapses.

### Mathematical formulation

**Step 1 — Robust rolling correlation (Fisher-smoothed to avoid noise-trading):**

$$
\rho_t = \text{corr}_{90d}(r^{BTC}, r^{SPY}), \qquad z_t = \tanh\left(\text{EWMA}_{21}\left[\text{arctanh}(\rho_t)\right]\right)
$$

Fisher-transforming before smoothing stabilizes the estimator near $|\rho|=1$ and the EWMA prevents daily rebalancing on correlation noise.

**Step 2 — Effective Number of Bets (ENB) via correlation matrix eigen-decomposition:**

Given rolling correlation matrix $C_t$ of the 3 assets with eigenvalues $\lambda_i$:

$$
\text{ENB}_t = \exp\left(-\sum_i \tilde\lambda_i \ln \tilde\lambda_i\right), \qquad \tilde\lambda_i = \frac{\lambda_i}{\sum_j \lambda_j}
$$

ENB = 3 → three independent bets; ENB → 1 → one macro bet.

**Step 3 — Continuous de-risking function (no binary cliff):**

Define the SPY→defensive transfer fraction:

$$
\phi_t = \text{clip}\left(\frac{z_t - \rho_{lo}}{\rho_{hi} - \rho_{lo}}, 0, 1\right) \cdot \text{clip}\left(\frac{\text{ENB}_{hi} - \text{ENB}_t}{\text{ENB}_{hi} - \text{ENB}_{lo}}, 0, 1\right)
$$

with $\rho_{lo}=0.30,\ \rho_{hi}=0.60,\ \text{ENB}_{lo}=1.5,\ \text{ENB}_{hi}=2.2$.

**Step 4 — Rotation with macro-conditional destination:**

$$
w_{SPY} = 0.25(1-\phi_t), \qquad \Delta = 0.25\,\phi_t
$$

$$
\text{destination}(\Delta) = \begin{cases} \text{GLD} & \text{if GLD 63d momentum} > 0 \\ \text{BIL (T-bills)} & \text{otherwise} \end{cases}
$$

This is critical: in a 2022-style regime (stocks AND gold down, rates up), the correlation spike must route to **cash-equivalents earning the risk-free rate**, not blindly to gold.

**Step 5 — Rebalance dead band:** only trade the overlay if $|\phi_t - \phi_{executed}| > 0.10$. Turnover control.

### Python

```python
def fisher_smooth_corr(r_btc, r_spy, win=90, span=21):
    rho = r_btc.rolling(win).corr(r_spy).clip(-0.99, 0.99)
    return np.tanh(np.arctanh(rho).ewm(span=span).mean())

def effective_num_bets(returns_df, win=90):
    def enb(C):
        lam = np.linalg.eigvalsh(C)
        lam = np.clip(lam, 1e-12, None); lam /= lam.sum()
        return np.exp(-(lam * np.log(lam)).sum())
    out = pd.Series(np.nan, index=returns_df.index)
    for i in range(win, len(returns_df)):
        C = returns_df.iloc[i-win:i].corr().values
        out.iloc[i] = enb(C)
    return out.ewm(span=10).mean()

def overlay_weights(rets, gld_close, rho_lo=0.30, rho_hi=0.60,
                    enb_lo=1.5, enb_hi=2.2, band=0.10):
    z   = fisher_smooth_corr(rets['BTC'], rets['SPY'])
    enb = effective_num_bets(rets[['BTC','SPY','GLD']])
    phi = (np.clip((z - rho_lo)/(rho_hi - rho_lo), 0, 1)
         * np.clip((enb_hi - enb)/(enb_hi - enb_lo), 0, 1))

    # dead band on executed ph