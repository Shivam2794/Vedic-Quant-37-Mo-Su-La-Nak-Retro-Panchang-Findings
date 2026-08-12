import pandas as pd
import numpy as np
idx = pd.date_range("2017-12-30", "2018-01-03")
ret = pd.Series([0.1, 0.2, 0.3, 0.4, 0.5], index=idx)
turn = pd.Series([1, 2, 3, 4, 5], index=idx)
mask = idx < pd.Timestamp("2018-01-01")
try:
    ret[mask] = ret[mask] - turn[mask] * 0.1
    print(ret)
except Exception as e:
    print("Error:", e)
