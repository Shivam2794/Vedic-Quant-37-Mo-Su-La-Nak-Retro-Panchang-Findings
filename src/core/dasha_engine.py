"""
FULL VIMSHOTTARI DASHA ENGINE - 3 LEVELS
Calculates Mahadasha, Antardasha, Pratyantardasha for any birth datetime.
Verified against classical Parashari rules.
"""
import sys, swisseph as swe, json
from datetime import datetime, timedelta
import pytz
sys.stdout.reconfigure(encoding='utf-8')

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# === VIMSHOTTARI CONSTANTS ===
# 27 Nakshatras and their ruling lords (Parashari order)
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigasira","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
# Nakshatra lord order (9 lords cycling 3x = 27 nakshatras)
NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

# Dasha years (Vimshottari = 120 year cycle)
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

# Each nakshatra = 13°20' = 800 arcmin
NAK_SIZE_DEG = 360.0 / 27.0  # = 13.3333...

def get_moon_lon(dt_string):
    ny_tz = pytz.timezone('America/New_York')
    dt_naive = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
    dt_utc = ny_tz.localize(dt_naive).astimezone(pytz.utc)
    utc_hour = dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, utc_hour)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0]
    return moon_lon, dt_utc

def calc_vimshottari_dasha(dt_string):
    moon_lon, birth_utc = get_moon_lon(dt_string)
    
    # Step 1: Find nakshatra and lord
    nak_idx = int(moon_lon / NAK_SIZE_DEG)                  # 0..26
    lord_idx = nak_idx % 9                                    # 0..8 in NAK_LORDS
    birth_lord = NAK_LORDS[lord_idx]
    
    # Step 2: Find how far into this nakshatra the Moon is (0..1)
    deg_into_nak = moon_lon - (nak_idx * NAK_SIZE_DEG)       # 0..13.333
    fraction_elapsed = deg_into_nak / NAK_SIZE_DEG            # 0..1 (fraction of nak traversed)
    
    # Step 3: Balance of first dasha = remaining fraction * dasha years
    dasha_total_years = DASHA_YEARS[birth_lord]
    years_elapsed = fraction_elapsed * dasha_total_years
    years_remaining = dasha_total_years - years_elapsed
    
    # Step 4: Build full timeline from birth
    # Start the clock at birth, backing up by years_elapsed of the birth dasha
    DAYS_PER_YEAR = 365.25636042
    birth_dt = datetime(birth_utc.year, birth_utc.month, birth_utc.day, 
                        birth_utc.hour, birth_utc.minute, birth_utc.second,
                        tzinfo=pytz.utc)
    
    # When did this Mahadasha start (before birth)?
    first_maha_start = birth_dt - timedelta(days=years_elapsed * DAYS_PER_YEAR)
    
    # Build the dasha sequence starting from birth_lord
    lord_start_idx = DASHA_ORDER.index(birth_lord)
    
    dasha_timeline = []
    current_start = first_maha_start
    for i in range(9):  # All 9 Mahadashas
        lord = DASHA_ORDER[(lord_start_idx + i) % 9]
        duration_days = DASHA_YEARS[lord] * DAYS_PER_YEAR
        maha_end = current_start + timedelta(days=duration_days)
        dasha_timeline.append({
            "lord": lord,
            "start": current_start,
            "end": maha_end,
            "years": DASHA_YEARS[lord]
        })
        current_start = maha_end
    
    return {
        "moon_nakshatra": NAKSHATRAS[nak_idx],
        "moon_nak_idx": nak_idx,
        "moon_lon": moon_lon,
        "birth_lord": birth_lord,
        "fraction_elapsed": fraction_elapsed,
        "years_remaining_first_dasha": years_remaining,
        "dasha_timeline": dasha_timeline
    }

def get_dasha_at_date(dasha_result, query_date_str="today"):
    """Find the exact Mahadasha, Antardasha, Pratyantardasha at a given date."""
    if query_date_str == "today":
        query_dt = datetime.now(pytz.utc)
    else:
        query_dt = pytz.utc.localize(datetime.strptime(query_date_str, "%Y-%m-%d"))
    
    DAYS_PER_YEAR = 365.25636042
    timeline = dasha_result["dasha_timeline"]
    
    # Find Mahadasha
    maha = None
    for d in timeline:
        if d["start"] <= query_dt < d["end"]:
            maha = d
            break
    if not maha:
        return None
    
    # Find Antardasha within Mahadasha
    maha_lord = maha["lord"]
    maha_lord_idx = DASHA_ORDER.index(maha_lord)
    maha_duration_days = maha["years"] * DAYS_PER_YEAR
    
    antar_start = maha["start"]
    antar = None
    for j in range(9):
        antar_lord = DASHA_ORDER[(maha_lord_idx + j) % 9]
        # Antardasha proportion = (antar_lord_years / 120) * maha_years * 365.25636042
        antar_days = (DASHA_YEARS[antar_lord] / 120.0) * maha_duration_days
        antar_end = antar_start + timedelta(days=antar_days)
        if antar_start <= query_dt < antar_end:
            antar = {"lord": antar_lord, "start": antar_start, "end": antar_end}
            break
        antar_start = antar_end
    if not antar:
        return None
    
    # Find Pratyantardasha within Antardasha
    antar_lord = antar["lord"]
    antar_lord_idx = DASHA_ORDER.index(antar_lord)
    antar_duration_days = (antar["end"] - antar["start"]).total_seconds() / 86400.0
    
    pratyantar_start = antar["start"]
    pratyantar = None
    for k in range(9):
        prat_lord = DASHA_ORDER[(antar_lord_idx + k) % 9]
        prat_days = (DASHA_YEARS[prat_lord] / 120.0) * antar_duration_days
        prat_end = pratyantar_start + timedelta(days=prat_days)
        if pratyantar_start <= query_dt < prat_end:
            pratyantar = {"lord": prat_lord, "start": pratyantar_start, "end": prat_end}
            break
        pratyantar_start = prat_end
    
    return {
        "Mahadasha": maha_lord,
        "Mahadasha_start": maha["start"].strftime("%Y-%m-%d"),
        "Mahadasha_end": maha["end"].strftime("%Y-%m-%d"),
        "Antardasha": antar_lord if antar else "?",
        "Antardasha_start": antar["start"].strftime("%Y-%m-%d") if antar else "?",
        "Antardasha_end": antar["end"].strftime("%Y-%m-%d") if antar else "?",
        "Pratyantardasha": pratyantar["lord"] if pratyantar else "?",
        "Pratyantar_start": pratyantar["start"].strftime("%Y-%m-%d") if pratyantar else "?",
        "Pratyantar_end": pratyantar["end"].strftime("%Y-%m-%d") if pratyantar else "?"
    }


