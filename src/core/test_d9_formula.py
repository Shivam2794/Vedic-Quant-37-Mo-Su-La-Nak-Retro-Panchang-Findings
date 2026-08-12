import sys
sys.stdout.reconfigure(encoding='utf-8')

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def navamsa_nakshatra_pada(lon):
    """The correct classical Parashari D9 formula: absolute navamsa number mod 12"""
    nav_num = int(lon / (10.0/3.0))
    return SIGNS[nav_num % 12]

# ALL test cases from Chrome data
tests = [
    (10*30+29+26/60.0, 'Aries',       'XLK_Asc Aq29.44'),
    (8*30+0+42/60.0,   'Aries',       'XLK_Sun Sag0.7'),
    (7*30+5+45/60.0,   'Leo',         'XLK_Moon Sco5.75'),
    (5*30+16+42/60.0,  'Capricorn',   'XLK_Mars Vir16.7'),
    (7*30+9+38/60.0,   'Sagittarius', 'XLK_Mercury Sco9.63'),
    (10*30+26+10/60.0, 'Taurus',      'XLK_Jupiter Aq26.17'),
    (8*30+12+22/60.0,  'Cancer',      'XLK_Venus Sag12.37'),
    (0*30+3+3/60.0,    'Aries',       'XLK_Saturn Ar3.05'),
    (4*30+1+21/60.0,   'Aries',       'XLK_Rahu Leo1.35'),
    (10*30+1+21/60.0,  'Libra',       'XLK_Ketu Aq1.35'),
    (11*30+3+42/60.0,  'Leo',         'SMH_Asc Pi3.7'),
    (8*30+3+14/60.0,   'Pisces',      'SMH_Sun Sag3.23'),
    (5*30+11+46/60.0,  'Pisces',      'SMH_Moon Vir11.77'),
    (6*30+3+14/60.0,   'Scorpio',     'SMH_Mars Lib3.23'),
    (7*30+29+15/60.0,  'Virgo',       'SMH_Mercury Sco29.25'),
    (1*30+9+36/60.0,   'Virgo',       'SMH_Jupiter Tau9.6'),
    (9*30+18+7/60.0,   'Aries',       'SMH_Venus Cap18.12'),
    (1*30+1+26/60.0,   'Capricorn',   'SMH_Saturn Tau1.43'),
    (2*30+22+31/60.0,  'Pisces',      'SMH_Rahu Gem22.52'),
    (8*30+22+31/60.0,  'Scorpio',     'SMH_Ketu Sag22.52'),
    (5*30+19+0/60.0,   'Pisces',      'XLRE_Sun Vir19'),
    (3*30+9+46/60.0,   'Scorpio',     'XLRE_Moon Can9.77'),
    (4*30+17+54/60.0,  'Scorpio',     'XLRE_Jupiter Leo17.9'),
    (5*30+6+5/60.0,    'Gemini',      'XLRE_Rahu Vir6.08'),
    (11*30+6+5/60.0,   'Sagittarius', 'XLRE_Ketu Pi6.08'),
    (2*30+4+17/60.0,   'Sagittarius', 'XME_Sun Gem4.28'),
    (6*30+15+28/60.0,  'Libra',       'XME_Jupiter Lib15.47'),
    (1*30+0+54/60.0,   'Libra',       'XME_Venus Tau0.9'),
    (11*30+6+3/60.0,   'Cancer',      'XME_Rahu Pi6.05'),
    (5*30+6+3/60.0,    'Aries',       'XME_Ketu Vir6.05'),
]

print("D9 NAKSHATRA-PADA FORMULA TEST")
print(f"{'Label':<30} {'Our':>14} {'Chrome':>14}  STATUS")
print("-"*68)
passes = fails = 0
for lon, expected, label in tests:
    got = navamsa_nakshatra_pada(lon)
    ok = "OK" if got == expected else "FAIL"
    if got == expected: passes += 1
    else: fails += 1
    print(f"{label:<30} {got:>14} {expected:>14}  {ok}")
print(f"\nResult: {passes} PASS / {fails} FAIL out of {len(tests)}")
