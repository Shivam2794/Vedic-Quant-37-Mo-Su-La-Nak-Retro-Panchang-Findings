import sys
sys.stdout.reconfigure(encoding='utf-8')

# Deep reverse-engineering: what formula produces Chrome's D9 results?
# We know the exact longitude and we know the Chrome answer.
# Let's manually trace what computation leads to each Chrome result.

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def sign_name(i): return SIGNS[i % 12]

# Element-based starting sign for navamsa
D9_STARTS_ELEMENT = {0:0,4:0,8:0, 1:9,5:9,9:9, 2:6,6:6,10:6, 3:3,7:3,11:3}

print("=" * 100)
print("MANUAL TRACE: Reverse-engineering the Chrome D9 formula")
print("=" * 100)

cases = [
    # (label, lon_degrees, chrome_d9_result)
    ("SMH_Sun  Sag 3°14'",    8*30 + 3 + 14/60.0,   "Pisces"),
    ("SMH_Moon Vir 11°46'",   5*30 + 11 + 46/60.0,  "Pisces"),
    ("SMH_Mars Lib 3°14'",    6*30 + 3 + 14/60.0,   "Scorpio"),
    ("SMH_Merc Sco 29°15'",   7*30 + 29 + 15/60.0,  "Virgo"),
    ("SMH_Jupi Tau 9°36'",    1*30 + 9 + 36/60.0,   "Virgo"),
    ("SMH_Venu Cap 18°07'",   9*30 + 18 + 7/60.0,   "Aries"),
    ("SMH_Rahu Gem 22°31'",   2*30 + 22 + 31/60.0,  "Pisces"),
    ("SMH_Ketu Sag 22°31'",   8*30 + 22 + 31/60.0,  "Scorpio"),
    ("XLRE_Sun Vir 19°00'",   5*30 + 19 + 0/60.0,   "Pisces"),
    ("XLRE_Moon Can 9°46'",   3*30 + 9 + 46/60.0,   "Scorpio"),
    ("XLRE_Jupi Leo 17°54'",  4*30 + 17 + 54/60.0,  "Scorpio"),
    ("XLRE_Rahu Vir 6°05'",   5*30 + 6 + 5/60.0,    "Gemini"),
    ("XLRE_Ketu Pis 6°05'",   11*30 + 6 + 5/60.0,   "Sagittarius"),
    ("XME_Sun  Gem 4°17'",    2*30 + 4 + 17/60.0,   "Sagittarius"),
    ("XME_Jupi Lib 15°28'",   6*30 + 15 + 28/60.0,  "Libra"),
    ("XME_Venu Tau 0°54'",    1*30 + 0 + 54/60.0,   "Libra"),
    ("XME_Rahu Pis 6°03'",    11*30 + 6 + 3/60.0,   "Cancer"),
    ("XME_Ketu Vir 6°03'",    5*30 + 6 + 3/60.0,    "Aries"),
    ("XLK_Asc  Aq 29°26'",    10*30 + 29 + 26/60.0, "Aries"),
    ("XLK_Mars Vir 16°42'",   5*30 + 16 + 42/60.0,  "Capricorn"),
    ("XLK_Merc Sco 9°38'",    7*30 + 9 + 38/60.0,   "Sagittarius"),
]

for label, lon, chrome_expected in cases:
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon % 30
    
    # Method 1: absolute mod 12
    m1 = SIGNS[int(lon / (10/3)) % 12]
    
    # Method 2: element start + nav_num
    nav_n = int(deg_in_sign * 9 / 30)
    m2 = SIGNS[(D9_STARTS_ELEMENT[sign_idx] + nav_n) % 12]
    
    # Method 3: absolute but with different computation
    # Each navamsa = 3°20' = 200 arcmin
    lon_arcmin = lon * 60
    nav_abs = int(lon_arcmin / 200)
    m3 = SIGNS[nav_abs % 12]
    
    # Method 4: Try computing which navamsa number within sign, using floor
    # nav_num_in_sign = floor((deg_in_sign / 30) * 9)
    nav_in_sign = int((deg_in_sign / 30.0) * 9)
    m4_start = D9_STARTS_ELEMENT[sign_idx]
    m4 = SIGNS[(m4_start + nav_in_sign) % 12]

    # What navamsa number would produce Chrome's answer with element-based start?
    chrome_sign_idx = SIGNS.index(chrome_expected)
    start = D9_STARTS_ELEMENT[sign_idx]
    required_nav = (chrome_sign_idx - start) % 12
    
    print(f"\n{label}")
    print(f"  lon={lon:.4f} sign={SIGNS[sign_idx]} deg_in_sign={deg_in_sign:.4f}")
    print(f"  Required nav_num from element start ({SIGNS[start]}): {required_nav}")
    print(f"  nav_num via int(deg*9/30)={nav_n} | via int(lon_arcmin/200)%12 mod={nav_abs%12} | int(deg/30*9)={nav_in_sign}")
    print(f"  M1(abs%12)={m1} | M2(elem+int(d*9/30))={m2} | M3(arcmin)={m3} | M4(floor)={m4} | Chrome={chrome_expected}")
    if m1==chrome_expected: print("  => METHOD 1 CORRECT")
    elif m2==chrome_expected: print("  => METHOD 2 CORRECT")
    elif m3==chrome_expected: print("  => METHOD 3 CORRECT")
    elif m4==chrome_expected: print("  => METHOD 4 CORRECT")
    else:
        # Try: what if we use (sign_idx * 9 + nav_in_sign) % 12
        m5 = SIGNS[(sign_idx * 9 + nav_in_sign) % 12]
        # Try: direct nakshatra pada
        nak_size = 360.0 / 108.0
        pada = int(lon / nak_size)
        m6 = SIGNS[pada % 12]
        print(f"  M5(si*9+nav)={m5} | M6(pada%12)={m6}")
        if m5 == chrome_expected: print("  => METHOD 5 CORRECT")
        if m6 == chrome_expected: print("  => METHOD 6 CORRECT")
        if m5 != chrome_expected and m6 != chrome_expected:
            # last resort: try all combinations
            for st in range(12):
                for nv in range(9):
                    if SIGNS[(st+nv)%12] == chrome_expected:
                        # check if nv matches some formula of deg_in_sign
                        pass
            print(f"  => UNKNOWN FORMULA (required nav={required_nav} from start={SIGNS[start]})")
