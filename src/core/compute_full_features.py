"""
COMPUTE ALL MISSING FEATURES FROM BACKEND:
1. Nakshatra + Pada for every planet, every asset birth datetime
2. Vimshottari Dasha (full sequence + 3-level at birth + 3-level at 2026-06-04)
3. Panchang: Tithi, Karana, Yoga, Vara for each birth datetime
Outputs a full JSON matching the Chrome agent schema for cross-verification.
"""
import sys, swisseph as swe, json
from datetime import datetime, timedelta
import pytz
sys.stdout.reconfigure(encoding='utf-8')

swe.set_ephe_path(None)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ===== CONSTANTS =====
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigasira","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
NAK_SIZE = 360.0 / 27.0   # 13.3333...°

NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
DAYS_PER_YEAR = 365.25636042

TITHI_NAMES = [
    "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami",
    "Navami","Dashami","Ekadashi","Dvadashi","Trayodashi","Chaturdashi","Purnima/Amavasya"
]
YOGA_NAMES = [
    "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti",
    "Shula","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
    "Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
]
KARANA_NAMES = [
    "Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti",
    "Shakuni","Chatushpada","Naga","Kimstughna"
]
VARA_NAMES = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

PLANET_IDS = {
    "Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
    "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE
}

def get_jd(dt_str):
    ny = pytz.timezone('America/New_York')
    dt = ny.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")).astimezone(pytz.utc)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0), dt

def nak_pada(lon):
    nak_idx = int(lon / NAK_SIZE)
    deg_in = lon - nak_idx * NAK_SIZE
    pada = int(deg_in / (NAK_SIZE / 4)) + 1
    pada = min(pada, 4)
    return NAKSHATRAS[nak_idx % 27], pada

def calc_panchang(jd, dt_utc):
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    sun_lon = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0]

    # Tithi: each tithi = 12° of Moon-Sun angular difference
    moon_sun_diff = (moon_lon - sun_lon) % 360.0
    tithi_num = int(moon_sun_diff / 12.0) + 1   # 1..30
    tithi_idx = (tithi_num - 1) % 15
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"
    tithi_name_base = TITHI_NAMES[tithi_idx] if tithi_idx < 14 else ("Purnima" if tithi_num == 15 else "Amavasya")
    tithi_name = f"{tithi_name_base} ({paksha})"

    # Yoga: each yoga = 13°20' of (Moon+Sun) combined longitude
    yoga_lon = (moon_lon + sun_lon) % 360.0
    yoga_idx = int(yoga_lon / (360.0/27.0)) % 27
    yoga_name = YOGA_NAMES[yoga_idx]

    # Karana: each karana = 6° of Moon-Sun difference (half tithi)
    karana_idx_raw = int(moon_sun_diff / 6.0)
    if karana_idx_raw == 0:
        karana_name = "Kimstughna"
    elif karana_idx_raw == 57:
        karana_name = "Shakuni"
    elif karana_idx_raw == 58:
        karana_name = "Chatushpada"
    elif karana_idx_raw == 59:
        karana_name = "Naga"
    else:
        karana_name = KARANA_NAMES[(karana_idx_raw - 1) % 7]

    # Vara (weekday) — from Julian Day
    # JD 0 = Monday in some systems; swe.day_of_week returns 0=Mon..6=Sun
    dow = int(jd + 1.5) % 7   # 0=Sun, 1=Mon... (standard astronomical)
    vara_name = VARA_NAMES[dow]

    # Moon Nakshatra + Pada
    moon_nak, moon_pada = nak_pada(moon_lon)

    return {
        "tithi": tithi_name,
        "tithi_number": tithi_num,
        "karana": karana_name,
        "yoga": yoga_name,
        "vara": vara_name,
        "moon_nakshatra": moon_nak,
        "moon_pada": moon_pada
    }

def calc_dasha(moon_lon, birth_dt):
    nak_idx = int(moon_lon / NAK_SIZE)
    lord_idx = nak_idx % 9
    birth_lord = NAK_LORDS[lord_idx]
    deg_into_nak = moon_lon - nak_idx * NAK_SIZE
    fraction_elapsed = deg_into_nak / NAK_SIZE
    years_elapsed = fraction_elapsed * DASHA_YEARS[birth_lord]

    lord_start_idx = DASHA_ORDER.index(birth_lord)
    first_maha_start = birth_dt - timedelta(days=years_elapsed * DAYS_PER_YEAR)

    sequence = []
    cur = first_maha_start
    for i in range(9):
        lord = DASHA_ORDER[(lord_start_idx + i) % 9]
        dur = DASHA_YEARS[lord] * DAYS_PER_YEAR
        end = cur + timedelta(days=dur)
        sequence.append({"lord": lord, "start": cur, "end": end, "years": DASHA_YEARS[lord]})
        cur = end
    return sequence

