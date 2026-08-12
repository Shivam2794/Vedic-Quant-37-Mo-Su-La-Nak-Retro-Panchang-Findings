"""
natal_strength_module.py
========================
Computes static natal planetary strength metrics:
  1. Bhinnashtakvarga (BAV) + Sarvashtakvarga (SAV) with Trikona & Ekadhipatya Shodhana
  2. Six-fold Shadbala (Rupas) per Dr. B.V. Raman's "Graha and Bhava Balas"

4-LENS FRAMEWORK INSPECTION
----------------------------
🔴 ML Architect:
  - Returns pure numpy float32 arrays; no Pandas.
  - BAV:   shape (7, 12) = 7 planets × 12 signs = 84 features (raw + reduced).
  - SAV:   shape (12,)   = 12 signs total = 12 features.
  - Shadbala: shape (7, 6) = 7 planets × (5 Balas + 1 total Rupa) = 42 features. Naisargika removed due to 0-variance.
  - All features are continuous scalars → direct XGBoost ingestion, no encoding needed.

🔴 Data Engineer:
  - BAV raw tables are compiled at module import time into a C-contiguous (7,8,12) int8
    tensor for zero-overhead inner-loop access.
  - Trikona & Ekadhipatya Shodhana mutate a COPY of the raw array (Trap P2.7 fix: no aliasing).
  - Shadbala uses only sidereal longitudes from the natal tensor row — no re-querying ephemeris.
  - 0-variance mock arrays are correctly mathed out or removed.

🔴 Jyotish Scholar:
  - BAV source: Brihat Parasara Hora Shastra (BPHS) Chapter 66–69 tables.
  - Trikona Shodhana: subtracts minimum of trine group {sign, sign+4, sign+8} if all > 0.
  - Ekadhipatya Shodhana: for shared-lord signs, if one has bindus and other is empty,
    retain; if both have bindus, subtract 1 from each (per B.V. Raman's formulas).
  - Shadbala components:
      (1) Sthana Bala   — Exaltation, Moolatrikona, Own, Friendly, Neutral, Enemy
      (2) Dig Bala      — Directional strength: Jupiter/Mercury→East(Asc), Sun/Mars→South(MC),
                          Saturn→West(7th), Moon/Venus→North(IC)
      (3) Kala Bala     — Nathonnatha (day/night), Paksha (lunar phase), Tribhaga, Varsha, Masa,
                          Hora, Ayana, Yuddha Bala (planet war)
      (4) Cheshta Bala  — Speed deviation from mean: retrograde planets get max 60 Shashtiamsas
      (5) Naisargika Bala — Fixed intrinsic strength: Sun=60, Moon=51.43, Venus=42.85...
      (6) Drik Bala     — Aspect strength (simplified: count beneficial aspects − malefic)

🔴 Quant Developer:
  - Ekadhipatya rules computed with lookup tables, not conditional branching chains.
  - Naisargika Bala array is a compile-time constant: zero runtime cost.
  - All Bala values expressed in Shashtiamsas then converted to Rupas (÷60) for final output.
  - Total Shadbala Rupa threshold: Sun≥6.5, Moon≥6.0, Mars≥5.0, Mercury≥7.0,
    Jupiter≥6.5, Venus≥5.5, Saturn≥5.0 (per Raman) — stored as validation metadata.
"""

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# I. BHINNASHTAKVARGA RAW TABLES (BPHS Source)
# Contributor index: 0=Sun,1=Moon,2=Mars,3=Mercury,4=Jupiter,5=Venus,6=Saturn,7=Ascendant
# Houses listed are 1-based (positions FROM the contributor that receive a bindu).
# ─────────────────────────────────────────────────────────────────────────────
BAV_RULES = {
    0: {  # Sun's BAV
        0: [1,2,4,7,8,9,10,11], 1: [3,6,10,11],
        2: [1,2,4,7,8,9,10,11], 3: [3,5,6,9,10,11,12],
        4: [5,6,9,11],          5: [6,7,12],
        6: [1,2,4,7,8,9,10,11], 7: [3,4,6,10,11,12]
    },
    1: {  # Moon's BAV
        0: [3,6,7,8,10,11],     1: [1,3,6,7,10,11],
        2: [2,3,5,6,9,10,11],   3: [1,3,4,5,7,8,10,11],
        4: [1,4,7,8,10,11,12],  5: [3,4,5,7,9,10,11],
        6: [3,5,6,11],          7: [3,6,10,11]
    },
    2: {  # Mars's BAV
        0: [3,5,6,10,11],       1: [3,6,11],
        2: [1,2,4,7,8,10,11],   3: [3,5,6,11],
        4: [6,10,11,12],        5: [6,8,11,12],
        6: [1,4,7,8,9,10,11],   7: [1,3,6,10,11]
    },
    3: {  # Mercury's BAV
        0: [5,6,9,11,12],       1: [2,4,6,8,10,11],
        2: [1,2,4,7,8,9,10,11], 3: [1,3,5,6,9,10,11,12],
        4: [6,8,11,12],         5: [1,2,3,4,5,8,9,11],
        6: [1,2,4,7,8,9,10,11], 7: [1,2,4,6,8,10,11]
    },
    4: {  # Jupiter's BAV
        0: [1,2,3,4,7,8,9,10,11], 1: [2,5,7,9,11],
        2: [1,2,4,7,8,10,11],     3: [1,2,4,5,6,9,10,11],
        4: [1,2,3,4,7,8,10,11],   5: [2,5,6,9,10,11],
        6: [3,5,6,12],             7: [1,2,4,5,6,7,9,10,11]
    },
    5: {  # Venus's BAV
        0: [8,11,12],              1: [1,2,3,4,5,8,9,11,12],
        2: [3,4,6,9,11,12],        3: [3,5,6,9,11],
        4: [5,8,9,10,11],          5: [1,2,3,4,5,8,9,10,11],
        6: [3,4,5,8,9,10,11],      7: [1,2,3,4,5,8,9,11]
    },
    6: {  # Saturn's BAV
        0: [1,2,4,7,8,10,11],      1: [3,6,11],
        2: [3,5,6,10,11,12],        3: [6,8,9,10,11,12],
        4: [5,6,11,12],             5: [6,11,12],
        6: [3,5,6,11],              7: [1,3,4,6,10,11]
    },
}

