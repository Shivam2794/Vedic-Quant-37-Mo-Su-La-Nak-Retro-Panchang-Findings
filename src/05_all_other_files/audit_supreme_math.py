import pandas as pd
import numpy as np

FILE = r"C:\Users\patel\Desktop\Python\Learn\supreme_genesis_matrix.parquet"

print("="*80)
print(" SUPREME MATRIX MATHEMATICAL AUDIT ")
print("="*80)

df = pd.read_parquet(FILE)
df["Date"] = pd.to_datetime(df["Date"])

print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")

# 1. Ashtakvarga Math Check
print("\n[1] ASHTAKVARGA BINDU VERIFICATION")
print("-" * 50)
sarva_min = df["Sarvashtakavarga"].min()
sarva_max = df["Sarvashtakavarga"].max()
sarva_mean = df["Sarvashtakavarga"].mean()
print(f"Sarvashtakavarga Range: {sarva_min} to {sarva_max} (Mean: {sarva_mean:.2f})")
# Verify that it strictly falls between mathematical limits (usually between 20 and 45 per sign)
# The sum of all 12 signs = 337. The average per sign is 337/12 = 28.08
print(f"Mathematical Expected Mean: 28.08. Actual Mean: {sarva_mean:.2f}")

# 2. Dasha System Check
print("\n[2] VIMSHOTTARI DASHA TRANSITION VERIFICATION")
print("-" * 50)
maha_shifts = df[df["Maha_Saturn"].diff() == 1]
if not maha_shifts.empty:
    date_saturn = maha_shifts.iloc[0]["Date"]
    print(f"Found Maha Dasha shift to Saturn on: {date_saturn.date()}")
else:
    print("Saturn Maha Dasha not started or already running in 2005.")
    
maha_shifts_mercury = df[df["Maha_Mercury"].diff() == 1]
if not maha_shifts_mercury.empty:
    date_merc = maha_shifts_mercury.iloc[0]["Date"]
    print(f"Found Maha Dasha shift to Mercury on: {date_merc.date()}")
    
# 3. True Combustion (Cazimi) Check
print("\n[3] CAZIMI (EXACT CONJUNCTION < 0.5°) VERIFICATION")
print("-" * 50)
cazimi_mercury = df[df["Mercury_true_cazimi"] == 1]
print(f"Found {len(cazimi_mercury)} days of Mercury Cazimi.")
if not cazimi_mercury.empty:
    sample = cazimi_mercury.iloc[0]
    sun_lon = sample["Sun_lon"]
    merc_lon = sample["Mercury_lon"]
    diff = abs((merc_lon - sun_lon + 180) % 360 - 180)
    print(f"  Sample Date: {sample['Date'].date()}")
    print(f"  Sun Lon: {sun_lon:.3f} | Mercury Lon: {merc_lon:.3f}")
    print(f"  Calculated Difference: {diff:.3f}° (Must be < 0.5°)")

# 4. Graha Yuddha (Planetary War) Check
print("\n[4] GRAHA YUDDHA (PLANETARY WAR < 1.0°) VERIFICATION")
print("-" * 50)
war_mars_saturn = df[df["Mars_Saturn_true_war"] == 1]
print(f"Found {len(war_mars_saturn)} days of Mars-Saturn war.")
if not war_mars_saturn.empty:
    sample = war_mars_saturn.iloc[0]
    mars_lon = sample["Mars_lon"]
    sat_lon = sample["Saturn_lon"]
    mars_lat = sample["Mars_lat"]
    sat_lat = sample["Saturn_lat"]
    diff = abs((mars_lon - sat_lon + 180) % 360 - 180)
    mars_wins = sample["Mars_Saturn_war_Mars_wins"]
    print(f"  Sample Date: {sample['Date'].date()}")
    print(f"  Mars Lon: {mars_lon:.3f} | Saturn Lon: {sat_lon:.3f}")
    print(f"  Longitude Difference: {diff:.3f}° (Must be < 1.0°)")
    print(f"  Mars Lat: {mars_lat:.3f} | Saturn Lat: {sat_lat:.3f}")
    if mars_wins:
        print("  Algorithm declared: Mars wins war (Lat closer to 0).")
    else:
        print("  Algorithm declared: Saturn wins war (Lat closer to 0).")

# 5. Planetary Station (Speed changing sign) Check
print("\n[5] PLANETARY STATION (SPEED REVERSAL) VERIFICATION")
print("-" * 50)
station_jup = df[df["Jupiter_true_station_R"] == 1]
print(f"Found {len(station_jup)} Jupiter Station-Retrograde events.")
if not station_jup.empty:
    idx = station_jup.index[0]
    day_before = df.iloc[idx-1]
    day_of = df.iloc[idx]
    print(f"  Sample Date: {day_of['Date'].date()}")
    print(f"  Day Before Speed: {day_before['Jupiter_speed']:+.5f}°/day")
    print(f"  Station Day Speed: {day_of['Jupiter_speed']:+.5f}°/day (Must be negative)")

print("="*80)
print(" AUDIT SCRIPT COMPLETE ")
print("="*80)
