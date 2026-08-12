import pandas as pd
import glob
import os

print('Parquets:')
for f in glob.glob('*.parquet'):
    if 'continuous' not in f and 'stock_returns' not in f and 'genesis_9009_daily' not in f:
        print(f, pd.read_parquet(f).shape)
    else:
        print(f, 'skipped loading due to size')

print('\nCSVs:')
for f in ['advanced_ml_dataset.csv', 'orion_master_dataset.csv', 'master_feature_columns.csv', 'ml_features.csv']:
    if os.path.exists(f):
        print(f, pd.read_csv(f, nrows=5).shape)
