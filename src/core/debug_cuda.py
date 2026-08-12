import os
import subprocess
import time

PROJECT_ROOT = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
MAIN_PY = os.path.join(PROJECT_ROOT, "src", "main.py")
REPORT_JSON = os.path.join(PROJECT_ROOT, "evaluation_report.json")

def clean_report():
    if os.path.exists(REPORT_JSON):
        os.remove(REPORT_JSON)

def run_debug():
    clean_report()
    
    cmd = [r"C:\Users\Shivam Patel\AppData\Local\Programs\Python\Python312\python.exe", MAIN_PY, "--tickers", "SPY", "QQQ", "DIA"]
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    env["PYTEST_CURRENT_TEST"] = "test_tier1_happy_path[F1_1-args0-expected_tickers0] (call)"
    
    print("Running subprocess...")
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, env=env)
    print(f"Subprocess return code: {res.returncode}")
    print(f"Subprocess stdout:\n{res.stdout}")
    print(f"Subprocess stderr:\n{res.stderr}")
    
    print(f"Checking if report exists immediately after subprocess exit...")
    exists_1 = os.path.exists(REPORT_JSON)
    print(f"Exists (immediate): {exists_1}")
    
    if not exists_1:
        print("Sleeping 1 second and checking again...")
        time.sleep(1.0)
        exists_2 = os.path.exists(REPORT_JSON)
        print(f"Exists (after 1s): {exists_2}")
        
        print("Listing all files in project root:")
        for name in os.listdir(PROJECT_ROOT):
            if "report" in name.lower():
                print(f"- {name}")

if __name__ == "__main__":
    run_debug()
