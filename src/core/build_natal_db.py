"""
Stock Natal Chart Database Builder
===================================
1. Gets S&P 500 tickers from Wikipedia
2. Scrapes earliest trading date via yfinance (proxy for IPO date)
3. Computes full Vedic natal chart for each stock at market open (9:30 AM ET)
4. Computes Vimshottari Dasha periods for each stock
5. Stores everything in SQLite

Output: stock_natal_charts.db
"""
import json
import os
import sqlite3
import time
import math
from datetime import datetime, timezone, timedelta
import numpy as np

try:
    import yfinance as yf
    import swisseph as swe
    import pandas as pd
except ImportError as e:
    print(f"Missing: {e}. Run: pip install yfinance pyswisseph pandas")
    exit(1)

# ─── Config ───
DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
swe.set_sid_mode(swe.SIDM_LAHIRI)

# NYSE coordinates (birth location for all US stocks)
NYSE_LAT, NYSE_LON = 40.7128, -74.0060
MARKET_OPEN_ET = 9.5  # 9:30 AM ET = 9.5 hours
ET_TO_UTC_OFFSET = 5  # EST = UTC-5 (standard); EDT = UTC-4

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAKSHATRAS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','P.Phalguni','U.Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Moola','P.Ashadha','U.Ashadha','Shravana','Dhanishta',
    'Shatabhisha','P.Bhadra','U.Bhadra','Revati'
]
VIM_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIM_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Total = 120 years
VIM_DAYS = [y * 365.25636042 for y in VIM_YEARS]

BODIES = [
    (swe.SUN, "Sun"), (swe.MOON, "Moon"), (swe.MERCURY, "Mercury"),
    (swe.VENUS, "Venus"), (swe.MARS, "Mars"), (swe.JUPITER, "Jupiter"),
    (swe.SATURN, "Saturn"), (swe.URANUS, "Uranus"), (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO, "Pluto"),
]


def get_sp500_tickers():
    """Get S&P 500 tickers from Wikipedia."""
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Clean tickers (replace . with -)
        tickers = [t.replace('.', '-') for t in tickers]
        print(f"  Retrieved {len(tickers)} S&P 500 tickers")
        return tickers
    except Exception as e:
        print(f"  Wikipedia scrape failed: {e}")
        # Fallback: top 100 by market cap
        return _fallback_tickers()


def _fallback_tickers():
    """Hardcoded top 100 tickers as fallback."""
    return [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","BRK-B","LLY","UNH",
        "V","JPM","XOM","MA","JNJ","AVGO","PG","HD","COST","MRK",
        "ABBV","ADBE","CRM","AMD","CVX","NFLX","KO","PEP","TMO","WMT",
        "ACN","LIN","MCD","CSCO","ABT","DHR","ORCL","INTC","QCOM","TXN",
        "AMGN","PM","UNP","IBM","INTU","GE","CAT","LOW","BA","HON",
        "SPGI","AMAT","GS","BLK","NOW","ADP","SBUX","ISRG","RTX","MS",
        "PLD","MDLZ","BKNG","DE","GILD","VRTX","ADI","SYK","REGN","MMC",
        "PGR","ZTS","LRCX","CB","CI","BDX","KLAC","SO","DUK","SHW",
        "CME","MO","SNPS","CL","ICE","CDNS","FI","MCK","EOG","APD",
        "WM","NOC","PYPL","ORLY","GD","ITW","TGT","SLB","CTAS","EMR",
    ]


def get_listing_date(ticker):
    """Get the verified trading date for a stock."""
    csv_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\verified_ipo_dates.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, index_col="Ticker")
            if ticker in df.index:
                return str(df.loc[ticker, "IPO_Date"])
        except Exception:
            pass

    # Fallback to yfinance with a loud warning
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="max", interval="1d")
        if hist.empty:
            return None
        first_date = hist.index[0].strftime("%Y-%m-%d")
        print(f"  [WARNING] Using unverified yfinance date for {ticker}: {first_date}")
        return first_date
    except Exception:
        return None


