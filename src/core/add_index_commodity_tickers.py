"""
Step 1: Add 10 index/commodity/ETF tickers to the natal DB.
These represent: broad market, commodities (gold/silver/oil), bonds, and sectors.
IPO/inception date used as the "natal" chart date (NYSE open at inception).
Computes all the same natal features as stocks (planets, houses, BAV/SAV, Shadbala, Karakas, Ghatak).
"""
import sqlite3, json, sys, math
sys.path.insert(0, r"C:\Users\Shivam Patel\Desktop\Python\Learn")
import swisseph as swe
from datetime import datetime
import pandas as pd

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
EPHE_PATH = r"C:\Users\Shivam Patel\Desktop\Python\Learn\ephe"
NYSE_LAT, NYSE_LON = 40.7128, -74.0060

swe.set_ephe_path(EPHE_PATH)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# New tickers with inception dates and sectors
NEW_TICKERS = [
    ("SPY",  "1993-01-22", "Index",     "S&P 500 ETF"),
    ("QQQ",  "1999-03-10", "Index",     "NASDAQ-100 ETF"),
    ("IWM",  "2000-05-26", "Index",     "Russell 2000 ETF"),
    ("DIA",  "1998-01-20", "Index",     "DJIA ETF"),
    ("GLD",  "2004-11-18", "Commodity", "Gold ETF"),
    ("SLV",  "2006-04-28", "Commodity", "Silver ETF"),
    ("USO",  "2006-04-10", "Commodity", "Oil ETF"),
    ("TLT",  "2002-07-26", "Bond",      "20Y Treasury ETF"),
    ("XLE",  "1998-12-22", "Sector",    "Energy Sector ETF"),
    ("VIXY", "2011-01-04", "Volatility","VIX Short-Term Futures ETF"),
]

PLANETS = {
    'Sun':  swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE, 'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO,
}
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Moola','P.Ashadha','U.Ashadha','Shravana','Dhanishta',
    'Shatabhisha','P.Bhadra','U.Bhadra','Revati'
]

# Ashtakavarga tables (from compute_ashtakavarga.py)
SUN_BAV    = {'Sun':[1,2,4,7,8,9,10,11],'Moon':[3,6,10,11],'Mars':[1,2,4,7,8,9,10,11],'Mercury':[3,5,6,9,10,11,12],'Jupiter':[5,6,9,11],'Venus':[6,7,12],'Saturn':[1,2,4,7,8,9,10,11],'Lagna':[3,4,6,10,11,12]}
MOON_BAV   = {'Sun':[3,6,7,8,10,11],'Moon':[1,3,6,7,10,11],'Mars':[2,3,5,6,9,10,11],'Mercury':[1,3,4,5,7,8,10,11],'Jupiter':[1,4,7,8,10,11,12],'Venus':[3,4,5,7,9,10,11],'Saturn':[3,5,6,11],'Lagna':[3,6,10,11]}
MARS_BAV   = {'Sun':[3,5,6,10,11],'Moon':[3,6,11],'Mars':[1,2,4,7,8,10,11],'Mercury':[3,5,6,11],'Jupiter':[6,10,11,12],'Venus':[6,8,11,12],'Saturn':[1,4,7,8,9,10,11],'Lagna':[1,3,6,10,11]}
MERCURY_BAV= {'Sun':[5,6,9,11,12],'Moon':[2,4,6,8,10,11],'Mars':[1,2,4,7,8,9,10,11],'Mercury':[1,3,5,6,9,10,11,12],'Jupiter':[6,8,11,12],'Venus':[1,2,3,4,5,8,9,11],'Saturn':[1,2,4,7,8,9,10,11],'Lagna':[1,2,4,6,8,10,11]}
JUPITER_BAV= {'Sun':[1,2,3,4,7,8,9,10,11],'Moon':[2,5,7,9,11],'Mars':[1,2,4,7,8,10,11],'Mercury':[1,2,4,5,6,9,10,11],'Jupiter':[1,2,3,4,7,8,10,11],'Venus':[2,5,6,9,10,11],'Saturn':[3,5,6,12],'Lagna':[1,2,4,5,6,7,9,10,11]}
VENUS_BAV  = {'Sun':[8,11,12],'Moon':[1,2,3,4,5,8,9,11,12],'Mars':[3,5,6,9,11,12],'Mercury':[3,5,6,9,11],'Jupiter':[5,8,9,10,11],'Venus':[1,2,3,4,5,8,9,10,11],'Saturn':[3,4,5,8,9,10,11],'Lagna':[1,2,3,4,5,8,9,11]}
SATURN_BAV = {'Sun':[1,2,4,7,8,10,11],'Moon':[3,6,11],'Mars':[3,5,6,10,11,12],'Mercury':[6,8,9,10,11,12],'Jupiter':[5,6,11,12],'Venus':[6,11,12],'Saturn':[3,5,6,11],'Lagna':[1,3,4,6,10,11]}
ALL_BAV    = {'Sun':SUN_BAV,'Moon':MOON_BAV,'Mars':MARS_BAV,'Mercury':MERCURY_BAV,'Jupiter':JUPITER_BAV,'Venus':VENUS_BAV,'Saturn':SATURN_BAV}

