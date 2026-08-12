"""
Phase 6A: Universe Expansion — IPO Date Compilation & Natal Chart Generation
============================================================================
Compiles IPO/first-trade dates for 74 new tickers and generates
Vedic natal charts using Swiss Ephemeris.

Uses yfinance to pull the earliest available trading date as a proxy
for IPO date (this is the most reliable automated method).
"""
import yfinance as yf
import sqlite3
import json
import os
import time
import swisseph as swe

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

# 74 new tickers from Master Plan V2
NEW_TICKERS = [
    # Semiconductors
    "TSM", "AMD", "ASML", "INTC", "ADI", "NXPI", "MU",
    # Application Software
    "PLTR", "HUBS", "TYL", "TRMB",
    # IT Consulting
    "IBM", "CTSH", "EPAM", "DXC",
    # Interactive Media
    "MTCH", "TRIP", "YELP", "IAC",
    # Telecom
    "VZ", "T", "CMCSA", "TMUS",
    # Broadline Retail
    "BABA", "MELI", "EBAY", "ETSY", "M", "KSS", "DDS",
    # Consumer Staples
    "DG", "KR", "CASY", "BJ",
    # Payments
    "SQ", "FI", "FIS", "JKHY",
    # Capital Markets
    "MCO", "MSCI", "CBOE", "FDS", "LPLA", "EVR",
    # Aerospace & Defense
    "GE", "RTX", "BA", "LMT", "GD", "TDG", "LHX", "AXON",
    # Machinery
    "CAT", "CMI", "PCAR", "OSK", "WAB", "TTC", "TEX", "ALSN",
    # Agriculture
    "AGCO",
    # Ground Transport
    "CSX", "JBHT", "SAIA", "R", "LSTR",
    # Logistics
    "UPS", "FDX",
    # Pharma/Biotech
    "JNJ", "ABT",
    # Energy
    "XOM", "CVX",
    # Real Estate
    "CSGP", "CBRE",
]

