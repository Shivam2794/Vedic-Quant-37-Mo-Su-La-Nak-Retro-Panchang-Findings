import pandas as pd, glob

f = glob.glob(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned\ticker=MSFT\**\*.parquet", recursive=True)[0]
df = pd.read_parquet(f)
cols = [c for c in df.columns if not c.startswith("rule_")]

entities = ["Sun", "Moon", "Mars", "Mercury", "Venus", "Jupiter", "Saturn", "Rahu", "Ketu"]
for e in entities:
    ecols = [c for c in cols if e in c and "dasha" not in c.lower()]
    print(f"{e}: {len(ecols)} cols -> {ecols[:6]}...")

print(f"\nTotal non-rule cols: {len(cols)}")
dasha_cols = [c for c in cols if "dasha" in c.lower()]
print(f"Dasha cols ({len(dasha_cols)}): {dasha_cols}")
sade_cols = [c for c in cols if "sade" in c.lower()]
print(f"Sade Sati cols: {sade_cols}")