EXALTATION = {'Sun':10.0,'Moon':33.0,'Mars':298.0,'Mercury':165.0,'Jupiter':95.0,'Venus':357.0,'Saturn':200.0}
OWN_SIGNS  = {'Sun':[4],'Moon':[3],'Mars':[0,7],'Mercury':[2,5],'Jupiter':[8,11],'Venus':[1,6],'Saturn':[9,10]}
MOOLATRIKONA = {'Sun':(4,0,20),'Moon':(1,4,20),'Mars':(0,0,12),'Mercury':(5,16,20),'Jupiter':(8,0,10),'Venus':(6,0,15),'Saturn':(10,0,20)}
DIG_BALA_HOUSES = {'Sun':10,'Moon':4,'Mars':10,'Mercury':1,'Jupiter':1,'Venus':4,'Saturn':7}
KARAKA_PLANETS = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
KARAKA_NAMES   = ['AK','AmK','BK','MK','PK','GK','DK']
GHATAK_TABLE = {
    0:{"bad_day":6,"bad_nak":18,"bad_rashi":4,"bad_tithi":[2,7,12],"bad_lagna":6},
    1:{"bad_day":3,"bad_nak":21,"bad_rashi":5,"bad_tithi":[1,6,11],"bad_lagna":7},
    2:{"bad_day":0,"bad_nak":24,"bad_rashi":6,"bad_tithi":[5,10,15],"bad_lagna":8},
    3:{"bad_day":4,"bad_nak":0,"bad_rashi":7,"bad_tithi":[4,9,14],"bad_lagna":9},
    4:{"bad_day":1,"bad_nak":3,"bad_rashi":8,"bad_tithi":[3,8,13],"bad_lagna":10},
    5:{"bad_day":5,"bad_nak":6,"bad_rashi":9,"bad_tithi":[2,7,12],"bad_lagna":11},
    6:{"bad_day":2,"bad_nak":9,"bad_rashi":10,"bad_tithi":[1,6,11],"bad_lagna":0},
    7:{"bad_day":6,"bad_nak":12,"bad_rashi":11,"bad_tithi":[5,10,15],"bad_lagna":1},
    8:{"bad_day":3,"bad_nak":15,"bad_rashi":0,"bad_tithi":[4,9,14],"bad_lagna":2},
}
DAYS_OF_WEEK = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']


def compute_natal_for_ticker(ipo_date_str):
    parts = ipo_date_str.split('-')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    dt = datetime(year, month, day)
    market_open = 9.5  # 9:30 AM ET for all modern ETFs
    ts = pd.Timestamp(year, month, day, 9, 30).tz_localize('America/New_York').tz_convert('UTC')
    utc_h = ts.hour + ts.minute / 60.0
    jd = swe.julday(ts.year, ts.month, ts.day, utc_h)
    ayan = swe.get_ayanamsa_ut(jd)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH

    # Planets
    planet_data = {}
    for pname, pid in PLANETS.items():
        try:
            pos, _ = swe.calc_ut(jd, pid, flags)
            lon = (pos[0] - ayan) % 360
            speed = pos[3]
            sign_idx = int(lon / 30)
            nak_idx  = int(lon / (360/27))
            pada     = int((lon % (360/27)) / (360/27/4)) + 1
            planet_data[pname] = {
                "longitude": round(lon, 4),
                "sign": sign_idx, "sign_name": SIGNS[sign_idx],
                "nakshatra": nak_idx, "nakshatra_name": NAKSHATRAS[nak_idx],
                "pada": pada, "speed": round(speed, 6),
                "retrograde": speed < 0,
            }
        except Exception as e:
            pass

    # Ketu
    if 'Rahu' in planet_data:
        r_lon = planet_data['Rahu']['longitude']
        k_lon = (r_lon + 180) % 360
        sign_idx = int(k_lon / 30)
        nak_idx  = int(k_lon / (360/27))
        planet_data['Ketu'] = {
            "longitude": round(k_lon, 4),
            "sign": sign_idx, "sign_name": SIGNS[sign_idx],
            "nakshatra": nak_idx, "nakshatra_name": NAKSHATRAS[nak_idx],
            "pada": int((k_lon % (360/27)) / (360/27/4)) + 1,
            "speed": 0.0, "retrograde": False,
        }

    # Houses
    cusps, ascmc = swe.houses_ex(jd, NYSE_LAT, NYSE_LON, b'P', flags)
    asc = (ascmc[0] - ayan) % 360
    mc  = (ascmc[1] - ayan) % 360
    houses = {f"house_{i+1}": round((cusps[i] - ayan) % 360, 4) for i in range(12)}
    lagna_sign = int(asc / 30)

    # Moon nakshatra for Ghatak
    moon_nak = planet_data.get('Moon', {}).get('nakshatra', 0)

    natal = {
        "planets": planet_data,
        "houses": houses,
        "ascendant": round(asc, 4),
        "mc": round(mc, 4),
        "lagna_sign": lagna_sign,
        "jd": jd,
    }
    return natal, lagna_sign, moon_nak


