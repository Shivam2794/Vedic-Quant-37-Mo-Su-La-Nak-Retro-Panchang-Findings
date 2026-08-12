import urllib.request
import json
import os

API_KEY = "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"
MODEL = "anthropic/claude-3.5-sonnet:beta" # Use Sonnet to simulate Fable as per previous rules, or anthropic/claude-3.5-sonnet

with open("fable_phase6_results_query.md", "r") as f:
    prompt = f.read()

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/google/antigravity",
    "X-Title": "Antigravity Quant",
}
data = {
    "model": "~anthropic/claude-fable-latest", # Genuine Fable Model
    "messages": [
        {"role": "system", "content": "You are Fable, an elite hyper-critical quantitative strategist."},
        {"role": "user", "content": prompt}
    ]
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        resp_data = json.loads(response.read().decode('utf-8'))
        content = resp_data['choices'][0]['message']['content']
        with open("C:\\Users\\Shivam Patel\\.gemini\\antigravity\\brain\\b3588b90-74a9-4f14-9ed8-3f4ec28d5d93\\fable_phase6_results_response.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("Success! Response written to artifacts.")
except Exception as e:
    print(f"Error: {e}")
