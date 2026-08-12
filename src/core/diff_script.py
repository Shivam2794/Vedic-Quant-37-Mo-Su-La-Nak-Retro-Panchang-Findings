import json
import math

r2_chart_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\sample_data\horoscope-chart_AAL_20050927_000000.json"
r2_kp_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\sample_data\kp_AAL_20050927_000000.json"
r2_dasha_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\sample_data\vimshottari-dasha_AAL_20050927_000000.json"
local_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\local_ephemeris_AAL_20050927_000000.json"

with open(r2_kp_path, "r") as f:
    r2_kp = json.load(f)["data"]

with open(r2_chart_path, "r") as f:
    r2_chart = json.load(f)["data"]

with open(local_path, "r") as f:
    local_data = json.load(f)

# Timezone alignment check
print("--- TIMEZONE CHECK ---")
print("R2 Date:", r2_kp.get("date"), "Time:", r2_kp.get("time"), "TZ:", r2_kp.get("timezone"))
print("Local Timestamp:", local_data.get("timestamp"))

# Degree check
print("\n--- DEGREE CHECK ---")
r2_planets = {p["name"]: float(p["full_degree"]) for p in r2_kp["planets"]}
local_positions = local_data["positions"]

diffs = []
for name, local_p in local_positions.items():
    if name in r2_planets:
        r2_deg = r2_planets[name]
        loc_deg = local_p["longitude"]
        diff = abs(r2_deg - loc_deg)
        if diff > 180:
            diff = 360 - diff
        diffs.append((name, r2_deg, loc_deg, diff))
        print(f"{name}: R2={r2_deg:.4f}, Local={loc_deg:.4f}, Diff={diff:.4f}")
    else:
        print(f"{name} not found in R2.")

print("\nMAX DIFF:", max([d[3] for d in diffs]) if diffs else 0)

# Also let's check D1 chart placements.
print("\n--- D1 CHART PLACEMENT ---")
# R2 Chart has {"1": {"sign_no": 7, "planet": [{"name": "Venus"}, ...]}, "2": ...}
r2_signs = {}
if "data" in r2_chart and "1" in r2_chart["data"]:
    for h, hdata in r2_chart["data"].items():
        sign_no = hdata["sign_no"] - 1 # 0-indexed
        for pl in hdata["planet"]:
            r2_signs[pl["name"]] = sign_no

local_d1 = {}
for k, v in local_data["vedic_features"].items():
    if k.endswith("_D1"):
        pname = k.replace("TRANSIT_", "").replace("_D1", "")
        local_d1[pname] = int(v)

for name, r2_sign in r2_signs.items():
    loc_sign = local_d1.get(name)
    if loc_sign is not None:
        if loc_sign != r2_sign:
            print(f"D1 MISMATCH for {name}: R2={r2_sign}, Local={loc_sign}")
        else:
            print(f"D1 Match for {name}: {r2_sign}")

