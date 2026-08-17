"""
Feature Matrix Generator (Phase 0.7) - Full Production Multi-Core Run
======================================================================
Generates the master feature matrix for ALL 548 tickers.
Runs with multiprocessing (8 workers) for maximum CPU throughput.
Idempotent: skips any ticker that already has a parquet in features_partitioned.

DST Fix: All timestamps use pytz US/Eastern 9:30 AM → UTC to ensure
         correct Lahiri sidereal positions regardless of DST state.
"""
import sqlite3
import json
import time
import os
import glob
import multiprocessing
from datetime import datetime, timezone
import pytz
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import sys

sys.path.append(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch")
sys.path.append(r"E:\Python\Learn")

MARKET_DATA_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\market_data"
OUTPUT_DIR      = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
COMPILED_RULES_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\compiled_rules.json"
DB_PATH         = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_natal_charts.db"
SECTOR_CSV      = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\sector_tags.csv"

N_WORKERS = 8  # Leave 4 cores free for OS + other processes

# ─────────────────────────────────────────────────────────────────────────────
# CHECKPOINT: Which tickers already have parquets?
# ─────────────────────────────────────────────────────────────────────────────
def get_completed_tickers():
    done = set()
    for td in glob.glob(os.path.join(OUTPUT_DIR, "ticker=*")):
        ticker = os.path.basename(td).replace("ticker=", "")
        # Make sure at least one parquet file is inside
        if glob.glob(os.path.join(td, "**", "*.parquet"), recursive=True):
            done.add(ticker)
    return done


def get_all_tickers():
    tickers = []
    for f in glob.glob(os.path.join(MARKET_DATA_DIR, "*_ohlcv.parquet")):
        t = os.path.basename(f).replace("_ohlcv.parquet", "")
        tickers.append(t)
    return sorted(tickers)


def load_compiled_rules():
    with open(COMPILED_RULES_PATH, "r") as f:
        rules_dict = json.load(f)
    funcs = {}
    for name, expr in rules_dict.items():
        try:
            funcs[name] = compile(expr, "<string>", "eval")
        except Exception as e:
            print(f"Error compiling rule {name}: {e}")
    return funcs


# ─────────────────────────────────────────────────────────────────────────────
# WORKER FUNCTION (runs in subprocess, so no shared state issues)
# ─────────────────────────────────────────────────────────────────────────────
def worker_process_ticker(ticker):
    """Top-level function for multiprocessing. Must be importable."""
    try:
        import swisseph as swe
        from ephemeris_engine import compute_all_features
        from transit_engine import StockAstroEngine
        from institution_backtest_analysis import (
            extract_all_features, compute_natal_blueprint,
            extract_natal_transit_crossref, extract_vedha_topic23
        )

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        engine = StockAstroEngine()
        rule_funcs = load_compiled_rules()
        sky_cache = {}

        result = process_ticker(ticker, engine, rule_funcs, sky_cache)
        return (ticker, result, None)
    except Exception as exc:
        import traceback
        return (ticker, None, traceback.format_exc())


def process_ticker(ticker, engine, rule_funcs, sky_cache):
    """Processes a single ticker. Returns number of rows written."""
    import swisseph as swe
    from ephemeris_engine import compute_all_features
    from institution_backtest_analysis import (
        extract_all_features, compute_natal_blueprint,
        extract_natal_transit_crossref, extract_vedha_topic23
    )

    md_path = os.path.join(MARKET_DATA_DIR, f"{ticker}_ohlcv.parquet")
    if not os.path.exists(md_path):
        print(f"  [{ticker}] No market data. Skipping.")
        return None

    md_df = pd.read_parquet(md_path)
    dates = md_df['Date'].tolist()

    # ── Natal Blueprint ──────────────────────────────────────────────────────
    try:
        n_lons = {}
        if "planets" in engine.natal_cache[ticker]["natal"]:
            for p, data in engine.natal_cache[ticker]["natal"]["planets"].items():
                n_lons[p] = data.get("longitude", 0.0)

        ipo_str = engine.natal_cache[ticker]["ipo_date"]
        dt_ipo = datetime.strptime(ipo_str, "%Y-%m-%d")
        dt_ipo_et = pytz.timezone("US/Eastern").localize(dt_ipo.replace(hour=9, minute=30))
        dt_ipo_utc = dt_ipo_et.astimezone(timezone.utc)
        n_lons['_jd'] = swe.julday(
            dt_ipo_utc.year, dt_ipo_utc.month, dt_ipo_utc.day,
            dt_ipo_utc.hour + dt_ipo_utc.minute / 60.0
        )

        c = engine.conn.cursor()
        c.execute("SELECT ascendant_degree, lagna_sign, moon_nakshatra FROM stocks WHERE ticker=?", (ticker,))
        res = c.fetchone()
        n_lons['_asc'] = res[0] if res else 0.0
        n_lons['_moon_nak_i'] = engine.natal_cache[ticker]["moon_nak"]

        # BAV/SAV
        try:
            sav_row = c.execute(
                "SELECT sign_0,sign_1,sign_2,sign_3,sign_4,sign_5,sign_6,sign_7,sign_8,sign_9,sign_10,sign_11 "
                "FROM natal_sav WHERE ticker=?", (ticker,)
            ).fetchone()
            if sav_row:
                n_lons['_sav'] = list(sav_row)
                bav_dict = {}
                for bav_row in c.execute(
                    "SELECT planet,sign_0,sign_1,sign_2,sign_3,sign_4,sign_5,sign_6,sign_7,sign_8,sign_9,sign_10,sign_11 "
                    "FROM natal_bav WHERE ticker=?", (ticker,)
                ).fetchall():
                    bav_dict[bav_row[0]] = list(bav_row[1:])
                n_lons['_bav'] = bav_dict
                n_lons['_moon_sign_idx'] = int(n_lons.get('Moon', 0) / 30)
                asc_sign = res[1] if res and res[1] is not None else int(n_lons['_asc'] / 30)
                n_lons['_asc_sign_idx'] = asc_sign
        except Exception:
            pass

        # Shadbala
        shadbala_feats = {}
        try:
            for sb_row in c.execute(
                "SELECT planet, sthana_bala, dig_bala, chesta_bala, total_shadbala "
                "FROM natal_shadbala WHERE ticker=?", (ticker,)
            ).fetchall():
                p = sb_row[0]
                shadbala_feats[f'SB_{p}_sthana'] = sb_row[1]
                shadbala_feats[f'SB_{p}_dig']    = sb_row[2]
                shadbala_feats[f'SB_{p}_chesta'] = sb_row[3]
                shadbala_feats[f'SB_{p}_total']  = sb_row[4]
        except Exception:
            pass

        # Karakas
        karaka_feats = {}
        try:
            for kk_row in c.execute(
                "SELECT karaka, planet FROM natal_karakas WHERE ticker=?", (ticker,)
            ).fetchall():
                karaka_feats[f'natal_karaka_{kk_row[0]}'] = kk_row[1]
        except Exception:
            pass

        # Ghatak
        ghatak_feats = {}
        try:
            gh_row = c.execute(
                "SELECT bad_day, bad_nakshatra, bad_rashi, bad_tithi_json, bad_lagna "
                "FROM natal_ghatak WHERE ticker=?", (ticker,)
            ).fetchone()
            if gh_row:
                ghatak_feats['_ghatak_bad_day']   = gh_row[0]
                ghatak_feats['_ghatak_bad_nak']   = gh_row[1]
                ghatak_feats['_ghatak_bad_rashi'] = gh_row[2]
                ghatak_feats['_ghatak_bad_tithi'] = json.loads(gh_row[3]) if gh_row[3] else []
                ghatak_feats['_ghatak_bad_lagna'] = gh_row[4]
        except Exception:
            pass

        # Sector
        c.execute("SELECT sector FROM sector_tags WHERE ticker=?", (ticker,))
        res2 = c.fetchone()
        sector = res2[0] if res2 else "Unknown"

        bp = compute_natal_blueprint(n_lons)

    except Exception as e:
        print(f"  [{ticker}] Natal blueprint error: {e}")
        return None

    # ── Per-day processing ───────────────────────────────────────────────────
    all_rows = []
    for dt in dates:
        local_dt = pytz.timezone("US/Eastern").localize(
            datetime(dt.year, dt.month, dt.day, 9, 30)
        )
        dt_utc = local_dt.astimezone(timezone.utc)
        date_str = dt_utc.strftime("%Y-%m-%d %H:%M")

        if date_str not in sky_cache:
            sky_cache[date_str] = compute_all_features(dt_utc)
        sky = sky_cache[date_str]

        stock_features = engine.compute_stock_features(dt_utc, ticker, sky)

        try:
            feats, tlons = extract_all_features(n_lons, ipo_str, dt_utc, sector)
            cx = extract_natal_transit_crossref(bp, feats, tlons)
            ml_features = {**feats, **bp, **cx}
            ml_features.pop('_panchang_raw', None)
        except Exception:
            ml_features = {}

        try:
            vedha_feats = extract_vedha_topic23(n_lons, date_str)
            if vedha_feats:
                ml_features.update(vedha_feats)
        except Exception:
            pass

        ml_features.update(shadbala_feats)
        ml_features.update(karaka_feats)

        if ghatak_feats:
            vedic_day = (dt_utc.weekday() + 1) % 7
            ml_features['ghatak_bad_day']   = 1 if vedic_day == ghatak_feats.get('_ghatak_bad_day', -1) else 0
            transit_moon_nak  = sky.get('Moon_nakshatra', -1)
            transit_moon_sign = sky.get('Moon_sign', -1)
            if isinstance(transit_moon_nak, (int, float)):
                ml_features['ghatak_bad_nak']   = 1 if int(transit_moon_nak)  == ghatak_feats.get('_ghatak_bad_nak', -1)   else 0
            if isinstance(transit_moon_sign, (int, float)):
                ml_features['ghatak_bad_rashi'] = 1 if int(transit_moon_sign) == ghatak_feats.get('_ghatak_bad_rashi', -1) else 0
            ml_features['ghatak_score'] = (
                ml_features.get('ghatak_bad_day', 0) +
                ml_features.get('ghatak_bad_nak', 0) +
                ml_features.get('ghatak_bad_rashi', 0)
            )

        combined = {**sky, **stock_features, **ml_features}

        rule_evals = {}
        local_vars = {"features": combined}
        for rule_name, code_obj in rule_funcs.items():
            try:
                rule_evals[f"rule_{rule_name}"] = 1.0 if eval(code_obj, {"__builtins__": None}, local_vars) else 0.0
            except Exception:
                rule_evals[f"rule_{rule_name}"] = 0.0

        row = {"date": dt_utc, "ticker": ticker, **combined, **rule_evals}
        all_rows.append(row)

    if not all_rows:
        return 0

    df = pd.DataFrame(all_rows)

    # Stationarity: sin/cos of longitudes
    for col in [c for c in df.columns if "longitude" in c]:
        rad = np.radians(df[col])
        df[f"{col}_sin"] = np.sin(rad)
        df[f"{col}_cos"] = np.cos(rad)

    # CRITICAL BUG FIX #13: Unwrap phase angles
    if "moon_phase" in df.columns:
        # moon_phase is 0 to 1. Convert to radians, unwrap, convert back.
        rad_phase = df["moon_phase"] * 2 * np.pi
        df["moon_phase_unwrapped"] = np.unwrap(rad_phase) / (2 * np.pi)
        
    df['year'] = df['date'].dt.year

    table = pa.Table.from_pandas(df)
    pq.write_to_dataset(table, root_path=OUTPUT_DIR, partition_cols=['ticker', 'year'])

    return len(df)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_matrix():
    all_tickers  = get_all_tickers()
    done_tickers = get_completed_tickers()
    remaining    = [t for t in all_tickers if t not in done_tickers]

    print(f"Total tickers:     {len(all_tickers)}")
    print(f"Already completed: {len(done_tickers)}")
    print(f"Remaining:         {len(remaining)}")
    print(f"Workers:           {N_WORKERS}")
    print("=" * 60)

    if not remaining:
        print("All tickers already completed. Nothing to do.")
        return

    t_start = time.perf_counter()
    total_rows = 0
    completed  = 0
    failed     = []

    with multiprocessing.Pool(processes=N_WORKERS) as pool:
        for ticker, rows, err in pool.imap_unordered(worker_process_ticker, remaining):
            completed += 1
            if err:
                failed.append(ticker)
                print(f"[{completed}/{len(remaining)}] FAIL {ticker}: {err[:120]}")
            else:
                total_rows += rows or 0
                elapsed = (time.perf_counter() - t_start) / 60
                eta = (elapsed / completed) * (len(remaining) - completed) if completed > 0 else 0
                print(f"[{completed}/{len(remaining)}] OK {ticker} ({rows or 0} rows) | {elapsed:.1f}m elapsed | ETA {eta:.1f}m")

    elapsed = time.perf_counter() - t_start
    print("=" * 60)
    print("MATRIX GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total Rows:   {total_rows:,}")
    print(f"Total Time:   {elapsed / 60:.1f} mins")
    print(f"Failed:       {len(failed)} — {failed}")
    print(f"Output:       {OUTPUT_DIR}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    generate_matrix()
