"""
Fix #2: Compute and store Natal BAV/SAV Ashtakavarga tables for all 155 stocks.

BAV (Bhinnashtakavarga): Per-planet score for each of the 12 signs.
  - For each of 7 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn),
    compute which signs receive benefic points (bindus) based on the
    natal positions of all planets and Ascendant.
  - Each planet has a fixed lookup table of benefic-point-giving positions.

SAV (Sarvashtakavarga): Sum of all 7 BAV tables = 12 total scores.

Uses the classical Parashara Ashtakavarga point tables.

Output: New table natal_bav in stock_natal_charts.db
        + natal_sav table with 12 values per stock.
"""
import sqlite3
import json
import swisseph as swe

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

# ══════════════════════════════════════════════════════════════
# PARASHARA'S ASHTAKAVARGA BENEFIC POINT TABLES
# ══════════════════════════════════════════════════════════════
# For each planet, the dict maps a "contributor" (another planet or Lagna)
# to a list of houses (from that contributor) where the planet receives a bindu.
# House numbers are 1-based (1st, 2nd, ... 12th house from the contributor).

# SUN's BAV: who gives Sun a bindu and from which houses
SUN_BAV = {
    'Sun':     [1, 2, 4, 7, 8, 9, 10, 11],
    'Moon':    [3, 6, 10, 11],
    'Mars':    [1, 2, 4, 7, 8, 9, 10, 11],
    'Mercury': [3, 5, 6, 9, 10, 11, 12],
    'Jupiter': [5, 6, 9, 11],
    'Venus':   [6, 7, 12],
    'Saturn':  [1, 2, 4, 7, 8, 9, 10, 11],
    'Lagna':   [3, 4, 6, 10, 11, 12],
}

# MOON's BAV
MOON_BAV = {
    'Sun':     [3, 6, 7, 8, 10, 11],
    'Moon':    [1, 3, 6, 7, 10, 11],
    'Mars':    [2, 3, 5, 6, 9, 10, 11],
    'Mercury': [1, 3, 4, 5, 7, 8, 10, 11],
    'Jupiter': [1, 4, 7, 8, 10, 11, 12],
    'Venus':   [3, 4, 5, 7, 9, 10, 11],
    'Saturn':  [3, 5, 6, 11],
    'Lagna':   [3, 6, 10, 11],
}

# MARS's BAV
MARS_BAV = {
    'Sun':     [3, 5, 6, 10, 11],
    'Moon':    [3, 6, 11],
    'Mars':    [1, 2, 4, 7, 8, 10, 11],
    'Mercury': [3, 5, 6, 11],
    'Jupiter': [6, 10, 11, 12],
    'Venus':   [6, 8, 11, 12],
    'Saturn':  [1, 4, 7, 8, 9, 10, 11],
    'Lagna':   [1, 3, 6, 10, 11],
}

# MERCURY's BAV
MERCURY_BAV = {
    'Sun':     [5, 6, 9, 11, 12],
    'Moon':    [2, 4, 6, 8, 10, 11],
    'Mars':    [1, 2, 4, 7, 8, 9, 10, 11],
    'Mercury': [1, 3, 5, 6, 9, 10, 11, 12],
    'Jupiter': [6, 8, 11, 12],
    'Venus':   [1, 2, 3, 4, 5, 8, 9, 11],
    'Saturn':  [1, 2, 4, 7, 8, 9, 10, 11],
    'Lagna':   [1, 2, 4, 6, 8, 10, 11],
}

# JUPITER's BAV
JUPITER_BAV = {
    'Sun':     [1, 2, 3, 4, 7, 8, 9, 10, 11],
    'Moon':    [2, 5, 7, 9, 11],
    'Mars':    [1, 2, 4, 7, 8, 10, 11],
    'Mercury': [1, 2, 4, 5, 6, 9, 10, 11],
    'Jupiter': [1, 2, 3, 4, 7, 8, 10, 11],
    'Venus':   [2, 5, 6, 9, 10, 11],
    'Saturn':  [3, 5, 6, 12],
    'Lagna':   [1, 2, 4, 5, 6, 7, 9, 10, 11],
}

# VENUS's BAV
VENUS_BAV = {
    'Sun':     [8, 11, 12],
    'Moon':    [1, 2, 3, 4, 5, 8, 9, 11, 12],
    'Mars':    [3, 5, 6, 9, 11, 12],
    'Mercury': [3, 5, 6, 9, 11],
    'Jupiter': [5, 8, 9, 10, 11],
    'Venus':   [1, 2, 3, 4, 5, 8, 9, 10, 11],
    'Saturn':  [3, 4, 5, 8, 9, 10, 11],
    'Lagna':   [1, 2, 3, 4, 5, 8, 9, 11],
}

# SATURN's BAV
SATURN_BAV = {
    'Sun':     [1, 2, 4, 7, 8, 10, 11],
    'Moon':    [3, 6, 11],
    'Mars':    [3, 5, 6, 10, 11, 12],
    'Mercury': [6, 8, 9, 10, 11, 12],
    'Jupiter': [5, 6, 11, 12],
    'Venus':   [6, 11, 12],
    'Saturn':  [3, 5, 6, 11],
    'Lagna':   [1, 3, 4, 6, 10, 11],
}

ALL_BAV_TABLES = {
    'Sun': SUN_BAV,
    'Moon': MOON_BAV,
    'Mars': MARS_BAV,
    'Mercury': MERCURY_BAV,
    'Jupiter': JUPITER_BAV,
    'Venus': VENUS_BAV,
    'Saturn': SATURN_BAV,
}

