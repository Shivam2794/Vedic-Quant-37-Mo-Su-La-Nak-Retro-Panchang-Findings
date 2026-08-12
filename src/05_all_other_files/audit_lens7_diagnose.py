"""
Diagnose the Lens 7 FAIL: Are the large daily jumps genuine data errors or
legitimate multi-day calendar gaps in the merged matrix?
"""
import pandas as pd
import numpy as np

FILE = r"C:\Users\patel\Desktop\Python\Learn\supreme_genesis_matrix.parquet"
df = pd.read_parquet(FILE)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

print("[DIAGNOSIS] Checking date continuity and nature of large jumps")

# Check for calendar gaps
gaps = df["Date"].diff().dt.days
print(f"\nDate gap distribution:")
print(gaps.value_counts().sort_index())

# Look at the actual Sun longitude jump
sun_raw_diff = df["Sun_lon"].diff().abs()
sun_wrap = sun_raw_diff.apply(lambda x: min(x, 360-x) if pd.notna(x) else 0)

large_jumps = df[sun_wrap > 1.5][["Date", "Sun_lon"]].copy()
large_jumps["sun_jump"] = sun_wrap[sun_wrap > 1.5]
large_jumps["date_gap"] = gaps[sun_wrap > 1.5]
print(f"\nTop 5 large Sun jumps:")
print(large_jumps.head(10).to_string())

# Check if jumps perfectly match (date_gap * typical daily motion)
SUN_DAILY_MOTION = 0.9856  # degrees per day (mean)
large_jumps["expected_motion"] = large_jumps["date_gap"] * SUN_DAILY_MOTION
large_jumps["motion_per_day"] = large_jumps["sun_jump"] / large_jumps["date_gap"]
print(f"\nExpected daily motion (if purely calendar gap): {SUN_DAILY_MOTION}°/day")
print(large_jumps[["Date","sun_jump","date_gap","expected_motion","motion_per_day"]].head(10).to_string())
