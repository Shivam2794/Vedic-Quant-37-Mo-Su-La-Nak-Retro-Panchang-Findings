import json
import pandas as pd
from master_grinder_v9 import load_all_data, build_daily_features, build_intraday_lookup, strategy_multi_day_trend, strategy_intraday_bracket, strategy_overnight, strategy_grand_portfolio, compute_metrics, walk_forward_check, TARGET_MAX_DD, TARGET_CAGR, TARGET_SR

def eval_current_best():
    with open('grinder_v9_eternal_best.json', 'r') as f:
        best = json.load(f)
    
    qqq_d, qqq_1m, tqqq_1m = load_all_data()
    daily_feats = build_daily_features(qqq_d)
    intraday_lk = build_intraday_lookup(qqq_1m, tqqq_1m)
    signal_df = intraday_lk.join(daily_feats, how='inner').dropna()

    arch = best['params'].get('arch', 'multiday')
    p = best['params']
    if arch == 'overnight':
        pnl = strategy_overnight(signal_df, p)
    elif arch == 'intraday':
        pnl = strategy_intraday_bracket(signal_df, p)
    elif arch == 'grand_portfolio':
        pnl = strategy_grand_portfolio(signal_df, p)
    else:
        pnl = strategy_multi_day_trend(signal_df, p)
        
    m = compute_metrics(pnl)
    wf = walk_forward_check(pnl, n_windows=3, min_sr=1.0)
    
    print("\n" + "="*60)
    print("V9 ETERNAL GRINDER — CURRENT BEST OPTIMIZED METRICS")
    print("="*60)
    print(f"Archetype:            {arch.upper()}")
    print(f"Trials Completed:     {best['trials_completed']} (Optimized at trial #{best['trials_completed']})")
    print(f"Objective Score:      {best['best_objective']:.4f}")
    print("-" * 60)
    print(f"CAGR:                 {m['CAGR']*100:.2f}%  (Target: >= {TARGET_CAGR*100:.1f}%)")
    print(f"Sharpe Ratio:         {m['Sharpe']:.4f}   (Target: >= {TARGET_SR:.2f})")
    print(f"Maximum Drawdown:     {m['MaxDD']*100:.2f}%  (Target: <= {TARGET_MAX_DD*100:.1f}%)")
    print(f"Annualized Vol:       {m['AnnVol']*100:.2f}%")
    print(f"Win Rate:             {m['WinRate']*100:.2f}%")
    print(f"Total Trades:         {m['Trades']} (Min required: 50)")
    print(f"3-Window OOS WF:      {'PASS (All OOS SR >= 1.0)' if wf else 'FAIL'}")
    print("=" * 60)

if __name__ == '__main__':
    eval_current_best()
