
import csv
from collections import Counter, defaultdict
import re

with open('master_feature_columns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

cats = defaultdict(list)
for r in rows:
    cats[r['category_code']].append(r)

issues = defaultdict(list)  # category_code -> list of issue strings

# ──────────────────────────────────────────────────────────────
# HELPER: collect names per cat
# ──────────────────────────────────────────────────────────────
def names(code):
    return [r['column_name'] for r in cats[code]]

def col_re(code, pattern):
    return [n for n in names(code) if re.search(pattern, n, re.IGNORECASE)]

def missing(code, expected_substr):
    ns = names(code)
    return [s for s in expected_substr if not any(s.lower() in n.lower() for n in ns)]

# ──────────────────────────────────────────────────────────────
# CAT 1A — Natal D1 Core Matrix (1114 cols)
# ──────────────────────────────────────────────────────────────
code = '1A'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 1A: Natal D1 Core Matrix ({len(g)} cols)")
print(f"{'='*60}")

# Planets expected
PLANETS = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
# Check all 9 planets have standard natal fields
EXPECTED_FIELDS = ['Sign_ID','Sign_Name','Local_Degree','Lon_0_360','Nakshatra_ID',
                   'Nakshatra_Name','Pada','House','Exalted_Flag','Debilitated_Flag',
                   'Retrograde_Flag','Combust_Flag','Mulatrikona_Flag','Own_Sign_Flag',
                   'Friendly_Sign_Flag','Enemy_Sign_Flag','Neutral_Sign_Flag',
                   'Velocity_DegPerDay','Declination']

for p in PLANETS:
    for f in EXPECTED_FIELDS:
        key = f'Natal_{p}_{f}'
        if key not in ns:
            issues[code].append(f"MISSING: {key}")

# Check special points: Ascendant, MC, Gulika, Mandi, Upagrahas
SPECIAL_POINTS = ['Ascendant','MC','Gulika','Mandi','Bhrigu_Bindu',
                  'Yogi_Point','Avayogi_Point','Pranapada_Lon']
for sp in SPECIAL_POINTS:
    if not any(sp.lower() in n.lower() for n in ns):
        issues[code].append(f"MISSING special point: {sp}")

# Check Shadbala columns
SHADBALA_COMPS = ['Sthana_Bala','Dig_Bala','Kala_Bala','Cheshta_Bala',
                  'Naisargika_Bala','Drig_Bala','Total_Shadbala','Shadbala_Ratio']
for p in PLANETS[:7]:  # Shadbala for 7 grahas only (not nodes)
    for s in SHADBALA_COMPS:
        key = f'Natal_{p}_{s}'
        if key not in ns:
            issues[code].append(f"MISSING Shadbala: {key}")

# Check Arudha Padas
for h in range(1, 13):
    key = f'Natal_Arudha_Pada_{h}'
    if key not in ns:
        issues[code].append(f"MISSING Arudha Pada: {key}")

# Check Upachaya / Dusthana house lords
for h in range(1, 13):
    key = f'Natal_House_{h}_Lord'
    if key not in ns:
        issues[code].append(f"MISSING house lord: {key}")

# Check Bhava Chalit vs Rasi house placement (separate)
if not any('bhava_chalit' in n.lower() for n in ns):
    issues[code].append("MISSING: Bhava Chalit house placements (separate from Rasi houses)")

# Check Lagna-lord in which house
if not any('lagna_lord' in n.lower() for n in ns):
    issues[code].append("MISSING: Natal_Lagna_Lord columns")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:30]:
    print(f"  {iss}")
if len(issues[code]) > 30:
    print(f"  ... and {len(issues[code])-30} more")

# ──────────────────────────────────────────────────────────────
# CAT 1B — Natal 16 Varga Matrices (12174 cols)
# ──────────────────────────────────────────────────────────────
code = '1B'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 1B: Natal 16 Varga Matrices ({len(g)} cols)")
print(f"{'='*60}")

VARGAS = ['D2','D3','D4','D7','D9','D10','D12','D16','D20','D24','D27','D30','D40','D45','D60']
VARGA_FIELDS = ['Ascendant_Sign','Ascendant_House_Of_D1_Planet',
                'Ascendant_Lord','Ascendant_Lord_Sign','Ascendant_Lord_House']
for p in PLANETS:
    VARGA_FIELDS += [f'{p}_Sign', f'{p}_House', f'{p}_Exalted_Flag',
                     f'{p}_Debilitated_Flag', f'{p}_Own_Sign_Flag']