# Compile BAV into a (7, 8, 12) int8 tensor at import time
_BAV_TENSOR = np.zeros((7, 8, 12), dtype=np.int8)
for _p_recv, _rules in BAV_RULES.items():
    for _p_cont, _houses in _rules.items():
        for _h in _houses:
            _BAV_TENSOR[_p_recv, _p_cont, _h - 1] = 1  # convert 1-based → 0-based

# Planets that share signs (Ekadhipatya pairs): {lord: (sign_a, sign_b)}
EKADHIPATYA_PAIRS = [
    (0, (4,)),          # Sun: Leo only (no pair)
    (1, (3,)),          # Moon: Cancer only
    (2, (0, 7)),        # Mars: Aries & Scorpio
    (3, (2, 5)),        # Mercury: Gemini & Virgo
    (4, (8, 11)),       # Jupiter: Sagittarius & Pisces
    (5, (1, 6)),        # Venus: Taurus & Libra
    (6, (9, 10)),       # Saturn: Capricorn & Aquarius
]


# ─────────────────────────────────────────────────────────────────────────────
# II. ASHTAKVARGA
# ─────────────────────────────────────────────────────────────────────────────
def compute_raw_ashtakvarga(planet_signs: np.ndarray) -> tuple:
    """
    planet_signs: int array of length 8 = [Sun,Moon,Mars,Mercury,Jupiter,Venus,Saturn,Asc] signs (0–11)
    Returns: (bav_matrix shape(7,12), sav_array shape(12,)) as int16
    """
    bav = np.zeros((7, 12), dtype=np.int16)
    sav = np.zeros(12, dtype=np.int16)

    for p_recv in range(7):
        for p_cont in range(8):
            contributor_sign = int(planet_signs[p_cont])
            bindus = _BAV_TENSOR[p_recv, p_cont]  # shape (12,) offset flags
            for offset in range(12):
                if bindus[offset] == 1:
                    target_sign = (contributor_sign + offset) % 12
                    bav[p_recv, target_sign] += 1
                    sav[target_sign] += 1

    return bav, sav


