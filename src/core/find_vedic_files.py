import os
from pathlib import Path

scratch_dir = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")
keywords = ["jaimini", "nadi", "vedic", "transit", "astro", "ephemeris"]

print("Vedic Quant related files in scratch:")
for f in scratch_dir.iterdir():
    if f.is_file():
        name_lower = f.name.lower()
        if any(k in name_lower for k in keywords):
            print(f"  - {f.name:<40} | Size: {f.stat().st_size/1024:>7.2f} KB")
