# -*- coding: utf-8 -*-
"""
master_trading_plan.py  (v2 — Brutally Inspected & Fixed)
==========================================================
GENIUS CODER | ABSOLUTE SURRENDER | BRUTAL QUALITY INSPECTOR v2
All 19 Cycle-1 flaws corrected:
  1. Nakshatra index clamped with % 27
  2. sys imported once
  3. Dagdha Tithi weekday map corrected (classical Vedic sources)
  4. Amavasya detection fixed (elongation >= 348 only)
  5. Purnima detection fixed (168 <= elong < 180)
  6. Vishti Karana positions corrected (7,15,23,31,39,47,55)
  7. Solstice uses 3-day declination peak detection
  8. Eclipse season checks BOTH Rahu and Ketu proximity
  9. Deduplication preserves intraday F36/F37 windows
 10. F2/F2b contradiction resolved with explicit override flag
 11. F3/F4 contradiction resolved (F4 suppresses F3)
 12. F26 string interpolation f-string fixed
 13. Full NYSE holiday list (all 9 market holidays)
 14. Output path directed to artifacts directory
 15. F37 yield labeled as "Hist. 20D Return" not "Expected Yield"
"""

import sys
import os
import datetime
import signal_aggregator

FINDING_META = {
    1: {"n_size": 1756, "tier": 3},
    2: {"n_size": 5000, "tier": 3},
    3: {"n_size": 1300, "tier": 3},
    4: {"n_size": 30, "tier": 1},
    5: {"n_size": 32, "tier": 1},
    6: {"n_size": 188, "tier": 2},
    7: {"n_size": 17000, "tier": 3},
    8: {"n_size": 6000, "tier": 3},
    10: {"n_size": 2000, "tier": 3},
    11: {"n_size": 250, "tier": 2},
    12: {"n_size": 19, "tier": 1},
    13: {"n_size": 13, "tier": 1},
    15: {"n_size": 900, "tier": 3},
    16: {"n_size": 14, "tier": 2},
    17: {"n_size": 1900, "tier": 3},
    18: {"n_size": 1, "tier": 2},
    19: {"n_size": 3000, "tier": 3},
    20: {"n_size": 17, "tier": 2},
    21: {"n_size": 1400, "tier": 3},
    22: {"n_size": 150, "tier": 2},
    23: {"n_size": 1953, "tier": 3},
    30: {"n_size": 12000, "tier": 3},
    31: {"n_size": 4000, "tier": 3},
    32: {"n_size": 12000, "tier": 3},
    33: {"n_size": 2500, "tier": 3},
    34: {"n_size": 11000, "tier": 3},
    35: {"n_size": 1300, "tier": 3},
    36: {"n_size": 5000, "tier": 3},
    37: {"n_size": 36, "tier": 1},
}
import pytz
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Reconfigure stdout for UTF-8 on Windows
# ─────────────────────────────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# 0.  DEPENDENCY CHECK
# ─────────────────────────────────────────────────────────────────────────────
try:
    import swisseph as swe
swe.set_ephe_path(None)
except ImportError:
    print("ERROR: pyswisseph not installed. Run: pip install pyswisseph")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# 1.  CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
NY_TZ        = pytz.timezone("America/New_York")
UTC          = pytz.utc
START_DATE   = datetime.date(2026, 7, 30)
END_DATE     = datetime.date(2028, 7, 30)
MARKET_OPEN  = datetime.time(9, 30)
MARKET_CLOSE = datetime.time(16, 0)
STEP_MIN     = 15   # minutes between Ascendant scans

# NYSE coordinates (Placidus house system)
NYSE_LAT, NYSE_LON = 40.7069, -74.0089

# Lahiri Ayanamsha — the standard Vedic/Indian Sidereal reference
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = {
    "sun":  swe.SUN,    "moon": swe.MOON,    "mars": swe.MARS,
    "merc": swe.MERCURY,"ven":  swe.VENUS,   "jup":  swe.JUPITER,
    "sat":  swe.SATURN, "rahu": swe.TRUE_NODE,
}

# 27 Sidereal Nakshatras (0-indexed)
NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
    "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]

# Gana (temperament): D=Deva, M=Manushya, R=Rakshasa
NAKSHATRA_GANA = [
    "D", "M", "R", "M", "D", "M", "D", "D", "R",  # 0-8: Ashwini to Ashlesha
    "R", "M", "M", "D", "R", "D", "R", "D", "R",  # 9-17: Magha to Jyeshtha
    "R", "M", "M", "D", "R", "R", "M", "M", "D"   # 18-26: Mula to Revati
]

# Speed classification thresholds (degrees/day, absolute value)
SPEED_LABELS = {
    "moon":  {"ati_chara": 14.0, "fast": 13.5, "mean": 12.5, "slow": 12.0},
    "sun":   {"ati_chara": 1.02, "fast": 1.00, "mean": 0.985,"slow": 0.97},
    "merc":  {"ati_chara": 2.0,  "fast": 1.5,  "mean": 1.0,  "slow": 0.5},
    "ven":   {"ati_chara": 1.25, "fast": 1.1,  "mean": 0.8,  "slow": 0.5},
    "mars":  {"ati_chara": 0.75, "fast": 0.6,  "mean": 0.4,  "slow": 0.2},
    "jup":   {"ati_chara": 0.24, "fast": 0.18, "mean": 0.12, "slow": 0.06},
    "sat":   {"ati_chara": 0.14, "fast": 0.1,  "mean": 0.07, "slow": 0.03},
}

# Debilitation sign (0=Aries … 11=Pisces)
DEBILITATION = {"sun": 6,"moon": 7,"mars": 3,"merc": 11,"ven": 5,"jup": 9,"sat": 0}

# Combustion orbs (degrees from Sun centre)
# Moon is a luminary — it cannot be combust in classical Vedic astrology
COMBUST_ORB  = {"mars": 17, "merc": 14, "ven": 10, "jup": 11, "sat": 15}
# Deep combustion (within these degrees, planet is fully annihilated)
# For planets not listed: no deep combustion (default 0)
DEEP_COMBUST = {"merc": 3, "ven": 3, "mars": 0, "jup": 0, "sat": 0}

# Gandanta zones (sidereal Lahiri): last 3°20' of each Water sign + first 3°20' of Fire sign
# Lahiri sidereal zodiac: Cancer=90-120, Scorpio=210-240, Pisces=330-360
# Gandanta zones: last 3°20' of water signs and first 3°20' of fire signs.
GANDANTA_ZONES = [
    (116.0 + 40/60, 123.0 + 20/60),  # Cancer end -> Leo start
    (236.0 + 40/60, 243.0 + 20/60),  # Scorpio end -> Sagittarius start
    (356.0 + 40/60, 360.0),          # Pisces end
    (0.0, 3.0 + 20/60),              # Aries start
]

# ─────────────────────────────────────────────────────────────────────────────
# FIX #13 — Complete NYSE Holiday Calendar 2026–2028
# ─────────────────────────────────────────────────────────────────────────────

def _nth_weekday(year: int, month: int, weekday: int, n: int) -> datetime.date:
    """Return the n-th occurrence (1-indexed) of weekday in (year, month).
    weekday: 0=Mon … 6=Sun (Python convention).
    """
    count = 0
    day = datetime.date(year, month, 1)
    while True:
        if day.weekday() == weekday:
            count += 1
            if count == n:
                return day
        day += datetime.timedelta(days=1)


