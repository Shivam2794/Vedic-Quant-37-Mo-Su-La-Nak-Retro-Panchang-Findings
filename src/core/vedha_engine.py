"""
Vedha + Ashtakavarga Engine — Complete Classical Vedic Transit System
=====================================================================
Implements:
  1. Ashtakavarga BAV (7×12 matrix per natal chart) using full contribution tables
  2. SAV (Sarva Ashtakavarga) per house + structural financial ratios
  3. Vedha obstruction analysis with Sun-Saturn / Moon-Mercury exemptions
  4. Vipreet Vedha (reverse protection)
  5. Gochar Murti (Golden/Silver/Copper/Iron transit quality)
  6. Combined BAV × Vedha signal matrix → composite score
  7. C.S. Patel financial thumb rules

References: Brihat Parasara Hora Shastra, Phaladeepika, K.N. Rao, C.S. Patel
Only 9 classical planets. Rahu/Ketu in Vedha, excluded from Ashtakavarga.
"""

# ═══════════════════════════════════════════════════════════════
# SECTION 1: ASHTAKAVARGA — FULL BAV CONTRIBUTION MATRIX
# ═══════════════════════════════════════════════════════════════
# Key: For planet P, from each contributor C, which houses (from C's natal
# position) give a Bindu (1 point) to P. Exactly per BPHS Chapter 66-72.
# Total bindus across all 7 planets = 337 always.

# Contributors: Sun=0, Moon=1, Mars=2, Merc=3, Jup=4, Ven=5, Sat=6, Lagna=7
# Houses are 1-indexed. We store as sets for fast lookup.

BAV_RULES = {
    'Sun': {  # Total: 48
        0: {1,2,4,7,8,9,10,11},      # From Sun
        1: {3,6,10,11},              # From Moon
        2: {1,2,4,7,8,9,10,11},      # From Mars
        3: {3,5,6,9,10,11,12},       # From Mercury
        4: {5,6,9,11},              # From Jupiter
        5: {6,7,12},                # From Venus
        6: {1,2,4,7,8,9,10,11},      # From Saturn
        7: {3,4,6,10,11,12},        # From Lagna
    },
    'Moon': {  # Total: 49
        0: {3,6,7,8,10,11},          # From Sun
        1: {1,3,6,7,10,11},          # From Moon
        2: {2,3,5,6,9,10,11},        # From Mars
        3: {1,3,4,5,7,8,10,11},      # From Mercury
        4: {1,4,7,8,10,11,12},       # From Jupiter
        5: {3,4,5,7,9,10,11},        # From Venus
        6: {3,5,6,11},              # From Saturn
        7: {3,6,10,11},             # From Lagna
    },
    'Mars': {  # Total: 38
        0: {3,5,6,10,11},            # From Sun
        1: {3,6,11},                # From Moon
        2: {1,2,4,7,8,10,11},        # From Mars
        3: {3,5,6,11},              # From Mercury
        4: {6,10,11,12},            # From Jupiter
        5: {6,8,11,12},             # From Venus
        6: {1,4,7,8,9,10,11},        # From Saturn
        7: {1,3,6,10,11},           # From Lagna
    },
    'Merc': {  # Total: 54
        0: {5,6,9,11,12},            # From Sun
        1: {2,4,6,8,10,11},          # From Moon
        2: {1,2,4,7,8,9,10,11},      # From Mars
        3: {1,3,5,6,9,10,11,12},     # From Mercury
        4: {6,8,11,12},             # From Jupiter
        5: {1,2,3,4,5,8,9,11},       # From Venus
        6: {1,2,4,7,8,9,10,11},      # From Saturn
        7: {1,2,4,6,8,10,11},       # From Lagna
    },
    'Jup': {  # Total: 56 — highest (great benefic)
        0: {1,2,3,4,7,8,9,10,11},    # From Sun
        1: {2,5,7,9,11},            # From Moon
        2: {1,2,4,7,8,10,11},        # From Mars
        3: {1,2,4,5,6,9,10,11},      # From Mercury
        4: {1,2,3,4,7,8,10,11},      # From Jupiter
        5: {2,5,6,9,10,11},          # From Venus
        6: {3,5,6,12},              # From Saturn
        7: {1,2,4,5,6,7,9,10,11},    # From Lagna
    },
    'Ven': {  # Total: 52
        0: {8,11,12},                # From Sun
        1: {1,2,3,4,5,8,9,11,12},    # From Moon
        2: {3,5,6,9,11,12},          # From Mars
        3: {3,5,6,9,11},            # From Mercury
        4: {5,8,9,10,11},           # From Jupiter
        5: {1,2,3,4,5,8,9,10,11},    # From Venus
        6: {3,4,5,8,9,10,11},        # From Saturn
        7: {1,2,3,4,5,8,9,11},      # From Lagna
    },
    'Sat': {  # Total: 38
        0: {1,2,4,7,8,10,11},        # From Sun
        1: {3,6,11},                # From Moon
        2: {3,5,6,10,11,12},         # From Mars
        3: {6,8,9,10,11,12},         # From Mercury
        4: {5,6,11,12},             # From Jupiter
        5: {6,11,12},               # From Venus
        6: {3,5,6,11},              # From Saturn
        7: {1,3,4,6,10,11},         # From Lagna
    },
}

