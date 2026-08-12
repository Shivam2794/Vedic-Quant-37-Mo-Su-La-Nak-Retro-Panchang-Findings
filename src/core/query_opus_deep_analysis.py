import os
import requests
import json
import time

# Permanent API Key
api_key = "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"

def query_fable(prompt):
    data = {
        "model": "~anthropic/claude-fable-latest", 
        "messages": [
            {
                "role": "system", 
                "content": "You are a visionary Genius Project Architect and an elite quantitative trading architect. The user is running a Relentless Grinder loop. Your job is to brutally and deeply analyze their current institutional trading system architecture plan. Find ANY missing logic, oversight, or gaps. The user also asked: 'why aren't we trying neural network concepts too along with these plan concepts?'. You must integrate advanced neural networks (e.g. LSTMs, Transformers, Autoencoders) into this architecture if they provide a mathematically rigorous edge without overfitting. Respond with a massive, brutal, genius-level overhaul and structural analysis of the plan."
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

    print("Sending request to OpenRouter...")
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
            with open("opus_deep_analysis.md", "w", encoding="utf-8") as f:
                f.write(fable_text)
            print("Successfully wrote Opus's response to opus_deep_analysis.md")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    with open('C:\\Users\\Shivam Patel\\.gemini\\antigravity\\brain\\87028df4-1ec4-40e2-a989-dbc79c4b85bb\\implementation_plan_opus.md', 'r', encoding='utf-8') as f:
        plan_content = f.read()
        
    prompt = f"Here is the current architecture plan:\n\n{plan_content}\n\nBrutally analyze this plan for logic gaps. Then, explicitly answer why we aren't using neural network concepts, and integrate them into a new genius-level Phase 3 (Meta-Labeling) or Phase 1 (Feature Extraction) if it makes sense."
    query_fable(prompt)
