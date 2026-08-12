"""
Fix #1: Repair 86 stocks with missing house cusps in natal_chart_json.
Re-computes Placidus house cusps for all stocks and updates the JSON blob.
Does NOT touch the natal_planets table or any other data.
"""
import sqlite3
import json
import swisseph as swe
import pandas as pd

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
NYSE_LAT, NYSE_LON = 40.7128, -74.0060

swe.set_sid_mode(swe.SIDM_LAHIRI)

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    rows = c.execute("SELECT ticker, ipo_date, natal_chart_json FROM stocks").fetchall()
    fixed = 0
    already_ok = 0
    errors = []

    for ticker, ipo_date, json_str in rows:
        if not json_str or not ipo_date:
            errors.append(f"{ticker}: missing json or ipo_date")
            continue

        natal = json.loads(json_str)
        houses = natal.get("houses", {})

        # Check if houses already present and complete
        if isinstance(houses, dict) and len(houses) >= 12:
            already_ok += 1
            continue

        # Recompute house cusps from IPO date
        try:
            parts = ipo_date.split("-")
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

            # Historical market open logic (same as build_natal_db.py)
            from datetime import datetime
            dt = datetime(year, month, day)
            if dt < datetime(1985, 9, 30):
                market_open_et_hour = 10.0
            else:
                market_open_et_hour = 9.5

            ts = pd.Timestamp(year, month, day, int(market_open_et_hour),
                              int((market_open_et_hour % 1) * 60))
            ts = ts.tz_localize("America/New_York").tz_convert("UTC")
            utc_hour = ts.hour + ts.minute / 60.0
            jd = swe.julday(ts.year, ts.month, ts.day, utc_hour)

            flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
            cusps, ascmc = swe.houses_ex(jd, NYSE_LAT, NYSE_LON, b'P', flags)

            natal["houses"] = {f"house_{i+1}": round(cusps[i], 4) for i in range(12)}
            natal["ascendant"] = round(ascmc[0], 4)
            natal["mc"] = round(ascmc[1], 4)
            natal["lagna_sign"] = int(ascmc[0] / 30)

            # Also compute D9 if missing
            if "d9" not in natal or not natal["d9"]:
                natal["d9"] = {}
                for p_name, p_data in natal.get("planets", {}).items():
                    lon = p_data.get("longitude", 0)
                    d9_sign = (int(lon / 30) * 9 + int((lon % 30) * 9 / 30)) % 12
                    SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
                             'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
                    natal["d9"][p_name] = {"sign": d9_sign, "sign_name": SIGNS[d9_sign]}

            # Update DB
            c.execute("UPDATE stocks SET natal_chart_json=?, ascendant_degree=?, lagna_sign=? WHERE ticker=?",
                      (json.dumps(natal), ascmc[0], int(ascmc[0] / 30), ticker))
            fixed += 1

        except Exception as e:
            errors.append(f"{ticker}: {e}")

    conn.commit()
    conn.close()

    print(f"Already OK: {already_ok}")
    print(f"Fixed: {fixed}")
    print(f"Errors: {len(errors)}")
    for e in errors[:10]:
        print(f"  {e}")

if __name__ == "__main__":
    main()
