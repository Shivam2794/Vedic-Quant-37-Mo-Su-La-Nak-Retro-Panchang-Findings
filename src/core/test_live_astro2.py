import sys
sys.path.insert(0, r'E:\Python\Learn')
import build_stock_matrix
import pandas as pd
import json
import joblib

def test():
    with open(r"E:\Python\Learn\master_natal_memory.json", "r") as f:
        natal_memory = json.load(f)
    
    transit_df = pd.read_csv(r"E:\Python\Learn\AstroData_2004_2027.csv")
    transit_df["Date"] = pd.to_datetime(transit_df["Time"].astype(str), format="%Y%m%d")
    transit_df = transit_df.set_index("Date").sort_index()

    pack_b = joblib.load(r"E:\Python\Learn\Model_B_Veto.pkl")
    veto_features = pack_b["features"]

    import time
    t0 = time.time()
    tickers = ["AAPL", "MSFT"]
    target_date = pd.Timestamp("2026-06-03")
    dates = [target_date, target_date - pd.Timedelta(days=1), target_date - pd.Timedelta(days=3)]
    
    rows = []
    for ticker in tickers:
        feats = build_stock_matrix.build_stock_features(ticker, natal_memory[ticker], transit_df, dates)
        feats = feats.reset_index()
        if 'index' in feats.columns and 'Date' not in feats.columns:
            feats = feats.rename(columns={'index': 'Date'})
        row = feats[feats['Date'] == target_date].copy()
        row['Ticker'] = ticker
        rows.append(row)
    
    live_df = pd.concat(rows)
    
    # Simulate the processing that happened before Model_B
    # Usually categorical features are one-hot encoded. Wait, did the training script one-hot encode them?
    # Let's check phase13_model_freezer.py. 
    # phase13 just loaded hybrid_earnings_matrix.parquet. It didn't do pd.get_dummies().
    # That means phase9_hybrid_matrix_builder or build_master_earnings_matrix did it!
    # Let's just create an empty dataframe with veto_features and fill from live_df.
    
    final_df = pd.DataFrame(index=live_df.index, columns=veto_features)
    for col in veto_features:
        if col in live_df.columns:
            final_df[col] = live_df[col]
        else:
            final_df[col] = 0
            
    final_df = final_df.fillna(0)
    print(f"Time taken: {time.time()-t0:.2f}s")
    
    prob = pack_b["model"].predict_proba(final_df)[:, 1]
    print("Prob_Toxic:", prob)

if __name__ == "__main__":
    test()
