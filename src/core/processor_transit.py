
import swisseph as swe
import numpy as np
from numba import njit

# ---------------------------------------------------------------------------------
# TAJIKA DEEPTAMSHA ORBS (TRAP P2.6 FIX)
# ---------------------------------------------------------------------------------
DEEPTAMSHAS = {
    0: 15.0, # Sun
    1: 12.0, # Moon
    2: 8.0,  # Mars
    3: 7.0,  # Mercury
    4: 9.0,  # Jupiter
    5: 7.0,  # Venus
    6: 9.0   # Saturn
}

@njit(cache=True)
def check_ithasala_yoga(fast_lon, fast_speed, slow_lon, slow_speed, orb_fast, orb_slow):
    """
    TRAP P2.6 FIX: Strictly evaluates Tajika Ithasala Yogas handling Retrogrades.
    Application occurs when the two bodies are approaching each other.
    """
    allowed_orb = (orb_fast + orb_slow) / 2.0
    distance = (slow_lon - fast_lon) % 360.0
    
    if distance > 180.0:
        distance -= 360.0 # -180 to +180
        
    abs_distance = abs(distance)
    
    if abs_distance > allowed_orb:
        return False
        
    # Relative speed. If relative speed is closing the distance, it's applying.
    # distance is slow_lon - fast_lon.
    # Rate of change of distance = slow_speed - fast_speed.
    # If distance > 0 (slow is ahead), they are approaching if fast > slow (rate < 0).
    # If distance < 0 (fast is ahead), they are approaching if slow > fast (rate > 0).
    rate_of_change = slow_speed - fast_speed
    
    if distance > 0 and rate_of_change < 0:
        return True
    elif distance < 0 and rate_of_change > 0:
        return True
        
    return False

# ---------------------------------------------------------------------------------
# TARABALA LUNAR INGRESS ROOT-FINDER (TRAP P2.12 FIX)
# ---------------------------------------------------------------------------------
def get_moon_lon(jd):
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED | swe.FLG_SWIEPH
    pos, _ = swe.calc_ut(jd, swe.MOON, flags)
    return pos[0]

def calculate_lunar_ingress_array(start_jd, end_jd):
    """
    TRAP P2.12 FIX: Pre-calculates exact milliseconds of every Lunar Nakshatra ingress
    for the entire 31-year timeline to allow exact Ghati evaluation without skipping.
    """
    print("Calculating exact Lunar Nakshatra Ingress timeline...")
    ingress_jds = []
    
    NAK_LEN = 360.0 / 27.0
    current_jd = start_jd
    current_moon = get_moon_lon(current_jd)
    current_nak = int(current_moon / NAK_LEN)
    
    # Moon moves ~13.2 deg/day. We can step by 0.5 days safely.
    step = 0.5
    
    while current_jd <= end_jd + 2.0:
        next_jd = current_jd + step
        next_moon = get_moon_lon(next_jd)
        next_nak = int(next_moon / NAK_LEN)
        
        if next_nak != current_nak and not (current_nak == 26 and next_nak == 26):
            # Boundary crossed! Root find exact JD.
            target_boundary = ((current_nak + 1) % 27) * NAK_LEN
            
            jd_low = current_jd
            jd_high = next_jd
            
            for _ in range(20): # Binary search
                jd_mid = (jd_low + jd_high) / 2.0
                mid_lon = get_moon_lon(jd_mid)
                
                diff = (mid_lon - target_boundary) % 360.0
                if diff > 180.0: diff -= 360.0
                
                if abs(diff) < 0.0001:
                    break
                if diff > 0:
                    jd_high = jd_mid
                else:
                    jd_low = jd_mid
                    
            ingress_jds.append({
                "nak_num": (current_nak + 1) % 27,
                "ingress_jd": jd_mid
            })
            
            current_nak = (current_nak + 1) % 27
            
        current_jd = next_jd
        
    return pd.DataFrame(ingress_jds)

@njit(cache=True)
def check_tarabala_ghatis(current_jd, nak_start_jd, tara_type):
    """
    Only flags toxic Taras for their explicit Ghatis duration.
    1 Ghati = 24 minutes = 0.01666 days.
    """
    elapsed_days = current_jd - nak_start_jd
    elapsed_minutes = elapsed_days * 1440.0
    
    # Example logic placeholder
    return elapsed_minutes < 120.0
