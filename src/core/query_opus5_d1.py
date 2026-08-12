import requests
import json

api_key = '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'

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\download_and_freeze_data.py', 'r', encoding='utf-8') as f:
    data_freezer = f.read()
    
with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_signal_generator_v6.py', 'r', encoding='utf-8') as f:
    signal_gen = f.read()

with open(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\test_signal_causality.py', 'r', encoding='utf-8') as f:
    causality_test = f.read()

prompt = f'''
# BRUTAL MULTIPOINT QUALITY INSPECTION — PHASE 3 "V6 DELIVERABLE 1"

You are the master brain. You denied Absolution in V5 and issued 6 Deliverables.
I am executing Deliverable 1: Data Integrity and Signal Causality.

I have frozen the data to a Parquet file using the exact Close/Adj Close logic to prevent corporate action lookahead bias.
I have also written the Numba optimized signal generator and the bitwise causality test.

Here is the data freezer:
{data_freezer}

Here is the signal generator:
{signal_gen}

Here is the causality test:
{causality_test}

RESULTS:
The test passed.
Generated and sealed V6 signals for SPY...
=======================================
OPUS 5 CAUSALITY TEST: BITWISE ASSERTION
=======================================
PASS: MACD is bitwise identical and leak-free.
PASS: SMA200 is bitwise identical and leak-free.

YOUR MANDATE:
The user has invoked the "Absolute Surrender & Relentless Grinder" mandate on every new piece of code.
Does this setup mathematically fulfill FATAL-4 and MODERATE-11? 
Have I correctly enforced strict `int8` {{0,1}} dtype semantics (SEVERE-9)?
Are there any gaps in this specific portion of the V6 overhaul before I move on to rewriting the gridsearch and ERC optimizer?
'''

data = {
    "model": "anthropic/claude-opus-5",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

print("Sending request to OpenRouter...")
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json=data
)

if response.status_code == 200:
    content = response.json()['choices'][0]['message']['content']
    with open(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\opus5_v6_deliverable1_review.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully wrote Fable response to opus5_v6_deliverable1_review.md")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
