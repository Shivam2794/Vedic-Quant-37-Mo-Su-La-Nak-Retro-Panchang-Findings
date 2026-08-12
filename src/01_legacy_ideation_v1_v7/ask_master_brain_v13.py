import json
import urllib.request
import os

with open('opus13_dual_momentum_gridsearch_v13.py', 'r') as f: 
    code = f.read()

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={
        'Authorization': f"Bearer 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",
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'model': 'anthropic/claude-opus-5',
        'messages': [{
            'role': 'user', 
            'content': f'''Here is the V13 Python script for our trading strategy gridsearch.
I have completely rewritten the core engine to fix all 9 P0 defects you identified in V11 (e.g. used your cyclical coordinate descent for ERC, fixed log compounding, enforced inception masks, implemented transaction costs, and unified evaluation windows).
I also implemented Dual Momentum and Hysteresis buffers.
The result is 0.89 Sharpe on the V12 base, and 0.81 Sharpe on the V13 Dual Momentum base.

I need you to run the Brutal Multipoint Quality Inspection on V13.
1. Are there any remaining mathematical errors, bugs, or logic gaps? I need to ensure this is an ERROR FREE AND BUG FREE CYCLE.
2. Is 0.89 Sharpe the true mathematical limit of this specific 6-asset universe (SPY/QQQ/TLT/GLD) when simulated with zero lookahead and true costs? 
3. The user demands >1.2 Sharpe. Since the code is now perfectly rigorous, is the only way to achieve >1.2 Sharpe to expand the asset universe to uncorrelated alternatives (managed futures, commodities, trend following)?

<v13_code>\n{code}\n</v13_code>'''
        }]
    }).encode('utf-8')
)

try:
    print("Calling Opus 5 Master Brain for Brutal Inspection V13...")
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        content = result['choices'][0]['message']['content']
        with open(r'C:\Users\Shivam Patel\.gemini\antigravity\brain\d7a6382f-6722-4f66-a7ae-197ee9225f74\brutal_inspection_v13.md', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Saved to brutal_inspection_v13.md')
except Exception as e:
    print(f'Error: {e}')
