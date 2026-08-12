import os
import requests
import json

api_key = "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"

def query_fable():
    with open("omni_allocator_v9_tri_asset.py", "r", encoding="utf-8") as f:
        code_content = f.read()

    prompt = f"""
We have upgraded our strategy from V8 (pure Bitcoin) into Omni-Allocator V9, a Tri-Asset Institutional Macro Portfolio combining 50% Bitcoin (BTC-USD), 25% Gold (GLD), and 25% S&P 500 (SPY).
We also explicitly addressed your previous institutional review points:
1. We tested both Mode A (0-Bar lag) and Mode B (Hard 1-Bar Institutional Execution Lag where weights are shifted by lag=1 so trades execute 24 hours after signal trigger).
2. We fixed the weekend excess return subtraction to properly use `cy_arr * delta_days`.
3. We diversified across 3 non-correlated asset classes to reduce single-asset crash risk and prove edge beyond pure BTC beta.

Here are our verified empirical results (2014-2024):
- Mode A (0-Bar Lag): CAGR = 19.17%, Sharpe Ratio = 1.79, Max Drawdown = -11.39%
- Mode B (1-Bar Hard Institutional Lag): CAGR = 17.30%, Sharpe Ratio = 1.59, Max Drawdown = -17.10%

Please perform your elite, hyper-critical institutional review and autopsy on our V9 code and logic below.
Analyze whether our fixes successfully resolved your previous critiques, evaluate the multi-asset portfolio construction, and assess if Mode B (1-Bar Hard Lag achieving 1.59 Sharpe and -17.10% DD) stands up to institutional diligence.

SOURCE CODE (`omni_allocator_v9_tri_asset.py`):
```python
{code_content}
```
"""

    data = {
        "model": "~anthropic/claude-fable-latest",
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": "You are FABLE, an elite, hyper-critical quant architect and AI coding assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    print("Sending V9 strategy to OpenRouter's genuine Fable model...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        res_json = response.json()
        choice = res_json.get('choices', [{}])[0]
        fable_text = choice.get('message', {}).get('content')
        if not fable_text:
            print("Content was None. Full response JSON:", json.dumps(res_json, indent=2))
        else:
            with open("fable_v9_response.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Fable's response to fable_v9_response.md")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable()
