import os
import requests
import json

api_key = "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"

def query_fable_idea_10():
    prompt = """
Give us IDEA 10 to complete the 10 Institutional Creative Genius Quant Ideas! Provide its mathematical formulation and why it protects Sharpe/drawdown under execution lag.
"""

    data = {
        "model": "~anthropic/claude-fable-latest",
        "max_tokens": 2048,
        "messages": [
            {"role": "system", "content": "You are FABLE, an elite quant architect."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        res_json = response.json()
        choice = res_json.get('choices', [{}])[0]
        fable_text = choice.get('message', {}).get('content', '')
        with open("fable_idea_10.md", "w", encoding="utf-8") as f:
            f.write(fable_text)
        print("Successfully wrote Fable's idea 10 to fable_idea_10.md")

if __name__ == "__main__":
    query_fable_idea_10()
