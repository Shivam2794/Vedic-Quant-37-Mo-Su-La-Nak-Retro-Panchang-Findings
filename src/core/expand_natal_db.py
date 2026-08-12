"""Process remaining S&P 500 stocks from the captured CSV data."""
import sqlite3
import json
import time
import sys
sys.path.insert(0, r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")
from build_natal_db import get_listing_date, compute_natal_chart, compute_vimshottari_dasha

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"

# Full S&P 500 tickers from the Wikipedia data
SP500_TICKERS = [
    "MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","ABNB","AKAM","ALB",
    "ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR","AEE","AEP","AXP",
    "AIG","AMT","AWK","AMP","AME","AMGN","APH","ADI","AON","APA","APO","AAPL","AMAT","APP",
    "APTV","ACGL","ADM","ARES","ANET","AJG","AIZ","T","ATO","ADSK","ADP","AZO","AVB","AVY",
    "AXON","BKR","BALL","BAC","BAX","BDX","BRK-B","BBY","TECH","BIIB","BLK","BX","XYZ","BK",
    "BA","BKNG","BSX","BMY","AVGO","BR","BRO","BF-B","BLDR","BG","BXP","CHRW","CDNS","CPT",
    "CPB","COF","CAH","CCL","CARR","CVNA","CASY","CAT","CBOE","CBRE","CDW","COR","CNC","CNP",
    "CF","CRL","SCHW","CHTR","CVX","CMG","CB","CHD","CIEN","CI","CINF","CTAS","CSCO","C",
    "CFG","CLX","CME","CMS","KO","CTSH","COHR","COIN","CL","CMCSA","FIX","CAG","COP","ED",
    "STZ","CEG","COO","CPRT","GLW","CPAY","CTVA","CSGP","COST","CTRA","CRH","CRWD","CCI",
    "CSX","CMI","CVS","DHR","DRI","DDOG","DVA","DECK","DE","DELL","DAL","DVN","DXCM","FANG",
    "DLR","DG","DLTR","D","DPZ","DASH","DOV","DOW","DHI","DTE","DUK","DD","ETN","EBAY",
    "SATS","ECL","EIX","EW","EA","ELV","EME","EMR","ETR","EOG","EPAM","EQT","EFX","EQIX",
    "EQR","ERIE","ESS","EL","EG","EVRG","ES","EXC","EXE","EXPE","EXPD","EXR","XOM","FFIV",
    "FDS","FICO","FAST","FRT","FDX","FIS","FITB","FSLR","FE","FISV","F","FTNT","FTV","FOXA",
    "FOX","BEN","FCX","GRMN","IT","GE","GEHC","GEV","GEN","GNRC","GD","GIS","GM","GPC",
    "GILD","GPN","GL","GDDY","GS","HAL","HIG","HAS","HCA","DOC","HSIC","HSY","HPE","HLT",
    "HD","HON","HRL","HST","HWM","HPQ","HUBB","HUM","HBAN","HII","IBM","IEX","IDXX","ITW",
    "INCY","IR","PODD","INTC","IBKR","ICE","IFF","IP","INTU","ISRG","IVZ","INVH","IQV",
    "IRM","JBHT","JBL","JKHY","J","JNJ","JCI","JPM","KVUE","KDP","KEY","KEYS","KMB","KIM",
    "KMI","KKR","KLAC","KHC","KR","LHX","LH","LRCX","LVS","LDOS","LEN","LII","LLY","LIN",
    "LYV","LMT","L","LOW","LULU","LITE","LYB","MTB","MPC","MAR","MRSH","MLM","MAS","MA",
    "MKC","MCD","MCK","MDT","MRK","META","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MRNA",
    "TAP","MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NEM",
    "NWSA","NWS","NEE","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH","NRG","NUE","NVDA","NVR",
    "NXPI","ORLY","OXY","ODFL","OMC","ON","OKE","ORCL","OTIS","PCAR","PKG","PLTR","PANW",
    "PSKY","PH","PAYX","PYPL","PNR","PEP","PFE","PCG","PM","PSX","PNW","PNC","POOL","PPG",
    "PPL","PFG","PG","PGR","PLD","PRU","PEG","PTC","PSA","PHM","PWR","QCOM","DGX","Q","RL",
    "RJF","RTX","O","REG","REGN","RF","RSG","RMD","RVTY","HOOD","ROK","ROL","ROP","ROST",
    "RCL","SPGI","CRM","SNDK","SBAC","SLB","STX","SRE","NOW","SHW","SPG","SWKS","SJM","SW",
    "SNA","SOLV","SO","LUV","SWK","SBUX","STT","STLD","STE","SYK","SMCI","SYF","SNPS","SYY",
    "TMUS","TROW","TTWO","TPR","TRGP","TGT","TEL","TDY","TER","TSLA","TXN","TPL","TXT","TMO",
    "TJX","TKO","TTD","TSCO","TT","TDG","TRV","TRMB","TFC","TYL","TSN","USB","UBER","UDR",
    "ULTA","UNP","UAL","UPS","URI","UNH","UHS","VLO","VTR","VLTO","VRSN","VRSK","VZ","VRTX",
    "VRT","VTRS","VICI","V","VST","VMC","WRB","GWW","WAB","WMT","DIS","WBD","WM","WAT",
    "WEC","WFC","WELL","WST","WDC","WY","WSM","WMB","WTW","WDAY","WYNN","XEL","XYL","YUM",
    "ZBRA","ZBH","ZTS",
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

existing = set(r[0] for r in c.execute("SELECT ticker FROM stocks"))
new_tickers = [t for t in SP500_TICKERS if t not in existing]
print(f"Already have: {len(existing)} stocks")
print(f"New to process: {len(new_tickers)}")

success = 0
failed = []
for i, ticker in enumerate(new_tickers):
    ipo_date = get_listing_date(ticker)
    if not ipo_date:
        failed.append(ticker)
        continue
    try:
        natal = compute_natal_chart(ipo_date)
        dasha = compute_vimshottari_dasha(natal)
        c.execute("""
            INSERT OR REPLACE INTO stocks 
            (ticker, ipo_date, natal_chart_json, lagna_sign, moon_nakshatra,
             moon_nakshatra_name, ascendant_degree, current_mahadasha, current_antardasha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticker, ipo_date, json.dumps(natal), natal.get("lagna_sign", 0),
              natal.get("moon_nakshatra", 0), natal.get("moon_nakshatra_name", ""),
              natal.get("ascendant", 0.0), dasha["mahadasha_lord"], dasha["antardasha_lord"]))
        for p_name, p_data in natal["planets"].items():
            d9_sign = natal.get("d9", {}).get(p_name, {}).get("sign", 0)
            c.execute("""
                INSERT OR REPLACE INTO natal_planets
                (ticker, planet, longitude, sign, sign_name, nakshatra, 
                 nakshatra_name, pada, speed, retrograde, d9_sign)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticker, p_name, p_data.get("longitude", 0),
                  p_data.get("sign", 0), p_data.get("sign_name", ""),
                  p_data.get("nakshatra", 0), p_data.get("nakshatra_name", ""),
                  p_data.get("pada", 0), p_data.get("speed", 0),
                  p_data.get("retrograde", False), d9_sign))
        success += 1
    except Exception as e:
        failed.append(f"{ticker}:{e}")

    if (i + 1) % 25 == 0:
        conn.commit()
        print(f"  Progress: {i+1}/{len(new_tickers)} ({success} ok, {len(failed)} failed)")
        time.sleep(1)

conn.commit()
total = c.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
print(f"\nFINAL: {total} stocks with natal charts")
print(f"New: {success} | Failed: {len(failed)}")
if failed:
    print(f"Failed: {failed[:20]}")

# Distribution summary
print("\nMahadasha Distribution:")
for row in c.execute("SELECT current_mahadasha, COUNT(*) FROM stocks GROUP BY current_mahadasha ORDER BY COUNT(*) DESC"):
    print(f"  {row[0]:10s} {row[1]:3d}")

import os
print(f"\nDB size: {os.path.getsize(DB_PATH)/1024/1024:.1f} MB")
conn.close()
