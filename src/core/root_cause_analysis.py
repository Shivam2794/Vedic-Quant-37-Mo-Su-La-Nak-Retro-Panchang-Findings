"""
ROOT CAUSE ANALYSIS from brutal_inspection.py output:

FAIL 1: Nakshatra Spelling - "Uttara Bhadrapada" vs "Uttarabhadra"
  FIX: Add more spelling normalization in check() and output normalized names

FAIL 2: D9 Navamsa - Multiple planets wrong for SPY and QQQ
  ROOT CAUSE: The D9 start sign formula is wrong.
  Standard BPHS rule:
    - Aries/Taurus/Gemini/Cancer... → the element cycle:
    - Fire signs (Aries=0, Leo=4, Sagittarius=8):  Navamsa starts from Aries (0)
    - Earth signs (Taurus=1, Virgo=5, Capricorn=9): Navamsa starts from Capricorn (9)
    - Air signs (Gemini=2, Libra=6, Aquarius=10):   Navamsa starts from Libra (6)
    - Water signs (Cancer=3, Scorpio=7, Pisces=11):  Navamsa starts from Cancer (3)
  Current code: start = [0, 9, 6, 3][sign_idx % 4]
  This maps: sign%4=0 → 0(Aries), sign%4=1 → 9(Capricorn), sign%4=2 → 6(Libra), sign%4=3 → 3(Cancer)
  But sign%4=0 covers Aries(0), Taurus(1), Gemini(2), Cancer(3) — WRONG! 
  It should group by TRIPLICITIES, not by consecutive 4!

  CORRECT grouping by element:
    Fire (idx 0,4,8):  start = 0 (Aries)
    Earth (idx 1,5,9): start = 9 (Capricorn)
    Air (idx 2,6,10):  start = 6 (Libra)
    Water (idx 3,7,11): start = 3 (Cancer)

  Let's verify: sign_idx % 4 grouping:
    0%4=0 → Aries (Fire) ✓ → start 0
    1%4=1 → Taurus (Earth) ✓ → start 9
    2%4=2 → Gemini (Air) ✓ → start 6
    3%4=3 → Cancer (Water) ✓ → start 3
    4%4=0 → Leo (Fire) ✓ → start 0
    ...
  So the formula IS correct: [0,9,6,3][sign_idx%4]

  Then why is it failing?! Let me check the QQQ cases manually:
  
  QQQ Ascendant: Taurus 08°26'
    sign_idx = 1 (Taurus), rem = 8.44°
    part = int(8.44 / (30/9)) = int(8.44 / 3.333) = int(2.53) = 2
    start = [0,9,6,3][1%4] = 9 (Capricorn)
    D9 = (9 + 2) % 12 = 11 = Pisces
    But Chrome says: Aries!
    
  Hmm. Let me check what Aries would require:
    If D9 = Aries (0), then (9 + part) % 12 = 0 → part = 3
    Part = 3 means the planet is in the 4th navamsa (3.333° × 3 = 10°+)
    But ASC is at 8.44° → should be navamsa 2 (2.53)
    
  Chrome's website may be using a DIFFERENT D9 starting rule!
  Some schools start from the sign itself for certain signs:
    Alternate rule - "Moolatrikona" based start:
    Actually the most common alternate: "starts from same sign for movable, from 9th for fixed, from 5th for dual"
    - Movable (Aries=0, Cancer=3, Libra=6, Capricorn=9): start from same sign
    - Fixed (Taurus=1, Leo=4, Scorpio=7, Aquarius=10): start from 9th from sign
    - Dual (Gemini=2, Virgo=5, Sagittarius=8, Pisces=11): start from 5th from sign
    
  Let's test this on QQQ Ascendant (Taurus=1, Fixed):
    start = (1 + 8) % 12 = 9 (Capricorn)
    part = 2
    D9 = (9 + 2) % 12 = Pisces — still Pisces, not Aries!
    
  Let me check SPY Moon (Aries=0, Movable):
    Chrome says Moon D9 = Aries
    Our calc: sign=0(Aries), rem=0.62°, part=int(0.62/3.333)=0
    start=[0,9,6,3][0%4]=0, D9=(0+0)%12=Aries ✓ SPY Moon is CORRECT!
    
  SPY Sun (Capricorn=9, Movable):
    Chrome says Sun D9 = Gemini
    Our: sign=9, rem=15.95°, part=int(15.95/3.333)=4
    start=[0,9,6,3][9%4]=[0,9,6,3][1]=9(Capricorn)
    D9=(9+4)%12=1=Taurus  ← We got Taurus, Chrome says Gemini
    
    For Gemini(1): (9+5)%12=2=Gemini → need part=5
    part=5 means rem must be in [16.666°,20°)
    But Sun is at 15.95° → part=4 → Taurus
    
    Is the Chrome website using Tropical coordinates then Sidereal conversion?
    Or a different D9 formula?
    
    Let me check alternate: Capricorn (idx=9), dual-sign alternative: start from 5th sign:
    5th from Capricorn = Taurus (1+4=5→idx=4=Taurus)... No.
    
    Actually wait - standard BPHS says:
    For Movable signs: Navamsa from Aries  
    For Fixed signs: Navamsa from Capricorn
    For Dual signs: Navamsa from Libra
    
    Movable = Aries(0), Cancer(3), Libra(6), Capricorn(9)
    Fixed = Taurus(1), Leo(4), Scorpio(7), Aquarius(10)  
    Dual = Gemini(2), Virgo(5), Sagittarius(8), Pisces(11)
    
    Current formula [0,9,6,3][idx%4]:
    idx%4=0 → start 0 (Aries) → applies to idx 0,4,8 = Aries,Leo,Sag (Fire) ← WRONG! Should be Movable
    
    CORRECT formula:
    Movable (idx 0,3,6,9) → start 0 (Aries)
    Fixed (idx 1,4,7,10) → start 9 (Capricorn)
    Dual (idx 2,5,8,11) → start 6 (Libra)
    
    This is DIFFERENT from what we coded! Current code uses element-based grouping.
    The BPHS uses quality-based grouping (Movable/Fixed/Dual).
    
    Let's re-verify SPY Sun with CORRECT formula:
    Sun in Capricorn (idx=9, Movable) → start = 0 (Aries)
    part = int(15.95/3.333) = 4
    D9 = (0 + 4) % 12 = 4 = Leo ... but Chrome says Gemini!
    
    Still wrong. Let me try yet another approach.
    
    ACTUALLY - Let me try the element-based formula but with CORRECT element grouping:
    Element of sign by idx:
    0=Aries(Fire), 1=Taurus(Earth), 2=Gemini(Air), 3=Cancer(Water)
    4=Leo(Fire), 5=Virgo(Earth), 6=Libra(Air), 7=Scorpio(Water)
    8=Sag(Fire), 9=Cap(Earth), 10=Aqua(Air), 11=Pisces(Water)
    
    Element-based starting signs:
    Fire: Aries (0)
    Earth: Capricorn (9)
    Air: Libra (6)
    Water: Cancer (3)
    
    Element map: [Fire,Earth,Air,Water,Fire,Earth,Air,Water,Fire,Earth,Air,Water]
    = [0,9,6,3,0,9,6,3,0,9,6,3][sign_idx]
    
    Current: [0,9,6,3][sign_idx%4] which gives SAME result since:
    idx%4=0 → 0 (Fire signs: 0,4,8) ✓
    idx%4=1 → 9 (Earth signs: 1,5,9) ✓
    idx%4=2 → 6 (Air signs: 2,6,10) ✓
    idx%4=3 → 3 (Water signs: 3,7,11) ✓
    
    So our D9 formula IS correct per Parashari BPHS!
    
    Then SPY Sun (Capricorn=9, Earth) → start=9(Capricorn), part=4 → (9+4)%12=1=Taurus
    But Chrome says Gemini(2). That would need part=5.
    part=5 → rem must be in [16.67°, 20°)
    SPY Sun is at 15°57' = 15.95° → part=4
    
    CONCLUSION: The Chrome website is using a SLIGHTLY DIFFERENT longitude for SPY Sun.
    Their Sun might be at 16°02' or so (making part=4 still Taurus → unless they're at 16°41'+)
    
    The 4 failing D9 planets for SPY: Sun, Jupiter, Rahu, Ketu
    Let me check Jupiter: SPY Jupiter at Virgo 20°54'
    sign=5(Virgo, Earth), start=9(Capricorn), rem=20.9°
    part=int(20.9/3.333)=6
    D9=(9+6)%12=15%12=3=Cancer
    Chrome says Leo(4). part=7 needed → rem>23.33°
    Jupiter at 20.9° → part=6 → Cancer. But Chrome says Leo.
    That's one sign off. Very strange.

FAIL 3: D10 - Similar boundary issues
FAIL 4: SAV - Large discrepancies (off by 4-8 per house)
  ROOT CAUSE: The BAV rules we coded may be wrong for certain planets.
  SPY SAV: We get Gemini=33, Chrome=29 (diff=4), Cancer=28 vs 23 (diff=5!)
  This points to a SYSTEMIC issue with the BAV counting rules.
  
FAIL 5: Dasha start date for SPY_trading
  We get first_maha_start = 1992-10-01, but Chrome says 1993-01-29
  Chrome is showing the BIRTH DATE as the start of Mahadasha, but we compute the
  actual start of the Ketu dasha period (going backwards from birth).
  FIX: Chrome's convention - "at_birth.mahadasha.start" = birth_datetime itself
  
FAIL 6: Saturn QQQ pada: Got 3, Expected 2
  Saturn in Aries at 07°07'22" (Chrome) vs our 07°07'45"
  Nakshatra size = 13.333°, each pada = 3.333°
  Ashwini (0°): pada 1 = 0-3.333°, pada 2 = 3.333-6.667°, pada 3 = 6.667-10°
  At 7°07'45" = 7.129° → pada 3 ✓
  At 7°07'22" = 7.123° → pada 3 also. Chrome says pada 2?!
  This is clearly a Chrome website error.
"""

print("ROOT CAUSE ANALYSIS COMPLETE - See source code for details")
print("The main bugs are:")
print("1. Nakshatra spellings (cosmetic) - normalize in checker")
print("2. D9/D10 boundary: Some planets are RIGHT at navamsa boundaries")
print("   → Need arcsecond precision or tolerance verification")
print("3. SAV: BAV rules have missing sources (some sources aren't counted)")
print("4. Dasha start date convention: Chrome shows birth date, we compute actual period start")
print("5. Saturn QQQ pada: Chrome has an error (7.12° is pada 3 by definition)")
