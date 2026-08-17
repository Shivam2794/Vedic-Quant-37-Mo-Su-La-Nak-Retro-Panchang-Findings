"""
Institution-Level Backtesting: Analysis Phases 4-8 (v3)
=========================================================
EPOCH-BIAS CORRECTED + VEDHA/ASHTAKAVARGA (Topic #23):
- Slow planets epoch-detrended
- Fast×slow interaction features
- Full Vedha obstruction analysis + Ashtakavarga BAV/SAV
- Combined BAV×Vedha signal matrix
- C.S. Patel financial thumb rules
"""
import numpy as np
import pandas as pd
import datetime, os, pickle, json, warnings
from collections import Counter, defaultdict
warnings.filterwarnings("ignore")

from institution_backtest import (
    CACHE_DIR, REPORT_PATH, SIGNS, NAKS, PL, MOVING, WATER, POS_SIGNS,
    WEALTH_H, LOSS_H, NEG_NAKS, PRACPAW, POS_NAKS, DASHA_ORDER, DASHA_YEARS,
    NAK_DASHA, NAK_SPAN, ASPECT_WEALTH_POS, ASPECT_DANGER_POS, ASPECT_NEUTRAL_POS,
    PUSHKAR, PUSHKAR_D9, PUSHKAR_BHAGA, NATURAL_BENEFICS, SIGN_EL,
    NAK27_GOOD, NAK27_BAD, SPEED_RANK, SECTOR_MAP, LATTA,
    gs, gn, gni, gh, gnav, aspect_within, grade_aspect_dist,
    is_pushkar, is_pushkar_d9v, is_pushkar_bhaga, is_vargottama,
    pushkar_vargottama, get_dasha_levels, log
)
from vedha_engine import (
    compute_composite_score, extract_vedha_features,
    compute_natal_vedha, extract_natal_transit_cross_features
)
from panchang_engine import (
    extract_panchang_features, extract_natal_panchang,
    extract_panchang_crossref
)
import swisseph as swe

EPHE_PATH = r'C:\Users\patel\Desktop\Python\Learn\sweph'

# ── SPEED CLASSIFICATION ──
# Standalone nakshatra/sign features for these are EPOCH-BIASED
VERY_SLOW = {'Uranus','Neptune','Pluto'}         # 7-32yr per nakshatra
SLOW      = {'Sat','Rahu','Ketu'}                # 9mo-1yr per nakshatra
FAST      = {'Moon','Merc','Ven','Sun','Mars'}   # days-weeks per nakshatra
SLOW_ALL  = VERY_SLOW | SLOW                     # union

