"""
Panchang Engine - Complete Vedic Panchang & Hora Calculator
============================================================
Computes the five limbs of Vedic time (Tithi, Vara, Nakshatra, Yoga, Karana)
plus Hora (planetary hours), Rahu Kaal, Mercury Retrograde, and Combustion.

Used for both natal (IPO) and transit date analysis.
"""
import swisseph as swe
import math, datetime

# ══════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════

# Chaldean Hora sequence (never deviates)
HORA_SEQ = ['Sun', 'Ven', 'Merc', 'Moon', 'Sat', 'Jup', 'Mars']

# Day lord → first Hora planet (index into HORA_SEQ)
# Monday=0(Moon=idx3), Tuesday=1(Mars=idx6), ..., Sunday=6(Sun=idx0)
DAY_FIRST_HORA = {
    0: 3,  # Monday → Moon
    1: 6,  # Tuesday → Mars
    2: 2,  # Wednesday → Mercury
    3: 5,  # Thursday → Jupiter
    4: 1,  # Friday → Venus
    5: 4,  # Saturday → Saturn
    6: 0,  # Sunday → Sun
}

# Hora financial scores
HORA_SCORE = {
    'Jup': +3, 'Ven': +2, 'Merc': +2,
    'Moon': +1, 'Sun': +1, 'Mars': -1, 'Sat': -2
}

# Vara (weekday) scores
VARA_SCORE = {
    0: +1,  # Monday (Moon)
    1: -1,  # Tuesday (Mars)
    2: +2,  # Wednesday (Mercury)
    3: +3,  # Thursday (Jupiter)
    4: +2,  # Friday (Venus)
    5: -2,  # Saturday (Saturn)
    6: +1,  # Sunday (Sun)
}
VARA_LORD = {0:'Moon', 1:'Mars', 2:'Merc', 3:'Jup', 4:'Ven', 5:'Sat', 6:'Sun'}

# Tithi scores (index 1-30)
# Shukla 1-15, Krishna 16-30
TITHI_SCORE = {}
# Shukla Paksha
_shukla = {1:+1, 2:+2, 3:+2, 4:0, 5:+2, 6:+2, 7:+2, 8:-2, 9:-2,
           10:+2, 11:+3, 12:+2, 13:+2, 14:-3, 15:+1}
# Krishna Paksha
_krishna = {16:+1, 17:+1, 18:+1, 19:0, 20:+1, 21:+1, 22:+1, 23:-2, 24:-2,
            25:+1, 26:+2, 27:+1, 28:+1, 29:-3, 30:-3}
TITHI_SCORE.update(_shukla)
TITHI_SCORE.update(_krishna)

# Danger Tithis (8th, 9th, 14th in both Pakshas)
TITHI_DANGER = {8, 9, 14, 23, 24, 29}

# Yoga names and scores (1-27)
YOGA_NAMES = [
    '', 'Vishkumbha', 'Preeti', 'Ayushman', 'Saubhagya', 'Shobhana',
    'Atiganda', 'Sukarma', 'Dhriti', 'Shoola', 'Ganda', 'Vriddhi',
    'Dhruva', 'Vyaghata', 'Harshana', 'Vajra', 'Siddhi', 'Vyatipata',
    'Variyana', 'Parigha', 'Shiva', 'Siddha', 'Sadhya', 'Shubha',
    'Shukla', 'Brahma', 'Indra', 'Vaidhriti'
]
YOGA_INAUSPICIOUS = {1, 6, 9, 10, 13, 15, 17, 19, 27}  # 9 bad Yogas
YOGA_EXCELLENT = {4, 12, 16, 25, 26}  # Saubhagya, Dhruva, Siddhi, Brahma, Indra
YOGA_WORST = {17, 27}  # Vyatipata, Vaidhriti → strongest reversal signals
YOGA_SCORE = {}
for i in range(1, 28):
    if i in YOGA_WORST:
        YOGA_SCORE[i] = -3
    elif i in YOGA_INAUSPICIOUS:
        YOGA_SCORE[i] = -2
    elif i in YOGA_EXCELLENT:
        YOGA_SCORE[i] = +3
    elif i in {3, 11, 18, 20, 23}:
        YOGA_SCORE[i] = +2  # Ayushman, Vriddhi, Variyana, Shiva, Shubha
    else:
        YOGA_SCORE[i] = +1  # All other auspicious

