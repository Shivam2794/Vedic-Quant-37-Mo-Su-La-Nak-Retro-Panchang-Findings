# Original User Request

## Initial Request — 2026-06-18T10:59:33-05:00

# Teamwork Project Prompt

An exploratory Neural Network machine learning pipeline to find, predict, and prove hidden trends and volatility patterns in SPY, QQQ, and DIA using a massive dataset of continuous Z-Axis Vedic astrological features. The agents must act as a 'Vedic Quant Architect' and 'Brutal Multipoint Quality Inspector' throughout the process.

Working directory: `C:\Users\Shivam Patel\.gemini\antigravity\scratch`
Integrity mode: development

## Requirements

### R1. PyTorch Neural Network Architecture
Build a Neural Network in PyTorch designed for discovering complex, non-linear feature combinations and groups. To aggressively combat the high risk of overfitting, the architecture must implement strict regularization techniques (e.g., heavy dropout, weight decay, early stopping).

### R2. Exploratory Target Prediction (SPY/QQQ/DIA)
The primary goal is exploratory pattern recognition. The pipeline must test SPY, QQQ, and DIA to predict trend direction or volatility clusters using the engineered ephemeris features. The swarm should analyze all three and select the asset with the strongest signal.

### R3. Rigorous Walk-Forward Validation
To mathematically prove that any discovered edge is not overfit, the pipeline must use strict Walk-Forward Cross Validation (such as Purged K-Fold or TimeSeriesSplit with embargo). Standard randomized train/test splits are strictly prohibited due to time-series data leakage.

## Acceptance Criteria

### Verification & Performance Metrics
- [ ] A PyTorch pipeline script executes end-to-end without errors, performs Walk-Forward CV, and saves an Evaluation Report (CAGR, Max Drawdown, Sharpe Ratio) to disk.
- [ ] The out-of-sample performance mathematically proves it beats a random "Dummy Predictor" baseline.
- [ ] The out-of-sample performance mathematically proves it beats a standard "Buy and Hold" baseline for the chosen ETF.
