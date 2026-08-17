"""
Phase 6A (Patch): Add missed top stocks + fix SQ/FI ticker issues
"""
import yfinance as yf
import sqlite3
import json
import os
import time
import swisseph as swe

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

# Stocks that were excluded but are top names the user wants
MISSED_TICKERS = [
    "APP",   # AppLovin - top performer, Application Software
    "HOOD",  # Robinhood - Investment Banking & Brokerage
    "HWM",   # Howmet Aerospace - Aerospace & Defense
    "CPNG",  # Coupang - Broadline Retail
    "TOST",  # Toast - Transaction & Payment Processing
    "AFRM",  # Affirm - Transaction & Payment Processing
    "GO",    # Grocery Outlet - Food Retail
    "CPAY",  # Corpay (formerly FleetCor) - Transaction & Payment Processing
    "DOX",   # Amdocs - IT Consulting
    "SNDR",  # Schneider National - Cargo Ground Transportation
    "ARCB",  # ArcBest - Cargo Ground Transportation
    "CARG",  # CarGurus - Interactive Media
    "SQ",    # Block Inc (was Square) - Payments
    "FI",    # Fiserv - Payments (may need FISV fallback)
]

MISSED_GICS = {
    "APP": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "HOOD": ("Financials", "Capital Markets", "Capital Markets", "Investment Banking & Brokerage"),
    "HWM": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "CPNG": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "TOST": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "AFRM": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "GO": ("Consumer Staples", "Consumer Staples Distribution", "Food Retail", "Food Retail"),
    "CPAY": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "DOX": ("Information Technology", "Software & Services", "IT Services", "IT Consulting & Other Services"),
    "SNDR": ("Industrials", "Transportation", "Ground Transportation", "Cargo Ground Transportation"),
    "ARCB": ("Industrials", "Transportation", "Ground Transportation", "Cargo Ground Transportation"),
    "CARG": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "SQ": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "FI": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni", "U.Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "P.Ashadha", "U.Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "P.Bhadra", "U.Bhadra", "Revati"
]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def compute_natal_chart(date_str):
    from datetime import datetime
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    jd = swe.julday(dt.year, dt.month, dt.day, 14.5)
    
    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
    }
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)
    
    planets_data = {}
    for name, pid in planet_ids.items():
        pos = swe.calc_ut(jd, pid)
        lon = (pos[0][0] - ayanamsa) % 360
        speed = pos[0][3]
        sign_idx = int(lon / 30)
        nak_idx = int(lon / (360/27))
        pada = int((lon % (360/27)) / (360/108)) + 1
        planets_data[name] = {
            "longitude": round(lon, 4), "sign": sign_idx, "sign_name": SIGNS[sign_idx],
            "degree_in_sign": round(lon % 30, 4), "nakshatra": nak_idx,
            "nakshatra_name": NAKSHATRAS[nak_idx], "pada": pada,
            "speed": round(speed, 6), "retrograde": speed < 0
        }
    
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = (rahu_pos[0][0] - ayanamsa) % 360
    ketu_lon = (rahu_lon + 180) % 360
    planets_data["Rahu"] = {"longitude": round(rahu_lon, 4), "sign": int(rahu_lon/30), "sign_name": SIGNS[int(rahu_lon/30)], "nakshatra": int(rahu_lon/(360/27)), "nakshatra_name": NAKSHATRAS[int(rahu_lon/(360/27))]}
    planets_data["Ketu"] = {"longitude": round(ketu_lon, 4), "sign": int(ketu_lon/30), "sign_name": SIGNS[int(ketu_lon/30)], "nakshatra": int(ketu_lon/(360/27)), "nakshatra_name": NAKSHATRAS[int(ketu_lon/(360/27))]}
    
    houses = swe.houses(jd, 40.7128, -74.0060, b'P')
    asc = round((houses[1][0] - ayanamsa) % 360, 4)
    lagna_sign = int(asc / 30)
    moon_nak = planets_data["Moon"]["nakshatra"]
    moon_nak_name = planets_data["Moon"]["nakshatra_name"]
    dasha_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_lord = dasha_lords[moon_nak % 9]
    bhukti_lord = dasha_lords[(moon_nak + 1) % 9]
    
    chart_json = json.dumps({"jd": jd, "date": date_str, "planets": planets_data, "ascendant": asc, "mc": round((houses[1][1] - ayanamsa) % 360, 4), "lagna_sign": lagna_sign, "moon_nakshatra": moon_nak, "moon_nakshatra_name": moon_nak_name})
    return chart_json, lagna_sign, moon_nak, moon_nak_name, asc, dasha_lord, bhukti_lord, planets_data