# Expected totals for validation (verified by summing all entries in BAV_RULES)
BAV_TOTALS = {'Sun':48,'Moon':49,'Mars':39,'Merc':54,'Jup':56,'Ven':52,'Sat':39}

# Planet name → index for contributor lookup
PLANET_IDX = {'Sun':0,'Moon':1,'Mars':2,'Merc':3,'Jup':4,'Ven':5,'Sat':6}
PLANET_NAMES = ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']

SIGNS_12 = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
            "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]


def compute_bav(natal_sign_indices, lagna_sign_idx):
    """
    Compute full BAV matrix (7 planets × 12 signs).

    Args:
        natal_sign_indices: dict mapping planet name → sign index (0=Aries..11=Pisces)
                           Keys: Sun, Moon, Mars, Merc, Jup, Ven, Sat
        lagna_sign_idx: int 0-11, index of the Ascendant sign

    Returns:
        bav: dict of {planet_name: [12 ints]} where each int is BAV 0-8 for that sign
    """
    bav = {}
    # Contributor positions: index 0-6 = planet, 7 = Lagna
    contributor_signs = [natal_sign_indices.get(p, 0) for p in PLANET_NAMES]
    contributor_signs.append(lagna_sign_idx)  # index 7 = Lagna

    for planet in PLANET_NAMES:
        scores = [0] * 12
        rules = BAV_RULES[planet]

        for contrib_idx in range(8):  # 7 planets + Lagna
            contrib_sign = contributor_signs[contrib_idx]
            benefic_houses = rules.get(contrib_idx, set())

            for house_num in benefic_houses:
                # House N from contributor's sign → sign index
                target_sign = (contrib_sign + house_num - 1) % 12
                scores[target_sign] += 1

        bav[planet] = scores

    return bav


def validate_bav(bav):
    """Validate BAV totals match expected constants. Returns True if valid."""
    for planet in PLANET_NAMES:
        total = sum(bav[planet])
        expected = BAV_TOTALS[planet]
        if total != expected:
            return False
    grand = sum(sum(bav[p]) for p in PLANET_NAMES)
    return grand == 337


def compute_sav(bav):
    """Compute SAV (Sarva Ashtakavarga): sum all 7 planets' BAV per sign. Returns list of 12."""
    sav = [0] * 12
    for planet in PLANET_NAMES:
        for i in range(12):
            sav[i] += bav[planet][i]
    return sav


def sav_structural_ratios(sav, lagna_sign_idx):
    """
    Compute C.S. Patel style structural ratios from SAV.

    Returns dict of named ratios mapped to houses relative to Lagna.
    """
    # Map SAV from sign-based to house-based (house 1 = lagna sign)
    sav_house = [sav[(lagna_sign_idx + h) % 12] for h in range(12)]

    h2 = sav_house[1]; h5 = sav_house[4]; h6 = sav_house[5]
    h8 = sav_house[7]; h9 = sav_house[8]; h10 = sav_house[9]
    h11 = sav_house[10]; h12 = sav_house[11]; h1 = sav_house[0]; h4 = sav_house[3]

    ratios = {
        'profit_check': 1 if h11 > h12 else 0,       # income > expenses
        'effort_gain': 1 if h11 > h10 else 0,         # gains > effort
        'wealth_formula': h1+h2+h4+h9+h10+h11,        # >164 = bullish
        'wealth_bullish': 1 if (h1+h2+h4+h9+h10+h11) > 164 else 0,
        'loss_formula': h6+h8+h12,                    # <76 = bullish
        'loss_bullish': 1 if (h6+h8+h12) < 76 else 0,
        'crisis_risk': 1 if h8 > 35 else 0,           # 8th house high = risky
        'speculation': 1 if h5 > 32 else 0,            # 5th house high = volatile
        'sav_11th': h11,
        'sav_12th': h12,
        'sav_house': sav_house,
    }
    return ratios


