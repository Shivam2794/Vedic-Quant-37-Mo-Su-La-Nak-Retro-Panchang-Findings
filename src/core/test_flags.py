import swisseph as swe
import datetime

swe.set_ephe_path('/ephe')

jd = 2454788.1930555557

swe.set_topo(-74.0060, 40.7128, 0.0)

targets = {
    "Sun": 211.825,
    "Moon": 93.426,
    "Mars": 217.095,
    "Jupiter": 265.771,
    "Asc": 278.505
}

flags_geocentric = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
flags_topocentric = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_TOPOCTR

for name, flags in [("Geocentric", flags_geocentric), ("Topocentric", flags_topocentric)]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    print(f"--- {name} ---")
    pos_sun = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    pos_moon = swe.calc_ut(jd, swe.MOON, flags)[0][0]
    pos_mars = swe.calc_ut(jd, swe.MARS, flags)[0][0]
    pos_jup = swe.calc_ut(jd, swe.JUPITER, flags)[0][0]
    asc = swe.houses_ex(jd, 40.7128, -74.0060, b'P', swe.FLG_SIDEREAL)[1][0]
    
    diff_sun = abs(pos_sun - targets["Sun"])
    diff_moon = abs(pos_moon - targets["Moon"])
    diff_mars = abs(pos_mars - targets["Mars"])
    diff_jup = abs(pos_jup - targets["Jupiter"])
    diff_asc = abs(asc - targets["Asc"])
    
    print(f"Sun: {pos_sun:.3f} (diff {pos_sun - targets['Sun']:.3f})")
    print(f"Moon: {pos_moon:.3f} (diff {pos_moon - targets['Moon']:.3f})")
    print(f"Mars: {pos_mars:.3f} (diff {pos_mars - targets['Mars']:.3f})")
    print(f"Jup: {pos_jup:.3f} (diff {pos_jup - targets['Jupiter']:.3f})")
    print(f"Asc: {asc:.3f} (diff {asc - targets['Asc']:.3f})")
    print("Total abs diff:", diff_sun+diff_moon+diff_mars+diff_jup+diff_asc)
