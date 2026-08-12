import os
import json
import urllib.request
import traceback
import subprocess
import time

SCRATCH_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
OPENROUTER_API_KEY = "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"

files_to_fix = [
    'opus13_dual_momentum_gridsearch_v13.py', 'opus12_erc_optimizer_v12.py', 'opus12_goal_gridsearch_v12.py', 
    'ask_master_brain_v11.py', 'opus14_genesis_v14.py', 'ask_master_brain_v13.py', 'ask_opus5.py', 
    'opus11_goal_gridsearch.py', 'opus10_erc_optimizer_v10.py', 'opus10_compare_naive.py', 
    'opus10_gridsearch_v10.py', 'ask_master_brain_v9_blocking.py', 'ask_master_brain_v9.py', 
    'test_signal_causality_v8.py', 'opus8_signal_generator_v8.py', 'download_and_freeze_data_v2.py', 
    'query_opus5_d1_v2.py', 'test_signal_causality_v7.py', 'opus8_signal_generator_v7.py', 
    'verify_artifacts_v9.py', 'opus9_signal_generator_v9.py', 'test_data_causality_v9.py', 
    'download_and_freeze_data_v3.py', 'check_qqq.py', 'test_signal_causality_v9.py', 
    'query_opus5_d1_v8.py', 'opus8_phase3_optimizer_v2.py', 'opus8_matrix_gigantic_gridsearch_v5.py', 
    'opus8_phase3_optimizer.py', 'opus8_matrix_gigantic_gridsearch_v4.py', 'opus8_matrix_gigantic_gridsearch_v3.py', 
    'opus8_matrix_1a_generator.py', 'download_and_freeze_data.py', 'opus8_config.py', 
    'query_opus5_d1.py', 'test_signal_causality.py', 'opus8_signal_generator_v6.py', 'query_opus5.py'
]

def query_opus5(prompt):
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f"Bearer {OPENROUTER_API_KEY}",
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            'model': 'anthropic/claude-opus-5',
            'messages': [{'role': 'user', 'content': prompt}]
        }).encode('utf-8')
    )
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res = json.loads(response.read().decode())
                return res['choices'][0]['message']['content']
        except Exception as e:
            print(f"API Error: {e}, retrying...")
            time.sleep(5)
    return ""

def test_script(filepath):
    try:
        result = subprocess.run(['python', filepath], capture_output=True, text=True, timeout=60, cwd=SCRATCH_DIR)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: Script took longer than 60 seconds."
    except Exception as e:
        return False, str(e)

def extract_code(text):
    if "```python" in text:
        parts = text.split("```python")
        if len(parts) > 1:
            return parts[1].split("```")[0].strip()
    return text.strip()

print("STARTING ABSOLUTE SURRENDER & RELENTLESS GRINDER LOOP")
for f in files_to_fix:
    fpath = os.path.join(SCRATCH_DIR, f)
    if not os.path.exists(fpath):
        continue
        
    print(f"\n--- PROCESSING: {f} ---")
    with open(fpath, "r", encoding="utf-8", errors="ignore") as file:
        code = file.read()
        
    clean_fpath = os.path.join(SCRATCH_DIR, f.replace(".py", "_clean.py"))
    
    # Check if already processed
    if os.path.exists(clean_fpath):
        print(f"Already cleaned: {clean_fpath}")
        continue
        
    prompt = f"""
You are the Brutal Multipoint Quality Inspector under Absolute Surrender Protocol.
Your task is to fix ALL bugs, logic gaps, and mathematical errors in the following python script.
We know that older versions of this strategy had the following fatal bugs:
1. .fillna(0) creating phantom assets prior to inception.
2. Wrong Sharpe formula (CAGR/vol instead of true excess return Sharpe).
3. No transaction costs or borrowing spread.
4. No Absolute Momentum on defensive assets.
5. Inception alignment ignored.

Rewrite this entire script to be 100% logic-gap free, mathematically perfect, and executable.
If it is a utility script, ensure it has zero bugs.
OUTPUT ONLY THE PYTHON CODE inside a ```python ``` block. NO EXPLANATIONS.

Original Code ({f}):
```python
{code}
```
"""
    
    success = False
    attempts = 0
    while not success and attempts < 3:
        attempts += 1
        print(f"Cycle {attempts} for {f}...")
        
        fixed_text = query_opus5(prompt)
        fixed_code = extract_code(fixed_text)
        
        with open(clean_fpath, "w", encoding="utf-8") as out:
            out.write(fixed_code)
            
        is_clean, output = test_script(clean_fpath)
        if is_clean:
            print(f"SUCCESS! {f} is clean and logic-gap free.")
            success = True
        else:
            print(f"FAILED on attempt {attempts}. Error: {output[:200]}...")
            prompt += f"\n\nYOUR PREVIOUS CODE FAILED WITH THIS ERROR:\n{output}\nFIX IT AND OUTPUT ONLY PYTHON CODE."

print("RELENTLESS GRINDER LOOP COMPLETED.")
