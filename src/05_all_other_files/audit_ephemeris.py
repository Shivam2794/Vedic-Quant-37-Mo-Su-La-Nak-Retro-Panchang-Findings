import sys
import datetime
import pytz
import swisseph as swe
import numpy as np

sys.path.append(r"E:\Python\Learn\Astrology 2-20260611T223423Z-3-001\Astrology 2\orion_essential\Codebase")

from orion_ephemeris_core import OrionEphemerisEngine

def main():
    try:
        engine = OrionEphemerisEngine(ephe_path=None) # let's try None to see if we can avoid an invalid path error, wait OrionEphemerisEngine expects a string or None, though its signature says str = "/ephe".
    except Exception as e:
        print("Engine init error with None:", e)
        engine = OrionEphemerisEngine()

    ny = pytz.timezone('America/New_York')
    # 1993-01-22 09:30:00 EST
    dt = ny.localize(datetime.datetime(1993, 1, 22, 9, 30, 0)).astimezone(datetime.timezone.utc)
    
    jd = engine._datetime_to_jd(dt)
    
    planets = {
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }
    
    longs = {}
    print(f"--- Planetary Longitudes for {dt} UTC ---")
    for name, p_id in planets.items():
        pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL)
        longs[name] = pos[0]
        print(f"{name}: {longs[name]:.4f}")
        
    print("\n--- Exact Angles Between Slow-Moving Planets ---")
    planet_names = list(planets.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planet_names[i]
            p2 = planet_names[j]
            diff = abs(longs[p1] - longs[p2]) % 360.0
            angle = min(diff, 360.0 - diff)
            print(f"{p1} - {p2}: {angle:.4f}")

if __name__ == "__main__":
    main()