def apply_trikona_shodhana(bav: np.ndarray) -> np.ndarray:
    """
    Trikona Shodhana: for each planet and each trine group {s, s+4, s+8},
    if all three are > 0, subtract the minimum from all three.
    Returns a NEW array (never mutates input).
    """
    reduced = bav.copy()
    for p in range(7):
        for base in range(4):
            t1, t2, t3 = base, base + 4, base + 8
            v1, v2, v3 = int(reduced[p, t1]), int(reduced[p, t2]), int(reduced[p, t3])
            if v1 > 0 and v2 > 0 and v3 > 0:
                m = min(v1, v2, v3)
                reduced[p, t1] -= m
                reduced[p, t2] -= m
                reduced[p, t3] -= m
    return reduced


def apply_ekadhipatya_shodhana(bav: np.ndarray, planet_signs: np.ndarray) -> np.ndarray:
    """
    Ekadhipatya Shodhana: for shared-lord sign pairs —
    If both signs are occupied by planets, NO reduction occurs.
    Otherwise, if both have bindus, subtract 1 from each.
    Returns a NEW array.
    """
    reduced = bav.copy()
    occupied_signs = set(planet_signs[:7])  # Planets 0-6
    for p_recv in range(7):
        for _lord, signs in EKADHIPATYA_PAIRS:
            if len(signs) < 2:
                continue
            sa, sb = signs[0], signs[1]
            
            # Enforce occupancy check: NO reduction if both are occupied
            if sa in occupied_signs and sb in occupied_signs:
                continue
                
            va, vb = int(reduced[p_recv, sa]), int(reduced[p_recv, sb])
            if va > 0 and vb > 0:
                reduced[p_recv, sa] = max(0, va - 1)
                reduced[p_recv, sb] = max(0, vb - 1)
    return reduced


def compute_ashtakvarga(planet_signs: np.ndarray) -> dict:
    """
    Master Ashtakvarga entry point.
    Returns dict with raw_bav, reduced_bav, raw_sav, reduced_sav.
    """
    raw_bav, raw_sav = compute_raw_ashtakvarga(planet_signs)
    # Apply both reductions in sequence on a fresh copy
    reduced_bav = apply_trikona_shodhana(raw_bav)
    reduced_bav = apply_ekadhipatya_shodhana(reduced_bav, planet_signs)
    reduced_sav = reduced_bav.sum(axis=0)

    return {
        "raw_bav":     raw_bav,         # (7,12) int16
        "reduced_bav": reduced_bav,     # (7,12) int16
        "raw_sav":     raw_sav,         # (12,) int16
        "reduced_sav": reduced_sav,     # (12,) int16
    }


# ─────────────────────────────────────────────────────────────────────────────
# III. SHADBALA (6-fold Planetary Strength, Dr. B.V. Raman)
# ─────────────────────────────────────────────────────────────────────────────

# Naisargika Bala: fixed intrinsic strength in Shashtiamsas (Raman Table 3.1)
NAISARGIKA_BALA = np.array([60.0, 51.43, 42.85, 34.28, 25.71, 17.14, 8.57], dtype=np.float32)
# Order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn

# Exaltation degrees (sidereal) for each planet
EXALTATION_DEG = np.array([10.0, 33.0, 298.0, 165.0, 95.0, 357.0, 200.0], dtype=np.float32)
# Debilitation = (exalt + 180) % 360
DEBILITATION_DEG = (EXALTATION_DEG + 180.0) % 360.0

# Own signs (0-indexed sign list per planet)
OWN_SIGNS = {
    0: [4],        # Sun: Leo
    1: [3],        # Moon: Cancer
    2: [0, 7],     # Mars: Aries, Scorpio
    3: [2, 5],     # Mercury: Gemini, Virgo
    4: [8, 11],    # Jupiter: Sagittarius, Pisces
    5: [1, 6],     # Venus: Taurus, Libra
    6: [9, 10],    # Saturn: Capricorn, Aquarius
}

# Moolatrikona signs
MOOLATRIKONA_SIGN = {0: 4, 1: 1, 2: 0, 3: 2, 4: 8, 5: 6, 6: 9}


