import pandas as pd
df = pd.read_parquet('orion_pipeline/smart_ml/output/orion_alpha_registry.parquet')
print(df.head())
print(df.info())
