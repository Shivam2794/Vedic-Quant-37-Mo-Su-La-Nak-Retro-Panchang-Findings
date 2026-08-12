import pandas as pd
import glob

# Try loading orion_master_dataset
try:
    df = pd.read_csv('orion_master_dataset.csv')
    df_encoded = pd.get_dummies(df)
    print("orion_master_dataset encoded shape:", df_encoded.shape)
except Exception as e:
    print("orion_master_dataset error:", e)

# Try loading master_feature_matrix.parquet
try:
    df2 = pd.read_parquet('master_feature_matrix.parquet')
    print("master_feature_matrix shape:", df2.shape)
except Exception as e:
    print("master_feature_matrix error:", e)
    
# Try loading genesis_9009_daily.parquet
try:
    df3 = pd.read_parquet('genesis_9009_daily.parquet')
    print("genesis_9009_daily shape:", df3.shape)
except Exception as e:
    print("genesis_9009_daily error:", e)