def _is_slow_standalone(feat_name):
    """Return True if feature is a standalone slow-planet nakshatra/sign feature."""
    for sp in VERY_SLOW:
        if feat_name.startswith(sp+'_') and any(feat_name.endswith(s) for s in
            ['_NegNak','_PracPaw','_D9PosNak','_Moving','_D9Moving',
             '_PushNav','_PushD9V','_PushBhaga','_Vargottama','_PushVarg']):
            return True
    # Saturn/Rahu/Ketu: less extreme but still slow
    for sp in SLOW:
        if feat_name.startswith(sp+'_') and any(feat_name.endswith(s) for s in
            ['_D9PosNak','_D9Moving','_PushNav','_PushD9V','_Vargottama','_PushVarg']):
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# PHASE 4: TRANSIT FEATURE EXTRACTION (EPOCH-BIAS AWARE)
# ═══════════════════════════════════════════════════════════════
def extract_all_features(natal_lons, ipo_str, target_date_str_or_dt, sector='Unknown'):
    """Extract ALL 22-topic features for one stock at one date."""
    swe.set_ephe_path(EPHE_PATH); swe.set_sid_mode(swe.SIDM_LAHIRI)
    if isinstance(target_date_str_or_dt, datetime.datetime):
        dt = target_date_str_or_dt
        dt_utc = dt.astimezone(datetime.timezone.utc)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    else:
        try:
            import pytz
            dt = datetime.datetime.strptime(target_date_str_or_dt, '%Y-%m-%d')
            est = pytz.timezone('US/Eastern')
            dt_local = est.localize(datetime.datetime(dt.year, dt.month, dt.day, 9, 30))
            dt_utc = dt_local.astimezone(datetime.timezone.utc)
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
        except:
            return None
    
    ayan = swe.get_ayanamsa_ut(jd)
    jd_birth = natal_lons.get('_jd', jd - 365*10)
    asc = natal_lons.get('_asc', 0)

    feats = {}
    lons = {}
    secpl = set(SECTOR_MAP.get(sector, []))
    feats['_year'] = dt.year   # for epoch-detrending

    # ── Compute transit positions ──
    for nm, pid in PL.items():
        try:
            pos, _ = swe.calc_ut(jd, pid)
            lon = (pos[0] - ayan) % 360
        except:
            continue
        lons[nm] = lon
        sign = gs(lon); nak = gn(lon); nh = gh(lon, asc)
        nav_s = gnav(lon)

        # Topic 5: Moving signs D1
        feats[f'{nm}_Moving'] = 1 if sign in MOVING else 0
        feats[f'{nm}_D9Moving'] = 1 if nav_s in MOVING else 0
        # Topic 14: Nakshatra quality
        feats[f'{nm}_NegNak'] = 1 if nak in NEG_NAKS else 0
        feats[f'{nm}_PracPaw'] = 1 if nak in PRACPAW else 0
        # Topic 20: D9 nak quality
        d9_nak_lon = SIGNS.index(nav_s)*30+15
        feats[f'{nm}_D9PosNak'] = 1 if gn(d9_nak_lon) in POS_NAKS else 0
        # Topic 7: Sector planets
        feats[f'{nm}_IsSec'] = 1 if nm in secpl else 0
        # Topic 11: Pushkar Nav
        feats[f'{nm}_PushNav'] = 1 if is_pushkar(lon) else 0
        feats[f'{nm}_PushD9V'] = 1 if is_pushkar_d9v(lon) else 0
        # Topic 12: Pushkar Bhaga
        feats[f'{nm}_PushBhaga'] = 1 if is_pushkar_bhaga(lon) else 0
        # Topic 13: Vargottama
        feats[f'{nm}_Vargottama'] = 1 if is_vargottama(lon) else 0
        feats[f'{nm}_PushVarg'] = 1 if pushkar_vargottama(lon) else 0
        # House placements
        feats[f'{nm}_WealthH'] = 1 if nh in WEALTH_H else 0
        feats[f'{nm}_LossH'] = 1 if nh in LOSS_H else 0
        # Gap 4: Element
        feats[f'{nm}_Element_Fire'] = 1 if SIGN_EL.get(sign) == 'Fire' else 0
        feats[f'{nm}_Element_Earth'] = 1 if SIGN_EL.get(sign) == 'Earth' else 0
        feats[f'{nm}_Element_Air'] = 1 if SIGN_EL.get(sign) == 'Air' else 0
        feats[f'{nm}_Element_Water'] = 1 if SIGN_EL.get(sign) == 'Water' else 0
        # Gap 9: Positive signs
        feats[f'{nm}_PosSign'] = 1 if sign in POS_SIGNS else 0

    # Ketu
    if 'Rahu' in lons:
        kl = (lons['Rahu']+180)%360; lons['Ketu'] = kl
        ks = gs(kl); knak = gn(kl)
        feats['Ketu_Moving'] = 1 if ks in MOVING else 0
        feats['Ketu_NegNak'] = 1 if knak in NEG_NAKS else 0

    # ── NEW: INTERACTION FEATURES (Fast × Slow) ──
    # These are genuinely predictive: fast planet changes but slow planet gives context
    for fast_p in FAST:
        if fast_p not in lons: continue
        for slow_p in SLOW_ALL:
            sl = lons.get(slow_p)
            if sl is None: continue
            fl = lons[fast_p]
            # Aspect between fast and slow (changes frequently as fast moves)
            for ang in [0, 90, 180]:
                if aspect_within(fl, sl, ang, orb=8):
                    feats[f'IX_{fast_p}_{slow_p}_{ang}'] = 1
            # Combined: fast planet in Pushkar WHILE conjunct slow planet
            if aspect_within(fl, sl, 0, orb=10) and is_pushkar(fl):
                feats[f'IX_{fast_p}_{slow_p}_ConjPush'] = 1
            # Combined: fast planet in positive nak + slow planet in positive nak
            if gn(fl) in POS_NAKS and gn(sl) in POS_NAKS:
                feats[f'IX_{fast_p}_{slow_p}_BothPosNak'] = 1

    # Fast×Fast interactions (always valid)
    fast_list = [p for p in FAST if p in lons]
    for i, p1 in enumerate(fast_list):
        for p2 in fast_list[i+1:]:
            for ang in [0, 90, 180]:
                if aspect_within(lons[p1], lons[p2], ang, orb=8):
                    feats[f'FF_{p1}_{p2}_{ang}'] = 1

    # ── Topic 1: Index Volatility & Gap 1 ──
    if 'Moon' in lons and 'Merc' in lons and 'Sun' in lons:
        ml, mel, sl = lons['Moon'], lons['Merc'], lons['Sun']
        # Moon-Merc
        feats['Vol_MoonMerc_Conj'] = 1 if aspect_within(ml,mel,0) else 0
        feats['Vol_MoonMerc_Sq'] = 1 if aspect_within(ml,mel,90) else 0
        feats['Vol_MoonMerc_Opp'] = 1 if aspect_within(ml,mel,180) else 0
        # Moon-Sun
        feats['Vol_MoonSun_Conj'] = 1 if aspect_within(ml,sl,0) else 0
        feats['Vol_MoonSun_Sq'] = 1 if aspect_within(ml,sl,90) else 0
        feats['Vol_MoonSun_Opp'] = 1 if aspect_within(ml,sl,180) else 0
        # Merc-Sun
        feats['Vol_MercSun_Conj'] = 1 if aspect_within(mel,sl,0) else 0
        feats['Vol_MercSun_Sq'] = 1 if aspect_within(mel,sl,90) else 0
        feats['Vol_MercSun_Opp'] = 1 if aspect_within(mel,sl,180) else 0
        
        # Kendra counts
        feats['Vol_Kendra_Count'] = sum(1 for pl in [ml, mel, sl] if gs(pl) in MOVING)
        
        # D9 Moon-Merc-Sun concepts
        feats['D9_MoonMerc_Conj'] = 1 if aspect_within(ml,mel,0,orb=15) else 0
        feats['D9_MoonSun_Conj'] = 1 if aspect_within(ml,sl,0,orb=15) else 0
        feats['D9_MercSun_Conj'] = 1 if aspect_within(mel,sl,0,orb=15) else 0
        
        vol_d1 = (feats['Vol_MoonMerc_Conj'] or feats['Vol_MoonMerc_Opp'] or feats['Vol_MoonMerc_Sq'] or
                  feats['Vol_MoonSun_Conj'] or feats['Vol_MoonSun_Opp'] or feats['Vol_MoonSun_Sq'])
        vol_d9 = feats['D9_MoonMerc_Conj'] or feats['D9_MoonSun_Conj'] or feats['D9_MercSun_Conj']
        feats['Volatility_D1D9_Both'] = 1 if (vol_d1 and vol_d9) else 0

    # ── Topic 2 & Gap 2: Slow planet ahead of fast (D1 & D9) ──
    apply_ct = 0; separ_ct = 0
    d9_apply_ct = 0; d9_separ_ct = 0
    for f in FAST:
        for s in list(SLOW_ALL) + ['Jup']:
            if f in lons and s in lons:
                diff = (lons[s] - lons[f]) % 360
                if diff < 15:
                    feats[f'Apply_{f}_{s}'] = 1; apply_ct += 1
                elif diff > 345:
                    feats[f'Separ_{f}_{s}'] = 1; separ_ct += 1
                
                # Gap 2: D9 apply/separating
                f_d9 = (lons[f] * 9) % 360
                s_d9 = (lons[s] * 9) % 360
                d9_diff = (s_d9 - f_d9) % 360
                if d9_diff < 15:
                    feats[f'D9_Apply_{f}_{s}'] = 1; d9_apply_ct += 1
                elif d9_diff > 345:
                    feats[f'D9_Separ_{f}_{s}'] = 1; d9_separ_ct += 1

    feats['Apply_Total'] = apply_ct
    feats['Separ_Total'] = separ_ct
    feats['D9_Apply_Total'] = d9_apply_ct
    feats['D9_Separ_Total'] = d9_separ_ct

    # ── Topic 3: Trend reversal aspects ──
    tr_planets = ['Rahu','Merc','Ven','Ketu','Sun','Mars','Jup','Moon']
    tr_count = 0
    for i, p1 in enumerate(tr_planets):
        for p2 in tr_planets[i+1:]:
            l1 = lons.get(p1); l2 = lons.get(p2)
            if l1 is None or l2 is None: continue
            for ang in [0, 90, 120, 180]:
                if aspect_within(l1, l2, ang):
                    feats[f'TR_{p1}{p2}_{ang}'] = 1; tr_count += 1
    feats['TR_Total'] = tr_count

    # ── Topic 4 & Gap 3: Mercury-Venus aspects & Direction Match ──
    if 'Merc' in lons and 'Ven' in lons and 'Sun' in lons:
        feats['MercVen_60'] = 1 if aspect_within(lons['Merc'], lons['Ven'], 60) else 0
        for ang in [0, 90, 120, 180]:
            feats[f'MercVen_{ang}'] = 1 if aspect_within(lons['Merc'], lons['Ven'], ang) else 0
            
        # Gap 3: Both moving same direction w.r.t Sun
        sl = lons['Sun']; ml = lons['Merc']; vl = lons['Ven']
        dist_m = (ml - sl) % 360
        dist_v = (vl - sl) % 360
        m_ahead = dist_m < 180
        v_ahead = dist_v < 180
        feats['MercVen_SameDir'] = 1 if m_ahead == v_ahead else 0

    # ── Topic 6 & Gap 11: Max elongation (continuous & binary) ──
    for p1 in ['Merc', 'Ven', 'Mars']:
        if p1 in lons and 'Sun' in lons:
            sep = abs(lons['Sun']-lons[p1])%360; sep = min(sep, 360-sep)
            feats[f'Elong_Sun{p1}_raw'] = sep / 180.0
            
    if 'Sun' in lons and 'Merc' in lons:
        sep = abs(lons['Sun']-lons['Merc'])%360; sep = min(sep, 360-sep)
        feats['MaxElong_SunMerc'] = 1 if sep >= 25 else 0
    if 'Sun' in lons and 'Ven' in lons:
        sep = abs(lons['Sun']-lons['Ven'])%360; sep = min(sep, 360-sep)
        feats['MaxElong_SunVen'] = 1 if sep >= 44 else 0

    # ── Topic 8/9 & Gap 5 & 6: Deeper Dasha & Transit Condition ──
    moon_lon_natal = natal_lons.get('Moon', 0)
    # Re-calc Dasha properly with PD level
    time_passed = jd - jd_birth
    years_passed = time_passed / 365.25636  # Sidereal year
    
    nak_pos = (moon_lon_natal % 360) / NAK_SPAN
    nak_idx = int(nak_pos)
    rem_fraction = nak_pos - nak_idx
    
    current_idx_md = nak_idx % 9
    first_dasha_lord = NAK_DASHA[current_idx_md]
    first_dasha_total_years = DASHA_YEARS[first_dasha_lord]
    first_dasha_rem_years = first_dasha_total_years * (1.0 - rem_fraction)
    
    # ── Level 1: Mahadasha (MD) ──
    if years_passed <= first_dasha_rem_years:
        md_lord = first_dasha_lord
        md_years_elapsed = years_passed
    else:
        rem_yr = years_passed - first_dasha_rem_years
        idx = current_idx_md + 1
        while True:
            lord = NAK_DASHA[idx]
            dyr = DASHA_YEARS[lord]
            if rem_yr <= dyr:
                md_lord = lord
                md_years_elapsed = rem_yr
                break
            rem_yr -= dyr
            idx += 1
            
    # ── Level 2: Antardasha (AD) ──
    md_total_years = DASHA_YEARS[md_lord]
    fraction_md_passed = md_years_elapsed / md_total_years
    start_ad_idx = DASHA_ORDER.index(md_lord)
    
    rem_fraction_ad = fraction_md_passed
    ad_lord = md_lord
    for i in range(9):
        curr_lord = DASHA_ORDER[(start_ad_idx + i) % 9]
        ad_fraction = DASHA_YEARS[curr_lord] / 120.0  # AD ratio = (AD yrs) / 120
        if rem_fraction_ad <= ad_fraction:
            ad_lord = curr_lord
            ad_total_fraction = ad_fraction
            ad_fraction_elapsed = rem_fraction_ad
            break
        rem_fraction_ad -= ad_fraction
        
    # ── Level 3: Pratyantar Dasha (PD) ──
    fraction_ad_passed = ad_fraction_elapsed / ad_total_fraction
    start_pd_idx = DASHA_ORDER.index(ad_lord)
    
    rem_fraction_pd = fraction_ad_passed
    pd_lord = ad_lord
    for i in range(9):
        curr_lord = DASHA_ORDER[(start_pd_idx + i) % 9]
        pd_fraction = DASHA_YEARS[curr_lord] / 120.0
        if rem_fraction_pd <= pd_fraction:
            pd_lord = curr_lord
            break
        rem_fraction_pd -= pd_fraction

    feats['MD'] = md_lord; feats['AD'] = ad_lord; feats['PD'] = pd_lord
    
    # Dasha inter-distances and moving signs (Gap 5, 6)
    for p_pair, l1, l2 in [('MD_AD', md_lord, ad_lord), ('AD_PD', ad_lord, pd_lord), ('MD_PD', md_lord, pd_lord)]:
        if l1 in lons and l2 in lons:
            dist = (lons[l2] - lons[l1]) % 360
            grade = grade_aspect_dist(lons[l1], lons[l2])[1]
            feats[f'{p_pair}_wealth'] = 1 if grade == 'WEALTH' else 0
            feats[f'{p_pair}_danger'] = 1 if grade == 'DANGER' else 0
            
    dasha_in_moving = sum(1 for dp in {md_lord, ad_lord, pd_lord} if dp in lons and gs(lons[dp]) in MOVING)
    feats['Dasha_InMoving'] = dasha_in_moving
    dasha_in_pracpaw = sum(1 for dp in {md_lord, ad_lord, pd_lord} if dp in lons and gn(lons[dp]) in PRACPAW)
    feats['Dasha_InPracPaw'] = dasha_in_pracpaw

    # ── Topic 10: Health Grid ──
    moon_nak_i = natal_lons.get('_moon_nak_i', 0)
    good_ct = 0; bad_ct = 0
    for nm, lon in lons.items():
        if nm.startswith('_'): continue
        offset = (gni(lon) - moon_nak_i) % 27 + 1
        if offset in NAK27_GOOD: good_ct += 1
        if offset in NAK27_BAD: bad_ct += 1
    feats['HealthGrid_Good'] = good_ct
    feats['HealthGrid_Bad'] = bad_ct
    feats['HealthGrid_Ratio'] = good_ct / max(bad_ct, 1)

    # ── Topic 15: Latta ──
    latta_ct = 0
    for nm, lon in lons.items():
        if nm.startswith('_'): continue
        nak_i = gni(lon) + 1
        if nak_i in LATTA and LATTA[nak_i]:
            if nm in LATTA[nak_i]: latta_ct += 1
    feats['Latta_Count'] = latta_ct

    # ── Topic 17/18 & Gap 10: Conjunction combos & Wealth Pairs ──
    conj_pos_ct = 0; conj_push_ct = 0
    conj_wealth_ct = 0
    WEALTH_PAIRS = [{'Jup','Pluto'}, {'Pluto','Ven'}, {'Jup','Ven'}, {'Sat','Ven'}, {'Rahu','Ven'}]
    
    pl_list = [nm for nm in lons if not nm.startswith('_')]
    for i, p1 in enumerate(pl_list):
        for p2 in pl_list[i+1:]:
            if aspect_within(lons[p1], lons[p2], 0, orb=8):
                if gn(lons[p1]) in POS_NAKS and gn(lons[p2]) in POS_NAKS:
                    conj_pos_ct += 1
                    # Gap 10 specific wealth combinations
                    if {p1, p2} in WEALTH_PAIRS:
                        if is_pushkar(lons[p1]) or is_pushkar(lons[p2]):
                            conj_wealth_ct += 1
                if is_pushkar(lons[p1]) and is_pushkar(lons[p2]):
                    conj_push_ct += 1
    feats['ConjPosNak_Total'] = conj_pos_ct
    feats['ConjPush_Total'] = conj_push_ct
    feats['ConjWealthPair_PushPos'] = conj_wealth_ct

    # ── Topic 19 & Gap 7, 8: Slow Planet Aggregates ──
    slow_in_moving = sum(1 for s in ['Jup','Sat','Rahu','Ketu','Uranus','Neptune','Pluto']
                         if s in lons and gs(lons[s]) in MOVING)
                         
    slow_in_scorpio_naks = sum(1 for s in ['Jup','Sat','Rahu','Ketu','Uranus','Neptune','Pluto']
                               if s in lons and gn(lons[s]) in NEG_NAKS)
                               
    slow_in_loss_h = sum(1 for s in ['Jup','Sat','Rahu','Ketu','Uranus','Neptune','Pluto']
                               if s in lons and gh(lons[s], asc) in LOSS_H)
                               
    feats['Slow_InMoving'] = slow_in_moving
    feats['Slow_InScorpioNaks'] = slow_in_scorpio_naks
    feats['Slow_InLossH'] = slow_in_loss_h

    # ── Topic 21: Pressure transit ──
    pressure_ct = 0
    for nm, lon in lons.items():
        if nm.startswith('_'): continue
        offset = (gni(lon) - moon_nak_i) % 27 + 1
        if offset in NAK27_BAD: pressure_ct += 1
    feats['Transit_InPressureNak'] = pressure_ct

    # ── Aggregates (FAST PLANETS ONLY to avoid epoch bias) ──
    feats['Fast_Moving_Count'] = sum(1 for nm in FAST if nm in lons and gs(lons[nm]) in MOVING)
    feats['Fast_PosSign_Count'] = sum(1 for nm in FAST if nm in lons and gs(lons[nm]) in POS_SIGNS)
    feats['Fast_PushNav_Count'] = sum(1 for nm in FAST if nm in lons and is_pushkar(lons[nm]))
    feats['Fast_Vargottama_Count'] = sum(1 for nm in FAST if nm in lons and is_vargottama(lons[nm]))
    feats['Fast_NegNak_Count'] = sum(1 for nm in FAST if nm in lons and gn(lons[nm]) in NEG_NAKS)
    feats['Fast_PosNak_Count'] = sum(1 for nm in FAST if nm in lons and gn(lons[nm]) in POS_NAKS)
    feats['All_Moving_Count'] = sum(1 for nm in lons if not nm.startswith('_') and gs(lons[nm]) in MOVING)
    feats['All_Vargottama_Count'] = sum(1 for nm in lons if not nm.startswith('_') and is_vargottama(lons[nm]))

    # ── Topic 25-30: Panchang + Hora (transit) ──
    sun_lon = lons.get('Sun', 0)
    moon_lon = lons.get('Moon', 0)
    try:
        panchang_feats = extract_panchang_features(jd, sun_lon, moon_lon, lons)
        for k, v in panchang_feats.items():
            if not k.startswith('_'):
                feats[k] = v
        # Store raw values for cross-ref
        feats['_panchang_raw'] = panchang_feats
    except:
        pass

    return feats, lons


