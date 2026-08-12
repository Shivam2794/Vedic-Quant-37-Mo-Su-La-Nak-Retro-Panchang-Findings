
import numpy as np
from numba import njit

# ---------------------------------------------------------------------------------
# VARGA VECTORIZATION (TRAP P2.3 FIX)
# ---------------------------------------------------------------------------------
@njit(cache=True)
def compute_varga_array(longitudes, varga_id):
    """
    TRAP P2.3 FIX: Vectorized Numba Varga execution.
    Consumes the entire 8038-day array of longitudes in a pure C-loop
    rather than choking on millions of Python scalar calls.
    """
    n = len(longitudes)
    varga_signs = np.zeros(n, dtype=np.int32)
    
    for i in range(n):
        lon = longitudes[i]
        sign = int(lon / 30.0)
        degree = lon % 30.0
        
        if varga_id == 1:
            varga_signs[i] = sign
            
        elif varga_id == 2:
            is_odd = (sign % 2 == 0)
            first_half = (degree < 15.0)
            if is_odd: varga_signs[i] = 4 if first_half else 3
            else: varga_signs[i] = 3 if first_half else 4
                
        elif varga_id == 9: # Navamsa
            part = int(degree / (30.0 / 9.0))
            varga_signs[i] = (sign * 9 + part) % 12
            
        # (Other vargas omitted for brevity, but structurally identical)
        else:
            varga_signs[i] = sign
            
    return varga_signs

# Other core features like Jaimini Karakas remain...
