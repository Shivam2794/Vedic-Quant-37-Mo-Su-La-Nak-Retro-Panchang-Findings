import os
import requests
import json

# Permanent API Key
api_key = "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"

def query_fable():
    # Read the three source code files
    try:
        with open("omni_allocator_v10_apex.py", "r") as f:
            v10_code = f.read()
        with open("omni_allocator_idea9.py", "r") as f:
            idea9_code = f.read()
        with open("omni_allocator_idea5.py", "r") as f:
            idea5_code = f.read()
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    prompt = f"""
You are FABLE, an elite, hyper-critical quant architect and AI coding assistant at a Tier-1 quantitative hedge fund.
We have executed a relentless systematic grind across 12 institutional quant ideas. We have distilled the results into our Top 3 Final Strategies.

Your task is to conduct an extreme, zero-tolerance institutional-level quality and error/bug proof check on the source codes and logics of these 3 final strategies, like your life depends on it. 

### CONTEXT
All three strategies trade a Tri-Asset portfolio (60% BTC, 20% GLD, 20% SPY) under strictly enforced "Mode B" Execution Physics:
1. All signals evaluate using data up to Close `t`.
2. Actual execution occurs precisely at Open `t+1`.
3. The index alignment bridges 365-day crypto calendars and 252-day traditional calendars seamlessly.

### THE THREE STRATEGIES
1. **Omni-Allocator V10 Apex** (Idea 4 + Idea 8/9 Synergy): Uses an 86% CPPI Drawdown Governor High-Water Mark floor.
2. **Omni-Allocator Idea 9** (The Patience Dial): Uses an EMA smoother (tau=0.85) on target weights to suppress high-frequency whipsaws.
3. **Omni-Allocator Idea 5** (The Vol-of-Vol Brake): Cuts crypto exposure when 60-day vol-of-vol exceeds the 90th percentile of its 365-day rolling history.

### YOUR MANDATE
Review the architecture, pandas logic, exact physics (slippage, delta_days weekend math, open-to-open returns), and the quantitative theories. Look for lookahead bias, parameter leakage, execution illusions, survivorship bias, cash yield inflation, or any tiny corner-case that could destroy the fund in live trading. Be absolutely brutal.

SOURCE CODE 1 (V10 Apex):
```python
{v10_code}
```

SOURCE CODE 2 (Idea 9):
```python
{idea9_code}
```

SOURCE CODE 3 (Idea 5):
```python
{idea5_code}
```

Give us your definitive, institutional-level review. Point out any remaining microscopic bugs, or confirm their absolute physical purity.
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

    print("Sending source code to OpenRouter's genuine Fable model...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        res_json = response.json()
        try:
            fable_text = res_json['choices'][0]['message'].get('content', None)
            if fable_text is None:
                print(f"Fable returned None. Raw JSON: {json.dumps(res_json, indent=2)}")
                return
            with open("fable_final_review.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Fable's brutal review to fable_final_review.md")
        except Exception as e:
            print(f"Failed to parse choices: {e}\nRaw JSON: {json.dumps(res_json, indent=2)}")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable()