# ═══════════════════════════════════════════════════════════════
# NATAL BLUEPRINT: Compute ALL topic features at birth (cached per stock)
# Mirrors extract_all_features() but using NATAL positions
# ═══════════════════════════════════════════════════════════════
def compute_natal_blueprint(natal_lons):
    """
    Compute ALL topic features for the NATAL chart itself (D1 and D9).
    This mirrors extract_all_features() exactly but runs on birth positions.
    Called once per stock, cached, then cross-referenced every transit move.

    Returns dict with:
    - Per-planet features: N_{planet}_{feature} (Topics 5,11,12,13,14,20)
    - Aspect features: N_Vol_*, N_TR_*, N_MercVen_*, N_Apply_*, etc (Topics 1-4,6)
    - Structural features: N_ConjPosNak_Total, etc (Topics 17/18)
    - Latta/HealthGrid at birth (Topics 10,15)
    - Sign indices for sign-return detection
    """
    bp = {}
    asc = natal_lons.get('_asc', 0)
    nlons = {}  # natal lon dict for aspect computation

    # ── Per-planet features at birth (Topics 5, 11, 12, 13, 14, 20) ──
    for nm in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat','Rahu','Ketu']:
        lon = natal_lons.get(nm)
        if lon is None:
            if nm == 'Ketu' and 'Rahu' in natal_lons:
                lon = (natal_lons['Rahu'] + 180) % 360
            else:
                continue

        nlons[nm] = lon
        sign = gs(lon); nak = gn(lon); nh = gh(lon, asc)
        nav_s = gnav(lon)

        # Topic 5: Moving signs
        bp[f'N_{nm}_Moving'] = 1 if sign in MOVING else 0
        bp[f'N_{nm}_D9Moving'] = 1 if nav_s in MOVING else 0
        # Topic 14: Nakshatra quality
        bp[f'N_{nm}_NegNak'] = 1 if nak in NEG_NAKS else 0
        bp[f'N_{nm}_PracPaw'] = 1 if nak in PRACPAW else 0
        bp[f'N_{nm}_PosNak'] = 1 if nak in POS_NAKS else 0
        # Topic 20: D9 nak quality
        d9_nak_lon = SIGNS.index(nav_s)*30+15 if nav_s in SIGNS else 0
        bp[f'N_{nm}_D9PosNak'] = 1 if gn(d9_nak_lon) in POS_NAKS else 0
        # Topic 11: Pushkar Nav
        bp[f'N_{nm}_PushNav'] = 1 if is_pushkar(lon) else 0
        bp[f'N_{nm}_PushD9V'] = 1 if is_pushkar_d9v(lon) else 0
        # Topic 12: Pushkar Bhaga
        bp[f'N_{nm}_PushBhaga'] = 1 if is_pushkar_bhaga(lon) else 0
        # Topic 13: Vargottama
        bp[f'N_{nm}_Vargottama'] = 1 if is_vargottama(lon) else 0
        bp[f'N_{nm}_PushVarg'] = 1 if pushkar_vargottama(lon) else 0
        # House placements
        bp[f'N_{nm}_WealthH'] = 1 if nh in WEALTH_H else 0
        bp[f'N_{nm}_LossH'] = 1 if nh in LOSS_H else 0
        # Gap 4: Element
        bp[f'N_{nm}_Element_Fire'] = 1 if SIGN_EL.get(sign) == 'Fire' else 0
        bp[f'N_{nm}_Element_Earth'] = 1 if SIGN_EL.get(sign) == 'Earth' else 0
        bp[f'N_{nm}_Element_Air'] = 1 if SIGN_EL.get(sign) == 'Air' else 0
        bp[f'N_{nm}_Element_Water'] = 1 if SIGN_EL.get(sign) == 'Water' else 0
        # Gap 9: Positive signs
        bp[f'N_{nm}_PosSign'] = 1 if sign in POS_SIGNS else 0
        # Sign/Nak indices (for sign-return detection)
        bp[f'N_{nm}_Sign'] = SIGNS.index(sign) if sign in SIGNS else 0
        bp[f'N_{nm}_Nak'] = nak
        bp[f'N_{nm}_D9Sign'] = SIGNS.index(nav_s) if nav_s in SIGNS else 0

    # ── Topic 1: Natal Volatility aspects (Moon-Merc-Sun at birth & Gap 1) ──
    if 'Moon' in nlons and 'Merc' in nlons and 'Sun' in nlons:
        ml, mel, sl = nlons['Moon'], nlons['Merc'], nlons['Sun']
        # Moon-Merc
        bp['N_Vol_MoonMerc_Conj'] = 1 if aspect_within(ml,mel,0) else 0
        bp['N_Vol_MoonMerc_Sq'] = 1 if aspect_within(ml,mel,90) else 0
        bp['N_Vol_MoonMerc_Opp'] = 1 if aspect_within(ml,mel,180) else 0
        # Moon-Sun
        bp['N_Vol_MoonSun_Conj'] = 1 if aspect_within(ml,sl,0) else 0
        bp['N_Vol_MoonSun_Sq'] = 1 if aspect_within(ml,sl,90) else 0
        bp['N_Vol_MoonSun_Opp'] = 1 if aspect_within(ml,sl,180) else 0
        # Merc-Sun
        bp['N_Vol_MercSun_Conj'] = 1 if aspect_within(mel,sl,0) else 0
        bp['N_Vol_MercSun_Sq'] = 1 if aspect_within(mel,sl,90) else 0
        bp['N_Vol_MercSun_Opp'] = 1 if aspect_within(mel,sl,180) else 0
        
        # Kendra counts
        bp['N_Vol_Kendra_Count'] = sum(1 for pl in [ml, mel, sl] if gs(pl) in MOVING)
        
        # D9 Moon-Merc-Sun concepts
        bp['N_D9_MoonMerc_Conj'] = 1 if aspect_within(ml,mel,0,orb=15) else 0
        bp['N_D9_MoonSun_Conj'] = 1 if aspect_within(ml,sl,0,orb=15) else 0
        bp['N_D9_MercSun_Conj'] = 1 if aspect_within(mel,sl,0,orb=15) else 0
        
        vol_d1 = (bp['N_Vol_MoonMerc_Conj'] or bp['N_Vol_MoonMerc_Opp'] or bp['N_Vol_MoonMerc_Sq'] or
                  bp['N_Vol_MoonSun_Conj'] or bp['N_Vol_MoonSun_Opp'] or bp['N_Vol_MoonSun_Sq'])
        vol_d9 = bp['N_D9_MoonMerc_Conj'] or bp['N_D9_MoonSun_Conj'] or bp['N_D9_MercSun_Conj']
        bp['N_Volatility_D1D9_Both'] = 1 if (vol_d1 and vol_d9) else 0

    # ── Topic 2 & Gap 2: Slow planet ahead of fast at birth (D1 & D9) ──
    apply_ct = 0; separ_ct = 0
    d9_apply_ct = 0; d9_separ_ct = 0
    for f in FAST:
        for s in list(SLOW_ALL) + ['Jup']:
            if f in nlons and s in nlons:
                diff = (nlons[s] - nlons[f]) % 360
                if diff < 15:
                    bp[f'N_Apply_{f}_{s}'] = 1; apply_ct += 1
                elif diff > 345:
                    bp[f'N_Separ_{f}_{s}'] = 1; separ_ct += 1
                    
                # Gap 2: D9 apply/separating
                f_d9 = (nlons[f] * 9) % 360
                s_d9 = (nlons[s] * 9) % 360
                d9_diff = (s_d9 - f_d9) % 360
                if d9_diff < 15:
                    bp[f'N_D9_Apply_{f}_{s}'] = 1; d9_apply_ct += 1
                elif d9_diff > 345:
                    bp[f'N_D9_Separ_{f}_{s}'] = 1; d9_separ_ct += 1

    bp['N_Apply_Total'] = apply_ct
    bp['N_Separ_Total'] = separ_ct
    bp['N_D9_Apply_Total'] = d9_apply_ct
    bp['N_D9_Separ_Total'] = d9_separ_ct

    # ── Topic 1: Volatility natal aspects ──
    ml, mel, sl = nlons.get('Moon'), nlons.get('Merc'), nlons.get('Sun')
    if ml is not None and mel is not None:
        bp['N_Vol_MoonMerc_Conj'] = 1 if aspect_within(ml,mel,0) else 0
        bp['N_Vol_MoonMerc_Opp'] = 1 if aspect_within(ml,mel,180) else 0
    if ml is not None and sl is not None:
        bp['N_Vol_MoonSun_Conj'] = 1 if aspect_within(ml,sl,0) else 0
        bp['N_Vol_MoonSun_Sq'] = 1 if aspect_within(ml,sl,90) else 0

    # ── Topic 2: Natal applying/separating ──
    n_apply = 0; n_separ = 0
    for f in FAST:
        for s in list(SLOW_ALL) + ['Jup']:
            if f in nlons and s in nlons:
                diff = (nlons[s] - nlons[f]) % 360
                if diff < 15: n_apply += 1
                elif diff > 345: n_separ += 1
    bp['N_Apply_Total'] = n_apply
    bp['N_Separ_Total'] = n_separ

    # ── Topic 3: Natal trend reversal aspects ──
    tr_planets = ['Rahu','Merc','Ven','Ketu','Sun','Mars','Jup','Moon']
    n_tr_count = 0
    for i, p1 in enumerate(tr_planets):
        for p2 in tr_planets[i+1:]:
            l1 = nlons.get(p1); l2 = nlons.get(p2)
            if l1 is None or l2 is None: continue
            for ang in [0, 90, 120, 180]:
                if aspect_within(l1, l2, ang):
                    n_tr_count += 1
    bp['N_TR_Total'] = n_tr_count

    # ── Topic 4 & Gap 3: Natal Mercury-Venus aspects & Direction ──
    if 'Merc' in nlons and 'Ven' in nlons and 'Sun' in nlons:
        bp['N_MercVen_Conj'] = 1 if aspect_within(nlons['Merc'], nlons['Ven'], 0) else 0
        bp['N_MercVen_60'] = 1 if aspect_within(nlons['Merc'], nlons['Ven'], 60) else 0
        bp['N_MercVen_90'] = 1 if aspect_within(nlons['Merc'], nlons['Ven'], 90) else 0
        bp['N_MercVen_120'] = 1 if aspect_within(nlons['Merc'], nlons['Ven'], 120) else 0
        bp['N_MercVen_180'] = 1 if aspect_within(nlons['Merc'], nlons['Ven'], 180) else 0

        sl = nlons['Sun']; ml = nlons['Merc']; vl = nlons['Ven']
        dist_m = (ml - sl) % 360
        dist_v = (vl - sl) % 360
        m_ahead = dist_m < 180
        v_ahead = dist_v < 180
        bp['N_MercVen_SameDir'] = 1 if m_ahead == v_ahead else 0

    # ── Topic 6 & Gap 11: Natal max elongation ──
    for p1 in ['Merc', 'Ven', 'Mars']:
        if p1 in nlons and 'Sun' in nlons:
            sep = abs(nlons['Sun']-nlons[p1])%360; sep = min(sep, 360-sep)
            bp[f'N_Elong_Sun{p1}_raw'] = sep / 180.0
            
    if 'Sun' in nlons and 'Merc' in nlons:
        sep = abs(nlons['Sun']-nlons['Merc'])%360; sep = min(sep, 360-sep)
        bp['N_MaxElong_SunMerc'] = 1 if sep >= 25 else 0
    if 'Sun' in nlons and 'Ven' in nlons:
        sep = abs(nlons['Sun']-nlons['Ven'])%360; sep = min(sep, 360-sep)
        bp['N_MaxElong_SunVen'] = 1 if sep >= 44 else 0

    # ── Topic 10: Natal Health Grid (natal planets in natal Moon's nak grid) ──
    moon_nak_i = natal_lons.get('_moon_nak_i', 0)
    n_good = 0; n_bad = 0
    for nm, lon in nlons.items():
        if nm.startswith('_'): continue
        offset = (gni(lon) - moon_nak_i) % 27 + 1
        if offset in NAK27_GOOD: n_good += 1
        if offset in NAK27_BAD: n_bad += 1
    bp['N_HealthGrid_Good'] = n_good
    bp['N_HealthGrid_Bad'] = n_bad
    bp['N_HealthGrid_Ratio'] = n_good / max(n_bad, 1)

    # ── Topic 15: Natal Latta ──
    n_latta = 0
    for nm, lon in nlons.items():
        if nm.startswith('_'): continue
        nak_i = gni(lon) + 1
        if nak_i in LATTA and LATTA[nak_i]:
            if nm in LATTA[nak_i]: n_latta += 1
    bp['N_Latta_Count'] = n_latta

    # ── Topic 17/18 & Gap 10: Natal conjunction combos & Wealth Pairs ──
    n_conj_pos = 0; n_conj_push = 0
    n_conj_wealth_ct = 0
    WEALTH_PAIRS = [{'Jup','Pluto'}, {'Pluto','Ven'}, {'Jup','Ven'}, {'Sat','Ven'}, {'Rahu','Ven'}]

    pl_list = [nm for nm in nlons if not nm.startswith('_')]
    for i, p1 in enumerate(pl_list):
        for p2 in pl_list[i+1:]:
            if aspect_within(nlons[p1], nlons[p2], 0, orb=8):
                if gn(nlons[p1]) in POS_NAKS and gn(nlons[p2]) in POS_NAKS:
                    n_conj_pos += 1
                    if {p1, p2} in WEALTH_PAIRS:
                        if is_pushkar(nlons[p1]) or is_pushkar(nlons[p2]):
                            n_conj_wealth_ct += 1
                if is_pushkar(nlons[p1]) and is_pushkar(nlons[p2]):
                    n_conj_push += 1
    bp['N_ConjPosNak_Total'] = n_conj_pos
    bp['N_ConjPush_Total'] = n_conj_push
    bp['N_ConjWealthPair_PushPos'] = n_conj_wealth_ct

    # ── Structural totals & Gaps 7,8,9 ──
    bp['N_Moving_Total'] = sum(1 for p in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']
                               if bp.get(f'N_{p}_Moving', 0) == 1)
    bp['N_WealthH_Total'] = sum(1 for p in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']
                                 if bp.get(f'N_{p}_WealthH', 0) == 1)
                                 
    slow_all_in_ns = ['Jup','Sat','Rahu','Ketu','Uranus','Neptune','Pluto']
    bp['N_Slow_InMoving'] = sum(1 for p in slow_all_in_ns if p in nlons and gs(nlons[p]) in MOVING)
    bp['N_Slow_InScorpioNaks'] = sum(1 for p in slow_all_in_ns if p in nlons and gn(nlons[p]) in NEG_NAKS)
    bp['N_Slow_InLossH'] = sum(1 for p in slow_all_in_ns if p in nlons and gh(nlons[p], asc) in LOSS_H)
    
    bp['N_Fast_PosSign_Count'] = sum(1 for p in FAST if p in nlons and gs(nlons[p]) in POS_SIGNS)

    bp['N_PushNav_Total'] = sum(1 for p in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']
                                 if bp.get(f'N_{p}_PushNav', 0) == 1)
    bp['N_PushBhaga_Total'] = sum(1 for p in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']
                                   if bp.get(f'N_{p}_PushBhaga', 0) == 1)
    bp['N_Varg_Total'] = sum(1 for p in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']
                              if bp.get(f'N_{p}_Vargottama', 0) == 1)

    # ── Topic 25-31: Natal Panchang fingerprint ──
    ipo_jd = natal_lons.get('_jd', 0)
    if ipo_jd:
        try:
            natal_panch = extract_natal_panchang(natal_lons, ipo_jd)
            bp.update(natal_panch)
        except:
            pass

    return bp


