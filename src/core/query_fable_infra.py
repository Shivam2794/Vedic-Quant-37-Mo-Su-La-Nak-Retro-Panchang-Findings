import os
import requests
import json
import sys

# Permanent API Key
api_key = "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"

def query_fable(prompt):
    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are the Brutal Multipoint Quality Inspector and a Genius Project Architect. I am providing you with the core infrastructure of my live trading bot fleet (Alpaca Execution Engine, FastAPI Dashboard, Config). You must brutally inspect it line-by-line for flaws, security risks, concurrency bugs, API rate limiting issues, latency bottlenecks, and structural weaknesses. Output a Brutal Inspection Report."
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

    print("Sending Infrastructure Inspection Request to Fable...")
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
        
        # Save to the artifacts directory so the AI agent can read it
        out_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\662b40cd-41f4-48b4-8be0-781b58f55b00\fable_infra_inspection.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(fable_text)
        print(f"Successfully wrote Fable's inspection to {out_path}")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\live_bot.py", "r") as f:
        live_bot_code = f.read()
        
    with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\dashboard_v2\fleet_api.py", "r") as f:
        fleet_api_code = f.read()
        
    with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\dashboard_v2\fleet_config.json", "r") as f:
        fleet_config_json = f.read()
        
    prompt = f"""
I have developed the execution and dashboard infrastructure for my live trading bot.
Please brutally inspect these files from a Quant Institutional perspective.

File 1: `live_bot.py`
```python
{live_bot_code}
```

File 2: `fleet_api.py`
```python
{fleet_api_code}
```

File 3: `fleet_config.json`
```json
{fleet_config_json}
```
"""
    query_fable(prompt)
