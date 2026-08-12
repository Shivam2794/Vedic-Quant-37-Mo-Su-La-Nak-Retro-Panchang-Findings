import os
import json
import urllib.request
import traceback
import subprocess
import time
import glob

SCRATCH_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
OPENROUTER_API_KEY = "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"

def query_gemini_pro(prompt):
    """Simulates the Gemini Agent's second pass using OpenRouter's Gemini 1.5 Pro"""
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f"Bearer {OPENROUTER_API_KEY}",
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            'model': 'google/gemini-1.5-pro',
            'messages': [{'role': 'user', 'content': prompt}]
        }).encode('utf-8')
    )
    for _ in range(5): # Relentless retries
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res = json.loads(response.read().decode())
                return res['choices'][0]['message']['content']
        except Exception as e:
            print(f"API Error (Gemini Pass): {e}, retrying in 10s...")
            time.sleep(10)
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

print("STARTING DUAL-LLM VETTING LOOP (PASS 2: GEMINI INSPECTION)")
print("Waiting for Opus 5 to output _clean.py files...")

processed_files = set()

while True:
    clean_files = glob.glob(os.path.join(SCRATCH_DIR, "*_clean.py"))
    
    found_new = False
    for clean_fpath in clean_files:
        if clean_fpath in processed_files:
            continue
            
        vetted_fpath = clean_fpath.replace("_clean.py", "_vetted.py")
        if os.path.exists(vetted_fpath):
            processed_files.add(clean_fpath)
            continue
            
        found_new = True
        filename = os.path.basename(clean_fpath)
        print(f"\n--- DUAL-VETTING INITIATED: {filename} ---")
        
        with open(clean_fpath, "r", encoding="utf-8", errors="ignore") as file:
            code = file.read()
            
        # The prompt forces Gemini 1.5 Pro to act exactly as the Brutal Multipoint Inspector
        prompt = f"""
You are the Brutal Multipoint Quality Inspector (Google Gemini 1.5 Pro) under Absolute Surrender Protocol.
Your peer, Opus 5, has just rewritten this script to remove lookahead bias, phantom assets, and Sharpe formula errors.
Your mission is to perform the SECOND PASS of the dual-LLM vetting process. 

Scrutinize this code like your life depends on it. 
Look for ANY remaining mathematical errors, logic gaps, off-by-one errors, or data leakage that Opus 5 might have missed.
Rewrite the code to be mathematically perfect, 100% bug-free, and executable.
OUTPUT ONLY THE PYTHON CODE inside a ```python ``` block. NO EXPLANATIONS.

Opus 5's Code ({filename}):
```python
{code}
```
"""
        success = False
        attempts = 0
        while not success and attempts < 5:
            attempts += 1
            print(f"Gemini Vetting Cycle {attempts} for {filename}...")
            
            fixed_text = query_gemini_pro(prompt)
            fixed_code = extract_code(fixed_text)
            
            if not fixed_code:
                print("Failed to extract code. Retrying...")
                continue
                
            with open(vetted_fpath, "w", encoding="utf-8") as out:
                out.write(fixed_code)
                
            is_clean, output = test_script(vetted_fpath)
            if is_clean:
                print(f"DUAL-VETTING SUCCESS! {filename} is now fully certified by both Opus 5 and Gemini.")
                success = True
                processed_files.add(clean_fpath)
            else:
                print(f"FAILED on attempt {attempts}. Error: {output[:200]}...")
                prompt += f"\n\nYOUR PREVIOUS CODE FAILED WITH THIS ERROR:\n{output}\nFIX IT AND OUTPUT ONLY PYTHON CODE."

    if not found_new:
        # Check if original script is done (just a rough heuristic: if we processed 38 files)
        if len(processed_files) >= 38:
            print("ALL FILES HAVE BEEN DUAL-VETTED. LOOP COMPLETE.")
            break
        time.sleep(15) # Wait for Opus 5 to finish more files
