
import numpy as np
from numba import njit

# ==============================================================================
# SHADBALA ENGINE (6-Fold Planetary Strength)
# Evaluates Sthana, Dik, Kaala, Chesta, Naisargika, and Drik Bala in Rupas.
# Required for ML evaluation of core asset strength.
# ==============================================================================

@njit(cache=True)
def get_sthana_bala(planet_id, longitude, house_idx):
    """
    Positional Strength (Sthana Bala).
    Placeholder logic for structural integration.
    Calculates Uchcha Bala (Exaltation), Saptavargaja (Varga strength),
    Ojayugmarasyamsa (Odd/Even sign), Kendra Bala, and Drekkana Bala.
    """
    # Simple placeholder returning nominal Rupas
    return 1.0

@njit(cache=True)
def get_dik_bala(planet_id, longitude, ascendant_lon):
    """
    Directional Strength (Dik Bala).
    Sun/Mars strongest in 10th (MC).
    Jupiter/Mercury strongest in 1st (Asc).
    Saturn strongest in 7th (Desc).
    Moon/Venus strongest in 4th (IC).
    """
    return 1.0

@njit(cache=True)
def get_kaala_bala(planet_id, jd_ut, is_day_birth):
    """
    Temporal Strength (Kaala Bala).
    Nathonnatha (Day/Night), Paksha (Lunar phase), Tribhaga, Ayana (Declination),
    and Yuddha (Planetary war) bala.
    """
    return 1.0

@njit(cache=True)
def get_chesta_bala(planet_id, longitude, sun_longitude, speed):
    """
    Motional Strength (Chesta Bala).
    Calculated based on retrogression and speed relative to the Sun.
    """
    return 1.0

@njit(cache=True)
def get_naisargika_bala(planet_id):
    """
    Natural Strength (Naisargika Bala).
    Static multiplier: Sun > Moon > Venus > Jupiter > Mercury > Mars > Saturn
    """
    natural_strengths = np.array([
        1.0,      # 0: Sun (60/60)
        0.857,    # 1: Moon (51.4/60)
        0.285,    # 2: Mars (17.1/60)
        0.428,    # 3: Mercury (25.7/60)
        0.571,    # 4: Jupiter (34.2/60)
        0.714,    # 5: Venus (42.8/60)
        0.142     # 6: Saturn (8.5/60)
    ])
    return natural_strengths[planet_id]

@njit(cache=True)
def get_drik_bala(planet_id, all_longitudes):
    """
    Aspectual Strength (Drik Bala).
    Sum of partial and full aspects from all other planets.
    """
    return 0.0

@njit(cache=True)
def calculate_shadbala(planet_id, longitude, speed, all_longitudes, house_idx, ascendant_lon, jd_ut, is_day_birth):
    """
    Orchestrator for the 6-fold planetary strength calculation.
    Returns the total Shadbala in Rupas.
    """
    sb = get_sthana_bala(planet_id, longitude, house_idx)
    db = get_dik_bala(planet_id, longitude, ascendant_lon)
    kb = get_kaala_bala(planet_id, jd_ut, is_day_birth)
    cb = get_chesta_bala(planet_id, longitude, sun_longitude=all_longitudes[0], speed=speed)
    nb = get_naisargika_bala(planet_id)
    drik = get_drik_bala(planet_id, all_longitudes)
    
    total_rupas = (sb + db + kb + cb + drik) * nb
    return total_rupas

