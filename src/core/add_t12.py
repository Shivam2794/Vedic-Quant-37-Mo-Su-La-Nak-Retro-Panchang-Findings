
import csv

CSV_FILE = 'master_feature_columns.csv'

with open(CSV_FILE, encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def make_row(col_name, cat_code, cat_name, desc, data_type, tv='1'):
    return {
        'column_name': col_name,
        'category_code': cat_code,
        'category_name': cat_name,
        'description': desc,
        'data_type': data_type,
        'is_time_varying': tv
    }

new_rows = []

# 12a: ML Crosses (Cat 10)
new_rows.extend([
    make_row("MD_Lord_Current_Transit_Sign", "10", "ML Interaction Crosses", "Sign of current MD Lord", "INTEGER"),
    make_row("MD_Lord_Current_Transit_House", "10", "ML Interaction Crosses", "House of current MD Lord", "INTEGER"),
    make_row("AD_Lord_Current_Transit_Sign", "10", "ML Interaction Crosses", "Sign of current AD Lord", "INTEGER"),
    make_row("AD_Lord_Current_Transit_House", "10", "ML Interaction Crosses", "House of current AD Lord", "INTEGER"),
    make_row("MD_AD_Lord_Same_Sign_Flag", "10", "ML Interaction Crosses", "MD and AD lords conjoined", "INTEGER"),
    make_row("MD_Lord_Transiting_Natal_Sign_Flag", "10", "ML Interaction Crosses", "MD lord transiting own natal sign", "INTEGER"),
])

# 12b: Market Fixes
new_rows.extend([
    make_row("adx_14", "MKT_TECH", "Asset Technical Indicators", "Average Directional Index (14)", "FLOAT"),
    make_row("cci_14", "MKT_TECH", "Asset Technical Indicators", "Commodity Channel Index (14)", "FLOAT"),
    make_row("is_fed_meeting_day", "MKT_CAL", "Market Calendar Events", "Fed Meeting Day Flag", "INTEGER"),
    make_row("Yield_2Y", "MKT_CONTEXT", "Market Context Features", "2-Year Treasury Yield", "FLOAT"),
    make_row("Yield_Spread_10Y_2Y", "MKT_CONTEXT", "Market Context Features", "10Y - 2Y Yield Spread", "FLOAT"),
    make_row("Credit_Spread_HY", "MKT_CONTEXT", "Market Context Features", "High Yield Credit Spread", "FLOAT"),
    make_row("vol_realized_10d", "MKT_TARGET", "Market Target Labels", "10-day Realized Volatility", "FLOAT"),
    make_row("sharpe_21d", "MKT_TARGET", "Market Target Labels", "21-day Sharpe Ratio", "FLOAT"),
    make_row("max_drawdown_21d", "MKT_TARGET", "Market Target Labels", "21-day Max Drawdown", "FLOAT"),
])

# Append and save
rows.extend(new_rows)
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Added {len(new_rows)} columns for Task 12 (10, MKT).")
