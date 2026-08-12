import json
import math

r2_kp_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\sample_data\kp_AAL_20050927_000000.json"
local_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\local_ephemeris_AAL_20050927_000000.json"

with open(r2_kp_path, "r") as f:
    r2_kp = json.load(f)["data"]

with open(local_path, "r") as f:
    local_data = json.load(f)

local_features = local_data["vedic_features"]

print("--- LOCAL MOON D-CHART VARGAS ---")
for k, v in local_features.items():
    if k.startswith("TRANSIT_Moon_D"):
        print(f"{k}: {v}")

print("--- NAKSHATRAS ---")
def get_nakshatra(degree):
    return int(degree / (360/27)) + 1

print(f"R2 Moon Deg: {r2_kp['planets'][1]['full_degree']}, Nakshatra: {r2_kp['planets'][1]['nakshatra']}")
print(f"Local Moon Deg: {local_data['positions']['Moon']['longitude']}, Nakshatra computed: {get_nakshatra(local_data['positions']['Moon']['longitude'])}")
