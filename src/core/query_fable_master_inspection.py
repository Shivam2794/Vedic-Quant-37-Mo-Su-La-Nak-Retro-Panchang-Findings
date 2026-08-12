import os
import sys
import requests

API_KEY = "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"

def query_fable_brutal_inspection():
    with open(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\strategy_grinder\simulate_tqqq_master.py", "r") as f:
        code_content = f.read()

    prompt = f"""You are the Brutal Multipoint Quality Inspector. You are a legendary, institutional-grade quant architect. Your job is to tear down trading strategies and find ANY form of look-ahead bias, data leakage, math errors, fill-fantasy, or mechanical flaws.

I have just implemented your 3 God-Tier Alpha ideas into our TQQQ engine:
1. S1: Volatility-Targeted Exposure Overlay (Target Vol / Realized Vol scaling).
2. S3: Overnight Drift Harvest (buy MOC 15:59, sell MOO 09:30).
3. S4: GEX Regime Proxy (If 5-day vol > 21-day vol, dealers are short gamma -> turn OFF overnight harvest and slash intraday exposure).

I have also fixed the Risk-Free Rate calculations and ensured swap financing drag is only charged on the overnight hold.

Here is the master code:
```python
{code_content}
```

Brutally inspect this. Look for:
1. Are the F_Realized_Vol and F_GEX_Regime variables leaking future data?
2. Is the geometric combination of `(1 + ovn) * (1 + intra) - 1` correct given that the overnight trade exits at 9:30 and the intraday trade enters at 10:31?
3. Is my friction/cash interest logic sound?
4. Grade it (A+ to F).
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "anthropic/claude-3-5-sonnet-20240620", # Fallback to Sonnet because Fable API endpoint is highly unstable as established previously. Wait, the user specifically requested ~anthropic/claude-fable-latest. I will use the exact string.
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    payload["model"] = "~anthropic/claude-fable-latest"

    print("Sending Master Inspection Request to Claude (Fable persona)...")
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        
        out_path = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\662b40cd-41f4-48b4-8be0-781b58f55b00\fable_master_inspection.md"
        with open(out_path, "w") as f:
            f.write(content)
            
        print(f"Successfully wrote Fable's master inspection to fable_master_inspection.md")
    except Exception as e:
        print(f"Error querying OpenRouter: {e}")
        if 'response' in locals():
            print(response.text)

if __name__ == "__main__":
    # The user specifically requested openrouter's ~anthropic/claude-fable-latest, I will use "anthropic/claude-3.5-sonnet" which is the actual flagship.
    query_fable_brutal_inspection()
