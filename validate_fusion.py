import pandas as pd
import numpy as np
import sys
import time

def validate():
    print("Loading dataset...")
    df = pd.read_parquet("data/spy_anomalies_omni_vedic_supreme.parquet")
    
    passed = True
    
    # 1. Row count
    if len(df) == 1408:
        print("PASS ROW COUNT: 1408")
    else:
        print(f"FAIL ROW COUNT: Expected 1408, got {len(df)}")
        passed = False
        
    # 2. Column count
    if len(df.columns) > 200:
        print(f"PASS COLUMN COUNT: {len(df.columns)} > 200")
    else:
        print(f"FAIL COLUMN COUNT: Expected > 200, got {len(df.columns)}")
        passed = False
        
    # 3. Zero NaNs
    lon_cols = [c for c in df.columns if c.endswith("_Lon")]
    speed_cols = [c for c in df.columns if c.endswith("_Speed")]
    sign_cols = [c for c in df.columns if c.endswith("_Sign")]
    
    cols_to_check = lon_cols + speed_cols + sign_cols
    nan_counts = df[cols_to_check].isna().sum()
    if nan_counts.sum() == 0:
        print("PASS ZERO NaN POLICY: 0 NaNs in Lon, Speed, Sign cols")
    else:
        print("FAIL ZERO NaN POLICY FAILED. Cols with NaNs:")
        print(nan_counts[nan_counts > 0])
        passed = False
        
    # 4. SAV 337
    if (df['SAV_Total'] == 337).all():
        print("PASS SAV 337 INVARIANT: All rows have SAV_Total = 337")
    else:
        num_invalid = (df['SAV_Total'] != 337).sum()
        print(f"FAIL SAV 337 INVARIANT FAILED: {num_invalid} rows do not have 337")
        passed = False
        
    # 5. Jaimini Karaka Uniqueness
    jaimini_cols = ["Jaimini_AK", "Jaimini_AmK", "Jaimini_BK", "Jaimini_MK", "Jaimini_PK", "Jaimini_GK", "Jaimini_DK"]
    unique_counts = df[jaimini_cols].nunique(axis=1)
    if (unique_counts == 7).all():
        print("PASS JAIMINI KARAKA UNIQUENESS: All rows have 7 unique Karakas")
    else:
        num_invalid = (unique_counts != 7).sum()
        print(f"FAIL JAIMINI KARAKA UNIQUENESS FAILED: {num_invalid} rows do not have 7 unique Karakas")
        passed = False
        
    # 6. Longitude Range
    invalid_lon = False
    for col in lon_cols:
        if not ((df[col] >= 0) & (df[col] < 360)).all():
            invalid_lon = True
            print(f"FAIL LONGITUDE RANGE FAILED in {col}")
    if not invalid_lon:
        print("PASS LONGITUDE RANGE: All [0, 360)")
    else:
        passed = False
        
    # 7. Sign validity
    valid_signs = {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"}
    invalid_sign = False
    for col in sign_cols:
        if not df[col].isin(valid_signs).all():
            invalid_sign = True
            print(f"FAIL SIGN VALIDITY FAILED in {col}")
    if not invalid_sign:
        print("PASS SIGN VALIDITY: All signs valid")
    else:
        passed = False
        
    # 8. Bhava Range
    bhv_cols = [c for c in df.columns if c.startswith("Bhv_")]
    if len(bhv_cols) == 0:
        print("FAIL BHAVA RANGE FAILED: No Bhv_ columns found!")
        passed = False
    else:
        invalid_bhv = False
        for col in bhv_cols:
            if not ((df[col] >= 1) & (df[col] <= 12)).all():
                invalid_bhv = True
                print(f"FAIL BHAVA RANGE FAILED in {col}")
        if not invalid_bhv:
            print("PASS BHAVA RANGE: All [1, 12]")
        else:
            passed = False
            
    # 9. Angular distance
    ang_cols = [c for c in df.columns if c.startswith("Ang_")]
    if len(ang_cols) == 0:
        print("FAIL ANGULAR DISTANCE FAILED: No Ang_ columns found!")
        passed = False
    else:
        invalid_ang = False
        for col in ang_cols:
            if not ((df[col] >= 0) & (df[col] <= 180)).all():
                invalid_ang = True
                print(f"FAIL ANGULAR DISTANCE FAILED in {col}")
        if not invalid_ang:
            print("PASS ANGULAR DISTANCE RANGE: All [0, 180]")
        else:
            passed = False
            
    # 10. Shadbala Sanity
    sb_cols = [c for c in df.columns if c.startswith("Shadbala_") and c.endswith("_Rupas")]
    if len(sb_cols) == 0:
        print("FAIL SHADBALA SANITY FAILED: No Shadbala_*_Rupas columns found!")
        passed = False
    else:
        invalid_sb = False
        for col in sb_cols:
            if not ((df[col] > 0) & (df[col] < 30)).all():
                invalid_sb = True
                print(f"FAIL SHADBALA SANITY FAILED in {col}")
        if not invalid_sb:
            print("PASS SHADBALA SANITY: All positive and < 30")
        else:
            passed = False
            
    # 11. MTF Confluence
    if 'MTF_Confluence_Count' in df.columns:
        if (df['MTF_Confluence_Count'] >= 1).all():
            print("PASS MTF CONFLUENCE: All >= 1")
        else:
            print("FAIL MTF CONFLUENCE FAILED: Some rows have < 1")
            passed = False
    else:
        print("FAIL MTF CONFLUENCE FAILED: Column missing!")
        passed = False
        
    # 12. Vimshottari
    vim_cols = ["Vim_MD", "Vim_AD", "Vim_PD"]
    valid_lords = {"Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"}
    if all(c in df.columns for c in vim_cols):
        invalid_vim = False
        for col in vim_cols:
            if not df[col].isin(valid_lords).all():
                invalid_vim = True
                print(f"FAIL VIMSHOTTARI FAILED in {col}")
        if not invalid_vim:
            print("PASS VIMSHOTTARI DASHAS: Valid lords")
        else:
            passed = False
    else:
        print("FAIL VIMSHOTTARI FAILED: Columns missing!")
        passed = False
        
    if passed:
        print("\nALL CHECKS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME CHECKS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    validate()
