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
                "content": "You are the Brutal Multipoint Quality Inspector. I am returning with my fixed script after your previous teardown. Please review every line again. Have I fixed all 5 critical flaws? Have I successfully implemented Out-Of-Sample constraints? Output must be a Brutal Inspection Report: Grade, Remaining Weaknesses, Final Verdict."
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

    print("Sending Re-Inspection Request to Fable...")
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
        with open("fable_reinspection.md", "w", encoding="utf-8") as f:
            f.write(fable_text)
        print("Successfully wrote Fable's re-inspection to fable_reinspection.md")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\strategy_grinder\simulate_tqqq.py", "r") as f:
        code = f.read()
        
    prompt = f"""
I have rewritten the simulation engine according to your exact D+ Brutal Inspection Report.
Please re-grade the following script.

```python
{code}
```
"""
    query_fable(prompt)
