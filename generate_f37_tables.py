import pandas as pd
import numpy as np
import sys
import os

# Ensure we can import from src/core
sys.path.append(os.path.abspath('src/core'))
from master_trading_plan_v7 import load_celestial_matrix_v7

def main():
    print("Loading V7 Celestial Matrix...")
    # returns: merged_df, X, opens, highs, lows, closes, sma200, atr_5, atr_14, atr_21, vol20, feature_cols
    # wait, load_celestial_matrix_v7 returns 12 items:
    # merged_out, X, opens_arr, highs_arr, lows_arr, closes_arr, sma200, atr_5, atr_14, atr_21, vol20_arr, feature_cols
    res = load_celestial_matrix_v7()
    merged = res[0]
    
    print(f"Loaded {len(merged)} dates.")
    
    # We want Top 15 Bullish and Bearish dates for F37
    # F37_Grid_Bullish_Extreme
    # F37_Grid_Bearish_Extreme
    
    if 'F37_Grid_Bullish_Extreme' not in merged.columns or 'F37_Grid_Bearish_Extreme' not in merged.columns:
        print("Error: F37 features not found in V7 matrix.")
        return
        
    bullish = merged.sort_values(by='F37_Grid_Bullish_Extreme', ascending=False).head(15)
    bearish = merged.sort_values(by='F37_Grid_Bearish_Extreme', ascending=False).head(15)
    
    # Let's also look at forward returns.
    # Calculate 10-day forward return for context
    merged['Fwd_10D_Ret'] = merged['Close'].shift(-10) / merged['Close'] - 1.0
    
    # Remap
    bullish = merged.loc[bullish.index]
    bearish = merged.loc[bearish.index]
    
    md = "# F37: Nakshatra-based Grid Extremes - Top 15 Historical Conviction Dates\n\n"
    
    md += "## Top 15 Bullish Activations (Punarvasu + Retrograde Venus/Saturn)\n\n"
    md += "| Date | F37 Bullish Score | Close Price | 10D Forward Return |\n"
    md += "|---|---|---|---|\n"
    for _, row in bullish.iterrows():
        ret_str = f"{row['Fwd_10D_Ret']:.2%}" if pd.notna(row['Fwd_10D_Ret']) else "N/A"
        md += f"| {row.name.strftime('%Y-%m-%d')} | {row['F37_Grid_Bullish_Extreme']:.4f} | ${row['Close']:.2f} | {ret_str} |\n"
        
    md += "\n## Top 15 Bearish Activations (Swati + Retrograde Mercury/Jupiter)\n\n"
    md += "| Date | F37 Bearish Score | Close Price | 10D Forward Return |\n"
    md += "|---|---|---|---|\n"
    for _, row in bearish.iterrows():
        ret_str = f"{row['Fwd_10D_Ret']:.2%}" if pd.notna(row['Fwd_10D_Ret']) else "N/A"
        md += f"| {row.name.strftime('%Y-%m-%d')} | {row['F37_Grid_Bearish_Extreme']:.4f} | ${row['Close']:.2f} | {ret_str} |\n"
        
    with open('F37_Nakshatra_Tables.md', 'w') as f:
        f.write(md)
        
    print("Saved to F37_Nakshatra_Tables.md")

if __name__ == '__main__':
    main()
