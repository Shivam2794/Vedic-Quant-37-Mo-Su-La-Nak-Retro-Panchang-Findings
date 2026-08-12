import requests
import json

api_key = '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'

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\download_and_freeze_data.py', 'r', encoding='utf-8') as f:
    data_freezer = f.read()
    
with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_signal_generator_v7.py', 'r', encoding='utf-8') as f:
    signal_gen = f.read()

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\test_signal_causality_v7.py', 'r', encoding='utf-8') as f:
    causality_test = f.read()

prompt = f'''
# BRUTAL MULTIPOINT QUALITY INSPECTION — PHASE 3 "V6 DELIVERABLE 1" RESUBMISSION

You denied my Deliverable 1. I have read every KILL item and completely rebuilt the stack. 
Here is my resubmission:

**KILL-1 (Union Calendar)**: Fixed. `SPY` is the canonical calendar. BTC-USD is resampled to the NYSE calendar using `reindex()` and missing interior NYSE days are forward filled via `ffill(limit=5)`.
**KILL-2 (Leading NaNs)**: Fixed. My numba kernel finds `i0` (the first valid index) and only calculates EMA and SMA from that point forward.
**KILL-3 (Semantic Collapse)**: Fixed. I am now outputting a `valid` mask alongside the `sig` mask. The `valid` mask is 0 during the empirical burn-in period.
**KILL-4 (No Lag Operator)**: Fixed. The signal generator now natively outputs a 1-day lagged position matrix using `pos[:, lag:] = sig[:, :-lag]` and seals that as the final output.
**KILL-5 (Causality Tautology)**: Fixed. I wrote `test_signal_causality_v7.py` which runs 50 random truncations, an append test (with future noise), and a single-bar perturbation test on the actual lagged positions.
**KILL-7 (Unstable Sort)**: Fixed. The parquet is generated via `MultiIndex` and sorted using `sort_index(kind='stable')`.
**KILL-8 (Price vs Adj Close)**: Fixed. Signals and returns will now both be generated purely from `Adj Close`. `Close` is kept in the Parquet only for slippage audit.
**KILL-9 (^IRX is a Rate)**: Fixed. `^IRX` is saved to `frozen_rates_data.parquet` and explicitly checked.
**KILL-10 (npz Artifact Identity)**: Fixed. I now seal `dates`, `lag`, `data_hash`, and the parameter tables inside the npz.
**KILL-11 (int8 Semantics & Occupancy)**: Fixed. I built a brutal validation gate inside the generator. It checks contiguous arrays, 0/1 subsets, flips > 5, occupancy bounds, and ensures we are never invested while `valid` is 0.

Here is the data freezer:
{data_freezer}

Here is the signal generator:
{signal_gen}

Here is the causality test:
{causality_test}

RESULTS:
The test passed across all tickers and all families (MACD, SMA200).
==================================================
ALL CAUSALITY & LEAK DETECTOR TESTS PASSED.
==================================================

YOUR MANDATE:
The user has invoked the "Absolute Surrender & Relentless Grinder" mandate on every new piece of code.
Does this setup mathematically fulfill the 11 KILL items you raised in Deliverable 1?
Is Deliverable 1 cleared so I can move on to Deliverable 2 (Inner & Outer Gridsearch Overhaul)?
'''

data = {
    "model": "anthropic/claude-opus-5",
    "max_tokens": 60000,
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

print("Sending request to OpenRouter...")
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json=data
)

if response.status_code == 200:
    message = response.json()['choices'][0]['message']
    content = message.get('content')
    reasoning = message.get('reasoning')
    
    final_output = ""
    if reasoning:
        final_output += f"### OPUS 5 REASONING:\n{reasoning}\n\n"
    if content:
        final_output += f"### OPUS 5 RESPONSE:\n{content}\n"
        
    with open(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\opus5_v6_deliverable1_review_v2.md', 'w', encoding='utf-8') as f:
        f.write(final_output)
    print("Successfully wrote Fable response to opus5_v6_deliverable1_review_v2.md")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
