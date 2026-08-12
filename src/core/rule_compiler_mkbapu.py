import pandas as pd
import numpy as np
from datetime import timedelta
import sys
import os

# Ensure we can import ephemeris_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ephemeris_engine import compute_all_features
except ImportError:
    print("WARNING: Could not import ephemeris_engine. Running in mock mode.")
    # Mock for testing if ephemeris_engine is missing dependencies
    def compute_all_features(dt):
        return {"house_placidus_1_cusp": (dt.hour * 15) % 360}

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", 
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
]

def apply_mkbapu_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame of market data (with DatetimeIndex in UTC)
    and applies the MK Bapu Astrological strategy rules.
    """
    df = df.copy()
    
    # 1. Compute Lagna for every row
    asc_degrees = []
    for dt in df.index:
        feats = compute_all_features(dt)
        asc_degrees.append(feats.get("house_placidus_1_cusp", 0.0))
        
    df['lagna_degree'] = asc_degrees
    df['lagna_rashi_idx'] = (df['lagna_degree'] // 30).astype(int)
    df['lagna_rashi_name'] = df['lagna_rashi_idx'].map(lambda x: RASHI_NAMES[x % 12])
    
    # 2. Detect Rashi Change (Lagna Transit)
    df['rashi_changed'] = df['lagna_rashi_idx'] != df['lagna_rashi_idx'].shift(1)
    df.loc[df.index[0], 'rashi_changed'] = True # First row is a start by definition
    
    # 3. Track state
    rashi_start_prices = []
    pushkar_start_prices = []
    
    current_rashi_start_price = None
    vrishchika_start_time = None
    current_pushkar_price = None
    
    for i in range(len(df)):
        dt = df.index[i]
        
        # New Rashi Started
        if df['rashi_changed'].iloc[i]:
            current_rashi_start_price = df['Open'].iloc[i]
            current_pushkar_price = None # Reset pushkar
            
            if df['lagna_rashi_name'].iloc[i] == 'Vrishchika':
                vrishchika_start_time = dt
            else:
                vrishchika_start_time = None
                
        # Check Pushkar (60 minutes delay)
        if vrishchika_start_time is not None:
            mins_elapsed = (dt - vrishchika_start_time).total_seconds() / 60.0
            if mins_elapsed >= 60.0 and current_pushkar_price is None:
                current_pushkar_price = df['Open'].iloc[i]
                
        rashi_start_prices.append(current_rashi_start_price)
        pushkar_start_prices.append(current_pushkar_price)
        
    df['rashi_start_price'] = rashi_start_prices
    df['pushkar_start_price'] = pushkar_start_prices
    
    # 4. Generate the final Features for ML
    df['dist_to_lagna_start_price'] = df['Close'] - df['rashi_start_price']
    df['is_vrishchika_pushkar_active'] = df['pushkar_start_price'].notna().astype(int)
    
    return df

if __name__ == "__main__":
    # Quick test harness
    print("Testing MK Bapu Rule Compiler...")
    
    # Generate mock 15m data
    dti = pd.date_range("2026-05-25 04:00:00", periods=50, freq="15min", tz="UTC")
    mock_df = pd.DataFrame({
        'Open': np.random.randn(50).cumsum() + 100,
        'Close': np.random.randn(50).cumsum() + 100
    }, index=dti)
    
    res_df = apply_mkbapu_rules(mock_df)
    
    cols = ['lagna_rashi_name', 'rashi_changed', 'Open', 'rashi_start_price', 'dist_to_lagna_start_price', 'pushkar_start_price']
    print(res_df[cols].head(30))