def extract_natal_transit_crossref(natal_bp, transit_feats, transit_lons=None):
    """
    COMPREHENSIVE natal promise × transit activation cross-reference.
    Covers ALL 23 topics: per-planet features, aspects, conjunctions, elongation, etc.

    For each planet+dimension, creates:
    - MATCH: natal + transit both active → strongest signal
    - CONFLICT: one active, other not → frustrated/surprising
    - ACTIVATE: overcoming natal weakness via transit
    - REINFORCE_BAD: natal bad + transit bad → double trouble
    """
    cx = {}

    KEY_PLANETS = ['Sun','Moon','Mars','Merc','Jup','Ven','Sat']

    # ═══ LAYER 1: Per-planet dimension cross-ref (Topics 5,11,12,13,14,20) + Gaps 4, 9 ═══
    GOOD_DIMS = ['Moving','WealthH','PushNav','PushD9V','PushBhaga','Vargottama',
                 'PushVarg','D9Moving','D9PosNak','PosNak', 'PosSign']
    BAD_DIMS = ['LossH','NegNak','PracPaw']
    
    ELEM_DIMS = ['Element_Fire', 'Element_Earth', 'Element_Air', 'Element_Water']

    match_good_total = 0; match_bad_total = 0
    conflict_total = 0; activate_total = 0

    for planet in KEY_PLANETS:
        p_mg = 0; p_mb = 0; p_con = 0; p_act = 0

        for dim in GOOD_DIMS:
            nv = natal_bp.get(f'N_{planet}_{dim}', 0)
            tv = transit_feats.get(f'{planet}_{dim}', 0)
            if nv == 1 and tv == 1: p_mg += 1
            elif nv == 1 and tv == 0: p_con += 1
            elif nv == 0 and tv == 1: p_act += 1

        for dim in BAD_DIMS:
            nv = natal_bp.get(f'N_{planet}_{dim}', 0)
            tv = transit_feats.get(f'{planet}_{dim}', 0)
            if nv == 1 and tv == 1: p_mb += 1
            elif nv == 1 and tv == 0: p_act += 1
            elif nv == 0 and tv == 1: p_con += 1
            
        # Elements Match (Gap 4)
        for dim in ELEM_DIMS:
            nv = natal_bp.get(f'N_{planet}_{dim}', 0)
            tv = transit_feats.get(f'{planet}_{dim}', 0)
            if nv == 1 and tv == 1:
                cx[f'BP_{planet}_{dim}_Match'] = 1

        # Per-planet features (key planets only to avoid explosion)
        if planet in ('Jup','Sat','Mars','Ven','Moon'):
            cx[f'BP_{planet}_MatchGood'] = p_mg
            cx[f'BP_{planet}_MatchBad'] = p_mb
            cx[f'BP_{planet}_Conflict'] = p_con
            cx[f'BP_{planet}_Activate'] = p_act
            cx[f'BP_{planet}_Net'] = p_mg - p_mb

        match_good_total += p_mg; match_bad_total += p_mb
        conflict_total += p_con; activate_total += p_act

    # Aggregate per-planet cross
    cx['BP_MatchGood_Total'] = match_good_total
    cx['BP_MatchBad_Total'] = match_bad_total
    cx['BP_Conflict_Total'] = conflict_total
    cx['BP_Activate_Total'] = activate_total
    cx['BP_NetQuality'] = match_good_total - match_bad_total
    cx['BP_Alignment'] = match_good_total + match_bad_total

    # ═══ LAYER 2: Sign return detection (transit planet in natal sign) ═══
    sign_returns = 0; d9_sign_returns = 0
    if transit_lons:
        for planet in KEY_PLANETS:
            natal_sign = natal_bp.get(f'N_{planet}_Sign', -1)
            natal_d9sign = natal_bp.get(f'N_{planet}_D9Sign', -1)
            tl = transit_lons.get(planet)
            if tl is not None and natal_sign >= 0:
                transit_sign = SIGNS.index(gs(tl)) if gs(tl) in SIGNS else -1
                if transit_sign == natal_sign:
                    sign_returns += 1
                    cx[f'BP_{planet}_SignReturn'] = 1
                transit_d9sign = SIGNS.index(gnav(tl)) if gnav(tl) in SIGNS else -1
                if transit_d9sign == natal_d9sign:
                    d9_sign_returns += 1
    cx['BP_SignReturn_Total'] = sign_returns
    cx['BP_D9SignReturn_Total'] = d9_sign_returns

    # ═══ LAYER 3: Aspect pattern cross-ref (Topics 1-4, 6) + Gaps 1, 2, 3, 11 ═══
    # Topic 1 & Gap 1: Volatility — natal birth had Moon-Merc/Moon-Sun aspects? (D1 & D9)
    # If stock was born with volatility aspects AND transit has them → amplified
    n_vol_mmConj = natal_bp.get('N_Vol_MoonMerc_Conj', 0)
    n_vol_mmOpp = natal_bp.get('N_Vol_MoonMerc_Opp', 0)
    n_vol_msSq = natal_bp.get('N_Vol_MoonSun_Sq', 0)
    n_vol_d1d9 = natal_bp.get('N_Volatility_D1D9_Both', 0)
    
    t_vol_mmConj = transit_feats.get('Vol_MoonMerc_Conj', 0)
    t_vol_mmOpp = transit_feats.get('Vol_MoonMerc_Opp', 0)
    t_vol_msSq = transit_feats.get('Vol_MoonSun_Sq', 0)
    
    natal_vol = n_vol_mmConj or n_vol_mmOpp or n_vol_msSq
    transit_vol = t_vol_mmConj or t_vol_mmOpp or t_vol_msSq
    cx['BP_VolBothActive'] = 1 if (natal_vol and transit_vol) else 0
    cx['BP_VolNatalOnly'] = 1 if (natal_vol and not transit_vol) else 0
    cx['BP_Volatility_D1D9_BothActive'] = 1 if (n_vol_d1d9 and transit_vol) else 0

    # Topic 2 & Gap 2: Applying/Separating (D1 and D9) — compare natal pattern to transit
    n_apply = natal_bp.get('N_Apply_Total', 0)
    n_separ = natal_bp.get('N_Separ_Total', 0)
    t_apply = transit_feats.get('Apply_Total', 0)
    t_separ = transit_feats.get('Separ_Total', 0)
    cx['BP_ApplyMatch'] = min(n_apply, t_apply)  # overlap count
    cx['BP_SeparMatch'] = min(n_separ, t_separ)
    cx['BP_ApplyNatalHigh'] = 1 if n_apply >= 2 else 0  # stock born with many applying
    cx['BP_SeparNatalHigh'] = 1 if n_separ >= 2 else 0
    
    n_d9_apply = sum(1 for p in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat'] if natal_bp.get(f'N_D9_Apply_{p}_{p}', 0) == 1)
    cx['BP_D9_ApplyMatch'] = min(n_d9_apply, t_apply)

    # Topic 3: Trend reversal — natal aspect density vs transit
    n_tr = natal_bp.get('N_TR_Total', 0)
    t_tr = transit_feats.get('TR_Total', 0)
    cx['BP_TR_NatalDense'] = 1 if n_tr >= 5 else 0  # stock born with many aspects
    cx['BP_TR_BothDense'] = 1 if (n_tr >= 5 and t_tr >= 5) else 0

    # Topic 4 & Gap 3: Mercury-Venus natal → transit cross (including direction)
    n_mv_conj = natal_bp.get('N_MercVen_Conj', 0)
    t_mv_conj = transit_feats.get('MercVen_0', 0)
    cx['BP_MercVen_BothConj'] = 1 if (n_mv_conj and t_mv_conj) else 0
    n_mv_any = n_mv_conj or natal_bp.get('N_MercVen_60', 0) or natal_bp.get('N_MercVen_90', 0)
    t_mv_any = t_mv_conj or transit_feats.get('MercVen_60', 0) or transit_feats.get('MercVen_90', 0)
    cx['BP_MercVen_BothAspect'] = 1 if (n_mv_any and t_mv_any) else 0
    
    n_mv_sdir = natal_bp.get('N_MercVen_SameDir', 0)
    t_mv_sdir = transit_feats.get('MercVen_SameDir', 0)
    cx['BP_MercVen_BothSameDir'] = 1 if (n_mv_sdir and t_mv_sdir) else 0

    # Topic 6 & Gap 11: Max elongation (Raw & Threshold)
    n_elong_sm = natal_bp.get('N_MaxElong_SunMerc', 0)
    n_elong_sv = natal_bp.get('N_MaxElong_SunVen', 0)
    t_elong_sm = transit_feats.get('MaxElong_SunMerc', 0)
    t_elong_sv = transit_feats.get('MaxElong_SunVen', 0)
    cx['BP_ElongSunMerc_Both'] = 1 if (n_elong_sm and t_elong_sm) else 0
    cx['BP_ElongSunVen_Both'] = 1 if (n_elong_sv and t_elong_sv) else 0
    
    # Differential distance
    n_raw_sm = natal_bp.get('N_Elong_SunMerc_raw', 0)
    t_raw_sm = transit_feats.get('Elong_SunMerc_raw', 0)
    cx['BP_ElongSunMerc_Delta'] = t_raw_sm - n_raw_sm

    # ═══ LAYER 4: Health Grid / Latta natal vs transit cross (Topics 10, 15) ═══
    n_hg_good = natal_bp.get('N_HealthGrid_Good', 0)
    n_hg_bad = natal_bp.get('N_HealthGrid_Bad', 0)
    t_hg_good = transit_feats.get('HealthGrid_Good', 0)
    t_hg_bad = transit_feats.get('HealthGrid_Bad', 0)
    cx['BP_HG_NatalGoodHigh'] = 1 if n_hg_good >= 4 else 0
    cx['BP_HG_NatalBadHigh'] = 1 if n_hg_bad >= 3 else 0
    cx['BP_HG_BothGoodHigh'] = 1 if (n_hg_good >= 4 and t_hg_good >= 4) else 0
    cx['BP_HG_BothBadHigh'] = 1 if (n_hg_bad >= 3 and t_hg_bad >= 3) else 0

    n_latta = natal_bp.get('N_Latta_Count', 0)
    t_latta = transit_feats.get('Latta_Count', 0)
    cx['BP_Latta_NatalActive'] = 1 if n_latta >= 1 else 0
    cx['BP_Latta_BothActive'] = 1 if (n_latta >= 1 and t_latta >= 1) else 0

    # ═══ LAYER 5: Conjunction pattern cross (Topics 17/18) + Gap 10 ═══
    n_conj_pos = natal_bp.get('N_ConjPosNak_Total', 0)
    n_conj_push = natal_bp.get('N_ConjPush_Total', 0)
    n_conj_w_pp = natal_bp.get('N_ConjWealthPair_PushPos', 0)
    
    t_conj_pos = transit_feats.get('ConjPosNak_Total', 0)
    t_conj_push = transit_feats.get('ConjPush_Total', 0)
    t_conj_w_pp = transit_feats.get('ConjWealthPair_PushPos', 0)
    
    cx['BP_ConjPosNak_NatalHigh'] = 1 if n_conj_pos >= 1 else 0
    cx['BP_ConjPosNak_BothHigh'] = 1 if (n_conj_pos >= 1 and t_conj_pos >= 1) else 0
    cx['BP_ConjPush_BothHigh'] = 1 if (n_conj_push >= 1 and t_conj_push >= 1) else 0
    cx['BP_ConjWealthPP_BothHigh'] = 1 if (n_conj_w_pp >= 1 and t_conj_w_pp >= 1) else 0

    # ═══ LAYER 6: Natal structural scores (characterize stock's birth quality) & Gaps 7,8,9 ═══
    cx['BP_N_WealthTotal'] = natal_bp.get('N_WealthH_Total', 0)
    cx['BP_N_LossTotal'] = natal_bp.get('N_LossH_Total', 0)
    cx['BP_N_PushTotal'] = natal_bp.get('N_PushNav_Total', 0)
    cx['BP_N_PushBhagaTotal'] = natal_bp.get('N_PushBhaga_Total', 0)
    cx['BP_N_VargTotal'] = natal_bp.get('N_Varg_Total', 0)
    cx['BP_N_MovingTotal'] = natal_bp.get('N_Moving_Total', 0)
    cx['BP_N_NetHouse'] = natal_bp.get('N_WealthH_Total', 0) - natal_bp.get('N_LossH_Total', 0)
    cx['BP_N_HGRatio'] = natal_bp.get('N_HealthGrid_Ratio', 1.0)
    cx['BP_N_Slow_InScorpioNaks'] = natal_bp.get('N_Slow_InScorpioNaks', 0)
    cx['BP_N_Slow_InLossH'] = natal_bp.get('N_Slow_InLossH', 0)
    cx['BP_N_Fast_PosSign_Count'] = natal_bp.get('N_Fast_PosSign_Count', 0)

    return cx


def extract_vedha_topic23(natal_lons, target_date_str):
    """Extract Topic #23: Vedha + Ashtakavarga features for one stock at one date."""
    swe.set_ephe_path(EPHE_PATH); swe.set_sid_mode(swe.SIDM_LAHIRI)
    try:
        import pytz
        dt = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
        est = pytz.timezone('US/Eastern')
        dt_local = est.localize(datetime.datetime(dt.year, dt.month, dt.day, 9, 30))
        dt_utc = dt_local.astimezone(datetime.timezone.utc)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
    except:
        return {}

    bav = natal_lons.get('_bav')
    sav = natal_lons.get('_sav')
    moon_sign_idx = natal_lons.get('_moon_sign_idx', 0)
    asc_sign_idx = natal_lons.get('_asc_sign_idx', 0)
    if bav is None or sav is None:
        return {}

    ayan = swe.get_ayanamsa_ut(jd)

    CLASSICAL_PL = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
        'Merc': swe.MERCURY, 'Jup': swe.JUPITER, 'Ven': swe.VENUS,
        'Sat': swe.SATURN, 'Rahu': swe.MEAN_NODE,
    }
    transit_sign_indices = {}
    for nm, pid in CLASSICAL_PL.items():
        try:
            pos, _ = swe.calc_ut(jd, pid)
            lon = (pos[0] - ayan) % 360
            transit_sign_indices[nm] = int(lon / 30)
        except:
            continue
    if 'Rahu' in transit_sign_indices:
        transit_sign_indices['Ketu'] = (transit_sign_indices['Rahu'] + 6) % 12

    transit_moon_sign = transit_sign_indices.get('Moon', 0)

    try:
        composite = compute_composite_score(
            bav, sav, moon_sign_idx, asc_sign_idx,
            transit_sign_indices, transit_moon_sign
        )
        feats = extract_vedha_features(composite)

        natal_sign_idx = natal_lons.get('_sign_indices', {})
        d9_indices = {}
        for pname in ['Sun','Moon','Mars','Merc','Jup','Ven','Sat','Rahu','Ketu']:
            if pname in natal_lons and not pname.startswith('_'):
                lon = natal_lons[pname]
                si = int(lon / 30)
                d9_pos_in_sign = (lon % 30) / (30.0/9.0)
                element_starts = [0, 9, 6, 3]
                element = si % 4
                d9_sign = (element_starts[element] + int(d9_pos_in_sign)) % 12
                d9_indices[pname] = d9_sign

        d9_moon_sidx = d9_indices.get('Moon', 0)
        natal_vedha = compute_natal_vedha(
            natal_sign_idx, moon_sign_idx, d9_indices, d9_moon_sidx
        )
        cross_feats = extract_natal_transit_cross_features(natal_vedha, composite)
        feats.update(cross_feats)

        return feats
    except:
        return {}