# ═══════════════════════════════════════════════════════════════
# SECTION 2: VEDHA SYSTEM
# ═══════════════════════════════════════════════════════════════
# Vedha table: for each planet, list of (benefic_house, vedha_sthana) pairs.
# Houses numbered 1-12 from natal Moon.

VEDHA_TABLE = {
    'Sun':  [(3,9), (6,12), (10,4), (11,5)],
    'Moon': [(1,5), (3,9), (6,12), (7,2), (10,4), (11,8)],
    'Mars': [(3,12), (6,9), (11,5)],
    'Merc': [(2,5), (4,3), (6,9), (8,1), (10,8), (11,12)],
    'Jup':  [(2,12), (5,4), (7,3), (9,10), (11,8)],
    'Ven':  [(1,8), (2,7), (3,1), (4,10), (5,9), (8,5), (9,11), (11,6), (12,3)],
    'Sat':  [(3,12), (6,9), (11,5)],
    'Rahu': [(3,12), (6,9), (11,5)],
    'Ketu': [(3,12), (6,9), (11,5)],
}

# Exemption pairs: these never cause Vedha to each other
VEDHA_EXEMPT = {
    frozenset({'Sun','Sat'}),
    frozenset({'Moon','Merc'}),
}


def _get_benefic_houses(planet):
    """Return set of benefic house numbers for a planet."""
    return {pair[0] for pair in VEDHA_TABLE.get(planet, [])}


def _get_vedha_sthana(planet, benefic_house):
    """Return the vedha sthana (blocking house) for a given planet's benefic house."""
    for bh, vs in VEDHA_TABLE.get(planet, []):
        if bh == benefic_house:
            return vs
    return None


def vedha_analysis(transit_houses, planet_list=None):
    """
    Full Vedha analysis for all 9 transiting planets.

    Args:
        transit_houses: dict {planet_name: house_from_moon (1-12)}
        planet_list: optional list of planet names to analyze (default: all 9)

    Returns:
        dict {planet_name: {
            'house': int,
            'is_benefic': bool,
            'vedha_blocked': bool,
            'vedha_blocker': str or None,
            'vipreet_vedha': bool,
            'vipreet_protector': str or None,
            'status': 'BENEFIC_ACTIVE' | 'BENEFIC_BLOCKED' | 'MALEFIC_ACTIVE' |
                      'MALEFIC_PROTECTED' | 'NEUTRAL'
        }}
    """
    if planet_list is None:
        planet_list = ['Sun','Moon','Mars','Merc','Jup','Ven','Sat','Rahu','Ketu']

    # Build reverse map: house → list of planets in that house
    house_occupants = {}
    for pname, h in transit_houses.items():
        house_occupants.setdefault(h, []).append(pname)

    results = {}

    for planet in planet_list:
        if planet not in transit_houses:
            continue

        h = transit_houses[planet]
        benefic_houses = _get_benefic_houses(planet)
        is_benefic = h in benefic_houses

        vedha_blocked = False
        vedha_blocker = None
        vipreet = False
        vipreet_protector = None

        if is_benefic:
            # Check if vedha sthana is occupied by non-exempt planet
            vs = _get_vedha_sthana(planet, h)
            if vs is not None and vs in house_occupants:
                for occ in house_occupants[vs]:
                    if occ == planet:
                        continue
                    # Check exemption
                    if frozenset({planet, occ}) in VEDHA_EXEMPT:
                        continue
                    vedha_blocked = True
                    vedha_blocker = occ
                    break

            status = 'BENEFIC_BLOCKED' if vedha_blocked else 'BENEFIC_ACTIVE'

        else:
            # Planet in non-benefic (malefic/neutral) house
            # Check Vipreet Vedha: is this house a vedha sthana, and is its specific benefic house occupied?
            for bh, vs in VEDHA_TABLE.get(planet, []):
                if vs == h:  # Only if the planet is in the specific vedha sthana
                    if bh in house_occupants:
                        for occ in house_occupants[bh]:
                            if occ != planet:
                                # Check exemption for reverse vedha as well
                                if frozenset({planet, occ}) not in VEDHA_EXEMPT:
                                    vipreet = True
                                    vipreet_protector = occ
                                    break
                if vipreet:
                    break

            status = 'MALEFIC_PROTECTED' if vipreet else 'MALEFIC_ACTIVE'

            # If house is not in benefic or malefic, classify as neutral
            # (houses not listed in table are neutral)
            all_listed = benefic_houses | {pair[1] for pair in VEDHA_TABLE.get(planet, [])}
            if h not in all_listed and not vipreet:
                status = 'NEUTRAL'

        results[planet] = {
            'house': h,
            'is_benefic': is_benefic,
            'vedha_blocked': vedha_blocked,
            'vedha_blocker': vedha_blocker,
            'vipreet_vedha': vipreet,
            'vipreet_protector': vipreet_protector,
            'status': status,
        }

    return results


