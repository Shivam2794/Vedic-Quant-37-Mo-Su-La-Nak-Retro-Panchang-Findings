import requests
import json
import os

api_key = "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"

def call_opus5(prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-opus-5",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    print("Status:", response.status_code)
    
    if response.status_code == 200:
        result = response.json()
        print(result['choices'][0]['message']['content'])
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    prompt = "Hello Opus 5, are you there?"
    call_opus5(prompt)
