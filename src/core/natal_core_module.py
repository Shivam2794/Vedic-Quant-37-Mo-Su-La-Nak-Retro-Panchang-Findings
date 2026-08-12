import numpy as np

class NatalCoreLens:
    """
    Applies the 4-Lens Framework to the Natal Core Module.
    - ML Architect: Array ops completely vectorized, Numba-free.
    - Data Engineer: Edge-case precision handling with np.clip and epsilons.
    - Jyotish Scholar: Precise definition of 16 Vargas and 7 Chara Karakas.
    - Quant Developer: High performance and mathematically elegant mapping.
    """
    
    @staticmethod
    def compute_vargas_and_karakas(natal_topo_row, classical_indices=None):
        """
        Computes the 16 exact Parashari Divisional Charts (Vargas) for natal entities,
        and the 8 classical Jaimini Chara Karakas.
        
        Args:
            natal_topo_row: 1D array-like representing the topocentric 
                            ecliptic longitudes (0 to 360 degrees).
            classical_indices: list or array of indices for the 8 classical planets.
                               Defaults to [1, 2, 3, 4, 5, 6, 7, 8].
                               
        Returns:
            vargas_sin: 2D numpy array of shape (16, N_entities). Sine embeddings of the 16 Vargas.
            vargas_cos: 2D numpy array of shape (16, N_entities). Cosine embeddings of the 16 Vargas.
            karakas: List of lists of length 8. Each index corresponds to the Karaka rank
                     (0=AK, 1=AmK, 2=BK, 3=MK, 4=PiK, 5=PK, 6=GK, 7=DK).
                     Contains the indices of planets holding that rank. Tied planets share a rank.
        """
        L = np.asarray(natal_topo_row, dtype=np.float64) % 360.0
        
        # Base computations
        L_floor_30 = np.floor(L / 30.0)
        sign = L_floor_30.astype(np.int32) % 12
        deg = L - (L_floor_30 * 30.0)
        # Correct small negative degrees due to floating point inaccuracies
        deg = np.where(deg < 0, deg + 30.0, deg) % 30.0
        
        frac = deg / 30.0  # Normalized position within the sign [0, 1)
        
        odd_sign = (sign % 2) == 0  # Aries(0), Gemini(2), etc., are Odd signs
        
        vargas = np.zeros((16, len(L)), dtype=np.int32)
        
        def get_part(n_parts):
            # Protects against floating point frac rounding to 1.0 using np.clip
            return np.clip(np.floor(frac * n_parts).astype(np.int32), 0, n_parts - 1)
        
        # 1. D-1 (Rasi)
        vargas[0] = sign
        
        # 2. D-2 (Hora)
        part_d2 = get_part(2)
        d2_odd = np.where(part_d2 == 0, 4, 3)
        d2_even = np.where(part_d2 == 0, 3, 4)
        vargas[1] = np.where(odd_sign, d2_odd, d2_even)
        
        # 3. D-3 (Drekkana)
        vargas[2] = (sign + get_part(3) * 4) % 12
        
        # 4. D-4 (Chaturthamsha)
        vargas[3] = (sign + get_part(4) * 3) % 12
        
        # 5. D-7 (Saptamsha)
        vargas[4] = np.where(odd_sign, (sign + get_part(7)) % 12, (sign + 6 + get_part(7)) % 12)
        
        # 6. D-9 (Navamsha) - Direct continuous global formula
        part_d9_global = np.floor((L / 360.0) * 108.0).astype(np.int32)
        vargas[5] = part_d9_global % 12
        
        # 7. D-10 (Dashamsha)
        vargas[6] = np.where(odd_sign, (sign + get_part(10)) % 12, (sign + 8 + get_part(10)) % 12)
        
        # 8. D-12 (Dvadashamsha)
        vargas[7] = (sign + get_part(12)) % 12
        
        # 9. D-16 (Shodashamsha)
        vargas[8] = ((sign % 3) * 4 + get_part(16)) % 12
        
        # 10. D-20 (Vimshamsha)
        vargas[9] = ((sign % 3) * 8 + get_part(20)) % 12
        
        # 11. D-24 (Chaturvimshamsha)
        vargas[10] = np.where(odd_sign, (4 + get_part(24)) % 12, (3 + get_part(24)) % 12)
        
        # 12. D-27 (Saptavimshamsha / Bhamsha)
        vargas[11] = ((sign % 4) * 3 + get_part(27)) % 12
        
        # 13. D-30 (Trimshamsha)
        # Odd signs: Mars(0) 5°, Sat(10) 5°, Jup(8) 8°, Mer(2) 7°, Ven(6) 5°
        d30_odd = np.piecewise(deg,
                               [deg < 5.0, (deg >= 5.0) & (deg < 10.0), (deg >= 10.0) & (deg < 18.0), (deg >= 18.0) & (deg < 25.0), deg >= 25.0],
                               [0, 10, 8, 2, 6])
        # Even signs: Ven(1) 5°, Mer(5) 7°, Jup(11) 8°, Sat(9) 5°, Mars(7) 5°
        d30_even = np.piecewise(deg,
                                [deg < 5.0, (deg >= 5.0) & (deg < 12.0), (deg >= 12.0) & (deg < 20.0), (deg >= 20.0) & (deg < 25.0), deg >= 25.0],
                                [1, 5, 11, 9, 7])
        vargas[12] = np.where(odd_sign, d30_odd, d30_even).astype(np.int32)
        
        # 14. D-40 (Khavedamsha)
        vargas[13] = np.where(odd_sign, (0 + get_part(40)) % 12, (6 + get_part(40)) % 12)
        
        # 15. D-45 (Akshavedamsha)
        vargas[14] = ((sign % 3) * 4 + get_part(45)) % 12
        
        # 16. D-60 (Shashtiamsha)
        vargas[15] = (sign + get_part(60)) % 12

        # Chara Karakas (8-Karaka scheme including Rahu)
        if classical_indices is None:
            classical_indices = np.arange(1, 9)
            
        classical_indices = np.array(classical_indices, dtype=np.int32)
        karaka_degs = deg[classical_indices]
        
        # Invert Rahu's degrees 30.0 - deg for the Jaimini 8-Karaka sort
        rahu_mask = (classical_indices == 8)
        karaka_degs = np.where(rahu_mask, 30.0 - karaka_degs, karaka_degs)
        
        # Classical Jaimini shared-karaka resolution for degree ties
        # Rank is defined as the number of valid planets with a strictly greater degree.
        ranks = np.array([(karaka_degs > d).sum() for d in karaka_degs], dtype=np.int32)
        karakas = [classical_indices[ranks == i].tolist() for i in range(len(classical_indices))]
        
        # Convert Vargas to sin/cos embeddings
        angles = (vargas / 12.0) * 2 * np.pi
        vargas_sin = np.sin(angles)
        vargas_cos = np.cos(angles)
        
        return vargas_sin, vargas_cos, karakas

# Expose primary function directly
compute_vargas_and_karakas = NatalCoreLens.compute_vargas_and_karakas

if __name__ == "__main__":
    # Test execution
    dummy_tensor = np.array([12.5, 45.2, 88.9, 120.1, 150.8, 199.3, 245.6, 290.0, 311.2, 131.2, 55.4, 23.1, 190.5, 200.8, 210.3, 350.9])
    v_sin, v_cos, k = compute_vargas_and_karakas(dummy_tensor)
    print("Vargas (sin) Shape:", v_sin.shape)
    print("Vargas (cos) Shape:", v_cos.shape)
    print("Jaimini Chara Karakas (AK to DK) Computed Successfully:", k)