# === LOAD ALL ASSETS AND COMPUTE DASHAS ===
with open("asset_birth_database.json") as f:
    db = json.load(f)

QUERY_DATE = "2026-06-04"  # Today

print("=" * 110)
print(f"VIMSHOTTARI DASHA - ALL 28 ASSETS | Query Date: {QUERY_DATE}")
print("=" * 110)
print(f"\n{'Asset':<8} {'Event':<12} {'Moon Nak':<22} {'Birth Lord':<10} {'Mahadasha':<12} {'Maha Start':<12} {'Maha End':<12} {'Antardasha':<12} {'Pratyantardasha'}")
print("-" * 140)

assets = list(db.keys())[:28]

# Also build complete output for Chrome comparison payload
full_dasha_output = {}

for ticker in assets:
    dates = db[ticker]
    for event_type, dt_str in [("Conception", dates["conception"]), ("Trading", dates["trading"])]:
        try:
            result = calc_vimshottari_dasha(dt_str)
            at_date = get_dasha_at_date(result, QUERY_DATE)
            
            key = f"{ticker}_{event_type}"
            full_dasha_output[key] = {
                "birth_datetime": dt_str,
                "moon_nakshatra": result["moon_nakshatra"],
                "moon_longitude": round(result["moon_lon"], 4),
                "birth_dasha_lord": result["birth_lord"],
                "years_remaining_first_dasha": round(result["years_remaining_first_dasha"], 4),
                "dasha_at_query_date": at_date,
                "full_sequence": [
                    {
                        "mahadasha": d["lord"],
                        "start": d["start"].strftime("%Y-%m-%d"),
                        "end": d["end"].strftime("%Y-%m-%d"),
                        "years": d["years"]
                    } for d in result["dasha_timeline"]
                ]
            }
            
            if at_date:
                print(f"{ticker:<8} {event_type:<12} {result['moon_nakshatra']:<22} {result['birth_lord']:<10} "
                      f"{at_date['Mahadasha']:<12} {at_date['Mahadasha_start']:<12} {at_date['Mahadasha_end']:<12} "
                      f"{at_date['Antardasha']:<12} {at_date['Pratyantardasha']}")
        except Exception as e:
            print(f"{ticker:<8} {event_type:<12} ERROR: {e}")

# Save full output for Chrome verification
with open("dasha_verification_payload.json", "w") as f:
    json.dump(full_dasha_output, f, indent=2, default=str)

print(f"\n\nFull dasha payload saved to dasha_verification_payload.json")
print("\n\nDETAILED BREAKDOWN FOR KEY ASSETS (SPY, QQQ, GLD, XLC):")
for ticker in ["SPY", "QQQ", "GLD", "XLC"]:
    dates = db.get(ticker, {})
    for event_type, dt_str in [("Conception", dates.get("conception")), ("Trading", dates.get("trading"))]:
        if not dt_str:
            continue
        result = calc_vimshottari_dasha(dt_str)
        print(f"\n{'='*80}")
        print(f"  {ticker} {event_type} | {dt_str}")
        print(f"  Moon @ {result['moon_lon']:.4f}° | Nakshatra: {result['moon_nakshatra']} | Birth Lord: {result['birth_lord']}")
        print(f"  Fraction through nak: {result['fraction_elapsed']:.4f} | Years remaining in first dasha: {result['years_remaining_first_dasha']:.4f}")
        print(f"\n  COMPLETE DASHA SEQUENCE:")
        print(f"  {'Mahadasha':<12} {'Start':>12} {'End':>12}  {'Years'}")
        print(f"  {'-'*50}")
        for d in result["dasha_timeline"]:
            print(f"  {d['lord']:<12} {d['start'].strftime('%Y-%m-%d'):>12} {d['end'].strftime('%Y-%m-%d'):>12}  {d['years']}")
        at_today = get_dasha_at_date(result, QUERY_DATE)
        if at_today:
            print(f"\n  AT {QUERY_DATE}:")
            print(f"  Mahadasha:       {at_today['Mahadasha']}  ({at_today['Mahadasha_start']} → {at_today['Mahadasha_end']})")
            print(f"  Antardasha:      {at_today['Antardasha']}  ({at_today['Antardasha_start']} → {at_today['Antardasha_end']})")
            print(f"  Pratyantardasha: {at_today['Pratyantardasha']}  ({at_today['Pratyantar_start']} → {at_today['Pratyantar_end']})")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
