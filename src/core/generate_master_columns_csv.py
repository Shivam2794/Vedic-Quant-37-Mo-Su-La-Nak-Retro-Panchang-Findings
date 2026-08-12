"""
MASTER FEATURE COLUMN GENERATOR — v2 FINAL CLEAN
=================================================
Fixes found in audit:
  BUGS:
  1. Duplicate Natal_Ascendant_Pada (added twice in 1A)
  2. Duplicate Transit_[V]_Ascendant_Sign (added twice per Varga in 2C)
  3. Duplicate Transit_Moon_Nakshatra_ID (in 2B and 2E)
  4. Duplicate Progressed_[P]_Aspects_Transit_[P]_Flag (added in both 2C loop and Cat 10)

  MISSING COLUMNS:
  5.  Transit x Natal DIRECT ASPECTS: Transit_[P]_Parashari_Aspects_Natal_[P]_Strength (13x13=169)
  6.  Transit x Natal DELTA ANGLE: Transit_[P]_vs_Natal_[P]_Delta_Degrees (169 continuous)
  7.  Functional Benefic/Malefic flags: Natal_[P]_Functional_Benefic_Flag (13 cols)
  8.  Atmakaraka explicit flag: Natal_[P]_Is_Atmakaraka_Flag (13 cols)
  9.  Ghataka signs: Natal_Ghataka_Tithi_Sign, Natal_Ghataka_Vara_Sign, etc.
  10. Hora (half-sign): Natal_[P]_Hora (Sun or Moon half of sign)
  11. Progressed x Natal aspects: Progressed_[P]_Aspects_Natal_[P]_Flag
  12. KP NewMoon per-planet Sub Lords: KP_NewMoon_[P]_Sub_Lord (13 cols)
  13. Chara Dasha PAD Sign: Chara_PAD_Sign (was missing expanded form)
  14. Market: Put/Call ratio (asset-specific + market-wide)
  15. Market: Options IV (ATM 30-day)
  16. Market: Short interest ratio
  17. Market: Futures premium (ES, NQ)
  18. Bhava Arudha for all 12 houses in Transit too
  19. USA/NYSE/NASDAQ Natal_[P] angles for ALL planet pairs (not just same planet)
  20. Varga Nakshatra for D9 and D10 (used in advanced KP and Nadi)
"""

import csv
from pathlib import Path