# GICS Level 4 Taxonomy for ALL 143 tickers (existing 69 + new 74)
GICS_TAGS = {
    # === EXISTING 69 TICKERS ===
    "NVDA": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "AVGO": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "TXN": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "QCOM": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "KLAC": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductor Equipment"),
    "LRCX": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductor Equipment"),
    "ADBE": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "CRM": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "INTU": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "SNPS": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "CDNS": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "NOW": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "ORCL": ("Information Technology", "Software & Services", "Software", "Systems Software"),
    "MSFT": ("Information Technology", "Software & Services", "Software", "Systems Software"),
    "CSCO": ("Information Technology", "Technology Hardware", "Communications Equipment", "Communications Equipment"),
    "ACN": ("Information Technology", "Software & Services", "IT Services", "IT Consulting"),
    "GOOGL": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "META": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "NFLX": ("Communication Services", "Media & Entertainment", "Movies & Entertainment", "Movies & Entertainment"),
    "AMZN": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "TSLA": ("Consumer Discretionary", "Automobiles & Components", "Automobiles", "Automobile Manufacturers"),
    "BKNG": ("Consumer Discretionary", "Consumer Services", "Hotels Restaurants & Leisure", "Hotels Resorts & Cruise Lines"),
    "SBUX": ("Consumer Discretionary", "Consumer Services", "Hotels Restaurants & Leisure", "Restaurants"),
    "MCD": ("Consumer Discretionary", "Consumer Services", "Hotels Restaurants & Leisure", "Restaurants"),
    "HD": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Specialty Retail", "Home Improvement Retail"),
    "ORLY": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Specialty Retail", "Automotive Retail"),
    "TGT": ("Consumer Staples", "Consumer Staples Distribution", "Consumer Staples Merchandise Retail", "General Merchandise Stores"),
    "WMT": ("Consumer Staples", "Consumer Staples Distribution", "Consumer Staples Merchandise Retail", "Hypermarkets & Super Centers"),
    "COST": ("Consumer Staples", "Consumer Staples Distribution", "Consumer Staples Merchandise Retail", "Hypermarkets & Super Centers"),
    "PEP": ("Consumer Staples", "Food Beverage & Tobacco", "Beverages", "Soft Drinks & Non-alcoholic Beverages"),
    "MDLZ": ("Consumer Staples", "Food Beverage & Tobacco", "Food Products", "Packaged Foods & Meats"),
    "PM": ("Consumer Staples", "Food Beverage & Tobacco", "Tobacco", "Tobacco"),
    "CL": ("Consumer Staples", "Household & Personal Products", "Household Products", "Household Products"),
    "V": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "MA": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "PYPL": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "SPGI": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "CME": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "ICE": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "BLK": ("Financials", "Capital Markets", "Asset Management", "Asset Management & Custody Banks"),
    "GS": ("Financials", "Capital Markets", "Capital Markets", "Investment Banking & Brokerage"),
    "MS": ("Financials", "Capital Markets", "Capital Markets", "Investment Banking & Brokerage"),
    "CB": ("Financials", "Insurance", "Insurance", "Property & Casualty Insurance"),
    "BRK-B": ("Financials", "Insurance", "Insurance", "Multi-line Insurance"),
    "LLY": ("Health Care", "Pharma Biotech & Life Sciences", "Pharmaceuticals", "Pharmaceuticals"),
    "AMGN": ("Health Care", "Pharma Biotech & Life Sciences", "Biotechnology", "Biotechnology"),
    "GILD": ("Health Care", "Pharma Biotech & Life Sciences", "Biotechnology", "Biotechnology"),
    "REGN": ("Health Care", "Pharma Biotech & Life Sciences", "Biotechnology", "Biotechnology"),
    "VRTX": ("Health Care", "Pharma Biotech & Life Sciences", "Biotechnology", "Biotechnology"),
    "ABBV": ("Health Care", "Pharma Biotech & Life Sciences", "Pharmaceuticals", "Pharmaceuticals"),
    "UNH": ("Health Care", "Health Care Equipment & Services", "Health Care Providers", "Managed Health Care"),
    "ISRG": ("Health Care", "Health Care Equipment & Services", "Health Care Equipment", "Health Care Equipment"),
    "DHR": ("Health Care", "Pharma Biotech & Life Sciences", "Life Sciences Tools", "Life Sciences Tools & Services"),
    "MCK": ("Health Care", "Health Care Equipment & Services", "Health Care Providers", "Health Care Distributors"),
    "ZTS": ("Health Care", "Pharma Biotech & Life Sciences", "Pharmaceuticals", "Pharmaceuticals"),
    "CI": ("Health Care", "Health Care Equipment & Services", "Health Care Providers", "Managed Health Care"),
    "BDX": ("Health Care", "Health Care Equipment & Services", "Health Care Equipment", "Health Care Equipment"),
    "DE": ("Industrials", "Capital Goods", "Machinery", "Agricultural & Farm Machinery"),
    "EMR": ("Industrials", "Capital Goods", "Electrical Equipment", "Electrical Components & Equipment"),
    "CTAS": ("Industrials", "Commercial & Professional Services", "Commercial Services", "Diversified Support Services"),
    "ITW": ("Industrials", "Capital Goods", "Machinery", "Industrial Machinery & Supplies"),
    "NOC": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "UNP": ("Industrials", "Transportation", "Ground Transportation", "Rail Transportation"),
    "WM": ("Industrials", "Commercial & Professional Services", "Commercial Services", "Environmental Services"),
    "LIN": ("Materials", "Materials", "Chemicals", "Industrial Gases"),
    "SLB": ("Energy", "Energy", "Oil Gas & Consumable Fuels", "Oil & Gas Equipment & Services"),
    "EOG": ("Energy", "Energy", "Oil Gas & Consumable Fuels", "Oil & Gas Exploration & Production"),
    "SO": ("Utilities", "Utilities", "Electric Utilities", "Electric Utilities"),
    "PLD": ("Real Estate", "Equity REITs", "Industrial REITs", "Industrial REITs"),
    # === NEW 74 TICKERS ===
    "TSM": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "AMD": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "ASML": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductor Equipment"),
    "INTC": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "ADI": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "NXPI": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "MU": ("Information Technology", "Semiconductors & Equipment", "Semiconductors", "Semiconductors"),
    "PLTR": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "HUBS": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "TYL": ("Information Technology", "Software & Services", "Software", "Application Software"),
    "TRMB": ("Information Technology", "Technology Hardware", "Electronic Equipment", "Electronic Equipment & Instruments"),
    "IBM": ("Information Technology", "Software & Services", "IT Services", "IT Consulting & Other Services"),
    "CTSH": ("Information Technology", "Software & Services", "IT Services", "IT Consulting & Other Services"),
    "EPAM": ("Information Technology", "Software & Services", "IT Services", "IT Consulting & Other Services"),
    "DXC": ("Information Technology", "Software & Services", "IT Services", "IT Consulting & Other Services"),
    "MTCH": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "TRIP": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "YELP": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "IAC": ("Communication Services", "Media & Entertainment", "Interactive Media", "Interactive Media & Services"),
    "VZ": ("Communication Services", "Telecommunication Services", "Diversified Telecom", "Integrated Telecom Services"),
    "T": ("Communication Services", "Telecommunication Services", "Diversified Telecom", "Integrated Telecom Services"),
    "CMCSA": ("Communication Services", "Media & Entertainment", "Cable & Satellite", "Cable & Satellite"),
    "TMUS": ("Communication Services", "Telecommunication Services", "Wireless Telecom", "Wireless Telecom Services"),
    "BABA": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "MELI": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "EBAY": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "ETSY": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "M": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "KSS": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "DDS": ("Consumer Discretionary", "Consumer Discretionary Distribution", "Broadline Retail", "Broadline Retail"),
    "DG": ("Consumer Staples", "Consumer Staples Distribution", "Consumer Staples Merchandise Retail", "General Merchandise Stores"),
    "KR": ("Consumer Staples", "Consumer Staples Distribution", "Food Retail", "Food Retail"),
    "CASY": ("Consumer Staples", "Consumer Staples Distribution", "Food Retail", "Food Retail"),
    "BJ": ("Consumer Staples", "Consumer Staples Distribution", "Consumer Staples Merchandise Retail", "Hypermarkets & Super Centers"),
    "SQ": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "FI": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "FIS": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "JKHY": ("Financials", "Financial Services", "Transaction & Payment Processing", "Transaction & Payment Processing Services"),
    "MCO": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "MSCI": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "CBOE": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "FDS": ("Financials", "Capital Markets", "Financial Exchanges & Data", "Financial Exchanges & Data"),
    "LPLA": ("Financials", "Capital Markets", "Capital Markets", "Investment Banking & Brokerage"),
    "EVR": ("Financials", "Capital Markets", "Capital Markets", "Investment Banking & Brokerage"),
    "GE": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "RTX": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "BA": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "LMT": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "GD": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "TDG": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "LHX": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "AXON": ("Industrials", "Capital Goods", "Aerospace & Defense", "Aerospace & Defense"),
    "CAT": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "CMI": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "PCAR": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "OSK": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "WAB": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "TTC": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "TEX": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "ALSN": ("Industrials", "Capital Goods", "Machinery", "Construction Machinery & Heavy Equipment"),
    "AGCO": ("Industrials", "Capital Goods", "Machinery", "Agricultural & Farm Machinery"),
    "CSX": ("Industrials", "Transportation", "Ground Transportation", "Rail Transportation"),
    "JBHT": ("Industrials", "Transportation", "Ground Transportation", "Cargo Ground Transportation"),
    "SAIA": ("Industrials", "Transportation", "Ground Transportation", "Cargo Ground Transportation"),
    "R": ("Industrials", "Transportation", "Ground Transportation", "Cargo Ground Transportation"),
    "LSTR": ("Industrials", "Transportation", "Ground Transportation", "Cargo Ground Transportation"),
    "UPS": ("Industrials", "Transportation", "Air Freight & Logistics", "Air Freight & Logistics"),
    "FDX": ("Industrials", "Transportation", "Air Freight & Logistics", "Air Freight & Logistics"),
    "JNJ": ("Health Care", "Pharma Biotech & Life Sciences", "Pharmaceuticals", "Pharmaceuticals"),
    "ABT": ("Health Care", "Health Care Equipment & Services", "Health Care Equipment", "Health Care Equipment"),
    "XOM": ("Energy", "Energy", "Oil Gas & Consumable Fuels", "Integrated Oil & Gas"),
    "CVX": ("Energy", "Energy", "Oil Gas & Consumable Fuels", "Integrated Oil & Gas"),
    "CSGP": ("Real Estate", "Real Estate Management", "Real Estate Services", "Real Estate Services"),
    "CBRE": ("Real Estate", "Real Estate Management", "Real Estate Services", "Real Estate Services"),
}

