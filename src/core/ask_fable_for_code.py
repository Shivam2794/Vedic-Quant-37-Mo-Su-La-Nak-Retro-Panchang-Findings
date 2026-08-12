import os
import requests
import json

api_key = "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"

def query_fable_code():
    prompt = """
You laid out an elite 9-Point Grinder to test if our 1.91 Sharpe ratio is physically real. The user has called your bluff and commanded that we run it. Furthermore, they commanded that YOU write the code for it.

Please write a Python class or set of functions `def run_fable_grinder(port_ret_series, btc_ret_series, base_60_20_20_ret_series):` that accepts pandas Series (daily returns, datetime index) and computes the exact rigorous metrics from your 9-Point Grinder:
1. Incremental Sharpe (vs base_60_20_20_ret_series).
2. Deflated Sharpe Ratio (DSR), assuming N=12 trials (use an approximation or standard DSR formula).
3. Block-Bootstrap Monte Carlo: Resample `port_ret_series` in 20-day blocks for 1000 paths, and return the 5th percentile worst-case Sharpe Ratio.
4. Drift Haircut: Rescale `btc_ret_series` drift down to a 10% annualized CAGR (while preserving daily vol), and re-evaluate the strategy. (Just provide the scaling math).
5. Regime Slices: Calculate the Sharpe Ratio for these exact slices: '2014-2017', '2018-2019', '2020-2021', '2022', '2023-2024'.
6. Cold Start: Sharpe Ratio calculated strictly post Jan-1-2018.

Write elite, vectorized Pandas/Numpy Python code. Return ONLY the code block, no markdown chat.
"""
    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {"role": "system", "content": "You are FABLE, an elite quant coder. Write pure Python code."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    print("Sending request to OpenRouter's genuine Fable model for code generation...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        res_json = response.json()
        fable_text = res_json['choices'][0]['message']['content']
        with open("fable_generated_grinder.py", "w", encoding="utf-8") as f:
            # Clean up potential markdown blocks if Fable includes them
            code = fable_text.replace("```python", "").replace("```", "").strip()
            f.write(code)
        print("Successfully wrote Fable's code to fable_generated_grinder.py")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable_code()
