import sys
sys.path.insert(0, r'E:\Python\Learn')
import build_stock_matrix
import pandas as pd
import json

def test():
    with open(r"E:\Python\Learn\master_natal_memory.json", "r") as f:
        natal_memory = json.load(f)
    
    transit_df = pd.read_csv(r"E:\Python\Learn\AstroData_2004_2027.csv")
    transit_df["Date"] = pd.to_datetime(transit_df["Time"].astype(str), format="%Y%m%d")
    transit_df = transit_df.set_index("Date").sort_index()

    import time
    t0 = time.time()
    ticker = "AAPL"
    target_date = pd.Timestamp("2026-06-03")
    dates = [target_date, target_date - pd.Timedelta(days=1), target_date - pd.Timedelta(days=3)]
    
    feats = build_stock_matrix.build_stock_features(ticker, natal_memory[ticker], transit_df, dates)
    print(f"Time taken: {time.time()-t0:.2f}s")
    print(f"Features: {len(feats.columns)}")

if __name__ == "__main__":
    test()