VIMSHOPAKA_EXPECTED = ['Natal_Sun_Vimshopaka_Bala','Natal_Moon_Vimshopaka_Bala',
                       'Natal_Mars_Vimshopaka_Bala','Natal_Mercury_Vimshopaka_Bala',
                       'Natal_Jupiter_Vimshopaka_Bala','Natal_Venus_Vimshopaka_Bala',
                       'Natal_Saturn_Vimshopaka_Bala']

for v in VARGAS:
    for f in VARGA_FIELDS:
        key = f'Natal_{v}_{f}'
        if key not in ns:
            issues[code].append(f"MISSING: {key}")

for k in VIMSHOPAKA_EXPECTED:
    if k not in ns:
        issues[code].append(f"MISSING Vimshopaka: {k}")

# Check for D1 contamination
d1_in_1b = [n for n in ns if re.match(r'Natal_(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)_(Sign_ID|Nakshatra_ID|Local_Degree)', n)]
if d1_in_1b:
    issues[code].append(f"POSSIBLE D1 LEAKAGE into 1B: {d1_in_1b[:5]}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:30]:
    print(f"  {iss}")
if len(issues[code]) > 30:
    print(f"  ... and {len(issues[code])-30} more")

# ──────────────────────────────────────────────────────────────
# CAT 1C — Natal Extended Esoterics (579 cols)
# ──────────────────────────────────────────────────────────────
code = '1C'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 1C: Natal Extended Esoterics ({len(g)} cols)")
print(f"{'='*60}")

# Check Ashtakvarga per house (houses 1-12)
for h in range(1, 13):
    for p in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']:
        key = f'Natal_{p}_BAV_{h}'
        if key not in ns:
            issues[code].append(f"MISSING BAV: {key}")
    key2 = f'Natal_SAV_{h}'
    if key2 not in ns:
        issues[code].append(f"MISSING SAV: {key2}")

# Check Shodhya Pinda
for h in range(1, 13):
    key = f'Natal_Shodhya_Pinda_{h}'
    if key not in ns:
        issues[code].append(f"MISSING Shodhya Pinda: {key}")

# Check Bhava Bala
for h in range(1, 13):
    key = f'Natal_Bhava_Bala_{h}'
    if key not in ns:
        issues[code].append(f"MISSING Bhava Bala: {key}")

# Check Yoga flags
MAJOR_YOGAS = ['Raj_Yoga','Dhana_Yoga','Viparita_Raj_Yoga','Neechabhanga_Raj_Yoga',
               'Parivartana_Yoga','Gaja_Kesari_Yoga','Budha_Aditya_Yoga',
               'Chandra_Mangal_Yoga','Pancha_Mahapurusha_Yoga','Kemadruma_Yoga',
               'Voshi_Yoga','Veshi_Yoga','Obhayachari_Yoga','Amala_Yoga',
               'Maha_Bhagya_Yoga','Adhi_Yoga']
for y in MAJOR_YOGAS:
    key = f'Natal_{y}_Flag'
    if key not in ns:
        issues[code].append(f"MISSING Yoga flag: {key}")

# Check Sarvatobhadra Chakra
if not any('SBC' in n or 'Sarvatobhadra' in n for n in ns):
    issues[code].append("MISSING: Natal SBC (Sarvatobhadra Chakra) in wrong category (should be Cat 7 but check)")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:30]:
    print(f"  {iss}")
if len(issues[code]) > 30:
    print(f"  ... and {len(issues[code])-30} more")

# ──────────────────────────────────────────────────────────────
# CAT 1D — Natal Panchang (21 cols)
# ──────────────────────────────────────────────────────────────
code = '1D'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 1D: Natal Panchang ({len(g)} cols)")
print(f"{'='*60}")

PANCHANG_MUST = [
    'Natal_Tithi_Number','Natal_Tithi_Name','Natal_Tithi_Type','Natal_Tithi_Paksha','Natal_Tithi_Deity',
    'Natal_Nakshatra_ID','Natal_Nakshatra_Name','Natal_Nakshatra_Lord','Natal_Nakshatra_Pada',
    'Natal_Yoga_ID','Natal_Yoga_Name',
    'Natal_Karana_ID','Natal_Karana_Name','Natal_Karana_Lord',
    'Natal_Vara_ID','Natal_Vara_Name','Natal_Vara_Lord',
    'Natal_Muhurtha_Name',
    'Natal_Rahu_Kaal_Active_Flag',
    'Natal_Gulika_Kaal_Active_Flag',
    'Natal_Abhijit_Muhurtha_Active_Flag',
]
for k in PANCHANG_MUST:
    if k not in ns:
        issues[code].append(f"MISSING: {k}")

# Check for missing sub-elements
if not any('sun_rise' in n.lower() for n in ns):
    issues[code].append("MISSING: Natal sunrise time (needed for Rahu Kaal/Gulika calc)")
