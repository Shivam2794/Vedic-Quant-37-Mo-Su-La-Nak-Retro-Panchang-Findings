import os
import requests
import json

api_key = "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"

def query_fable_genius():
    prompt = """
You previously reviewed our Omni-Allocator V9 (50% BTC / 25% GLD / 25% SPY) strategy and identified three main institutional risks:
1. Over-reliance on short-horizon SMA(2/40) momentum on Bitcoin which degrades under 1-bar execution lag (Mode B drops from 1.79 to 1.59 Sharpe and DD goes from -11.39% to -17.10%) and generates high turnover.
2. Rising correlation between Bitcoin and S&P 500 post-2020 (0.4 to 0.6), weakening static 50/25/25 diversification during macro liquidity sell-offs.
3. Vulnerability to non-bull market regimes where static trend filters might whip-saw.

We want an INSTITUTIONAL-LEVEL CREATIVE GENIUS IDEA to systematically eliminate or mitigate these risks while keeping our performance goals (Sharpe Ratio >= 1.50, Max Drawdown < 18% under realistic 1-bar institutional execution lag).

Please give us your top 3 brilliant, concrete quant engineering solutions that we can code directly into Python:
1. A robust, low-turnover trend/momentum filter for Bitcoin that does NOT whip-saw or degrade heavily under 1-bar lag (e.g. multi-horizon ensemble, breakout filter, EWMA, or volatility-filtered momentum).
2. A dynamic correlation or macro regime overlay (e.g. dynamically shifting capital between SPY, GLD, or short-term Treasuries/cash when BTC-SPY rolling correlation spikes or regime shifts).
3. Any quantitative risk-control architecture that institutions use to lock in <15% drawdown without sacrificing CAGR.

Provide exact mathematical formulations and clear Python implementable logic for each idea.
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

    print("Sending request for Creative Genius solutions to OpenRouter's genuine Fable model...")
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
            with open("fable_genius_response.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Fable's creative genius response to fable_genius_response.md")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable_genius()
