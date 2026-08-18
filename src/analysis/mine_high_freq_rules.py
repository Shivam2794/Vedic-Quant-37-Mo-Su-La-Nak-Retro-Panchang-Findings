import pandas as pd
import numpy as np

p_anom = 'data/spy_anomalies_omni_vedic_supreme.parquet'
p_base = 'data/spy_continuous_rth_omni_vedic_baseline.parquet'

df_a = pd.read_parquet(p_anom)
df_b = pd.read_parquet(p_base)

dir_col = 'Candle_Direction'
green_mask = (df_a[dir_col].astype(str).str.upper() == 'GREEN').values
red_mask = (df_a[dir_col].astype(str).str.upper() == 'RED').values
total_anom = len(df_a)
total_base = len(df_b)

df_a['Year'] = pd.to_datetime(df_a['Datetime_UTC']).dt.year
df_a['Date'] = pd.to_datetime(df_a['Datetime_UTC']).dt.date

years_span = df_a['Year'].max() - df_a['Year'].min() + 1

fast_cols = [
    'Moon_Nakshatra', 'Moon_Sign', 'Moon_Kakshya', 'Lagna_NYSE_Sign', 'Lagna_NYSE_Nakshatra',
    'Hour_Of_Day', 'Bhv_Moon_Lagna', 'Bhv_Sun_Moon', 'Bhv_Moon_Mars', 'Bhv_Moon_Saturn',
    'Bhv_Moon_Jupiter', 'Bhv_Moon_Venus', 'Bhv_Moon_Mercury', 'Bhv_Moon_Rahu', 'Bhv_Moon_Ketu',
    'Mercury_Kakshya', 'Venus_Kakshya', 'Mars_Kakshya', 'Sun_Kakshya', 'Saturn_Kakshya',
    'SPY_Gochar_Moon_to_Lagna_Bhv', 'SPY_Gochar_Moon_to_Moon_Bhv',
    'USA_Gochar_Moon_to_Moon_Bhv', 'NYSE_Gochar_Moon_to_Moon_Bhv',
    'SPY_Gochar_Mars_to_Moon_Bhv', 'USA_Gochar_Mars_to_Moon_Bhv'
]

def mine_combinations(target_direction, min_conf=0.70, min_support=20):
    t_mask = green_mask if target_direction == 'BULLISH' else red_mask
    rules = []
    
    # 1-way
    for col in fast_cols:
        if col not in df_a.columns: continue
        for val in df_a[col].dropna().unique():
            m_a = (df_a[col] == val).values
            k_a = int(m_a.sum())
            if k_a < min_support: continue
            
            k_t = int((m_a & t_mask).sum())
            conf = k_t / k_a
            if conf >= min_conf:
                u_dates = df_a.loc[m_a & t_mask, 'Date'].nunique()
                u_years = df_a.loc[m_a & t_mask, 'Year'].nunique()
                if u_dates >= 8 and u_years >= 5:
                    k_b = int((df_b[col] == val).sum()) if col in df_b.columns else 0
                    p_a = k_t / total_anom
                    p_b_smooth = (k_b + 1.0) / (total_base + 10.0)
                    lift = p_a / p_b_smooth
                    rules.append({
                        'Rule': f'[{col} == {val}]',
                        'Direction': target_direction,
                        'Target_Wins': k_t,
                        'Total_Signals': k_a,
                        'Confidence_Pct': round(conf * 100.0, 1),
                        'Lift_Ratio': round(lift, 2),
                        'Distinct_Dates': u_dates,
                        'Distinct_Years': u_years,
                        'Annual_Frequency': round(k_t / u_years, 1)
                    })
                    
    # 2-way
    for i in range(len(fast_cols)):
        c1 = fast_cols[i]
        if c1 not in df_a.columns: continue
        for j in range(i + 1, len(fast_cols)):
            c2 = fast_cols[j]
            if c2 not in df_a.columns: continue
            
            vals1 = df_a[c1].value_counts().head(8).index
            vals2 = df_a[c2].value_counts().head(8).index
            
            for v1 in vals1:
                m1_a = (df_a[c1] == v1).values
                for v2 in vals2:
                    m2_a = m1_a & (df_a[c2] == v2).values
                    k_a = int(m2_a.sum())
                    if k_a < min_support: continue
                    
                    k_t = int((m2_a & t_mask).sum())
                    conf = k_t / k_a
                    if conf >= min_conf:
                        u_dates = df_a.loc[m2_a & t_mask, 'Date'].nunique()
                        u_years = df_a.loc[m2_a & t_mask, 'Year'].nunique()
                        if u_dates >= 8 and u_years >= 5:
                            k_b = int(((df_b[c1] == v1) & (df_b[c2] == v2)).sum()) if (c1 in df_b.columns and c2 in df_b.columns) else 0
                            p_a = k_t / total_anom
                            p_b_smooth = (k_b + 1.0) / (total_base + 10.0)
                            lift = p_a / p_b_smooth
                            rules.append({
                                'Rule': f'[{c1} == {v1}] AND [{c2} == {v2}]',
                                'Direction': target_direction,
                                'Target_Wins': k_t,
                                'Total_Signals': k_a,
                                'Confidence_Pct': round(conf * 100.0, 1),
                                'Lift_Ratio': round(lift, 2),
                                'Distinct_Dates': u_dates,
                                'Distinct_Years': u_years,
                                'Annual_Frequency': round(k_t / u_years, 1)
                            })
                            
    df_out = pd.DataFrame(rules)
    if not df_out.empty:
        # Deduplicate redundant Gochar aliases
        df_out = df_out.sort_values(by=['Confidence_Pct', 'Target_Wins'], ascending=[False, False])
    return df_out

print("================================================================================")
print("TOP HIGH-FREQUENCY BEARISH CRASH COMBINATIONS (>= 70% WIN RATE, >= 8 DATES, >= 5 YEARS)")
print("================================================================================")
df_bear = mine_combinations('BEARISH', min_conf=0.72, min_support=20)
print(df_bear.head(15).to_string(index=False))

print("\n================================================================================")
print("TOP HIGH-FREQUENCY BULLISH RALLY COMBINATIONS (>= 50% BULLISH OVERWEIGHT, >= 8 DATES, >= 5 YEARS)")
print("================================================================================")
# Note: Baseline bullish is ~36.9%. So any rule >= 55%-65% is heavily bullish skewed!
df_bull = mine_combinations('BULLISH', min_conf=0.52, min_support=20)
print(df_bull.head(15).to_string(index=False))