if not any('moon_phase' in n.lower() for n in ns):
    issues[code].append("MISSING: Natal Moon phase angle (degrees)")
if not any('ayanamsa_value' in n.lower() for n in ns):
    issues[code].append("MISSING: Natal ayanamsa value used")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 2A — Transit Kinematic Physics (147 cols)
# ──────────────────────────────────────────────────────────────
code = '2A'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 2A: Transit Kinematic Physics ({len(g)} cols)")
print(f"{'='*60}")

# TIME_VARYING issue: ALL 147 flagged as static (is_time_varying=1 but in STATIC_CATS set)
# Actually: CAT 2A IS dynamic — it's wrong to classify it as STATIC. 
# The confusion: transit data IS time-varying. 
tv_2a = sum(1 for r in g if r['is_time_varying'] == '1')
tv_0_2a = sum(1 for r in g if r['is_time_varying'] == '0')
issues[code].append(f"is_time_varying AUDIT: {tv_2a} set to 1, {tv_0_2a} set to 0 — 2A IS dynamic, should all be 1")

# Check all 9 planets + Ascendant have kinematics
KINEM_FIELDS = ['Lon_0_360','Velocity_DegPerDay','Acceleration','Declination',
                'Latitude','Distance_From_Earth','Right_Ascension']
for p in PLANETS + ['Ascendant','MC']:
    for f in KINEM_FIELDS:
        key = f'Transit_{p}_{f}'
        if key not in ns:
            issues[code].append(f"MISSING kinematics: {key}")

# Check for outer planets (should be in transit, often missed)
OUTER = ['Uranus','Neptune','Pluto']
for p in OUTER:
    if not any(p in n for n in ns):
        issues[code].append(f"MISSING outer planet transit kinematics: {p}")