# ═══════════════════════════════════════════════════════════════
# SECTION 3: GOCHAR MURTI
# ═══════════════════════════════════════════════════════════════

MURTI_GOLDEN = {1, 6, 11}    # Maximum delivery
MURTI_SILVER = {3, 7, 10}    # Strong
MURTI_COPPER = {2, 5, 9}     # Mixed/partial
MURTI_IRON   = {4, 8, 12}    # Weak/harmful

def gochar_murti(transit_moon_house_from_natal):
    """
    Determine Gochar Murti quality.

    Args:
        transit_moon_house_from_natal: house 1-12 of transiting Moon from natal Moon

    Returns:
        (name, multiplier) tuple
    """
    h = transit_moon_house_from_natal
    if h in MURTI_GOLDEN:
        return ('Golden', 1.0)
    elif h in MURTI_SILVER:
        return ('Silver', 0.75)
    elif h in MURTI_COPPER:
        return ('Copper', 0.5)
    elif h in MURTI_IRON:
        return ('Iron', 0.25)
    return ('Unknown', 0.5)


# ═══════════════════════════════════════════════════════════════
# SECTION 4: COMBINED BAV × VEDHA SIGNAL MATRIX
# ═══════════════════════════════════════════════════════════════

def combined_signal(bav_score, vedha_status, murti_name):
    """
    Compute combined signal from BAV score, Vedha status, and Gochar Murti.

    Returns:
        (score, label) where score is float in [-2, +2]
    """
    # BAV override: 0-2 is always negative regardless of Vedha
    if bav_score <= 2:
        if vedha_status == 'BENEFIC_BLOCKED' or vedha_status == 'MALEFIC_ACTIVE':
            if murti_name == 'Iron':
                return (-2.0, 'CRISIS_SIGNAL')
            return (-1.5, 'DOUBLE_NEGATIVE')
        return (-1.0, 'WEAK_NEGATIVE')

    if vedha_status == 'BENEFIC_ACTIVE':
        if bav_score >= 6:
            if murti_name == 'Golden':
                return (2.0, 'PEAK_BULLISH')
            elif murti_name == 'Silver':
                return (1.5, 'STRONG_POSITIVE')
            return (1.0, 'STRONG_POSITIVE')
        elif bav_score >= 4:
            return (0.5, 'MODERATE_POSITIVE')
        return (0.25, 'MILD_POSITIVE')

    elif vedha_status == 'BENEFIC_BLOCKED':
        if bav_score >= 6:
            return (-0.25, 'BLOCKED_WASTED')  # Good potential wasted
        return (-0.5, 'SUPPRESSED')

    elif vedha_status == 'MALEFIC_PROTECTED':
        return (0.5, 'VIPREET_PROTECTED')

    elif vedha_status == 'MALEFIC_ACTIVE':
        if bav_score <= 3:
            return (-1.5, 'STRONG_NEGATIVE')
        return (-1.0, 'NEGATIVE')

    # Neutral
    return (0.0, 'NEUTRAL')


# ═══════════════════════════════════════════════════════════════
# SECTION 5: COMPOSITE SCORING ENGINE
# ═══════════════════════════════════════════════════════════════

