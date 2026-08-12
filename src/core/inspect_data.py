import pandas as pd
import os

files = ['qqq_daily.parquet', 'qqq_1m.parquet', 'tqqq_1m.parquet']
for f in files:
    if os.path.exists(f):
        df = pd.read_parquet(f)
        print(f"--- {f} ---")
        print("Shape:", df.shape)
        print("Columns:", df.columns.tolist())
        print("Head:")
        print(df.head(2))
        print("Index:", type(df.index))
        if len(df) > 0:
            print("First index:", df.index[0], "Last index:", df.index[-1])
    else:
        print(f"{f} not found in {os.getcwd()}")