def phase4_extract_features(moves, stock_info, natal):
    cache = os.path.join(CACHE_DIR, 'features_v8.pkl')
    if os.path.exists(cache):
        with open(cache,'rb') as f: df = pickle.load(f)
        log(f"Phase 4: Loaded v8 feature matrix ({df.shape}) from cache")
        return df

    log("Phase 4: Extracting features (v8: Comprehensive Gap Fixes)...")

    # Pre-compute natal blueprints (once per stock, not per move)
    log("  Computing natal blueprints for all stocks...")
    natal_blueprints = {}
    for ticker, nlons in natal.items():
        natal_blueprints[ticker] = compute_natal_blueprint(nlons)
    log(f"  Computed {len(natal_blueprints)} natal blueprints")

    rows = []
    vedha_ok = 0; vedha_fail = 0
    for i, m in enumerate(moves):
        if i % 500 == 0: log(f"  Processing move {i}/{len(moves)}...")
        ticker = m['ticker']
        if ticker not in natal: continue
        result = extract_all_features(
            natal[ticker], stock_info[ticker]['ipo'],
            m['start'], stock_info[ticker].get('sector','Unknown')
        )
        if result is None: continue
        feats, transit_lons = result

        # Topic #23: Vedha + Ashtakavarga
        vedha_feats = extract_vedha_topic23(natal[ticker], m['start'])
        if vedha_feats:
            feats.update(vedha_feats)
            vedha_ok += 1
        else:
            vedha_fail += 1

        # UNIVERSAL: Full Natal D1/D9 × Transit ALL Topics
        if ticker in natal_blueprints:
            cross = extract_natal_transit_crossref(
                natal_blueprints[ticker], feats, transit_lons
            )
            feats.update(cross)

            # Topic 31: Panchang cross-reference (natal Panchang fingerprint × transit)
            transit_panch = feats.get('_panchang_raw', {})
            if transit_panch:
                natal_bp = natal_blueprints[ticker]
                panch_cx = extract_panchang_crossref(natal_bp, transit_panch)
                feats.update(panch_cx)

        # Remove internal key
        feats.pop('_panchang_raw', None)

        feats['_ticker'] = ticker
        feats['_return'] = m['return_pct']
        feats['_direction'] = m['direction']
        feats['_sector'] = m.get('sector','Unknown')
        feats['_is_bull'] = 1 if 'BULL' in m['direction'] else 0
        feats['_date'] = m['start']
        rows.append(feats)

    df = pd.DataFrame(rows)
    log(f"  Feature matrix v7: {df.shape} (Vedha OK: {vedha_ok}, fail: {vedha_fail})")
    with open(cache,'wb') as f: pickle.dump(df, f)
    return df


