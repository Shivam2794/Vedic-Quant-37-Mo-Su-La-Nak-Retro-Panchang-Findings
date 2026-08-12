import os
import requests
import json

api_key = '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'

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_gigantic_gridsearch_v5.py', 'r', encoding='utf-8') as f:
    gridsearch_code = f.read()

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_phase3_optimizer_v2.py', 'r', encoding='utf-8') as f:
    optimizer_code = f.read()

prompt = f'''
You are The Fable X-High Reasoning Model, executing the BRUTAL MULTIPOINT QUALITY INSPECTOR persona for the Opus-8 algorithmic trading project.
You previously reviewed Phase 1C and identified 5 fatal flaws, including the lack of Nested Walk-Forward Strategy Selection, Mean-Variance bias, and BTC-USD weekend dropout.

We have completely rebuilt the engine in Phase 2 to address your flaws. We present to you the new architecture:

1. Nested Walk-Forward Gridsearch (opus8_matrix_gigantic_gridsearch_v3.py):
This engine chunks the data into 51 Walk-Forward windows (IS: 504 days, OOS: 126 days).
For EACH window, it generates the top parameters per family IN-SAMPLE, then finds the best pair combinations IN-SAMPLE across all logic gates. 
It then builds the Out-of-Sample return purely based on the IS winner.

CODE:
{gridsearch_code}

2. True Risk Parity / Equal Risk Contribution Optimizer (opus8_phase3_optimizer.py):
This engine loads the OOS returns generated above, and walk-forwards a True Risk Parity (Equal Risk Contribution) objective using SciPy SLSQP. It also deducts 5 bps per unit of turnover and accurately tracks drifted weights daily.

CODE:
{optimizer_code}

RESULTS:
The final mathematically-sealed V5 execution yielded the following:

--- 1. ALGORITHMIC WFO OVERLAY ---
Total Return : 149.01%
CAGR         : 3.64%
Max Drawdown : -14.77%
Sharpe Ratio : 0.5750

--- 2. STATIC ERC BENCHMARK (NULL HYPOTHESIS) ---
CAGR         : 14.49%
Sharpe Ratio : 0.9692
Max Drawdown : -42.42%

YOUR MANDATE:
The user has invoked the "Absolute Surrender & Relentless Grinder" mandate. We fixed the matrix transpose memory read, the boolean promotion, and the risk parity 0-variance explosion.
As you predicted, the Algorithmic Overlay is mathematically value-destroying (3.64% CAGR) compared to the Static Null Hypothesis (14.49% CAGR). 
Is the architecture finally free of code rot, leaks, and logic bugs? Have we successfully proved that this particular universe/strategy has negative edge? 
Do not hold back. If the logic is fully sealed, declare Absolution.
'''

data = {
    'model': 'anthropic/claude-opus-5',
    'messages': [
        {'role': 'system', 'content': 'You are OPUS 5, an elite, hyper-critical quant architect and AI coding assistant.'},
        {'role': 'user', 'content': prompt}
    ]
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'HTTP-Referer': 'https://localhost',
    'X-Title': 'Fable Agent',
    'Content-Type': 'application/json'
}

print('Sending request to OpenRouter...')
response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    data=json.dumps(data)
)

if response.status_code == 200:
    res_json = response.json()
    fable_text = res_json['choices'][0]['message']['content']
    with open(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\opus5_fable_review_v3.md', 'w', encoding='utf-8') as f:
        f.write(fable_text)
    print('Successfully wrote Fable response to opus5_fable_review_v3.md')
else:
    print(f'Error {response.status_code}: {response.text}')