# Karana cycle: 7 moveable repeat through 60 Karanas per month
KARANA_MOVEABLE = ['Bava', 'Balava', 'Kaulava', 'Taitila', 'Garija', 'Vanija', 'Vishti']
KARANA_FIXED = {
    57: 'Shakuni',    # Krishna 14, 2nd half
    58: 'Chatushpada', # Amavasya, 1st half
    59: 'Naga',        # Amavasya, 2nd half
    60: 'Kinstughna',  # Shukla 1, 1st half
}
KARANA_SCORE_MAP = {
    'Vanija': +3, 'Bava': +2, 'Balava': +2,
    'Kaulava': +1, 'Taitila': +1, 'Garija': +1,
    'Shakuni': 0, 'Chatushpada': 0, 'Naga': 0,
    'Kinstughna': -2, 'Vishti': -3
}

# Nakshatra (Panchang) scores — Moon's nakshatra quality
NAK_PANCHANG_BEST = {4, 8, 12, 21, 26}     # Rohini, Pushya, U.Phalguni, U.Ashadha, U.Bhadra → +3
NAK_PANCHANG_GOOD = {7, 13, 15, 16, 22, 23} # Punarvasu, Hasta, Swati, Vishakha, Shravana, Dhanishtha → +2
NAK_PANCHANG_BAD = {6, 9, 18, 19, 3}       # Ardra, Ashlesha, Jyeshtha, Mula, Krittika → -2
NAK_PANCHANG_GANDA = {1, 9, 10, 18, 19, 27} # Ganda Mool junction stars → 0

# Combustion thresholds (degrees from Sun)
COMBUST_THRESHOLD = {
    'Moon': 12, 'Mars': 17, 'Merc': 14, 'Jup': 11, 'Ven': 10, 'Sat': 15
}

# Rahu Kaal sequence by weekday (0=Mon,...,6=Sun)
# Each value = which 1/8th segment of the day (from sunrise) is Rahu Kaal
# Mon=2nd, Sat=3rd, Fri=4th, Wed=5th, Thu=6th, Tue=7th, Sun=8th
RAHU_KAAL_SEGMENT = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}

# NYSE location
NYSE_LAT = 40.7128
NYSE_LON = -74.0060


# ══════════════════════════════════════════════════════════
# SUNRISE / SUNSET CALCULATION
# ══════════════════════════════════════════════════════════

def compute_sunrise_sunset(jd, lat=NYSE_LAT, lon=NYSE_LON):
    """Compute sunrise and sunset Julian Days for a given date at a location."""
    geopos = (lon, lat, 0.0)  # (longitude, latitude, altitude)
    try:
        res_rise, tret_rise = swe.rise_trans(jd - 0.5, swe.SUN, swe.CALC_RISE, geopos)
        jd_rise = tret_rise[0] if res_rise == 0 else jd - 0.5 + (11.5 / 24)
        res_set, tret_set = swe.rise_trans(jd - 0.5, swe.SUN, swe.CALC_SET, geopos)
        jd_set = tret_set[0] if res_set == 0 else jd - 0.5 + (24.5 / 24)
    except:
        # Fallback: approximate sunrise 6:30AM ET → 11:30 UTC, sunset 7:30PM ET → 00:30 UTC+1
        jd_rise = jd - 0.5 + (11.5 / 24)  # ~6:30 AM ET in UTC
        jd_set = jd - 0.5 + (24.5 / 24)   # ~7:30 PM ET in UTC
    return jd_rise, jd_set


