"""
IPO Date Verifier & CSV Generator
=================================
This script attempts to fetch the earliest trading dates for the S&P 500.
As a quantitative safeguard, it specifically looks for known yfinance truncation artifacts
(e.g., dates landing exactly on 1962-01-02 or 1980-03-17). 

If a date hits a truncation artifact, the stock is flagged as 'UNVERIFIED' requiring 
manual intervention. Feeding a truncated date into an Astrological Compiler will corrupt 
the Vimshottari Dasha cycles and invalidate the model.

Output: verified_ipo_dates.csv
"""
import pandas as pd
import yfinance as yf
import time
import os

OUTPUT_CSV = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\verified_ipo_dates.csv"

# Known dates where yfinance truncates history artificially
TRUNCATION_ARTIFACTS = {
    "1962-01-02",
    "1980-03-17",
    "1980-12-12" # Sometimes AAPL is correct, but let's be careful
}

def get_sp500_tickers():
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

def build_ipo_csv():
    tickers = get_sp500_tickers()
    print(f"Loaded {len(tickers)} tickers. Beginning IPO date extraction...\n")
    
    results = []
    
    for i, tk in enumerate(tickers):
        try:
            ticker_obj = yf.Ticker(tk)
            hist = ticker_obj.history(period="max", interval="1d")
            
            if hist.empty:
                print(f"[{tk}] ERROR: No data found.")
                results.append({"Ticker": tk, "IPO_Date": None, "Status": "NO_DATA"})
                continue
                
            first_date = hist.index[0].strftime("%Y-%m-%d")
            
            if first_date in TRUNCATION_ARTIFACTS or first_date.startswith("1962"):
                status = "TRUNCATED_WARNING"
                print(f"[{tk}] WARNING: Truncated date detected -> {first_date}")
            else:
                status = "VERIFIED"
                print(f"[{tk}] {first_date} -> {status}")
                
            results.append({
                "Ticker": tk,
                "IPO_Date": first_date,
                "Status": status
            })
            
        except Exception as e:
            print(f"[{tk}] ERROR: {e}")
            results.append({"Ticker": tk, "IPO_Date": None, "Status": "ERROR"})
            
        # Rate limit
        time.sleep(0.1)
        
    df = pd.DataFrame(results)
    
    print("\n" + "="*50)
    print("IPO EXTRACTION SUMMARY")
    print("="*50)
    print(df['Status'].value_counts())
    
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved to {OUTPUT_CSV}")
    print("ACTION REQUIRED: Manually update the 'IPO_Date' for rows marked 'TRUNCATED_WARNING' using CRSP or SEC EDGAR.")

if __name__ == "__main__":
    build_ipo_csv()
