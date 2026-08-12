import os

files_to_check = [
    "run_phase4_5.py",
    "run_phase6.py",
    "eternal_quant_evolution_v2.py",
    "eternal_quant_evolution_v3.py",
    "eternal_quant_evolution_v4.py",
    "v13_engine_grid_search.py",
    "validation_harness.py",
    "v9_ml_century_backtest_expanding.py",
    "v11_ml_century_backtest_expanding.py",
    "grid_search.py",
    "ml_parameter_optimizer.py",
    "brutal_ml_optimizer.py",
    "quick_diagnostic_v6.py"
]

found = set()
for root, _, files in os.walk(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch"):
    for f in files:
        if f in files_to_check:
            found.add(f)
            print(f"Found: {os.path.join(root, f)}")
            
print("\n--- Missing Files ---")
for f in files_to_check:
    if f not in found:
        print(f)
