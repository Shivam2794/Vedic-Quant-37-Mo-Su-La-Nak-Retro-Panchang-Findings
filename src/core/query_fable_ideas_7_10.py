import os
import requests
import json

api_key = "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"

def query_fable_ideas_7_10():
    prompt = """
You just gave us Ideas 1 through 6:
1. The Turbulence Tripwire (Mahalanobis Regime Shield)
2. The Drawdown Governor (CPPI-Style Risk Budget with Regenerating Floor)
3. The Efficiency Chameleon (Adaptive Lookback via Fractal Efficiency)
4. The Jump Auditor (Bipower Variation Gap-Risk Budget for BTC)
5. The Alpha Half-Life Certificate (Lag-Robust Signal Admission)
6. The Tranching Engine (Rebalance-Date Diversification)

Now please give us IDEAS 7, 8, 9, and 10 to complete the 10 Institutional Creative Genius Quant Ideas! Include mathematical formulations and why they systematically protect Sharpe/drawdown under realistic execution lags.
"""

    data = {
        "model": "~anthropic/claude-fable-latest",
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": "You are FABLE, an elite, hyper-critical quant architect and creative genius AI coding assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    print("Sending request for Ideas 7 to 10 to OpenRouter's genuine Fable model...")
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
            with open("fable_ideas_7_10.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Fable's ideas 7-10 response to fable_ideas_7_10.md")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable_ideas_7_10()
