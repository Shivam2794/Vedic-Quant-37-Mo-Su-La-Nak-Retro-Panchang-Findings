import os
import requests
import json

# Permanent API Key
api_key = "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"

def query_fable():
    with open("opus8_matrix_gigantic_gridsearch.py", "r", encoding="utf-8") as f:
        code_content = f.read()
        
    prompt = f"""
Please perform a brutally meticulous and intelligent review of this Numba-optimized Gigantic Grid Search engine.
The plan is to gridsearch ALL combinations of these indicators with all parameters, with ALL ensemble techniques and their values for all our ETFs.
We are using Opus 5 xhigh reasoning model for this.

Here is the updated code (with previous Numba heap allocation fixes and lookahead bias fixes applied):
```python
{code_content}
```

Review this strictly as a Genius Coder, Brutal Multipoint Quality Inspector, and Relentless Grinder.
Is there anything we missed? Any logic gaps?
"""

    data = {
        "model": "~anthropic/claude-fable-latest",
        "messages": [
            {"role": "system", "content": "You are Opus-5 (Fable), an elite, hyper-critical quant architect and AI coding assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Fable Agent",
        "Content-Type": "application/json"
    }

    print("Sending request to OpenRouter's genuine Opus 5 (Fable) model...")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=120
        )

        if response.status_code == 200:
            res_json = response.json()
            fable_text = res_json['choices'][0]['message']['content']
            with open("fable_response.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Fable's response to fable_response.md")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"API Request Failed: {e}")

if __name__ == "__main__":
    query_fable()