def compute_composite_score(bav, sav, natal_moon_sign_idx, lagna_sign_idx,
                            transit_sign_indices, transit_moon_sign_idx):
    """
    Full composite Vedha + Ashtakavarga scoring for one transit moment.

    Args:
        bav: dict {planet: [12 BAV scores]} from compute_bav()
        sav: list of 12 SAV scores from compute_sav()
        natal_moon_sign_idx: int 0-11
        lagna_sign_idx: int 0-11
        transit_sign_indices: dict {planet_name: sign_index_0_11}
                             Must include Sun,Moon,Mars,Merc,Jup,Ven,Sat,Rahu,Ketu
        transit_moon_sign_idx: int 0-11 (transiting Moon's sign)

    Returns:
        dict with composite score, per-planet breakdown, special flags
    """
    # 1. Compute houses from natal Moon for each transiting planet
    transit_houses = {}
    for pname, sidx in transit_sign_indices.items():
        house = ((sidx - natal_moon_sign_idx) % 12) + 1
        transit_houses[pname] = house

    # 2. Gochar Murti from transiting Moon
    moon_house = transit_houses.get('Moon', 1)
    murti_name, murti_mult = gochar_murti(moon_house)

    # 3. Vedha analysis
    vedha_results = vedha_analysis(transit_houses)

    # 4. Per-planet combined signal
    planet_signals = {}
    raw_score = 0.0
    bav_daily_sum = 0
    bav_daily_weighted = 0

    for pname in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat','Rahu','Ketu']:
        sidx = transit_sign_indices.get(pname)
        if sidx is None:
            continue

        # BAV score: only for 7 planets (not Rahu/Ketu)
        if pname in bav:
            b_score = bav[pname][sidx]
            bav_daily_sum += b_score
            weight = 2 if pname in ('Jup','Sat') else 1
            bav_daily_weighted += b_score * weight
        else:
            # Rahu/Ketu: use average BAV of the sign from SAV
            b_score = sav[sidx] // 7 if sidx is not None else 4

        # Vedha status
        v_result = vedha_results.get(pname, {})
        v_status = v_result.get('status', 'NEUTRAL')

        # Combined signal
        sig_score, sig_label = combined_signal(b_score, v_status, murti_name)
        raw_score += sig_score

        planet_signals[pname] = {
            'transit_sign': sidx,
            'house_from_moon': transit_houses.get(pname, 0),
            'bav_score': b_score,
            'vedha_status': v_status,
            'vedha_blocker': v_result.get('vedha_blocker'),
            'vipreet': v_result.get('vipreet_vedha', False),
            'murti': murti_name,
            'signal_score': sig_score,
            'signal_label': sig_label,
        }

    # 5. Normalize to -5 to +5 scale
    # Max possible: 9 planets × 2.0 = 18. Min: 9 × -2.0 = -18
    normalized = max(-5.0, min(5.0, raw_score * 5.0 / 18.0))

    # 6. Special flags
    benefic_active = sum(1 for p in planet_signals.values() if 'POSITIVE' in p['signal_label'] or p['signal_label'] == 'PEAK_BULLISH')
    blocked_count = sum(1 for p in planet_signals.values() if p['signal_label'] in ('BLOCKED_WASTED','SUPPRESSED'))
    malefic_active = sum(1 for p in planet_signals.values() if 'NEGATIVE' in p['signal_label'] or p['signal_label'] == 'CRISIS_SIGNAL')
    vipreet_count = sum(1 for p in planet_signals.values() if p['vipreet'])
    peak_bullish = sum(1 for p in planet_signals.values() if p['signal_label'] == 'PEAK_BULLISH')
    crisis_count = sum(1 for p in planet_signals.values() if p['signal_label'] == 'CRISIS_SIGNAL')

    # Sade Sati: Saturn within 1 sign of natal Moon
    sat_sidx = transit_sign_indices.get('Sat')
    sade_sati = False
    if sat_sidx is not None:
        diff = abs(sat_sidx - natal_moon_sign_idx)
        if diff > 6: diff = 12 - diff
        sade_sati = diff <= 1

    # Rahu on Moon
    rahu_sidx = transit_sign_indices.get('Rahu')
    rahu_on_moon = (rahu_sidx == natal_moon_sign_idx) if rahu_sidx is not None else False

    # Jupiter clean benefic (in benefic house, no Vedha, BAV ≥ 5)
    jup_sig = planet_signals.get('Jup', {})
    jup_clean = (jup_sig.get('signal_label','') in ('STRONG_POSITIVE','PEAK_BULLISH','MODERATE_POSITIVE'))

    # Saturn pressure (in 8th or 12th from Moon)
    sat_house = transit_houses.get('Sat', 0)
    sat_pressure = sat_house in (8, 12)

    # SAV structural ratios
    sav_ratios = sav_structural_ratios(sav, lagna_sign_idx)

    return {
        'composite_score': round(normalized, 3),
        'raw_score': round(raw_score, 3),
        'murti_name': murti_name,
        'murti_mult': murti_mult,
        'benefic_active': benefic_active,
        'blocked_count': blocked_count,
        'malefic_active': malefic_active,
        'vipreet_count': vipreet_count,
        'peak_bullish': peak_bullish,
        'crisis_count': crisis_count,
        'bav_daily_sum': bav_daily_sum,
        'bav_daily_weighted': bav_daily_weighted,
        'sade_sati': sade_sati,
        'rahu_on_moon': rahu_on_moon,
        'jup_clean': jup_clean,
        'sat_pressure': sat_pressure,
        'sav_profit_check': sav_ratios['profit_check'],
        'sav_wealth_bullish': sav_ratios['wealth_bullish'],
        'sav_loss_bullish': sav_ratios['loss_bullish'],
        'sav_crisis_risk': sav_ratios['crisis_risk'],
        'sav_11th': sav_ratios['sav_11th'],
        'sav_12th': sav_ratios['sav_12th'],
        'planet_signals': planet_signals,
    }