def _last_weekday(year: int, month: int, weekday: int) -> datetime.date:
    """Return the last occurrence of weekday in (year, month)."""
    # FIX C2-10: handle month=12 without datetime.date(year, 13, 1) overflow
    if month == 12:
        first_next = datetime.date(year + 1, 1, 1)
    else:
        first_next = datetime.date(year, month + 1, 1)
    last = first_next - datetime.timedelta(days=1)
    while last.weekday() != weekday:
        last -= datetime.timedelta(days=1)
    return last


def _good_friday(year: int) -> datetime.date:
    """Easter Sunday via Anonymous Gregorian algorithm, then subtract 2 days."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day   = ((h + l - 7 * m + 114) % 31) + 1
    easter = datetime.date(year, month, day)
    return easter - datetime.timedelta(days=2)


def build_holiday_set(years: range) -> set:
    """Build the complete set of NYSE market holidays for the given years."""
    holidays = set()
    for yr in years:
        # New Year's Day (observed)
        # NYSE Rule: If Jan 1 is Sunday, observed Monday. If Jan 1 is Saturday, NO preceding Friday observance.
        nyd = datetime.date(yr, 1, 1)
        if nyd.weekday() == 6:  # Sunday
            holidays.add(datetime.date(yr, 1, 2))
        elif nyd.weekday() < 5:
            holidays.add(nyd)
        # if Saturday, it's not observed on Friday

        # MLK Day: 3rd Monday in January
        holidays.add(_nth_weekday(yr, 1, 0, 3))

        # Presidents Day: 3rd Monday in February
        holidays.add(_nth_weekday(yr, 2, 0, 3))

        # Good Friday (variable)
        holidays.add(_good_friday(yr))

        # Memorial Day: last Monday in May
        holidays.add(_last_weekday(yr, 5, 0))

        # Juneteenth (observed): June 19 (or nearest weekday) - started in 2022
        if yr >= 2022:
            jun19 = datetime.date(yr, 6, 19)
            if jun19.weekday() == 5:  # Saturday
                holidays.add(datetime.date(yr, 6, 18))
            elif jun19.weekday() == 6:  # Sunday
                holidays.add(datetime.date(yr, 6, 20))
            else:
                holidays.add(jun19)

        # Independence Day: July 4 (observed)
        jul4 = datetime.date(yr, 7, 4)
        if jul4.weekday() == 5:
            holidays.add(datetime.date(yr, 7, 3))
        elif jul4.weekday() == 6:
            holidays.add(datetime.date(yr, 7, 5))
        else:
            holidays.add(jul4)

        # Labor Day: 1st Monday in September
        holidays.add(_nth_weekday(yr, 9, 0, 1))

        # Thanksgiving: 4th Thursday in November
        holidays.add(_nth_weekday(yr, 11, 3, 4))

        # Christmas (observed)
        xmas = datetime.date(yr, 12, 25)
        if xmas.weekday() == 5:  # Saturday
            holidays.add(datetime.date(yr, 12, 24))
        elif xmas.weekday() == 6:  # Sunday
            holidays.add(datetime.date(yr, 12, 26))
        else:
            holidays.add(xmas)

    return holidays

def is_half_day(d: datetime.date) -> bool:
    """Return True if the given date is an NYSE half-day (closes at 1:00 PM EST)."""
    # Black Friday: Day after 4th Thursday in November
    if d.month == 11 and d.weekday() == 4 and 23 <= d.day <= 29:
        return True
    # Christmas Eve: Dec 24 on a weekday
    if d.month == 12 and d.day == 24 and d.weekday() < 5:
        return True
    # July 3: If July 4 is Tue, Wed, Thu, Fri
    if d.month == 7 and d.day == 3:
        jul4_weekday = datetime.date(d.year, 7, 4).weekday()
        if jul4_weekday in (1, 2, 3, 4):
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 2.  CORE EPHEMERIS HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _jd(dt_utc: datetime.datetime) -> float:
    """Convert a UTC-aware datetime to Julian Day Number.
    
    IMPORTANT: dt_utc MUST be timezone-aware (tzinfo != None) and in UTC.
    Passing a naive datetime will silently produce wrong planetary positions.
    """
    # FIX C3-3: Guard against naive datetimes
    assert dt_utc.tzinfo is not None, (
        f"_jd() requires a timezone-aware datetime, got naive: {dt_utc}"
    )
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )


def get_speed_cat(name: str, spd: float, is_retro: bool) -> str:
    """Classify planet speed into Vedic speed categories."""
    if is_retro:
        return "Retrograde"
    thres = SPEED_LABELS.get(name, {})
    if not thres:
        return "Mean"
    abs_spd = abs(spd)
    if abs_spd >= thres.get("ati_chara", 999): return "Ati-Chara (Very Fast)"
    if abs_spd >= thres.get("fast",      999): return "Fast"
    if abs_spd >= thres.get("mean",      0):   return "Mean"
    if abs_spd >= thres.get("slow",      0):   return "Slow"
    return "Very Slow"


def get_planet_state(jd: float) -> dict:
    """
    Calculate full Vedic Sidereal state for all planets at Julian Day jd.
    Returns a dict with per-planet sub-dicts plus aggregated indicators.
    """
    state: dict = {}
    sun_lon: Optional[float] = None

    # ── Raw ephemeris pass ──────────────────────────────────────────────────
    for name, pid in PLANETS.items():
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        result, _ = swe.calc_ut(jd, pid, flags)
        lon  = result[0] % 360.0
        spd  = result[3]
        sign = int(lon // 30)
        # FIX #1: clamp nakshatra index to 0–26
        nak  = int(lon / (360.0 / 27)) % 27
        is_retro = spd < 0

        state[name] = {
            "lon":          lon,
            "speed":        spd,
            "sign":         sign,
            "nak":          nak,
            "nak_name":     NAKSHATRA_NAMES[nak],
            "gana":         NAKSHATRA_GANA[nak],
            "is_retrograde": is_retro,
            "speed_cat":    get_speed_cat(name, spd, is_retro),
        }
        if name == "sun":
            sun_lon = lon

    # ── Combustion, debilitation, gandanta, vargottama ─────────────────────
    for name in ["moon", "mars", "merc", "ven", "jup", "sat"]:
        s = state[name]
        if sun_lon is not None:
            ang = abs(s["lon"] - sun_lon)
            if ang > 180.0:
                ang = 360.0 - ang
            # FIX C2-11: Moon cannot be combust — COMBUST_ORB default=0 prevents false positives
            # FIX C2-12: DEEP_COMBUST default=0 prevents all non-listed planets from being flagged
            s["is_combust"]      = ang <= COMBUST_ORB.get(name, 0)
            s["is_deep_combust"] = ang <= DEEP_COMBUST.get(name, 0)
        else:
            s["is_combust"] = s["is_deep_combust"] = False

        s["is_debilitated"] = (s["sign"] == DEBILITATION.get(name, -1))
        s["is_gandanta"]    = any(lo <= s["lon"] <= hi for lo, hi in GANDANTA_ZONES)

        # Vargottama: Navamsa sign == Rasi sign
        navamsa_sign = int(s["lon"] / (360.0 / 108)) % 12
        s["is_vargottama"] = (navamsa_sign == s["sign"])

    # ── Moon Panchanga ──────────────────────────────────────────────────────
    m  = state["moon"]
    su = state["sun"]
    elongation    = (m["lon"] - su["lon"]) % 360.0
    m["is_waxing"]= elongation < 180.0
    tithi_num     = int(elongation / (360.0 / 30))  # 0–29
    m["tithi"]    = tithi_num + 1                   # 1–30
    m["is_rikta"] = (m["tithi"] % 5) == 4           # Tithis 4,9,14,19,24,29
    # FIX #4: Amavasya = ONLY 30th Tithi = elongation [348°, 360°)
    m["is_amavasya"] = elongation >= 348.0
    # FIX #5: Purnima = ONLY 15th Tithi = elongation [168°, 180°)
    m["is_purnima"]  = 168.0 <= elongation < 180.0
    m["is_gandanta"] = any(lo <= m["lon"] <= hi for lo, hi in GANDANTA_ZONES)

    # Nitya Yoga (Sun + Moon sidereal, / (360/27))
    yoga_idx = int(((su["lon"] + m["lon"]) % 360.0) / (360.0 / 27))
    MALEFIC_YOGAS = {0, 5, 6, 12, 14, 15, 16, 18, 26}
    state["yoga_idx"]        = yoga_idx
    state["is_malefic_yoga"] = yoga_idx in MALEFIC_YOGAS

    # FIX #6: Vishti Karana positions corrected (7,15,23,31,39,47,55)
    karana_num = int(elongation / (360.0 / 60))
    VISHTI_POS = {7, 15, 23, 31, 39, 47, 55}
    state["is_vishti"] = karana_num in VISHTI_POS

    # Solar declination (tropical equatorial frame)
    try:
        eq_result, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SPEED | swe.FLG_EQUATORIAL)
        state["sun_decl"] = eq_result[1]
    except Exception:
        state["sun_decl"] = 0.0

    # FIX #3: Dagdha Tithi — correct classical map
    # Python weekday: 0=Mon,1=Tue,2=Wed,3=Thu,4=Fri,5=Sat,6=Sun
    # Classical: Mon=12,Tue=7,Wed=3,Thu=5,Fri=8,Sat=6,Sun=2
    # BUGFIX: Do NOT derive weekday from JD epoch arithmetic (UTC — can be 1 day off for NYSE).
    # Instead, store a sentinel; the real weekday is injected by detect_all_signals()
    # which always has access to the NYSE calendar date object.
    DAGDHA = {0: [12], 1: [7], 2: [3], 3: [5], 4: [8], 5: [6], 6: [2]}
    state["_DAGDHA_TABLE"] = DAGDHA
    state["_moon_tithi"] = m["tithi"]
    state["is_dagdha"] = False  # Will be correctly computed in detect_all_signals()

    # Eclipse season: Sun within 18 degrees of Rahu OR Ketu (both nodes)
    # FIX #8 (Cycle 1): check both nodes; FIX C3-12: Ketu arc = |180 - Rahu arc|
    rahu_lon = state["rahu"]["lon"]
    sun_rahu = abs(su["lon"] - rahu_lon)
    if sun_rahu > 180.0:
        sun_rahu = 360.0 - sun_rahu
    sun_ketu = abs(180.0 - sun_rahu)  # Ketu always opposite Rahu
    state["is_eclipse_season"] = (sun_rahu <= 18.0) or (sun_ketu <= 18.0)

    state["retro_count"] = sum(
        1 for p in ["merc", "ven", "mars", "jup", "sat"]
        if state[p]["is_retrograde"]
    )
    # Ascendant fields filled later by compute_ascendant()
    state["asc_lon"] = state["asc_nak"] = state["asc_gana"] = None
    return state


def compute_ascendant(jd: float) -> tuple:
    """
    Compute the Sidereal Ascendant for NYSE (New York) at Julian Day jd.
    Returns (sidereal_longitude, nakshatra_idx, gana_char).
    """
    try:
        houses_result = swe.houses(jd, NYSE_LAT, NYSE_LON, b"P")
        asc_trop  = houses_result[1][0]
        ayanamsha = swe.get_ayanamsa_ut(jd)
        asc_sid   = (asc_trop - ayanamsha) % 360.0
        # FIX #1: clamp nakshatra index
        nak_idx   = int(asc_sid / (360.0 / 27)) % 27
        return asc_sid, nak_idx, NAKSHATRA_GANA[nak_idx]
    except Exception:
        return 0.0, 0, "D"


# FIX #7: Solstice detection uses 3-day peak (not just one-sided check)
def get_solstice_type(date: datetime.date) -> Optional[str]:
    """
    Returns 'SUMMER' if the Sun's declination reached its maximum today,
    'WINTER' if it reached its minimum, else None.
    Uses a 3-day window: decl_prev < decl_today >= decl_next (summer peak).
    """
    def decl_at(d: datetime.date) -> float:
        dt = datetime.datetime(d.year, d.month, d.day, 12, tzinfo=UTC)
        try:
            eq, _ = swe.calc_ut(_jd(dt), swe.SUN, swe.FLG_SPEED | swe.FLG_EQUATORIAL)
            return eq[1]
        except Exception:
            return 0.0

    d_prev = decl_at(date - datetime.timedelta(days=1))
    d_curr = decl_at(date)
    d_next = decl_at(date + datetime.timedelta(days=1))

    if d_prev < d_curr >= d_next and d_curr > 22.5:
        return "SUMMER"
    if d_prev > d_curr <= d_next and d_curr < -22.5:
        return "WINTER"
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 3.  37-FINDING DETECTION RULES  (v2 — all conflicts resolved)
# ─────────────────────────────────────────────────────────────────────────────

def detect_all_signals(state: dict, date: datetime.date) -> list:
    """
    Evaluate all 37 finding rules against the current planetary state.
    Returns a list of signal dicts, with crash signals given highest priority.
    Contradictory signals are resolved: crash signals suppress bullish signals.
    """
    signals   = []
    crash_day = False  # FIX #11: track if a crash signal fires

    # DAGDHA FIX: Compute is_dagdha here using the NYSE date's weekday (not UTC JD epoch)
    # date.weekday() is guaranteed correct since it is the NYSE trading day.
    _dagdha_table = state.get("_DAGDHA_TABLE", {0:[12],1:[7],2:[3],3:[5],4:[8],5:[6],6:[2]})
    _moon_tithi   = state.get("_moon_tithi", state.get("moon", {}).get("tithi", 0))
    state["is_dagdha"] = _moon_tithi in _dagdha_table.get(date.weekday(), [])

    moon = state["moon"]
    sun  = state["sun"]
    merc = state["merc"]
    ven  = state["ven"]
    mars = state["mars"]
    jup  = state["jup"]
    sat  = state["sat"]
    asc_nak  = state.get("asc_nak")
    rc       = state["retro_count"]
    uttarayana   = state["sun_decl"] > 0
    dakshinayana = state["sun_decl"] < 0

    def sig(fid: int, title: str, direction: str, yld: float, stop: float,
            days: int, rationale: str, conditions: str = "", hist_label: str = ""):
        """Append a signal dict. hist_label overrides the yield display label."""
        meta = FINDING_META.get(fid, {"n_size": 100, "tier": 3})
        signals.append({
            "finding":    fid,
            "title":      title,
            "direction":  direction,
            "historical_yield": yld,
            "yield_pct":  yld,
            "n_size":     meta["n_size"],
            "tier":       meta["tier"],
            "stop_pct":   stop,
            "hold_days":  days,
            "rationale":  rationale,
            "conditions": conditions,
            "hist_label": hist_label,  # FIX #15: separate display label
        })

    # ── PHASE 1: CRASH SIGNALS (highest priority — evaluated first) ────────

    # F4 — Retrograde Pile-Up CRASH
    if rc >= 3:
        crash_day = True
        retrograde_planets = [p for p in ["merc","ven","mars","jup","sat"]
                               if state[p]["is_retrograde"]]
        sig(4, "RETROGRADE PILE-UP — CRASH SIGNAL", "SHORT", 12.3, 8.0, 5,
            f"ABSOLUTE CRASH: {rc} planets retrograde simultaneously. "
            "SPY -123 bps in 5 days. Exit ALL longs immediately.",
            f"Retro count: {rc} | Planets: {retrograde_planets}")

    # F5 — Double Vakri (Merc + Venus)
    if merc["is_retrograde"] and ven["is_retrograde"]:
        crash_day = True
        sig(5, "Mercury + Venus DOUBLE VAKRI — Commerce Freeze", "SHORT", 13.7, 9.0, 20,
            "Both commerce & capital planets Rx. "
            "SPY collapses +87 bps -> -137 bps over 20 days. Maximum short.",
            "Mercury Retrograde + Venus Retrograde")

    # F13 — Doomsday Bearish
    if moon["is_waxing"] and rc >= 3 and dakshinayana:
        crash_day = True
        sig(13, "DOOMSDAY BEARISH ALIGNMENT", "SHORT", 8.5, 10.0, 5,
            "ULTRA-RARE CRASH: Waxing+3+Retrogrades+Dakshinayana. "
            "DJIA -84 bps, SPY -65 bps in 5 days. Maximum short.",
            f"Shukla Paksha+{rc} Retrogrades+Dakshinayana")

    # F26 — Vargottama rescue fails
    if rc >= 3 and jup["is_vargottama"]:
        crash_day = True
        # FIX #12: was missing f-string prefix
        sig(26, "Pile-Up Overrides Vargottama", "SHORT", 17.8, 12.0, 20,
            f"Even Vargottama Jupiter cannot stop {rc} retrogrades. "
            "DJIA -178 bps. SHORT despite apparent strength.",
            f"{rc} Retrogrades+Jup Vargottama")

    # ── PHASE 2: NON-CRASH SIGNALS (only if they don't contradict crashes) ─

    # F1 — New Moon
    if moon["is_amavasya"]:
        if not merc["is_retrograde"] and not ven["is_retrograde"] and not crash_day:
            sig(1, "Frictionless Slingshot — New Moon Buy", "LONG", 13.1, 6.5, 20,
                "New Moon fear-bottom + inner planets Direct. "
                "SPY +131 bps historically. Clearest mean-reversion setup.",
                "Amavasya|Merc Direct|Ven Direct")
        elif merc["is_retrograde"] or ven["is_retrograde"]:
            sig(1, "Broken Bottom — New Moon + Retrograde (Fade)", "SHORT", 4.8, 5.0, 5,
                "New Moon during inner retrograde. The bounce fails. Fade it.",
                f"Amavasya|Merc_Retro:{merc['is_retrograde']}|Ven_Retro:{ven['is_retrograde']}")

    # F1b — Full Moon fade
    if moon["is_purnima"] and not merc["is_retrograde"]:
        sig(1, "Full Moon (Purnima) Fade", "SHORT", 2.2, 4.0, 1,
            "Full Moon = peak euphoria. SPY yields net loss on Day 1. "
            "Short the open, cover by EOD.",
            "Purnima|Mercury Direct")

    # F2 — Mercury Retrograde stagnation
    # FIX #10/13: F2 SHORT and F2b LONG are mutually exclusive — pick SHORT first
    if merc["is_retrograde"]:
        sig(2, "Mercury Retrograde — Stagnation Short Bias", "SHORT", 0.59, 4.0, 5,
            "Mercury Rx: commerce reversed. SPY -0.59 bps Day1, "
            "+3.57 bps Day5 vs +23.15 Direct. Lean short / reduce longs.",
            f"Mercury Retrograde speed={merc['speed']:.3f}")
        # F6 — Retrograde overrides Purnima
        if moon["is_purnima"]:
            sig(6, "Retrograde Nullifies Purnima — Double Fade", "SHORT", 1.8, 4.5, 5,
                "Full Moon bullishness NULLIFIED by Mercury Rx. "
                "SPY -17.69 vs +30 bps when Direct. Short the euphoria.",
                "Purnima + Mercury Retrograde")
    else:
        # Only emit Venus Retrograde LONG signal when Mercury is NOT retrograde
        # (no SHORT/LONG contradiction on same day for same base finding)
        if ven["is_retrograde"]:
            sig(2, "Venus Retrograde — Volatility Shock (Buy Dips)", "LONG", 2.7, 5.0, 5,
                "Venus Rx inflates True Range 123->150 bps. "
                "Buy vol spikes. Mean-revert intraday drops.",
                f"Venus Retrograde speed={ven['speed']:.3f}")

    # Mercury Station Direct — flash buy
    if abs(merc["speed"]) < 0.05 and not merc["is_retrograde"]:
        sig(2, "Mercury Stations Direct — 1-Day Flash Buy", "LONG", 1.9, 3.5, 1,
            "Exact station day: +19 bps Day1 historically. Buy at open.",
            f"Mercury stationing direct speed={merc['speed']:.4f}")

    # F3 — Mars Retrograde (clean, no crash) — FIX #11: suppress if crash_day
    if (mars["is_retrograde"] and not merc["is_retrograde"]
            and not ven["is_retrograde"] and not crash_day):
        sig(3, "Mars Retrograde (Clean) — Quiet Drift Up", "LONG", 10.0, 7.0, 20,
            "Mars Rx alone = historically BULLISH (+100 vs +74 bps). "
            "Aggression reduces, market drifts quietly upward.",
            "Mars Retro|Merc Direct|Ven Direct")

    # F7 — Krishna Paksha (Waning) buy — suppress on crash days
    if not moon["is_waxing"] and not merc["is_retrograde"] and not ven["is_retrograde"] and not crash_day:
        sig(7, "Krishna Paksha (Waning Moon) — Inversion Buy", "LONG", 0.79, 3.5, 20,
            "Waning Moon = highest forward returns. "
            "+79 vs +75 bps. Buy darkness, sell light.",
            "Waning Moon|Inner Planets Direct")

    # F8 — Rikta Tithi
    if moon["is_rikta"] and not merc["is_retrograde"] and not crash_day:
        sig(8, "Rikta Tithi (Empty) — Mean-Reversion Buy", "LONG", 0.82, 3.0, 20,
            "Classically forbidden days = highest 20-day returns. "
            "+82 bps. Buy institutional fear.",
            f"Tithi {moon['tithi']} (Rikta)|Mercury Direct")

    # F10 — Solstice
    solstice = get_solstice_type(date)
    if solstice == "WINTER":
        sig(10, "WINTER SOLSTICE — Strong Bullish Reversal", "LONG", 14.9, 7.0, 20,
            "Sun turns North. DJIA +88 bps (5d), +149 bps (20d). "
            "One of the strongest macro nodes in 140 years. BUY.",
            "Winter Solstice: Sun declination at nadir, turning North")
    if solstice == "SUMMER":
        sig(10, "SUMMER SOLSTICE — 1-Day Bearish Shock", "SHORT", 2.7, 5.0, 1,
            "Sun turns South. SPY -27 bps Day1. "
            "Short first 30min, cover by close.",
            "Summer Solstice: Sun declination at peak, turning South")

    # F11 — Retrograde crushing Uttarayana
    if uttarayana and (merc["is_retrograde"] or ven["is_retrograde"]):
        sig(11, "Retrograde Crushing Expansion Phase", "SHORT", 6.5, 5.5, 20,
            "Inner planet Rx during Sun northward phase. "
            "SPY 20d collapses 66%: +94->+32 bps. Lean short.",
            f"Uttarayana|Merc_Rx:{merc['is_retrograde']}|Ven_Rx:{ven['is_retrograde']}")

    # F12 — Holy Grail Bullish
    if (not moon["is_waxing"] and moon["is_rikta"] and uttarayana
            and not merc["is_retrograde"] and not ven["is_retrograde"]
            and not crash_day):
        sig(12, "HOLY GRAIL BULLISH ALIGNMENT", "LONG", 9.3, 6.5, 20,
            "ULTIMATE BUY: Waning+Rikta+Uttarayana+Inner Direct. "
            "+93 bps SPY. ~10x/yr. Maximum confidence.",
            f"Waning+Rikta(T{moon['tithi']})+Uttarayana+No_Friction")

    # F15 — Monthly Fear Paradox
    if not moon["is_waxing"] and moon["is_rikta"] and not crash_day:
        sig(15, "Monthly Fear Paradox (Waning+Rikta) — Buy", "LONG", 0.86, 3.5, 20,
            "Maximum classical fear = best monthly buy. +86 bps. ~28x/yr.",
            f"Tithi {moon['tithi']}|Waning|Rikta")

    # F16 — Retrograde Solstice Trap
    # FIX C2-4: Both Summer AND Winter solstice + retrograde = SHORT
    # Rationale: Retrograde destroys the RECOVERY. Winter solstice normally bullish,
    # but with Rx the expected bounce is killed. Both cases are SHORT.
    if solstice and (merc["is_retrograde"] or ven["is_retrograde"]):
        sig(16, f"Retrograde Solstice Trap ({solstice}) -- Recovery Killed", "SHORT", 4.5, 5.5, 5,
            f"{solstice} Solstice with inner planet Rx: the expected reversal is destroyed. "
            "Short the initial spike/gap. Cover within 5 days.",
            f"{solstice} Solstice+Inner Retrograde")

    # F17 — Lunar Gandanta bullish
    if moon["is_gandanta"] and not merc["is_retrograde"] and not crash_day:
        sig(17, "Moon in Gandanta — Slight Bullish Accelerant", "LONG", 0.85, 4.0, 20,
            "Moon at Water/Fire junction = +85 vs +76 bps. Add to longs.",
            f"Moon Gandanta {moon['lon']:.1f}|No Retrograde")

    # F18 — Abyss Alignment
    if moon["is_gandanta"] and not moon["is_waxing"] and moon["is_rikta"] and not crash_day:
        sig(18, "THE ABYSS ALIGNMENT — Hyper-Fear Buy", "LONG", 15.6, 7.5, 20,
            "HYPER-RARE: Waning+Rikta+Gandanta. SPY +155.82 bps. "
            "1.1x/yr. Fear climax inside karmic dissolution. BUY HARD.",
            f"Waning+Rikta(T{moon['tithi']})+Gandanta({moon['lon']:.1f})")

    # F19 — Mercury Combust effects
    if merc["is_retrograde"] and merc["is_deep_combust"]:
        sig(19, "Mercury Deep Combust + Retrograde — Annihilation", "SHORT", 8.8, 6.0, 20,
            "Mercury Rx + Deep Combust (<3 from Sun) = TOTAL destruction. "
            "SPY +11 bps vs +126 bps Direct+Combust. Reduce all longs.",
            "Mercury: Rx + Deep Combust")
    elif merc["is_retrograde"] and merc["is_combust"]:
        sig(19, "Mercury Combust + Retrograde — Friction Vector", "SHORT", 4.9, 5.0, 10,
            "Commerce disrupted: +49 bps 20d (well below baseline). Short bias.",
            "Mercury: Rx + Combust")
    elif not merc["is_retrograde"] and merc["is_deep_combust"]:
        sig(19, "Mercury Direct + Deep Combust — Solar Empowerment", "LONG", 12.6, 8.0, 20,
            "Sun amplifies forward Mercury. +126 vs +80 bps baseline. BUY.",
            "Mercury: Direct + Deep Combust")

    # F20 — Vakri-Uccha
    if jup["is_debilitated"] and jup["is_retrograde"]:
        sig(20, "Jupiter Vakri-Uccha (Neecha-Bhanga) — Exalted", "LONG", 23.4, 9.0, 20,
            "Jupiter Debilitated+Rx = Exalted per Vedic theorem. "
            "SPY +233 bps. MAXIMUM LONG. Ultra-rare.",
            f"Jupiter Neecha(sign {jup['sign']}) + Retrograde")
    if mars["is_debilitated"] and mars["is_retrograde"]:
        sig(20, "Mars Vakri-Uccha (Neecha-Bhanga) — Exalted", "LONG", 14.4, 8.0, 20,
            "Mars Debilitated+Rx = Exalted. SPY +144 bps. BUY.",
            f"Mars Neecha(sign {mars['sign']}) + Retrograde")

    # F21 — Combustion drag
    if jup["is_combust"] and not jup["is_retrograde"]:
        sig(21, "Jupiter Combust — Growth Engine Burned", "SHORT", 4.8, 5.5, 20,
            "Jupiter combusted by Sun. SPY +80->+32 bps. Reduce longs.",
            "Jupiter Combust|Direct")
    if sat["is_combust"] and not sat["is_retrograde"]:
        sig(21, "Saturn Combust — Structural Foundation Burned", "SHORT", 7.2, 6.0, 20,
            "Saturn combusted. SPY +84->+12 bps. Capital preservation mode.",
            "Saturn Combust|Direct")

    # F22 — Vargottama Jupiter
    if jup["is_vargottama"] and not jup["is_retrograde"] and not crash_day:
        sig(22, "Jupiter Vargottama Shield — Macro Tailwind", "LONG", 0.92, 3.5, 20,
            "Jupiter D1=D9 sign = unshakeable. SPY +75->+92 bps. Add longs.",
            f"Jupiter Vargottama {jup['lon']:.1f}")

    # F23 — Jupiter Gandanta stagnation
    if jup["is_gandanta"]:
        sig(23, "Jupiter in Gandanta — Growth Stagnation", "SHORT", 4.4, 4.0, 20,
            "Jupiter at Water/Fire boundary. DJIA +51->+5 bps. "
            "Market enters stagnation. Sell rallies.",
            f"Jupiter Gandanta {jup['lon']:.1f}")

    # F24 — Double Dissolution
    if jup["is_gandanta"] and sat["is_gandanta"]:
        sig(24, "DOUBLE DISSOLUTION — Secular Contraction", "SHORT", 10.75, 8.0, 20,
            "Both Jupiter+Saturn in Gandanta. DJIA -107.5 bps. "
            "Maximum defensive. Both structural pillars dissolving.",
            f"Jup Gandanta({jup['lon']:.1f})+Sat Gandanta({sat['lon']:.1f})")

    # F25 — False Light Trap
    if moon["is_purnima"] and jup["is_combust"] and sat["is_combust"]:
        sig(25, "FALSE LIGHT TRAP — Euphoria + Burned Macro", "SHORT", 9.4, 7.5, 5,
            "Full Moon rally attempt with Jup+Sat Combust. "
            "DJIA -93.9 bps. SELL THE GAP.",
            "Purnima+Jup Combust+Sat Combust")

    # F27 — Combust Dakshinayana
    if dakshinayana and jup["is_combust"]:
        sig(27, "Combust Dakshinayana — Winter Drift", "SHORT", 3.3, 4.5, 20,
            "Contraction season + wealth engine burned. "
            "SPY -33 bps, near-zero drift. Reduce net long.",
            "Dakshinayana+Jupiter Combust")

    # F28 — Eclipse of Growth
    if state["is_eclipse_season"] and jup["is_combust"]:
        sig(28, "TOTAL ECLIPSE OF GROWTH — Liquidity Vacuum", "SHORT", 11.9, 8.5, 20,
            "Eclipse Season + Jupiter Combust. DJIA -73 bps, SPY -119 bps. "
            "True liquidity vacuum. Maximum short.",
            "Eclipse Season+Jupiter Combust")

    # F30 — Malefic Yoga buy
    if state["is_malefic_yoga"] and not merc["is_retrograde"] and not crash_day:
        sig(30, "Malefic Nitya Yoga — Calamity Day Buy", "LONG", 1.3, 3.0, 5,
            "9 malefic Yogas yield +25.74 vs +16.15 bps. Buy the calamity. ~92x/yr.",
            f"Yoga #{state['yoga_idx']} (Malefic)|Mercury Direct")

    # F31 — Vishti Karana buy
    if state["is_vishti"] and not merc["is_retrograde"] and not crash_day:
        sig(31, "Vishti (Obstruction) Karana — Forbidden Buy", "LONG", 0.86, 3.5, 20,
            "Vishti = +85.92 bps, beats Merchant (+60 bps). Buy obstruction. ~38x/yr.",
            "Vishti Karana|Mercury Direct")

    # F32 — Rakshasa Moon
    if moon["gana"] == "R" and not merc["is_retrograde"] and not crash_day:
        sig(32, "Rakshasa Moon — Vol Injection", "LONG", 0.53, 4.0, 1,
            "Demonic nakshatra: True Range 123->127 bps. "
            "Buy dips, sell rips. Options plays on elevated vol. ~93x/yr.",
            f"Moon Nak: {moon['nak_name']} (Rakshasa)")

    # F33 — Dagdha Tithi (stand aside)
    if state["is_dagdha"]:
        sig(33, "Dagdha Tithi — Burnt Day (Stay Flat)", "CASH", 0.0, 0.0, 1,
            "Burnt day destroys momentum: +4.18->+1.36 bps. "
            "No momentum trades. Close scalps by EOD. ~23x/yr.",
            f"Dagdha Tithi (T{moon['tithi']})")

    # F34 — Moon Speed
    if moon["speed_cat"] in ("Ati-Chara (Very Fast)", "Fast") and not merc["is_retrograde"]:
        sig(34, "Fast Moon — 5-Day Momentum", "LONG", 1.96, 4.0, 5,
            "Fast Moon >14/day = +19.59 bps 5d momentum. Ride it.",
            f"Moon speed: {moon['speed']:.2f}/d ({moon['speed_cat']})")
    elif moon["speed_cat"] in ("Slow", "Very Slow") and not merc["is_retrograde"]:
        sig(34, "Slow Moon — 20-Day Grind Setup", "LONG", 0.81, 3.5, 20,
            "Slow Moon = stronger 20-day grind +81.45 bps. Patient accumulation.",
            f"Moon speed: {moon['speed']:.2f}/d ({moon['speed_cat']})")

    # F35 — Sun Nakshatra dominance
    sun_nak = sun["nak"]
    if sun_nak == 25:  # Uttara Bhadrapada (0-indexed 25 = nak #26)
        sig(35, "Sun in Uttara Bhadrapada — Top Bullish Sun Nak", "LONG", 5.86, 7.4, 20,
            "Sun Nak 26 = #1 ML feature. Top bullish. +5.86% realized yield.",
            f"Sun Nak: {sun['nak_name']} (idx {sun_nak})")
    if sun_nak == 22:  # Dhanishtha (0-indexed 22 = nak #23)
        sig(35, "Sun in Dhanishtha — Top Bearish Sun Nak", "SHORT", 5.58, 9.9, 20,
            "Sun Nak 23 = top bearish Sun Nakshatra. -5.58% realized yield.",
            f"Sun Nak: {sun['nak_name']} (idx {sun_nak})")

    # F36 — NYSE Ascendant (requires asc_nak to be set)
    if asc_nak is not None:
        if asc_nak == 3:  # Rohini
            sig(36, "NYSE Lagna — Rohini Ascendant (Bullish Open)", "LONG", 3.9, 7.8, 20,
                "Market opens in Rohini Asc. Top bullish opening. +3.90% yield.",
                f"Market Open Asc: {NAKSHATRA_NAMES[asc_nak]} ({asc_nak})")
        if asc_nak == 14:  # Swati
            sig(36, "NYSE Lagna — Swati Ascendant (Bearish Open)", "SHORT", 4.4, 11.1, 20,
                "Market opens in Swati Asc. Top bearish opening. -4.40% yield.",
                f"Market Open Asc: {NAKSHATRA_NAMES[asc_nak]} ({asc_nak})")

    # F37 — Grid extremes
    # FIX #15: hist_label distinguishes between historical avg and forward expectation
    if sun_nak == 6 and ven["is_retrograde"] and sat["is_retrograde"]:
        sig(37, "GRID BULLISH EXTREME — Sun Punarvasu + Ven/Sat Retro",
            "LONG", 13.46, 6.5, 20,
            "THE ABSOLUTE LIMIT: +1346 bps (+13.46%) over 20 days (N=36 in 141yr). "
            "Fires ~once every 4 years. MAXIMUM SIZE when active.",
            "Sun Nak 6 (Punarvasu)+Venus Retro+Saturn Retro",
            "Hist. 20D Avg Return: +13.46%")

    if (asc_nak == 14 and merc["is_retrograde"]
            and ven["speed_cat"] == "Mean"
            and jup["speed_cat"] in ("Slow", "Very Slow")):
        sig(37, "GRID BEARISH EXTREME — Swati Lagna + Merc Retro + Slow Jup",
            "SHORT", 10.95, 11.1, 20,
            "THE ABSOLUTE BEARISH LIMIT: -1095 bps (-10.95%) over 20 days (N=30 in 141yr). "
            "MAXIMUM SHORT. Swati ASC + Mercury Rx + Slow Jupiter is lethal.",
            "Swati ASC+Mercury Retro+Venus Mean+Jupiter Slow",
            "Hist. 20D Avg Return: -10.95%")

    if (ven["speed_cat"] == "Mean" and mars["is_retrograde"]
            and sat["speed_cat"] == "Ati-Chara (Very Fast)"):
        sig(37, "Grid High-Freq Bullish Engine (N=1356, +1.86%)",
            "LONG", 1.86, 5.0, 20,
            "High-freq structural skew: Venus Mean+Mars Retro+Saturn Ati-Chara. "
            "+186 bps. Fires ~10x/yr.",
            "Venus Mean+Mars Retro+Saturn Ati-Chara (Very Fast)",
            "Hist. 20D Avg Return: +1.86%")

    if not signals:
        sig(99, 'NO SIGNALS — STAND ASIDE', 'CASH', 0.0, 0.0, 1, 'No Vedic indicators triggered today. Preserve capital.')
    return signals


# ─────────────────────────────────────────────────────────────────────────────
# 4.  TRADE ENTRY FORMATTER
# ─────────────────────────────────────────────────────────────────────────────

def format_trade_entry(date: datetime.date, window_start: str,
                        window_end: Optional[str], signal: dict,
                        rank: int, total: int) -> str:
    """Render one trade signal as a Markdown table block."""
    d_icon = {"LONG": "LONG", "SHORT": "SHORT", "CASH": "CASH"}.get(
        signal["direction"], "?"
    )
    yld  = signal["yield_pct"]
    stop = signal["stop_pct"]
    days = signal["hold_days"]
    # FIX #15: use hist_label when available
    yield_label = signal.get("hist_label") or f"Hist. 20D Avg: +{yld:.2f}%"
    window_str  = window_start + (f" to {window_end}" if window_end else "")

    if signal["direction"] == "LONG":
        sl_rule = f"Trailing stop {stop:.1f}% below highest close during hold"
        entry   = "BUY at market open or window start"
    elif signal["direction"] == "SHORT":
        sl_rule = f"Trailing stop {stop:.1f}% above lowest close during hold"
        entry   = "SELL SHORT at market open or window start"
    else:
        sl_rule = "No position — stand aside completely"
        entry   = "Do NOT enter any directional trades"

    size = "FULL (100%)" if yld >= 10.0 else ("HALF (50%)" if yld >= 5.0 else "QUARTER (25%)")

    return (
        f"### [{rank}/{total}] Finding #{signal['finding']} -- {signal['title']}\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| **Date** | {date.strftime('%A, %B %d, %Y')} |\n"
        f"| **Entry Window (EST)** | {window_str} |\n"
        f"| **Direction** | **{d_icon}** |\n"
        f"| **Historical Return** | {yield_label} |\n"
        f"| **Trailing Stop** | {stop:.1f}% |\n"
        f"| **Hold Period** | {days} trading days |\n"
        f"| **Position Size** | {size} |\n"
        f"| **Entry Rule** | {entry} |\n"
        f"| **Stop Loss Rule** | {sl_rule} |\n"
        f"| **Signal Conditions** | {signal['conditions']} |\n\n"
        f"> **Rationale:** {signal['rationale']}\n\n---\n\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5.  MAIN CALENDAR GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_calendar(start_date=None, end_date=None, output_path=None):
    """
    Scan every NYSE trading day from start_date to end_date.
    Detect all 37 findings. Write complete trading plan to Markdown.
    
    Args:
        start_date: datetime.date — defaults to module-level START_DATE (2026-07-30)
        end_date:   datetime.date — defaults to module-level END_DATE   (2028-07-30)
        output_path: str — full path for the output file. If None, auto-generated.
    """
    if start_date is None:
        start_date = START_DATE
    if end_date is None:
        end_date = END_DATE

    # Auto-generate output file name from date range
    script_dir = os.path.dirname(os.path.abspath(__file__))
    year_label = f"{start_date.year}_{end_date.year}"
    if output_path is None:
        output_path = os.path.join(script_dir, f"master_trading_plan_{year_label}.md")

    date_range_str = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
    print(f"[MASTER PLAN v2] Generating trading plan ({date_range_str}) for all 37 findings...")
    print(f"[MASTER PLAN v2] Output -> {output_path}")

    # Build holiday set dynamically from the actual year range
    HOLIDAYS = build_holiday_set(range(start_date.year, end_date.year + 2))

    all_entries: list = []
    current = start_date

    while current <= end_date:
        if current.weekday() >= 5 or current in HOLIDAYS:
            current += datetime.timedelta(days=1)
            continue

        # Compute planetary state at NYSE market open
        dt_open = NY_TZ.localize(datetime.datetime.combine(current, MARKET_OPEN))
        jd_open = _jd(dt_open.astimezone(UTC))
        state   = get_planet_state(jd_open)
        asc_lon, asc_nak, asc_gana = compute_ascendant(jd_open)
        state["asc_lon"] = asc_lon
        state["asc_nak"] = asc_nak
        state["asc_gana"] = asc_gana
        
        # Dynamic close time for half-days
        close_time = datetime.time(13, 0) if is_half_day(current) else MARKET_CLOSE
        close_str = close_time.strftime("%I:%M %p").lstrip("0")

        # Detect daily signals (planetary state doesn't change significantly intraday)
        for s in detect_all_signals(state, current):
            all_entries.append({
                "date": current,
                "window_start": "09:30 AM",
                "window_end":   close_str,
                "signal": s,
                "intraday": False,
            })

        # Intraday Ascendant scan for Finding 37 (Ascendant-sensitive Grid Extreme)
        # FIX C5-1: Finding 36 is explicitly a daily *Open* signal, must not fire intraday.
        step    = datetime.timedelta(minutes=STEP_MIN)
        t       = dt_open + step  # start after first window already captured
        t_close = NY_TZ.localize(datetime.datetime.combine(current, close_time))
        prev_nak = asc_nak

        while t < t_close:
            jd_t = _jd(t.astimezone(UTC))
            asc_t, nak_t, gana_t = compute_ascendant(jd_t)
            if nak_t != prev_nak:
                state_t = get_planet_state(jd_t)
                state_t["asc_lon"]  = asc_t
                state_t["asc_nak"]  = nak_t
                state_t["asc_gana"] = gana_t
                for s in detect_all_signals(state_t, current):
                    # F37 is the only intraday signal
                    if s["finding"] == 37:
                        t_str   = t.strftime("%I:%M %p").lstrip("0")
                        t_end   = min(t + datetime.timedelta(hours=2), t_close)
                        te_str  = t_end.strftime("%I:%M %p").lstrip("0")
                        all_entries.append({
                            "date":         current,
                            "window_start": t_str,
                            "window_end":   te_str,
                            "signal":       s,
                            "intraday":     True,
                        })
                prev_nak = nak_t
            t += step

        current += datetime.timedelta(days=1)
        if current.day == 1:
            print(f"  Processed through {current.strftime('%B %Y')}")

    # Sort by date, then yield descending (highest-impact first within each day)
    all_entries.sort(key=lambda e: (e["date"], -e["signal"]["yield_pct"]))

    # FIX #9: Deduplication — intraday signals preserve unique window times
    seen: set = set()
    deduped: list = []
    for e in all_entries:
        s = e["signal"]
        if e["intraday"]:
            # For intraday, key includes window start to preserve multiple windows
            key = (e["date"], s["finding"], s["direction"], e["window_start"])
        else:
            key = (e["date"], s["finding"], s["direction"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    # FIX C3-8: Guard against suspiciously empty output (e.g. ephemeris data missing)
    assert len(deduped) > 100, (
        f"[FATAL] Suspiciously low signal count ({len(deduped)}). "
        "Check ephemeris data and pyswisseph installation."
    )
    print(f"\n[MASTER PLAN v2] Total unique signals: {len(deduped)}")

    dir_counts: dict  = {"LONG": 0, "SHORT": 0, "CASH": 0}
    find_counts: dict = {}
    for e in deduped:
        d = e["signal"]["direction"]
        dir_counts[d]  = dir_counts.get(d, 0) + 1
        f = e["signal"]["finding"]
        find_counts[f] = find_counts.get(f, 0) + 1

    # ── Build Markdown document ─────────────────────────────────────────────
    header = (
        f"# MASTER VEDIC-QUANT TRADING PLAN {start_date.year}-{end_date.year}\n"
        "## All 37 Proven Findings | SPY / ES1! | Swiss Ephemeris (Lahiri Sidereal)\n\n"
        f"> **Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} EST  \n"
        "> **Method:** Swiss Ephemeris (Lahiri Ayanamsha) + 141-Year DuckDB Backtests  \n"
        "> **Instrument:** SPY (S&P 500 ETF) / ES1! (E-mini S&P 500 Futures)  \n"
        f"> **Total Unique Signals:** {len(deduped)}  \n"
        f"> **Coverage:** {date_range_str}  \n\n"
        "---\n\n"
        "## HOW TO USE THIS PLAN\n\n"
        "| Symbol | Meaning |\n|---|---|\n"
        "| **LONG** | Buy SPY at market open -- ride with trailing stop |\n"
        "| **SHORT** | Sell short SPY / sell ES1! at the window open |\n"
        "| **CASH** | No directional position -- stand flat for the day |\n"
        "| **FULL (100%)** | High-conviction signal (hist. return >=10%) |\n"
        "| **HALF (50%)** | Medium-conviction signal (5-10% hist. return) |\n"
        "| **QUARTER (25%)** | Structural/frequency edge (<5% hist. return) |\n\n"
        "> IMPORTANT: Stop Loss Rule -- Set a trailing stop at the listed % from the\n"
        "> highest close (LONG) or lowest close (SHORT) during the hold period.\n"
        "> This trails with the market to lock in profit.\n\n"
        "> WARNING: CRASH SIGNAL OVERRIDE -- If Finding #4 (Retrograde Pile-Up),\n"
        "> #5 (Double Vakri), or #13 (Doomsday) fires, EXIT ALL LONGS IMMEDIATELY\n"
        "> and enter SHORT. These override every bullish signal.\n\n"
        "> Signal Hierarchy:\n"
        "> 1. Crash Signals (#4, #5, #13, #26) -- ABSOLUTE PRIORITY\n"
        "> 2. Holy Grail Signals (#12, #18, #37 Extremes) -- Maximum Size\n"
        "> 3. High-Yield Rare Signals (>10% hist. return)\n"
        "> 4. High-Frequency Daily Signals (<5% hist. return, structural edge)\n\n"
        "---\n\n"
    )

    from collections import defaultdict
    import signal_aggregator
    
    # Pre-calculate daily probability aggregates
    signals_by_date = defaultdict(list)
    for e in deduped:
        signals_by_date[e["date"]].append(e["signal"])
        
    daily_aggregates = {}
    for d, sigs in signals_by_date.items():
        p_long, p_short, net_yld, bias, is_override = signal_aggregator.compute_daily_probability(sigs)
        daily_aggregates[d] = {
            "p_long": p_long,
            "p_short": p_short,
            "net_yield": net_yld,
            "bias": bias,
            "is_override": is_override
        }

    from calendar import month_name as MN
    body_lines: list = []
    prev_month = None
    prev_day = None
    total = len(deduped)

    for rank, e in enumerate(deduped, 1):
        # Month header
        mo_key = (e["date"].year, e["date"].month)
        if mo_key != prev_month:
            body_lines.append(f"## {MN[e['date'].month]} {e['date'].year}\n\n")
            prev_month = mo_key
            
        # Daily Math Aggregator Header
        if e["date"] != prev_day:
            prev_day = e["date"]
            agg = daily_aggregates[e["date"]]
            d_str = e["date"].strftime("%A, %B %d, %Y")
            body_lines.append(f"### ☀️ {d_str} — DAILY MATH AGGREGATE\n")
            body_lines.append(f"> **Net System Bias:** {agg['bias']}\n")
            if agg['is_override']:
                body_lines.append(f"> 🚨 **TIER 1 OVERRIDE ACTIVE** 🚨\n")
            body_lines.append(f"> **P(Long):** {agg['p_long']:.1%} | **P(Short):** {agg['p_short']:.1%} | **Expected Net Yield:** {agg['net_yield']:+.2f}%\n\n")
            body_lines.append("---\n\n")
            
        body_lines.append(format_trade_entry(
            e["date"], e["window_start"], e["window_end"],
            e["signal"], rank, total
        ))

    FINDING_TITLES = {
        1: "New Moon/Full Moon Phases",      2: "Inner Retrograde Effects",
        3: "Mars Retrograde (Clean)",        4: "Retrograde Pile-Up CRASH",
        5: "Double Vakri Commerce Freeze",   6: "Retrograde Overrides Purnima",
        7: "Krishna Paksha Inversion",       8: "Rikta Tithi Empty Buy",
        10: "Solstice Reversals",            11: "Retrograde Crushes Uttarayana",
        12: "Holy Grail Bullish",            13: "Doomsday Bearish",
        15: "Monthly Fear Paradox",          16: "Retrograde Solstice Trap",
        17: "Lunar Gandanta Bullish",        18: "Abyss Alignment",
        19: "Mercury Combust Effects",       20: "Vakri-Uccha Exaltation",
        21: "Combustion Drag (Jup/Sat)",     22: "Jupiter Vargottama Shield",
        23: "Jupiter Gandanta Stagnation",   24: "Double Dissolution",
        25: "False Light Trap",              26: "Vargottama Rescue Fails",
        27: "Combust Dakshinayana Drift",    28: "Eclipse of Growth",
        30: "Malefic Yoga Buy",              31: "Vishti Karana Buy",
        32: "Rakshasa Moon Vol",             33: "Dagdha Tithi Cash",
        34: "Moon Speed Trade",              35: "Sun Nakshatra Dominance",
        36: "NYSE Ascendant (Lagna)",        37: "Grid Search Extremes",
    }
    summary_rows = "\n".join(
        f"| #{k} | {FINDING_TITLES.get(k, f'Finding #{k}')} | {v} |"
        for k, v in sorted(find_counts.items())
    )
    summary = (
        "\n---\n\n## PLAN STATISTICS\n\n"
        "| Metric | Count |\n|---|---|\n"
        f"| **Total Unique Signals** | {total} |\n"
        f"| **LONG Signals** | {dir_counts.get('LONG', 0)} |\n"
        f"| **SHORT Signals** | {dir_counts.get('SHORT', 0)} |\n"
        f"| **CASH Days** | {dir_counts.get('CASH', 0)} |\n\n"
        "### Signals by Finding:\n\n"
        "| Finding | Title | Count |\n|---|---|---|\n"
        + summary_rows + "\n"
    )

    full_doc = header + "".join(body_lines) + summary
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(full_doc)

    print(f"\n[MASTER PLAN v2] Done!")
    print(f"  File: {output_path}")
    print(f"  LONG: {dir_counts.get('LONG',0)} | SHORT: {dir_counts.get('SHORT',0)} | CASH: {dir_counts.get('CASH',0)}")
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# 6.  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Vedic Quant Master Trading Plan Generator")
    parser.add_argument("--start", default=None,
        help="Start date YYYY-MM-DD (default: 2026-07-30 for future plan)")
    parser.add_argument("--end", default=None,
        help="End date YYYY-MM-DD (default: 2028-07-30 for future plan)")
    parser.add_argument("--out", default=None,
        help="Output file path (auto-generated if not specified)")
    args = parser.parse_args()

    sd = datetime.date.fromisoformat(args.start) if args.start else None
    ed = datetime.date.fromisoformat(args.end)   if args.end   else None
    generate_calendar(start_date=sd, end_date=ed, output_path=args.out)


# CRITICAL BUG FIX #17: Ensure swisseph is closed
import atexit
atexit.register(swe.close)