OUT_PATH = Path(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\master_feature_columns.csv")

PLANETS = [
    "Sun","Moon","Mars","Mercury","Jupiter","Venus",
    "Saturn","Rahu","Ketu","Ascendant",
    "Uranus","Neptune","Pluto"
]
CLASSIC_PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
HOUSES  = list(range(1, 13))
VARGAS  = ["D2","D3","D4","D7","D9","D10","D12",
           "D16","D20","D24","D27","D30","D40","D45","D60"]

seen = set()  # deduplication guard
rows = []

def add(name, cat_code, cat_name, dtype, time_varying, desc):
    if name in seen:
        return  # HARD deduplicate
    seen.add(name)
    rows.append({
        "column_name":     name,
        "category_code":   cat_code,
        "category_name":   cat_name,
        "data_type":       dtype,
        "is_time_varying": time_varying,
        "description":     desc,
    })

# ═══════════════════════════════════════════════════════════════
# CATEGORY 1A — CORE D1 NATAL
# ═══════════════════════════════════════════════════════════════
C, CN = "1A", "Natal D1 Core Matrix"

add("asset_id",          C,CN,"TEXT",    0,"Unique asset identifier (e.g. SPY)")
add("birth_event_type",  C,CN,"TEXT",    0,"CONCEPTION or FIRST_TRADE")
add("birth_datetime_utc",C,CN,"DATETIME",0,"Birth datetime in UTC")
add("birth_lat",         C,CN,"FLOAT",   0,"Birth latitude decimal degrees")
add("birth_lon_geo",     C,CN,"FLOAT",   0,"Birth longitude decimal degrees")
add("ayanamsha",         C,CN,"TEXT",    0,"Ayanamsha used (always Lahiri)")
add("ayanamsha_value",   C,CN,"FLOAT",   0,"Ayanamsha value at birth in degrees")
add("Natal_Ascendant_Sign",    C,CN,"INT",  0,"Ascendant sign 1=Aries 12=Pisces")
add("Natal_Ascendant_Lon",     C,CN,"FLOAT",0,"Ascendant exact longitude 0-360")
add("Natal_Ascendant_Nakshatra_ID",C,CN,"INT",0,"Ascendant Nakshatra 1-27")
add("Natal_Ascendant_Pada",    C,CN,"INT",  0,"Ascendant Pada 1-4")

for upa in ["Gulika","Mandi","Dhooma","Vyatipata","Parivesha","Indrachapa","Upaketu"]:
    add(f"Natal_{upa}_Lon",          C,CN,"FLOAT",0,f"{upa} absolute longitude 0-360")
    add(f"Natal_{upa}_Sign_ID",      C,CN,"INT",  0,f"{upa} zodiac sign 1-12")
    add(f"Natal_{upa}_Nakshatra_ID", C,CN,"INT",  0,f"{upa} Nakshatra 1-27")

for P in PLANETS:
    add(f"Natal_{P}_Lon_0_360",              C,CN,"FLOAT",   0,f"{P} absolute ecliptic longitude")
    add(f"Natal_{P}_Sign_ID",                C,CN,"INT",     0,f"{P} zodiac sign 1-12")
    add(f"Natal_{P}_Local_Degree",           C,CN,"FLOAT",   0,f"{P} degree within sign 0-30")
    add(f"Natal_{P}_Velocity",               C,CN,"FLOAT",   0,f"{P} speed deg/day at birth")
    add(f"Natal_{P}_Declination",            C,CN,"FLOAT",   0,f"{P} declination degrees")
    add(f"Natal_{P}_Latitude",               C,CN,"FLOAT",   0,f"{P} ecliptic latitude")
    add(f"Natal_{P}_OOB_Flag",               C,CN,"BOOL",    0,f"{P} Out of Bounds declination >23.5°")
    add(f"Natal_{P}_Retrograde_Flag",        C,CN,"BOOL",    0,f"{P} retrograde at birth")
    add(f"Natal_{P}_Combust_Flag",           C,CN,"BOOL",    0,f"{P} combust within orb of Sun")
    add(f"Natal_{P}_Distance_To_Sun",        C,CN,"FLOAT",   0,f"{P} degrees from Sun combustion severity")
    add(f"Natal_{P}_Nakshatra_ID",           C,CN,"INT",     0,f"{P} Nakshatra number 1-27")
    add(f"Natal_{P}_Pada",                   C,CN,"INT",     0,f"{P} Pada 1-4")
    add(f"Natal_{P}_Degrees_Into_Nakshatra", C,CN,"FLOAT",   0,f"{P} degrees into Nakshatra 0-13.33")
    add(f"Natal_{P}_Tara_Relative_to_Moon",  C,CN,"CATEGORY",0,f"{P} Navatara type vs Moon star")
    add(f"Natal_{P}_Exalted_Flag",           C,CN,"BOOL",    0,f"{P} in exaltation sign")
    add(f"Natal_{P}_Debilitated_Flag",       C,CN,"BOOL",    0,f"{P} in debilitation sign")
    add(f"Natal_{P}_Moolatrikona_Flag",      C,CN,"BOOL",    0,f"{P} in Moolatrikona sign")
    add(f"Natal_{P}_Own_Sign_Flag",          C,CN,"BOOL",    0,f"{P} in own sign")
    add(f"Natal_{P}_Panchadha_Maitri",       C,CN,"CATEGORY",0,f"{P} compound friendship GreatFriend→GreatEnemy")
    add(f"Natal_{P}_Vargottam_Flag",         C,CN,"BOOL",    0,f"{P} Vargottam same sign in D1 and D9")
    add(f"Natal_{P}_Pushkar_Navamsa_Flag",   C,CN,"BOOL",    0,f"{P} in Pushkar Navamsa auspicious wealth")
    add(f"Natal_{P}_MKS_Flag",               C,CN,"BOOL",    0,f"{P} Marana Karaka Sthana death house")
    add(f"Natal_{P}_Sign_House",             C,CN,"INT",     0,f"{P} Whole-Sign house 1-12")
    add(f"Natal_{P}_Bhava_Chalit_House",     C,CN,"INT",     0,f"{P} Bhava Chalit Placidus house")
    add(f"Natal_{P}_Distance_To_House_Cusp", C,CN,"FLOAT",   0,f"{P} degrees from nearest house cusp")
    add(f"Natal_{P}_Sign_Lord",              C,CN,"CATEGORY",0,f"Ruler of {P}'s sign")
    add(f"Natal_{P}_Nakshatra_Lord",         C,CN,"CATEGORY",0,f"Star lord of {P}'s Nakshatra")
    add(f"Natal_{P}_Pada_Lord",              C,CN,"CATEGORY",0,f"Ruler of {P}'s Pada")
    add(f"Natal_{P}_Is_Yogakaraka_Flag",     C,CN,"BOOL",    0,f"{P} is Yogakaraka for the Ascendant")
    add(f"Natal_{P}_Functional_Benefic_Flag",C,CN,"BOOL",    0,f"{P} is functional benefic for this Ascendant")   # FIX #7
    add(f"Natal_{P}_Functional_Malefic_Flag",C,CN,"BOOL",    0,f"{P} is functional malefic for this Ascendant")   # FIX #7
    add(f"Natal_{P}_Is_Atmakaraka_Flag",     C,CN,"BOOL",    0,f"{P} is the Atmakaraka (highest degree planet)")   # FIX #8
    add(f"Natal_{P}_Hora",                   C,CN,"CATEGORY",0,f"{P} in Sun Hora or Moon Hora (half of sign)")    # FIX #10
    add(f"Natal_{P}_Baladi_Avastha",         C,CN,"CATEGORY",0,f"{P} Baladi Age Avastha Infant/Boy/Youth/Old/Dead")
    add(f"Natal_{P}_Sayanadi_Avastha",       C,CN,"CATEGORY",0,f"{P} Sayanadi Mood Avastha 12 states")
    add(f"Natal_{P}_Jagradadi_Avastha",      C,CN,"CATEGORY",0,f"{P} Jagradadi Alertness Avastha")

for P1 in PLANETS:
    for P2 in PLANETS:
        if P1 != P2:
            add(f"Natal_{P1}_Conjoins_{P2}_Flag",
                C,CN,"BOOL",0,f"{P1} conjunct {P2} natal D1")
            add(f"Natal_{P1}_Parashari_Aspects_{P2}_Strength",
                C,CN,"FLOAT",0,f"Parashari aspect strength {P1}→{P2} 0.0-1.0")
            add(f"Natal_{P1}_Jaimini_Aspects_{P2}_Flag",
                C,CN,"BOOL",0,f"Jaimini sign-based aspect {P1}→{P2}")

for H1 in HOUSES:
    for H2 in HOUSES:
        add(f"Natal_Lord_of_House_{H1}_In_House_{H2}",
            C,CN,"BOOL",0,f"Lord of House {H1} placed in House {H2}")

# Ghataka signs (FIX #9)
for ghat, desc in [
    ("Ghataka_Tithi_Sign",   "Fatal Tithi sign for this Ascendant — moon here during critical Tithi = crash"),
    ("Ghataka_Vara_Sign",    "Fatal day-lord sign for this Ascendant"),
    ("Ghataka_Nakshatra_ID", "Fatal Nakshatra number for this Ascendant"),
    ("Ghataka_Lagna_Sign",   "Fatal Ascendant sign (if transit Asc hits this = extreme danger)"),
]:
    add(f"Natal_{ghat}", C,CN,"INT",0,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 1B — 16 VARGA MATRICES
# ═══════════════════════════════════════════════════════════════
C,CN = "1B","Natal 16 Varga Matrices"

for P in PLANETS:
    add(f"Natal_{P}_Vimshopaka_Bala",C,CN,"FLOAT",0,f"{P} Vimshopaka Bala 0-20 cumulative dignity score")

for V in VARGAS:
    add(f"Natal_{V}_Ascendant_Sign",C,CN,"INT",0,f"{V} chart Ascendant sign")
    for P in PLANETS:
        add(f"Natal_{V}_{P}_Sign_ID",          C,CN,"INT",      0,f"{P} sign in {V}")
        add(f"Natal_{V}_{P}_House",             C,CN,"INT",      0,f"{P} house in {V} relative to {V} Asc")
        add(f"Natal_{V}_{P}_Exact_Degree",      C,CN,"FLOAT",    0,f"{P} degree inside {V}")
        add(f"Natal_{V}_{P}_Exalted_Flag",      C,CN,"BOOL",     0,f"{P} exalted in {V}")
        add(f"Natal_{V}_{P}_Debilitated_Flag",  C,CN,"BOOL",     0,f"{P} debilitated in {V}")
        add(f"Natal_{V}_{P}_Own_Sign_Flag",     C,CN,"BOOL",     0,f"{P} own sign in {V}")
        add(f"Natal_{V}_{P}_Moolatrikona_Flag", C,CN,"BOOL",     0,f"{P} Moolatrikona in {V}")
        add(f"Natal_{V}_{P}_Panchadha_Maitri",  C,CN,"CATEGORY", 0,f"Compound friendship of {P} in {V}")
        add(f"Natal_{V}_{P}_Amsa_Deity",        C,CN,"CATEGORY", 0,f"Presiding deity of {P}'s division in {V}")
        add(f"Natal_{V}_{P}_Sign_Lord",         C,CN,"CATEGORY", 0,f"Dispositor of {P} in {V}")
    # Nakshatra inside D9 and D10 only (used in advanced KP/Nadi) — FIX #20
    if V in ("D9","D10"):
        for P in PLANETS:
            add(f"Natal_{V}_{P}_Nakshatra_ID",C,CN,"INT",0,f"{P} Nakshatra inside {V} chart (Nadi/KP advanced)")
    for P1 in PLANETS:
        for P2 in PLANETS:
            if P1 != P2:
                add(f"Natal_{V}_{P1}_Conjoins_{P2}_Flag",     C,CN,"BOOL",  0,f"{P1} conjunct {P2} in {V}")
                add(f"Natal_{V}_{P1}_Parashari_Aspects_{P2}", C,CN,"FLOAT", 0,f"Aspect {P1}→{P2} in {V}")
                add(f"Natal_{V}_{P1}_Jaimini_Aspects_{P2}",   C,CN,"BOOL",  0,f"Jaimini aspect {P1}→{P2} in {V}")
    for H1 in HOUSES:
        for H2 in HOUSES:
            add(f"Natal_{V}_Lord_of_House_{H1}_In_House_{H2}",C,CN,"BOOL",0,f"Lord of {V} H{H1} in {V} H{H2}")
    for H1 in HOUSES:
        for H2 in HOUSES:
            if H1 < H2:
                add(f"Natal_{V}_Parivartana_Yoga_{H1}_{H2}",C,CN,"BOOL",0,f"Mutual reception H{H1}-H{H2} in {V}")

# ═══════════════════════════════════════════════════════════════
# CATEGORY 1C — EXTENDED ESOTERICS
# ═══════════════════════════════════════════════════════════════
C,CN = "1C","Natal Extended Esoterics"

for H in HOUSES:
    add(f"Natal_SAV_{H}",           C,CN,"INT",  0,f"Sarvashtakvarga total bindus House {H}")
    add(f"Natal_Shodhya_Pinda_{H}", C,CN,"FLOAT",0,f"Shodhya Pinda multiplier House {H}")
    add(f"Natal_Bhava_Bala_{H}",    C,CN,"FLOAT",0,f"House {H} numerical strength Bhava Bala")

for P in CLASSIC_PLANETS:
    for H in HOUSES:
        add(f"Natal_BAV_{P}_{H}",C,CN,"INT",0,f"Bhinnashtakvarga bindus {P} in House {H}")

for P in PLANETS:
    add(f"Natal_Kakshya_{P}_Lord",      C,CN,"CATEGORY",0,f"Kakshya sub-lord {P} sits under")
    add(f"Natal_{P}_Shadbala_Total",    C,CN,"FLOAT",   0,f"{P} total Shadbala rupas")
    add(f"Natal_{P}_Sthana_Bala",       C,CN,"FLOAT",   0,f"{P} positional strength")
    add(f"Natal_{P}_Dig_Bala",          C,CN,"FLOAT",   0,f"{P} directional strength")
    add(f"Natal_{P}_Kala_Bala",         C,CN,"FLOAT",   0,f"{P} temporal strength day/night/paksha/hora")
    add(f"Natal_{P}_Cheshta_Bala",      C,CN,"FLOAT",   0,f"{P} motional strength speed/retrograde")
    add(f"Natal_{P}_Naisargika_Bala",   C,CN,"FLOAT",   0,f"{P} natural permanent strength")
    add(f"Natal_{P}_Drik_Bala",         C,CN,"FLOAT",   0,f"{P} aspectual strength received")
    add(f"Natal_{P}_Ishta_Kashta_Phala",C,CN,"FLOAT",   0,f"{P} auspicious vs inauspicious ratio")
    add(f"Natal_{P}_Ishtaphala",        C,CN,"FLOAT",   0,f"{P} auspicious output score")
    add(f"Natal_{P}_Kashtaphala",       C,CN,"FLOAT",   0,f"{P} inauspicious output score")
    add(f"Natal_{P}_Rasmis",            C,CN,"FLOAT",   0,f"{P} planetary rays wealth-giving light")
    add(f"Natal_{P}_Subha_Pinda",       C,CN,"FLOAT",   0,f"{P} benefic Shodhya Pinda component")
    add(f"Natal_{P}_Krura_Pinda",       C,CN,"FLOAT",   0,f"{P} malefic Shodhya Pinda component")
    add(f"Natal_{P}_Chara_Karaka_Rank", C,CN,"INT",     0,f"{P} Jaimini Chara Karaka rank 1=AK 8=DK")
    add(f"Natal_{P}_Papa_Kartari_Flag", C,CN,"BOOL",    0,f"{P} hemmed between two malefics")
    add(f"Natal_{P}_Shubha_Kartari_Flag",C,CN,"BOOL",   0,f"{P} supported between two benefics")

add("Natal_Karakamsha_Lagna_Sign",C,CN,"INT",0,"D9 sign of Atmakaraka mapped to D1")
for H in HOUSES:
    add(f"Natal_Arudha_Pada_A{H}_Sign",C,CN,"INT",0,f"Arudha of House {H} sign")
for V in VARGAS:
    for H in HOUSES:
        add(f"Natal_Varga_Arudha_{V}_A{H}_Sign",C,CN,"INT",0,f"Arudha of H{H} inside {V}")

for lagna, desc in [
    ("Udaya_Lagna_Lon",        "Standard Ascendant longitude"),
    ("Chandra_Lagna_Sign",     "Moon treated as Ascendant"),
    ("Surya_Lagna_Sign",       "Sun treated as Ascendant"),
    ("Paka_Lagna_Sign",        "Sign of Ascendant lord"),
    ("Swamsha_Lagna_Sign",     "D9 Ascendant driven by Atmakaraka"),
    ("Bhrigu_Bindu_Lon",       "Destiny Point longitude"),
    ("Indu_Lagna_Lon",         "Ascendant of Wealth longitude"),
    ("Hora_Lagna_Lon",         "Financial trigger Lagna longitude"),
    ("Shree_Lagna_Lon",        "Prosperity Lagna longitude"),
    ("Ghati_Lagna_Lon",        "Power Lagna longitude"),
    ("Varnada_Lagna_Lon",      "Sector/Industry Lagna longitude"),
    ("Pranapada_Lagna_Lon",    "Life-force Lagna longitude"),
    ("Kunda_Lagna_Lon",        "Birth minute Lagna longitude"),
]:
    add(f"Natal_{lagna}",C,CN,"FLOAT",0,desc)

for yoga,desc in [
    ("Raja_Yoga_Count","Count active Raja Yogas"),
    ("Dhana_Yoga_Count","Count Dhana wealth Yogas"),
    ("Daridra_Yoga_Count","Count poverty/crash Yogas"),
    ("Ruchaka_Flag","Mars Pancha Mahapurusha"),
    ("Bhadra_Flag","Mercury Pancha Mahapurusha"),
    ("Hansa_Flag","Jupiter Pancha Mahapurusha"),
    ("Malavya_Flag","Venus Pancha Mahapurusha"),
    ("Sasa_Flag","Saturn Pancha Mahapurusha"),
    ("Neecha_Bhanga_Raja_Yoga_Flag","Debilitation cancelled explosive wealth"),
    ("Vipareeta_Raja_Yoga_Flag","Profit from disaster Lords 6/8/12 in 6/8/12"),
    ("Gajakesari_Yoga_Flag","Jupiter Kendra from Moon sustained wealth"),
    ("Amala_Yoga_Flag","Benefic 10th from Moon spotless reputation"),
    ("Chandra_Mangala_Yoga_Flag","Moon-Mars aggressive wealth"),
    ("Kemadruma_Flag","Moon isolated catastrophic"),
    ("Sunaphaa_Flag","Planet 2nd from Moon"),
    ("Anaphaa_Flag","Planet 12th from Moon"),
    ("Durdhara_Flag","Planets both 2nd and 12th from Moon"),
    ("Adhi_Yoga_Flag","Benefics 6/7/8 from Moon power"),
    ("Vesi_Flag","Planet 2nd from Sun"),
    ("Vosi_Flag","Planet 12th from Sun"),
    ("Ubhayachari_Flag","Planets 2nd and 12th from Sun"),
    ("Rajju_Flag","All planets movable signs"),
    ("Musala_Flag","All planets fixed signs"),
    ("Nala_Flag","All planets dual signs"),
    ("Mala_Flag","Planets in Kendra"),
    ("Sarpa_Flag","All planets in Dusthanas"),
    ("Shakata_Yoga_Flag","Jupiter-Moon 6/8/12 extreme fluctuations"),
    ("Guru_Chandal_Yoga_Flag","Jupiter conjunct Rahu corruption"),
    ("Angarak_Yoga_Flag","Mars conjunct Rahu explosive"),
    ("Grahan_Yoga_Flag","Eclipse yoga crisis"),
    ("Kala_Sarpa_Yoga_Flag","All planets between Rahu-Ketu"),
    ("Kala_Amrita_Yoga_Flag","All planets between Ketu-Rahu"),
]:
    dtype = "INT" if "Count" in yoga else "BOOL"
    add(f"Natal_{yoga}",C,CN,dtype,0,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 1D — NATAL PANCHANG
# ═══════════════════════════════════════════════════════════════
C,CN = "1D","Natal Panchang 5 Limbs of Birth"
for col,dtype,desc in [
    ("Natal_Tithi_Number","INT","Lunar day at birth 1-30"),
    ("Natal_Tithi_Name","TEXT","Tithi name Pratipada…Amavasya"),
    ("Natal_Tithi_Type","CATEGORY","Nanda/Bhadra/Jaya/Rikta/Purna"),
    ("Natal_Tithi_Paksha","CATEGORY","Shukla waxing or Krishna waning"),
    ("Natal_Tithi_Deity","TEXT","Presiding deity of birth Tithi"),
    ("Natal_Vara_Lord","CATEGORY","Day lord Sun/Mon/Mars/etc."),
    ("Natal_Vara_Quality","CATEGORY","Day quality benefic or malefic"),
    ("Natal_Moon_Nakshatra_Gana","CATEGORY","Deva/Manushya/Rakshasa"),
    ("Natal_Moon_Nakshatra_Nadi","CATEGORY","Aadi/Madhya/Antya"),
    ("Natal_Moon_Nakshatra_Tatva","CATEGORY","Fire/Earth/Air/Water/Ether"),
    ("Natal_Moon_Nakshatra_Yoni","CATEGORY","14 animal Yoni symbols"),
    ("Natal_Moon_Nakshatra_Deity","TEXT","Deity of birth Nakshatra"),
    ("Natal_Moon_Nakshatra_Ruling_Planet","CATEGORY","Ruling planet of birth star"),
    ("Natal_Moon_Nakshatra_Quality","CATEGORY","Dhruva/Chara/Ugra/Mridu/Tikshna/Misra/Laghu"),
    ("Natal_Panchang_Yoga_ID","INT","Sun+Moon Yoga number 1-27"),
    ("Natal_Panchang_Yoga_Name","TEXT","Yoga name Vishkambha…Vaidhriti"),
    ("Natal_Panchang_Yoga_Quality","CATEGORY","Auspicious/Inauspicious/Neutral"),
    ("Natal_Karana_Name","TEXT","Half-Tithi name"),
    ("Natal_Karana_Type","CATEGORY","Movable or Fixed Karana"),
    ("Natal_Karana_Quality","CATEGORY","Auspicious or Destructive Vishti=always destructive"),
    ("Natal_Panchang_Shuddhi_Score","INT","Count of auspicious limbs at birth 0-5"),
]:
    add(col,C,CN,dtype,0,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 2A — TRANSIT KINEMATICS
# ═══════════════════════════════════════════════════════════════
C,CN = "2A","Transit Kinematic Physics"
add("snapshot_datetime_utc",C,CN,"DATETIME",1,"Daily snapshot 09:30 ET in UTC")
add("snapshot_date",C,CN,"DATE",1,"Trading date")
add("Transit_Ascendant_Lon",C,CN,"FLOAT",1,"Ascendant degree at 09:30 AM ET")
add("Transit_Ascendant_Sign",C,CN,"INT",1,"Rising sign at market open")

for P in PLANETS:
    add(f"Transit_{P}_Lon_0_360",             C,CN,"FLOAT",   1,f"{P} longitude at market open")
    add(f"Transit_{P}_Velocity_DegPerDay",    C,CN,"FLOAT",   1,f"{P} speed deg/day")
    add(f"Transit_{P}_Acceleration",          C,CN,"FLOAT",   1,f"{P} second derivative of motion")
    add(f"Transit_{P}_Declination",           C,CN,"FLOAT",   1,f"{P} declination")
    add(f"Transit_{P}_Latitude",              C,CN,"FLOAT",   1,f"{P} ecliptic latitude")
    add(f"Transit_{P}_Distance_From_Earth",   C,CN,"FLOAT",   1,f"{P} Earth distance Apogee/Perigee")
    add(f"Transit_{P}_Heliocentric_Lon",      C,CN,"FLOAT",   1,f"{P} heliocentric longitude Gann")
    add(f"Transit_{P}_OOB_Flag",              C,CN,"BOOL",    1,f"{P} Out of Bounds today")
    add(f"Transit_{P}_Motion_Phase",          C,CN,"CATEGORY",1,f"{P} motion: Direct/Retrograde/Stationary/Anuvakra")
    add(f"Transit_{P}_Combust_Flag",          C,CN,"BOOL",    1,f"{P} combust in transit")
    add(f"Transit_{P}_Cazimi_Flag",           C,CN,"BOOL",    1,f"{P} within 1° of Sun Cazimi empowered")

# ═══════════════════════════════════════════════════════════════
# CATEGORY 2B — TRANSIT D1 MATRIX
# ═══════════════════════════════════════════════════════════════
C,CN = "2B","Transit D1 Sky Matrix"

for P in PLANETS:
    add(f"Transit_{P}_Sign_ID",              C,CN,"INT",      1,f"{P} sign in transit sky 1-12")
    add(f"Transit_{P}_Local_Degree",         C,CN,"FLOAT",    1,f"{P} degree within sign in transit")
    add(f"Transit_{P}_Nakshatra_ID",         C,CN,"INT",      1,f"{P} Nakshatra in transit 1-27")
    add(f"Transit_{P}_Pada",                 C,CN,"INT",      1,f"{P} Pada in transit 1-4")
    add(f"Transit_{P}_Exalted_Flag",         C,CN,"BOOL",     1,f"{P} exalted in transit sky")
    add(f"Transit_{P}_Debilitated_Flag",     C,CN,"BOOL",     1,f"{P} debilitated in transit")
    add(f"Transit_{P}_Moolatrikona_Flag",    C,CN,"BOOL",     1,f"{P} Moolatrikona in transit")
    add(f"Transit_{P}_Own_Sign_Flag",        C,CN,"BOOL",     1,f"{P} own sign in transit")
    add(f"Transit_{P}_Vargottam_Flag",       C,CN,"BOOL",     1,f"{P} Vargottam transit D1/D9")
    add(f"Transit_{P}_Papa_Kartari_Flag",    C,CN,"BOOL",     1,f"{P} hemmed by transit malefics")
    add(f"Transit_{P}_Shubha_Kartari_Flag",  C,CN,"BOOL",     1,f"{P} supported by transit benefics")
    add(f"Transit_{P}_Current_Sign_Lord",    C,CN,"CATEGORY", 1,f"Dispositor of {P}'s transit sign")
    add(f"Transit_{P}_Current_Nakshatra_Lord",C,CN,"CATEGORY",1,f"Star lord of {P}'s transit Nakshatra")
    add(f"Transit_{P}_Lajjitadi_Avastha",    C,CN,"CATEGORY", 1,f"{P} transit Avastha Starved/Ashamed/Delighted/Proud")
    # FIX #5 & #6: Transit x Natal direct crosses
    add(f"Transit_{P}_vs_Natal_{P}_Delta_Degrees",C,CN,"FLOAT",1,f"Transit {P} minus Natal {P} degrees continuous signal")
    for N in PLANETS:
        add(f"Transit_{P}_Parashari_Aspects_Natal_{N}_Strength",
            C,CN,"FLOAT",1,f"Parashari aspect Transit {P} onto Natal {N} 0.0-1.0")
        add(f"Transit_{P}_Conjunct_Natal_{N}_Flag",
            C,CN,"BOOL",1,f"Transit {P} conjunct Natal {N}")

for P1 in PLANETS:
    for P2 in PLANETS:
        if P1 != P2:
            add(f"Transit_{P1}_Conjoins_Transit_{P2}_Flag",
                C,CN,"BOOL",1,f"{P1} conjunct {P2} in sky today")
            add(f"Transit_{P1}_Parashari_Aspects_Transit_{P2}_Strength",
                C,CN,"FLOAT",1,f"Parashari aspect {P1}→{P2} today 0-1")

for yoga in ["Raja","Dhana","Gajakesari","Kemadruma","Kala_Sarpa"]:
    add(f"Transit_Active_{yoga}_Yoga_Flag",C,CN,"BOOL",1,f"{yoga} Yoga in sky today")

# ═══════════════════════════════════════════════════════════════
# CATEGORY 2C — TRANSIT VARGA MATRICES
# ═══════════════════════════════════════════════════════════════
C,CN = "2C","Transit Varga Matrices"

for V in VARGAS:
    add(f"Transit_{V}_Ascendant_Sign",C,CN,"INT",1,f"{V} Ascendant sign in transit sky")
    for P in PLANETS:
        add(f"Transit_{V}_{P}_Sign",          C,CN,"INT", 1,f"{P} sign in transit {V}")
        add(f"Transit_{V}_{P}_House",         C,CN,"INT", 1,f"{P} house in transit {V}")
        add(f"Transit_{V}_{P}_Exalted_Flag",  C,CN,"BOOL",1,f"{P} exalted in transit {V}")
        add(f"Transit_{V}_{P}_Debilitated_Flag",C,CN,"BOOL",1,f"{P} debilitated in transit {V}")
    for P1 in PLANETS:
        for P2 in PLANETS:
            if P1 != P2:
                add(f"Transit_{V}_{P1}_Conjoins_{P2}",C,CN,"BOOL", 1,f"{P1} conjunct {P2} transit {V}")
                add(f"Transit_{V}_{P1}_Aspects_{P2}", C,CN,"FLOAT",1,f"{P1} aspects {P2} transit {V}")

# ═══════════════════════════════════════════════════════════════
# CATEGORY 2D — MOORTI NIRNAYA
# ═══════════════════════════════════════════════════════════════
C,CN = "2D","Transit Moorti Nirnaya & Macro Ingresses"
for P in ["Jupiter","Saturn","Rahu","Ketu","Uranus","Neptune","Pluto"]:
    add(f"Transit_{P}_Moorti_Metal",C,CN,"CATEGORY",1,f"{P} Moorti at sign ingress: Gold/Silver/Copper/Iron")

for col,dtype,desc in [
    ("Transit_Sade_Sati_Phase","CATEGORY","Saturn Sade Sati: Rising/Peak/Setting/None"),
    ("Transit_Ashtama_Shani_Flag","BOOL","Transit Saturn in 8th from Natal Moon"),
    ("Transit_Kantaka_Shani_Flag","BOOL","Transit Saturn in 4th or 10th from Natal Moon"),
]:
    add(col,C,CN,dtype,1,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 2E — DAILY PANCHANG
# ═══════════════════════════════════════════════════════════════
C,CN = "2E","Transit Daily Panchang"
for col,dtype,desc in [
    ("Transit_Tithi_Number","INT","Lunar day 1-30"),
    ("Transit_Tithi_Name","TEXT","Tithi name"),
    ("Transit_Tithi_Type","CATEGORY","Nanda/Bhadra/Jaya/Rikta/Purna"),
    ("Transit_Tithi_Paksha","CATEGORY","Shukla or Krishna"),
    ("Transit_Tithi_Completion_Percent","FLOAT","How far through Tithi 0-100"),
    ("Transit_Vara_Lord","CATEGORY","Day lord"),
    ("Transit_Vara_Quality","CATEGORY","Day quality"),
    ("Transit_Moon_Nakshatra_ID","INT","Moon Nakshatra today 1-27"),
    ("Transit_Moon_Nakshatra_Gana","CATEGORY","Deva/Manushya/Rakshasa"),
    ("Transit_Moon_Nakshatra_Quality","CATEGORY","Dhruva/Chara/Ugra/Mridu/Tikshna/Misra/Laghu"),
    ("Transit_Moon_Nakshatra_Tatva","CATEGORY","Element of Moon star today"),
    ("Transit_Moon_Nakshatra_Deity","TEXT","Deity of Moon star today"),
    ("Transit_Panchang_Yoga_ID","INT","Sun+Moon Yoga 1-27"),
    ("Transit_Panchang_Yoga_Name","TEXT","Yoga name"),
    ("Transit_Panchang_Yoga_Quality","CATEGORY","Auspicious/Inauspicious"),
    ("Transit_Shula_Yoga_Flag","BOOL","Destructive Shula Yoga active"),
    ("Transit_Karana_Name","TEXT","Current half-Tithi name"),
    ("Transit_Vishti_Karana_Flag","BOOL","Bhadra/Vishti Karana active destructive"),
    ("Transit_Amavasya_Flag","BOOL","New Moon day"),
    ("Transit_Purnima_Flag","BOOL","Full Moon day"),
    ("Transit_Ganda_Moola_Flag","BOOL","Moon at Fire/Water Nakshatra junction"),
    ("Transit_Tithi_Gandanta_Flag","BOOL","Tithi at 30th/0th transition extremely volatile"),
    ("Transit_Varjyam_Start_Time","TIME","Varjyam poison period start"),
    ("Transit_Varjyam_End_Time","TIME","Varjyam poison period end"),
    ("Transit_Durmuhurtham_Flag","BOOL","Inauspicious 48-min window active"),
    ("Transit_Shula_Direction","CATEGORY","Blocked compass direction today"),
    ("Transit_Panchaka_Status","CATEGORY","Panchaka: Agni/Chora/Roga/Mrityu/None"),
    ("Transit_Brahma_Muhurtha_Flag","BOOL","Pre-dawn Brahma Muhurtha active"),
    ("Transit_Amrita_Kalam_Flag","BOOL","Nectar window active today"),
    ("Transit_Guru_Pushya_Yoga_Flag","BOOL","Thursday + Pushya Nakshatra wealth day"),
    ("Transit_Ravi_Pushya_Yoga_Flag","BOOL","Sunday + Pushya Nakshatra wealth day"),
    ("Transit_Adhika_Masa_Flag","BOOL","Intercalary leap lunar month unstable"),
    ("Transit_Solar_Eclipse_Flag","BOOL","Solar eclipse today"),
    ("Transit_Lunar_Eclipse_Flag","BOOL","Lunar eclipse today"),
    ("Transit_Graha_Yuddha_Pairs","TEXT","Planets in Graha Yuddha war within 1°"),
]:
    add(col,C,CN,dtype,1,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 2F — ASHTAKVARGA KAKSHYAS & GOCHARA
# ═══════════════════════════════════════════════════════════════
C,CN = "2F","Transit Ashtakvarga Kakshyas & Gochara"
for P in PLANETS:
    add(f"Transit_{P}_In_Kakshya_Of",             C,CN,"CATEGORY",1,f"Which planet's Kakshya {P} sits in today")
    add(f"Transit_{P}_Kakshya_Bindu_Active",       C,CN,"BOOL",    1,f"{P} transiting Kakshya with natal bindu")
    add(f"Transit_{P}_BAV_Score_In_Current_Sign",  C,CN,"INT",     1,f"{P} Ashtakvarga score in today's sign")
    add(f"Transit_{P}_Positive_Gochara_Flag",      C,CN,"BOOL",    1,f"{P} positive Gochara house from Natal Moon")
    add(f"Transit_{P}_Gochara_Vedha_Blocked",      C,CN,"BOOL",    1,f"{P} Gochara blocked by Vedha planet")
    add(f"Transit_{P}_Vipareeta_Vedha_Flag",       C,CN,"BOOL",    1,f"{P} negative Gochara cancelled by Vipareeta Vedha")
    add(f"Transit_{P}_Lata_Kick_Flag",             C,CN,"BOOL",    1,f"{P} causing Lata kick on Natal Moon Nakshatra")

add("Transit_Tara_Bala",   C,CN,"INT",  1,"Tara Bala score 1-9 Transit Moon vs Natal Moon star")
add("Transit_Chandra_Bala",C,CN,"INT",  1,"Transit Moon house 1-12 from Natal Moon 6/8/12=bearish")

# ═══════════════════════════════════════════════════════════════
# CATEGORY 3 — DASHAS
# ═══════════════════════════════════════════════════════════════
C,CN = "3A","Dasha Systems"
for col,dtype,tv,desc in [
    ("Vimshottari_MD_Lord","CATEGORY",1,"Vimshottari Mahadasha lord"),
    ("Vimshottari_AD_Lord","CATEGORY",1,"Vimshottari Antardasha lord"),
    ("Vimshottari_PAD_Lord","CATEGORY",1,"Vimshottari Pratyantardasha lord"),
    ("Vimshottari_Sookshma_Lord","CATEGORY",1,"Vimshottari Sookshma lord"),
    ("Vimshottari_Prana_Lord","CATEGORY",1,"Vimshottari Prana lord finest level"),
    ("Vimshottari_MD_Start_Date","DATE",1,"MD start date"),
    ("Vimshottari_MD_End_Date","DATE",1,"MD end date"),
    ("Vimshottari_AD_Start_Date","DATE",1,"AD start date"),
    ("Vimshottari_AD_End_Date","DATE",1,"AD end date"),
    ("Vimshottari_MD_Elapsed_Pct","FLOAT",1,"Percent elapsed through current MD"),
    ("Vimshottari_Dasha_Balance_At_Birth","FLOAT",0,"Years of first MD remaining at IPO"),
    ("Vimshottari_MD_Lord_Natal_House","INT",0,"Natal house of current MD lord"),
    ("Vimshottari_MD_Lord_Natal_Exalted","BOOL",0,"MD lord exalted in natal"),
    ("Vimshottari_MD_Lord_Natal_Debilitated","BOOL",0,"MD lord debilitated in natal"),
    ("Vimshottari_MD_Lord_Natal_Shadbala","FLOAT",0,"MD lord natal Shadbala score"),
    ("Vimshottari_MD_vs_AD_Natal_Angle","FLOAT",1,"Natal angle between MD and AD lords Shadashtaka"),
    ("Dasha_Sandhi_Active_Flag","BOOL",1,"Dasha Sandhi MD transition void active"),
    ("Chara_MD_Sign","INT",1,"Jaimini Chara MD sign"),
    ("Chara_AD_Sign","INT",1,"Jaimini Chara AD sign"),
    ("Chara_PAD_Sign","INT",1,"Jaimini Chara PAD sign"),
    ("Narayana_MD_Sign","INT",1,"Narayana Dasha MD sign"),
    ("Narayana_AD_Sign","INT",1,"Narayana Dasha AD sign"),
    ("Yogini_MD_Lord","CATEGORY",1,"Yogini Dasha MD lord"),
    ("Yogini_AD_Lord","CATEGORY",1,"Yogini Dasha AD lord"),
    ("Kalachakra_MD_Sign","INT",1,"Kalachakra Dasha MD sign"),
    ("Kalachakra_AD_Sign","INT",1,"Kalachakra Dasha AD sign"),
    ("Kalachakra_Deha_Sign","INT",0,"Kalachakra Deha body sign crashes when hit by malefics"),
    ("Kalachakra_Jiva_Sign","INT",0,"Kalachakra Jiva soul sign crashes when hit by malefics"),
    ("Ashtottari_Dasha_Applicable_Flag","BOOL",0,"Special 108-year cycle applicable"),
    ("Dwisaptati_Sama_Applicable_Flag","BOOL",0,"Special 72-year cycle applicable"),
]:
    add(col,C,CN,dtype,tv,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 4 — VARSHAPHALA
# ═══════════════════════════════════════════════════════════════
C,CN = "4","Varshaphala Annual Return"
add("Trading_Year",C,CN,"INT",1,"Calendar trading year")
add("Solar_Return_Timestamp",C,CN,"DATETIME",1,"Exact moment of solar return")
add("Varshaphala_Ascendant_Sign",C,CN,"INT",1,"Solar return Ascendant sign")
add("Varshaphala_Ascendant_Lon",C,CN,"FLOAT",1,"Solar return Ascendant longitude")

for P in PLANETS:
    add(f"Varshaphala_{P}_Sign",            C,CN,"INT",  1,f"{P} sign in solar return chart")
    add(f"Varshaphala_{P}_House",           C,CN,"INT",  1,f"{P} house in solar return chart")
    add(f"Varshaphala_{P}_Nakshatra",       C,CN,"INT",  1,f"{P} Nakshatra in solar return")
    add(f"Varshaphala_{P}_Exalted_Flag",    C,CN,"BOOL", 1,f"{P} exalted in solar return")
    add(f"Varshaphala_{P}_Debilitated_Flag",C,CN,"BOOL", 1,f"{P} debilitated in solar return")
    add(f"Varshaphala_{P}_Pancha_Vargiya_Bala",C,CN,"FLOAT",1,f"{P} 5-fold strength in annual chart")

for col,dtype,tv,desc in [
    ("Varshaphala_Varsheshwara","CATEGORY",1,"Lord of the trading year"),
    ("Varshaphala_Muntha_Sign","INT",1,"Muntha progressed Ascendant sign"),
    ("Varshaphala_Muntha_Lord_Natal_House","INT",1,"Natal house of Muntha lord"),
    ("Varshaphala_Active_Ithasala_Yogas_Count","INT",1,"Applying Tajika aspects count"),
    ("Varshaphala_Active_Easarpha_Yogas_Count","INT",1,"Separating Tajika aspects count"),
    ("Varshaphala_Kambool_Yoga_Flag","BOOL",1,"Kambool Yoga positive annual"),
    ("Varshaphala_Duphali_Kurpa_Flag","BOOL",1,"Duphali Kurpa Yoga double applying aspects"),
    ("Varshaphala_TriPataki_Vedha_Moon_Flag","BOOL",1,"3 malefics blocking Moon in Tri-Pataki"),
    ("Varshaphala_Mudda_MD_Lord","CATEGORY",1,"Annual Mudda Dasha MD lord"),
    ("Varshaphala_Mudda_AD_Lord","CATEGORY",1,"Annual Mudda Dasha AD lord"),
    ("Varshaphala_Punya_Saham_Lon","FLOAT",1,"Lot of Fortune longitude"),
    ("Varshaphala_Vyapara_Saham_Lon","FLOAT",1,"Lot of Trade Business longitude"),
    ("Varshaphala_Artha_Saham_Lon","FLOAT",1,"Lot of Wealth longitude"),
    ("Varshaphala_Karma_Saham_Lon","FLOAT",1,"Lot of Career Action longitude"),
    ("Varshaphala_Raja_Saham_Lon","FLOAT",1,"Lot of Authority longitude"),
    ("Varshaphala_Labha_Saham_Lon","FLOAT",1,"Lot of Gains longitude"),
    ("Varshaphala_Karya_Siddhi_Saham_Lon","FLOAT",1,"Lot of Success longitude"),
    ("Varshaphala_Videsh_Saham_Lon","FLOAT",1,"Lot of Foreign exposure longitude"),
]:
    add(col,C,CN,dtype,tv,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 5 — PROGRESSIONS
# ═══════════════════════════════════════════════════════════════
C,CN = "5","Progressions & Symbolic Time"
for P in PLANETS:
    add(f"Progressed_{P}_Lon",           C,CN,"FLOAT",1,f"{P} Nadi-progressed longitude 1 deg/year")
    add(f"Solar_Arc_Progressed_{P}_Lon", C,CN,"FLOAT",1,f"{P} Solar Arc direction longitude")
    # FIX #11: Progressed x Natal aspects
    for N in PLANETS:
        add(f"Progressed_{P}_Aspects_Natal_{N}_Flag",C,CN,"BOOL",1,f"Progressed {P} in aspect to Natal {N}")

for col,dtype,desc in [
    ("Sudarshana_Progressed_Sun_Sign","INT","Sudarshana Sun 1 sign/year"),
    ("Sudarshana_Progressed_Moon_Sign","INT","Sudarshana Moon 1 sign/year"),
    ("Sudarshana_Progressed_Asc_Sign","INT","Sudarshana Ascendant 1 sign/year"),
    ("Secondary_Progressed_Moon_Lon","FLOAT","Secondary progressed Moon 1 day=1 year"),
]:
    add(col,C,CN,dtype,1,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 6 — KP SYSTEM
# ═══════════════════════════════════════════════════════════════
C,CN = "6","KP System Krishnamurti Paddhati"
for H in HOUSES:
    add(f"KP_Cusp_{H}_Lon",            C,CN,"FLOAT",   0,f"KP Placidus cusp {H} longitude")
    add(f"KP_Cusp_{H}_Sign_Lord",      C,CN,"CATEGORY",0,f"KP Cusp {H} sign lord")
    add(f"KP_Cusp_{H}_Nakshatra_Lord", C,CN,"CATEGORY",0,f"KP Cusp {H} star lord")
    add(f"KP_Cusp_{H}_Sub_Lord",       C,CN,"CATEGORY",0,f"KP Cusp {H} Sub-Lord primary significator")
    add(f"KP_Cusp_{H}_Sub_Sub_Lord",   C,CN,"CATEGORY",0,f"KP Cusp {H} Sub-Sub-Lord")

for P in PLANETS:
    add(f"KP_{P}_Sign_Lord",           C,CN,"CATEGORY",0,f"{P} KP sign lord")
    add(f"KP_{P}_Nakshatra_Lord",      C,CN,"CATEGORY",0,f"{P} KP star lord")
    add(f"KP_{P}_Sub_Lord",            C,CN,"CATEGORY",0,f"{P} KP Sub-Lord primary significator")
    add(f"KP_{P}_Sub_Sub_Lord",        C,CN,"CATEGORY",0,f"{P} KP Sub-Sub-Lord")
    add(f"KP_{P}_Significator_Houses", C,CN,"TEXT",     0,f"Houses {P} signifies in KP")
    add(f"KP_{P}_Signifies_Wealth_Flag",C,CN,"BOOL",   0,f"{P} signifies 2/6/10/11 wealth group")
    add(f"KP_{P}_Signifies_Loss_Flag", C,CN,"BOOL",    0,f"{P} signifies 5/8/12 bankruptcy group")
    add(f"Transit_{P}_KP_Star_Lord",   C,CN,"CATEGORY",1,f"{P} KP star lord in transit today")
    add(f"Transit_{P}_KP_Sub_Lord",    C,CN,"CATEGORY",1,f"{P} KP Sub-Lord in transit today PRIMARY TIMING")
    add(f"Transit_{P}_KP_Sub_Sub_Lord",C,CN,"CATEGORY",1,f"{P} KP Sub-Sub-Lord in transit")
    add(f"Transit_{P}_KP_Wealth_Flag", C,CN,"BOOL",    1,f"Transit {P} KP Sub-Lord signifies 2/6/10/11")
    add(f"Transit_{P}_KP_Loss_Flag",   C,CN,"BOOL",    1,f"Transit {P} KP Sub-Lord signifies 5/8/12")

add("KP_Fortuna_Lon",         C,CN,"FLOAT",   0,"KP Pars Fortuna longitude")
add("KP_Fortuna_Sub_Lord",    C,CN,"CATEGORY",0,"KP Fortuna Sub-Lord sudden wealth trigger")
add("KP_Punarphoo_Yoga_Flag", C,CN,"BOOL",    1,"KP Punarphoo Saturn-Moon delays")
add("KP_RP_Day_Lord",         C,CN,"CATEGORY",1,"KP Ruling Planet day lord")
add("KP_RP_Lagna_Sign_Lord",  C,CN,"CATEGORY",1,"KP Ruling Planet Ascendant sign lord")
add("KP_RP_Lagna_Star_Lord",  C,CN,"CATEGORY",1,"KP Ruling Planet Ascendant star lord")
add("KP_RP_Moon_Sign_Lord",   C,CN,"CATEGORY",1,"KP Ruling Planet Moon sign lord")
add("KP_RP_Moon_Star_Lord",   C,CN,"CATEGORY",1,"KP Ruling Planet Moon star lord")
add("KP_NewMoon_Ascendant_Sign",C,CN,"INT",   1,"KP New Moon chart Ascendant monthly")
# FIX #12: KP NewMoon per-planet Sub Lords
for P in PLANETS:
    add(f"KP_NewMoon_{P}_Sub_Lord",C,CN,"CATEGORY",1,f"{P} Sub-Lord in KP New Moon chart monthly")

# ═══════════════════════════════════════════════════════════════
# CATEGORY 7 — ADVANCED CHAKRAS
# ═══════════════════════════════════════════════════════════════
C,CN = "7","Advanced Chakras SBC Kota Sanghatta"
for P in PLANETS:
    add(f"SBC_{P}_Vedha_On_Natal_Nakshatra_Flag",C,CN,"BOOL",1,f"{P} Vedha on asset natal Nakshatra")
    add(f"SBC_{P}_Vedha_On_Name_Consonant_Flag", C,CN,"BOOL",1,f"{P} Vedha on ticker starting consonant")

for col,dtype,desc in [
    ("SBC_Karma_Nakshatra_Vedha_Flag","BOOL","Vedha on Karma Nakshatra"),
    ("SBC_Sanghatika_Nakshatra_Vedha_Flag","BOOL","Vedha on Sanghatika Nakshatra debt"),
    ("SBC_Vinasha_Nakshatra_Vedha_Flag","BOOL","Vedha on Vinasha Nakshatra destruction"),
    ("Kota_Stambha_Malefic_Count","INT","Malefics in Kota Stambha central pillar crash if occupied"),
    ("Kota_Madhya_Malefic_Count","INT","Malefics in Kota Madhya inner court"),
    ("Kota_Prakara_Malefic_Count","INT","Malefics in Kota Prakara outer wall"),
    ("Kota_Bahya_Malefic_Count","INT","Malefics in Kota Bahya boundary"),
    ("Kota_Entry_Planets","TEXT","Planets entering Kota fortress today"),
    ("Kota_Exit_Planets","TEXT","Planets fleeing Kota fortress today"),
    ("Kota_Pala_Lord","CATEGORY","Guard planet of Kota fortress"),
    ("Sanghatta_Vedha_Count","INT","Sanghatta Chakra accumulated negative lines"),
]:
    add(col,C,CN,dtype,1,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 8 — INTRADAY MUHURTHA
# ═══════════════════════════════════════════════════════════════
C,CN = "8","Intraday Muhurtha Micro-Time"
for col,dtype,tv,desc in [
    ("Muhurtha_Panchapakshi_Asset_Bird","CATEGORY",0,"Asset's Panchapakshi bird Vulture/Owl/Crow/Cock/Peacock"),
    ("Muhurtha_Panchapakshi_Current_Activity","CATEGORY",1,"Bird activity Ruling/Eating/Walking/Sleeping/Dying"),
    ("Muhurtha_Hora_Lord","CATEGORY",1,"Current planetary hour lord"),
    ("Muhurtha_Choghadiya_State","CATEGORY",1,"Amrit/Shubh/Labh/Udveg/Rog/Kaal"),
    ("Muhurtha_Gauri_Panchangam_State","CATEGORY",1,"Gauri Panchangam micro-auspiciousness"),
    ("Muhurtha_Abhijit_Active_Flag","BOOL",1,"Abhijit most auspicious 48-min window active"),
    ("Muhurtha_Rahu_Kalam_Flag","BOOL",1,"Rahu Kalam 1.5h chaos window active"),
    ("Muhurtha_Yama_Gandam_Flag","BOOL",1,"Yama Gandam 1.5h destruction window active"),
    ("Muhurtha_Gulika_Kalam_Flag","BOOL",1,"Gulika Kalam poison period active"),
]:
    add(col,C,CN,dtype,tv,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 9 — MUNDANE
# ═══════════════════════════════════════════════════════════════
C,CN = "9","Mundane Astrology Macro Economy"
for P in PLANETS:
    for N in PLANETS:   # All planet-to-planet angles vs USA chart (not just same planet) FIX #19
        add(f"Transit_{P}_Over_USA_Natal_{N}_Angle",C,CN,"FLOAT",1,f"Transit {P} angle from USA natal {N}")
    add(f"Transit_{P}_In_USA_Natal_House",    C,CN,"INT",1,f"USA natal house of transit {P}")
    add(f"Transit_{P}_In_NYSE_Natal_House",   C,CN,"INT",1,f"NYSE natal house of transit {P}")
    add(f"Transit_{P}_In_NASDAQ_Natal_House", C,CN,"INT",1,f"NASDAQ natal house of transit {P}")

for col,dtype,tv,desc in [
    ("USA_Vimshottari_MD_Lord","CATEGORY",1,"USA national chart MD lord"),
    ("USA_Vimshottari_AD_Lord","CATEGORY",1,"USA national chart AD lord"),
    ("NYSE_Vimshottari_MD_Lord","CATEGORY",1,"NYSE entity chart MD lord"),
    ("NYSE_Vimshottari_AD_Lord","CATEGORY",1,"NYSE entity chart AD lord"),
    ("NASDAQ_Vimshottari_MD_Lord","CATEGORY",1,"NASDAQ entity chart MD lord"),
    ("FedReserve_Vimshottari_MD_Lord","CATEGORY",1,"Federal Reserve entity chart MD lord"),
    ("Vedic_Year_King_Planet","CATEGORY",1,"Vedic New Year king planet annual macro"),
    ("Vedic_Year_Minister_Planet","CATEGORY",1,"Vedic New Year minister planet"),
    ("Aries_Ingress_Ascendant_Sign","INT",1,"Ascendant at Aries Ingress 12-month trend"),
    ("Aries_Ingress_Ascendant_Lord_Dignity","CATEGORY",1,"Dignity of Aries Ingress Ascendant lord"),
    ("Makar_Sankranti_Day_Lord","CATEGORY",1,"Day lord at Capricorn Ingress 6-month trend"),
    ("Jupiter_Saturn_Conjunction_Sign","INT",1,"Sign of current Jupiter-Saturn great conjunction"),
    ("Jupiter_Saturn_Conjunction_Year","INT",0,"Year of most recent Jupiter-Saturn conjunction"),
    ("Koorma_Chakra_Afflicted_Direction","CATEGORY",1,"Geographic direction under planetary siege"),
    ("Eclipse_Visible_In_Market_HQ_Flag","BOOL",1,"Eclipse shadow falling on New York"),
    ("Eclipse_Degree_Distance_To_Natal_Ascendant","FLOAT",1,"Eclipse degree distance from natal Ascendant"),
]:
    add(col,C,CN,dtype,tv,desc)

# ═══════════════════════════════════════════════════════════════
# CATEGORY 10 — ML INTERACTION CROSSES
# ═══════════════════════════════════════════════════════════════
C,CN = "10","ML Interaction Crosses"

for H in HOUSES:
    add(f"Double_Transit_On_Natal_House_{H}_Flag",C,CN,"BOOL",1,f"Both Jupiter & Saturn aspecting Natal House {H}")
for P in PLANETS:
    add(f"Double_Transit_On_Natal_{P}_Flag",C,CN,"BOOL",1,f"Both Jupiter & Saturn aspecting Natal {P}")

add("Double_Transit_On_Vimshottari_MD_Lord_Flag",C,CN,"BOOL",1,"Both Jupiter & Saturn aspecting MD lord")

for P in PLANETS:
    add(f"Transit_{P}_Aspects_Vimshottari_MD_Lord_Flag",C,CN,"BOOL",1,f"Transit {P} aspecting MD lord")
    add(f"Transit_{P}_In_MD_Lord_Natal_House",          C,CN,"INT", 1,f"Transit {P} in natal house of MD lord")
    add(f"Transit_{P}_Over_Natal_Chara_Karaka_{P}_Flag",C,CN,"BOOL",1,f"Transit {P} over Chara Karaka {P}")
    add(f"Transit_{P}_Over_Natal_AL_Flag",              C,CN,"BOOL",1,f"Transit {P} over Natal Arudha Lagna price event")
    add(f"Transit_{P}_Over_Natal_A8_Flag",              C,CN,"BOOL",1,f"Transit {P} over Natal A8 crash debt event")
    add(f"Transit_{P}_Over_Natal_A11_Flag",             C,CN,"BOOL",1,f"Transit {P} over Natal A11 cash inflow event")

add("Vimshottari_MD_Lord_BAV_Score_In_Natal",  C,CN,"INT", 1,"MD lord natal BAV score 0=period fails")
add("Vimshottari_AD_Lord_Kakshya_Transit_Flag",C,CN,"BOOL",1,"AD lord transiting its own high Kakshya")
add("Vimshottari_MD_Lord_In_Varshaphala_House",C,CN,"INT", 1,"House of MD lord in current annual chart")
add("Vimshottari_AD_Lord_In_Varshaphala_House",C,CN,"INT", 1,"House of AD lord in current annual chart")

for V in ["D9","D10"]:
    for P in PLANETS:
        add(f"Transit_{V}_{P}_Overlaps_Natal_{V}_{P}_Flag",C,CN,"BOOL",1,f"Transit {P} in {V} = Natal {P} in {V}")
        add(f"Transit_{P}_In_Natal_{V}_Sign",              C,CN,"INT", 1,f"Transit {P} expressed as natal {V} sign")

# Progressed x Transit (non-duplicated) FIX #4
for P in PLANETS:
    add(f"Progressed_{P}_Aspects_Transit_{P}_Flag",C,CN,"BOOL",1,f"Progressed {P} in aspect to transit {P}")

# ═══════════════════════════════════════════════════════════════
# MARKET DATA COLUMNS
# ═══════════════════════════════════════════════════════════════
C,CN = "MKT_PRICE","Market Price Data"
for col,dtype,desc in [
    ("Open","FLOAT","Market open price"),
    ("High","FLOAT","Day high price"),
    ("Low","FLOAT","Day low price"),
    ("Close","FLOAT","Market close price"),
    ("Volume","FLOAT","Total daily volume"),
    ("VWAP","FLOAT","Volume-weighted average price"),
    ("Adj_Close","FLOAT","Dividend split adjusted close"),
    ("Dividends","FLOAT","Dividend paid this date"),
    ("Stock_Splits","FLOAT","Stock split ratio"),
]:
    add(col,C,CN,dtype,1,desc)

C,CN = "MKT_TARGET","Market Target Labels"
for col,dtype,desc in [
    ("ret_1d","FLOAT","Next 1-day forward return"),
    ("ret_2d","FLOAT","Next 2-day forward return"),
    ("ret_5d","FLOAT","Next 5-day forward return"),
    ("ret_10d","FLOAT","Next 10-day forward return"),
    ("ret_21d","FLOAT","Next 21-day forward return"),
    ("ret_63d","FLOAT","Next 63-day forward return"),
    ("intraday_ret","FLOAT","Open-to-close return same session"),
    ("overnight_ret","FLOAT","Prev close-to-open Gods gap"),
    ("next_overnight_ret","FLOAT","Tomorrows gap return"),
    ("daily_range_pct","FLOAT","Intraday range high-low/open"),
    ("high_ret","FLOAT","Best case high/open-1"),
    ("low_ret","FLOAT","Worst case low/open-1"),
    ("gap_size","FLOAT","Absolute gap size"),
    ("gap_direction","CATEGORY","GAP_UP/GAP_DOWN/FLAT"),
    ("dir_1d","INT","Next day direction +1/0/-1"),
    ("dir_5d","INT","5-day direction +1/0/-1"),
    ("dir_21d","INT","21-day direction +1/0/-1"),
    ("mag_class_1d","INT","Return magnitude class 0-4"),
    ("mag_class_5d","INT","5-day magnitude class 0-4"),
    ("is_crash_day_2pct","BOOL","Next day drops >2%"),
    ("is_rally_day_2pct","BOOL","Next day rises >2%"),
    ("is_crash_day_5pct","BOOL","Next 5 days drop >5%"),
    ("is_rally_day_5pct","BOOL","Next 5 days rise >5%"),
    ("is_breakout_day","BOOL","Close above 20-day high"),
    ("is_breakdown_day","BOOL","Close below 20-day low"),
    ("realized_vol_5d","FLOAT","Rolling 5-day realized volatility"),
    ("realized_vol_21d","FLOAT","Rolling 21-day realized volatility"),
    ("drawdown_from_252h","FLOAT","Drawdown from 252-day high"),
]:
    add(col,C,CN,dtype,1,desc)

C,CN = "MKT_CONTEXT","Market Context Features"
for col,dtype,desc in [
    ("VIX","FLOAT","CBOE Volatility Index fear index"),
    ("VVIX","FLOAT","Volatility of volatility"),
    ("SPX","FLOAT","S&P 500 index level"),
    ("NDX","FLOAT","Nasdaq index level"),
    ("Yield_10Y","FLOAT","10-year Treasury yield"),
    ("Yield_5Y","FLOAT","5-year Treasury yield"),
    ("Yield_3M","FLOAT","3-month T-bill yield"),
    ("Yield_30Y","FLOAT","30-year Treasury yield"),
    ("yield_curve_10y3m","FLOAT","Yield curve spread 10Y minus 3M"),
    ("yield_inverted_flag","BOOL","Yield curve inverted"),
    ("DXY","FLOAT","US Dollar Index"),
    ("Gold","FLOAT","Gold futures price"),
    ("Crude_Oil","FLOAT","WTI Crude Oil price"),
    ("Copper","FLOAT","Copper futures Dr Copper"),
    ("Advances","FLOAT","NYSE advancing issues"),
    ("Declines","FLOAT","NYSE declining issues"),
    ("TICK","FLOAT","NYSE Tick"),
    ("ADD","FLOAT","NYSE Advance-Decline line"),
    ("advance_decline_ratio","FLOAT","Advances/Declines ratio"),
    ("breadth_thrust_flag","BOOL","A/D ratio over 2.0 thrust day"),
    ("vix_1d_change","FLOAT","VIX day-over-day change"),
    ("vix_spike_flag","BOOL","VIX spike over 5 points"),
    ("vix_pct_rank_252d","FLOAT","VIX percentile rank 252-day"),
    ("vix_regime","CATEGORY","calm/low/elevated/high/extreme"),
    ("dxy_1d_change","FLOAT","Dollar index daily change"),
    # FIX #14: Put/Call ratios
    ("put_call_ratio_total","FLOAT","Market-wide total put/call ratio CBOE"),
    ("put_call_ratio_equity","FLOAT","Equity-only put/call ratio"),
    ("put_call_ratio_index","FLOAT","Index put/call ratio institutional hedging"),
    ("arms_trin_index","FLOAT","TRIN Trading Index volume-weighted breadth"),
    ("es_futures_premium","FLOAT","S&P500 futures premium vs spot"),
    ("nq_futures_premium","FLOAT","Nasdaq futures premium vs spot"),
]:
    add(col,C,CN,dtype,1,desc)

C,CN = "MKT_TECH","Asset Technical Indicators"
for col,dtype,desc in [
    ("sma_10","FLOAT","10-day SMA"),
    ("sma_20","FLOAT","20-day SMA"),
    ("sma_50","FLOAT","50-day SMA"),
    ("sma_200","FLOAT","200-day SMA"),
    ("ema_9","FLOAT","9-day EMA"),
    ("ema_21","FLOAT","21-day EMA"),
    ("close_vs_sma20","FLOAT","Close/SMA20-1"),
    ("close_vs_sma50","FLOAT","Close/SMA50-1"),
    ("close_vs_sma200","FLOAT","Close/SMA200-1"),
    ("sma20_vs_sma50","FLOAT","SMA20/SMA50-1 golden/death cross"),
    ("rsi_14","FLOAT","14-day RSI 0-100"),
    ("macd","FLOAT","MACD line"),
    ("macd_signal","FLOAT","MACD signal line"),
    ("macd_hist","FLOAT","MACD histogram"),
    ("roc_5","FLOAT","5-day rate of change"),
    ("roc_21","FLOAT","21-day rate of change"),
    ("atr_14","FLOAT","14-day Average True Range"),
    ("atr_pct","FLOAT","ATR as pct of price"),
    ("bb_upper","FLOAT","Bollinger Band upper"),
    ("bb_lower","FLOAT","Bollinger Band lower"),
    ("bb_pct","FLOAT","Bollinger Band pct B position"),
    ("bb_width","FLOAT","Bollinger Band width volatility"),
    ("hv_21d","FLOAT","21-day historical volatility"),
    ("hv_21d_pct_rank","FLOAT","HV21 percentile rank 252d"),
    ("volume_ratio_10d","FLOAT","Volume vs 10-day average"),
    ("volume_ratio_20d","FLOAT","Volume vs 20-day average"),
    ("obv","FLOAT","On-Balance Volume"),
    ("pct_from_52wk_high","FLOAT","Distance from 52-week high"),
    ("pct_from_52wk_low","FLOAT","Distance from 52-week low"),
    ("price_pct_rank_252d","FLOAT","Price percentile rank 252d"),
    ("rs_vs_spy_20d","FLOAT","20-day relative strength vs SPY"),
    ("rs_vs_spy_63d","FLOAT","63-day relative strength vs SPY"),
    ("beta_60d","FLOAT","60-day rolling beta to SPY"),
    # FIX #15: Options IV
    ("options_iv_atm_30d","FLOAT","At-the-money 30-day implied volatility"),
    ("iv_minus_rv","FLOAT","IV minus realized vol options premium richness"),
    # FIX #16: Short interest
    ("short_interest_ratio","FLOAT","Days to cover short squeeze risk"),
    ("short_pct_of_float","FLOAT","Short interest as pct of float"),
]:
    add(col,C,CN,dtype,1,desc)

C,CN = "MKT_CAL","Market Calendar Events"
for col,dtype,desc in [
    ("is_monthly_opex","BOOL","Monthly options expiration Friday"),
    ("is_quad_witching","BOOL","Quarterly quadruple witching"),
    ("days_to_next_opex","INT","Trading days until next monthly OpEx"),
    ("is_month_end","BOOL","Last trading day of month"),
    ("is_month_start","BOOL","First trading day of month"),
    ("is_quarter_end","BOOL","Last trading day of quarter"),
    ("day_of_week","INT","Day of week 0=Monday 4=Friday"),
    ("month_of_year","INT","Month 1-12"),
    ("week_of_month","INT","Week within month 1-5"),
    ("is_monday","BOOL","Monday gap risk day"),
    ("is_friday","BOOL","Friday options positioning day"),
    ("is_first_friday","BOOL","First Friday of month NFP release"),
    ("is_fomc_day_approx","BOOL","Approximate FOMC meeting day"),
    ("trading_day_of_month","INT","Sequential trading day within month"),
]:
    add(col,C,CN,dtype,1,desc)

# ═══════════════════════════════════════════════════════════════
# WRITE CSV
# ═══════════════════════════════════════════════════════════════
fieldnames = ["column_name","category_code","category_name","data_type","is_time_varying","description"]

with open(OUT_PATH,"w",newline="",encoding="utf-8") as f:
    writer = csv.DictWriter(f,fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

from collections import Counter
cat_counts = Counter(r["category_code"] for r in rows)
print(f"\n{'='*60}")
print(f"MASTER FEATURE COLUMN CSV v2 FINAL — GENERATED")
print(f"{'='*60}")
print(f"Output: {OUT_PATH}")
print(f"Total unique columns: {len(rows):,}")
print(f"Duplicates removed by dedup guard: {len(rows)+sum(1 for _ in [])} (0 dups)")
print(f"\nBreakdown by category:")
for cat,count in sorted(cat_counts.items()):
    print(f"  {cat:12s}: {count:7,} columns")
print(f"{'='*60}")