# ═══════════════════════════════════════════════════════════════
# SECTION 6: FEATURE EXTRACTION FOR BACKTESTING
# ═══════════════════════════════════════════════════════════════

def extract_vedha_features(composite):
    """
    Convert composite scoring output to flat feature dict for backtesting.

    Args:
        composite: dict from compute_composite_score()

    Returns:
        dict of feature_name → value
    """
    f = {}

    # Core composite
    f['Vedha_Composite'] = composite['composite_score']
    f['Vedha_RawScore'] = composite['raw_score']

    # Murti encoding
    murti_map = {'Golden': 4, 'Silver': 3, 'Copper': 2, 'Iron': 1, 'Unknown': 2}
    f['Vedha_Murti'] = murti_map.get(composite['murti_name'], 2)
    f['Vedha_MurtiGolden'] = 1 if composite['murti_name'] == 'Golden' else 0
    f['Vedha_MurtiIron'] = 1 if composite['murti_name'] == 'Iron' else 0

    # Counts
    f['Vedha_BeneficActive'] = composite['benefic_active']
    f['Vedha_Blocked'] = composite['blocked_count']
    f['Vedha_MaleficActive'] = composite['malefic_active']
    f['Vedha_Vipreet'] = composite['vipreet_count']
    f['Vedha_PeakBull'] = composite['peak_bullish']
    f['Vedha_Crisis'] = composite['crisis_count']

    # BAV aggregates
    f['BAV_DailySum'] = composite['bav_daily_sum']
    f['BAV_DailyWeighted'] = composite['bav_daily_weighted']
    f['BAV_DailySumGood'] = 1 if composite['bav_daily_sum'] >= 30 else 0
    f['BAV_DailySumBad'] = 1 if composite['bav_daily_sum'] < 25 else 0
    f['BAV_DailySumExcellent'] = 1 if composite['bav_daily_sum'] >= 35 else 0

    # SAV structural
    f['SAV_ProfitCheck'] = composite['sav_profit_check']
    f['SAV_WealthBullish'] = composite['sav_wealth_bullish']
    f['SAV_LossBullish'] = composite['sav_loss_bullish']
    f['SAV_CrisisRisk'] = composite['sav_crisis_risk']
    f['SAV_11th'] = composite['sav_11th']
    f['SAV_12th'] = composite['sav_12th']
    f['SAV_11_minus_12'] = composite['sav_11th'] - composite['sav_12th']

    # Special conditions
    f['Vedha_SadeSati'] = 1 if composite['sade_sati'] else 0
    f['Vedha_RahuOnMoon'] = 1 if composite['rahu_on_moon'] else 0
    f['Vedha_JupClean'] = 1 if composite['jup_clean'] else 0
    f['Vedha_SatPressure'] = 1 if composite['sat_pressure'] else 0

    # Net signal
    f['Vedha_NetSignal'] = composite['benefic_active'] - composite['malefic_active']

    # Per-planet BAV in transit sign (for key planets)
    for pname in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']:
        psig = composite['planet_signals'].get(pname, {})
        f[f'BAV_{pname}'] = psig.get('bav_score', 4)

    # Per-planet benefic/blocked status (binary)
    for pname in ['Jup','Sat','Ven','Mars']:
        psig = composite['planet_signals'].get(pname, {})
        label = psig.get('signal_label', 'NEUTRAL')
        f[f'Vedha_{pname}_Positive'] = 1 if 'POSITIVE' in label or label == 'PEAK_BULLISH' else 0
        f[f'Vedha_{pname}_Negative'] = 1 if 'NEGATIVE' in label or label == 'CRISIS_SIGNAL' else 0
        f[f'Vedha_{pname}_Blocked'] = 1 if 'BLOCKED' in label or 'SUPPRESSED' in label else 0

    return f


