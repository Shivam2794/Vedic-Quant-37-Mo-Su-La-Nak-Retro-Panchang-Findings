# V5 Walk-Forward OOS Validation Report — Phase 4 & 5

> Generated: 2026-08-06T10:18:43.535128
> IS Window: 1260 days (5y) | OOS Window: 252 days (1y) | Step: 252 days
> Total Folds: 27

---

## Phase 4 — Generation Convergence Log

| Gen | Best CAGR | Net Return | Max DD | Front-1 Size |
|---|---|---|---|---|
| 00 | -1.20% | -36.66% | 49.98% | 2 |
| 01 | -0.67% | -15.51% | 20.57% | 1 |
| 02 | -0.16% | -10.40% | 13.49% | 2 |
| 03 | -0.18% | -10.17% | 7.44% | 3 |
| 04 | +0.10% | -9.87% | 3.31% | 1 |
| 05 | -0.14% | -6.32% | 6.37% | 3 |
| 06 | +0.00% | -3.30% | 0.00% | 1 |
| 07 | +0.00% | -0.60% | 0.00% | 1 |
| 08 | +0.00% | -0.10% | 0.00% | 1 |
| 09 | +0.00% | +0.00% | 0.00% | 1 |
| 10 | +0.00% | +0.00% | 0.00% | 8 |
| 11 | +0.00% | +0.00% | 0.00% | 20 |
| 12 | +0.00% | +0.00% | 0.00% | 20 |
| 13 | +0.00% | +0.00% | 0.00% | 20 |
| 14 | +0.00% | +0.00% | 0.00% | 20 |
| 15 | +0.00% | +0.00% | 0.00% | 20 |
| 16 | +0.00% | +0.00% | 0.00% | 20 |
| 17 | +0.00% | +0.00% | 0.00% | 20 |
| 18 | +0.00% | +0.00% | 0.00% | 20 |
| 19 | +0.00% | +0.00% | 0.00% | 20 |
| 20 | +0.00% | +0.00% | 0.00% | 20 |

---

## Phase 5 — Per-Fold OOS Results

| Fold | IS CAGR | OOS CAGR | OOS MaxDD | OOS Sharpe | IS/OOS Ratio | OOS > 0? |
|---|---|---|---|---|---|---|
| 01 | +33.19% | -16.00% | 34.12% | +0.324 | -2.07x | NO |
| 02 | +37.16% | -1.62% | 20.57% | -0.799 | -22.88x | NO |
| 03 | +67.94% | +0.59% | 15.69% | +0.149 | 114.34x | YES |
| 04 | +23.07% | -9.34% | 15.31% | -1.084 | -2.47x | NO |
| 05 | +19.59% | +9.67% | 6.33% | +0.721 | 2.03x | YES |
| 06 | +22.83% | +1.64% | 3.22% | +0.653 | 13.94x | YES |
| 07 | +21.07% | +6.50% | 7.02% | +0.083 | 3.24x | YES |
| 08 | +20.58% | -8.30% | 10.02% | -1.543 | -2.48x | NO |
| 09 | +43.75% | -10.01% | 15.51% | -0.724 | -4.37x | NO |
| 10 | +21.11% | -11.78% | 16.29% | -1.062 | -1.79x | NO |
| 11 | +0.99% | -0.57% | 1.42% | +1.413 | -1.73x | NO |
| 12 | +16.41% | -22.25% | 24.70% | -1.414 | -0.74x | NO |
| 13 | +30.83% | -37.02% | 44.20% | -1.001 | -0.83x | NO |
| 14 | +10.97% | +3.05% | 3.21% | -0.897 | 3.60x | YES |
| 15 | +53.75% | +37.55% | 13.58% | +1.787 | 1.43x | YES |
| 16 | +40.22% | -6.63% | 12.34% | -0.707 | -6.06x | NO |
| 17 | +21.96% | +5.12% | 11.64% | +0.815 | 4.29x | YES |
| 18 | +29.43% | -12.80% | 19.25% | -0.864 | -2.30x | NO |
| 19 | +32.11% | +11.14% | 3.61% | +1.625 | 2.88x | YES |
| 20 | +28.31% | +10.12% | 29.35% | +0.300 | 2.80x | YES |
| 21 | +41.28% | -23.58% | 32.55% | -0.838 | -1.75x | NO |
| 22 | +24.69% | +5.02% | 11.03% | +0.870 | 4.92x | YES |
| 23 | +41.49% | +34.78% | 19.91% | +1.846 | 1.19x | YES |
| 24 | +18.22% | -4.52% | 7.60% | -0.940 | -4.03x | NO |
| 25 | +31.78% | +6.09% | 17.88% | +0.027 | 5.21x | YES |
| 26 | +56.95% | +64.22% | 17.61% | +1.567 | 0.89x | YES |
| 27 | +41.43% | -7.53% | 22.13% | -0.419 | -5.50x | NO |

---

## Aggregate OOS Statistics

| Metric | Value |
|---|---|
| Mean IS CAGR | +30.78% |
| Mean OOS CAGR | +0.87% |
| Mean OOS Max DD | 16.15% |
| Mean OOS Sharpe | -0.004 |
| Folds with OOS CAGR > 0% | 13/27 (48.1%) |
| Mean IS/OOS Ratio | 35.29x |

---

## OOS Integrity Verification

- **OOS Contamination**: IS GA receives ONLY IS-sliced arrays. OOS arrays are sliced separately
  and passed to OOS simulation AFTER champion is frozen. Zero contamination by construction.
- **Champion Selection**: Champion selected by `max(population, key=lambda g: g.net_return)`
  using IS Pareto frontier only. OOS metric never influences selection.
- **Fold Boundary**: `is_end == oos_start` enforced for every fold. Zero overlap, zero gap.
- **No Re-fitting**: OOS simulation receives frozen `champion.weights`, `stop_loss`,
  `max_leverage`, `v_th`. No parameter updates on OOS data.