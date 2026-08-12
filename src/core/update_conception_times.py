import json
import urllib.request
import urllib.error
import time
from datetime import datetime
import pytz

def get_ciks():
    req = urllib.request.Request(
        'https://www.sec.gov/files/company_tickers.json',
        headers={'User-Agent': 'Antigravity Research (research@example.com)'}
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    ticker_to_cik = {}
    for idx, info in data.items():
        ticker_to_cik[info['ticker'].upper()] = str(info['cik_str']).zfill(10)
    return ticker_to_cik

def fetch_sec_filings(cik):
    req = urllib.request.Request(
        f'https://data.sec.gov/submissions/CIK{cik}.json',
        headers={'User-Agent': 'Antigravity Research (research@example.com)'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {cik}: {e}")
        return []
    
    # We want to find the oldest acceptanceDateTime
    recent = data.get('filings', {}).get('recent', {})
    dates = recent.get('acceptanceDateTime', [])
    
    oldest_dt = None
    for d in dates:
        if not d: continue
        try:
            dt = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
        except ValueError:
            try:
                dt = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            except:
                continue
                
        if oldest_dt is None or dt < oldest_dt:
            oldest_dt = dt
            
    return oldest_dt

def main():
    print("Fetching CIK mappings...")
    ciks = get_ciks()
    
    db_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\asset_birth_database.json"
    with open(db_path, "r") as f:
        db = json.load(f)
        
    ny_tz = pytz.timezone("America/New_York")
    
    updated = 0
    for ticker, info in db.items():
        if ticker in ciks:
            cik = ciks[ticker]
            print(f"Processing {ticker} (CIK: {cik})...")
            oldest_dt = fetch_sec_filings(cik)
            if oldest_dt:
                ny_time = oldest_dt.astimezone(ny_tz)
                new_str = ny_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"  Old Conception: {info['conception']}")
                print(f"  New Conception: {new_str}")
                info['conception'] = new_str
                updated += 1
            time.sleep(0.1) # Respect SEC rate limit (max 10 req/sec)
        else:
            print(f"Ticker {ticker} not found in SEC database.")
            
    with open(db_path, "w") as f:
        json.dump(db, f, indent=4)
        
    print(f"Updated {updated} assets with exact SEC timestamps.")

if __name__ == "__main__":
    main()
