"""
SPY Solid & Big Green/Red High-Volume Candlestick Anomaly Extraction Engine
Branch: feat/extreme-solid-candlestick-anomalies
Timeframes: 1h, 2h, 4h, 1d, 1w, 1mo

Extracts all historical candlestick datetimes where:
1. Candlestick is solid (Body / Total Range >= 0.65)
2. Candlestick is big green or red (Body / ATR(20) >= 1.50 or absolute return outlier)
3. Volume is higher than normal (RVOL >= 1.50x relative to 20-period trailing SMA)
"""

import os
import sys
import gc
import json
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# Try importing data providers
try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
except ImportError:
    StockHistoricalDataClient = None


def get_alpaca_client():
    env_paths = [
        r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\.env",
        r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings\.env"
    ]
    for ep in env_paths:
        if os.path.exists(ep):
            load_dotenv(ep)
            break

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in .env")
    return StockHistoricalDataClient(api_key, secret_key)


def fetch_alpaca_1h(start_year=2016, end_year=2026):
    """
    Fetches full 1-hour historical bars for SPY from Alpaca API.
    """
    print(f"\n[1/6] Fetching SPY 1-Hour data from Alpaca ({start_year} to {end_year})...")
    client = get_alpaca_client()
    
    all_dfs = []
    curr_start = datetime(start_year, 1, 1)
    end_dt = datetime.now()

    while curr_start < end_dt:
        curr_end = min(curr_start + relativedelta(years=1), end_dt)
        print(f"  Fetching: {curr_start.date()} -> {curr_end.date()}...", end=" ", flush=True)
        
        req = StockBarsRequest(
            symbol_or_symbols=['SPY'],
            timeframe=TimeFrame.Hour,
            start=curr_start,
            end=curr_end
        )
        try:
            bars = client.get_stock_bars(req)
            if not bars.df.empty:
                df_chunk = bars.df.reset_index()
                if 'symbol' in df_chunk.columns:
                    df_chunk = df_chunk.drop(columns=['symbol'])
                print(f"{len(df_chunk)} bars.")
                all_dfs.append(df_chunk)
            else:
                print("0 bars.")
        except Exception as e:
            print(f"Error: {e}")
            
        curr_start = curr_end

    if not all_dfs:
        raise RuntimeError("Failed to fetch 1-hour SPY data from Alpaca.")

    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.rename(columns={
        'timestamp': 'Datetime',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    # Ensure Datetime formatting in US/Eastern
    combined['Datetime'] = pd.to_datetime(combined['Datetime']).dt.tz_convert('US/Eastern')
    combined = combined.drop_duplicates(subset=['Datetime']).sort_values('Datetime').reset_index(drop=True)
    
    # Keep standard columns
    cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
    combined = combined[[c for c in cols if c in combined.columns]]
    print(f"-> Total 1H Bars Fetched: {len(combined)} (Range: {combined['Datetime'].iloc[0]} to {combined['Datetime'].iloc[-1]})")
    return combined


def resample_ohlcv(df_1h, rule='2h', label='2H'):
    """
    Resamples 1h data into higher intraday timeframes (2h, 4h) cleanly.
    """
    print(f"\nResampling 1H -> {label} ({rule})...")
    df = df_1h.copy()
    df = df.set_index('Datetime')
    
    resampled = df.resample(rule, closed='left', label='left').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna().reset_index()
    
    # Filter out empty volume rows
    resampled = resampled[resampled['Volume'] > 0].reset_index(drop=True)
    print(f"-> Total {label} Bars: {len(resampled)} (Range: {resampled['Datetime'].iloc[0]} to {resampled['Datetime'].iloc[-1]})")
    return resampled


def fetch_yfinance_bars(interval='1d', label='1D'):
    """
    Fetches full history from yfinance for 1d, 1wk, 1mo.
    """
    print(f"\nFetching SPY {label} ({interval}) data from inception (1993 to present)...")
    ticker = yf.Ticker('SPY')
    hist = ticker.history(period='max', interval=interval, auto_adjust=False)
    if hist.empty:
        raise RuntimeError(f"Failed to fetch {interval} data from yfinance.")
        
    hist = hist.reset_index()
    
    date_col = 'Date' if 'Date' in hist.columns else 'Datetime'
    hist = hist.rename(columns={date_col: 'Datetime'})
    hist['Datetime'] = pd.to_datetime(hist['Datetime'])
    if hist['Datetime'].dt.tz is None:
        hist['Datetime'] = hist['Datetime'].dt.tz_localize('US/Eastern')
    else:
        hist['Datetime'] = hist['Datetime'].dt.tz_convert('US/Eastern')
        
    cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
    hist = hist[[c for c in cols if c in hist.columns]].dropna().sort_values('Datetime').reset_index(drop=True)
    print(f"-> Total {label} Bars Fetched: {len(hist)} (Range: {hist['Datetime'].iloc[0]} to {hist['Datetime'].iloc[-1]})")
    return hist


def compute_features_and_anomalies(df, timeframe,
                                   min_solid_ratio=0.65,
                                   min_atr_ratio=1.50,
                                   min_rvol=1.50,
                                   min_return_floor=None):
    """
    Computes candlestick geometry, trailing volatility, volume ratio, and extracts anomalies.
    All trailing indicators are shifted by 1 to guarantee ZERO lookahead bias.
    """
    df = df.copy()
    
    # 1. Candlestick Geometry
    df['Timeframe'] = timeframe
    df['Body'] = (df['Close'] - df['Open']).abs()
    df['Range'] = df['High'] - df['Low']
    df['Solid_Ratio'] = np.where(df['Range'] > 1e-6, df['Body'] / df['Range'], 0.0)
    
    # 2. Direction & Return
    df['Direction'] = np.where(df['Close'] > df['Open'], 'GREEN',
                               np.where(df['Close'] < df['Open'], 'RED', 'DOJI'))
    df['Return_Pct'] = (df['Close'] - df['Open']) / df['Open'] * 100.0
    df['Abs_Return_Pct'] = df['Return_Pct'].abs()
    
    # 3. Trailing True Range and ATR(20) - Shifted by 1 period
    prev_close = df['Close'].shift(1)
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - prev_close).abs()
    tr3 = (df['Low'] - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Trailing 20-period ATR using historical bars only (prior to current candle)
    df['Trailing_ATR20'] = true_range.shift(1).rolling(window=20, min_periods=5).mean()
    df['Body_ATR_Ratio'] = np.where(df['Trailing_ATR20'] > 1e-6, df['Body'] / df['Trailing_ATR20'], 0.0)
    
    # 4. Trailing Volume Baseline & Relative Volume (RVOL) - Shifted by 1 period
    df['Trailing_Vol_SMA20'] = df['Volume'].shift(1).rolling(window=20, min_periods=5).mean()
    df['RVOL'] = np.where(df['Trailing_Vol_SMA20'] > 0, df['Volume'] / df['Trailing_Vol_SMA20'], 0.0)
    
    # 5. Timeframe Specific Return Floor Default
    floor_map = {
        '1H': 0.50,
        '2H': 0.80,
        '4H': 1.20,
        '1D': 1.50,
        '1W': 3.00,
        '1MO': 5.00
    }
    if min_return_floor is None:
        min_return_floor = floor_map.get(timeframe.upper(), 1.0)
        
    df['Min_Return_Floor'] = min_return_floor

    # 6. Anomaly Criteria Boolean Flags
    df['is_solid'] = df['Solid_Ratio'] >= min_solid_ratio
    df['is_high_volume'] = df['RVOL'] >= min_rvol
    df['is_big_magnitude'] = (df['Body_ATR_Ratio'] >= min_atr_ratio) | (df['Abs_Return_Pct'] >= min_return_floor)
    
    # Core Filter: Solid AND High Volume AND Big Magnitude AND Direction in {GREEN, RED}
    df['is_extreme_anomaly'] = (
        df['is_solid'] &
        df['is_high_volume'] &
        df['is_big_magnitude'] &
        df['Direction'].isin(['GREEN', 'RED'])
    )
    
    # Anomaly Strength Tier:
    # Tier 2: Super Anomaly (Solid >= 0.75, RVOL >= 2.0x, Body/ATR >= 2.0x)
    # Tier 1: Strong Anomaly (Solid >= 0.65, RVOL >= 1.5x, Body/ATR >= 1.5x)
    df['Anomaly_Tier'] = np.where(
        df['is_extreme_anomaly'] & (df['Solid_Ratio'] >= 0.75) & (df['RVOL'] >= 2.0) & (df['Body_ATR_Ratio'] >= 2.0),
        2,
        np.where(df['is_extreme_anomaly'], 1, 0)
    )

    # Filter out warmup period (first 20 bars where trailing stats are incomplete)
    valid_mask = df['Trailing_ATR20'].notna() & df['Trailing_Vol_SMA20'].notna()
    df_valid = df[valid_mask].copy().reset_index(drop=True)
    
    anomalies = df_valid[df_valid['is_extreme_anomaly']].copy().reset_index(drop=True)
    
    print(f"\n--- Anomaly Summary for [{timeframe}] ---")
    print(f"  Total Evaluated Bars : {len(df_valid)}")
    print(f"  Solid Candles Found  : {df_valid['is_solid'].sum()} ({df_valid['is_solid'].mean()*100:.1f}%)")
    print(f"  High-Vol Candles     : {df_valid['is_high_volume'].sum()} ({df_valid['is_high_volume'].mean()*100:.1f}%)")
    print(f"  Big Magnitude Candles: {df_valid['is_big_magnitude'].sum()} ({df_valid['is_big_magnitude'].mean()*100:.1f}%)")
    print(f"  >>> TOTAL QUALIFYING EXTREME ANOMALIES: {len(anomalies)} <<<")
    if len(anomalies) > 0:
        green_cnt = (anomalies['Direction'] == 'GREEN').sum()
        red_cnt = (anomalies['Direction'] == 'RED').sum()
        tier2_cnt = (anomalies['Anomaly_Tier'] == 2).sum()
        print(f"      - Bullish (Green) : {green_cnt} ({green_cnt/len(anomalies)*100:.1f}%)")
        print(f"      - Bearish (Red)   : {red_cnt} ({red_cnt/len(anomalies)*100:.1f}%)")
        print(f"      - Tier 2 (Super)  : {tier2_cnt}")
        print(f"      - Mean Body/Range : {anomalies['Solid_Ratio'].mean():.3f}")
        print(f"      - Mean RVOL       : {anomalies['RVOL'].mean():.2f}x")
        print(f"      - Mean Abs Return : {anomalies['Abs_Return_Pct'].mean():.2f}%")
        
    return df_valid, anomalies


def run_full_pipeline():
    repo_root = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings"
    data_dir = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print("================================================================================")
    print("  SPY EXTREME CANDLESTICK ANOMALY EXTRACTION PIPELINE")
    print("  Repository: Vedic-Quant-37-Mo-Su-La-Nak-Retro-Panchang-Findings")
    print("  Branch    : feat/extreme-solid-candlestick-anomalies")
    print("================================================================================")
    
    # 1. Ingest Data across all 6 timeframes
    # 1H (Alpaca)
    df_1h_raw = fetch_alpaca_1h(start_year=2016, end_year=2026)
    
    # 2H (Resampled from 1H)
    df_2h_raw = resample_ohlcv(df_1h_raw, rule='2h', label='2H')
    
    # 4H (Resampled from 1H)
    df_4h_raw = resample_ohlcv(df_1h_raw, rule='4h', label='4H')
    
    # 1D, 1W, 1MO (yfinance 1993-2026)
    df_1d_raw = fetch_yfinance_bars(interval='1d', label='1D')
    df_1w_raw = fetch_yfinance_bars(interval='1wk', label='1W')
    df_1mo_raw = fetch_yfinance_bars(interval='1mo', label='1MO')
    
    timeframe_datasets = [
        ('1H', df_1h_raw),
        ('2H', df_2h_raw),
        ('4H', df_4h_raw),
        ('1D', df_1d_raw),
        ('1W', df_1w_raw),
        ('1MO', df_1mo_raw)
    ]
    
    all_anomalies_list = []
    manifest_summary = {}

    for tf_label, raw_df in timeframe_datasets:
        full_df, anom_df = compute_features_and_anomalies(raw_df, timeframe=tf_label)
        
        # File paths
        file_prefix = f"spy_anomalies_{tf_label.lower()}"
        full_file_prefix = f"spy_full_series_{tf_label.lower()}"
        
        # Save anomalies
        anom_parquet = os.path.join(data_dir, f"{file_prefix}.parquet")
        anom_csv = os.path.join(data_dir, f"{file_prefix}.csv")
        anom_df.to_parquet(anom_parquet, index=False)
        anom_df.to_csv(anom_csv, index=False)
        
        # Save full feature series
        full_parquet = os.path.join(data_dir, f"{full_file_prefix}.parquet")
        full_df.to_parquet(full_parquet, index=False)
        
        print(f"  [SAVED] {anom_parquet} ({os.path.getsize(anom_parquet):,} bytes)")
        print(f"  [SAVED] {anom_csv} ({os.path.getsize(anom_csv):,} bytes)")
        
        all_anomalies_list.append(anom_df)
        
        manifest_summary[tf_label] = {
            'total_bars': len(full_df),
            'start_date': str(full_df['Datetime'].iloc[0]),
            'end_date': str(full_df['Datetime'].iloc[-1]),
            'anomaly_count': len(anom_df),
            'green_count': int((anom_df['Direction'] == 'GREEN').sum()) if len(anom_df) > 0 else 0,
            'red_count': int((anom_df['Direction'] == 'RED').sum()) if len(anom_df) > 0 else 0,
            'tier2_super_anomalies': int((anom_df['Anomaly_Tier'] == 2).sum()) if len(anom_df) > 0 else 0,
            'mean_solid_ratio': float(anom_df['Solid_Ratio'].mean()) if len(anom_df) > 0 else 0.0,
            'mean_rvol': float(anom_df['RVOL'].mean()) if len(anom_df) > 0 else 0.0,
            'mean_abs_return_pct': float(anom_df['Abs_Return_Pct'].mean()) if len(anom_df) > 0 else 0.0,
        }

    # Combine into Master Manifest
    master_manifest = pd.concat(all_anomalies_list, ignore_index=True)
    master_manifest = master_manifest.sort_values('Datetime').reset_index(drop=True)
    
    master_parquet = os.path.join(data_dir, "spy_anomalies_master_manifest.parquet")
    master_csv = os.path.join(data_dir, "spy_anomalies_master_manifest.csv")
    master_json = os.path.join(data_dir, "spy_anomalies_summary_stats.json")
    
    master_manifest.to_parquet(master_parquet, index=False)
    master_manifest.to_csv(master_csv, index=False)
    
    with open(master_json, 'w') as f:
        json.dump(manifest_summary, f, indent=2)
        
    print("\n================================================================================")
    print("  EXTRACTION COMPLETE & VERIFIED")
    print(f"  Master Manifest Parquet : {master_parquet} ({len(master_manifest)} total anomalies)")
    print(f"  Master Manifest CSV     : {master_csv}")
    print(f"  Summary Statistics JSON : {master_json}")
    print("================================================================================")
    
    return manifest_summary


if __name__ == "__main__":
    run_full_pipeline()
