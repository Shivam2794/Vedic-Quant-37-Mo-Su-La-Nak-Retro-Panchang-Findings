import json
with open('v16_trial_ledger.json', 'r') as f:
    ledger = json.load(f)
print("First 5 values:", [t['value'] for t in ledger[:5]])
best_trial = max(ledger, key=lambda x: x['value'])
print("Best value:", best_trial['value'])
