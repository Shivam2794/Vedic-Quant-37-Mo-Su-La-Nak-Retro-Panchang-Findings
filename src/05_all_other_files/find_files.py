import os

def find_file():
    scratch_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"
    for root, _, files in os.walk(scratch_dir):
        for f in files:
            if "v9_ml_century_backtest_expanding.py" in f:
                print(os.path.join(root, f))
            if "run_phase4_5.py" in f:
                print(os.path.join(root, f))
            if "validation_harness.py" in f:
                print(os.path.join(root, f))
                
if __name__ == "__main__":
    find_file()
