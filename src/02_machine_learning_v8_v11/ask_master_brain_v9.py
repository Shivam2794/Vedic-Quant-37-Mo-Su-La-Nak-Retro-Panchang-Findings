import requests
import json
import os

api_key = "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"

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def call_opus5(prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-opus-5",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    print("Calling Opus 5 Master Brain (streaming)...")
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, stream=True)
    
    if response.status_code == 200:
        with open('master_brain_v9_review.md', 'w', encoding='utf-8') as f:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        if line == 'data: [DONE]':
                            break
                        try:
                            chunk = json.loads(line[6:])
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content')
                                if content:
                                    print(content, end='', flush=True)
                                    f.write(content)
                        except json.JSONDecodeError:
                            pass
        print("\nReview saved to master_brain_v9_review.md")
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    v9_plan = read_file(r"C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\scratch\v9_action_plan.md")
    freezer = read_file("download_and_freeze_data_v3.py")
    generator = read_file("opus9_signal_generator_v9.py")
    test_data = read_file("test_data_causality_v9.py")
    test_sig = read_file("test_signal_causality_v9.py")
    
    prompt = f"""You are the Master Brain (Opus 5 Max Effort). You are performing the final Deliverable 1 review of our V9 architecture. 
Our primary mandate is "Absolute Surrender & Relentless Grinder". We do not stop until we get an error-free, bug-free, logic-gap-free cycle.

The previous V8 architecture failed due to 4 Blockers and several Majors. 
I have implemented V9 which fixes these issues through a strictly causal freezer and signal generator.

Here is the V9 Action Plan containing the 16 Acceptance Gates:
{v9_plan}

Here is the Data Freezer (download_and_freeze_data_v3.py):
{freezer}

Here is the Signal Generator (opus9_signal_generator_v9.py):
{generator}

Here is the Data Causality Test (test_data_causality_v9.py):
{test_data}

Here is the Signal Causality Test (test_signal_causality_v9.py):
{test_sig}

Please perform a Brutal Multipoint Inspection on this code. Check if all 16 Acceptance Gates are met. Check for ANY remaining look-ahead biases, logical gaps, or bugs.
Do I have your CLEARANCE to proceed to Deliverable 2 (Gridsearch & ERC Optimizer)?
"""
    call_opus5(prompt)
