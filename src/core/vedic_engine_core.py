import sys, math, json
import swisseph as swe
from datetime import datetime
import pytz

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigasira","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
PLANET_IDS = {
    "Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
    "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,
    "Rahu":swe.MEAN_NODE, "Ketu": -1, "Ascendant": -2
}

BAV_RULES = {
    "Sun": {"Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11], "Mercury": [3,5,6,9,10,11,12], "Jupiter": [5,6,9,11], "Venus": [6,7,12], "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [3,4,6,10,11,12]},
    "Moon": {"Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11], "Mercury": [1,3,4,5,7,8,10,11], "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11], "Saturn": [3,5,6,11], "Ascendant": [3,6,10,11]},
    "Mars": {"Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,10,11], "Mercury": [3,5,6,11], "Jupiter": [6,10,11,12], "Venus": [6,8,11,12], "Saturn": [1,4,7,8,9,10,11], "Ascendant": [1,3,6,10,11]},
    "Mercury": {"Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11], "Mars": [1,2,4,7,8,9,10,11], "Mercury": [1,3,5,6,9,10,11,12], "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11], "Saturn": [1,2,4,7,8,9,10,11], "Ascendant": [1,2,4,6,8,10,11]},
    "Jupiter": {"Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,6,7,9,11], "Mars": [1,2,4,7,8,10,11], "Mercury": [1,2,4,5,6,9,10,11], "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11], "Saturn": [3,5,6,12], "Ascendant": [1,2,4,5,6,9,10,11]},
    "Venus": {"Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12], "Mars": [3,5,6,9,11,12], "Mercury": [3,5,6,9,11], "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11], "Saturn": [3,4,5,8,9,10,11], "Ascendant": [1,2,3,4,5,8,9,11]},
    "Saturn": {"Sun": [1,2,4,7,8,10,11], "Moon": [2,3,6,11], "Mars": [3,5,6,10,11], "Mercury": [6,8,9,10,11,12], "Jupiter": [5,6,11,12], "Venus": [6,11,12], "Saturn": [3,5,6,11], "Ascendant": [1,3,4,6,10,11]}
}

class VedicAstrologyEngine:
    def __init__(self, lat=40.7128, lon=-74.0060, tz='America/New_York'):
        self.lat = lat
        self.lon = lon
        self.tz = pytz.timezone(tz)
        
    def get_jd(self, dt_str):
        dt = self.tz.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
        return jd, dt

    def nak_pada(self, lon):
        nak_size = 360.0 / 27.0
        nak_idx = int(lon / nak_size)
        deg_in = lon - nak_idx * nak_size
        pada = int(deg_in / (nak_size / 4)) + 1
        return NAKSHATRAS[nak_idx % 27], min(pada, 4)

    def calculate_d1(self, jd):
        flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
        # FLG_SPEED is essential for accurate Chesta Bala in Shadbala
        flags_with_speed = swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED
        
        # We also need to compute the Ascendant and MC (Midheaven) accurately
        houses, ascmc = swe.houses_ex(jd, self.lat, self.lon, b'W', flags)
        asc_lon = ascmc[0]
        mc_lon = ascmc[1]
        
        planets = {}
        for p, pid in PLANET_IDS.items():
            if pid == -1: # Ketu
                lon = (planets["Rahu"]["longitude"] + 180.0) % 360.0
                spd = -planets["Rahu"]["speed"]  # Ketu moves opposite to Rahu
            elif pid == -2: # Ascendant
                lon = asc_lon
                spd = 0
            else:
                res = swe.calc_ut(jd, pid, flags_with_speed)
                lon = res[0][0]
                spd = res[0][3]
            
            nak, pada = self.nak_pada(lon)
            sign_idx = int(lon / 30) % 12
            d = int(lon % 30); m = int((lon % 30 - d) * 60); s = int(((lon % 30 - d) * 60 - m) * 60)
            
            planets[p] = {
                "sign": SIGNS[sign_idx],
                "sign_idx": sign_idx,
                "longitude": lon,
                "degrees": f"{d:02d}° {m:02d}' {s:02d}\"",
                "nakshatra": nak,
                "pada": pada,
                "retrograde": spd < 0,
                "speed": spd
            }
            
        planets["MC"] = {"longitude": mc_lon} # Needed for precise Dik Bala
        return planets

    def calculate_divisional(self, planets):
        d9 = {}
        d10 = {}
        
        for p, data in planets.items():
            if p == "MC": continue
            lon = data["longitude"]
            d1_sign = int(lon / 30)
            rem = lon % 30
            
            # Navamsa (D9)
            # Element-based start: Fire=0, Earth=9, Air=6, Water=3
            start9 = [0, 9, 6, 3][d1_sign % 4]
            d9_idx = (start9 + int(rem / (30.0 / 9.0))) % 12
            d9[p] = SIGNS[d9_idx]
            
            # Dasamsa (D10)
            # Odd signs start from same sign. Even signs start from 9th sign.
            part10 = int(rem / 3.0)
            if d1_sign % 2 == 0:  # Odd sign (0-indexed, so Aries=0=even)
                d10_idx = (d1_sign + part10) % 12
            else:  # Even sign (1-indexed, so Taurus=1=odd)
                d10_idx = (d1_sign + 8 + part10) % 12
            d10[p] = SIGNS[d10_idx]
            
        return {"D9_navamsa": d9, "D10_dasamsa": d10}

    def calculate_bav_sav(self, planets):
        bav = {p: {s: 0 for s in SIGNS} for p in BAV_RULES.keys()}
        
        for tgt_planet, sources in BAV_RULES.items():
            for src_planet, positions in sources.items():
                src_sign_idx = planets[src_planet]["sign_idx"]
                for pos in positions:
                    target_sign_idx = (src_sign_idx + pos - 1) % 12
                    bav[tgt_planet][SIGNS[target_sign_idx]] += 1
                    
        sav = {s: sum(bav[p][s] for p in BAV_RULES.keys()) for s in SIGNS}
        return {"bhinnashtakvarga": bav, "sarvashtakvarga": sav}

    def process(self, dt_str):
        jd, dt_utc = self.get_jd(dt_str)
        planets = self.calculate_d1(jd)
        div = self.calculate_divisional(planets)
        ashtakvarga = self.calculate_bav_sav(planets)
        
        # Formatting D1 output to match user snippet
        d1_rasi = {}
        for p, d in planets.items():
            if p == "MC": continue
            d1_rasi[p] = {"sign": d["sign"], "degrees": d["degrees"], "nakshatra": d["nakshatra"], "pada": d["pada"]}
            
        if planets["Mercury"]["retrograde"]: d1_rasi["Mercury"]["retrograde"] = True
        
        return {
            "birth_datetime": dt_str,
            "D1_rasi": d1_rasi,
            "D9_navamsa": div["D9_navamsa"],
            "D10_dasamsa": div["D10_dasamsa"],
            "ashtakvarga": ashtakvarga
        }


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
