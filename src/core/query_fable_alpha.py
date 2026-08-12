import os
import requests
import json
import sys

# Permanent API Key
api_key = "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"

def query_fable():
    prompt = """
We are building a new algorithmic trading engine specifically for TQQQ. Earlier we planned to test 100s of unique, creative quant ideas.

Please brutally review the landscape of these creative alpha ideas (e.g., cross-asset correlations, volume delta footprints, auction sweeps, volatility drag, dealer gamma exposure, microstructure signals, order book imbalances, etc.). 
I want you to ruthlessly filter through the noise and select the absolute best, most genius, and robust concepts to plug into our new TQQQ engine. 

Discard the weak, over-fitted, or impractical ideas. Give me a master review of the god-tier alpha concepts that actually work for a highly leveraged ETF like TQQQ, and explain exactly why they survive your brutal inspection.
"""
    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are FABLE, an elite, hyper-critical quant architect and AI coding assistant."
            },
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    print("Sending request to OpenRouter's genuine Fable model...")
    sys.stdout.flush()
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=120
        )
    except Exception as e:
        print(f"Request failed: {e}")
        return

    if response.status_code == 200:
        res_json = response.json()
        fable_text = res_json['choices'][0]['message']['content']
        artifact_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\65c31ead-fdb3-400b-9322-39134f92edde\fable_alpha_review.md"
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(fable_text)
        print(f"Successfully wrote Fable's response to {artifact_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    query_fable()
