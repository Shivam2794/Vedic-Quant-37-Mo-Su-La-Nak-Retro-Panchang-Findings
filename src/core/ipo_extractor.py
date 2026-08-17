import yfinance as yf
import pandas as pd
import json
import os
import sys

sys.path.append(r"C:\Users\patel\Desktop\Python\Learn")
from stock_kundali import StockChart

tickers = [
    'GLD', 'SLV', 'COPX', 'CPER', 'GDX', 'URA', 'NLR', 'XLE', 'XLF', 'XLV', 
    'XLI', 'XLB', 'XLY', 'XLP', 'XLU', 'XLRE', 'XLC', 'XLK', 'SMH', 'XOP', 
    'KRE', 'ITB', 'XBI', 'JETS', 'HACK', 'TAN', 'PAVE', 'XME'
]

print("="*60)
print(" ETF IPO EXTRACTOR & NATAL CHART COMPILER")
print("="*60)

etf_natal_memory = {}

for t in tickers:
    try:
        data = yf.download(t, period="max", progress=False, auto_adjust=False)
        if len(data) == 0:
            print(f"Failed to fetch data for {t}")
            continue
            
        first_date = data.index.min().date()
        print(f"{t:>6}: {first_date}")
        
        # Calculate Natal Chart
        # Assuming listing time 09:30 AM EST, New York coordinates
        chart = StockChart(ticker=t, listing_date=first_date, listing_time_str="09:30", timezone_str="US/Eastern")
        
        # Package into format required by build_stock_matrix.py
        # It expects `Divisional_Charts.D1` and `KP_Cusps`
        natal_entry = {
            "Meta": {
                "Ticker": t,
                "Birth_Date": str(first_date),
                "Time": "09:30",
                "City": "New York"
            },
            "Divisional_Charts": {
                "D1": {
                    "Ascendant": chart.asc_sidereal,
                    "Sun": chart.planets_d1["Sun"]["longitude"],
                    "Moon": chart.planets_d1["Moon"]["longitude"],
                    "Mars": chart.planets_d1["Mars"]["longitude"],
                    "Mercury": chart.planets_d1["Mercury"]["longitude"],
                    "Jupiter": chart.planets_d1["Jupiter"]["longitude"],
                    "Venus": chart.planets_d1["Venus"]["longitude"],
                    "Saturn": chart.planets_d1["Saturn"]["longitude"],
                    "Rahu": chart.planets_d1["Rahu"]["longitude"],
                    "Ketu": chart.ketu_d1["longitude"]
                }
            },
            "KP_Cusps": {
                "Cusp_1": chart.asc_sidereal
            }
        }
        etf_natal_memory[t] = natal_entry
    except Exception as e:
        print(f"Error processing {t}: {e}")

output_path = r"C:\Users\patel\Desktop\Python\Learn\etf_natal_memory.json"
with open(output_path, "w") as f:
    json.dump(etf_natal_memory, f, indent=4)
    
print(f"Saved Natal Memory to {output_path}")