def main():
    print("=" * 60, flush=True)
    print("PHASE 6A PATCH: Adding Missed Top Stocks", flush=True)
    print("=" * 60, flush=True)
    
    conn = sqlite3.connect(DB_PATH)
    added = 0
    
    for ticker in MISSED_TICKERS:
        print(f"  Processing {ticker}...", end=" ", flush=True)
        
        # Try multiple ticker symbols for problematic ones
        symbols_to_try = [ticker]
        if ticker == "SQ": symbols_to_try = ["SQ", "XYZ"]
        if ticker == "FI": symbols_to_try = ["FI", "FISV"]
        
        ipo_date = None
        actual_symbol = ticker
        for sym in symbols_to_try:
            try:
                tk = yf.Ticker(sym)
                hist = tk.history(period="max")
                if len(hist) > 100:
                    ipo_date = hist.index[0].strftime("%Y-%m-%d")
                    actual_symbol = sym
                    break
            except:
                continue
        
        if not ipo_date:
            print("NO DATA - SKIPPED", flush=True)
            continue
        
        print(f"IPO={ipo_date} ({actual_symbol})...", end=" ", flush=True)
        
        try:
            chart_json, lagna_sign, moon_nak, moon_nak_name, asc, dasha_lord, bhukti_lord, planets_data = compute_natal_chart(ipo_date)
            
            conn.execute(
                "INSERT OR REPLACE INTO stocks (ticker, ipo_date, natal_chart_json, lagna_sign, moon_nakshatra, moon_nakshatra_name, ascendant_degree, current_mahadasha, current_antardasha) VALUES (?,?,?,?,?,?,?,?,?)",
                (ticker, ipo_date, chart_json, lagna_sign, moon_nak, moon_nak_name, asc, dasha_lord, bhukti_lord)
            )
            
            for planet, data in planets_data.items():
                conn.execute(
                    "INSERT OR REPLACE INTO natal_planets (ticker, planet, longitude, sign, sign_name, nakshatra, nakshatra_name, pada, speed, retrograde, d9_sign) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (ticker, planet, data.get("longitude", 0), data.get("sign", 0), data.get("sign_name", ""),
                     data.get("nakshatra", 0), data.get("nakshatra_name", ""),
                     data.get("pada", 0), data.get("speed", 0),
                     1 if data.get("retrograde", False) else 0, 0)
                )
            
            # Add GICS tag
            if ticker in MISSED_GICS:
                s, ig, ind, si = MISSED_GICS[ticker]
                conn.execute("INSERT OR REPLACE INTO sector_tags (ticker, sector, industry_group, industry, sub_industry) VALUES (?,?,?,?,?)", (ticker, s, ig, ind, si))
            
            added += 1
            print("OK", flush=True)
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
        
        time.sleep(0.3)
    
    conn.commit()
    total = conn.execute("SELECT COUNT(DISTINCT ticker) FROM stocks").fetchone()[0]
    sectors = conn.execute("SELECT COUNT(DISTINCT ticker) FROM sector_tags").fetchone()[0]
    print(f"\nAdded {added} new tickers. Total: {total} in natal DB, {sectors} with GICS tags", flush=True)
    conn.close()

if __name__ == "__main__":
    main()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
