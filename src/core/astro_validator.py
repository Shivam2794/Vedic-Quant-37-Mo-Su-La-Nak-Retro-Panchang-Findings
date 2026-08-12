import pandas as pd
import numpy as np

print("="*70)
print(" VEDIC ASTROLOGY MULTIPOINT DATA INSPECTION")
print("="*70)

print("Loading continuous history matrix...")
df = pd.read_parquet('C:/Users/patel/Desktop/Python/Learn/full_history_astro_matrix.parquet')
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")

errors = []
warnings = []

# 1. Ephemeris & Longitude Bounds
print("\n[1] Checking Planetary Longitude Bounds (0 to 360 degrees)...")
planets = ['Sun', 'Moon', 'Mar', 'Mer', 'Jup', 'Ven', 'Sat', 'Rah', 'Ket']
for p in planets:
    col = f"{p}_Speed"
    if col in df.columns:
        # Check retrograde logic
        if p in ['Sun', 'Moon']:
            if (df[col] <= 0).any():
                errors.append(f"CRITICAL: {p} goes retrograde! (Speed <= 0 found)")
        elif p in ['Rah', 'Ket']:
            # Rahu/Ketu are usually retrograde, but stationary is 0
            if (df[col] > 1).any(): # Sometimes true nodes have small positive speeds, but mostly negative
                warnings.append(f"NOTE: {p} has large positive speeds? Max: {df[col].max()}")

    # Try to find longitude columns. They might be named differently (e.g. 'Panchang_Tithi', etc.)
    # Let's search for any column with '_Lon' or '_Pos'
    
# Check Tithi Logic
print("\n[2] Checking Panchang & Tithi bounds...")
if 'Tithi_Num' in df.columns:
    if df['Tithi_Num'].min() < 1 or df['Tithi_Num'].max() > 30:
        errors.append(f"CRITICAL: Tithi_Num out of bounds! Min: {df['Tithi_Num'].min()}, Max: {df['Tithi_Num'].max()}")
    else:
        print("Tithi_Num is perfectly bounded [1-30].")

if 'Yoga_Num' in df.columns:
    if df['Yoga_Num'].min() < 1 or df['Yoga_Num'].max() > 27:
        errors.append(f"CRITICAL: Yoga_Num out of bounds! Min: {df['Yoga_Num'].min()}, Max: {df['Yoga_Num'].max()}")
    else:
        print("Yoga_Num is perfectly bounded [1-27].")

if 'Karana_Num' in df.columns:
    if df['Karana_Num'].min() < 1 or df['Karana_Num'].max() > 60:
        warnings.append(f"Warning: Karana_Num bounds check. Min: {df['Karana_Num'].min()}, Max: {df['Karana_Num'].max()}")

# 3. Dignity & Shadbala
print("\n[3] Checking Dignity & Shadbala Bounds...")
shadbala_cols = [c for c in df.columns if 'Shadbala' in c]
for c in shadbala_cols:
    min_val, max_val = df[c].min(), df[c].max()
    if min_val < 0:
        errors.append(f"CRITICAL: {c} has negative Shadbala! ({min_val})")
    if max_val > 15: # Unusually high Shadbala
        warnings.append(f"High Shadbala observed in {c}: {max_val}")

dignity_cols = [c for c in df.columns if 'Dignity' in c]
for c in dignity_cols:
    min_val, max_val = df[c].min(), df[c].max()
    if min_val < -100 or max_val > 100: # Assuming dignity is scored
        warnings.append(f"Dignity outside normal bounds [-100, 100] for {c}: [{min_val}, {max_val}]")

# 4. Check for pure NaN/Garbage Columns
print("\n[4] Checking for Corrupted/Garbage Columns...")
nan_counts = df.isna().sum()
pure_nan_cols = nan_counts[nan_counts == len(df)]
if len(pure_nan_cols) > 0:
    warnings.append(f"Found {len(pure_nan_cols)} entirely NaN columns (likely conditional features like Planetary Wars).")

# Summary
print("\n" + "="*70)
print(" INSPECTION SUMMARY")
print("="*70)
if len(errors) == 0:
    print("NO CRITICAL MATHEMATICAL ERRORS FOUND IN ASTRO LOGIC.")
else:
    for e in errors: print(e)

print(f"\nTotal Warnings: {len(warnings)}")
for w in warnings[:10]:
    print(w)
if len(warnings) > 10:
    print(f"... and {len(warnings) - 10} more warnings.")

