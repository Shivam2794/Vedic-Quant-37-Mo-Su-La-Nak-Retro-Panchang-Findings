"""
Fixes #4, #5, #6: Compute Simplified Shadbala, Natal Jaimini Karakas, and Ghatak table.
All results stored in stock_natal_charts.db.
"""
import sqlite3
import json
import math

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# ══════════════════════════════════════════════════════════════
# FIX #4: SIMPLIFIED SHADBALA (3 components)
# ══════════════════════════════════════════════════════════════

# Exaltation degrees (Parashara) — planet is strongest at this degree
EXALTATION = {
    'Sun': 10.0,       # 10° Aries
    'Moon': 33.0,      # 3° Taurus
    'Mars': 298.0,     # 28° Capricorn
    'Mercury': 165.0,  # 15° Virgo
    'Jupiter': 95.0,   # 5° Cancer
    'Venus': 357.0,    # 27° Pisces
    'Saturn': 200.0,   # 20° Libra
}

# Own signs
OWN_SIGNS = {
    'Sun': [4],           # Leo
    'Moon': [3],          # Cancer
    'Mars': [0, 7],       # Aries, Scorpio
    'Mercury': [2, 5],    # Gemini, Virgo
    'Jupiter': [8, 11],   # Sagittarius, Pisces
    'Venus': [1, 6],      # Taurus, Libra
    'Saturn': [9, 10],    # Capricorn, Aquarius
}

# Moolatrikona signs (and degree ranges)
MOOLATRIKONA = {
    'Sun': (4, 0, 20),       # Leo 0-20
    'Moon': (1, 4, 20),      # Taurus 4-20
    'Mars': (0, 0, 12),      # Aries 0-12
    'Mercury': (5, 16, 20),  # Virgo 16-20
    'Jupiter': (8, 0, 10),   # Sagittarius 0-10
    'Venus': (6, 0, 15),     # Libra 0-15
    'Saturn': (10, 0, 20),   # Aquarius 0-20
}

# Dig Bala: planet gets directional strength in this house
DIG_BALA_HOUSES = {
    'Sun': 10,      # Strong in 10th house
    'Moon': 4,      # Strong in 4th house
    'Mars': 10,     # Strong in 10th house
    'Mercury': 1,   # Strong in 1st house (Lagna)
    'Jupiter': 1,   # Strong in 1st house
    'Venus': 4,     # Strong in 4th house
    'Saturn': 7,    # Strong in 7th house
}


def compute_sthana_bala(longitude, planet_name):
    """Positional strength: exaltation/debilitation + own sign + moolatrikona."""
    score = 0.0
    sign = int(longitude / 30)
    deg_in_sign = longitude % 30

    # 1. Uchcha Bala (Exaltation strength): 0 to 60 shashtamsa
    if planet_name in EXALTATION:
        exalt_deg = EXALTATION[planet_name]
        dist = abs(longitude - exalt_deg) % 360
        dist = min(dist, 360 - dist)
        # Max at exaltation (dist=0), min at debilitation (dist=180)
        score += (180 - dist) / 3.0  # 0 to 60

    # 2. Own sign bonus
    if planet_name in OWN_SIGNS and sign in OWN_SIGNS[planet_name]:
        score += 30.0

    # 3. Moolatrikona bonus
    if planet_name in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet_name]
        if sign == mt_sign and mt_start <= deg_in_sign <= mt_end:
            score += 45.0

    # 4. Friend/enemy sign (simplified: benefics in benefic signs get +15)
    benefic_signs = {0, 3, 4, 8, 11}  # Aries, Cancer, Leo, Sagittarius, Pisces
    if planet_name in ['Jupiter', 'Venus', 'Mercury', 'Moon'] and sign in benefic_signs:
        score += 15.0

    return score


def compute_dig_bala(planet_name, planet_sign, lagna_sign):
    """Directional strength based on house placement."""
    if planet_name not in DIG_BALA_HOUSES:
        return 0.0

    strong_house = DIG_BALA_HOUSES[planet_name]
    # Planet's house from lagna
    house = ((planet_sign - lagna_sign) % 12) + 1

    # Max strength at the strong house, min at 7th from it
    dist = abs(house - strong_house)
    if dist > 6:
        dist = 12 - dist
    return (6 - dist) * 10.0  # 0 to 60


def compute_chesta_bala(speed, planet_name):
    """Motional strength: retrograde planets and slow planets get different scores."""
    if planet_name in ['Sun', 'Moon']:
        # Sun and Moon never retrograde; speed is always relevant
        return min(abs(speed) * 10, 60.0)

    if speed < 0:
        # Retrograde: high chesta bala (planet is fighting against natural motion)
        return 60.0
    elif speed < 0.5:
        # Very slow: moderate-high
        return 45.0
    else:
        # Normal speed
        return min(speed * 15, 60.0)


