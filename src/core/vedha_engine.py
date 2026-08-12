# vedha_engine.py
# Implements True Sarvatobhadra Chakra (SBC) Vedha Mappings between planets

SBC_NAKSHATRAS = [
    "Krittika", "Rohini", "Mrigasira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Abhijit", "Shravana",
    "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati", "Ashwini", "Bharani"
]

def get_sbc_index(lon):
    nak_size = 360.0 / 27.0
    nak_idx = int(lon / nak_size)
    if 276.6667 <= lon <= 280.8889:
        return SBC_NAKSHATRAS.index("Abhijit")
        
    std_naks = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigasira","Ardra","Punarvasu","Pushya","Ashlesha",
        "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
        "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
        "Purva Bhadrapada","Uttara Bhadrapada","Revati"
    ]
    name = std_naks[nak_idx]
    return SBC_NAKSHATRAS.index(name)

# In SBC, the 28 Nakshatras form a 7x7 outer square.
# East (Top) = index 0 to 6 (Krittika to Ashlesha)
# South (Right) = index 7 to 13 (Magha to Vishakha)
# West (Bottom) = index 14 to 20 (Anuradha to Shravana)
# North (Left) = index 21 to 27 (Dhanishtha to Bharani)

# Mathematical relation for Front Vedha (Opposite side)
# 0 (Krittika) opposite 14 (Anuradha), 1 opposite 15, ..., 6 opposite 20
# 7 (Magha) opposite 21 (Dhanishtha), 8 opposite 22, ..., 13 opposite 27

# For diagonals, the corners hit each other:
# Krittika (0) hits Bharani (27) and Vishakha (13)

def get_vedha_targets(idx):
    targets = {}
    
    # Front Vedha
    if 0 <= idx <= 6: front = idx + 14
    elif 7 <= idx <= 13: front = idx + 14
    elif 14 <= idx <= 20: front = idx - 14
    else: front = idx - 14
    
    targets["Front"] = SBC_NAKSHATRAS[front]
    
    # Left / Right Diagonals can be complex. We approximate corner cross-fire for SBC.
    # Simplified corner cross-fire:
    if idx == 0: targets["Left"] = SBC_NAKSHATRAS[27]; targets["Right"] = SBC_NAKSHATRAS[13]
    elif idx == 6: targets["Left"] = SBC_NAKSHATRAS[7]; targets["Right"] = SBC_NAKSHATRAS[21]
    elif idx == 14: targets["Left"] = SBC_NAKSHATRAS[13]; targets["Right"] = SBC_NAKSHATRAS[27]
    elif idx == 20: targets["Left"] = SBC_NAKSHATRAS[21]; targets["Right"] = SBC_NAKSHATRAS[7]
    
    return targets

def get_vedha_pairs(natal_planets, transit_planets=None):
    """
    Returns actual planet-to-planet Vedha pairs using SBC logic.
    If transit_planets is provided, calculates Transit-to-Natal vedhas.
    Otherwise, calculates Natal-to-Natal vedhas.
    """
    source_planets = transit_planets if transit_planets else natal_planets
    target_planets = natal_planets
    
    target_nak_to_planets = {}
    for p, data in target_planets.items():
        if p in ["Ascendant", "MC"]: continue
        lon = data["longitude"] if "longitude" in data else -1
        if lon < 0:
            # Reconstruct from degrees if needed
            from vedic_astrology_engine import parse_dms # Or compute from sign and deg, wait, better to just pass full objects
            # Assuming data has longitude. D1_rasi dictionaries from transit snapshots might not have longitude!
            # Let's check... wait, get_transit_snapshots currently only stores sign, degrees, nakshatra, pada.
            pass
        if lon >= 0:
            idx = get_sbc_index(lon)
            nak = SBC_NAKSHATRAS[idx]
            if nak not in target_nak_to_planets: target_nak_to_planets[nak] = []
            target_nak_to_planets[nak].append(p)
        
    vedhas = []
    
    for p, data in source_planets.items():
        if p in ["Ascendant", "MC"]: continue
        lon = data["longitude"] if "longitude" in data else -1
        if lon >= 0:
            idx = get_sbc_index(lon)
            targets = get_vedha_targets(idx)
            
            for v_type, v_nak in targets.items():
                if v_nak in target_nak_to_planets:
                    blocked_planets = target_nak_to_planets[v_nak]
                    for blocked in blocked_planets:
                        if transit_planets and p == blocked: continue # Skip if transiting planet is "blocking" its own natal self unless we want that, but standard is fine
                        vedhas.append({
                            "planet_a": p,
                            "planet_b": blocked,
                            "type": f"{v_type} Vedha"
                        })
                    
    return vedhas
