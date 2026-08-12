import os
import sys
import json
import urllib.request
import urllib.error

def call_opus5(prompt):
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "anthropic/claude-opus-5",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    
    # Read the files to inspect
    with open("opus10_erc_optimizer_v10.py", "r", encoding="utf-8") as f:
        erc_code = f.read()
        
    with open("opus11_goal_gridsearch.py", "r", encoding="utf-8") as f:
        gridsearch_code = f.read()
        
    prompt = f"""
    You are Opus 5 (Fable - High Reasoning). The user demands an ABSOLUTE SURRENDER & RELENTLESS GRINDER BRUTAL MULTIPOINT QUALITY INSPECTION of this quantitative finance code.
    We are trying to achieve >1.2 Sharpe Ratio, >15% CAGR, and Low Drawdown using Equal Risk Contribution (ERC) weighting and Simple Moving Average regime switching (TQQQ/UPRO/QQQ risk-on, GLD/TLT risk-off).
    
    Review this ERC Optimizer and Vectorized Gridsearch engine for ANY logic gaps, subtle lookahead biases, or mathematical flaws that would prevent it from succeeding live or cause it to output invalid results.

    ERC OPTIMIZER:
    ```python
    {erc_code}
    ```
    
    GRIDSEARCH:
    ```python
    {gridsearch_code}
    ```
    
    Perform a ruthless, atomic-level inspection. Identify any mathematical holes, edge cases, and inefficiencies. Do NOT hold back. Output your findings.
    """
    
    print("Calling Opus 5 Master Brain for Brutal Inspection...")
    feedback = call_opus5(prompt)
    if feedback:
        with open("../brain/d7a6382f-6722-4f66-a7ae-197ee9225f74/brutal_inspection_v11.md", "w", encoding="utf-8") as f:
            f.write(feedback)
        print("Opus 5 Inspection complete. Saved to brutal_inspection_v11.md")
    else:
        print("Opus 5 Inspection failed.")