# ═══════════════════════════════════════════════════════════════
# PHASE 5: TOPIC-BY-TOPIC BACKTESTING (EPOCH-DETRENDED)
# ═══════════════════════════════════════════════════════════════
def phase5_topic_testing(df):
    log("Phase 5: Topic-by-topic testing (epoch-bias aware)...")
    results = {}
    target = '_is_bull'
    numeric_cols = [c for c in df.columns if not c.startswith('_') and c not in ['MD','AD']
                    and df[c].dtype in ['int64','float64','int32','float32']]

    # Get year column for detrending
    has_year = '_year' in df.columns

    for col in numeric_cols:
        try:
            vals = df[col].dropna()
            if len(vals) < 50: continue
            bull_vals = df.loc[df[target]==1, col].dropna()
            bear_vals = df.loc[df[target]==0, col].dropna()
            if len(bull_vals) < 20 or len(bear_vals) < 20: continue

            bull_mean = bull_vals.mean()
            bear_mean = bear_vals.mean()
            diff = bull_mean - bear_mean
            pooled_std = np.sqrt((bull_vals.std()**2 + bear_vals.std()**2)/2)
            cohens_d = diff / pooled_std if pooled_std > 0 else 0

            # Hit rate
            if vals.nunique() <= 3:
                br1 = (df.loc[df[col]==1, target].mean()) if (df[col]==1).sum() > 10 else np.nan
                br0 = (df.loc[df[col]==0, target].mean()) if (df[col]==0).sum() > 10 else np.nan
                hr_diff = (br1 - br0) if not (np.isnan(br1) or np.isnan(br0)) else 0
            else:
                hr_diff = df[[col, target]].corr().iloc[0,1]

            # EPOCH-DETRENDED Cohen's d: compute per-year and average
            epoch_d = 0.0
            is_slow = _is_slow_standalone(col)
            if has_year and is_slow:
                year_ds = []
                for yr, grp in df.groupby('_year'):
                    if len(grp) < 30: continue
                    b = grp.loc[grp[target]==1, col].dropna()
                    br = grp.loc[grp[target]==0, col].dropna()
                    if len(b) < 10 or len(br) < 10: continue
                    ps = np.sqrt((b.std()**2 + br.std()**2)/2)
                    if ps > 0: year_ds.append((b.mean()-br.mean())/ps)
                epoch_d = np.mean(year_ds) if year_ds else 0.0

            results[col] = {
                'bull_mean': round(bull_mean, 4),
                'bear_mean': round(bear_mean, 4),
                'diff': round(diff, 4),
                'cohens_d': round(cohens_d, 4),
                'epoch_d': round(epoch_d, 4),
                'hr_diff': round(hr_diff, 4),
                'n_samples': len(vals),
                'is_slow_standalone': is_slow,
                'effective_d': round(epoch_d if is_slow else cohens_d, 4)
            }
        except:
            continue

    # Sort by EFFECTIVE d (epoch-detrended for slow, raw for fast)
    results_sorted = sorted(results.items(),
                           key=lambda x: abs(x[1]['effective_d']), reverse=True)
    top_d = results_sorted[0][1]['effective_d'] if results_sorted else 'N/A'
    log(f"  Tested {len(results)} features, top effective_d: {top_d}")
    return dict(results_sorted)


