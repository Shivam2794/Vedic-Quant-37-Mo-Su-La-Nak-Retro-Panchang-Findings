"""Quick test of the Swiss Ephemeris engine."""
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
jd = swe.julday(2024, 1, 1, 12.0)

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKS = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
        'Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni',
        'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
        'Moola','P.Ashadha','U.Ashadha','Shravana','Dhanishta',
        'Shatabhisha','P.Bhadra','U.Bhadra','Revati']

bodies = [(0,'Sun'),(1,'Moon'),(2,'Mercury'),(3,'Venus'),(4,'Mars'),
          (5,'Jupiter'),(6,'Saturn'),(7,'Uranus'),(8,'Neptune'),(9,'Pluto')]

flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH

print("Date: Jan 1, 2024 12:00 UTC | Ayanamsa: Lahiri")
print("=" * 80)
for pid, name in bodies:
    r = swe.calc_ut(jd, pid, flags)
    lon, lat, dist, speed = r[0][0], r[0][1], r[0][2], r[0][3]
    sign = SIGNS[int(lon / 30)]
    nak = NAKS[int(lon / (360/27))]
    pada = int((lon % (360/27)) / (360/108)) + 1
    retro = "R" if speed < 0 else "D"
    print(f"  {name:10s} {lon:8.3f}  {sign:12s} {nak:15s} P{pada}  {speed:+7.3f} {retro}")

# Rahu (Mean Node)
r = swe.calc_ut(jd, swe.MEAN_NODE, flags)
lon = r[0][0]
sign = SIGNS[int(lon / 30)]
nak = NAKS[int(lon / (360/27))]
pada = int((lon % (360/27)) / (360/108)) + 1
print(f"  {'Rahu':10s} {lon:8.3f}  {sign:12s} {nak:15s} P{pada}")

# Ketu = Rahu + 180
ketu_lon = (lon + 180) % 360
sign = SIGNS[int(ketu_lon / 30)]
nak = NAKS[int(ketu_lon / (360/27))]
pada = int((ketu_lon % (360/27)) / (360/108)) + 1
print(f"  {'Ketu':10s} {ketu_lon:8.3f}  {sign:12s} {nak:15s} P{pada}")

print("\nSwiss Ephemeris engine: OPERATIONAL")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
