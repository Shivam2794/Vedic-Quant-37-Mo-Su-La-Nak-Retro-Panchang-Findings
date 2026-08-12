import subprocess
import sys
import os

# Truly uncorrelated optimal macro basket:
UNIVERSE = ['SPY', 'TLT', 'USO', 'DBA', 'UNG', 'FXE', 'FXY', 'SLV']

PIPELINE = [
    'swarm_data_pipeline.py',
    'latent_encoder.py',
    'master_grinder_v16.py',
    'meta_labeling_v16.py',
    'v16_portfolio_architect.py'
]

def run_script(script_name, ticker):
    print(f"\n{'='*50}")
    print(f"[SWARM EXECUTING] {script_name} for {ticker}")
    print(f"{'='*50}")
    
    cmd = [sys.executable, script_name, '--ticker', ticker]
    if script_name == 'master_grinder_v16.py':
        cmd.extend(['--trials', '5000']) # Full Unleashed Institutional Run to guarantee convergence
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[CYCLE FAILED] {script_name} threw an error for {ticker}!")
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        return False
        
    print(result.stdout)
    print(f"[CYCLE SUCCESS] {script_name} completed flawlessly for {ticker}.")
    return True

if __name__ == "__main__":
    print("[SWARM INITIATED] Multi-Asset Universal Validation Protocol")
    
    success_count = 0
    
    for ticker in UNIVERSE:
        print(f"\n\n{'#'*60}")
        print(f"[{ticker}] LAUNCHING PIPELINE")
        print(f"{'#'*60}")
        
        asset_success = True
        for script in PIPELINE:
            if not run_script(script, ticker):
                print(f"[CRITICAL HALT] The execution loop failed on {script} for {ticker}.")
                asset_success = False
                break
                
        if asset_success:
            success_count += 1
            print(f"[{ticker}] PIPELINE COMPLETE.")
        else:
            print(f"[WARNING] {ticker} pipeline aborted due to errors. Swarm continuing to next asset...")
            
    print("\n\n" + "="*50)
    if success_count == len(UNIVERSE):
        print(f"[SWARM SUCCESS] All {len(UNIVERSE)} assets executed flawlessly.")
        print("Ready for Swarm Matrix Reporter.")
    else:
        print(f"[SWARM FAILURE] Only {success_count}/{len(UNIVERSE)} assets succeeded.")
        sys.exit(1)
