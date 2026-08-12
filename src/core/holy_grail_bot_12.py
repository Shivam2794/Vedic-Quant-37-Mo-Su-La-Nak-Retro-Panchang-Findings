import os
import sys
import argparse
import logging
import datetime
import math
import time
import numpy as np
import pandas as pd
import yfinance as yf
import httpx
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables
env_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\.env"
load_dotenv(env_path)

ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
API_KEY = os.environ.get("FLEET_BOT_12_API_KEY") or os.environ.get("FLEET_BOT_12_KEY")
SECRET_KEY = os.environ.get("FLEET_BOT_12_SECRET_KEY") or os.environ.get("FLEET_BOT_12_SECRET")

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
    "Content-Type": "application/json"
}

# Core Strategy Universe
UNIVERSE = ["SPY", "QQQ", "IWM", "TQQQ", "UPRO", "XLK", "XLE", "GLD", "TLT"]

def fetch_historical_prices(universe, days=250):
    logging.info(f"Fetching historical daily price data for universe: {universe}")
    df = yf.download(universe, period=f"{days}d", interval="1d", progress=False)
    if "Adj Close" in df:
        df = df["Adj Close"]
    elif "Close" in df:
        df = df["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame()
    df = df.ffill().dropna(how="all")
    return df

def calculate_holy_grail_weights(df_prices, top_n=4, abs_mom_window=60, vol_window=20, lazy_thresh=0.03):
    rets = df_prices.pct_change()
    
    # 20-day annualized volatility
    vol_20d = rets.rolling(vol_window).std() * math.sqrt(252.0)
    vol_20d = vol_20d.clip(lower=0.05)
    
    # Absolute momentum gate (60-day return > 0)
    mom_60d = (df_prices / df_prices.shift(abs_mom_window)) - 1.0
    
    # Latest day values
    latest_prices = df_prices.iloc[-1]
    latest_vol = vol_20d.iloc[-1]
    latest_mom = mom_60d.iloc[-1]
    
    # Filter assets passing absolute momentum gate
    eligible_assets = latest_mom[latest_mom > 0.0].index.tolist()
    logging.info(f"Assets passing 60-day momentum gate (>0): {eligible_assets}")
    
    target_weights = {symbol: 0.0 for symbol in UNIVERSE}
    
    if not eligible_assets:
        logging.warning("No assets passed absolute momentum gate! Target portfolio is 100% Cash.")
        return target_weights, latest_prices
        
    # Rank eligible assets by momentum
    sorted_assets = latest_mom.loc[eligible_assets].sort_values(ascending=False).index.tolist()[:top_n]
    logging.info(f"Top {len(sorted_assets)} ranked momentum assets: {sorted_assets}")
    
    # Inverse volatility weights
    inv_vols = 1.0 / latest_vol.loc[sorted_assets]
    total_inv_vol = inv_vols.sum()
    
    for symbol in sorted_assets:
        target_weights[symbol] = float(inv_vols[symbol] / total_inv_vol)
        
    return target_weights, latest_prices

def get_alpaca_account():
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{ALPACA_BASE_URL}/v2/account", headers=HEADERS)
        r.raise_for_status()
        return r.json()

def get_alpaca_positions():
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{ALPACA_BASE_URL}/v2/positions", headers=HEADERS)
        r.raise_for_status()
        return r.json()

def cancel_open_orders():
    with httpx.Client(timeout=10.0) as client:
        r = client.delete(f"{ALPACA_BASE_URL}/v2/orders", headers=HEADERS)
        logging.info(f"Canceled open orders: status {r.status_code}")

def execute_rebalance(target_weights, latest_prices, lazy_thresh=0.03, dry_run=False):
    account = get_alpaca_account()
    equity = float(account.get("portfolio_value", account.get("equity", 0)))
    buying_power = float(account.get("buying_power", 0))
    logging.info(f"Alpaca Bot 12 Account Equity: ${equity:,.2f} | Buying Power: ${buying_power:,.2f}")
    
    positions = get_alpaca_positions()
    current_market_values = {}
    
    # Liquidate positions outside our universe if present
    with httpx.Client(timeout=10.0) as client:
        for p in positions:
            sym = p["symbol"]
            if sym not in UNIVERSE:
                logging.info(f"Liquidating old failing position outside Holy Grail universe: {sym} (Qty: {p['qty']})")
                if not dry_run:
                    client.delete(f"{ALPACA_BASE_URL}/v2/positions/{sym}", headers=HEADERS)
                    time.sleep(0.5)
            else:
                current_market_values[sym] = float(p["market_value"])
    current_weights = {symbol: current_market_values.get(symbol, 0.0) / equity for symbol in UNIVERSE}
    
    logging.info("--- PORTFOLIO REBALANCE ANALYSIS ---")
    orders_to_place = []
    
    for symbol in UNIVERSE:
        t_weight = target_weights.get(symbol, 0.0)
        c_weight = current_weights.get(symbol, 0.0)
        diff = t_weight - c_weight
        
        logging.info(f"Symbol: {symbol:5s} | Current Weight: {c_weight*100:6.2f}% | Target Weight: {t_weight*100:6.2f}% | Diff: {diff*100:+6.2f}%")
        
        if abs(diff) > lazy_thresh:
            target_dollar = t_weight * equity
            current_dollar = current_market_values.get(symbol, 0.0)
            trade_dollar = target_dollar - current_dollar
            
            price = float(latest_prices[symbol])
            shares = int(trade_dollar / price)
            
            if shares != 0:
                side = "buy" if shares > 0 else "sell"
                orders_to_place.append({
                    "symbol": symbol,
                    "qty": abs(shares),
                    "side": side,
                    "type": "market",
                    "time_in_force": "day"
                })
        else:
            logging.info(f"  -> Skipping {symbol}: Weight diff ({abs(diff)*100:.2f}%) within {lazy_thresh*100:.1f}% lazy threshold buffer.")
            
    if dry_run:
        logging.info("[DRY-RUN ENFORCED] Target orders calculated but NOT submitted:")
        for order in orders_to_place:
            logging.info(f"  DRY-RUN ORDER: {order['side'].upper()} {order['qty']} {order['symbol']} (Market)")
        return orders_to_place
        
    # Execute actual orders
    if orders_to_place:
        cancel_open_orders()
        with httpx.Client(timeout=10.0) as client:
            for order in orders_to_place:
                logging.info(f"Submitting LIVE ORDER: {order['side'].upper()} {order['qty']} {order['symbol']}...")
                r = client.post(f"{ALPACA_BASE_URL}/v2/orders", headers=HEADERS, json=order)
                if r.status_code in (200, 201):
                    res = r.json()
                    logging.info(f"  SUCCESS: Order ID {res.get('id')} | Status: {res.get('status')}")
                else:
                    logging.error(f"  FAILED: Status {r.status_code} | Output: {r.text}")
                time.sleep(0.5)
    else:
        logging.info("Portfolio is cleanly balanced within threshold. Zero trades needed today.")
        
    return orders_to_place

def run_bot(dry_run=False):
    logging.info("======================================================================")
    logging.info("      STARTING HOLY GRAIL 3-LAYER QUANTITATIVE ENGINE (BOT 12)       ")
    logging.info("======================================================================")
    
    if not API_KEY or not SECRET_KEY:
        logging.error("Missing FLEET_BOT_12 credentials in .env file! Exiting.")
        sys.exit(1)
        
    df_prices = fetch_historical_prices(UNIVERSE)
    target_weights, latest_prices = calculate_holy_grail_weights(df_prices)
    
    logging.info("Target Portfolio Weights:")
    for sym, w in target_weights.items():
        logging.info(f"  {sym:5s}: {w*100:6.2f}%")
        
    orders = execute_rebalance(target_weights, latest_prices, lazy_thresh=0.03, dry_run=dry_run)
    logging.info("======================================================================")
    logging.info("               EXECUTION CYCLE COMPLETED SUCCESSFULLY                 ")
    logging.info("======================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Holy Grail Bot 12 Live Execution Engine")
    parser.add_argument("--dry-run", action="store_true", help="Calculate targets without placing orders")
    args = parser.parse_args()
    
    run_bot(dry_run=args.dry_run)