def compute_simplified_shadbala(natal_chart):
    """Compute 3-component Shadbala for all planets."""
    planets = natal_chart.get("planets", {})
    lagna_sign = int(natal_chart.get("ascendant", 0) / 30)
    results = {}

    for p_name, p_data in planets.items():
        if p_name in ['Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto']:
            continue  # Shadbala is for 7 classical planets only

        lon = p_data.get("longitude", 0)
        sign = p_data.get("sign", int(lon / 30))
        speed = p_data.get("speed", 1.0)

        sthana = compute_sthana_bala(lon, p_name)
        dig = compute_dig_bala(p_name, sign, lagna_sign)
        chesta = compute_chesta_bala(speed, p_name)
        total = sthana + dig + chesta

        results[p_name] = {
            "sthana_bala": round(sthana, 2),
            "dig_bala": round(dig, 2),
            "chesta_bala": round(chesta, 2),
            "total_shadbala": round(total, 2),
        }

    return results


# ══════════════════════════════════════════════════════════════
# FIX #5: NATAL JAIMINI CHARA KARAKAS
# ══════════════════════════════════════════════════════════════

KARAKA_NAMES = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
KARAKA_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]


def compute_jaimini_karakas(natal_chart):
    """Compute Chara Karakas based on degree in sign (highest = Atmakaraka)."""
    planets = natal_chart.get("planets", {})
    degrees = []

    for p_name in KARAKA_PLANETS:
        if p_name in planets:
            lon = planets[p_name].get("longitude", 0)
            deg_in_sign = lon % 30
            # Enforce Retrograde Inversion for Rahu
            if p_name == "Rahu":
                deg_in_sign = 30.0 - deg_in_sign
            degrees.append((p_name, deg_in_sign))

    # Sort by degree descending: highest degree = Atmakaraka
    degrees.sort(key=lambda x: x[1], reverse=True)

    karakas = {}
    for i, (p_name, deg) in enumerate(degrees):
        if i < len(KARAKA_NAMES):
            karakas[KARAKA_NAMES[i]] = {
                "planet": p_name,
                "degree_in_sign": round(deg, 4),
            }

    return karakas


# ══════════════════════════════════════════════════════════════
# FIX #6: GHATAK (DANGER DAY) TABLE
# ══════════════════════════════════════════════════════════════
# Based on Janma Nakshatra (natal Moon nakshatra), determine
# the "bad" day, nakshatra, rashi, tithi, yoga, karana, and lagna.

# Ghatak lookup table indexed by Janma Nakshatra group (1-9)
# Each group of 3 nakshatras shares the same Ghatak values
GHATAK_TABLE = {
    # Group: (bad_vaara, bad_nakshatra_idx, bad_rashi_idx, bad_tithi_group, bad_lagna_idx)
    # Nakshatras 0,1,2 (Ashwini, Bharani, Krittika)
    0: {"bad_day": 6, "bad_nak": 18, "bad_rashi": 4, "bad_tithi": [2, 7, 12], "bad_lagna": 6},
    # Nakshatras 3,4,5 (Rohini, Mrigashira, Ardra)
    1: {"bad_day": 3, "bad_nak": 21, "bad_rashi": 5, "bad_tithi": [1, 6, 11], "bad_lagna": 7},
    # Nakshatras 6,7,8 (Punarvasu, Pushya, Ashlesha)
    2: {"bad_day": 0, "bad_nak": 24, "bad_rashi": 6, "bad_tithi": [5, 10, 15], "bad_lagna": 8},
    # Nakshatras 9,10,11 (Magha, P.Phalguni, U.Phalguni)
    3: {"bad_day": 4, "bad_nak": 0, "bad_rashi": 7, "bad_tithi": [4, 9, 14], "bad_lagna": 9},
    # Nakshatras 12,13,14 (Hasta, Chitra, Swati)
    4: {"bad_day": 1, "bad_nak": 3, "bad_rashi": 8, "bad_tithi": [3, 8, 13], "bad_lagna": 10},
    # Nakshatras 15,16,17 (Vishakha, Anuradha, Jyeshtha)
    5: {"bad_day": 5, "bad_nak": 6, "bad_rashi": 9, "bad_tithi": [2, 7, 12], "bad_lagna": 11},
    # Nakshatras 18,19,20 (Moola, P.Ashadha, U.Ashadha)
    6: {"bad_day": 2, "bad_nak": 9, "bad_rashi": 10, "bad_tithi": [1, 6, 11], "bad_lagna": 0},
    # Nakshatras 21,22,23 (Shravana, Dhanishta, Shatabhisha)
    7: {"bad_day": 6, "bad_nak": 12, "bad_rashi": 11, "bad_tithi": [5, 10, 15], "bad_lagna": 1},
    # Nakshatras 24,25,26 (P.Bhadra, U.Bhadra, Revati)
    8: {"bad_day": 3, "bad_nak": 15, "bad_rashi": 0, "bad_tithi": [4, 9, 14], "bad_lagna": 2},
}

DAYS_OF_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Moola','P.Ashadha','U.Ashadha','Shravana','Dhanishta',
    'Shatabhisha','P.Bhadra','U.Bhadra','Revati'
]


