"""
DEFINITIVE FORMULA INVESTIGATION
Reverse-engineer the CORRECT D9, D10, and Ashtakvarga formulas from Chrome Agent data.
We will test each planet one by one using the exact D1 degrees from Chrome.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ======================================================
# STEP 1: Reverse-engineer D9 (Navamsa) formula
# ======================================================
# CLASSIC VEDIC D9 FORMULA:
# Each sign = 9 navamsas of 3°20' each
# Starting navamsa sign depends on sign's element:
#   Fire (Aries=0, Leo=4, Sag=8)    → start Aries (0)
#   Earth (Taurus=1, Vir=5, Cap=9)  → start Capricorn (9)
#   Air (Gemini=2, Lib=6, Aq=10)    → start Libra (6)
#   Water (Cancer=3, Sc=7, Pi=11)   → start Cancer (3)

D9_STARTS = {0:0, 4:0, 8:0,   # Fire → Aries
             1:9, 5:9, 9:9,   # Earth → Capricorn
             2:6, 6:6, 10:6,  # Air → Libra
             3:3, 7:3, 11:3}  # Water → Cancer

def navamsa(lon):
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    nav_num = int(deg_in_sign / (30.0/9.0))  # 0 to 8
    start = D9_STARTS[sign_idx]
    return SIGNS[(start + nav_num) % 12]

def dasamsa(lon):
    """
    D10 FORMULA:
    Each sign = 10 parts of 3° each
    Odd signs (Aries=1, Gem=3, Leo=5, Lib=7, Sag=9, Aq=11): start from same sign
    Even signs (Tau=2, Can=4, Vir=6, Sc=8, Cap=10, Pi=12): start from 9th from sign
    Sign numbering: Aries=1 (odd), Taurus=2 (even)...
    Index:          Aries=0 (even index), Taurus=1 (odd index)...
    IMPORTANT: In Sanskrit, Aries is the 1st sign (ODD), Taurus is 2nd (EVEN)
    So odd signs by Sanskrit count = index 0,2,4,6,8,10 (Aries,Gem,Leo,Lib,Sag,Aq)
    Even signs = index 1,3,5,7,9,11 (Tau,Can,Vir,Sc,Cap,Pi)
    """
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    part = int(deg_in_sign / 3.0)  # 0 to 9
    if sign_idx % 2 == 0:  # Odd Sanskrit sign (Aries, Gem, Leo, Lib, Sag, Aq)
        return SIGNS[(sign_idx + part) % 12]
    else:  # Even Sanskrit sign (Tau, Can, Vir, Sc, Cap, Pi)
        return SIGNS[(sign_idx + 8 + part) % 12]

print("=" * 90)
print("STEP 1: D9 NAVAMSA FORMULA VERIFICATION")
print("=" * 90)

# Test with real planet degrees from Chrome JSON
test_planets_d9 = {
    # --- Sector ETFs Conception 1998-12-16 12:00 PM NY ---
    "XLK_Asc (Aquarius 29°26')": (10*30 + 29 + 26/60.0, "Aries"),
    "XLK_Sun (Sag 00°42')":      (8*30 + 0 + 42/60.0,   "Aries"),
    "XLK_Moon (Sco 05°45')":     (7*30 + 5 + 45/60.0,   "Leo"),
    "XLK_Mars (Vir 16°42')":     (5*30 + 16 + 42/60.0,  "Capricorn"),
    "XLK_Mercury (Sco 09°38')":  (7*30 + 9 + 38/60.0,   "Sagittarius"),
    "XLK_Jupiter (Aq 26°10')":   (10*30 + 26 + 10/60.0, "Taurus"),
    "XLK_Venus (Sag 12°22')":    (8*30 + 12 + 22/60.0,  "Cancer"),
    "XLK_Saturn (Ar 03°03')":    (0*30 + 3 + 3/60.0,    "Aries"),
    "XLK_Rahu (Leo 01°21')":     (4*30 + 1 + 21/60.0,   "Aries"),
    "XLK_Ketu (Aq 01°21')":      (10*30 + 1 + 21/60.0,  "Libra"),
    # --- SMH Conception 2000-12-18 12:00 PM NY ---
    "SMH_Asc (Pisces 03°42')":   (11*30 + 3 + 42/60.0,  "Leo"),
    "SMH_Sun (Sag 03°14')":      (8*30 + 3 + 14/60.0,   "Pisces"),
    "SMH_Moon (Vir 11°46')":     (5*30 + 11 + 46/60.0,  "Pisces"),
    "SMH_Mars (Lib 03°14')":     (6*30 + 3 + 14/60.0,   "Scorpio"),
    "SMH_Mercury (Sco 29°15')":  (7*30 + 29 + 15/60.0,  "Virgo"),
    "SMH_Jupiter (Tau 09°36')":  (1*30 + 9 + 36/60.0,   "Virgo"),
    "SMH_Venus (Cap 18°07')":    (9*30 + 18 + 7/60.0,   "Aries"),
    "SMH_Saturn (Tau 01°26')":   (1*30 + 1 + 26/60.0,   "Capricorn"),
    "SMH_Rahu (Gem 22°31')":     (2*30 + 22 + 31/60.0,  "Pisces"),
    "SMH_Ketu (Sag 22°31')":     (8*30 + 22 + 31/60.0,  "Scorpio"),
    # --- XLRE Conception 2015-10-06 ---
    "XLRE_Sun (Vir 19°00')":     (5*30 + 19 + 0/60.0,   "Pisces"),
    "XLRE_Moon (Can 09°46')":    (3*30 + 9 + 46/60.0,   "Scorpio"),
    "XLRE_Jupiter (Leo 17°54')":(4*30 + 17 + 54/60.0,  "Scorpio"),
    "XLRE_Rahu (Vir 06°05')":   (5*30 + 6 + 5/60.0,    "Gemini"),
    "XLRE_Ketu (Pis 06°05')":   (11*30 + 6 + 5/60.0,   "Sagittarius"),
    # --- XME Conception 2006-06-19 ---
    "XME_Sun (Gem 04°17')":      (2*30 + 4 + 17/60.0,   "Sagittarius"),
    "XME_Jupiter (Lib 15°28')":  (6*30 + 15 + 28/60.0,  "Libra"),
    "XME_Venus (Tau 00°54')":    (1*30 + 0 + 54/60.0,   "Libra"),
    "XME_Rahu (Pis 06°03')":     (11*30 + 6 + 3/60.0,   "Cancer"),
    "XME_Ketu (Vir 06°03')":     (5*30 + 6 + 3/60.0,    "Aries"),
}

print(f"\n  {'Planet':<35} {'Our Formula':>14} {'Chrome Truth':>14}  MATCH?")
print(f"  {'-'*75}")
d9_pass = d9_fail = 0
for label, (lon, chrome_truth) in test_planets_d9.items():
    our = navamsa(lon)
    match = "✅" if our == chrome_truth else "❌"
    if our == chrome_truth: d9_pass += 1
    else: d9_fail += 1
    print(f"  {label:<35} {our:>14} {chrome_truth:>14}  {match}")
print(f"\n  D9 Result: {d9_pass} PASS / {d9_fail} FAIL")

print("\n" + "=" * 90)
print("STEP 2: D10 DASAMSA FORMULA VERIFICATION")
print("=" * 90)

test_planets_d10 = {
    # --- Sector ETFs Conception 1998-12-16 12:00 PM NY ---
    "XLK_Asc (Aq 29°26')":      (10*30 + 29 + 26/60.0, "Scorpio"),
    "XLK_Sun (Sag 00°42')":     (8*30 + 0 + 42/60.0,   "Sagittarius"),
    "XLK_Moon (Sco 05°45')":    (7*30 + 5 + 45/60.0,   "Leo"),
    "XLK_Mars (Vir 16°42')":    (5*30 + 16 + 42/60.0,  "Libra"),
    "XLK_Mercury (Sco 09°38')":(7*30 + 9 + 38/60.0,   "Libra"),
    "XLK_Jupiter (Aq 26°10')":(10*30 + 26 + 10/60.0,  "Libra"),
    "XLK_Venus (Sag 12°22')":  (8*30 + 12 + 22/60.0,   "Aries"),
    "XLK_Saturn (Ar 03°03')":  (0*30 + 3 + 3/60.0,     "Taurus"),
    "XLK_Rahu (Leo 01°21')":   (4*30 + 1 + 21/60.0,    "Virgo"),
    "XLK_Ketu (Aq 01°21')":    (10*30 + 1 + 21/60.0,   "Aquarius"),
    # --- SMH Conception 2000-12-18 ---
    "SMH_Asc (Pis 03°42')":    (11*30 + 3 + 42/60.0,   "Sagittarius"),
    "SMH_Sun (Sag 03°14')":    (8*30 + 3 + 14/60.0,    "Capricorn"),
    "SMH_Moon (Vir 11°46')":   (5*30 + 11 + 46/60.0,   "Leo"),
    "SMH_Mercury (Sco 29°15')":(7*30 + 29 + 15/60.0,   "Aries"),
    "SMH_Saturn (Tau 01°26')":(1*30 + 1 + 26/60.0,    "Aquarius"),
    "SMH_Ketu (Sag 22°31')":   (8*30 + 22 + 31/60.0,   "Leo"),
    # --- XLRE Conception 2015-10-06 ---
    "XLRE_Asc (Sco 17°51')":   (7*30 + 17 + 51/60.0,   "Sagittarius"),
    "XLRE_Sun (Vir 19°00')":   (5*30 + 19 + 0/60.0,    "Scorpio"),
    "XLRE_Moon (Can 09°46')":  (3*30 + 9 + 46/60.0,    "Taurus"),
    "XLRE_Jupiter (Leo 17°54')":(4*30 + 17 + 54/60.0,  "Capricorn"),
    "XLRE_Saturn (Sco 07°25')":(7*30 + 7 + 25/60.0,    "Virgo"),
    # --- XME Conception 2006-06-19 ---
    "XME_Asc (Leo 23°09')":    (4*30 + 23 + 9/60.0,    "Pisces"),
    "XME_Moon (Pis 18°23')":   (11*30 + 18 + 23/60.0,  "Aries"),
    "XME_Jupiter (Lib 15°28')":(6*30 + 15 + 28/60.0,   "Taurus"),
}

print(f"\n  {'Planet':<35} {'Our Formula':>14} {'Chrome Truth':>14}  MATCH?")
print(f"  {'-'*75}")
d10_pass = d10_fail = 0
for label, (lon, chrome_truth) in test_planets_d10.items():
    our = dasamsa(lon)
    match = "✅" if our == chrome_truth else "❌"
    if our == chrome_truth: d10_pass += 1
    else: d10_fail += 1
    print(f"  {label:<35} {our:>14} {chrome_truth:>14}  {match}")
print(f"\n  D10 Result: {d10_pass} PASS / {d10_fail} FAIL")

print("\n" + "=" * 90)
print("STEP 3: ASHTAKVARGA SAV — VERIFY HOUSE COUNTING METHOD")
print("The Chrome JSON labels houses as ABSOLUTE ZODIAC signs, not relative to Ascendant")
print("e.g. 'H1_Aq' = House 1 = Aquarius absolute, not '1st house from Ascendant'")
print("This means the website treats House 1 = Aries always (absolute) OR counts from Asc sign")
print("=" * 90)

# From XLC Conception: Asc = Leo 22°16', Chrome SAV = H1_Ari:31, H2_Tau:30, H3_Gem:31...
# This means H1 = Aries, H2 = Taurus... absolute zodiac. NOT relative to Ascendant.
# But XLRE_Trading: Asc = Libra 19°32', Chrome SAV = H1_Ari:23, H2_Tau:29...
# H1 is still Aries! Confirms: SAV is stored as ABSOLUTE ZODIAC SIGN not relative to Asc.
print("\n  KEY FINDING: Chrome stores SAV indexed by ABSOLUTE ZODIAC SIGN (Aries=H1 always)")
print("  Our backend was incorrectly offsetting by Ascendant sign index!")
print("  FIX: Remove Ascendant offset from SAV — use raw absolute sign index directly.")

# Verify with XLK_Conception: Asc=Aquarius(10), our raw sarva[0..11] = absolute zodiac
# Chrome says H1_Aq=26, H2_Pi=23, H3_Ar=30... so H1=Aquarius... wait
# XLK has H1_Aq meaning House1=Aquarius (Ascendant sign)
# XLC Conception: Asc=Leo, Chrome H1_Ari... that's NOT the Ascendant sign
# Let's look more carefully...
print("\n  CHECKING XLC Conception: Asc=Leo (sign_idx=4), Chrome H1=Aries (sign_idx=0)")
print("  => Chrome H1 = Aries = absolute House 1 of the Kalpurush chart (Aries=House1 always)")
print("\n  CHECKING XLK Conception: Asc=Aquarius (sign_idx=10), Chrome H1=Aquarius (sign_idx=10)")
print("  => Chrome H1 = Aquarius = ASCENDANT sign. Relative to Ascendant!")
print("\n  CHECKING XLRE Conception: Asc=Scorpio (sign_idx=7), Chrome H1=Scorpio (sign_idx=7)")
print("  => Chrome H1 = Scorpio = ASCENDANT sign. Relative to Ascendant!")
print("\n  CHECKING SMH Conception: Asc=Pisces (sign_idx=11), Chrome H1_Ar=25")
print("  => Chrome H1 = Aries (sign_idx=0) = NOT Ascendant! INCONSISTENCY!")
print("\n  CONCLUSION: Website uses RELATIVE from Ascendant for some, absolute for others?")
print("  OR: SMH SAV chrome labels are WRONG/misread by Chrome agent.")
print("\n  Let's compute SAV absolutely and from Ascendant for SMH to determine which matches:")