def get_ipo_dates(tickers):
    """Pull earliest available date from yfinance as IPO proxy."""
    ipo_dates = {}
    for i, ticker in enumerate(tickers):
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="max")
            if len(hist) > 0:
                first_date = hist.index[0].strftime("%Y-%m-%d")
                ipo_dates[ticker] = first_date
                print(f"  [{i+1}/{len(tickers)}] {ticker}: {first_date} ({len(hist)} days)", flush=True)
            else:
                print(f"  [{i+1}/{len(tickers)}] {ticker}: NO DATA", flush=True)
        except Exception as e:
            print(f"  [{i+1}/{len(tickers)}] {ticker}: ERROR {e}", flush=True)
        time.sleep(0.3)  # Rate limit
    return ipo_dates

def compute_natal_chart(date_str, ticker):
    """Compute Vedic natal chart for a given date using Swiss Ephemeris."""
    from datetime import datetime
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    
    # Use 9:30 AM ET (market open) as birth time
    # Julian Day at 9:30 AM ET = 14:30 UTC
    jd = swe.julday(dt.year, dt.month, dt.day, 14.5)
    
    planets_data = {}
    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
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
    
    # Ayanamsa (Lahiri)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)
    
    for name, pid in planet_ids.items():
        pos = swe.calc_ut(jd, pid)
        lon_tropical = pos[0][0]
        lon_sidereal = (lon_tropical - ayanamsa) % 360
        speed = pos[0][3]
        
        sign_idx = int(lon_sidereal / 30)
        degree_in_sign = lon_sidereal % 30
        nakshatra_idx = int(lon_sidereal / (360/27))
        pada = int((lon_sidereal % (360/27)) / (360/108)) + 1
        
        # D9 (Navamsa)
        d9_sign = int((lon_sidereal % 30) / (30/9))
        d9_sign = (sign_idx * 9 + d9_sign) % 12 if sign_idx % 3 == 0 else d9_sign  # Simplified
        
        planets_data[name] = {
            "longitude": round(lon_sidereal, 4),
            "sign": sign_idx,
            "sign_name": SIGNS[sign_idx],
            "degree_in_sign": round(degree_in_sign, 4),
            "nakshatra": nakshatra_idx,
            "nakshatra_name": NAKSHATRAS[nakshatra_idx],
            "pada": pada,
            "speed": round(speed, 6),
            "retrograde": speed < 0
        }
    
    # Rahu/Ketu (Mean Node)
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE)
    rahu_lon = (rahu_pos[0][0] - ayanamsa) % 360
    ketu_lon = (rahu_lon + 180) % 360
    
    rahu_sign = int(rahu_lon / 30)
    ketu_sign = int(ketu_lon / 30)
    rahu_nak = int(rahu_lon / (360/27))
    ketu_nak = int(ketu_lon / (360/27))
    
    planets_data["Rahu"] = {
        "longitude": round(rahu_lon, 4),
        "sign": rahu_sign, "sign_name": SIGNS[rahu_sign],
        "nakshatra": rahu_nak, "nakshatra_name": NAKSHATRAS[rahu_nak]
    }
    planets_data["Ketu"] = {
        "longitude": round(ketu_lon, 4),
        "sign": ketu_sign, "sign_name": SIGNS[ketu_sign],
        "nakshatra": ketu_nak, "nakshatra_name": NAKSHATRAS[ketu_nak]
    }
    
    # Ascendant (Lagna) — using NYC coordinates (40.7128, -74.0060)
    houses = swe.houses(jd, 40.7128, -74.0060, b'P')
    asc_tropical = houses[1][0]
    asc_sidereal = (asc_tropical - ayanamsa) % 360
    mc_tropical = houses[1][1]
    mc_sidereal = (mc_tropical - ayanamsa) % 360
    
    lagna_sign = int(asc_sidereal / 30)
    moon_nak = planets_data["Moon"]["nakshatra"]
    moon_nak_name = planets_data["Moon"]["nakshatra_name"]
    
    # Determine Mahadasha lord from Moon nakshatra
    dasha_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_lord = dasha_lords[moon_nak % 9]
    
    # Bhukti lord (simplified — use 2nd level)
    bhukti_lord = dasha_lords[(moon_nak + 1) % 9]
    
    chart_json = json.dumps({
        "jd": jd, "date": date_str, "planets": planets_data,
        "ascendant": round(asc_sidereal, 4), "mc": round(mc_sidereal, 4),
        "lagna_sign": lagna_sign,
        "moon_nakshatra": moon_nak, "moon_nakshatra_name": moon_nak_name
    })
    
    return chart_json, lagna_sign, moon_nak, moon_nak_name, round(asc_sidereal, 4), dasha_lord, bhukti_lord

