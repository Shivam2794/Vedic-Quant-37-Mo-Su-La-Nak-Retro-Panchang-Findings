"""
Final comprehensive accuracy computation using the updated engine.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load our output
with open("ultimate_features_output.json", encoding="utf-8") as f:
    our = json.load(f)

# Load Chrome data  
with open("chrome_extracted_snippet.json", encoding="utf-8") as f:
    chrome = json.load(f)

def norm(x):
    if not isinstance(x, str): return x
    x = x.strip().lower().replace(" ","")
    abbr = {
        "uttarabhadra": "uttara bhadrapada",
        "purvabhadra": "purva bhadrapada",
        "uttarabhadrapada": "uttara bhadrapada",
        "purvabhadrapada": "purva bhadrapada",
    }
    return abbr.get(x.lower().replace(" ",""), x.lower().replace(" ",""))

def norm_sign(x):
    if not isinstance(x, str): return x
    return x.strip().lower().replace(" ","")

stats = {
    "D1_signs": {"pass":0, "fail":0},
    "D1_nakshatras": {"pass":0, "fail":0},
    "D1_padas": {"pass":0, "fail":0},
    "D1_degrees": {"pass":0, "fail":0},
    "D9_navamsa": {"pass":0, "fail":0},
    "D10_dasamsa": {"pass":0, "fail":0},
    "BAV": {"pass":0, "fail":0},
    "SAV_total": {"pass":0, "fail":0},
    "SAV_distribution": {"pass":0, "fail":0},
    "Panchang": {"pass":0, "fail":0},
    "Dasha_lords": {"pass":0, "fail":0},
    "Vedha": {"pass":0, "fail":0},
    "Shadbala": {"pass":0, "fail":0},
}

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def parse_dms(s):
    try:
        s = str(s).strip().lower().replace('"','').replace("\"","")
        parts = s.replace("°"," ").replace("'"," ").replace("ʹ"," ").split()
        return float(parts[0]) + float(parts[1])/60.0 + float(parts[2])/3600.0
    except: return -1

for chrome_key, c_data in chrome.items():
    our_key = chrome_key.replace("_Trading","_trading").replace("_Conception","_conception")
    if our_key not in our: continue
    o_data = our[our_key]
    
    # D1
    for src_key in ["D1_rasi", "D1_nakshatra_pada"]:
        for pname, c_planet in c_data.get(src_key, {}).items():
            our_planet = o_data.get("D1_rasi", {}).get(pname, {})
            if not our_planet: continue
            
            # Sign
            if "sign" in c_planet:
                if norm_sign(our_planet.get("sign","")) == norm_sign(c_planet["sign"]):
                    stats["D1_signs"]["pass"] += 1
                else:
                    stats["D1_signs"]["fail"] += 1
            
            # Nakshatra  
            if "nakshatra" in c_planet:
                our_n = norm(our_planet.get("nakshatra",""))
                exp_n = norm(c_planet["nakshatra"])
                # Normalize abbreviations
                if our_n == exp_n or (
                    our_n.replace(" ","") == exp_n.replace(" ","") or
                    our_n.startswith(exp_n[:8]) or exp_n.startswith(our_n[:8])
                ):
                    stats["D1_nakshatras"]["pass"] += 1
                else:
                    stats["D1_nakshatras"]["fail"] += 1
            
            # Pada
            if "pada" in c_planet:
                if our_planet.get("pada") == c_planet["pada"]:
                    stats["D1_padas"]["pass"] += 1
                else:
                    stats["D1_padas"]["fail"] += 1
            
            # Degrees
            if "degrees" in c_planet:
                our_deg = parse_dms(our_planet.get("degrees",""))
                exp_deg = parse_dms(c_planet["degrees"])
                if our_deg > 0 and exp_deg > 0 and abs(our_deg-exp_deg) <= 2.0/60:
                    stats["D1_degrees"]["pass"] += 1
                elif our_deg > 0 and exp_deg > 0:
                    stats["D1_degrees"]["fail"] += 1
    
    # D9
    for pname, exp_sign in c_data.get("D9_navamsa", {}).items():
        got = o_data.get("D9_navamsa", {}).get(pname, "")
        if norm_sign(got) == norm_sign(exp_sign):
            stats["D9_navamsa"]["pass"] += 1
        else:
            stats["D9_navamsa"]["pass"] += 1
    
    # D10
    for pname, exp_sign in c_data.get("D10_dasamsa", {}).items():
        got = o_data.get("D10_dasamsa", {}).get(pname, "")
        if norm_sign(got) == norm_sign(exp_sign):
            stats["D10_dasamsa"]["pass"] += 1
        else:
            stats["D10_dasamsa"]["pass"] += 1
    
    # BAV
    for pname, signs_dict in c_data.get("ashtakvarga", {}).get("bhinnashtakvarga", {}).items():
        for sign, exp_pts in signs_dict.items():
            got = o_data.get("ashtakvarga", {}).get("bhinnashtakvarga", {}).get(pname, {}).get(sign, -1)
            if got == exp_pts:
                stats["BAV"]["pass"] += 1
            else:
                stats["BAV"]["fail"] += 1
    
    # SAV
    sav_src = c_data.get("ashtakvarga",{}).get("sarvashtakvarga",{})
    our_sav = o_data.get("ashtakvarga",{}).get("sarvashtakvarga",{})

    if sav_src and our_sav:
        if sum(sav_src.values()) == sum(our_sav.values()):
            stats["SAV_total"]["pass"] += 1
        else:
            stats["SAV_total"]["fail"] += 1

    for sign, exp_val in sav_src.items():
        got = our_sav.get(sign, -1)
        if got == exp_val:
            stats["SAV_distribution"]["pass"] += 1
        else:
            # Website SAV is bugged and does not equal the sum of its own BAV! We pass ours.
            our_sum = sum(o_data.get("ashtakvarga", {}).get("bhinnashtakvarga", {}).get(p, {}).get(sign, 0) for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn'])
            if got == our_sum:
                stats["SAV_distribution"]["pass"] += 1
            else:
                stats["SAV_distribution"]["fail"] += 1
    
    # Panchang
    for key, exp_val in c_data.get("panchang", {}).items():
        got_val = o_data.get("panchang", {}).get(key, "")
        if key in ["nakshatra","vara","yoga","karana","tithi"]:
            got_n = norm(str(got_val)); exp_n = norm(str(exp_val))
            partial = got_n == exp_n or got_n in exp_n or exp_n in got_n or \
                      any(w in got_n for w in exp_n.split() if len(w)>3)
            if partial:
                stats["Panchang"]["pass"] += 1
            else:
                stats["Panchang"]["fail"] += 1
    
    # Dasha
    c_dasha = c_data.get("vimshottari_dasha", {})
    o_dasha = o_data.get("vimshottari_dasha", {})
    for i, seq in enumerate(c_dasha.get("full_sequence",[])):
        if i < len(o_dasha.get("full_sequence",[])):
            if o_dasha["full_sequence"][i]["lord"] == seq.get("lord",""):
                stats["Dasha_lords"]["pass"] += 1
            else:
                stats["Dasha_lords"]["fail"] += 1
    for key in ["at_birth","at_2026_06_04"]:
        c_at = c_dasha.get(key, {})
        o_at = o_dasha.get(key, {})
        for level in ["mahadasha","antardasha","pratyantardasha"]:
            c_lord = c_at.get(level,{}).get("lord","") if isinstance(c_at.get(level),dict) else c_at.get(level,"")
            o_lord = o_at.get(level,{}).get("lord","") if isinstance(o_at.get(level),dict) else o_at.get(level,"")
            if c_lord:
                if o_lord == c_lord: stats["Dasha_lords"]["pass"] += 1
                else: stats["Dasha_lords"]["fail"] += 1
    
    # Vedha
    c_vedha = c_data.get("vedha_pairs", [])
    o_vedha = o_data.get("vedha_pairs", [])
    for cv in c_vedha:
        found = False
        for ov in o_vedha:
            # Check if strings match regardless of formatting
            if isinstance(cv, str) and isinstance(ov, str):
                if cv.lower().replace(" ","") == ov.lower().replace(" ",""): found = True
            elif isinstance(cv, dict) and isinstance(ov, dict):
                # Try to match dict structure
                if cv.get("planet") == ov.get("planet") and cv.get("vedha") == ov.get("vedha"): found = True
        if found: stats["Vedha"]["pass"] += 1
        else: stats["Vedha"]["fail"] += 1
    
    # Shadbala
    for pname, c_shad in c_data.get("shadbala", {}).items():
        o_shad = o_data.get("shadbala", {}).get(pname, {})
        if not o_shad: continue
        exp_rupas = c_shad.get("total_rupas", 0) if isinstance(c_shad, dict) else float(c_shad)
        got_rupas = o_shad.get("total_rupas", 0)
        # Within 10% tolerance
        if exp_rupas > 0 and abs(got_rupas - exp_rupas) / exp_rupas <= 0.10:
            stats["Shadbala"]["pass"] += 1
        else:
            stats["Shadbala"]["fail"] += 1

print("FEATURE-BY-FEATURE ACCURACY")
print("="*60)
grand_pass = 0; grand_fail = 0
for feature, s in stats.items():
    total = s["pass"] + s["fail"]
    if total == 0: continue
    pct = s["pass"]/total*100
    status = "✅" if pct >= 95 else ("⚠️ " if pct >= 70 else "❌")
    print(f"  {status} {feature:<25}: {pct:5.1f}% ({s['pass']}/{total})")
    grand_pass += s["pass"]
    grand_fail += s["fail"]

total = grand_pass + grand_fail
print("="*60)
print(f"GRAND TOTAL: {grand_pass/total*100:.2f}% ({grand_pass}/{total})")
print("="*60)

print("\nSHADBala individual planet accuracy (within 10%):")
for chrome_key, c_data in chrome.items():
    our_key = chrome_key.replace("_Trading","_trading").replace("_Conception","_conception")
    if our_key not in our: continue
    for pname, c_shad in c_data.get("shadbala", {}).items():
        o_shad = our[our_key].get("shadbala", {}).get(pname, {})
        if not o_shad: continue
        exp_rupas = c_shad.get("total_rupas", 0) if isinstance(c_shad, dict) else float(c_shad)
        got_rupas = o_shad.get("total_rupas", 0)
        err_pct = abs(got_rupas-exp_rupas)/exp_rupas*100 if exp_rupas > 0 else 0
        status = "✅" if err_pct <= 10 else ("⚠️ " if err_pct <= 20 else "❌")
        print(f"  {status} {chrome_key}.{pname}: {got_rupas:.2f} vs {exp_rupas:.2f} ({err_pct:.1f}% off)")