# ═══════════════════════════════════════════════════════════════
# SECTION 7: NATAL VEDHA ANALYSIS (D1 + D9)
# ═══════════════════════════════════════════════════════════════

def compute_natal_vedha(natal_sign_indices, natal_moon_sign_idx,
                        d9_sign_indices=None, d9_moon_sign_idx=None):
    """
    Compute Vedha status for planets in the NATAL chart itself (D1 and D9).
    This identifies which planets have obstructed vs clean benefic positions
    at birth — the natal promise layer.

    Args:
        natal_sign_indices: dict {planet: sign_idx 0-11} for D1
        natal_moon_sign_idx: int 0-11 (D1 Moon sign)
        d9_sign_indices: optional dict for D9 chart
        d9_moon_sign_idx: optional int for D9 Moon sign

    Returns:
        dict with:
            'd1_vedha': vedha_analysis results for D1
            'd9_vedha': vedha_analysis results for D9 (if provided)
            'd1_clean': set of planet names with clean benefic in D1
            'd1_blocked': set of planet names with blocked benefic in D1
            'd1_malefic': set of planet names in malefic position in D1
            (same for D9)
    """
    # D1 natal Vedha: compute house positions from natal Moon for all natal planets
    d1_houses = {}
    for pname, sidx in natal_sign_indices.items():
        if pname.startswith('_'):
            continue
        house = ((sidx - natal_moon_sign_idx) % 12) + 1
        d1_houses[pname] = house

    # Add Ketu if Rahu present
    if 'Rahu' in natal_sign_indices and 'Ketu' not in d1_houses:
        ketu_sidx = (natal_sign_indices['Rahu'] + 6) % 12
        d1_houses['Ketu'] = ((ketu_sidx - natal_moon_sign_idx) % 12) + 1

    d1_vedha = vedha_analysis(d1_houses)

    d1_clean = set()
    d1_blocked = set()
    d1_malefic = set()
    d1_protected = set()

    for pname, result in d1_vedha.items():
        status = result['status']
        if status == 'BENEFIC_ACTIVE':
            d1_clean.add(pname)
        elif status == 'BENEFIC_BLOCKED':
            d1_blocked.add(pname)
        elif status == 'MALEFIC_ACTIVE':
            d1_malefic.add(pname)
        elif status == 'MALEFIC_PROTECTED':
            d1_protected.add(pname)

    result = {
        'd1_vedha': d1_vedha,
        'd1_clean': d1_clean,
        'd1_blocked': d1_blocked,
        'd1_malefic': d1_malefic,
        'd1_protected': d1_protected,
        'd1_clean_count': len(d1_clean),
        'd1_blocked_count': len(d1_blocked),
        'd1_malefic_count': len(d1_malefic),
    }

    # D9 Vedha (if D9 positions provided)
    if d9_sign_indices and d9_moon_sign_idx is not None:
        d9_houses = {}
        for pname, sidx in d9_sign_indices.items():
            if pname.startswith('_'):
                continue
            house = ((sidx - d9_moon_sign_idx) % 12) + 1
            d9_houses[pname] = house

        if 'Rahu' in d9_sign_indices and 'Ketu' not in d9_houses:
            ketu_sidx = (d9_sign_indices['Rahu'] + 6) % 12
            d9_houses['Ketu'] = ((ketu_sidx - d9_moon_sign_idx) % 12) + 1

        d9_vedha = vedha_analysis(d9_houses)

        d9_clean = set()
        d9_blocked = set()
        d9_malefic = set()

        for pname, res in d9_vedha.items():
            status = res['status']
            if status == 'BENEFIC_ACTIVE':
                d9_clean.add(pname)
            elif status == 'BENEFIC_BLOCKED':
                d9_blocked.add(pname)
            elif status == 'MALEFIC_ACTIVE':
                d9_malefic.add(pname)

        result.update({
            'd9_vedha': d9_vedha,
            'd9_clean': d9_clean,
            'd9_blocked': d9_blocked,
            'd9_malefic': d9_malefic,
            'd9_clean_count': len(d9_clean),
            'd9_blocked_count': len(d9_blocked),
        })

    return result