# ═══════════════════════════════════════════════════════════════
# PHASE 6: WALK-FORWARD ANALYSIS (EXCLUDE EPOCH-BIASED)
# ═══════════════════════════════════════════════════════════════
def phase6_wfa(df):
    log("Phase 6: Walk-Forward Analysis (epoch-bias controlled)...")
    try:
        from xgboost import XGBClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
    except ImportError:
        log("  XGBoost/sklearn not available, skipping WFA")
        return {'error': 'XGBoost not installed'}

    target = '_is_bull'
    feat_cols = [c for c in df.columns if not c.startswith('_') and c not in ['MD','AD']
                 and df[c].dtype in ['int64','float64','int32','float32']]

    # Exclude very-slow standalone features from WFA
    feat_cols = [c for c in feat_cols if not _is_slow_standalone(c)]
    feat_cols = [c for c in feat_cols if df[c].isna().mean() < 0.5]

    log(f"  Using {len(feat_cols)} features (excluded slow-planet standalone)")

    X = df[feat_cols].fillna(0)
    y = df[target].fillna(0).astype(int)

    n = len(X)
    fold_size = n // 5
    results = []
    imp = []

    for fold in range(4):
        train_end = fold_size * (fold + 2)
        test_start = train_end
        test_end = min(train_end + fold_size, n)
        if test_end <= test_start: break

        X_tr, y_tr = X.iloc[:train_end], y.iloc[:train_end]
        X_te, y_te = X.iloc[test_start:test_end], y.iloc[test_start:test_end]
        if len(y_tr.unique()) < 2 or len(y_te) < 20: continue

        model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1,
                              use_label_encoder=False, eval_metric='logloss', verbosity=0)
        model.fit(X_tr, y_tr)
        pred = model.predict(X_te)
        proba = model.predict_proba(X_te)[:,1]

        acc = accuracy_score(y_te, pred)
        try: auc = roc_auc_score(y_te, proba)
        except: auc = 0.5
        f1 = f1_score(y_te, pred, zero_division=0)

        results.append({
            'fold': fold+1, 'train_size': len(X_tr), 'test_size': len(X_te),
            'accuracy': round(acc,4), 'auc': round(auc,4), 'f1': round(f1,4)
        })

        if fold == len(range(4))-1 or fold == 3:
            imp = sorted(zip(feat_cols, model.feature_importances_),
                        key=lambda x: x[1], reverse=True)[:30]

    avg_acc = np.mean([r['accuracy'] for r in results]) if results else 0
    avg_auc = np.mean([r['auc'] for r in results]) if results else 0
    log(f"  WFA: {len(results)} folds, Avg Accuracy={avg_acc:.4f}, Avg AUC={avg_auc:.4f}")
    return {'folds': results, 'avg_acc': round(avg_acc,4), 'avg_auc': round(avg_auc,4),
            'top_features': imp}


# ═══════════════════════════════════════════════════════════════
# PHASE 7: MONTE CARLO (ON EFFECTIVE FEATURES ONLY)
# ═══════════════════════════════════════════════════════════════
def phase7_monte_carlo(df, topic_results, n_perms=500):
    log(f"Phase 7: Monte Carlo simulation ({n_perms} permutations)...")
    target = '_is_bull'
    y = df[target].values

    # Only MC-test features that aren't epoch-biased standalone
    top_feats = [f for f,d in list(topic_results.items())[:80]
                 if not d.get('is_slow_standalone', False)][:50]
    mc_results = {}

    for fi, feat in enumerate(top_feats):
        if fi % 10 == 0: log(f"  MC testing feature {fi}/{len(top_feats)}...")
        if feat not in df.columns: continue
        x = df[feat].fillna(0).values
        actual_corr = np.abs(np.corrcoef(x, y)[0,1]) if np.std(x) > 0 else 0

        perm_better = 0
        for _ in range(n_perms):
            y_shuf = np.random.permutation(y)
            perm_corr = np.abs(np.corrcoef(x, y_shuf)[0,1]) if np.std(x) > 0 else 0
            if perm_corr >= actual_corr:
                perm_better += 1

        p_value = perm_better / n_perms
        mc_results[feat] = {
            'actual_corr': round(actual_corr, 5),
            'p_value': round(p_value, 4),
            'significant_05': p_value < 0.05,
            'significant_01': p_value < 0.01,
            'significant_001': p_value < 0.001
        }

    sig_05 = sum(1 for v in mc_results.values() if v['significant_05'])
    sig_01 = sum(1 for v in mc_results.values() if v['significant_01'])
    log(f"  MC results: {sig_05}/{len(mc_results)} at p<0.05, {sig_01} at p<0.01")
    return mc_results