def compute_ghatak(moon_nakshatra_idx):
    """Compute Ghatak (danger) parameters from Janma Nakshatra."""
    group = moon_nakshatra_idx // 3
    if group > 8:
        group = 8

    g = GHATAK_TABLE[group]
    return {
        "bad_day": g["bad_day"],
        "bad_day_name": DAYS_OF_WEEK[g["bad_day"]],
        "bad_nakshatra": g["bad_nak"],
        "bad_nakshatra_name": NAKSHATRAS[g["bad_nak"]],
        "bad_rashi": g["bad_rashi"],
        "bad_rashi_name": SIGNS[g["bad_rashi"]],
        "bad_tithi": g["bad_tithi"],
        "bad_lagna": g["bad_lagna"],
        "bad_lagna_name": SIGNS[g["bad_lagna"]],
    }


# ══════════════════════════════════════════════════════════════
# MAIN: Run all three fixes
# ══════════════════════════════════════════════════════════════

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create tables
    c.execute("DROP TABLE IF EXISTS natal_shadbala")
    c.execute("DROP TABLE IF EXISTS natal_karakas")
    c.execute("DROP TABLE IF EXISTS natal_ghatak")

    c.execute("""
        CREATE TABLE natal_shadbala (
            ticker TEXT,
            planet TEXT,
            sthana_bala REAL,
            dig_bala REAL,
            chesta_bala REAL,
            total_shadbala REAL,
            PRIMARY KEY (ticker, planet)
        )
    """)

    c.execute("""
        CREATE TABLE natal_karakas (
            ticker TEXT,
            karaka TEXT,
            planet TEXT,
            degree_in_sign REAL,
            PRIMARY KEY (ticker, karaka)
        )
    """)

    c.execute("""
        CREATE TABLE natal_ghatak (
            ticker TEXT PRIMARY KEY,
            bad_day INTEGER,
            bad_day_name TEXT,
            bad_nakshatra INTEGER,
            bad_nakshatra_name TEXT,
            bad_rashi INTEGER,
            bad_rashi_name TEXT,
            bad_tithi_json TEXT,
            bad_lagna INTEGER,
            bad_lagna_name TEXT
        )
    """)

    rows = c.execute("SELECT ticker, natal_chart_json, moon_nakshatra FROM stocks").fetchall()
    sb_count = 0
    kk_count = 0
    gh_count = 0
    errors = []

    for ticker, json_str, moon_nak in rows:
        if not json_str:
            errors.append(f"{ticker}: no natal JSON")
            continue

        try:
            natal = json.loads(json_str)

            # Fix #4: Shadbala
            shadbala = compute_simplified_shadbala(natal)
            for p_name, scores in shadbala.items():
                c.execute("INSERT INTO natal_shadbala VALUES (?,?,?,?,?,?)",
                          (ticker, p_name, scores["sthana_bala"], scores["dig_bala"],
                           scores["chesta_bala"], scores["total_shadbala"]))
            sb_count += 1

            # Fix #5: Karakas
            karakas = compute_jaimini_karakas(natal)
            for k_name, k_data in karakas.items():
                c.execute("INSERT INTO natal_karakas VALUES (?,?,?,?)",
                          (ticker, k_name, k_data["planet"], k_data["degree_in_sign"]))
            kk_count += 1

            # Fix #6: Ghatak
            if moon_nak is not None:
                ghatak = compute_ghatak(int(moon_nak))
                c.execute("INSERT INTO natal_ghatak VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (ticker, ghatak["bad_day"], ghatak["bad_day_name"],
                           ghatak["bad_nakshatra"], ghatak["bad_nakshatra_name"],
                           ghatak["bad_rashi"], ghatak["bad_rashi_name"],
                           json.dumps(ghatak["bad_tithi"]),
                           ghatak["bad_lagna"], ghatak["bad_lagna_name"]))
                gh_count += 1

        except Exception as e:
            errors.append(f"{ticker}: {e}")

    conn.commit()

    # Verify
    print(f"Shadbala computed: {sb_count} stocks, {c.execute('SELECT count(*) FROM natal_shadbala').fetchone()[0]} rows")
    print(f"Karakas computed: {kk_count} stocks, {c.execute('SELECT count(*) FROM natal_karakas').fetchone()[0]} rows")
    print(f"Ghatak computed: {gh_count} stocks")

    # Samples
    print("\nSample Shadbala (MSFT):")
    for row in c.execute("SELECT * FROM natal_shadbala WHERE ticker='MSFT' ORDER BY total_shadbala DESC"):
        print(f"  {row[1]:10s}  Sthana={row[2]:6.1f}  Dig={row[3]:5.1f}  Chesta={row[4]:5.1f}  TOTAL={row[5]:6.1f}")

    print("\nSample Karakas (MSFT):")
    for row in c.execute("SELECT * FROM natal_karakas WHERE ticker='MSFT'"):
        print(f"  {row[1]:5s} = {row[2]:10s} ({row[3]:.2f}°)")

    print("\nSample Ghatak (MSFT):")
    row = c.execute("SELECT * FROM natal_ghatak WHERE ticker='MSFT'").fetchone()
    if row:
        print(f"  Bad day: {row[2]}, Bad nakshatra: {row[4]}, Bad rashi: {row[6]}, Bad lagna: {row[9]}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors[:5]:
            print(f"  {e}")

    conn.close()


if __name__ == "__main__":
    main()