def get_3level_dasha(sequence, query_dt):
    for maha in sequence:
        if maha["start"] <= query_dt < maha["end"]:
            maha_lord_idx = DASHA_ORDER.index(maha["lord"])
            maha_days = (maha["end"] - maha["start"]).total_seconds() / 86400.0

            antar_cur = maha["start"]
            for j in range(9):
                al = DASHA_ORDER[(maha_lord_idx + j) % 9]
                antar_days = (DASHA_YEARS[al] / 120.0) * maha_days
                antar_end = antar_cur + timedelta(days=antar_days)
                if antar_cur <= query_dt < antar_end:
                    al_idx = DASHA_ORDER.index(al)
                    prat_days_total = (antar_end - antar_cur).total_seconds() / 86400.0
                    prat_cur = antar_cur
                    for k in range(9):
                        pl = DASHA_ORDER[(al_idx + k) % 9]
                        prat_days = (DASHA_YEARS[pl] / 120.0) * prat_days_total
                        prat_end = prat_cur + timedelta(days=prat_days)
                        if prat_cur <= query_dt < prat_end:
                            return {
                                "mahadasha":       {"lord": maha["lord"], "start": maha["start"].strftime("%Y-%m-%d"), "end": maha["end"].strftime("%Y-%m-%d")},
                                "antardasha":      {"lord": al,           "start": antar_cur.strftime("%Y-%m-%d"),    "end": antar_end.strftime("%Y-%m-%d")},
                                "pratyantardasha": {"lord": pl,           "start": prat_cur.strftime("%Y-%m-%d"),     "end": prat_end.strftime("%Y-%m-%d")}
                            }
                        prat_cur = prat_end
                antar_cur = antar_end
    return None

def calc_chart_full(dt_str):
    jd, dt_utc = get_jd(dt_str)
    flags = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    planets = {}
    for p, pid in PLANET_IDS.items():
        res = swe.calc_ut(jd, pid, flags)
        lon, spd = res[0][0], res[0][3]
        nak, pada = nak_pada(lon)
        sign = SIGNS[int(lon/30) % 12]
        d = int(lon % 30); m = int((lon%30-d)*60); s = int(((lon%30-d)*60-m)*60)
        planets[p] = {
            "sign": sign,
            "degrees": f"{d:02d}°{m:02d}'{s:02d}\"",
            "longitude": round(lon, 6),
            "nakshatra": nak, "pada": pada,
            "retrograde": spd < 0
        }

    ketu_lon = (planets["Rahu"]["longitude"] + 180.0) % 360.0
    nak, pada = nak_pada(ketu_lon)
    sign = SIGNS[int(ketu_lon/30) % 12]
    d = int(ketu_lon%30); m = int((ketu_lon%30-d)*60); s = int(((ketu_lon%30-d)*60-m)*60)
    planets["Ketu"] = {"sign": sign, "degrees": f"{d:02d}°{m:02d}'{s:02d}\"",
                       "longitude": round(ketu_lon,6), "nakshatra": nak, "pada": pada, "retrograde": False}

    houses, ascmc = swe.houses_ex(jd, 40.7128, -74.0060, b'W', flags)
    asc_lon = ascmc[0]
    nak, pada = nak_pada(asc_lon)
    sign = SIGNS[int(asc_lon/30) % 12]
    d = int(asc_lon%30); m = int((asc_lon%30-d)*60); s = int(((asc_lon%30-d)*60-m)*60)
    planets["Ascendant"] = {"sign": sign, "degrees": f"{d:02d}°{m:02d}'{s:02d}\"",
                            "longitude": round(asc_lon,6), "nakshatra": nak, "pada": pada, "retrograde": False}

    panchang = calc_panchang(jd, dt_utc)

    moon_lon = planets["Moon"]["longitude"]
    birth_dt = datetime(dt_utc.year, dt_utc.month, dt_utc.day,
                        dt_utc.hour, dt_utc.minute, dt_utc.second, tzinfo=pytz.utc)
    sequence = calc_dasha(moon_lon, birth_dt)
    today = datetime(2026, 6, 4, 12, 0, 0, tzinfo=pytz.utc)

    dasha_at_birth = get_3level_dasha(sequence, birth_dt)
    dasha_today    = get_3level_dasha(sequence, today)

    return {
        "birth_datetime": dt_str,
        "D1": planets,
        "panchang": panchang,
        "vimshottari_dasha": {
            "birth_lord": NAK_LORDS[int(moon_lon / NAK_SIZE) % 9],
            "moon_nakshatra": planets["Moon"]["nakshatra"],
            "moon_pada": planets["Moon"]["pada"],
            "full_sequence": [{"lord": d["lord"], "start": d["start"].strftime("%Y-%m-%d"),
                                "end": d["end"].strftime("%Y-%m-%d"), "years": d["years"]} for d in sequence],
            "at_birth": dasha_at_birth,
            "at_2026_06_04": dasha_today
        }
    }