# ══════════════════════════════════════════════════════════
# HORA CALCULATOR (T25)
# ══════════════════════════════════════════════════════════

def compute_hora(jd, lat=NYSE_LAT, lon=NYSE_LON):
    """
    Compute which planet rules the Hora at the given Julian Day.
    Uses unequal (classical) Hora hours from actual sunrise/sunset.
    
    Returns: (hora_planet, hora_number, hora_score)
    """
    jd_rise, jd_set = compute_sunrise_sunset(jd, lat, lon)
    
    day_length = jd_set - jd_rise
    night_length = (jd_rise + 1.0) - jd_set  # next sunrise - this sunset
    
    if jd >= jd_rise and jd < jd_set:
        # Daytime
        hora_duration = day_length / 12.0
        elapsed_horas = int((jd - jd_rise) / hora_duration)
        hora_num = elapsed_horas + 1  # 1-based
    elif jd >= jd_set:
        # Nighttime (same day)
        hora_duration = night_length / 12.0
        elapsed_horas = int((jd - jd_set) / hora_duration)
        hora_num = 12 + elapsed_horas + 1
    else:
        # Before sunrise (previous night)
        prev_set = jd_set - 1.0  # approximate
        hora_duration = (jd_rise - prev_set) / 12.0
        elapsed_horas = int((jd - prev_set) / hora_duration) if hora_duration > 0 else 0
        hora_num = 12 + elapsed_horas + 1
    
    # Get day of week (0=Mon...6=Sun)
    # Standard JD: (JD + 1.5) % 7 → 0=Sun. Convert: (std+6)%7 → 0=Mon
    std_wd = int(jd + 1.5) % 7
    weekday = (std_wd + 6) % 7
    
    # First Hora planet for this weekday
    first_hora_idx = DAY_FIRST_HORA[weekday]
    
    # Walk the Chaldean sequence (hora_num - 1) steps from first planet
    planet_idx = (first_hora_idx + (hora_num - 1)) % 7
    hora_planet = HORA_SEQ[planet_idx]
    
    return hora_planet, hora_num, HORA_SCORE.get(hora_planet, 0)


# ══════════════════════════════════════════════════════════
# TITHI CALCULATOR (T26)
# ══════════════════════════════════════════════════════════

def compute_tithi(sun_sid_lon, moon_sid_lon):
    """
    Compute Tithi number (1-30) from sidereal Sun and Moon longitudes.
    Every 12° of Moon-Sun separation = 1 Tithi.
    
    Returns: (tithi_number, paksha, tithi_score, is_ekadashi, is_danger)
    """
    diff = (moon_sid_lon - sun_sid_lon) % 360
    tithi = int(diff / 12) + 1  # 1-30
    if tithi > 30: tithi = 30
    
    paksha = 'Shukla' if tithi <= 15 else 'Krishna'
    score = TITHI_SCORE.get(tithi, 0)
    is_ekadashi = tithi in (11, 26)  # Shukla 11 or Krishna 11 (=26)
    is_danger = tithi in TITHI_DANGER
    
    return tithi, paksha, score, is_ekadashi, is_danger


# ══════════════════════════════════════════════════════════
# VARA CALCULATOR (T27)
# ══════════════════════════════════════════════════════════

def compute_vara(jd):
    """
    Compute Vara (weekday) and its lord.
    
    Returns: (weekday_num, vara_lord, vara_score)
    """
    std_wd = int(jd + 1.5) % 7   # standard: 0=Sun
    weekday = (std_wd + 6) % 7    # convert to 0=Mon...6=Sun
    lord = VARA_LORD[weekday]
    score = VARA_SCORE[weekday]
    return weekday, lord, score


# ══════════════════════════════════════════════════════════
# YOGA CALCULATOR (T29)
# ══════════════════════════════════════════════════════════

