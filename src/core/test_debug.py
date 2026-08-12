import os
import subprocess

PROJECT_ROOT = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
REPORT_JSON = os.path.join(PROJECT_ROOT, "evaluation_report.json")
REPORT_MD = os.path.join(PROJECT_ROOT, "evaluation_report.md")

if os.path.exists(REPORT_JSON):
    os.remove(REPORT_JSON)
if os.path.exists(REPORT_MD):
    os.remove(REPORT_MD)

print("Starting subprocess...")
env = os.environ.copy()
env["PYTHONPATH"] = PROJECT_ROOT
env["PYTEST_CURRENT_TEST"] = "true"

res = subprocess.run(
    ["python", "src/main.py", "--tickers", "SPY"],
    capture_output=True,
    text=True,
    cwd=PROJECT_ROOT,
    env=env
)

print(f"Subprocess finished with returncode: {res.returncode}")
print(f"Stdout: {res.stdout}")
print(f"Stderr: {res.stderr}")

print(f"Does JSON report exist? {os.path.exists(REPORT_JSON)}")
if os.path.exists(REPORT_JSON):
    with open(REPORT_JSON, "r") as f:
        print(f"JSON Contents: {f.read()}")
print(f"Does MD report exist? {os.path.exists(REPORT_MD)}")

print("Files in scratch directory starting with evaluation_report:")
for f in os.listdir(PROJECT_ROOT):
    if f.startswith("evaluation_report"):
        print(f" - {f}")
