import subprocess
import os
import sys

PROJECT_ROOT = r"C:\Users\Shivam Patel\.\.gemini\antigravity\scratch"
MAIN_PY = os.path.join(PROJECT_ROOT, "src", "main.py")

def run_case(args):
    cmd = ["python", MAIN_PY] + args
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, env=env)
    print("ARGS:", args)
    print("RETURN CODE:", res.returncode)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
    print("-" * 50)

# Run F1_1
run_case(["--tickers", "SPY", "QQQ", "DIA"])

# Run T3_6
run_case(["--sae_bottleneck_dim", "16", "--sae_sparsity_weight", "1e-4", "--mlp_hidden_dims", "128", "64", "--mlp_dropout", "0.1", "--cv_splits", "10", "--cv_embargo_pct", "0.05"])
