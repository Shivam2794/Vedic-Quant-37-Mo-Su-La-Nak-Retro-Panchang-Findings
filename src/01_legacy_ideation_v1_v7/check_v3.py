import urllib.request
import json
import datetime

key = "PKPMH36BFLZ2K2KWNQ4CG5TE3F"
secret = "ESv78X8KC9Mxe1wEiBKsVtC4tc6XsuBqAFbG3U4Nwz62"

today = datetime.datetime.now().strftime('%Y-%m-%d')
start_of_day = f"{today}T00:00:00Z"

headers = {
    "APCA-API-KEY-ID": key,
    "APCA-API-SECRET-KEY": secret,
    "accept": "application/json"
}

print("=== V3 Deep AutoResearch ===")
try:
    # Check Account
    req_acct = urllib.request.Request("https://paper-api.alpaca.markets/v2/account", headers=headers)
    with urllib.request.urlopen(req_acct) as response:
        account = json.loads(response.read())
        print(f"  Equity: ${float(account.get('equity', 0)):.2f} (Status: {account.get('status')})")
        
    # Check Orders for Today
    req_orders = urllib.request.Request(f"https://paper-api.alpaca.markets/v2/orders?status=all&after={start_of_day}", headers=headers)
    with urllib.request.urlopen(req_orders) as response:
        orders = json.loads(response.read())
        filled_orders = [o for o in orders if o['status'] == 'filled']
        print(f"  Orders Today: {len(orders)} total, {len(filled_orders)} filled")
        for o in orders[:5]:
            print(f"    - {o['side']} {o['qty']} {o['symbol']} at {o['created_at']} (Status: {o['status']})")
            
    # Check Positions
    req_pos = urllib.request.Request("https://paper-api.alpaca.markets/v2/positions", headers=headers)
    with urllib.request.urlopen(req_pos) as response:
        positions = json.loads(response.read())
        print(f"  Open Positions: {len(positions)}")
        for p in positions[:3]:
            print(f"    - {p['qty']} {p['symbol']} (Unrealized PNL: ${float(p['unrealized_pl']):.2f})")
except Exception as e:
    print(f"  Error checking: {e}")
