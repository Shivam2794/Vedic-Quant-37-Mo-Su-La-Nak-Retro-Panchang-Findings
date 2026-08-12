import json
import master_grinder_v8 as mg

qqq_d, qqq_1m, tqqq_1m = mg.load_all_data()
feats = mg.build_daily_features(qqq_d)
lk = mg.build_intraday_lookup(qqq_1m, tqqq_1m)
sdf = lk.join(feats, how='inner').dropna()

best_json = json.load(open('grinder_v8_eternal_best.json'))
params = best_json['params']
arch = best_json['arch']

if arch == 'overnight':
    pnl = mg.strategy_overnight(sdf, params)
elif arch == 'intraday':
    pnl = mg.strategy_intraday_bracket(sdf, params)
elif arch == 'grand_portfolio':
    pnl = mg.strategy_grand_portfolio(sdf, params)
else:
    pnl = mg.strategy_multi_day_trend(sdf, params)

m = mg.compute_metrics(pnl)
wf = mg.walk_forward_check(pnl)

print("\n=== CURRENT ETERNAL GRINDER BEST METRICS ===")
print(f"Archetype:       {arch}")
print(f"Sharpe Ratio:    {m['Sharpe']:.4f}")
print(f"CAGR:            {m['CAGR']*100:.2f}%")
print(f"Max Drawdown:    {m['MaxDD']*100:.2f}%")
print(f"Win Rate:        {m['WinRate']*100:.2f}%")
print(f"Total Trades:    {m['Trades']}")
print(f"Walk-Forward SR: {'PASS (All windows SR >= 1.0)' if wf else 'FAIL'}")
print("============================================")
