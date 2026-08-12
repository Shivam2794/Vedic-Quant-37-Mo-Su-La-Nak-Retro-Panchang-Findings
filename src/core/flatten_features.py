import json
import pandas as pd
from datetime import datetime
import pytz

def get_dasha_at_date(sequence, target_dt):
    # Helper to find current MD, AD, PAD based on sequence from json
    from compute_full_features import get_3level_dasha
    # Sequence needs to be converted back to datetimes
    seq_dt = []
    for d in sequence:
        seq_dt.append({
            "lord": d["lord"],
            "start": datetime.strptime(d["start"], "%Y-%m-%d").replace(tzinfo=pytz.utc),
            "end": datetime.strptime(d["end"], "%Y-%m-%d").replace(tzinfo=pytz.utc),
            "years": d["years"]
        })
    return get_3level_dasha(seq_dt, target_dt)

def flatten_data():
    with open('ultimate_features_output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    rows = []
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for asset, asset_data in data.items():
        ticker = asset.split("_")[0] # e.g. SPY
        asset_type = asset.split("_")[1] # trading or conception
        
        # Natal Features (Static)
        natal_features = {}
        for p in planets:
            # D1
            if p in asset_data.get("D1_rasi", {}):
                natal_features[f"Natal_D1_{p}_Sign"] = asset_data["D1_rasi"][p].get("sign")
                natal_features[f"Natal_D1_{p}_Nak"] = asset_data["D1_rasi"][p].get("nakshatra")
            # D9
            if p in asset_data.get("D9_navamsa", {}):
                natal_features[f"Natal_D9_{p}_Sign"] = asset_data["D9_navamsa"][p]
            # D10
            if p in asset_data.get("D10_dasamsa", {}):
                natal_features[f"Natal_D10_{p}_Sign"] = asset_data["D10_dasamsa"][p]
                
            # Shadbala
            if p in asset_data.get("shadbala", {}):
                natal_features[f"Natal_Shadbala_{p}"] = asset_data["shadbala"][p]["total_rupas"]
                
        # SAV
        for sign, pts in asset_data.get("ashtakvarga", {}).get("sarvashtakvarga", {}).items():
            natal_features[f"Natal_SAV_{sign}"] = pts
            
        # Iterate over transits
        for t_date_str, t_data in asset_data.get("transit_snapshots", {}).items():
            row = {
                "Asset": asset,
                "Ticker": ticker,
                "Type": asset_type,
                "Transit_Date": t_date_str
            }
            row.update(natal_features)
            
            # Dynamic Transit Features
            for p in planets:
                if p in t_data.get("D1_rasi", {}):
                    row[f"Transit_{p}_Sign"] = t_data["D1_rasi"][p].get("sign")
                    row[f"Transit_{p}_Nak"] = t_data["D1_rasi"][p].get("nakshatra")
                    
            # Transit Vedhas (Count blocked per natal planet)
            vedha_counts = {f"Transit_Vedha_Blocked_{p}": 0 for p in planets}
            for v in t_data.get("transit_vedhas", []):
                blocked = v.get("planet_b")
                if blocked in vedha_counts:
                    vedha_counts[f"Transit_Vedha_Blocked_{blocked}"] += 1
            row.update(vedha_counts)
            
            # Dasha at Transit
            t_dt = datetime.strptime(t_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            seq = asset_data.get("vimshottari_dasha", {}).get("full_sequence", [])
            if seq:
                try:
                    dasha = get_dasha_at_date(seq, t_dt)
                    if dasha:
                        row["Dasha_MD"] = dasha.get("MD_lord")
                        row["Dasha_AD"] = dasha.get("AD_lord")
                        row["Dasha_PAD"] = dasha.get("PAD_lord")
                except Exception as e:
                    pass
                    
            rows.append(row)
            
    df = pd.DataFrame(rows)
    # Categorical columns to encode
    cat_cols = [c for c in df.columns if "Sign" in c or "Nak" in c or "Dasha" in c]
    df = pd.get_dummies(df, columns=cat_cols, drop_first=False)
    
    df.to_csv("ml_features.csv", index=False)
    print(f"Flattened {len(rows)} transit snapshots into ml_features.csv with {df.shape[1]} columns.")

if __name__ == "__main__":
    flatten_data()
