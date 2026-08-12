import sys, swisseph as swe
from datetime import datetime
import pytz
sys.stdout.reconfigure(encoding='utf-8')

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# Check if the Chrome D9 is computed from TROPICAL longitude, not sidereal
# For SMH 2000-12-18 12:00 NY:
# Sun sidereal = Sag 3°14', tropical = Sag 3°14' + ayanamsha (~23.7°) = Capricorn ~26.9° tropical
# Chrome D9 Sun = Pisces

# Let's get both tropical and sidereal longitudes and try computing D9 from each
PLANET_IDS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
              "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}

def get_both_lons(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_utc = ny_tz.localize(dt_naive).astimezone(pytz.utc)
    utc_hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    
    sidereal_flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    tropical_flags = swe.FLG_SWIEPH
    
    result = {}
    for p, pid in PLANET_IDS.items():
        sid = swe.calc_ut(jd, pid, sidereal_flags)[0][0]
        trop = swe.calc_ut(jd, pid, tropical_flags)[0][0]
        result[p] = {"sid": sid, "trop": trop}
    
    ketu_sid = (result["Rahu"]["sid"] + 180) % 360
    ketu_trop = (result["Rahu"]["trop"] + 180) % 360
    result["Ketu"] = {"sid": ketu_sid, "trop": ketu_trop}
    
    houses_sid, ascmc_sid = swe.houses_ex(jd, 40.7128, -74.0060, b'W', sidereal_flags)
    houses_trop, ascmc_trop = swe.houses_ex(jd, 40.7128, -74.0060, b'W', tropical_flags)
    result["Ascendant"] = {"sid": ascmc_sid[0], "trop": ascmc_trop[0]}
    
    return result

def nav_from_lon(lon):
    nav_num = int(lon / (10.0/3.0))
    return SIGNS[nav_num % 12]

CHROME_D9_SMH = {
    "Sun":"Pisces","Moon":"Pisces","Mars":"Scorpio","Mercury":"Virgo",
    "Jupiter":"Virgo","Venus":"Aries","Saturn":"Capricorn","Rahu":"Pisces",
    "Ketu":"Scorpio","Ascendant":"Leo"
}
CHROME_D9_XLK = {
    "Sun":"Aries","Moon":"Leo","Mars":"Capricorn","Mercury":"Sagittarius",
    "Jupiter":"Taurus","Venus":"Cancer","Saturn":"Aries","Rahu":"Aries",
    "Ketu":"Libra","Ascendant":"Aries"
}

print("TESTING TROPICAL vs SIDEREAL D9 COMPUTATION")
print("=" * 90)

for case_label, dt_str, chrome_d9 in [
    ("SMH Conception 2000-12-18", "2000-12-18 12:00:00", CHROME_D9_SMH),
    ("XLK Conception 1998-12-16", "1998-12-16 12:00:00", CHROME_D9_XLK),
]:
    print(f"\n  {case_label}")
    lons = get_both_lons(dt_str)
    print(f"  {'Planet':<12} {'Sidereal':>12} {'Tropical':>12} {'D9_sid':>12} {'D9_trop':>12} {'Chrome_D9':>12}  WHICH?")
    print(f"  {'-'*80}")
    for planet in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
        sid = lons[planet]["sid"]
        trop = lons[planet]["trop"]
        d9_sid = nav_from_lon(sid)
        d9_trop = nav_from_lon(trop)
        chrome = chrome_d9.get(planet,"N/A")
        which = "TROP" if d9_trop==chrome else ("SID" if d9_sid==chrome else "NEITHER")
        sid_sign = SIGNS[int(sid/30)%12]
        trop_sign = SIGNS[int(trop/30)%12]
        print(f"  {planet:<12} {sid_sign+' '+str(int(sid%30))+'°':>12} {trop_sign+' '+str(int(trop%30))+'°':>12} {d9_sid:>12} {d9_trop:>12} {chrome:>12}  {which}")