# Load asset DB
with open("asset_birth_database.json") as f:
    db = json.load(f)

# Focus on 9 Phase-1 dates first, then all remaining
PHASE1 = [
    ("Sector_ETFs", "conception", "1998-12-16 12:00:00"),
    ("Sector_ETFs", "trading",    "1998-12-22 09:30:00"),
    ("XLRE",        "conception", "2015-10-06 12:00:00"),
    ("XLRE",        "trading",    "2015-10-08 09:30:00"),
    ("XLC",         "conception", "2018-06-18 12:00:00"),
    ("XLC",         "trading",    "2018-06-19 09:30:00"),
    ("SMH",         "conception", "2000-12-18 12:00:00"),
    ("SMH",         "trading",    "2000-12-20 09:30:00"),
    ("XME",         "conception", "2006-06-19 12:00:00"),
]

all_results = {}

print("=" * 80)
print("BACKEND COMPUTED: Nakshatra+Pada, Panchang, Vimshottari Dasha")
print("=" * 80)

# Phase 1 — detailed print
for ticker, event, dt_str in PHASE1:
    key = f"{ticker}_{event}"
    try:
        r = calc_chart_full(dt_str)
        all_results[key] = r

        print(f"\n{'━'*80}")
        print(f"  {key} | {dt_str}")
        print(f"{'━'*80}")
        print(f"  PANCHANG:")
        p = r["panchang"]
        print(f"    Tithi: {p['tithi']} (#{p['tithi_number']}) | Yoga: {p['yoga']} | Karana: {p['karana']} | Vara: {p['vara']}")
        print(f"    Moon Nakshatra: {p['moon_nakshatra']} Pada {p['moon_pada']}")

        print(f"\n  D1 PLANETS (Sign | Deg | Nakshatra | Pada | Retro):")
        for pname in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu","Ascendant"]:
            pl = r["D1"][pname]
            retro = "(R)" if pl["retrograde"] else "   "
            print(f"    {pname:<12} {pl['sign']:<14} {pl['degrees']:<12} {retro} {pl['nakshatra']:<22} Pada {pl['pada']}")

        d = r["vimshottari_dasha"]
        print(f"\n  DASHA — Birth Lord: {d['birth_lord']} | Moon in {d['moon_nakshatra']} Pada {d['moon_pada']}")
        print(f"  Full Mahadasha Sequence:")
        for seq in d["full_sequence"]:
            print(f"    {seq['lord']:<10} {seq['start']} → {seq['end']}")
        if d["at_birth"]:
            ab = d["at_birth"]
            print(f"\n  AT BIRTH: {ab['mahadasha']['lord']} MD / {ab['antardasha']['lord']} AD / {ab['pratyantardasha']['lord']} PAD")
            print(f"    MD:  {ab['mahadasha']['start']} → {ab['mahadasha']['end']}")
            print(f"    AD:  {ab['antardasha']['start']} → {ab['antardasha']['end']}")
            print(f"    PAD: {ab['pratyantardasha']['start']} → {ab['pratyantardasha']['end']}")
        if d["at_2026_06_04"]:
            at = d["at_2026_06_04"]
            print(f"\n  AT 2026-06-04: {at['mahadasha']['lord']} MD / {at['antardasha']['lord']} AD / {at['pratyantardasha']['lord']} PAD")
            print(f"    MD:  {at['mahadasha']['start']} → {at['mahadasha']['end']}")
            print(f"    AD:  {at['antardasha']['start']} → {at['antardasha']['end']}")
            print(f"    PAD: {at['pratyantardasha']['start']} → {at['pratyantardasha']['end']}")
    except Exception as e:
        print(f"  ERROR for {key}: {e}")

# Phase 2 — all remaining assets (compute and save, minimal print)
print(f"\n\n{'='*80}")
print("PHASE 2 — ALL REMAINING ASSETS")
print(f"{'='*80}")

for ticker, dates in db.items():
    for event in ["conception", "trading"]:
        dt_str = dates.get(event)
        if not dt_str:
            continue
        key = f"{ticker}_{event}"
        if any(key == f"{t}_{e}" for t,e,_ in PHASE1):
            continue
        try:
            r = calc_chart_full(dt_str)
            all_results[key] = r
            d = r["vimshottari_dasha"]
            at = d.get("at_2026_06_04")
            ab = d.get("at_birth")
            print(f"  {key:<22} Panchang:{r['panchang']['tithi'][:20]:<22} "
                  f"BirthDasha:{ab['mahadasha']['lord'] if ab else '?'}/{ab['antardasha']['lord'] if ab else '?'} "
                  f"Today:{at['mahadasha']['lord'] if at else '?'}/{at['antardasha']['lord'] if at else '?'}")
        except Exception as e:
            print(f"  ERROR {key}: {e}")

# Save full JSON
with open("backend_full_features.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)

print(f"\n\nAll results saved to backend_full_features.json ({len(all_results)} entries)")


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