def compute_natal_chart(ipo_date_str):
    """Compute full Vedic natal chart for a stock."""
    parts = ipo_date_str.split("-")
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

    # Historical market open logic
    dt = datetime(year, month, day)
    
    # 1. Determine Market Open Time (ET)
    # Pre-1985-09-30: 10:00 AM. Post: 9:30 AM
    if dt < datetime(1985, 9, 30):
        market_open_et_hour = 10.0
    else:
        market_open_et_hour = 9.5
        
    # 2. Correctly convert ET to UTC based on historical daylight saving
    ts = pd.Timestamp(year, month, day, int(market_open_et_hour), int((market_open_et_hour % 1) * 60))
    ts = ts.tz_localize("America/New_York").tz_convert("UTC")
    
    # In case the UTC conversion shifts the day, we still use the UTC hour component 
    # and the original JD base plus the exact UTC hour fraction.
    utc_hour = ts.hour + ts.minute / 60.0
    jd = swe.julday(ts.year, ts.month, ts.day, utc_hour)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH

    natal = {"jd": jd, "date": ipo_date_str, "planets": {}}

    for pid, name in BODIES:
        result = swe.calc_ut(jd, pid, flags)
        lon = result[0][0]
        speed = result[0][3]
        natal["planets"][name] = {
            "longitude": round(lon, 4),
            "sign": int(lon / 30),
            "sign_name": SIGNS[int(lon / 30)],
            "degree_in_sign": round(lon % 30, 4),
            "nakshatra": int(lon / (360 / 27)),
            "nakshatra_name": NAKSHATRAS[int(lon / (360 / 27))],
            "pada": int((lon % (360 / 27)) / (360 / 108)) + 1,
            "speed": round(speed, 6),
            "retrograde": speed < 0,
        }

    # Rahu
    rahu_result = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    rahu_lon = rahu_result[0][0]
    natal["planets"]["Rahu"] = {
        "longitude": round(rahu_lon, 4),
        "sign": int(rahu_lon / 30),
        "sign_name": SIGNS[int(rahu_lon / 30)],
        "nakshatra": int(rahu_lon / (360 / 27)),
        "nakshatra_name": NAKSHATRAS[int(rahu_lon / (360 / 27))],
    }
    # Ketu
    ketu_lon = (rahu_lon + 180) % 360
    natal["planets"]["Ketu"] = {
        "longitude": round(ketu_lon, 4),
        "sign": int(ketu_lon / 30),
        "sign_name": SIGNS[int(ketu_lon / 30)],
        "nakshatra": int(ketu_lon / (360 / 27)),
        "nakshatra_name": NAKSHATRAS[int(ketu_lon / (360 / 27))],
    }

    # House cusps (Placidus)
    try:
        cusps, ascmc = swe.houses_ex(jd, NYSE_LAT, NYSE_LON, b'P', flags)
        natal["houses"] = {f"house_{i+1}": round(cusps[i], 4) for i in range(12)}
        natal["ascendant"] = round(ascmc[0], 4)
        natal["mc"] = round(ascmc[1], 4)
    except Exception:
        natal["houses"] = {}
        natal["ascendant"] = 0.0

    # Lagna (ascendant) sign
    natal["lagna_sign"] = int(natal.get("ascendant", 0) / 30)

    # Moon nakshatra (for Vimshottari)
    moon_lon = natal["planets"]["Moon"]["longitude"]
    natal["moon_nakshatra"] = int(moon_lon / (360 / 27))
    natal["moon_nakshatra_name"] = NAKSHATRAS[natal["moon_nakshatra"]]

    # Navamsha (D9) positions
    natal["d9"] = {}
    for p_name, p_data in natal["planets"].items():
        lon = p_data["longitude"]
        d9_sign = (int(lon / 30) * 9 + int((lon % 30) * 9 / 30)) % 12
        natal["d9"][p_name] = {"sign": d9_sign, "sign_name": SIGNS[d9_sign]}

    return natal


def compute_vimshottari_dasha(natal_chart, current_date_str=None):
    """Compute the current Vimshottari Dasha state for a stock."""
    moon_nak = natal_chart["moon_nakshatra"]
    ipo_date = natal_chart["date"]

    # Starting dasha lord based on Moon's nakshatra
    starting_lord_idx = moon_nak % 9

    # Moon's position within nakshatra determines elapsed portion of first dasha
    moon_lon = natal_chart["planets"]["Moon"]["longitude"]
    nak_start = moon_nak * (360 / 27)
    nak_size = 360 / 27
    elapsed_fraction = (moon_lon - nak_start) / nak_size

    # Days elapsed in the first dasha at birth
    first_dasha_total = VIM_DAYS[starting_lord_idx]
    first_dasha_elapsed = elapsed_fraction * first_dasha_total

    # IPO date
    ipo_parts = ipo_date.split("-")
    ipo_dt = datetime(int(ipo_parts[0]), int(ipo_parts[1]), int(ipo_parts[2]))

    # Current date
    if current_date_str:
        cur_parts = current_date_str.split("-")
        cur_dt = datetime(int(cur_parts[0]), int(cur_parts[1]), int(cur_parts[2]))
    else:
        cur_dt = datetime.now()

    days_since_ipo = (cur_dt - ipo_dt).days

    # Walk through dasha periods
    total_cycle_days = sum(VIM_DAYS)  # 120 years
    days_in_cycle = (days_since_ipo + first_dasha_elapsed) % total_cycle_days

    cumulative = 0
    mahadasha_lord_idx = starting_lord_idx
    mahadasha_lord = ""
    mahadasha_elapsed_pct = 0
    antardasha_lord = ""
    antardasha_elapsed_pct = 0

    for i in range(9):
        lord_idx = (starting_lord_idx + i) % 9
        period_days = VIM_DAYS[lord_idx]
        if cumulative + period_days > days_in_cycle:
            mahadasha_lord_idx = lord_idx
            mahadasha_lord = VIM_LORDS[lord_idx]
            mahadasha_elapsed_pct = (days_in_cycle - cumulative) / period_days
            days_into_maha = days_in_cycle - cumulative

            # Antardasha calculation
            ad_cumulative = 0
            for j in range(9):
                ad_lord_idx = (lord_idx + j) % 9
                ad_period = period_days * VIM_DAYS[ad_lord_idx] / total_cycle_days
                if ad_cumulative + ad_period > days_into_maha:
                    antardasha_lord = VIM_LORDS[ad_lord_idx]
                    antardasha_elapsed_pct = (days_into_maha - ad_cumulative) / ad_period
                    break
                ad_cumulative += ad_period
            break
        cumulative += period_days

    return {
        "mahadasha_lord": mahadasha_lord,
        "mahadasha_lord_idx": mahadasha_lord_idx,
        "mahadasha_elapsed_pct": round(mahadasha_elapsed_pct, 4),
        "antardasha_lord": antardasha_lord,
        "antardasha_elapsed_pct": round(antardasha_elapsed_pct, 4),
    }


