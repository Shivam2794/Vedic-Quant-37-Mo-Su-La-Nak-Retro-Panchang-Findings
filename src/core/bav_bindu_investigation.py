"""
TARGETED FIX: Find the EXACT missing bindus in BAV/SAV.
Compare what each planet contributes to each sign in detail.
"""
import sys, swisseph as swe
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding='utf-8')
swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NY_TZ = pytz.timezone('America/New_York')

def get_jd(dt_str):
    dt = NY_TZ.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)

jd = get_jd("1993-01-29 09:30:00")
flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
asc_lon = ascmc[0]

planet_ids = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
              "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}
plons = {}
for name, pid in planet_ids.items():
    plons[name] = swe.calc_ut(jd, pid, flags)[0][0]
plons["Ketu"] = (plons["Rahu"] + 180) % 360
plons["Ascendant"] = asc_lon

print("Planet Positions for SPY Trading:")
for name, lon in plons.items():
    si = int(lon/30)%12
    print(f"  {name:10}: {lon:8.4f}° | {SIGNS[si]:14} | sign_idx={si}")

# The SPY SAV issue: our total=335, Chrome=337 → we're missing 2 bindus
# Let me check if the issue is in how we handle the 12th house (position 12 = 0 in mod arithmetic)
# In BAV rules, position "12" means the 12th house from the planet, which is sign_idx-1 (the previous sign)

BAV_RULES_ORIGINAL = {
    "Sun":     {"Sun":[1,2,4,7,8,9,10,11],"Moon":[3,6,10,11],"Mars":[1,2,4,7,8,9,10,11],"Mercury":[3,5,6,9,10,11,12],"Jupiter":[5,6,9,11],"Venus":[6,7,12],"Saturn":[1,2,4,7,8,9,10,11],"Ascendant":[3,4,6,10,11,12]},
    "Moon":    {"Sun":[3,6,7,8,10,11],"Moon":[1,3,6,7,10,11],"Mars":[2,3,5,6,9,10,11],"Mercury":[1,3,4,5,7,8,10,11],"Jupiter":[1,4,7,8,10,11,12],"Venus":[3,4,5,7,9,10,11],"Saturn":[3,5,6,11],"Ascendant":[3,6,10,11]},
    "Mars":    {"Sun":[3,5,6,10,11],"Moon":[3,6,11],"Mars":[1,2,4,7,8,10,11],"Mercury":[3,5,6,11],"Jupiter":[6,10,11,12],"Venus":[6,8,11,12],"Saturn":[1,4,7,8,9,10,11],"Ascendant":[1,3,6,10,11]},
    "Mercury": {"Sun":[5,6,9,11,12],"Moon":[2,4,6,8,10,11],"Mars":[1,2,4,7,8,9,10,11],"Mercury":[1,3,5,6,9,10,11,12],"Jupiter":[6,8,11,12],"Venus":[1,2,3,4,5,8,9,11],"Saturn":[1,2,4,7,8,9,10,11],"Ascendant":[1,2,4,6,8,10,11]},
    "Jupiter": {"Sun":[1,2,3,4,7,8,9,10,11],"Moon":[2,5,7,9,11],"Mars":[1,2,4,7,8,10,11],"Mercury":[1,2,4,5,6,9,10,11],"Jupiter":[1,2,3,4,7,8,10,11],"Venus":[2,5,6,9,10,11],"Saturn":[3,5,6,12],"Ascendant":[1,2,4,5,6,9,10,11]},
    "Venus":   {"Sun":[8,11,12],"Moon":[1,2,3,4,5,8,9,11,12],"Mars":[3,5,6,9,11,12],"Mercury":[3,5,6,9,11],"Jupiter":[5,8,9,10,11],"Venus":[1,2,3,4,5,8,9,10,11],"Saturn":[3,4,5,8,9,10,11],"Ascendant":[1,2,3,4,5,8,9,11]},
    "Saturn":  {"Sun":[1,2,4,7,8,10,11],"Moon":[3,6,11],"Mars":[3,5,6,10,11],"Mercury":[6,8,9,10,11,12],"Jupiter":[5,6,11,12],"Venus":[6,11,12],"Saturn":[3,5,6,11],"Ascendant":[1,3,4,6,10,11]}
}

