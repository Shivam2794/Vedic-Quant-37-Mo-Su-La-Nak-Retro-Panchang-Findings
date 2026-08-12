import os
import subprocess

PROJECT_ROOT = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
MAIN_PY = os.path.join(PROJECT_ROOT, "src", "main.py")
FALLBACK_STUB = os.path.join(PROJECT_ROOT, "tests", "stubs", "main.py")

def run_debug(args):
    script_path = MAIN_PY if os.path.exists(MAIN_PY) else FALLBACK_STUB
    cmd = ["python", script_path] + args
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    env["PYTEST_CURRENT_TEST"] = "test_tier1_happy_path[F1_1-args0-expected_tickers0] (setup)" # Simulate running under pytest
    
    print(f"Running command: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, env=env)
    print(f"Return code: {res.returncode}")
    print(f"Stdout:\n{res.stdout}")
    print(f"Stderr:\n{res.stderr}")

if __name__ == "__main__":
    run_debug(["--tickers", "SPY", "QQQ", "DIA"])
