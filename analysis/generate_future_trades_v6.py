import os
import json
import numpy as np
import pandas as pd
import swisseph as swe
import pytz
from master_trading_plan_v7 import V5ContinuousVedicEngine, load_celestial_matrix

def jd_from_dt(dt):
    """Convert UTC datetime to Julian Day"""
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

def generate_future_ephemeris(start_date, end_date):
    print(f"Generating Ephemeris for {start_date} to {end_date}...")
    # Generate business days (NYSE schedule approximation)
    nyse_tz = pytz.timezone('America/New_York')
    dates = pd.bdate_range(start=start_date, end=end_date)
    
    swe.set_ephe_path(None) # Use built-in Swiss Ephemeris
    
    bodies = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mercury': swe.MERCURY,
        'Venus': swe.VENUS,
        'Mars': swe.MARS,
        'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN,
        'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO
    }
    
    data = []
    for d in dates:
        # Market open at 9:30 AM EST/EDT
        dt_ny = pd.Timestamp(year=d.year, month=d.month, day=d.day, hour=9, minute=30, tz=nyse_tz)
        dt_utc = dt_ny.tz_convert('UTC')
        jd = jd_from_dt(dt_utc)
        
        row = {'date': d.strftime('%Y-%m-%d')}
        for b_name, b_id in bodies.items():
            # Tropical positions
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            pos, _ = swe.calc_ut(jd, b_id, flags)
            lon_trop = pos[0]
            lat_trop = pos[1]
            speed_trop = pos[3]
            
            # Equatorial positions (Declination)
            flags_eq = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL
            pos_eq, _ = swe.calc_ut(jd, b_id, flags_eq)
            declination = pos_eq[1]
            
            row[f"{b_name}_Geo_Lon_Sin"] = np.sin(np.radians(lon_trop))
            row[f"{b_name}_Geo_Lon_Cos"] = np.cos(np.radians(lon_trop))
            row[f"{b_name}_Geo_Speed"] = speed_trop
            row[f"{b_name}_Geo_Decl"] = declination
            
            if b_name == 'Moon':
                row['Moon_Geo_Lat'] = lat_trop
            
        data.append(row)
        
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df

def main():
    # 1. Generate future data
    future_df = generate_future_ephemeris('2026-08-01', '2028-08-01')
    
    # 2. Compute Tensors
    print("Computing Tensors...")
    engine = V5ContinuousVedicEngine(future_df)
    tensor_df = engine.compute_all_tensors()
    
    feature_cols = [c for c in tensor_df.columns if c != 'date']
    X = tensor_df[feature_cols].to_numpy(dtype=np.float64)
    dates = pd.to_datetime(tensor_df['date']).dt.strftime('%Y-%m-%d').tolist()
    
    # 3. Load Champion Model
    model_path = "v6_fold_models/fold_27_champion.json"
    print(f"Loading Model: {model_path}")
    with open(model_path, 'r') as f:
        champion = json.load(f)
        
    weights = np.array(champion['weights'])
    v_th = champion['v_th']
    stop_loss = champion['stop_loss']
    take_profit = champion['take_profit']
    max_leverage = champion['max_leverage']
    
    # 4. Project Signal & Extract Trades
    print("Projecting Trades...")
    S = X @ weights
    
    trades = []
    current_position = 0
    entry_date = None
    entry_signal = 0.0
    
    for i in range(len(S)):
        signal = S[i]
        d = dates[i]
        
        # Simple threshold cross logic for future projection
        if current_position == 0:
            if signal > v_th:
                current_position = 1
                entry_date = d
                entry_signal = signal
            elif signal < -v_th:
                current_position = -1
                entry_date = d
                entry_signal = signal
        else:
            # Exit conditions: Reversion to 0
            if (current_position == 1 and signal < 0) or (current_position == -1 and signal > 0):
                trades.append({
                    'Type': 'LONG' if current_position == 1 else 'SHORT',
                    'Entry_Date': entry_date,
                    'Entry_Signal_Force': entry_signal,
                    'Exit_Date': d,
                    'Exit_Signal_Force': signal
                })
                current_position = 0
                
    # 5. Write Report
    report_path = "future_trades_2026_2028.md"
    print(f"Writing Report to {report_path}...")
    with open(report_path, 'w') as f:
        f.write("# Future Trades Projection (2026 - 2028)\n\n")
        f.write("> **Model**: Vedic Tensor Engine V6 (Walk-Forward Fold 27 Champion)\n")
        f.write(f"> **Activation Threshold ($v_{{th}}$)**: {v_th:.4f}\n")
        f.write(f"> **Optimized Stop Loss**: {stop_loss*100:.1f}%\n")
        f.write(f"> **Optimized Take Profit**: {take_profit*100:.1f}%\n")
        f.write(f"> **Max Leverage**: {max_leverage}x\n\n")
        
        f.write("## Projected Trades\n\n")
        if len(trades) == 0:
            f.write("*The planetary momentum does not exceed the activation friction threshold during this period.*")
        else:
            f.write("| Trade | Entry Date | Entry Signal | Exit Date | Exit Signal | Rules |\n")
            f.write("|---|---|---|---|---|---|\n")
            for t in trades:
                rules = f"SL: {stop_loss*100:.1f}%, TP: {take_profit*100:.1f}%"
                f.write(f"| **{t['Type']}** | {t['Entry_Date']} | {t['Entry_Signal_Force']:+.4f} | {t['Exit_Date']} | {t['Exit_Signal_Force']:+.4f} | {rules} |\n")
                
    print("Done!")

if __name__ == "__main__":
    main()


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