# Check Chara lagna (Hora Lagna, Ghati Lagna, Varnada Lagna)
for cl in ['Hora_Lagna','Ghati_Lagna','Varnada_Lagna','Sree_Lagna']:
    if not any(cl.lower() in n.lower() for n in ns):
        issues[code].append(f"MISSING Chara Lagna: Transit_{cl}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:25]:
    print(f"  {iss}")
if len(issues[code]) > 25:
    print(f"  ... and {len(issues[code])-25} more")

# ──────────────────────────────────────────────────────────────
# CAT 2B — Transit D1 Sky Matrix (850 cols)
# ──────────────────────────────────────────────────────────────
code = '2B'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 2B: Transit D1 Sky Matrix ({len(g)} cols)")
print(f"{'='*60}")

# Check natal-transit angular separations (aspects) for all planet pairs
ASPECT_COLS_EXPECTED = []
for p1 in PLANETS:
    for p2 in PLANETS:
        if p1 != p2:
            key = f'Transit_{p1}_Natal_{p2}_Angle'
            ASPECT_COLS_EXPECTED.append(key)
missing_angles = [k for k in ASPECT_COLS_EXPECTED if k not in ns]
if missing_angles:
    issues[code].append(f"MISSING natal-transit angles: {len(missing_angles)} cols, e.g. {missing_angles[:3]}")

# Check transit-to-natal house ingress flags
for h in range(1,13):
    key = f'Transit_Any_Planet_In_Natal_House_{h}'
    if key not in ns:
        issues[code].append(f"MISSING ingress flag: {key}")

# Check Graha Yuddha (planetary war) flag
if not any('yuddha' in n.lower() or 'war' in n.lower() for n in ns):
    issues[code].append("MISSING: Graha_Yuddha (planetary war) flags for close conjunctions (<1 deg)")

# Check Gochara (transit over natal) flags per planet
for tp in PLANETS:
    for np_ in PLANETS:
        key = f'Transit_{tp}_Conjunct_Natal_{np_}_Flag'
        if key not in ns:
            issues[code].append(f"MISSING Gochara conjunct: {key}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:20]:
    print(f"  {iss}")
if len(issues[code]) > 20:
    print(f"  ... and {len(issues[code])-20} more")

# ──────────────────────────────────────────────────────────────
# CAT 2C — Transit Varga Matrices (5460 cols)
# ──────────────────────────────────────────────────────────────
code = '2C'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 2C: Transit Varga Matrices ({len(g)} cols)")
print(f"{'='*60}")

# Expected: 15 vargas × (Ascendant + 9 planets) × ~N fields
# Check all 15 vargas have all planets
for v in VARGAS:
    for p in PLANETS + ['Ascendant']:
        key = f'Transit_{v}_{p}_Sign'
        if key not in ns:
            issues[code].append(f"MISSING: {key}")

# Check D9 specifically (most critical)
D9_MUST = [f'Transit_D9_{p}_Sign' for p in PLANETS]
D9_MUST += [f'Transit_D9_{p}_House' for p in PLANETS]
for k in D9_MUST:
    if k not in ns:
        issues[code].append(f"MISSING D9: {k}")

# Check for transit varga Ascendant computation (tricky — needs exact time)
if not any('Transit_D1_Ascendant_Sign' in n for n in ns):
    issues[code].append("MISSING: Transit D1 Ascendant (should be in 2A but check 2C)")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:20]:
    print(f"  {iss}")
if len(issues[code]) > 20:
    print(f"  ... and {len(issues[code])-20} more")

# ──────────────────────────────────────────────────────────────
# CAT 2D — Moorti Nirnaya & Macro Ingresses (10 cols)
# ──────────────────────────────────────────────────────────────
code = '2D'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 2D: Moorti Nirnaya & Macro Ingresses ({len(g)} cols)")
print(f"{'='*60}")

# Moorti check: Jupiter, Saturn, Rahu, Ketu should have all 4 moortis
MOORTI_TYPES = ['Metal','Stone','Fire','Water']  # or Gold/Silver/Copper/Iron
MOORTI_PLANETS = ['Jupiter','Saturn','Rahu','Ketu']
for p in MOORTI_PLANETS:
    for m in MOORTI_TYPES:
        key = f'Transit_{p}_Moorti_{m}'
        if key not in ns:
            issues[code].append(f"MISSING Moorti: {key}")

# Missing: Days since last Jupiter ingress, Saturn ingress, Rahu ingress
for p in ['Jupiter','Saturn','Rahu']:
    key = f'Days_Since_{p}_Sign_Ingress'
    if key not in ns:
        issues[code].append(f"MISSING ingress counter: {key}")
    key2 = f'Days_Until_{p}_Next_Sign_Ingress'
    if key2 not in ns:
        issues[code].append(f"MISSING ingress counter: {key2}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 2E — Transit Daily Panchang (34 cols)
# ──────────────────────────────────────────────────────────────
code = '2E'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 2E: Transit Daily Panchang ({len(g)} cols)")
print(f"{'='*60}")

PANCHANG_TRANSIT = [
    'Transit_Tithi_Number','Transit_Tithi_Name','Transit_Tithi_Type',
    'Transit_Tithi_Paksha','Transit_Tithi_Completion_Percent',
    'Transit_Nakshatra_ID','Transit_Nakshatra_Name','Transit_Nakshatra_Lord',
    'Transit_Nakshatra_Pada','Transit_Nakshatra_Completion_Percent',
    'Transit_Yoga_ID','Transit_Yoga_Name','Transit_Yoga_Completion_Percent',
    'Transit_Karana_ID','Transit_Karana_Name','Transit_Karana_Lord',
    'Transit_Vara_ID','Transit_Vara_Name','Transit_Vara_Lord',
    'Transit_Rahu_Kaal_Active_Flag','Transit_Gulika_Kaal_Active_Flag',
    'Transit_Abhijit_Muhurtha_Active_Flag',
    'Transit_Amrit_Kaal_Active_Flag','Transit_Brahma_Muhurtha_Active_Flag',
    'Transit_Sunrise_UTC','Transit_Sunset_UTC',
    'Transit_Moon_Phase_Angle',
    # Missing Chandrashtama
    'Transit_Chandrashtama_Active_Flag',
    'Transit_Sade_Sati_Active_Flag','Transit_Sade_Sati_Phase',
]
for k in PANCHANG_TRANSIT:
    if k not in ns:
        issues[code].append(f"MISSING: {k}")

# Sade Sati is computed per-asset (Moon in 12th/1st/2nd from natal Moon)
# This is a huge daily signal — critical
if not any('sade_sati' in n.lower() for n in ns):
    issues[code].append("MISSING Sade Sati (Saturn over natal Moon ±30 deg) — CRITICAL signal")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 2F — Transit AV Kakshyas & Gochara (93 cols)
# ──────────────────────────────────────────────────────────────
code = '2F'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 2F: Transit AV Kakshyas & Gochara ({len(g)} cols)")
print(f"{'='*60}")

# Should have per planet: Kakshya ruler, Bindu active, BAV score, positive Gochara, Vedha blocked
for p in PLANETS[:7]:  # 7 classical planets for AV
    for f in ['In_Kakshya_Of','Kakshya_Bindu_Active','BAV_Score_In_Current_Sign',
              'Positive_Gochara_Flag','Gochara_Vedha_Blocked']:
        key = f'Transit_{p}_{f}'
        if key not in ns:
            issues[code].append(f"MISSING: {key}")

# Should have Sarvashtakavarga score per house for transit day
for h in range(1,13):
    key = f'Transit_SAV_Score_House_{h}'
    if key not in ns:
        issues[code].append(f"MISSING SAV transit: {key}")

# Missing: Bindus of current transit sign in natal chart
if not any('Bindus_In_Transit_Sign' in n for n in ns):
    issues[code].append("MISSING: Bindus count in current transit sign (from natal BAV) per planet")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 3A — Dasha Systems (30 cols)
# ──────────────────────────────────────────────────────────────
code = '3A'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 3A: Dasha Systems ({len(g)} cols)")
print(f"{'='*60}")

DASHA_MUST = [
    # Vimshottari 5 levels
    'Vimshottari_MD_Lord','Vimshottari_MD_Start','Vimshottari_MD_End','Vimshottari_MD_Elapsed_Pct',
    'Vimshottari_AD_Lord','Vimshottari_AD_Start','Vimshottari_AD_End','Vimshottari_AD_Elapsed_Pct',
    'Vimshottari_PAD_Lord','Vimshottari_PAD_Start','Vimshottari_PAD_End','Vimshottari_PAD_Elapsed_Pct',
    'Vimshottari_Sookshma_Lord','Vimshottari_Sookshma_Start','Vimshottari_Sookshma_End',
    'Vimshottari_Prana_Lord','Vimshottari_Prana_Start','Vimshottari_Prana_End',
    # Yogini Dasha
    'Yogini_MD_Lord','Yogini_MD_Start','Yogini_MD_End',
    'Yogini_AD_Lord','Yogini_AD_Start','Yogini_AD_End',
    # Kalachakra
    'Kalachakra_MD_Lord','Kalachakra_MD_Start','Kalachakra_MD_End',
    'Kalachakra_Deha_Sign','Kalachakra_Jiva_Sign',
    # Ashtottari (found in jyotish — not in current plan)
    'Ashtottari_MD_Lord','Ashtottari_MD_Start','Ashtottari_MD_End',
    'Ashtottari_AD_Lord','Ashtottari_AD_Start','Ashtottari_AD_End',
    # Applicability flags
    'Ashtottari_Dasha_Applicable_Flag',
    'Dwisaptati_Sama_Applicable_Flag',
    'Vimshottari_Dasha_Balance_At_Birth',
    # MD/AD quality
    'Vimshottari_MD_AD_Quality','Vimshottari_MD_Lord_Natal_House',
    'Vimshottari_MD_Lord_Natal_Exalted','Vimshottari_MD_Lord_Natal_Debilitated',
    'Vimshottari_MD_Lord_Natal_Shadbala',
]
for k in DASHA_MUST:
    if k not in ns:
        issues[code].append(f"MISSING: {k}")

# Critical: is_time_varying check
tv_wrong_3a = [r for r in g if r['is_time_varying'] == '0' and 
               r['column_name'] not in ('Vimshottari_Dasha_Balance_At_Birth',
                                        'Kalachakra_Deha_Sign','Kalachakra_Jiva_Sign',
                                        'Ashtottari_Dasha_Applicable_Flag','Dwisaptati_Sama_Applicable_Flag')]
if tv_wrong_3a:
    issues[code].append(f"is_time_varying WRONG for {len(tv_wrong_3a)} dasha columns — should be 1 (changes daily)")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:30]:
    print(f"  {iss}")
if len(issues[code]) > 30:
    print(f"  ... and {len(issues[code])-30} more")

# ──────────────────────────────────────────────────────────────
# CAT 4 — Varshaphala Annual Return (99 cols)
# ──────────────────────────────────────────────────────────────
code = '4'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 4: Varshaphala Annual Return ({len(g)} cols)")
print(f"{'='*60}")

VARSHA_MUST = [
    'Trading_Year','Solar_Return_Timestamp',
    'Varshaphala_Ascendant_Sign','Varshaphala_Ascendant_Lon',
    'Varshaphala_Varsha_Lagna_Lord',
    'Varshaphala_Muntha_Sign','Varshaphala_Muntha_House',
    'Varshaphala_Muntha_Lord',
    'Varshaphala_Year_Lord',  # Varshesh
    'Varshaphala_Pancha_Vargiya_Bala_Sun',  # 5-varga bala, not 16!
    'Varshaphala_Pancha_Vargiya_Bala_Moon',
    'Varshaphala_Pancha_Vargiya_Bala_Mars',
    'Varshaphala_Pancha_Vargiya_Bala_Mercury',
    'Varshaphala_Pancha_Vargiya_Bala_Jupiter',
    'Varshaphala_Pancha_Vargiya_Bala_Venus',
    'Varshaphala_Pancha_Vargiya_Bala_Saturn',
    'Varshaphala_Sahams_Punya',
    'Varshaphala_Sahams_Vida',
    'Varshaphala_Sahams_Raja',
    'Varshaphala_Sahams_Karma',
    'Varshaphala_Tajika_Aspects_Active',
    'Varshaphala_Ithasala_Yogas',
    'Varshaphala_Ishrafa_Yogas',
    'Varshaphala_Nakta_Yoga',
    'Varshaphala_Yamaya_Yoga',
    'Varshaphala_Manahila_Yoga',
    'Varshaphala_Dasha_Current_Lord',  # Varshaphala has its own dasha (Mudda)
    'Varshaphala_Mudda_MD_Lord','Varshaphala_Mudda_AD_Lord',
]
for k in VARSHA_MUST:
    if k not in ns:
        issues[code].append(f"MISSING: {k}")

# BUG: Pancha Vargiya Bala uses 5 vargas (D1,D2,D3,D9,D30) NOT 16
# Check if any 16-varga Bala listed here
sixteen_varga = [n for n in ns if any(f'D{v}' in n for v in [4,7,10,12,16,20,24,27,40,45,60])]
if sixteen_varga:
    issues[code].append(f"BUG: Varshaphala should use Pancha (5) Vargiya Bala not 16-varga: {sixteen_varga[:3]}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 5 — Progressions (199 cols)
# ──────────────────────────────────────────────────────────────
code = '5'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 5: Progressions & Symbolic Time ({len(g)} cols)")
print(f"{'='*60}")

PROG_MUST = ['Progressed_Sun_Lon','Solar_Arc_Progressed_Sun_Lon']
for p in PLANETS:
    PROG_MUST.append(f'Progressed_{p}_Lon')
    PROG_MUST.append(f'Progressed_{p}_Sign')
    PROG_MUST.append(f'Solar_Arc_Progressed_{p}_Lon')
    PROG_MUST.append(f'Progressed_{p}_Aspects_Natal_Sun_Flag')
    PROG_MUST.append(f'Progressed_{p}_Aspects_Natal_Moon_Flag')

# Tertiary progressions (1 day = 1 lunar month)
for p in ['Sun','Moon']:
    PROG_MUST.append(f'Tertiary_Progressed_{p}_Lon')

# Minor progressions
PROG_MUST += ['Minor_Progressed_Sun_Lon','Minor_Progressed_Moon_Lon']

for k in PROG_MUST:
    if k not in ns:
        issues[code].append(f"MISSING: {k}")

# Check for Time Lord (Solo technique — 1 year = 1 day)
if not any('time_lord' in n.lower() for n in ns):
    issues[code].append("MISSING: Time Lord technique columns (symbolic direction)")

# Check Dwadashamsha progression (1 month = 1 day)
if not any('dwadashamsha' in n.lower() for n in ns):
    issues[code].append("MISSING: Dwadashamsha (12-fold) progressions")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:20]:
    print(f"  {iss}")
if len(issues[code]) > 20:
    print(f"  ... and {len(issues[code])-20} more")

# ──────────────────────────────────────────────────────────────
# CAT 6 — KP System (238 cols)
# ──────────────────────────────────────────────────────────────
code = '6'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 6: KP System ({len(g)} cols)")
print(f"{'='*60}")

# 12 cusps × 4 fields = 48
for h in range(1,13):
    for f in ['Lon','Sign_Lord','Nakshatra_Lord','Sub_Lord','Sub_Sub_Lord']:
        key = f'KP_Cusp_{h}_{f}'
        if key not in ns:
            issues[code].append(f"MISSING KP cusp: {key}")

# 9 planets × (Nakshatra_Lord + Sub_Lord + Sub_Sub_Lord) = 27
for p in PLANETS:
    for f in ['Nakshatra_Lord','Sub_Lord','Sub_Sub_Lord']:
        key = f'KP_{p}_{f}'
        if key not in ns:
            issues[code].append(f"MISSING KP planet: {key}")

# Significators per house (which planets signify each house via cusp ownership chains)
for h in range(1,13):
    key = f'KP_House_{h}_Significators'
    if key not in ns:
        issues[code].append(f"MISSING KP significators: {key}")

# Ruling Planets at time of query
for rp in ['RP_Vara_Lord','RP_Nakshatra_Lord','RP_Sub_Lord','RP_Ascendant_Lord']:
    key = f'KP_{rp}'
    if key not in ns:
        issues[code].append(f"MISSING KP Ruling Planets: {key}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:25]:
    print(f"  {iss}")
if len(issues[code]) > 25:
    print(f"  ... and {len(issues[code])-25} more")

# ──────────────────────────────────────────────────────────────
# CAT 7 — Advanced Chakras SBC/Kota/Sanghatta (37 cols)
# ──────────────────────────────────────────────────────────────
code = '7'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 7: Advanced Chakras ({len(g)} cols)")
print(f"{'='*60}")

# SBC: all 9 planets should have at minimum 2 vedha columns
for p in PLANETS:
    for v in ['Vedha_On_Natal_Nakshatra_Flag','Vedha_On_Name_Consonant_Flag']:
        key = f'SBC_{p}_{v}'
        if key not in ns:
            issues[code].append(f"MISSING SBC: {key}")

# Missing: SBC Rasi Vedha, Tithi Vedha, Swara Vedha (3 more types)
for p in PLANETS:
    for v in ['Rasi_Vedha_Flag','Tithi_Vedha_Flag','Swara_Vedha_Flag']:
        key = f'SBC_{p}_{v}'
        if key not in ns:
            issues[code].append(f"MISSING SBC Vedha type: {key}")

# Kota Chakra
for k in ['Kota_Chakra_Transit_Zone','Kota_Chakra_Stambha_Flag',
          'Kota_Chakra_Madhya_Flag','Kota_Chakra_Praakara_Flag',
          'Kota_Swami','Kota_Pala']:
    if k not in ns:
        issues[code].append(f"MISSING Kota Chakra: {k}")

# Sanghatta Chakra
if not any('sanghatta' in n.lower() for n in ns):
    issues[code].append("MISSING: All Sanghatta Chakra columns")

# Surya Siddhanta Chakra
if not any('surya_siddhanta' in n.lower() or 'chakra_score' in n.lower() for n in ns):
    issues[code].append("MISSING: Chakra score / Surya Siddhanta Chakra")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code][:25]:
    print(f"  {iss}")
if len(issues[code]) > 25:
    print(f"  ... and {len(issues[code])-25} more")

# ──────────────────────────────────────────────────────────────
# CAT 8 — Intraday Muhurtha / Micro-Time (9 cols)
# ──────────────────────────────────────────────────────────────
code = '8'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 8: Intraday Muhurtha Micro-Time ({len(g)} cols)")
print(f"{'='*60}")

MUHURTHA_MUST = [
    'Muhurtha_Panchapakshi_Asset_Bird','Muhurtha_Panchapakshi_Current_Activity',
    'Muhurtha_Panchapakshi_Activity_Score',  # numerical score 0-5
    'Muhurtha_Hora_Lord','Muhurtha_Hora_Number',
    'Muhurtha_Choghadiya_State','Muhurtha_Choghadiya_Score',
    'Muhurtha_Gauri_Panchangam_State',
    # Missing items
    'Muhurtha_Vela_Current','Muhurtha_Kalam_Current',  # Tamil Muhurtha elements
    'Muhurtha_Abhijit_Active','Muhurtha_Brahma_Active',
    'Muhurtha_Rahu_Kaal_Active','Muhurtha_Gulika_Kaal_Active',
    'Muhurtha_Yama_Ghantam_Active',  # Tamil equivalent
    'Muhurtha_Amrit_Kaal_Active',
    'Muhurtha_Pushkara_Navamsa_Active',
    'Muhurtha_Pushkara_Bhaga_Active',
    'Muhurtha_Market_Open_Hora_Lord',  # static daily feature
    'Muhurtha_Panchapakshi_Enemy_Bird_Flag',  # enemy bird = bad timing
]
for k in MUHURTHA_MUST:
    if k not in ns:
        issues[code].append(f"MISSING: {k}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 9 — Mundane Astrology / Macro Economy (224 cols)
# ──────────────────────────────────────────────────────────────
code = '9'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 9: Mundane Astrology ({len(g)} cols)")
print(f"{'='*60}")

# USA natal chart transit angles — verified as present
# Check for India natal chart
if not any('india' in n.lower() for n in ns):
    issues[code].append("MISSING: India natal chart transit angles (1947-08-15 chart)")

# Check for NYSE natal chart
if not any('nyse' in n.lower() for n in ns):
    issues[code].append("MISSING: NYSE natal chart transit angles (1792-05-17 chart)")

# Check for Federal Reserve natal chart
if not any('fed' in n.lower() or 'federal' in n.lower() for n in ns):
    issues[code].append("MISSING: Federal Reserve natal chart angles (1913-12-23 chart)")

# Check for Dollar (Bretton Woods / USD) chart
if not any('dollar' in n.lower() or 'usd' in n.lower() or 'bretton' in n.lower() for n in ns):
    issues[code].append("MISSING: USD/Bretton Woods natal chart angles (1944-07-22)")

# Jupiter-Saturn cycle
if not any('jupiter_saturn' in n.lower() for n in ns):
    issues[code].append("MISSING: Jupiter-Saturn conjunction cycle features (great conjunction)")

# Eclipse features
if not any('eclipse' in n.lower() for n in ns):
    issues[code].append("MISSING: Solar/Lunar eclipse proximity flags")

# Ingress of outer planets to key signs
if not any('ingress_flag' in n.lower() for n in ns):
    issues[code].append("MISSING: Jupiter/Saturn/Rahu sign ingress dates and proximity counters")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# CAT 10 — ML Interaction Crosses (173 cols)
# ──────────────────────────────────────────────────────────────
code = '10'
g = cats[code]
ns = [r['column_name'] for r in g]
print(f"\n{'='*60}")
print(f"CAT 10: ML Interaction Crosses ({len(g)} cols)")
print(f"{'='*60}")

# Check for Dasha-Transit crosses
if not any('dasha' in n.lower() and 'transit' in n.lower() for n in ns):
    issues[code].append("MISSING: Dasha × Transit interaction crosses (e.g. MD_Lord_Transit_Sign)")

# Check for Varga-Dasha crosses  
if not any('varga' in n.lower() or 'D9' in n for n in ns):
    issues[code].append("MISSING: Varga × Dasha interaction crosses")

# Double transit flags
dt_flags = [n for n in ns if 'double_transit' in n.lower()]
print(f"  Double-transit flags found: {len(dt_flags)}")

# Check cross naming consistency
mixed_case = [n for n in ns if n != n and n != n.upper()]
print(f"  Mixed case issues: {len(mixed_case)}")

print(f"Issues found: {len(issues[code])}")
for iss in issues[code]:
    print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# MARKET CATEGORIES
# ──────────────────────────────────────────────────────────────
for code in ['MKT_PRICE','MKT_TECH','MKT_CAL','MKT_CONTEXT','MKT_TARGET']:
    g = cats.get(code,[])
    ns = [r['column_name'] for r in g]
    print(f"\n{'='*60}")
    print(f"CAT {code}: ({len(g)} cols)")
    print(f"{'='*60}")
    
    # Type issues
    bool_t = [r for r in g if r['data_type'] == 'BOOL']
    cat_t  = [r for r in g if r['data_type'] == 'CATEGORY']
    print(f"  BOOL type: {len(bool_t)} (non-standard — should be BOOLEAN or INT 0/1)")
    print(f"  CATEGORY type: {len(cat_t)} (non-standard — should be TEXT or INT)")
    
    if code == 'MKT_PRICE':
        for k in ['Open','High','Low','Close','Volume','VWAP','Adj_Close']:
            if k not in ns:
                issues[code].append(f"MISSING: {k}")
    
    if code == 'MKT_TECH':
        for k in ['sma_10','sma_20','sma_50','sma_200','rsi_14','macd','macd_signal',
                  'bb_upper','bb_lower','bb_width','atr_14','adx_14','cci_14']:
            if k not in ns:
                issues[code].append(f"MISSING: {k}")
    
    if code == 'MKT_TARGET':
        for k in ['ret_1d','ret_5d','ret_21d','ret_63d','direction_1d','direction_5d',
                  'vol_realized_10d','sharpe_21d','max_drawdown_21d']:
            if k not in ns:
                issues[code].append(f"MISSING: {k}")
    
    if code == 'MKT_CAL':
        for k in ['is_monthly_opex','is_quad_witching','days_to_next_opex',
                  'is_fed_meeting_day','is_fomc_day']:
            if k not in ns:
                issues[code].append(f"MISSING: {k}")
    
    if code == 'MKT_CONTEXT':
        for k in ['VIX','VVIX','SPX','NDX','Yield_10Y','Yield_2Y',
                  'Yield_Spread_10Y_2Y','DXY','Gold_Price','Oil_Price',
                  'Credit_Spread_HY','Put_Call_Ratio']:
            if k not in ns:
                issues[code].append(f"MISSING: {k}")
    
    print(f"Issues found: {len(issues[code])}")
    for iss in issues[code]:
        print(f"  {iss}")

# ──────────────────────────────────────────────────────────────
# GLOBAL SUMMARY
# ──────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("GLOBAL SUMMARY OF ALL ISSUES")
print(f"{'='*60}")
total = sum(len(v) for v in issues.values())
print(f"Total issues across all categories: {total}")
print()
for code in sorted(issues.keys()):
    print(f"  [{code}] {len(issues[code])} issues")
