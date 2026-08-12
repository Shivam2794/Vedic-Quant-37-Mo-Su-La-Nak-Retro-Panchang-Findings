import sys
import datetime
from datetime import timezone

sys.path.append(r"C:\Users\Shivam Patel\Desktop\Python\Learn")
from institution_backtest_analysis import extract_all_features, compute_natal_blueprint, extract_natal_transit_crossref

# Mock natal lons
natal_lons = {
    'Sun': 0.0, 'Moon': 45.0, 'Mars': 90.0, 'Merc': 15.0, 'Jup': 180.0, 'Ven': 30.0, 'Sat': 270.0, 'Rahu': 120.0, 'Ketu': 300.0,
    '_jd': 2451545.0, '_asc': 0.0, '_moon_nak_i': 3
}

dt = datetime.datetime(2024, 1, 1, 14, 30, tzinfo=timezone.utc)
feats, tlons = extract_all_features(natal_lons, "2000-01-01", dt, "Information Technology")
bp = compute_natal_blueprint(natal_lons)
cx = extract_natal_transit_crossref(bp, feats, tlons)

combined = {**feats, **bp, **cx}
print(f"Total ML Features extracted: {len(combined)}")