def compute_bav_sav(natal_signs, lagna_sign):
    bav = {}
    for planet, table in ALL_BAV.items():
        scores = [0]*12
        for contrib, good_houses in table.items():
            contrib_sign = lagna_sign if contrib == 'Lagna' else natal_signs.get(contrib)
            if contrib_sign is None: continue
            for h in good_houses:
                scores[(contrib_sign + h - 1) % 12] += 1
        bav[planet] = scores
    sav = [sum(bav[p][i] for p in bav) for i in range(12)]
    return bav, sav


def compute_shadbala(natal_chart, lagna_sign):
    results = {}
    for pname, pdata in natal_chart['planets'].items():
        if pname in ['Rahu','Ketu','Uranus','Neptune','Pluto','Ketu']: continue
        lon   = pdata['longitude']
        sign  = pdata['sign']
        speed = pdata.get('speed', 1.0)
        # Sthana
        sthana = 0.0
        if pname in EXALTATION:
            d = abs(lon - EXALTATION[pname]) % 360
            d = min(d, 360-d)
            sthana += (180-d)/3.0
        if pname in OWN_SIGNS and sign in OWN_SIGNS[pname]: sthana += 30.0
        if pname in MOOLATRIKONA:
            mt_sign, mt_s, mt_e = MOOLATRIKONA[pname]
            if sign == mt_sign and mt_s <= (lon%30) <= mt_e: sthana += 45.0
        # Dig
        dig = 0.0
        if pname in DIG_BALA_HOUSES:
            strong = DIG_BALA_HOUSES[pname]
            house  = ((sign - lagna_sign) % 12) + 1
            dist   = abs(house - strong)
            if dist > 6: dist = 12 - dist
            dig = (6-dist)*10.0
        # Chesta
        if pname in ['Sun','Moon']:
            chesta = min(abs(speed)*10, 60.0)
        elif speed < 0:
            chesta = 60.0
        elif speed < 0.5:
            chesta = 45.0
        else:
            chesta = min(speed*15, 60.0)
        results[pname] = {"sthana_bala":round(sthana,2),"dig_bala":round(dig,2),"chesta_bala":round(chesta,2),"total_shadbala":round(sthana+dig+chesta,2)}
    return results


def compute_karakas(natal_chart):
    degs = [(p, natal_chart['planets'][p]['longitude']%30) for p in KARAKA_PLANETS if p in natal_chart['planets']]
    degs.sort(key=lambda x: x[1], reverse=True)
    karakas = {KARAKA_NAMES[i]: {"planet":p,"degree_in_sign":round(d,4)} for i,(p,d) in enumerate(degs) if i < len(KARAKA_NAMES)}
    if 'Rahu' in natal_chart['planets']:
        r_deg = 30 - (natal_chart['planets']['Rahu']['longitude']%30)
        karakas['RahuK'] = {"planet":"Rahu","degree_in_sign":round(r_deg,4)}
    return karakas


