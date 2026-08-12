import json

# AstroSage extracted data
astrosage_data = {
  "Sector_ETFs_Conception": {
    "panchang": {"tithi": "TRAYODASI", "yoga": "DHRITI"}
  },
  "Sector_ETFs_Trading": {
    "panchang": {"tithi": "CHATURTHI", "yoga": "HARSHANA"}
  },
  "XLRE_Conception": {
    "panchang": {"tithi": "DASAMI", "yoga": "SIDDHA"}
  },
  "XLRE_Trading": {
    "panchang": {"tithi": "DVADASI", "yoga": "SUBHA"}
  },
  "XLC_Conception": {
    "panchang": {"tithi": "SASHTI", "yoga": "VAJRA"}
  },
  "XLC_Trading": {
    "panchang": {"tithi": "SAPTAMI", "yoga": "SIDDHI"}
  },
  "SMH_Conception": {
    "panchang": {"tithi": "NAVAMI", "yoga": "SAUBHAGYA"}
  },
  "SMH_Trading": {
    "panchang": {"tithi": "EKADASI", "yoga": "ATIGANDA"}
  },
  "XME_Conception": {
    "panchang": {"tithi": "NAVAMI", "yoga": "SAUBHAGYA"}
  }
}

# Load backend computed data
with open("backend_full_features.json", "r", encoding="utf-8") as f:
    backend_data = json.load(f)

print("PANCHANG VERIFICATION: AstroSage vs Backend Engine\n")
print(f"{'Asset Event':<25} | {'AstroSage Tithi':<15} | {'Backend Tithi':<25} | {'AstroSage Yoga':<15} | {'Backend Yoga':<15}")
print("-" * 105)

for key, as_data in astrosage_data.items():
    if key in backend_data:
        be_panchang = backend_data[key]["panchang"]
        be_tithi = be_panchang["tithi"].split(' ')[0].upper() # extract base name
        be_tithi_full = be_panchang["tithi"]
        be_yoga = be_panchang["yoga"].upper()
        
        as_tithi = as_data["panchang"]["tithi"]
        as_yoga = as_data["panchang"]["yoga"]
        
        tithi_match = "✅" if be_tithi in as_tithi or as_tithi in be_tithi else "❌"
        yoga_match = "✅" if be_yoga == as_yoga else "❌"
        
        # handle slight spelling diffs (e.g., DASAMI vs Dashami)
        if as_tithi == "DASAMI" and be_tithi == "DASHAMI": tithi_match = "✅"
        if as_tithi == "TRAYODASI" and be_tithi == "TRAYODASHI": tithi_match = "✅"
        if as_tithi == "SASHTI" and be_tithi == "SHASHTHI": tithi_match = "✅"
        if as_yoga == "SUBHA" and be_yoga == "SHUBHA": yoga_match = "✅"
        
        print(f"{key:<25} | {as_tithi:<15} | {be_tithi_full:<25} {tithi_match} | {as_yoga:<15} | {be_yoga:<15} {yoga_match}")

