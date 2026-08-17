import os
import subprocess
import glob
import re

def main():
    print("Starting full validation suite run...")
    
    scripts = sorted(glob.glob("src/core/omni_engine_*.py"))
    scripts.extend(["src/core/v15_engine.py", "src/core/v16_engine.py"])
    
    results = []
    
    for script in scripts:
        print(f"Running {script}...")
        try:
            # We add src to pythonpath so imports work
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.abspath('src') + os.pathsep + env.get('PYTHONPATH', '')
            
            out = subprocess.check_output(["python", script], text=True, stderr=subprocess.STDOUT, env=env)
            
            cagr = "N/A"
            mdd = "N/A"
            calmar = "N/A"
            win_rate = "N/A"
            
            # Simple regex to extract common metrics from output
            # e.g., "CAGR: 19.83%" or "Strategy CAGR: 20.1%"
            cagr_match = re.search(r'(?i)(?:cagr|return).*?(\-?\d+\.\d+\s*%)', out)
            if cagr_match:
                cagr = cagr_match.group(1)
                
            mdd_match = re.search(r'(?i)(?:max\s*dd|drawdown).*?(\-?\d+\.\d+\s*%)', out)
            if mdd_match:
                mdd = mdd_match.group(1)
                
            calmar_match = re.search(r'(?i)calmar.*?(\d+\.\d+)', out)
            if calmar_match:
                calmar = calmar_match.group(1)
                
            win_match = re.search(r'(?i)win\s*rate.*?(\d+\.\d+\s*%)', out)
            if win_match:
                win_rate = win_match.group(1)
                
            results.append({
                "script": os.path.basename(script),
                "cagr": cagr,
                "mdd": mdd,
                "calmar": calmar,
                "win_rate": win_rate
            })
            print(f"-> CAGR: {cagr}, MDD: {mdd}, Calmar: {calmar}, Win Rate: {win_rate}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}:\n{e.output}")
            results.append({
                "script": os.path.basename(script),
                "cagr": "ERROR",
                "mdd": "ERROR",
                "calmar": "ERROR",
                "win_rate": "ERROR"
            })
            
    # Write to POST_FIX_RESULTS_LEDGER.md
    with open("C:/Users/Shivam Patel/.gemini/antigravity/brain/86ed51bb-ac58-46b1-95bc-0a79189d9c6d/POST_FIX_RESULTS_LEDGER.md", "w") as f:
        f.write("# Post-Fix Results Ledger\n\n")
        f.write("This ledger contains the post-fix execution results for the strategy suite, run after completely remediating the YFinance data leakage and correctly aligning all walk-forward and selection methodologies to strict causality constraints (BAN-001 mitigations).\n\n")
        f.write("| Strategy Engine | CAGR | Max DD | Calmar | Win Rate vs QQQ |\n")
        f.write("|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| `{r['script']}` | {r['cagr']} | {r['mdd']} | {r['calmar']} | {r['win_rate']} |\n")
            
    print("Ledger generated!")

if __name__ == "__main__":
    main()
