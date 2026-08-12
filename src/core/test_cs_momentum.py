import numpy as np
import pandas as pd
from carver_master_strategy import CarverSystem

print("Generating Multi-Asset Synthetic Data...")
np.random.seed(42)
dates = pd.date_range("2020-01-01", periods=1000)

# 3 synthetic assets
assets = {}
for name in ["BTC", "ETH", "SOL"]:
    ret = np.random.normal(0.0001, 0.02, 1000)
    price = 100 * np.exp(np.cumsum(ret))
    assets[name] = price

panel = pd.DataFrame(assets, index=dates)

sys = CarverSystem(ann_days=365)
print("Running Target Weights with Panel...")

w = sys.generate_target_weights(
    close_prices=panel["BTC"],
    panel_prices=panel,
    target_name="BTC"
)

print(f"Generated weights for BTC using CS Momentum. Shape: {w.shape}")
print(f"Dynamic FDM Computed: {sys.last_fdm:.3f}")
print("Correlation Matrix:")
print(sys.last_corr)
