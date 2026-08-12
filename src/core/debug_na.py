import numpy as np
import pandas as pd
from carver_master_strategy import CarverSystem

sys = CarverSystem(ann_days=365)

np.random.seed(42)
dates = pd.date_range("2020-01-01", periods=1000)

assets = {}
for name in ["BTC", "ETH", "SOL"]:
    ret = np.random.normal(0.0001, 0.02, 1000)
    price = 100 * np.exp(np.cumsum(ret))
    assets[name] = price

panel = pd.DataFrame(assets, index=dates)

target_name = "BTC"
panel_prices = panel

panel_ret = panel_prices.pct_change(fill_method=None).fillna(0.0)
vol_pnl = pd.DataFrame()
for col in panel_ret.columns:
    vol_col, _ = sys.vol_stack(panel_prices[col])
    # _normalised_price
    safe_vol = vol_col.replace(0.0, np.nan).bfill().fillna(1.0)
    r_norm = panel_ret[col] / (safe_vol / np.sqrt(sys.ann_days))
    r_norm = r_norm.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    vol_pnl[col] = 100.0 + r_norm.cumsum()

p_target = vol_pnl[target_name]
p_class = vol_pnl.mean(axis=1)
r = p_target - p_class # relative price

fcs = []
for h in [40, 80]:
    outperf = r.diff(1)
    f_raw = outperf.ewm(span=h, adjust=False).mean()
    scalar = sys.fc_target / f_raw.abs().mean()
    f_scaled = sys._clip_fc(f_raw * scalar)
    fcs.append(f_scaled)

fc_strat = (fcs[0] + fcs[1]) / 2.0 * 1.1
fc_strat = sys._clip_fc(fc_strat)

print("fc_strat na count:", fc_strat.isna().sum())
print("fc_strat valid count:", fc_strat.count())