def create_db():
    """Create the natal charts SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS stocks;
        DROP TABLE IF EXISTS natal_planets;
        DROP TABLE IF EXISTS natal_houses;

        CREATE TABLE stocks (
            ticker TEXT PRIMARY KEY,
            ipo_date TEXT,
            natal_chart_json TEXT,
            lagna_sign INTEGER,
            moon_nakshatra INTEGER,
            moon_nakshatra_name TEXT,
            ascendant_degree REAL,
            current_mahadasha TEXT,
            current_antardasha TEXT
        );

        CREATE TABLE natal_planets (
            ticker TEXT,
            planet TEXT,
            longitude REAL,
            sign INTEGER,
            sign_name TEXT,
            nakshatra INTEGER,
            nakshatra_name TEXT,
            pada INTEGER,
            speed REAL,
            retrograde BOOLEAN,
            d9_sign INTEGER,
            PRIMARY KEY (ticker, planet)
        );
    """)
    conn.commit()
    return conn


def main():
    print("=" * 60)
    print("STOCK NATAL CHART DATABASE BUILDER")
    print("=" * 60)

    conn = create_db()
    c = conn.cursor()

    # Get tickers
    print("\nStep 1: Getting S&P 500 tickers...")
    tickers = get_sp500_tickers()

    # Scrape listing dates
    print(f"\nStep 2: Scraping listing dates for {len(tickers)} stocks...")
    print("  (This will take a few minutes...)")

    success = 0
    failed = []
    batch_size = 10

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        for ticker in batch:
            ipo_date = get_listing_date(ticker)
            if not ipo_date:
                failed.append(ticker)
                continue

            # Compute natal chart
            try:
                natal = compute_natal_chart(ipo_date)
                dasha = compute_vimshottari_dasha(natal)

                # Store in DB
                c.execute("""
                    INSERT OR REPLACE INTO stocks 
                    (ticker, ipo_date, natal_chart_json, lagna_sign, moon_nakshatra,
                     moon_nakshatra_name, ascendant_degree, current_mahadasha, current_antardasha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticker, ipo_date, json.dumps(natal),
                    natal.get("lagna_sign", 0),
                    natal.get("moon_nakshatra", 0),
                    natal.get("moon_nakshatra_name", ""),
                    natal.get("ascendant", 0.0),
                    dasha["mahadasha_lord"],
                    dasha["antardasha_lord"],
                ))

                # Store natal planets
                for p_name, p_data in natal["planets"].items():
                    d9_sign = natal.get("d9", {}).get(p_name, {}).get("sign", 0)
                    c.execute("""
                        INSERT OR REPLACE INTO natal_planets
                        (ticker, planet, longitude, sign, sign_name, nakshatra, 
                         nakshatra_name, pada, speed, retrograde, d9_sign)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticker, p_name,
                        p_data.get("longitude", 0),
                        p_data.get("sign", 0),
                        p_data.get("sign_name", ""),
                        p_data.get("nakshatra", 0),
                        p_data.get("nakshatra_name", ""),
                        p_data.get("pada", 0),
                        p_data.get("speed", 0),
                        p_data.get("retrograde", False),
                        d9_sign,
                    ))

                success += 1
            except Exception as e:
                failed.append(f"{ticker}:{e}")

        conn.commit()
        pct = min(100, 100 * (i + batch_size) / len(tickers))
        print(f"  Progress: {pct:.0f}% ({success} processed, {len(failed)} failed)")
        time.sleep(0.5)  # Rate limit

    conn.commit()

    # Summary
    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"  Stocks processed: {success}")
    print(f"  Failed: {len(failed)}")
    if failed[:10]:
        print(f"  Failed samples: {failed[:10]}")

    # Show sample natal charts
    print(f"\n  SAMPLE NATAL CHARTS:")
    for row in c.execute("""
        SELECT ticker, ipo_date, moon_nakshatra_name, current_mahadasha, current_antardasha 
        FROM stocks ORDER BY ipo_date LIMIT 10
    """):
        print(f"    {row[0]:6s} IPO={row[1]}  Moon={row[2]:15s}  Dasha={row[3]}/{row[4]}")

    print(f"\n  Database: {DB_PATH}")
    print(f"  Size: {os.path.getsize(DB_PATH) / 1024 / 1024:.1f} MB")
    conn.close()


if __name__ == "__main__":
    main()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
