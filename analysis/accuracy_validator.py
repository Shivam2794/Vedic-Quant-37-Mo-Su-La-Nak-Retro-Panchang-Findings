import pandas as pd
import yfinance as yf
import numpy as np
import os
import warnings

# Suppress pandas FutureWarnings from yfinance
warnings.simplefilter(action='ignore', category=FutureWarning)

WORKSPACE = r"C:\Users\Shivam Patel\.gemini\antigravity\brain\f7cdee3c-586a-4806-b281-db74f64d657a"

def parse_calendar(filepath):
    dates = []
    directions = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('|') and 'Date' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    date_str = parts[1]
                    dir_str = parts[3]
                    
                    try:
                        dt = pd.to_datetime(date_str)
                    except:
                        continue
                        
                    if 'LONG' in dir_str:
                        direction = 'LONG'
                    elif 'SHORT' in dir_str:
                        direction = 'SHORT'
                    elif 'CASH' in dir_str:
                        direction = 'CASH'
                    else:
                        continue
                        
                    dates.append(dt)
                    directions.append(direction)
                    
    df = pd.DataFrame({'Date': dates, 'Direction': directions})
    df = df.set_index('Date')
    df = df[~df.index.duplicated(keep='last')]
    return df

def main():
    print("[1/4] Parsing Trading Calendars...")
    model_b_path = os.path.join(WORKSPACE, "historical_trading_calendar_2024_2026_Model_B.md")
    model_c_path = os.path.join(WORKSPACE, "historical_trading_calendar_2024_2026_Model_C.md")
    
    df_b = parse_calendar(model_b_path)
    df_c = parse_calendar(model_c_path)
    print(f"  -> Model B: {len(df_b)} valid signal days")
    print(f"  -> Model C: {len(df_c)} valid signal days")
    
    cal_start = min(df_b.index.min(), df_c.index.min())
    cal_end = max(df_b.index.max(), df_c.index.max())
    
    # Backdate fetch by 7 days to ensure first calendar day has a valid T-1 Close for C2C Returns
    fetch_start = (cal_start - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    fetch_end = (cal_end + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
    
    print(f"[2/4] Downloading SPY OHLC Data via yfinance ({fetch_start} to {fetch_end})...")
    spy = yf.download("SPY", start=fetch_start, end=fetch_end, progress=False)
    
    if spy.empty:
        print("  -> ERROR: Failed to download SPY data.")
        return
        
    print(f"  -> Downloaded {len(spy)} trading days of SPY data.")
    
    # Flatten MultiIndex columns if yfinance returns them
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.get_level_values(0)
    
    print("[3/4] Calculating Strategies...")
    
    # Calculate returns
    spy['Return_O2C'] = (spy['Close'] - spy['Open']) / spy['Open']
    spy['Return_C2C'] = spy['Close'].pct_change()
    
    results = []
    
    for model_name, df_signals in [("Model_B", df_b), ("Model_C", df_c)]:
        df_merged = df_signals.join(spy, how='inner')
        
        # Ensure we don't have NaN returns (like the first day's C2C)
        df_merged = df_merged.dropna(subset=['Return_O2C', 'Return_C2C'])
        
        def calc_strat_return(row, ret_col):
            if row['Direction'] == 'LONG':
                return row[ret_col]
            elif row['Direction'] == 'SHORT':
                return -row[ret_col]
            else:
                return 0.0
                
        df_merged['Strat_Ret_O2C'] = df_merged.apply(lambda r: calc_strat_return(r, 'Return_O2C'), axis=1)
        df_merged['Strat_Ret_C2C'] = df_merged.apply(lambda r: calc_strat_return(r, 'Return_C2C'), axis=1)
        
        def is_hit(row, ret_col):
            if row['Direction'] == 'LONG' and row[ret_col] > 0:
                return 1
            elif row['Direction'] == 'SHORT' and row[ret_col] < 0:
                return 1
            elif row['Direction'] == 'CASH':
                return np.nan
            else:
                return 0
                
        df_merged['Hit_O2C'] = df_merged.apply(lambda r: is_hit(r, 'Return_O2C'), axis=1)
        df_merged['Hit_C2C'] = df_merged.apply(lambda r: is_hit(r, 'Return_C2C'), axis=1)
        
        valid_o2c = df_merged['Hit_O2C'].dropna()
        valid_c2c = df_merged['Hit_C2C'].dropna()
        
        hr_o2c = valid_o2c.mean() if len(valid_o2c) > 0 else 0
        hr_c2c = valid_c2c.mean() if len(valid_c2c) > 0 else 0
        
        # Cumulative product for strategy and SPY Baseline
        cum_ret_o2c = (1 + df_merged['Strat_Ret_O2C']).cumprod().iloc[-1] - 1
        cum_ret_c2c = (1 + df_merged['Strat_Ret_C2C']).cumprod().iloc[-1] - 1
        
        # True Baseline: BnH must use raw SPY DataFrame over the bounded signal period, not df_merged
        actual_start_dt = df_merged.index.min()
        actual_end_dt = df_merged.index.max()
        
        # Sliced SPY for exact calendar boundary
        spy_bounded = spy.loc[actual_start_dt:actual_end_dt]
        
        bh_ret_o2c = (1 + spy_bounded['Return_O2C']).cumprod().iloc[-1] - 1
        # C2C True Buy and Hold: Final Close / Initial Close - 1
        bh_ret_c2c = spy_bounded['Close'].iloc[-1] / spy_bounded['Close'].iloc[0] - 1
        
        # Risk stats (Sharpe ratio assuming 252 trading days and 0% risk free rate)
        vol_o2c = df_merged['Strat_Ret_O2C'].std() * np.sqrt(252)
        vol_c2c = df_merged['Strat_Ret_C2C'].std() * np.sqrt(252)
        
        sharpe_o2c = (df_merged['Strat_Ret_O2C'].mean() * 252) / vol_o2c if vol_o2c != 0 else 0
        sharpe_c2c = (df_merged['Strat_Ret_C2C'].mean() * 252) / vol_c2c if vol_c2c != 0 else 0
        
        long_count = (df_merged['Direction'] == 'LONG').sum()
        short_count = (df_merged['Direction'] == 'SHORT').sum()
        
        results.append({
            "Model": model_name,
            "Total_Trades": len(valid_o2c),
            "LONG_Count": long_count,
            "SHORT_Count": short_count,
            "HitRate_O2C": hr_o2c,
            "HitRate_C2C": hr_c2c,
            "CumRet_O2C": cum_ret_o2c,
            "CumRet_C2C": cum_ret_c2c,
            "Sharpe_O2C": sharpe_o2c,
            "Sharpe_C2C": sharpe_c2c,
            "BnH_O2C": bh_ret_o2c,
            "BnH_C2C": bh_ret_c2c
        })
        
    print("[4/4] Generating Report...")
    report_path = os.path.join(WORKSPACE, "hit_rate_accuracy_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📈 SPY Historical Hit Rate Validation Report\n\n")
        f.write("**Period Tested**: July 30, 2024 to July 30, 2026\n")
        f.write("**Ticker**: SPY (SPDR S&P 500 ETF Trust)\n\n")
        
        f.write("> [!NOTE]\n")
        f.write("> **Execution Methodology:**\n")
        f.write("> - **O2C (Open-to-Close)**: Enter at Market Open, Exit at Market Close.\n")
        f.write("> - **C2C (Close-to-Close)**: Enter at Prior Day Close, Exit at Current Day Close.\n")
        f.write("> - **Hit Rate**: Measured purely as `(Profitable directional trades) / (Total LONG + SHORT)`\n")
        f.write("> - **Friction**: 0% slippage and $0 commissions modeled for theoretical edge discovery.\n\n")
        
        for r in results:
            f.write(f"## {r['Model']} Performance\n")
            f.write(f"- **Days Scored**: {r['Total_Trades']} (LONG: {r['LONG_Count']} | SHORT: {r['SHORT_Count']})\n")
            f.write(f"- **O2C Hit Rate**: {r['HitRate_O2C']*100:.2f}%\n")
            f.write(f"- **C2C Hit Rate**: {r['HitRate_C2C']*100:.2f}%\n\n")
            
            f.write("### Cumulative Returns & Risk\n")
            f.write("| Metric | Strategy (O2C) | SPY Baseline (O2C) | Strategy (C2C) | SPY Baseline (C2C) |\n")
            f.write("|---|---|---|---|---|\n")
            f.write(f"| **Total Return** | **{r['CumRet_O2C']*100:.2f}%** | {r['BnH_O2C']*100:.2f}% | **{r['CumRet_C2C']*100:.2f}%** | {r['BnH_C2C']*100:.2f}% |\n")
            f.write(f"| **Sharpe Ratio** | {r['Sharpe_O2C']:.2f} | N/A | {r['Sharpe_C2C']:.2f} | N/A |\n\n")
            
    print(f"[SUCCESS] Report written to: {report_path}")

if __name__ == "__main__":
    main()