# Count total bindus each planet contributes
print("\nTotal bindus each SOURCE contributes per TARGET planet:")
print(f"{'Target':<10}", end="")
for src in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Ascendant"]:
    print(f" {src[:5]:>6}", end="")
print(" | Total")
print("-" * 80)

grand_total = 0
for tgt, sources in BAV_RULES_ORIGINAL.items():
    total = 0
    print(f"{tgt:<10}", end="")
    for src in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Ascendant"]:
        cnt = len(sources.get(src, []))
        print(f" {cnt:>6}", end="")
        total += cnt
    print(f" | {total}")
    grand_total += total
print(f"\nGrand total bindus across all planets: {grand_total}")
print(f"Expected total in SAV: {grand_total} (each bindu contributes 1 to one sign)")

# Now compute our SAV and Chrome SAV  
def compute_bav(plons_dict, rules):
    bav = {planet: {s: 0 for s in SIGNS} for planet in rules}
    sign_idx = lambda n: int(plons_dict[n]/30)%12
    for tgt, sources in rules.items():
        for src, positions in sources.items():
            if src not in plons_dict: continue
            src_si = sign_idx(src)
            for pos in positions:
                target_si = (src_si + pos - 1) % 12
                bav[tgt][SIGNS[target_si]] += 1
    sav = {s: sum(bav[p][s] for p in rules) for s in SIGNS}
    return bav, sav

bav, sav = compute_bav(plons, BAV_RULES_ORIGINAL)
our_total = sum(sav.values())
print(f"\nOur computed SAV total: {our_total}")

chrome_sav = {"Aries":28,"Taurus":26,"Gemini":29,"Cancer":23,"Leo":26,"Virgo":31,
              "Libra":27,"Scorpio":33,"Sagittarius":28,"Capricorn":25,"Aquarius":32,"Pisces":29}
chrome_total = sum(chrome_sav.values())
print(f"Chrome SAV total: {chrome_total}")
print(f"\nNote: If our total is 335 and correct is 337, we're missing 2 bindus.")
print(f"Grand total bindus in rules = {grand_total}")
print(f"The 335 vs 337 means our rules are missing 2 positions somewhere.")
print()

# COMPARING OUR BAV vs CHROME BAV for SPY
chrome_bav = {
    "Sun": {"Aries":3,"Taurus":3,"Gemini":4,"Cancer":4,"Leo":4,"Virgo":6,"Libra":3,"Scorpio":3,"Sagittarius":3,"Capricorn":6,"Aquarius":7,"Pisces":2},
    "Moon": {"Aries":4,"Taurus":4,"Gemini":5,"Cancer":5,"Leo":5,"Virgo":3,"Libra":4,"Scorpio":5,"Sagittarius":3,"Capricorn":4,"Aquarius":2,"Pisces":5},
    "Mars": {"Aries":2,"Taurus":3,"Gemini":5,"Cancer":3,"Leo":4,"Virgo":3,"Libra":3,"Scorpio":3,"Sagittarius":2,"Capricorn":4,"Aquarius":3,"Pisces":4},
    "Mercury": {"Aries":5,"Taurus":4,"Gemini":5,"Cancer":5,"Leo":3,"Virgo":5,"Libra":4,"Scorpio":5,"Sagittarius":4,"Capricorn":6,"Aquarius":4,"Pisces":4},
    "Jupiter": {"Aries":6,"Taurus":3,"Gemini":5,"Cancer":5,"Leo":4,"Virgo":5,"Libra":4,"Scorpio":5,"Sagittarius":6,"Capricorn":5,"Aquarius":3,"Pisces":5},
    "Venus": {"Aries":6,"Taurus":7,"Gemini":5,"Cancer":4,"Leo":4,"Virgo":2,"Libra":4,"Scorpio":7,"Sagittarius":3,"Capricorn":3,"Aquarius":2,"Pisces":5},
    "Saturn": {"Aries":2,"Taurus":3,"Gemini":4,"Cancer":2,"Leo":6,"Virgo":2,"Libra":3,"Scorpio":4,"Sagittarius":2,"Capricorn":4,"Aquarius":4,"Pisces":3},
}

