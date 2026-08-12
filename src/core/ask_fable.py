import os
import requests
import json

api_key = "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"

def query_fable(prompt):
    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {"role": "system", "content": "You are FABLE, an elite, hyper-critical quant architect and AI coding assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    
    # Force use of ~anthropic/claude-fable-latest as instructed
    data["model"] = "~anthropic/claude-fable-latest"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    print("Sending request to OpenRouter's genuine Fable model...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        res_json = response.json()
        fable_text = res_json['choices'][0]['message']['content']
        with open("fable_response.md", "w", encoding="utf-8") as f:
            f.write(fable_text)
        print("Successfully wrote Fable's response to fable_response.md")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    prompt = """
Fable, my user and I have developed a Tri-Asset portfolio (60% BTC, 20% GLD, 20% SPY) utilizing 3 different execution overlays based on your previous ideas. 

We ran them through a relentless adversarial grinder using strict Mode B execution (Signal at Close t, Fill at Open t+1), realistic slippage (20bps BTC, 3bps GLD/SPY), strict SPY 252-day business calendars for alignment, and margin borrowing at IRX + 150bps (calculated over exact 365 calendar days). We even fixed a bug where your CPPI multiplier was capped at 0.56, allowing full 1.0 exposure when at all-time highs.

The results from 2014-2024 are staggering:
1. Idea 4: The Drawdown Governor (CPPI Floor at 86% of HWM): 1.91 Sharpe, 19.51% CAGR, -10.24% MaxDD
2. Idea 5: Vol-of-Vol Brake (Tail Shock Cutoff): 1.85 Sharpe, 20.22% CAGR, -12.02% MaxDD
3. Idea 9: The Patience Dial (EMA Smoothing tau=0.85): 1.73 Sharpe, 19.06% CAGR, -13.96% MaxDD

The S&P 500 benchmark did 11.64% CAGR with -32.05% MaxDD and 0.65 Sharpe. Our strategies beat SPY in exactly ~50% of months.

The user says: "I don't know, for some reason the returns of these 3 strategies look too perfect!"
As a hyper-critical quant architect, dissect these results. Is a 1.9 Sharpe over 10 years "too perfect"? Are we still being fooled by an invisible mirage of curve-fitting, survivor bias, or the sheer mathematical gravity of Bitcoin's historical beta? Or is it genuinely possible to achieve a 1.9 Sharpe physically in the real world using these exact mechanics? Grill us.
"""
    query_fable(prompt)
