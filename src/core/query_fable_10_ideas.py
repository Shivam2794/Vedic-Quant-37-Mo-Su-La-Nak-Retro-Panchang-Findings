import os
import requests
import json

api_key = "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"

def query_fable_10_ideas():
    prompt = """
We loved your previous 2 ideas ("The Committee" multi-horizon ensemble with hysteresis deadband, and "The Diversification Thermostat" ENB correlation overlay).

Now please give us 10 MORE INSTITUTIONAL CREATIVE GENIUS QUANT IDEAS (numbered 1 to 10) to make an asset allocation & trend strategy across Bitcoin (BTC), Gold (GLD), S&P 500 (SPY), and Cash/Treasuries truly institutional-grade, lag-proof, drawdown-controlled (<15% DD), and high-Sharpe (>= 1.50).

For each of the 10 ideas, provide:
- Idea Name & Core Quant Physics
- Why it systematically improves Sharpe or protects against tail drawdowns under realistic execution lags
- Concrete mathematical formulation or implementable logic
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

    print("Sending request for 10 MORE Creative Genius quant ideas to OpenRouter's genuine Fable model...")
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
            with open("fable_10_ideas.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Fable's 10 ideas response to fable_10_ideas.md")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable_10_ideas()