def compute_yoga(sun_sid_lon, moon_sid_lon):
    """
    Compute Nithya Yoga (1-27) from Sun+Moon sidereal longitudes.
    Formula: (Sun + Moon) / 13°20' = Yoga number
    
    Returns: (yoga_number, yoga_name, yoga_score, is_inauspicious, is_worst)
    """
    combined = (sun_sid_lon + moon_sid_lon) % 360
    yoga_num = int(combined / (360.0 / 27)) + 1
    if yoga_num > 27: yoga_num = 27
    
    name = YOGA_NAMES[yoga_num] if yoga_num < len(YOGA_NAMES) else 'Unknown'
    score = YOGA_SCORE.get(yoga_num, 0)
    is_inauspicious = yoga_num in YOGA_INAUSPICIOUS
    is_worst = yoga_num in YOGA_WORST
    
    return yoga_num, name, score, is_inauspicious, is_worst


# ══════════════════════════════════════════════════════════
# KARANA CALCULATOR (T30)
# ══════════════════════════════════════════════════════════

def compute_karana(tithi_number):
    """
    Compute Karana (half-Tithi) from Tithi number.
    Each Tithi has 2 Karanas. 60 Karanas per month total.
    4 fixed Karanas at month boundaries, 7 moveable repeat.
    
    Returns: (karana_name, karana_score, is_vishti, is_vanija)
    """
    # Karana number 1-60 (2 per Tithi)
    # For simplicity, compute the Karana at the start of the Tithi (first half)
    karana_idx = (tithi_number - 1) * 2 + 1  # 1-based first-half karana
    
    # Fixed Karanas: 57=Shakuni, 58=Chatushpada, 59=Naga, 60=Kinstughna
    if karana_idx >= 57:
        name = KARANA_FIXED.get(karana_idx, 'Kinstughna')
    elif karana_idx == 1:
        name = 'Kinstughna'  # First Karana of Shukla Pratipada
    else:
        # Moveable Karanas cycle: index (karana_idx - 2) % 7
        cycle_idx = (karana_idx - 2) % 7
        name = KARANA_MOVEABLE[cycle_idx]
    
    score = KARANA_SCORE_MAP.get(name, 0)
    is_vishti = name == 'Vishti'
    is_vanija = name == 'Vanija'
    
    return name, score, is_vishti, is_vanija


# ══════════════════════════════════════════════════════════
# NAKSHATRA PANCHANG SCORE (T28)
# ══════════════════════════════════════════════════════════

def compute_nak_panchang_score(moon_sid_lon):
    """
    Score the Moon's nakshatra position for Panchang quality.
    
    Returns: (nak_index_1based, nak_score)
    """
    nak_idx = int(moon_sid_lon / (360 / 27)) + 1
    if nak_idx > 27: nak_idx = 27
    
    if nak_idx in NAK_PANCHANG_BEST:
        return nak_idx, +3
    elif nak_idx in NAK_PANCHANG_GOOD:
        return nak_idx, +2
    elif nak_idx in NAK_PANCHANG_BAD:
        return nak_idx, -2
    elif nak_idx in NAK_PANCHANG_GANDA:
        return nak_idx, 0
    else:
        return nak_idx, +1


# ══════════════════════════════════════════════════════════
# RAHU KAAL CHECK
# ══════════════════════════════════════════════════════════

def is_rahu_kaal(jd, lat=NYSE_LAT, lon=NYSE_LON):
    """
    Check if the given moment falls within Rahu Kaal.
    Rahu Kaal = 1/8th of the daylight period.
    
    Returns: True if in Rahu Kaal
    """
    jd_rise, jd_set = compute_sunrise_sunset(jd, lat, lon)
    day_length = jd_set - jd_rise
    segment_length = day_length / 8.0
    
    std_wd = int(jd + 1.5) % 7   # standard: 0=Sun
    weekday = (std_wd + 6) % 7    # 0=Mon...6=Sun
    rk_seg = RAHU_KAAL_SEGMENT.get(weekday, 1)
    
    rk_start = jd_rise + (rk_seg - 1) * segment_length
    rk_end = rk_start + segment_length
    
    return rk_start <= jd < rk_end