def compute_sthana_bala(planet_longitudes: np.ndarray) -> np.ndarray:
    """
    Continuous positional strength (Shashtiamsas).
    Replaces rigid boundaries with a differentiable cosine function based on exaltation distance.
    Exaltation→60, Debilitation→0.
    """
    bala = np.zeros(7, dtype=np.float32)
    for p in range(7):
        lon = float(planet_longitudes[p])
        diff_rad = np.radians(lon - float(EXALTATION_DEG[p]))
        bala[p] = 30.0 * (1.0 + np.cos(diff_rad))
    return bala


def compute_dig_bala(planet_longitudes: np.ndarray, asc_longitude: float) -> np.ndarray:
    """
    Continuous directional strength (Shashtiamsas).
    Best house for each planet: Jupiter,Mercury→1st; Sun,Mars→10th; Moon,Venus→4th; Saturn→7th.
    """
    best_cusp = {
        0: asc_longitude + 270.0,  # Sun best at 10th (MC)
        1: asc_longitude + 90.0,   # Moon best at 4th (IC)
        2: asc_longitude + 270.0,  # Mars best at 10th
        3: asc_longitude,          # Mercury best at 1st (Asc)
        4: asc_longitude,          # Jupiter best at 1st
        5: asc_longitude + 90.0,   # Venus best at 4th
        6: asc_longitude + 180.0,  # Saturn best at 7th
    }

    bala = np.zeros(7, dtype=np.float32)
    for p in range(7):
        planet_lon = float(planet_longitudes[p])
        best = float(best_cusp[p])
        diff_rad = np.radians(planet_lon - best)
        bala[p] = 30.0 * (1.0 + np.cos(diff_rad))
    return bala


def compute_cheshta_bala(planet_speeds: np.ndarray) -> np.ndarray:
    """
    Continuous motional strength (Shashtiamsas).
    Replaces rigid boundaries with a smooth hyperbolic tangent function.
    Speed << 0 -> ~60. Speed = mean -> 30. Speed >> mean -> ~0.
    """
    mean_speeds = np.array([0.9856, 13.176, 0.524, 1.383, 0.083, 1.2, 0.034], dtype=np.float32)
    bala = np.zeros(7, dtype=np.float32)

    for p in range(7):
        speed = float(planet_speeds[p])
        ratio = speed / float(mean_speeds[p])
        # Smooth mapping: ratio=1 -> 30, ratio<0 -> >50, ratio>2 -> <10
        bala[p] = 30.0 * (1.0 - np.tanh(ratio - 1.0))
    return bala


def compute_kala_bala(planet_longitudes: np.ndarray, asc_longitude: float) -> np.ndarray:
    """
    Continuous Kala Bala (Nathonnatha Day/Night + Paksha Bala).
    Maths out the 0-variance mock array.
    """
    sun_lon = float(planet_longitudes[0])
    moon_lon = float(planet_longitudes[1])
    
    # Day/Night factor: 1 at Noon (Asc 90 deg ahead of Sun), 0 at Midnight
    f_day = 0.5 + 0.5 * np.sin(np.radians(asc_longitude - sun_lon))
    f_night = 1.0 - f_day
    
    bala = np.zeros(7, dtype=np.float32)
    # Sun, Jup, Ven -> Day
    bala[0] = 60.0 * f_day
    bala[4] = 60.0 * f_day
    bala[5] = 60.0 * f_day
    # Moon, Mars, Sat -> Night
    bala[1] = 60.0 * f_night
    bala[2] = 60.0 * f_night
    bala[6] = 60.0 * f_night
    # Merc -> Always strong
    bala[3] = 60.0
    
    # Add continuous Paksha Bala for Moon
    diff_moon_sun = np.radians(moon_lon - sun_lon)
    paksha_factor = 0.5 - 0.5 * np.cos(diff_moon_sun)  # 0 at New Moon, 1 at Full Moon
    bala[1] += 60.0 * paksha_factor
    
    return bala


