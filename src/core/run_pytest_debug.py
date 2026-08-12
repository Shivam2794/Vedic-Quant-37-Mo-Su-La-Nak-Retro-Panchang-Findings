import os
import subprocess
import pytest

# Save original subprocess.run and os.path.exists
original_run = subprocess.run
original_exists = os.path.exists

def mock_run(cmd, *args, **kwargs):
    print(f"\n--- SUBPROCESS RUN START ---")
    print(f"Command: {cmd}")
    res = original_run(cmd, *args, **kwargs)
    print(f"Return code: {res.returncode}")
    print(f"Stdout:\n{res.stdout}")
    print(f"Stderr:\n{res.stderr}")
    print(f"--- SUBPROCESS RUN END ---\n")
    return res

def mock_exists(path):
    res = original_exists(path)
    if "evaluation_report.json" in path:
        print(f"DEBUG: os.path.exists('{path}') called. Result: {res}")
        if not res:
            parent_dir = os.path.dirname(path)
            print(f"DEBUG: Directory listing of {parent_dir}:")
            for name in os.listdir(parent_dir):
                if "report" in name.lower():
                    print(f"  - {name} (size: {os.path.getsize(os.path.join(parent_dir, name))})")
    return res

# Mock them
subprocess.run = mock_run
os.path.exists = mock_exists
import os.path
os.path.exists = mock_exists

if __name__ == "__main__":
    PROJECT_ROOT = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    os.chdir(PROJECT_ROOT)
    pytest.main([
        "-v", "-s", 
        "-p", "no:seleniumbase", 
        "-p", "no:rerunfailures", 
        "-p", "no:xdist", 
        "-p", "no:ordering",
        "-p", "no:metadata",
        "-p", "no:html",
        "tests/test_e2e_pipeline.py", 
        "-k", "F1_1"
    ])