# ══════════════════════════════════════════════════════════
# MERCURY RETROGRADE CHECK
# ══════════════════════════════════════════════════════════

def is_mercury_retrograde(jd):
    """
    Check if Mercury is retrograde at the given Julian Day.
    Retrograde = negative daily speed in longitude.
    
    Returns: True if retrograde
    """
    try:
        pos, _ = swe.calc_ut(jd, swe.MERCURY, swe.FLG_SPEED | swe.FLG_SWIEPH)
        return pos[3] < 0  # speed in longitude
    except:
        return False


# ══════════════════════════════════════════════════════════
# PLANETARY COMBUSTION CHECK
# ══════════════════════════════════════════════════════════

def compute_combustion(planet_lons, sun_lon):
    """
    Check which planets are combust (too close to Sun).
    
    Args:
        planet_lons: dict of {planet_name: sidereal_longitude}
        sun_lon: Sun's sidereal longitude
    
    Returns: (combust_count, combust_dict)
    """
    combust = {}
    count = 0
    for planet, threshold in COMBUST_THRESHOLD.items():
        plon = planet_lons.get(planet)
        if plon is None:
            continue
        sep = abs(plon - sun_lon) % 360
        sep = min(sep, 360 - sep)
        is_combust = sep <= threshold
        combust[planet] = is_combust
        if is_combust:
            count += 1
    return count, combust


# ══════════════════════════════════════════════════════════
# COMPOSITE PANCHANG SCORE
# ══════════════════════════════════════════════════════════

def compute_panchang_score(hora_score, tithi_score, vara_score,
                           nak_score, yoga_score, karana_score):
    """
    Composite Panchang quality score: sum of all 6 elements.
    Range: -18 to +18
    """
    return hora_score + tithi_score + vara_score + nak_score + yoga_score + karana_score


# ══════════════════════════════════════════════════════════
# MASTER EXTRACTION FUNCTION
# ══════════════════════════════════════════════════════════

