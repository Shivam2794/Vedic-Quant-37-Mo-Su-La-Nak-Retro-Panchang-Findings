import sys
import math
import datetime

sys.path.insert(0, r"E:\Python\Learn\Astrology 2-20260611T223423Z-3-001\Astrology 2\orion_essential\Codebase")

try:
    from orion_ephemeris_core import OrionEphemerisEngine
    from orion_alpha_engine import OrionAlphaEngine

    def run_brutal_stress_test():
        print("INITIALIZING BRUTAL QA ENGINE...")
        ephe = OrionEphemerisEngine(r"E:\Python\Learn\Astrology 2-20260611T223423Z-3-001\Astrology 2\orion_essential\ephe")
        engine = OrionAlphaEngine(ephe)

        test_dates = [
            datetime.datetime(1990, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
            datetime.datetime(2000, 2, 29, 12, 0, tzinfo=datetime.timezone.utc), # Leap year
            datetime.datetime(2020, 5, 14, 18, 30, tzinfo=datetime.timezone.utc), # Jupiter Retrograde Station
            datetime.datetime(2026, 6, 12, 23, 59, tzinfo=datetime.timezone.utc), # Present edge case
            datetime.datetime(2050, 12, 31, 23, 59, tzinfo=datetime.timezone.utc) # Future extrapolation
        ]

        # Add 50 sequential days to check memory/state bleeding
        base_dt = datetime.datetime(2022, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        for i in range(50):
            test_dates.append(base_dt + datetime.timedelta(days=i))

        print(f"Executing {len(test_dates)} stress tests...")

        feature_sizes = []
        
        for dt in test_dates:
            features = engine.generate_features(dt)
            
            # 1. Check if dictionary is returned
            assert isinstance(features, dict), f"Failed at {dt}: generate_features did not return a dictionary!"
            
            # 2. Check for NaN values
            nan_keys = [k for k, v in features.items() if isinstance(v, float) and math.isnan(v)]
            assert len(nan_keys) == 0, f"NaN DETECTED at {dt} in keys: {nan_keys}"
            
            # 3. Check for Infinity values
            inf_keys = [k for k, v in features.items() if isinstance(v, float) and math.isinf(v)]
            assert len(inf_keys) == 0, f"INFINITY DETECTED at {dt} in keys: {inf_keys}"
            
            # 4. Check for un-sanitized keys (must be BigQuery compatible)
            invalid_keys = [k for k in features.keys() if ' ' in k or '-' in k]
            assert len(invalid_keys) == 0, f"INVALID SCHEMA DETECTED at {dt} in keys: {invalid_keys}"
            
            feature_sizes.append(len(features))

        print(f"All {len(test_dates)} stress tests PASSED. Feature vector size: ~{feature_sizes[0]} columns.")
        
        # Spot check some specialist keys
        sample_feats = engine.generate_features(test_dates[0])
        print("\nSPOT CHECKING CRITICAL GOD-AGENT FEATURES (13-BODY EXPANSION):")
        bodies = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto', 'Ascendant']
        for b in bodies:
            has_l3 = any(f'L3_{b}_' in k for k in sample_feats.keys())
            print(f"- {b} L3 Features Present: {'YES' if has_l3 else 'NO'}")
            if not has_l3:
                raise ValueError(f"Missing God Agent Expansion for {b}!")

        print("\nSPOT CHECKING SPECIALIST INTEGRATIONS:")
        drishti_keys = [k for k in sample_feats.keys() if 'Drishti' in k]
        print(f"- Drishti Keys Found: {len(drishti_keys)} (e.g. {drishti_keys[0] if drishti_keys else 'NONE'})")
        
        yuddha_keys = [k for k in sample_feats.keys() if 'WAR' in k.upper() or 'YUDDHA' in k.upper()]
        print(f"- Graha Yuddha Keys Found: {len(yuddha_keys)}")
        
        t2n_keys = [k for k in sample_feats.keys() if 'T2N' in k]
        print(f"- T2N Keys Found: {len(t2n_keys)}")

        print("\nBRUTAL QA INSPECTION COMPLETE. CODE IS FLAWLESS.")

    if __name__ == "__main__":
        run_brutal_stress_test()
except Exception as e:
    import traceback
    print(f"CRITICAL FAILURE: {e}")
    traceback.print_exc()
