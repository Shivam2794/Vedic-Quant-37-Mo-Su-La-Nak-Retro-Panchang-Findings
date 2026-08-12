import pandas as pd
import numpy as np
from autonomous_grinder import get_data, compute_features, generate_random_rule, backtest_rule

df = get_data()
feat, returns = compute_features(df)
binary_cols = [c for c in feat.columns if feat[c].nunique() == 2 and c != 'Target_Ret']

rule_str, components = generate_random_rule(binary_cols)
print("Rule:", rule_str)

signal = eval(rule_str).astype(int) 
alloc_SPY = signal.shift(1).fillna(0)
alloc_TLT = (1 - signal).shift(1).fillna(0)
turnover_SPY = alloc_SPY.diff().abs().fillna(0)
turnover_TLT = alloc_TLT.diff().abs().fillna(0)
total_turnover = turnover_SPY + turnover_TLT

port_return = (alloc_SPY * returns['SPY']) + (alloc_TLT * returns['TLT'])
print("port_return has nans?", port_return.isna().sum())

cost = total_turnover * (10/10000)
net_return = port_return - cost
print("net_return has nans?", net_return.isna().sum())

cum_ret = (1 + net_return).cumprod()
print("cum_ret has nans?", cum_ret.isna().sum())
print("cum_ret iloc[-1]", cum_ret.iloc[-1])
