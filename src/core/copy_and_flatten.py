import os
import re
import shutil

src_dir = r"C:\Users\Shivam Patel\Desktop\Python\Learn\quantum_oracle_fusion\mhre\data"
dest_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ml_options_hedging_project"

files_to_copy = [
    "anchor_generator.py",
    "compare_real_vs_synthetic.py",
    "eod_option_harvester.py",
    "generate_historical_ticks.py",
    "gpu_historical_tick_generator.py",
    "historical_csv_parser.py",
    "intraday_interpolator.py",
    "microstructure_layer.py",
    "run_massive_generation.py",
    "run_massive_generation_parallel.py",
    "ssvi_calibrator.py",
    "synthetic_chain_generator.py",
    "validate_historical_regimes.py",
    "validate_hourly_drift.py",
    "validate_intraday_tick.py",
    "validation_suite.py",
    "verify_sample_greeks.py",
    "vix_anchor_generator.py"
]

print("Starting copying and flattening...")

os.makedirs(dest_dir, exist_ok=True)

# Regex to find mhre.data.something imports
# e.g., "from mhre.data.ssvi_calibrator import SSVICalibrator" -> "from ssvi_calibrator import SSVICalibrator"
# and "import mhre.data.ssvi_calibrator" -> "import ssvi_calibrator"
# and also "mhre.data." paths
import_pattern = re.compile(r'\bmhre\.data\.')

# Path pattern to clean up the absolute paths
path_pattern_1 = re.compile(r'c:/Users/patel/Desktop/Python/Learn/quantum_oracle_fusion/data/')
path_pattern_2 = re.compile(r'C:/Users/Shivam%20Patel/\.gemini/antigravity/brain/')

for filename in files_to_copy:
    src_path = os.path.join(src_dir, filename)
    dest_path = os.path.join(dest_dir, filename)
    
    if not os.path.exists(src_path):
        print(f"Source file not found: {src_path}")
        continue
        
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
        
    # Replace imports
    modified_code = import_pattern.sub('', code)
    
    # Replace absolute paths to local data/ folder in project root
    modified_code = path_pattern_1.sub('data/', modified_code)
    
    # Write to destination
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(modified_code)
        
    print(f"Copied and flattened: {filename}")

print("\nCopying and flattening complete!")