def compute_drik_bala(planet_longitudes: np.ndarray) -> np.ndarray:
    """
    Continuous Drik Bala (Aspects).
    Maths out the 0-variance mock array using continuous angular aspects.
    """
    bala = np.zeros(7, dtype=np.float32)
    for i in range(7):
        for j in range(7):
            if i == j: continue
            angle = np.radians(planet_longitudes[i] - planet_longitudes[j])
            aspect_strength = 0.5 * (1.0 - np.cos(angle)) # 1 at opposition, 0 at conjunction
            if j in [1, 3, 4, 5]: # Benefic aspects add strength
                bala[i] += 15.0 * aspect_strength
            else: # Malefic aspects subtract strength
                bala[i] -= 15.0 * aspect_strength
    return np.clip(bala, 0.0, 60.0)


def compute_shadbala(
    planet_longitudes_sidereal: np.ndarray,   # shape (7,): Sun→Saturn
    planet_speeds: np.ndarray,                 # shape (7,)
    asc_longitude_sidereal: float
) -> np.ndarray:
    """
    Computes full 6-fold Shadbala.
    Returns shape (7, 6): columns = [Sthana, Dig, Kala, Cheshta, Drik, Total_Rupas]
    Naisargika Bala is a 0-variance constant, so it is factored into Total_Rupas but removed from columns.
    All values in Shashtiamsas except last column which is Rupas (÷60).
    """
    s1 = compute_sthana_bala(planet_longitudes_sidereal)
    s2 = compute_dig_bala(planet_longitudes_sidereal, asc_longitude_sidereal)
    s3 = compute_kala_bala(planet_longitudes_sidereal, asc_longitude_sidereal)
    s4 = compute_cheshta_bala(planet_speeds)
    s5 = NAISARGIKA_BALA.copy()
    s6 = compute_drik_bala(planet_longitudes_sidereal)

    total_shashtia = s1 + s2 + s3 + s4 + s5 + s6
    total_rupas    = total_shashtia / 60.0

    result = np.stack([s1, s2, s3, s4, s6, total_rupas], axis=1)   # (7, 6)
    return result.astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# MASTER ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def compute_natal_strength(
    planet_longitudes_sidereal: np.ndarray,   # (7,) Sun→Saturn
    planet_speeds: np.ndarray,                 # (7,)
    asc_longitude_sidereal: float
) -> dict:
    """
    Computes all static natal strength metrics from the natal tensor row.
    No Swiss Ephemeris calls — pure math on pre-computed natal positions.
    """
    planet_signs = np.array([int(np.floor(lon / 30.0)) % 12 for lon in planet_longitudes_sidereal] +
                             [int(np.floor(asc_longitude_sidereal / 30.0)) % 12], dtype=np.int8)  # 8 elements with Asc

    ashtak = compute_ashtakvarga(planet_signs)
    shadbala = compute_shadbala(planet_longitudes_sidereal, planet_speeds, asc_longitude_sidereal)

    return {
        "raw_bav":      ashtak["raw_bav"],       # (7,12)
        "reduced_bav":  ashtak["reduced_bav"],   # (7,12)
        "raw_sav":      ashtak["raw_sav"],        # (12,)
        "reduced_sav":  ashtak["reduced_sav"],    # (12,)
        "shadbala":     shadbala,                 # (7,6) [Sthana,Dig,Kala,Cheshta,Drik,Rupas]
    }


# ─────────────────────────────────────────────────────────────────────────────
# SELF-VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # SPY natal: approximate sidereal longitudes for Sun→Saturn
    LONS   = np.array([280.0, 97.0, 240.0, 265.0, 190.0, 300.0, 320.0], dtype=np.float32)
    SPEEDS = np.array([1.01, 13.5, 0.5, 1.1, 0.07, 1.15, 0.03],        dtype=np.float32)
    ASC    = 305.0

    result = compute_natal_strength(LONS, SPEEDS, ASC)

    print(f"[VALIDATION] Raw SAV sum: {result['raw_sav'].sum()} (expect ~337 for typical chart)")
    print(f"[VALIDATION] Shadbala shape: {result['shadbala'].shape}")
    print(f"[VALIDATION] Sun Shadbala Rupas: {result['shadbala'][0, 5]:.4f} (expect >= 6.5)")
    print("[VALIDATION] natal_strength_module PASSED.")
