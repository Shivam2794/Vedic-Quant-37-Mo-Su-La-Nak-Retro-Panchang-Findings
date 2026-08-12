"""
Database Purge Script (Phase 0.6)
=================================
Removes any stock from the natal database that does not have a 
'VERIFIED' status in verified_ipo_dates.csv. 

This guarantees a mathematically pristine universe by preventing 
corrupted/truncated birth dates from poisoning the Causal Sieve.
"""
import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
CSV_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\verified_ipo_dates.csv"

def purge_unverified_stocks():
    print("Loading verified IPO CSV...")
    df = pd.read_csv(CSV_PATH)
    
    unverified_tickers = df[df['Status'] != 'VERIFIED']['Ticker'].tolist()
    print(f"Found {len(unverified_tickers)} unverified tickers to purge.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check how many stocks are currently in DB
    cursor.execute("SELECT COUNT(*) FROM stocks")
    count_before = cursor.fetchone()[0]
    print(f"Total stocks in DB before purge: {count_before}")
    
    # Purge
    placeholders = ','.join(['?'] * len(unverified_tickers))
    query_stocks = f"DELETE FROM stocks WHERE ticker IN ({placeholders})"
    query_planets = f"DELETE FROM natal_planets WHERE ticker IN ({placeholders})"
    
    cursor.execute(query_stocks, unverified_tickers)
    purged_count = cursor.rowcount
    cursor.execute(query_planets, unverified_tickers)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM stocks")
    count_after = cursor.fetchone()[0]
    
    print(f"Purged {purged_count} records.")
    print(f"Total stocks in DB after purge: {count_after}")
    
    conn.close()

if __name__ == "__main__":
    purge_unverified_stocks()