# ═══════════════════════════════════════════════════════════════
# PHASE 8: COMPREHENSIVE REPORT (EPOCH-CORRECTED)
# ═══════════════════════════════════════════════════════════════
def phase8_report(df, topic_results, wfa_results, mc_results, stock_info):
    log("Phase 8: Generating v2 report (epoch-bias corrected)...")
    lines = []
    lines.append("# Institution-Level Astrological Backtesting Report (v2: Epoch-Corrected)")
    lines.append(f"\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("> [!IMPORTANT]")
    lines.append("> Slow-planet standalone features (Uranus/Neptune/Pluto 7-32yr per nak,")
    lines.append("> Saturn/Rahu/Ketu 9mo-1yr) are epoch-detrended. Their effective_d uses")
    lines.append("> per-year averaging to remove market-regime correlation.\n")

    # Universe Stats
    n_stocks = df['_ticker'].nunique() if '_ticker' in df.columns else 0
    n_bull = (df['_is_bull']==1).sum() if '_is_bull' in df.columns else 0
    n_bear = (df['_is_bull']==0).sum() if '_is_bull' in df.columns else 0
    lines.append("## Universe Statistics\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Stocks | {n_stocks} |")
    lines.append(f"| Total Significant Moves | {len(df)} |")
    lines.append(f"| Bull Moves | {n_bull} |")
    lines.append(f"| Bear Moves | {n_bear} |")
    lines.append(f"| Feature Columns | {len([c for c in df.columns if not c.startswith('_')])} |\n")

    # Sector breakdown
    if '_sector' in df.columns:
        lines.append("### Sector Distribution\n")
        lines.append(f"| Sector | Count | Bull% |")
        lines.append(f"|--------|-------|-------|")
        for sec, grp in df.groupby('_sector'):
            bp = grp['_is_bull'].mean()*100 if '_is_bull' in grp.columns else 0
            lines.append(f"| {sec} | {len(grp)} | {bp:.1f}% |")

    # Top features — FAST PLANET ONLY (reliable)
    fast_feats = [(f,d) for f,d in topic_results.items() if not d.get('is_slow_standalone',False)]
    lines.append("\n## Top 30 Reliable Features (Fast-Planet / Interaction / Epoch-Detrended)\n")
    lines.append("> These exclude standalone slow-planet nak/sign features that are epoch-biased.\n")
    lines.append(f"| Rank | Feature | Bull Mean | Bear Mean | Effective d | Type |")
    lines.append(f"|------|---------|-----------|-----------|-------------|------|")
    for rank, (feat, data) in enumerate(fast_feats[:30], 1):
        ftype = 'IX' if feat.startswith(('IX_','FF_')) else 'FAST' if any(feat.startswith(p+'_') for p in FAST) else 'MIXED'
        lines.append(f"| {rank} | {feat} | {data['bull_mean']} | {data['bear_mean']} | {data['effective_d']:+.4f} | {ftype} |")

    # Slow planet features (with epoch correction)
    slow_feats = [(f,d) for f,d in topic_results.items() if d.get('is_slow_standalone',False)]
    if slow_feats:
        lines.append("\n## Slow-Planet Features (Epoch-Detrended)\n")
        lines.append("> [!WARNING]")
        lines.append("> These features use per-year averaging. Raw d may be misleading.\n")
        lines.append(f"| Rank | Feature | Raw d | Epoch d | Verdict |")
        lines.append(f"|------|---------|-------|---------|---------|")
        for rank, (feat, data) in enumerate(slow_feats[:20], 1):
            verdict = '✅ Real' if abs(data['epoch_d']) > 0.10 else '⚠️ Weak' if abs(data['epoch_d']) > 0.05 else '❌ Spurious'
            lines.append(f"| {rank} | {feat} | {data['cohens_d']:+.4f} | {data['epoch_d']:+.4f} | {verdict} |")

    # Topic-grouped analysis
    lines.append("\n## Analysis by Topic\n")
    topic_groups = {
        'T1-Volatility (Moon-Merc-Sun)': [c for c in topic_results if c.startswith(('Vol_','D9_Moon','Volatility_'))],
        'T2-Applying/Separating': [c for c in topic_results if c.startswith(('Apply_','Separ_'))],
        'T3-Trend Reversal Pairs': [c for c in topic_results if c.startswith('TR_')],
        'T4-MercVen Aspects': [c for c in topic_results if c.startswith('MercVen_')],
        'T5-Moving Signs': [c for c in topic_results if 'Moving' in c and not c.startswith(('IX_','FF_'))],
        'T6-Max Elongation': [c for c in topic_results if c.startswith('MaxElong_')],
        'T7-Sector Planets': [c for c in topic_results if c.endswith('_IsSec')],
        'T8/9-Dasha': [c for c in topic_results if c.startswith('MD_')],
        'T10-Health Grid': [c for c in topic_results if c.startswith('HealthGrid_')],
        'T11-Pushkar Nav': [c for c in topic_results if ('PushNav' in c or 'PushD9V' in c) and not c.startswith('IX_')],
        'T12-Pushkar Bhaga': [c for c in topic_results if ('PushBhaga' in c or 'BeneficPB' in c) and not c.startswith('IX_')],
        'T13-Vargottama': [c for c in topic_results if ('Vargottama' in c or 'PushVarg' in c) and not c.startswith('IX_')],
        'T14-Nakshatra Quality': [c for c in topic_results if ('NegNak' in c or 'PracPaw' in c) and not c.startswith('IX_')],
        'T15-Latta/Vedha': [c for c in topic_results if c.startswith('Latta_')],
        'T17/18-Conjunction Combos': [c for c in topic_results if c.startswith(('ConjPos','ConjPush'))],
        'NEW: Fast×Slow Interactions': [c for c in topic_results if c.startswith('IX_')],
        'NEW: Fast×Fast Interactions': [c for c in topic_results if c.startswith('FF_')],
        'NEW: Fast-Planet Aggregates': [c for c in topic_results if c.startswith('Fast_')],
        'T23: Vedha+Ashtakavarga': [c for c in topic_results if c.startswith(('Vedha_','BAV_','SAV_','NatalV_','NX_'))],
        'T24: Natal Promise×Transit': [c for c in topic_results if c.startswith('BP_')],
    }

    for topic_name, cols in topic_groups.items():
        if not cols: continue
        avg_d = np.mean([abs(topic_results[c]['effective_d']) for c in cols if c in topic_results])
        best = max(cols, key=lambda c: abs(topic_results.get(c,{}).get('effective_d',0)))
        best_d = topic_results.get(best,{}).get('effective_d',0)
        n_sig = sum(1 for c in cols if c in mc_results and mc_results[c].get('significant_05',False))
        lines.append(f"### {topic_name}")
        lines.append(f"- Features tested: {len(cols)}")
        lines.append(f"- Avg |effective d|: {avg_d:.4f}")
        lines.append(f"- Best: `{best}` (d={best_d:+.4f})")
        lines.append(f"- MC significant (p<0.05): {n_sig}/{len(cols)}\n")

    # WFA Results
    lines.append("\n## Walk-Forward Analysis (Slow-Planet Standalone EXCLUDED)\n")
    if 'folds' in wfa_results:
        lines.append(f"| Fold | Train | Test | Accuracy | AUC | F1 |")
        lines.append(f"|------|-------|------|----------|-----|-----|")
        for fold in wfa_results['folds']:
            lines.append(f"| {fold['fold']} | {fold['train_size']} | {fold['test_size']} | {fold['accuracy']:.4f} | {fold['auc']:.4f} | {fold['f1']:.4f} |")
        lines.append(f"\n**Average Accuracy: {wfa_results['avg_acc']:.4f}, Average AUC: {wfa_results['avg_auc']:.4f}**\n")
        if wfa_results.get('top_features'):
            lines.append("### Top 15 WFA Feature Importance\n")
            lines.append(f"| Rank | Feature | Importance |")
            lines.append(f"|------|---------|------------|")
            for rank, (feat, importance) in enumerate(wfa_results['top_features'][:15], 1):
                lines.append(f"| {rank} | {feat} | {importance:.4f} |")

    # Monte Carlo Results
    lines.append("\n## Monte Carlo (Fast/Interaction Features Only)\n")
    sig_feats = [(f,d) for f,d in mc_results.items() if d['significant_05']]
    sig_feats.sort(key=lambda x: x[1]['p_value'])
    lines.append(f"**{len(sig_feats)}/{len(mc_results)} features significant (p<0.05)**\n")
    if sig_feats:
        lines.append(f"| Feature | Corr | p-value | p<0.01 | p<0.001 |")
        lines.append(f"|---------|------|---------|--------|---------|")
        for feat, data in sig_feats[:25]:
            lines.append(f"| {feat} | {data['actual_corr']:.5f} | {data['p_value']:.4f} | {'✅' if data['significant_01'] else '❌'} | {'✅' if data['significant_001'] else '❌'} |")

    lines.append("\n## Actionable Insights\n")
    lines.append("> [!IMPORTANT]")
    lines.append("> Results above are epoch-corrected. Only fast-planet and interaction")
    lines.append("> features are in the reliable rankings. Slow-planet standalone features")
    lines.append("> are shown separately with per-year detrended effect sizes.\n")

    report_text = "\n".join(lines)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_text)
    log(f"  Report v2 saved to {REPORT_PATH}")
    return report_text


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def run_analysis_phases(moves, stock_info, natal):
    df = phase4_extract_features(moves, stock_info, natal)
    topic_results = phase5_topic_testing(df)
    wfa_results = phase6_wfa(df)
    mc_results = phase7_monte_carlo(df, topic_results, n_perms=500)
    report = phase8_report(df, topic_results, wfa_results, mc_results, stock_info)

    print("\n" + "="*80)
    print("BACKTESTING COMPLETE (v2: Epoch-Corrected)")
    print("="*80)
    print(f"Report: {REPORT_PATH}")
    return topic_results, wfa_results, mc_results
