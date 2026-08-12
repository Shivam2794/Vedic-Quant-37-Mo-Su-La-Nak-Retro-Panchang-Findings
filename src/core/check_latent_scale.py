import pandas as pd
df = pd.read_parquet('qqq_daily_V16_latent.parquet')
print("Latent 0 stats:")
print(df['Latent_0'].describe())
print("Latent 1 stats:")
print(df['Latent_1'].describe())
