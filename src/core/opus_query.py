import os
import requests
import json

api_key = "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"

def query_opus(prompt):
    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {"role": "system", "content": "You are Opus 5, an elite, hyper-critical quant architect and xhigh reasoning model."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Opus 5 Agent",
        "Content-Type": "application/json"
    }

    print("Sending request to OpenRouter's Opus model...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        res_json = response.json()
        opus_text = res_json['choices'][0]['message']['content']
        with open(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\opus5_fable_review_v2.md", "w", encoding="utf-8") as f:
            f.write(opus_text)
        print("Successfully wrote Opus's response to artifacts.")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    prompt = """
I am presenting you with the logic and code for Opus-8 Absolution, a massive gridsearch quant system. 
The plan is to gridsearch all combinations of these all indicators with all parameters with all ensemble techniques and their values for all our etfs (TQQQ, UPRO, TLT, GLD, BTC-USD, SPY, QQQ).

Here is the code for the Walk-Forward Optimizer:
```python
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt

TICKERS = ['TQQQ', 'UPRO', 'TLT', 'GLD', 'BTC-USD']

def calc_metrics(returns):
    cum_ret = np.exp(np.log1p(returns).cumsum())
    total_ret = cum_ret.iloc[-1] - 1
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    
    years = len(returns) / 252.0
    cagr = (cum_ret.iloc[-1]) ** (1.0 / years) - 1.0 if years > 0 else 0.0
    
    ann_ret = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0
    
    win_rate = (returns > 0).sum() / (returns != 0).sum()
    
    return total_ret, max_dd, sharpe, win_rate, cum_ret, cagr

def optimize_weights(mean_rets, cov_matrix):
    def neg_sharpe(weights):
        port_ret = np.sum(mean_rets * weights)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        if port_vol == 0: return 0
        return - (port_ret / port_vol)
        
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    bounds = tuple((0.05, 0.40) for _ in range(len(TICKERS)))
    init_guess = [1.0 / len(TICKERS)] * len(TICKERS)
    
    result = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x if result.success else np.array(init_guess)

# df is the strategy returns. Walk-Forward Optimization (Rolling Risk Parity)
lookback = 252
rebalance_freq = 21

portfolio_returns = np.zeros(len(df))
current_weights = np.array([1.0 / len(TICKERS)] * len(TICKERS))

for i in range(len(df)):
    if i >= lookback and i % rebalance_freq == 0:
        window = df.iloc[i-lookback:i]
        mean_rets = window.mean() * 252
        cov_matrix = window.cov() * 252
        current_weights = optimize_weights(mean_rets, cov_matrix)
        
    # Calculate daily return for portfolio
    daily_ret = np.dot(df.iloc[i].values, current_weights)
    portfolio_returns[i] = daily_ret
```

And in the portfolio builder, we nullify the return to prevent data padding/zero-variance leakage when an asset (like BTC-USD or TQQQ) did not exist yet:
```python
        strat_ret = (raw_ret * is_invested) - costs
        # Nullify returns where the asset didn't exist
        strat_ret[np.isnan(orig_close)] = np.nan
        returns_dict[ticker] = strat_ret
```
The optimizer then does `df = df.dropna()` which correctly truncates the backtest to 2014-2026, the overlapping period where ALL assets actually existed.

Please provide a brutally meticulous and intelligent review of this Walk-Forward Optimization logic and the entire gridsearch plan.
"""
    query_opus(prompt)