def extract_panchang_features(jd, sun_sid_lon, moon_sid_lon, planet_lons,
                               lat=NYSE_LAT, lon=NYSE_LON):
    """
    Extract ALL Panchang + Hora features for a given moment.
    
    Args:
        jd: Julian Day of the moment
        sun_sid_lon: Sun's sidereal longitude
        moon_sid_lon: Moon's sidereal longitude
        planet_lons: dict of all planet sidereal longitudes
        lat, lon: location coordinates
    
    Returns: dict of feature_name → value
    """
    feats = {}
    
    # T25: Hora
    hora_planet, hora_num, hora_score = compute_hora(jd, lat, lon)
    feats['Hora_Score'] = hora_score
    for hp in ['Sun', 'Moon', 'Mars', 'Merc', 'Jup', 'Ven', 'Sat']:
        feats[f'Hora_{hp}'] = 1 if hora_planet == hp else 0
    
    # T26: Tithi
    tithi, paksha, tithi_score, is_ekadashi, is_danger = compute_tithi(sun_sid_lon, moon_sid_lon)
    feats['Tithi_Number'] = tithi
    feats['Tithi_Score'] = tithi_score
    feats['Tithi_Ekadashi'] = 1 if is_ekadashi else 0
    feats['Tithi_Danger'] = 1 if is_danger else 0
    feats['Paksha_Shukla'] = 1 if paksha == 'Shukla' else 0
    
    # T27: Vara
    weekday, vara_lord, vara_score = compute_vara(jd)
    feats['Vara_Score'] = vara_score
    feats['Vara_Thursday'] = 1 if weekday == 3 else 0
    feats['Vara_Saturday'] = 1 if weekday == 5 else 0
    
    # T28: Nakshatra (Panchang)
    nak_idx, nak_score = compute_nak_panchang_score(moon_sid_lon)
    feats['NakPanchang_Score'] = nak_score
    feats['NakPanchang_Best'] = 1 if nak_idx in NAK_PANCHANG_BEST else 0
    feats['NakPanchang_Bad'] = 1 if nak_idx in NAK_PANCHANG_BAD else 0
    feats['NakPanchang_Ganda'] = 1 if nak_idx in NAK_PANCHANG_GANDA else 0
    
    # T29: Yoga
    yoga_num, yoga_name, yoga_score, is_inausp, is_worst = compute_yoga(sun_sid_lon, moon_sid_lon)
    feats['Yoga_Number'] = yoga_num
    feats['Yoga_Score'] = yoga_score
    feats['Yoga_Inauspicious'] = 1 if is_inausp else 0
    feats['Yoga_Vyatipata'] = 1 if yoga_num == 17 else 0
    feats['Yoga_Vaidhriti'] = 1 if yoga_num == 27 else 0
    feats['Yoga_Excellent'] = 1 if yoga_num in YOGA_EXCELLENT else 0
    
    # T30: Karana
    karana_name, karana_score, is_vishti, is_vanija = compute_karana(tithi)
    feats['Karana_Score'] = karana_score
    feats['Karana_Vishti'] = 1 if is_vishti else 0
    feats['Karana_Vanija'] = 1 if is_vanija else 0
    
    # Rahu Kaal
    feats['RahuKaal_Active'] = 1 if is_rahu_kaal(jd, lat, lon) else 0
    
    # Mercury Retrograde
    feats['Mercury_Retrograde'] = 1 if is_mercury_retrograde(jd) else 0
    
    # Combustion
    combust_count, combust_dict = compute_combustion(planet_lons, sun_sid_lon)
    feats['Combust_Count'] = combust_count
    for pl, is_c in combust_dict.items():
        feats[f'Combust_{pl}'] = 1 if is_c else 0
    
    # Composite Panchang Score
    total = compute_panchang_score(hora_score, tithi_score, vara_score,
                                   nak_score, yoga_score, karana_score)
    feats['Panchang_Total'] = total
    feats['Panchang_Positive'] = 1 if total >= 6 else 0
    feats['Panchang_Negative'] = 1 if total <= -6 else 0
    
    # Store raw values for cross-reference
    feats['_hora_planet'] = hora_planet
    feats['_tithi'] = tithi
    feats['_paksha'] = paksha
    feats['_yoga_num'] = yoga_num
    feats['_karana'] = karana_name
    feats['_vara_lord'] = vara_lord
    
    return feats


def extract_natal_panchang(natal_lons, ipo_jd, lat=NYSE_LAT, lon=NYSE_LON):
    """
    Extract Panchang features at the stock's IPO moment.
    Called once per stock, cached as part of natal blueprint.
    
    Returns: dict prefixed with 'N_' for natal
    """
    swe.set_ephe_path(r'C:\Users\patel\Desktop\Python\Learn\sweph')
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    sun_lon = natal_lons.get('Sun', 0)
    moon_lon = natal_lons.get('Moon', 0)
    
    raw = extract_panchang_features(ipo_jd, sun_lon, moon_lon, natal_lons, lat, lon)
    
    # Prefix with N_ for natal
    natal_feats = {}
    for k, v in raw.items():
        if k.startswith('_'):
            natal_feats[k.replace('_', 'N__', 1)] = v  # internal keys
        else:
            natal_feats[f'N_{k}'] = v
    
    return natal_feats