def insert_natal_charts(ipo_dates):
    """Insert natal charts into the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    
    for ticker, date_str in ipo_dates.items():
        try:
            chart_json, lagna_sign, moon_nak, moon_nak_name, asc, dasha_lord, bhukti_lord = compute_natal_chart(date_str, ticker)
            
            # Insert into stocks table
            conn.execute(
                "INSERT OR REPLACE INTO stocks (ticker, ipo_date, natal_chart_json, lagna_sign, moon_nakshatra, moon_nakshatra_name, ascendant_degree, current_mahadasha, current_antardasha) VALUES (?,?,?,?,?,?,?,?,?)",
                (ticker, date_str, chart_json, lagna_sign, moon_nak, moon_nak_name, asc, dasha_lord, bhukti_lord)
            )
            
            # Insert into natal_planets table
            chart = json.loads(chart_json)
            for planet, data in chart["planets"].items():
                d9_sign = data.get("degree_in_sign", 0)  # simplified
                conn.execute(
                    "INSERT OR REPLACE INTO natal_planets (ticker, planet, longitude, sign, sign_name, nakshatra, nakshatra_name, pada, speed, retrograde, d9_sign) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (ticker, planet, data.get("longitude", 0), data.get("sign", 0), data.get("sign_name", ""),
                     data.get("nakshatra", 0), data.get("nakshatra_name", ""),
                     data.get("pada", 0), data.get("speed", 0),
                     1 if data.get("retrograde", False) else 0, int(d9_sign))
                )
            
            print(f"  Inserted {ticker} natal chart ({date_str})", flush=True)
        except Exception as e:
            print(f"  ERROR inserting {ticker}: {e}", flush=True)
    
    conn.commit()
    
    # Create sector_tags table
    conn.execute("DROP TABLE IF EXISTS sector_tags")
    conn.execute("""CREATE TABLE sector_tags (
        ticker TEXT PRIMARY KEY,
        sector TEXT,
        industry_group TEXT,
        industry TEXT,
        sub_industry TEXT
    )""")
    
    for ticker, (sector, ig, ind, si) in GICS_TAGS.items():
        conn.execute(
            "INSERT OR REPLACE INTO sector_tags (ticker, sector, industry_group, industry, sub_industry) VALUES (?,?,?,?,?)",
            (ticker, sector, ig, ind, si)
        )
    
    conn.commit()
    total = conn.execute("SELECT COUNT(DISTINCT ticker) FROM stocks").fetchone()[0]
    sectors = conn.execute("SELECT COUNT(DISTINCT ticker) FROM sector_tags").fetchone()[0]
    print(f"\nDatabase updated: {total} tickers in natal DB, {sectors} tickers with GICS tags", flush=True)
    conn.close()

def main():
    print("=" * 60, flush=True)
    print("PHASE 6A: UNIVERSE EXPANSION", flush=True)
    print("=" * 60, flush=True)
    
    # Step 1: Get IPO dates
    print(f"\nStep 1: Fetching IPO dates for {len(NEW_TICKERS)} new tickers...", flush=True)
    ipo_dates = get_ipo_dates(NEW_TICKERS)
    
    print(f"\nSuccessfully fetched {len(ipo_dates)}/{len(NEW_TICKERS)} IPO dates.", flush=True)
    
    # Step 2: Generate and insert natal charts
    print(f"\nStep 2: Generating Vedic natal charts...", flush=True)
    insert_natal_charts(ipo_dates)
    
    print(f"\n[SUCCESS] Phase 6A Step 1-2 complete.", flush=True)

if __name__ == "__main__":
    main()
