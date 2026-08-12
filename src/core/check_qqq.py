import yfinance as yf
import numpy as np
df = yf.download('QQQ', start='1999-01-01', auto_adjust=False, progress=False)
r = (df['Adj Close'] / df['Close']).dropna()
diffs = np.diff(r.values.ravel())
bad = np.where(diffs < -1e-6)[0]
print(len(bad), 'bad rows')
if len(bad) > 0:
    for b in bad[:5]:
        print(r.iloc[b:b+2])
