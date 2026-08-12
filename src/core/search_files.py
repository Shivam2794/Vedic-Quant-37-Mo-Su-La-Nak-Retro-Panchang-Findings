import os

search_names = [
    "ssvi_calibrator.py",
    "intraday_interpolator.py",
    "microstructure_layer.py",
    "validation_suite.py",
    "anchor_generator.py",
    "gpu_historical_tick_generator.py",
    "vix_anchor_generator.py",
    "run_massive_generation_parallel.py"
]

search_roots = [
    r"C:\Users\Shivam Patel",
    r"C:\Users\Shivam Patel", # from the chat logs
    r"E:\Python\Learn", # from the chat logs
]

print("Starting search...")
found = {}
for root in search_roots:
    if not os.path.exists(root):
        print(f"Path does not exist: {root}")
        continue
    print(f"Scanning {root}...")
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip large system or cache directories to be fast
        if any(p in dirpath.lower() for p in [".git", "node_modules", "__pycache__", "appdata\\local\\microsoft", "appdata\\local\\temp", "downloads", "documents"]):
            continue
        for name in filenames:
            if name in search_names:
                full_path = os.path.join(dirpath, name)
                print(f"FOUND: {name} in {full_path}")
                if name not in found:
                    found[name] = []
                found[name].append(full_path)

print("\n--- Search Complete ---")
for name in search_names:
    paths = found.get(name, [])
    print(f"{name}: {len(paths)} locations found: {paths}")
