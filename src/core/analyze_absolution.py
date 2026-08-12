import os
import sys

res_path = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data\opus8_gridsearch_absolution_results.csv'

if not os.path.exists(res_path):
    print("Results file not found.")
    sys.exit(0)

results = []
with open(res_path, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        line = line.strip()
        if not line: continue
        parts = line.split(',', 5)
        if len(parts) == 6:
            ticker, size, fams, logic, sharpe_str, params = parts
            try:
                sharpe = float(sharpe_str)
                results.append({
                    'Ticker': ticker,
                    'Size': int(size),
                    'Families': fams,
                    'Logic': logic,
                    'Sharpe': sharpe,
                    'Params': params
                })
            except:
                pass

print("OPUS-8 ABSOLUTION GRID SEARCH RESULTS")
print("==================================================")
print(f"Total Combinations Evaluated and Saved: {len(results)}")
print()

# Group by Ticker
tickers = set([r['Ticker'] for r in results])

for ticker in sorted(list(tickers)):
    print(f"--- Top 3 Strategies for {ticker} ---")
    t_res = [r for r in results if r['Ticker'] == ticker]
    t_res.sort(key=lambda x: x['Sharpe'], reverse=True)
    
    for i in range(min(3, len(t_res))):
        row = t_res[i]
        print(f"Size: {row['Size']} | Logic: {row['Logic']} | Sharpe: {row['Sharpe']:.4f}")
        print(f"Families: {row['Families']}")
        print(f"Params: {row['Params']}")
        print()