def extract_panchang_crossref(natal_panchang, transit_panchang):
    """
    Cross-reference natal Panchang fingerprint with transit Panchang.
    The stock's birth Panchang quality is permanent; transit Panchang
    tells us WHEN that quality activates.
    
    Returns: dict of BP_ prefixed cross-reference features
    """
    cx = {}
    
    # Hora match: same Hora planet at birth and transit
    n_hora = natal_panchang.get('N___hora_planet', '')
    t_hora = transit_panchang.get('_hora_planet', '')
    cx['BP_Hora_Match'] = 1 if (n_hora == t_hora and n_hora) else 0
    
    # Paksha match
    n_paksha = natal_panchang.get('N___paksha', '')
    t_paksha = transit_panchang.get('_paksha', '')
    cx['BP_Paksha_Match'] = 1 if (n_paksha == t_paksha and n_paksha) else 0
    
    # Vara lord match
    n_vara = natal_panchang.get('N___vara_lord', '')
    t_vara = transit_panchang.get('_vara_lord', '')
    cx['BP_Vara_Match'] = 1 if (n_vara == t_vara and n_vara) else 0
    
    # Yoga both inauspicious
    n_yoga_bad = natal_panchang.get('N_Yoga_Inauspicious', 0)
    t_yoga_bad = transit_panchang.get('Yoga_Inauspicious', 0)
    cx['BP_Yoga_BothBad'] = 1 if (n_yoga_bad and t_yoga_bad) else 0
    
    # Yoga both excellent
    n_yoga_good = natal_panchang.get('N_Yoga_Excellent', 0)
    t_yoga_good = transit_panchang.get('Yoga_Excellent', 0)
    cx['BP_Yoga_BothGood'] = 1 if (n_yoga_good and t_yoga_good) else 0
    
    # Karana both Vishti
    n_vishti = natal_panchang.get('N_Karana_Vishti', 0)
    t_vishti = transit_panchang.get('Karana_Vishti', 0)
    cx['BP_Karana_BothVishti'] = 1 if (n_vishti and t_vishti) else 0
    
    # Karana both Vanija
    n_vanija = natal_panchang.get('N_Karana_Vanija', 0)
    t_vanija = transit_panchang.get('Karana_Vanija', 0)
    cx['BP_Karana_BothVanija'] = 1 if (n_vanija and t_vanija) else 0
    
    # Tithi both Ekadashi
    n_ek = natal_panchang.get('N_Tithi_Ekadashi', 0)
    t_ek = transit_panchang.get('Tithi_Ekadashi', 0)
    cx['BP_Tithi_BothEkadashi'] = 1 if (n_ek and t_ek) else 0
    
    # Tithi both danger
    n_danger = natal_panchang.get('N_Tithi_Danger', 0)
    t_danger = transit_panchang.get('Tithi_Danger', 0)
    cx['BP_Tithi_BothDanger'] = 1 if (n_danger and t_danger) else 0
    
    # Composite Panchang both high (≥+6) or both low (≤-6)
    n_total = natal_panchang.get('N_Panchang_Total', 0)
    t_total = transit_panchang.get('Panchang_Total', 0)
    cx['BP_Panchang_BothHigh'] = 1 if (n_total >= 6 and t_total >= 6) else 0
    cx['BP_Panchang_BothLow'] = 1 if (n_total <= -6 and t_total <= -6) else 0
    cx['BP_Panchang_NatalHigh_TransitLow'] = 1 if (n_total >= 6 and t_total <= -3) else 0
    cx['BP_Panchang_NatalLow_TransitHigh'] = 1 if (n_total <= -6 and t_total >= 3) else 0
    
    # Hora score difference
    n_hora_score = natal_panchang.get('N_Hora_Score', 0)
    t_hora_score = transit_panchang.get('Hora_Score', 0)
    cx['BP_Hora_BothBullish'] = 1 if (n_hora_score >= 2 and t_hora_score >= 2) else 0
    cx['BP_Hora_BothBearish'] = 1 if (n_hora_score <= -1 and t_hora_score <= -1) else 0
    
    return cx