# Planet name mapping (our DB uses full names)
PLANET_ALIASES = {
    'Mercury': 'Mercury', 'Merc': 'Mercury',
    'Jupiter': 'Jupiter', 'Jup': 'Jupiter',
    'Venus': 'Venus', 'Ven': 'Venus',
    'Saturn': 'Saturn', 'Sat': 'Saturn',
}


def compute_bav(natal_signs, lagna_sign):
    """
    Compute Bhinnashtakavarga for all 7 planets.
    
    Args:
        natal_signs: dict {planet_name: sign_index_0_11}
        lagna_sign: int 0-11 (Ascendant sign)
    
    Returns:
        dict {planet_name: [12 bindu scores, one per sign]}
    """
    bav = {}
    
    for planet, bav_table in ALL_BAV_TABLES.items():
        scores = [0] * 12  # One score per sign
        
        for contributor, good_houses in bav_table.items():
            if contributor == 'Lagna':
                contrib_sign = lagna_sign
            elif contributor in natal_signs:
                contrib_sign = natal_signs[contributor]
            else:
                continue
            
            # For each "good house" from this contributor,
            # the planet gets a bindu in the sign that is (house-1) signs ahead
            for house in good_houses:
                target_sign = (contrib_sign + house - 1) % 12
                scores[target_sign] += 1
        
        bav[planet] = scores
    
    return bav


def compute_sav(bav):
    """
    Compute Sarvashtakavarga by summing all 7 BAV tables.
    
    Args:
        bav: dict from compute_bav()
    
    Returns:
        list of 12 SAV scores
    """
    sav = [0] * 12
    for planet, scores in bav.items():
        for i in range(12):
            sav[i] += scores[i]
    return sav


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute("DROP TABLE IF EXISTS natal_bav")
    c.execute("DROP TABLE IF EXISTS natal_sav")
    c.execute("""
        CREATE TABLE natal_bav (
            ticker TEXT,
            planet TEXT,
            sign_0 INTEGER, sign_1 INTEGER, sign_2 INTEGER, sign_3 INTEGER,
            sign_4 INTEGER, sign_5 INTEGER, sign_6 INTEGER, sign_7 INTEGER,
            sign_8 INTEGER, sign_9 INTEGER, sign_10 INTEGER, sign_11 INTEGER,
            total_bindus INTEGER,
            PRIMARY KEY (ticker, planet)
        )
    """)
    c.execute("""
        CREATE TABLE natal_sav (
            ticker TEXT PRIMARY KEY,
            sign_0 INTEGER, sign_1 INTEGER, sign_2 INTEGER, sign_3 INTEGER,
            sign_4 INTEGER, sign_5 INTEGER, sign_6 INTEGER, sign_7 INTEGER,
            sign_8 INTEGER, sign_9 INTEGER, sign_10 INTEGER, sign_11 INTEGER,
            total INTEGER,
            sav_json TEXT
        )
    """)
    
    rows = c.execute("SELECT ticker, natal_chart_json, lagna_sign FROM stocks").fetchall()
    computed = 0
    errors = []
    
    for ticker, json_str, lagna_sign in rows:
        if not json_str:
            errors.append(f"{ticker}: no natal JSON")
            continue
        
        try:
            natal = json.loads(json_str)
            planets = natal.get("planets", {})
            
            # Get sign indices for all planets
            natal_signs = {}
            for p_name, p_data in planets.items():
                if isinstance(p_data, dict):
                    natal_signs[p_name] = p_data.get("sign", int(p_data.get("longitude", 0) / 30))
            
            # Compute ascendant sign
            asc_sign = lagna_sign if lagna_sign is not None else int(natal.get("ascendant", 0) / 30)
            
            # Compute BAV
            bav = compute_bav(natal_signs, asc_sign)
            
            # Store BAV
            for planet, scores in bav.items():
                total = sum(scores)
                c.execute(
                    "INSERT INTO natal_bav VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (ticker, planet, *scores, total)
                )
            
            # Compute SAV
            sav = compute_sav(bav)
            total_sav = sum(sav)
            c.execute(
                "INSERT INTO natal_sav VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ticker, *sav, total_sav, json.dumps({"bav": {p: s for p, s in bav.items()}, "sav": sav}))
            )
            
            computed += 1
            
        except Exception as e:
            errors.append(f"{ticker}: {e}")
    
    conn.commit()
    
    # Verify
    bav_count = c.execute("SELECT count(*) FROM natal_bav").fetchone()[0]
    sav_count = c.execute("SELECT count(*) FROM natal_sav").fetchone()[0]
    
    print(f"Computed BAV/SAV for {computed} stocks")
    print(f"BAV rows: {bav_count} (expected {computed * 7})")
    print(f"SAV rows: {sav_count}")
    
    # Show sample
    print("\nSample BAV for MSFT (Sun):")
    row = c.execute("SELECT * FROM natal_bav WHERE ticker='MSFT' AND planet='Sun'").fetchone()
    if row:
        print(f"  Signs 0-11: {row[2:14]}, total={row[14]}")
    
    print("\nSample SAV for MSFT:")
    row = c.execute("SELECT * FROM natal_sav WHERE ticker='MSFT'").fetchone()
    if row:
        print(f"  Signs 0-11: {row[1:13]}, total={row[13]}")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors[:5]:
            print(f"  {e}")
    
    conn.close()

if __name__ == "__main__":
    main()
