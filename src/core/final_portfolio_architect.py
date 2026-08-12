import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

# Import core engine functions
import master_grinder_v12 as mg

def compute_institutional_metrics(daily_pnl: pd.Series, trades_array: np.ndarray):
    """Computes an extended set of institutional performance metrics."""
    trades = int(np.sum(trades_array))
    if trades < mg.MIN_TRADES:
        return None
        
    cum = (1 + daily_pnl).cumprod()
    actual_years = ((pd.to_datetime(str(daily_pnl.index[-1])) -
                     pd.to_datetime(str(daily_pnl.index[0]))).days / 365.25)
                     
    if actual_years < 0.1:
        return None
        
    cagr = (cum.iloc[-1]) ** (1 / actual_years) - 1.0
    running_max = cum.cummax()
    drawdown = (cum - running_max) / running_max
    max_dd = drawdown.min()
    
    mean_ret = daily_pnl.mean()
    std_ret = daily_pnl.std()
    
    if std_ret == 0:
        return None
        
    sharpe = (mean_ret / std_ret) * np.sqrt(252)
    
    # Sortino
    downside_ret = daily_pnl[daily_pnl < 0]
    downside_std = downside_ret.std() if len(downside_ret) > 1 else 1e-6
    sortino = (mean_ret / downside_std) * np.sqrt(252)
    
    # Trade Level Stats (approximate using daily returns since trades can overlap)
    # Because of overlapping multi-day trades, true trade-level stats are hard to extract from daily arrays.
    # We will use daily active returns as a proxy for 'trade days'.
    active_days = daily_pnl[daily_pnl != 0]
    win_days = active_days[active_days > 0]
    loss_days = active_days[active_days < 0]
    
    win_rate = len(win_days) / len(active_days) if len(active_days) > 0 else 0
    avg_win = win_days.mean() if len(win_days) > 0 else 0
    avg_loss = loss_days.mean() if len(loss_days) > 0 else 0
    
    profit_factor = abs(win_days.sum() / loss_days.sum()) if len(loss_days) > 0 and loss_days.sum() != 0 else float('inf')
    
    return {
        'CAGR': cagr,
        'MaxDD': max_dd,
        'Sharpe': sharpe,
        'Sortino': sortino,
        'WinRate': win_rate,
        'ProfitFactor': profit_factor,
        'AvgWin': avg_win,
        'AvgLoss': avg_loss,
        'Trades': trades,
        'Years': actual_years,
        'CumReturn': cum.iloc[-1] - 1.0
    }

