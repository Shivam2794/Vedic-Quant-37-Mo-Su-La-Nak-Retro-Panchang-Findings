import sys
import os
import datetime

# Add the codebase to the path
sys.path.insert(0, r"E:\Python\Learn\Astrology 2-20260611T223423Z-3-001\Astrology 2\orion_essential\Codebase")

try:
    from data_collection.canonical_anchors import CANONICAL_ANCHORS
    from orion_ephemeris_core import OrionEphemerisEngine
    from orion_alpha_engine import OrionAlphaEngine

    def test_house_transits():
        engine = OrionEphemerisEngine(anchors_list=CANONICAL_ANCHORS)
        alpha = OrionAlphaEngine(engine, anchor_name='SPY_CONCEPTION')
        
        # Check if house lords change based on ascendant
        asc_sign = alpha._get_sign(alpha.natal_asc)
        expected_lord = alpha._get_sign_lord(asc_sign)
        actual_lord = alpha.house_lords[0]
        
        assert expected_lord == actual_lord, f"House lords not dynamically calculated! Expected {expected_lord}, got {actual_lord}"
        
        dt = datetime.datetime(2026, 6, 12, tzinfo=datetime.timezone.utc)
        features = alpha.generate_features(dt)
        
        # We don't have L3_Jupiter_House in the features directly based on my last file read, 
        # let's just see if L3_Jupiter_House_X_Impact exists
        jupiter_keys = [k for k in features.keys() if 'L3_Jupiter_House_' in k and '_Impact' in k]
        assert len(jupiter_keys) > 0, "Jupiter Impact feature missing!"
        
        print("ALL TESTS PASSED")

    if __name__ == "__main__":
        test_house_transits()
except Exception as e:
    print(f"ERROR: {e}")
