
import numpy as np
from numba import njit

# Numba absolutely requires strongly typed input. We use @njit for C-speed without Python object overhead.

@njit(cache=True)
def get_varga_sign(longitude, varga):
    """
    Calculates the exact sign (0-11) of a given longitude for a specific Varga.
    Uses pure integer arithmetic (seconds of arc) to completely eliminate 
    floating-point boundary hallucination bugs.
    """
    # 1 sign = 30 degrees = 108,000,000 milli-seconds of arc. 
    # Max longitude = 360 degrees = 1,296,000,000 milli-seconds of arc.
    
    # We round to nearest integer milli-second to avoid float boundary issues
    total_seconds = int(round(longitude * 3600000.0))
    total_seconds = total_seconds % 1296000000 # keep within 360
    
    sign = total_seconds // 108000000
    sec = total_seconds % 108000000
    
    if varga == 1:
        return sign
        
    elif varga == 2: # Hora (2 segments)
        part = (sec * 2) // 108000000
        if sign % 2 == 0:
            return 4 if part == 0 else 3 # Leo / Cancer
        else:
            return 3 if part == 0 else 4 # Cancer / Leo
            
    elif varga == 3: # Drekkana (3 segments)
        part = (sec * 3) // 108000000
        return (sign + part * 4) % 12
        
    elif varga == 4: # Chaturthamsa (4 segments)
        part = (sec * 4) // 108000000
        return (sign + part * 3) % 12
        
    elif varga == 7: # Saptamsa (7 segments)
        part = (sec * 7) // 108000000
        if sign % 2 == 0:
            return (sign + part) % 12
        else:
            return (sign + 6 + part) % 12
            
    elif varga == 9: # Navamsa (9 segments)
        part = (sec * 9) // 108000000
        return (sign * 9 + part) % 12
        
    elif varga == 10: # Dasamsa (10 segments)
        part = (sec * 10) // 108000000
        if sign % 2 == 0:
            return (sign + part) % 12
        else:
            return (sign + 8 + part) % 12
            
    elif varga == 12: # Dwadasamsa (12 segments)
        part = (sec * 12) // 108000000
        return (sign + part) % 12
        
    elif varga == 16: # Shodasamsa (16 segments)
        part = (sec * 16) // 108000000
        start_sign = (sign % 3) * 4 # Movable->Aries(0), Fixed->Leo(4), Dual->Sag(8)
        return (start_sign + part) % 12
        
    elif varga == 20: # Vimsamsa (20 segments)
        part = (sec * 20) // 108000000
        mod = sign % 3
        if mod == 0: start_sign = 0   # Aries
        elif mod == 1: start_sign = 8 # Sagittarius
        else: start_sign = 4          # Leo
        return (start_sign + part) % 12
        
    elif varga == 24: # Chaturvimsamsa (24 segments)
        part = (sec * 24) // 108000000
        if sign % 2 == 0:
            return (4 + part) % 12 # Leo
        else:
            return (3 + part) % 12 # Cancer
            
    elif varga == 27: # Saptavimsamsa (27 segments)
        part = (sec * 27) // 108000000
        start_sign = (sign % 4) * 3 
        return (start_sign + part) % 12
        
    elif varga == 30: # Trimsamsa (uneven degrees, uses lookup bounds)
        if sign % 2 == 0: # Odd signs
            if sec < 18000000: return 0      # 0-5 deg -> Aries
            elif sec < 36000000: return 10   # 5-10 deg -> Aquarius
            elif sec < 64800000: return 8    # 10-18 deg -> Sagittarius
            elif sec < 90000000: return 2    # 18-25 deg -> Gemini
            else: return 6                # 25-30 deg -> Libra
        else: # Even signs
            if sec < 18000000: return 1      # 0-5 deg -> Taurus
            elif sec < 43200000: return 5    # 5-12 deg -> Virgo
            elif sec < 72000000: return 11   # 12-20 deg -> Pisces
            elif sec < 90000000: return 9    # 20-25 deg -> Capricorn
            else: return 7                # 25-30 deg -> Scorpio
            
    elif varga == 40: # Khavedamsa (40 segments)
        part = (sec * 40) // 108000000
        if sign % 2 == 0:
            return (0 + part) % 12
        else:
            return (6 + part) % 12
            
    elif varga == 45: # Akshavedamsa (45 segments)
        part = (sec * 45) // 108000000
        start_sign = (sign % 3) * 4
        return (start_sign + part) % 12
        
    elif varga == 60: # Shashtiamsa (60 segments)
        part = (sec * 60) // 108000000
        return (sign + part) % 12

    return sign

@njit(cache=True)
def get_all_vargas(longitude):
    """
    Returns an array of 15 Varga signs for the given longitude in one pass.
    Index 0 is D1, Index 1 is D2, etc. (mapped to specific vargas)
    """
    vargas = np.array([1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60], dtype=np.int32)
    results = np.zeros(16, dtype=np.int32)
    for i in range(16):
        results[i] = get_varga_sign(longitude, vargas[i])
    return results