def main():
    print("="*60)
    print("THE INSTITUTIONAL PORTFOLIO ARCHITECT")
    print("="*60)
    
    # 1. Load best params
    param_file = 'grinder_v12_eternal_best.json'
    if not os.path.exists(param_file):
        print(f"[ERROR] Could not find {param_file}. Ensure the V12 Engine has saved a best result.")
        return
        
    with open(param_file, 'r') as f:
        best_data = json.load(f)
        
    params = best_data.get('params', {})
    arch = best_data.get('arch', 'multi_day_trend')
    print(f"[INFO] Loaded Optimal Parameters for architecture: {arch}")
    
    # 2. Load Data
    print("[INFO] Booting Data Pipeline...")
    qqq_d, qqq_1m, tqqq_1m = mg.load_all_data()
    daily_feats = mg.build_daily_features(qqq_d)
    intraday_lk = mg.build_intraday_lookup(qqq_1m, tqqq_1m)
    signal_df = intraday_lk.join(daily_feats, how='inner').dropna()
    print(f"[INFO] Signal Matrix Ready: {len(signal_df)} days")
    
    # 3. Execute Strategy
    print("[INFO] Simulating Optimal Strategy...")
    if arch == 'overnight': pnl, trades = mg.strategy_overnight(signal_df, params)
    elif arch == 'intraday_bracket': pnl, trades = mg.strategy_intraday_bracket(signal_df, params)
    elif arch == 'grand_portfolio': pnl, trades = mg.strategy_grand_portfolio(signal_df, params)
    else: pnl, trades = mg.strategy_multi_day_trend(signal_df, params)
    
    daily_pnl = pd.Series(pnl, index=signal_df.index)
    metrics = compute_institutional_metrics(daily_pnl, trades)
    
    if metrics is None:
        print("[ERROR] Failed to compute metrics. Check trade count or parameters.")
        return
        
    # 4. Compute Benchmark
    # We use QQQ Buy and Hold as benchmark from the first day of our signal_df
    # We calculate daily returns of QQQ
    # Extract string dates from signal_df index for exact string matching on DatetimeIndex
    signal_dates = [str(d) for d in signal_df.index]
    # Because qqq_d is DatetimeIndex, we can convert its index to date strings to match
    qqq_d_dates = qqq_d.copy()
    qqq_d_dates.index = qqq_d_dates.index.date.astype(str)
    qqq_bench = qqq_d_dates.loc[signal_dates]
    bench_returns = qqq_bench['Close'].pct_change().fillna(0)
    bench_cum = (1 + bench_returns).cumprod()
    bench_cagr = (bench_cum.iloc[-1]) ** (1 / metrics['Years']) - 1.0
    bench_dd = (bench_cum - bench_cum.cummax()) / bench_cum.cummax()
    bench_max_dd = bench_dd.min()
    
    # 5. Plot Equity Curve
    cum_equity = (1 + daily_pnl).cumprod()
    cum_equity.index = pd.to_datetime(cum_equity.index)
    bench_cum.index = pd.to_datetime(bench_cum.index)
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(cum_equity.index, cum_equity.values * 100, color='#00ff88', label=f'Optimal Portfolio ({arch.upper()})', linewidth=2)
    ax.plot(bench_cum.index, bench_cum.values * 100, color='#888888', label='QQQ Benchmark (Buy & Hold)', linewidth=1.5, alpha=0.7)
    
    ax.set_title("Institutional Portfolio Tear Sheet", fontsize=18, color='white', pad=20)
    ax.set_ylabel("Growth ($100 Base)", fontsize=12)
    ax.grid(True, alpha=0.2)
    ax.legend(loc='upper left', fontsize=12)
    
    # Annotate metrics
    metrics_text = (
        f"CAGR: {metrics['CAGR']*100:.1f}%\n"
        f"Max Drawdown: {metrics['MaxDD']*100:.1f}%\n"
        f"Sharpe Ratio: {metrics['Sharpe']:.2f}\n"
        f"Sortino Ratio: {metrics['Sortino']:.2f}\n"
        f"Win Rate: {metrics['WinRate']*100:.1f}%\n"
        f"Profit Factor: {metrics['ProfitFactor']:.2f}\n"
        f"Total Trades: {metrics['Trades']}"
    )
    props = dict(boxstyle='round', facecolor='#111111', alpha=0.8, edgecolor='#333333')
    ax.text(0.02, 0.65, metrics_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props, color='white', family='monospace')
            
    # Save Plot
    brain_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\87028df4-1ec4-40e2-a989-dbc79c4b85bb"
    plot_path = os.path.join(brain_dir, "institutional_tear_sheet.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor='#111111')
    print(f"[INFO] Saved Equity Curve to {plot_path}")
    
    # 6. Generate Markdown Report
    md_path = os.path.join(brain_dir, "Institutional_Performance_Report.md")
    
    md_content = f"""# Institutional Performance Report

## The V12 Holy Grail Engine

The V12 Multi-Core Engine has identified the following optimal parameter set across the `{arch}` architecture.

### Executive Summary

| Metric | Optimal Portfolio | QQQ Benchmark |
|--------|-------------------|---------------|
| **CAGR** | `{metrics['CAGR']*100:.2f}%` | `{bench_cagr*100:.2f}%` |
| **Max Drawdown** | `{metrics['MaxDD']*100:.2f}%` | `{bench_max_dd*100:.2f}%` |
| **Sharpe Ratio** | `{metrics['Sharpe']:.2f}` | N/A |
| **Sortino Ratio** | `{metrics['Sortino']:.2f}` | N/A |
| **Total Cumulative Return** | `{metrics['CumReturn']*100:.2f}%` | `{(bench_cum.iloc[-1] - 1)*100:.2f}%` |

### Trade Statistics
- **Total Trades**: {metrics['Trades']}
- **Win Rate (Days)**: {metrics['WinRate']*100:.1f}%
- **Profit Factor**: {metrics['ProfitFactor']:.2f}
- **Avg Win / Avg Loss**: +{metrics['AvgWin']*100:.2f}% / {metrics['AvgLoss']*100:.2f}%

### Optimal Parameters
```json
{json.dumps(params, indent=4)}
```

### Visual Equity Curve
![Equity Curve](file:///{plot_path.replace('\\', '/')})
"""
    
    with open(md_path, 'w') as f:
        f.write(md_content)
        
    print(f"[INFO] Saved Markdown Report to {md_path}")
    print("="*60)
    print("ARCHITECT PROCESS COMPLETE.")
    print("="*60)

if __name__ == '__main__':
    main()