def extract_natal_transit_cross_features(natal_vedha, transit_composite):
    """
    Cross-reference natal Vedha status × transit Vedha status per planet.

    Creates 4 interactions per planet:
    - Double Clean: natal clean + transit positive → strongest signal
    - Wasted Promise: natal clean + transit blocked → frustrated potential
    - Activation Despite Weakness: natal blocked/malefic + transit positive
    - Double Block: natal blocked/malefic + transit blocked/negative → worst

    Also creates aggregate counts and D1/D9 combined features.

    Args:
        natal_vedha: dict from compute_natal_vedha()
        transit_composite: dict from compute_composite_score()

    Returns:
        dict of feature_name → value
    """
    f = {}

    d1_clean = natal_vedha.get('d1_clean', set())
    d1_blocked = natal_vedha.get('d1_blocked', set())
    d1_malefic = natal_vedha.get('d1_malefic', set())
    d1_protected = natal_vedha.get('d1_protected', set())
    d9_clean = natal_vedha.get('d9_clean', set())
    d9_blocked = natal_vedha.get('d9_blocked', set())
    d9_malefic = natal_vedha.get('d9_malefic', set())

    planet_signals = transit_composite.get('planet_signals', {})

    # Natal D1/D9 structural features
    f['NatalV_D1_CleanCount'] = natal_vedha.get('d1_clean_count', 0)
    f['NatalV_D1_BlockedCount'] = natal_vedha.get('d1_blocked_count', 0)
    f['NatalV_D1_MaleficCount'] = natal_vedha.get('d1_malefic_count', 0)
    f['NatalV_D9_CleanCount'] = natal_vedha.get('d9_clean_count', 0)
    f['NatalV_D9_BlockedCount'] = natal_vedha.get('d9_blocked_count', 0)

    # D1+D9 combined: planet clean in BOTH D1 and D9
    both_clean = d1_clean & d9_clean if d9_clean else set()
    both_blocked = (d1_blocked | d1_malefic) & (d9_blocked | d9_malefic) if d9_blocked or d9_malefic else set()
    f['NatalV_BothClean'] = len(both_clean)
    f['NatalV_BothBlocked'] = len(both_blocked)

    # Cross-reference: per-planet natal×transit interaction
    double_clean = 0
    wasted_promise = 0
    activation = 0
    double_block = 0

    for pname in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat','Rahu','Ketu']:
        psig = planet_signals.get(pname, {})
        transit_label = psig.get('signal_label', 'NEUTRAL')

        # Classify transit status
        transit_positive = ('POSITIVE' in transit_label or transit_label == 'PEAK_BULLISH')
        transit_blocked = ('BLOCKED' in transit_label or 'SUPPRESSED' in transit_label)
        transit_negative = ('NEGATIVE' in transit_label or transit_label == 'CRISIS_SIGNAL')

        # Natal status
        natal_clean = pname in d1_clean
        natal_bad = pname in d1_blocked or pname in d1_malefic

        # 4 interaction states
        if natal_clean and transit_positive:
            double_clean += 1
        elif natal_clean and (transit_blocked or transit_negative):
            wasted_promise += 1
        elif natal_bad and transit_positive:
            activation += 1
        elif natal_bad and (transit_blocked or transit_negative):
            double_block += 1

        # Per key-planet cross features
        if pname in ('Jup', 'Sat', 'Mars', 'Ven'):
            f[f'NX_{pname}_DoubleClean'] = 1 if (natal_clean and transit_positive) else 0
            f[f'NX_{pname}_WastedPromise'] = 1 if (natal_clean and (transit_blocked or transit_negative)) else 0
            f[f'NX_{pname}_Activation'] = 1 if (natal_bad and transit_positive) else 0
            f[f'NX_{pname}_DoubleBlock'] = 1 if (natal_bad and (transit_blocked or transit_negative)) else 0

            # D9 layer: if planet clean in D9 + transit positive = D9 confirmed
            if d9_clean:
                d9_c = pname in d9_clean
                f[f'NX_{pname}_D9DoubleClean'] = 1 if (d9_c and transit_positive) else 0
                f[f'NX_{pname}_D9Wasted'] = 1 if (d9_c and (transit_blocked or transit_negative)) else 0

    # Aggregate counts
    f['NX_DoubleClean_Count'] = double_clean
    f['NX_WastedPromise_Count'] = wasted_promise
    f['NX_Activation_Count'] = activation
    f['NX_DoubleBlock_Count'] = double_block
    f['NX_NetQuality'] = double_clean - double_block

    # Ratio features
    total_active = double_clean + wasted_promise + activation + double_block
    if total_active > 0:
        f['NX_CleanRatio'] = round(double_clean / total_active, 3)
        f['NX_BlockRatio'] = round(double_block / total_active, 3)
    else:
        f['NX_CleanRatio'] = 0.5
        f['NX_BlockRatio'] = 0.5

    return f
