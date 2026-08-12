import subprocess
import sys

def run_script(script_name):
    print(f"\n{'='*50}")
    print(f"[CYCLE EXECUTING] {script_name}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"[CYCLE SUCCESS] {script_name} completed flawlessly.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[CYCLE FAILED] {script_name} threw an error!")
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        return False

def infinite_quality_loop():
    scripts = [
        "master_data_pipeline_v16.py",
        "latent_encoder.py",
        "master_grinder_v16.py",
        "meta_labeling_v16.py",
        "v16_portfolio_architect.py"
    ]
    
    for script in scripts:
        success = run_script(script)
        if not success:
            print(f"\n[CRITICAL HALT] The execution loop failed on {script}. Brutal Inspector intervention required.")
            sys.exit(1)
            
    print("\n[ALL CYCLES ERROR-FREE] The V16 Pipeline executed end-to-end with zero errors.")

if __name__ == "__main__":
    infinite_quality_loop()
