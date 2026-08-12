import json
import os
import requests
from dotenv import load_dotenv

load_dotenv("C:\\Users\\Shivam Patel\\.gemini\\antigravity\\scratch\\.env")

with open("C:\\Users\\Shivam Patel\\.gemini\\antigravity\\scratch\\dashboard_v2\\fleet_config.json", "r") as f:
    bots = json.load(f)

ALPACA_BASE = "https://paper-api.alpaca.markets/v2"

print("Starting Bot Verification...")
for bot in bots:
    if bot["broker"] == "alpaca":
        env_prefix = bot["env_prefix"]
        key = os.environ.get(f"{env_prefix}_API_KEY") or os.environ.get(f"{env_prefix}_KEY")
        secret = os.environ.get(f"{env_prefix}_SECRET_KEY") or os.environ.get(f"{env_prefix}_SECRET")
        
        if not key or not secret:
            print(f"[FAIL] {bot['name']} (Prefix: {env_prefix}) - Missing API Keys in .env")
            continue
        
        headers = {
            "APCA-API-KEY-ID": key,
            "APCA-API-SECRET-KEY": secret
        }
        resp = requests.get(f"{ALPACA_BASE}/account", headers=headers)
        if resp.status_code == 200:
            acct = resp.json()
            print(f"[OK] {bot['name']} - Auth Success (Account: {acct.get('account_number')}, Equity: ${acct.get('portfolio_value')})")
        else:
            print(f"[FAIL] {bot['name']} - Auth Failed: {resp.status_code} {resp.text}")

    elif bot["broker"] == "angel":
        state_path = r"E:\Python\Learn\india_vedic_quant\live\live_state.json"
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    state = json.load(f)
                print(f"[OK] {bot['name']} - Found live state (Equity: Rs. {state.get('portfolio_value', 0)})")
            except Exception as e:
                print(f"[FAIL] {bot['name']} - Failed to parse live state: {e}")
        else:
            print(f"[FAIL] {bot['name']} - Missing live state file at {state_path}")
