import time
import datetime
import pandas as pd
import numpy as np
import logging
import requests
import sqlite3
import uuid
import os
from zoneinfo import ZoneInfo
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')

# Master God-Tier BINGO Parameters
TP_M = 5.2711
SL_M = 7.6553
RSI_M = 60.0045
GAP_M = 0.0050
VOL_M = 0.1500
TARGET_VOL = 0.3986
OVERNIGHT_ALLOCATION = 0.1039
PORTFOLIO_LEVERAGE = 2.0

# Load Credentials
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_API_SECRET = os.environ.get("ALPACA_SECRET_KEY")
if not ALPACA_API_KEY or not ALPACA_API_SECRET:
    raise ValueError("Missing Alpaca API credentials in .env")

ALPACA_BASE_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"

ET = ZoneInfo("America/New_York")

# ----------------- Database -----------------
DB_PATH = os.path.join(os.path.dirname(__file__), 'trading_state.db')
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS position_state (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            qty REAL,
            entry_price REAL,
            client_order_id TEXT,
            intraday_active BOOLEAN
        )''')
        # Seed empty state if not exists
        if conn.execute("SELECT COUNT(*) FROM position_state").fetchone()[0] == 0:
            conn.execute("INSERT INTO position_state (id, symbol, qty, entry_price, client_order_id, intraday_active) VALUES (1, 'TQQQ', 0, 0, '', 0)")
        conn.commit()

def get_db_state():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return dict(conn.execute("SELECT * FROM position_state WHERE id=1").fetchone())

def update_db_state(qty, entry_price, client_order_id, intraday_active):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE position_state SET qty=?, entry_price=?, client_order_id=?, intraday_active=? WHERE id=1",
                     (qty, entry_price, client_order_id, intraday_active))
        conn.commit()


# ----------------- Broker Class -----------------
class AlpacaBroker:
    def __init__(self):
        self.headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_API_SECRET,
            "accept": "application/json"
        }

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
    def request_get(self, url, params=None):
        resp = requests.get(url, headers=self.headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def request_post(self, url, payload):
        resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def request_delete(self, url):
        resp = requests.delete(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_equity(self):
        try:
            res = self.request_get(f"{ALPACA_BASE_URL}/account")
            return float(res['equity'])
        except Exception as e:
            logging.error(f"Failed to fetch equity: {e}")
            return 0.0

    def get_buying_power(self):
        try:
            res = self.request_get(f"{ALPACA_BASE_URL}/account")
            return float(res['buying_power'])
        except Exception as e:
            logging.error(f"Failed to fetch BP: {e}")
            return 0.0

    def get_position(self, symbol):
        try:
            res = self.request_get(f"{ALPACA_BASE_URL}/positions/{symbol}")
            return float(res['qty'])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return 0.0
            logging.error(f"Failed to fetch position: {e}")
            return 0.0

    def get_clock(self):
        return self.request_get(f"{ALPACA_BASE_URL}/clock")

    def buy_bracket(self, symbol, alloc_pct, price, tp_price, sl_price, reason=""):
        equity = self.get_equity()
        bp = self.get_buying_power()
        target_value = equity * alloc_pct
        
        # Ensure we don't exceed BP
        if target_value > bp:
            logging.warning(f"Target value ${target_value:,.2f} exceeds Buying Power ${bp:,.2f}. Capping.")
            target_value = bp

        shares = int(target_value / price)
        if shares > 0:
            client_id = f"tqqq_bracket_{uuid.uuid4().hex[:8]}"
            payload = {
                "symbol": symbol,
                "qty": str(shares),
                "side": "buy",
                "type": "market",
                "time_in_force": "day",
                "client_order_id": client_id,
                "order_class": "bracket",
                "take_profit": {
                    "limit_price": f"{tp_price:.2f}"
                },
                "stop_loss": {
                    "stop_price": f"{sl_price:.2f}"
                }
            }
            try:
                res = self.request_post(f"{ALPACA_BASE_URL}/orders", payload)
                logging.info(f"ALPACABROKER BUY BRACKET: {shares} shares of {symbol} @ ~${price:.2f} | Reason: {reason}")
                return shares, client_id
            except Exception as e:
                logging.error(f"Alpaca Buy Bracket Failed: {e}")
        return 0, ""
        
    def buy_market(self, symbol, alloc_pct, price, reason=""):
        equity = self.get_equity()
        bp = self.get_buying_power()
        target_value = equity * alloc_pct
        if target_value > bp:
            target_value = bp
            
        shares = int(target_value / price)
        if shares > 0:
            client_id = f"tqqq_market_{uuid.uuid4().hex[:8]}"
            payload = {
                "symbol": symbol,
                "qty": str(shares),
                "side": "buy",
                "type": "market",
                "time_in_force": "cls", # Market On Close (though may need 'day' if near close)
                "client_order_id": client_id
            }
            try:
                # If market is closed or too close to close, 'cls' might be rejected, fallback to 'day'
                self.request_post(f"{ALPACA_BASE_URL}/orders", payload)
                logging.info(f"ALPACABROKER BUY MARKET: {shares} shares of {symbol} @ ~${price:.2f} | Reason: {reason}")
                return shares, client_id
            except Exception as e:
                logging.error(f"Alpaca Buy Market Failed: {e}")
                # Fallback to day
                payload["time_in_force"] = "day"
                try:
                    self.request_post(f"{ALPACA_BASE_URL}/orders", payload)
                    return shares, client_id
                except Exception as e2:
                    logging.error(f"Fallback Alpaca Buy Market Failed: {e2}")
        return 0, ""

    def sell_all(self, symbol, reason=""):
        shares = self.get_position(symbol)
        if shares > 0:
            try:
                # Close position endpoint automatically cancels associated bracket orders
                self.request_delete(f"{ALPACA_BASE_URL}/positions/{symbol}")
                logging.info(f"ALPACABROKER SELL ALL: {shares} shares of {symbol} | Reason: {reason}")
            except Exception as e:
                logging.error(f"Alpaca Sell Failed: {e}")

    def fetch_alpaca_bars(self, symbol, timeframe, limit=1000, start=None, end=None):
        params = {"timeframe": timeframe, "limit": limit}
        if start: params["start"] = start
        if end: params["end"] = end
        res = self.request_get(f"{ALPACA_DATA_URL}/stocks/{symbol}/bars", params=params)
        bars = res.get('bars', [])
        if not bars:
            return pd.DataFrame()
        df = pd.DataFrame(bars)
        df.rename(columns={'t': 'timestamp', 'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
        return df
        
    def get_latest_price(self, symbol):
        try:
            res = self.request_get(f"{ALPACA_DATA_URL}/stocks/{symbol}/trades/latest")
            return float(res['trade']['p'])
        except Exception as e:
            logging.error(f"Failed to fetch latest price for {symbol}: {e}")
            return 0.0

# ----------------- Signal Logic -----------------
def fetch_daily_features(broker):
    logging.info("Fetching Daily Data for Regime/Signal calculation...")
    # Fetch ~60 days to get 40 trading days
    start = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%SZ')
    df = broker.fetch_alpaca_bars('QQQ', '1Day', start=start)
    
    if len(df) < 22:
        logging.error("Not enough data to calculate 21-day volatility.")
        return None
        
    hl = df['High'] - df['Low']
    hc = np.abs(df['High'] - df['Close'].shift(1))
    lc = np.abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs)) # Canonical RSI would use EWM, but matching existing logic to preserve strategy
    
    ret = df['Close'].pct_change()
    df['Realized_Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
    df['Realized_Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
    df['GEX_Regime'] = np.where(df['Realized_Vol_5'] < df['Realized_Vol_21'], 1, -1)
    
    # Needs to be yesterday's data (assuming today is the last incomplete bar, or yesterday if market closed)
    # To be safe, filter out today's date if it's there
    today_str = datetime.datetime.now(ET).strftime('%Y-%m-%d')
    df['date_str'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d')
    df_historical = df[df['date_str'] < today_str]
    
    if len(df_historical) < 1:
        return None
        
    yday = df_historical.iloc[-1]
    
    return {
        'F_RSI': yday['RSI'],
        'F_ATR_pct': yday['ATR'] / yday['Close'],
        'F_Realized_Vol': yday['Realized_Vol_21'],
        'F_GEX_Regime': yday['GEX_Regime'],
        'Prev_Close': yday['Close'],
        'Prev_Volume': yday['Volume']
    }

def fetch_first_hour_data(broker):
    logging.info("Fetching 09:30 - 10:30 Intraday Data...")
    today_start = datetime.datetime.now(ET).replace(hour=9, minute=30, second=0, microsecond=0)
    start_str = today_start.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    df = broker.fetch_alpaca_bars('QQQ', '1Min', start=start_str)
    
    if len(df) == 0:
        return None
        
    df['dt_et'] = pd.to_datetime(df['timestamp']).dt.tz_convert('America/New_York')
    df_fh = df[(df['dt_et'].dt.hour == 9) | ((df['dt_et'].dt.hour == 10) & (df['dt_et'].dt.minute < 30))]
    
    if len(df_fh) == 0:
        return None
        
    fh_open = df_fh['Open'].iloc[0]
    fh_close = df_fh['Close'].iloc[-1]
    fh_vol = df_fh['Volume'].sum()
    
    # Get proper gap (from yesterday's close, not first hour open)
    daily_feats = fetch_daily_features(broker)
    if not daily_feats:
        return None
    prev_close = daily_feats['Prev_Close']
    true_gap_pct = (fh_open / prev_close) - 1.0 # True overnight gap
    
    return {
        'First_Hour_Green': fh_close > fh_open,
        'Gap_Pct': abs(true_gap_pct),
        'FH_Vol': fh_vol,
        'Current_TQQQ_Price': broker.get_latest_price('TQQQ')
    }

def run_live_bot():
    init_db()
    broker = AlpacaBroker()
    
    logging.info(f"=== INITIALIZING MASTER ENGINE (TQQQ LIVE ALPACA BOT) ===")
    
    while True:
        try:
            clock = broker.get_clock()
            is_open = clock['is_open']
            next_close = pd.to_datetime(clock['next_close']).astimezone(ET)
            next_open = pd.to_datetime(clock['next_open']).astimezone(ET)
            now = datetime.datetime.now(ET)
            
            if not is_open:
                # Sleep until open
                sleep_sec = (next_open - now).total_seconds()
                logging.info(f"Market Closed. Sleeping until {next_open.strftime('%Y-%m-%d %H:%M:%S ET')} ({sleep_sec/3600:.1f} hours)")
                time.sleep(max(10, min(sleep_sec, 3600))) # Wake up at least every hour to check
                continue

            time_str = now.strftime("%H:%M")
            db_state = get_db_state()
            intraday_active = db_state['intraday_active']
            
            # --- 09:30: Sell Overnight Position ---
            if time_str == "09:30":
                pos = broker.get_position('TQQQ')
                if pos > 0:
                    broker.sell_all('TQQQ', reason="MOO Overnight Exit")
                    update_db_state(0, 0, "", False)
                time.sleep(60)
                
            # --- 10:30: Intraday Signal Generation ---
            elif time_str == "10:30" and not intraday_active:
                daily_feats = fetch_daily_features(broker)
                fh_feats = fetch_first_hour_data(broker)
                
                if daily_feats and fh_feats:
                    gap_pct = fh_feats['Gap_Pct']
                    vol_ratio = fh_feats['FH_Vol'] / daily_feats['Prev_Volume']
                    
                    logging.info(f"Signal Check | RSI: {daily_feats['F_RSI']:.1f}, FH_Green: {fh_feats['First_Hour_Green']}, TrueGap: {gap_pct:.4f}, VolRatio: {vol_ratio:.2f}")
                    
                    if fh_feats['First_Hour_Green'] and daily_feats['F_RSI'] < RSI_M and gap_pct < GAP_M and vol_ratio > VOL_M:
                        logging.info(">>> INTRADAY SIGNAL: GREEN <<<")
                        
                        tqqq_realized_vol = daily_feats['F_Realized_Vol'] * 3.0
                        exposure = min(1.0, TARGET_VOL / tqqq_realized_vol) if tqqq_realized_vol > 0 else 1.0
                        
                        if daily_feats['F_GEX_Regime'] == -1:
                            exposure *= 0.50
                            
                        total_exposure = exposure * PORTFOLIO_LEVERAGE
                        price = fh_feats['Current_TQQQ_Price']
                        vol = daily_feats['F_ATR_pct'] * price
                        
                        tp_price = price + (vol * TP_M)
                        sl_price = price - (vol * SL_M)
                        
                        shares, cid = broker.buy_bracket('TQQQ', total_exposure, price, tp_price, sl_price, reason="Intraday Entry")
                        if shares > 0:
                            update_db_state(shares, price, cid, True)
                            logging.info(f"Target Profit: ${tp_price:.2f} | Stop Loss: ${sl_price:.2f}")
                time.sleep(60)
                
            # --- 15:58: Intraday Time-Based Exit (1 minute before close) ---
            # Use next_close instead of hardcoded 15:59 to support half days
            minutes_to_close = (next_close - now).total_seconds() / 60.0
            
            if 0 < minutes_to_close <= 2.0:
                if intraday_active:
                    broker.sell_all('TQQQ', reason="Intraday End-of-Day Exit")
                    update_db_state(0, 0, "", False)
                    
                daily_feats = fetch_daily_features(broker)
                if daily_feats:
                    if daily_feats['F_GEX_Regime'] == 1:
                        total_ovn_exposure = OVERNIGHT_ALLOCATION * PORTFOLIO_LEVERAGE
                        price = broker.get_latest_price('TQQQ')
                        shares, cid = broker.buy_market('TQQQ', total_ovn_exposure, price, reason="Overnight MOC Entry")
                        if shares > 0:
                            update_db_state(shares, price, cid, False) # Overnight is not intraday_active
                    else:
                        logging.info("Regime is SHORT GAMMA (-1). No Overnight Entry.")
                time.sleep(120) # Sleep through the close
                
            else:
                # If during market hours and not in one of the specific action windows
                # Sync DB state with broker (in case bracket order executed)
                if intraday_active:
                    pos = broker.get_position('TQQQ')
                    if pos == 0:
                        logging.info("Broker reports 0 position. Bracket order must have filled. Resetting state.")
                        update_db_state(0, 0, "", False)
                time.sleep(30)
                
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(30)

if __name__ == "__main__":
    run_live_bot()
