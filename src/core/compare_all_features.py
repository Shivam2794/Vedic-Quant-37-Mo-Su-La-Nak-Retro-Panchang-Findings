import json

# Load the user-provided Chrome extracted snippet
with open("chrome_extracted_snippet.json", "r", encoding="utf-8") as f:
    chrome_data = json.load(f)

# Load the backend fully computed features
with open("backend_full_features.json", "r", encoding="utf-8") as f:
    backend_data = json.load(f)

print("="*80)
print("ASTROLOGY FEATURES COMPARISON: CHROME (Extracted) vs BACKEND (Computed)")
print("="*80)

def compare_d1(k, c, b):
    print(f"\n--- {k} : D1 Nakshatra & Pada ---")
    if "D1_nakshatra_pada" not in c or "D1" not in b:
        print("Data missing for D1.")
        return
    c_d1 = c["D1_nakshatra_pada"]
    b_d1 = b["D1"]
    for planet in c_d1:
        if planet in b_d1:
            c_nak = c_d1[planet].get("nakshatra", "N/A")
            c_pada = c_d1[planet].get("pada", "N/A")
            b_nak = b_d1[planet].get("nakshatra", "N/A")
            b_pada = b_d1[planet].get("pada", "N/A")
            nak_match = "✅" if c_nak.lower() == b_nak.lower() or c_nak[:4].lower() == b_nak[:4].lower() else "❌"
            pada_match = "✅" if str(c_pada) == str(b_pada) else "❌"
            print(f"{planet:<10} | Chrome: {c_nak:<15} P{c_pada} | Backend: {b_nak:<15} P{b_pada} | Match: {nak_match} {pada_match}")

def compare_panchang(k, c, b):
    print(f"\n--- {k} : Panchang ---")
    if "panchang" not in c or "panchang" not in b:
        print("Data missing for Panchang.")
        return
    c_p = c["panchang"]
    b_p = b["panchang"]
    
    for key in ["tithi", "karana", "yoga", "vara"]:
        if key in c_p and key in b_p:
            c_val = str(c_p[key])
            b_val = str(b_p[key])
            match = "✅" if c_val.split(' ')[0].lower() in b_val.lower() or b_val.split(' ')[0].lower() in c_val.lower() else "❌"
            print(f"{key.capitalize():<10} | Chrome: {c_val:<25} | Backend: {b_val:<25} | Match: {match}")

def compare_dasha(k, c, b):
    print(f"\n--- {k} : Vimshottari Dasha ---")
    if "vimshottari_dasha" not in c or "vimshottari_dasha" not in b:
        print("Data missing for Dasha.")
        return
    c_d = c["vimshottari_dasha"]
    b_d = b["vimshottari_dasha"]
    
    # At Birth
    if "at_birth" in c_d and "at_birth" in b_d:
        print("At Birth:")
        c_ab = c_d["at_birth"]
        b_ab = b_d["at_birth"]
        for level in ["mahadasha", "antardasha", "pratyantardasha"]:
            if type(c_ab) == dict and level in c_ab and level in b_ab:
                c_lord = c_ab[level] if type(c_ab[level]) == str else c_ab[level].get("lord")
                b_lord = b_ab[level].get("lord")
                match = "✅" if c_lord == b_lord else "❌"
                print(f"  {level.capitalize():<15} | Chrome: {str(c_lord):<10} | Backend: {str(b_lord):<10} | Match: {match}")

    # Today
    if "at_2026_06_04" in c_d and "at_2026_06_04" in b_d:
        print("Today (2026-06-04):")
        c_td = c_d["at_2026_06_04"]
        b_td = b_d["at_2026_06_04"]
        for level in ["mahadasha", "antardasha", "pratyantardasha"]:
            if type(c_td) == dict and level in c_td and level in b_td:
                c_lord = c_td[level] if type(c_td[level]) == str else c_td[level].get("lord")
                b_lord = b_td[level].get("lord")
                match = "✅" if c_lord == b_lord else "❌"
                print(f"  {level.capitalize():<15} | Chrome: {str(c_lord):<10} | Backend: {str(b_lord):<10} | Match: {match}")

for key in chrome_data:
    # Map keys to match backend (e.g., Sector_ETFs_trading -> Sector_ETFs_trading, SPY_Trading -> SPY_trading)
    mapped_key = key.replace('_Trading', '_trading').replace('_Conception', '_conception')
    if mapped_key in backend_data:
        b_data = backend_data[mapped_key]
        c_data = chrome_data[key]
        
        compare_d1(key, c_data, b_data)
        compare_panchang(key, c_data, b_data)
        compare_dasha(key, c_data, b_data)
    else:
        print(f"Key {mapped_key} not found in backend data.")