def compute_ghatak(moon_nak):
    g = GHATAK_TABLE[min(moon_nak//3, 8)]
    return {"bad_day":g["bad_day"],"bad_day_name":DAYS_OF_WEEK[g["bad_day"]],
            "bad_nakshatra":g["bad_nak"],"bad_nakshatra_name":NAKSHATRAS[g["bad_nak"]],
            "bad_rashi":g["bad_rashi"],"bad_rashi_name":SIGNS[g["bad_rashi"]],
            "bad_tithi":g["bad_tithi"],"bad_lagna":g["bad_lagna"],"bad_lagna_name":SIGNS[g["bad_lagna"]]}


def main():
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    # Check if sector_tags table exists for new entries
    c.execute("CREATE TABLE IF NOT EXISTS sector_tags (ticker TEXT PRIMARY KEY, sector TEXT, industry_group TEXT, industry TEXT, sub_industry TEXT)")

    for ticker, ipo_date, sector, description in NEW_TICKERS:
        # Skip if already exists
        existing = c.execute("SELECT COUNT(*) FROM stocks WHERE ticker=?", (ticker,)).fetchone()[0]
        if existing:
            print(f"  {ticker}: already in DB, skipping")
            continue

        print(f"  Computing natal for {ticker} ({ipo_date}) [{sector}]...")
        try:
            natal, lagna_sign, moon_nak = compute_natal_for_ticker(ipo_date)

            # Get moon nakshatra name and sign
            moon_data = natal['planets'].get('Moon', {})
            moon_nak_name = NAKSHATRAS[moon_nak] if moon_nak < 27 else 'Unknown'
            asc_deg = natal['ascendant']

            # Insert into stocks table
            c.execute("""INSERT INTO stocks (ticker, ipo_date, natal_chart_json, lagna_sign, moon_nakshatra, moon_nakshatra_name, ascendant_degree)
                         VALUES (?,?,?,?,?,?,?)""",
                      (ticker, ipo_date, json.dumps(natal), lagna_sign, moon_nak, moon_nak_name, asc_deg))

            # Insert into natal_planets
            for pname, pdata in natal['planets'].items():
                c.execute("""INSERT OR REPLACE INTO natal_planets (ticker, planet, longitude, sign, sign_name, nakshatra, nakshatra_name, pada)
                             VALUES (?,?,?,?,?,?,?,?)""",
                          (ticker, pname, pdata['longitude'], pdata['sign'], pdata['sign_name'],
                           pdata.get('nakshatra',0), pdata.get('nakshatra_name',''), pdata.get('pada',1)))

            # BAV/SAV
            natal_signs = {p: d['sign'] for p,d in natal['planets'].items()}
            bav, sav = compute_bav_sav(natal_signs, lagna_sign)
            for planet, scores in bav.items():
                c.execute("INSERT OR REPLACE INTO natal_bav VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (ticker, planet, *scores, sum(scores)))
            c.execute("INSERT OR REPLACE INTO natal_sav VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (ticker, *sav, sum(sav), json.dumps({"bav":{p:s for p,s in bav.items()},"sav":sav})))

            # Shadbala
            shadbala = compute_shadbala(natal, lagna_sign)
            for pname, scores in shadbala.items():
                c.execute("INSERT OR REPLACE INTO natal_shadbala VALUES (?,?,?,?,?,?)",
                          (ticker, pname, scores["sthana_bala"], scores["dig_bala"], scores["chesta_bala"], scores["total_shadbala"]))

            # Karakas
            karakas = compute_karakas(natal)
            for k_name, k_data in karakas.items():
                c.execute("INSERT OR REPLACE INTO natal_karakas VALUES (?,?,?,?)",
                          (ticker, k_name, k_data["planet"], k_data["degree_in_sign"]))

            # Ghatak
            ghatak = compute_ghatak(moon_nak)
            c.execute("INSERT OR REPLACE INTO natal_ghatak VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (ticker, ghatak["bad_day"], ghatak["bad_day_name"],
                       ghatak["bad_nakshatra"], ghatak["bad_nakshatra_name"],
                       ghatak["bad_rashi"], ghatak["bad_rashi_name"],
                       json.dumps(ghatak["bad_tithi"]),
                       ghatak["bad_lagna"], ghatak["bad_lagna_name"]))

            # sector_tags
            c.execute("INSERT OR REPLACE INTO sector_tags (ticker, sector, industry_group, industry, sub_industry) VALUES (?,?,?,?,?)",
                      (ticker, sector, sector, description, description))

            print(f"    -> ASC={SIGNS[lagna_sign]}, Moon={moon_nak_name}, SAV_total={sum(sav)}")

        except Exception as e:
            print(f"  {ticker}: ERROR — {e}")
            import traceback; traceback.print_exc()

    conn.commit()

    # Final count
    total = c.execute("SELECT count(*) FROM stocks").fetchone()[0]
    print(f"\nTotal tickers in DB: {total}")
    conn.close()


if __name__ == "__main__":
    main()