print("BAV COMPARISON (Our vs Chrome) for SPY:")
for pname in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
    our_total_p = sum(bav[pname].values())
    chr_total_p = sum(chrome_bav[pname].values()) if pname in chrome_bav else 0
    diff = our_total_p - chr_total_p
    print(f"  {pname:<10}: Our={our_total_p}, Chrome={chr_total_p}, Diff={diff:+d}")
    # Find which signs differ
    if pname in chrome_bav:
        for s in SIGNS:
            o = bav[pname][s]
            c = chrome_bav[pname].get(s, 0)
            if o != c:
                print(f"    {s}: Got {o}, Expected {c} (diff={o-c:+d})")

# CHECK: Difference should reveal the BAV rule discrepancy
print("\n\nCHECK JUPITER BAV in detail:")
print(f"Jupiter position: {plons['Jupiter']:.4f}° in {SIGNS[int(plons['Jupiter']/30)%12]}")
print("Jupiter BAV sources and what they contribute to Virgo:")
jup_rules = BAV_RULES_ORIGINAL["Jupiter"]
jup_virgo_5 = int(plons['Jupiter']/30)%12  # Virgo = 5
for src, positions in jup_rules.items():
    src_si = int(plons[src]/30)%12
    for pos in positions:
        tgt_si = (src_si + pos - 1) % 12
        if tgt_si == 5:  # Virgo
            print(f"  {src} in {SIGNS[src_si]} + position {pos} → Virgo ✓")

print("\nChrome says Jupiter.Virgo should have 5, we compute 4. Missing 1 bindu.")
print("Let's check all sources:")
for src, positions in jup_rules.items():
    src_si = int(plons[src]/30)%12
    src_sign = SIGNS[src_si]
    virgo_contributions = [pos for pos in positions if (src_si + pos - 1) % 12 == 5]
    if virgo_contributions:
        print(f"  {src} ({src_sign}) contributes via positions: {virgo_contributions}")
    else:
        print(f"  {src} ({src_sign}) does NOT contribute to Virgo")

print("\n\nCHECK SATURN BAV in detail:")
print(f"Saturn position: {plons['Saturn']:.4f}° in {SIGNS[int(plons['Saturn']/30)%12]}")
print("Looking for which source contributes to Taurus (idx=1) for Saturn BAV:")
sat_rules = BAV_RULES_ORIGINAL["Saturn"]
for src, positions in sat_rules.items():
    src_si = int(plons[src]/30)%12
    src_sign = SIGNS[src_si]
    taurus_contributions = [pos for pos in positions if (src_si + pos - 1) % 12 == 1]
    if taurus_contributions:
        print(f"  {src} ({src_sign}) contributes via positions: {taurus_contributions}")
    else:
        print(f"  {src} ({src_sign}) does NOT contribute to Taurus")
print(f"\nOur Saturn.Taurus = {bav['Saturn']['Taurus']}, Chrome says 3. Missing 1 bindu.")

# Look at alternative SAT BAV rules
# Standard BPHS alternate rules for Saturn:
# "Saturn contributes bindus to 3, 5, 6, 11 from Ascendant"
# Current: "Ascendant":[1,3,4,6,10,11]
# Let's check - maybe it should include position 8 or similar
print("\nAscendant contribution to Saturn BAV:")
asc_si = int(asc_lon/30)%12
print(f"Ascendant at {asc_lon:.4f}° in {SIGNS[asc_si]}")
for pos in sat_rules.get("Ascendant", []):
    tgt_si = (asc_si + pos - 1) % 12
    print(f"  Position {pos} → {SIGNS[tgt_si]}")
