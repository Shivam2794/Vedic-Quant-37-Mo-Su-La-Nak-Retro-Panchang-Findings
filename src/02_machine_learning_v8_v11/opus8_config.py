import os

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
OUT_DIR = IN_DIR
PARQUET_FILE = os.path.join(IN_DIR, 'frozen_universe_data.parquet')
RATES_FILE = os.path.join(IN_DIR, 'frozen_rates_data.parquet')
MANIFEST_FILE = os.path.join(IN_DIR, 'manifest.json')

# We use the SPY index as our canonical NYSE trading calendar
CANONICAL_TICKER = 'SPY'
TICKERS_TRADED = ['SPY', 'QQQ', 'TQQQ', 'UPRO', 'TLT', 'GLD', 'BTC-USD']

# Equities typically trade 252 days a year
ANNUALIZER = 252.0

# 1 bar lag for execution: signal generated at close t is executed at open t+1 (effectively close t+1 for daily bars)
LAG = 1
