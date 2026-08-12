import requests
from datetime import datetime, timezone

headers = {
    'APCA-API-KEY-ID': 'PKRP3DNPUG6PROD7L2BSJ3JBZS',
    'APCA-API-SECRET-KEY': '5GCpQ4U6TrjRfwKdiH4KKBFGFYAGhHEUi2ARQRKy6zJk'
}
BASE = 'https://paper-api.alpaca.markets'

# Account
a = requests.get(f'{BASE}/v2/account', headers=headers).json()
equity = float(a['equity'])
last_equity = float(a['last_equity'])
day_change = equity - last_equity
print("=== GENESIS ASTRO ENGINE - ACCOUNT ===")
print(f"Equity:      ${equity:,.2f}")
print(f"Cash:        ${float(a['cash']):,.2f}")
print(f"Day Change:  ${day_change:+,.2f}")

# Positions
pos = requests.get(f'{BASE}/v2/positions', headers=headers).json()
print(f"\n=== OPEN POSITIONS ({len(pos)}) ===")
for p in pos:
    print(f"  {p['symbol']} | {p['side']} {p['qty']} sh | entry ${float(p['avg_entry_price']):,.2f} | PnL ${float(p['unrealized_pl']):+,.2f}")
if not pos:
    print("  No open positions")

# Orders today
orders = requests.get(f'{BASE}/v2/orders?status=all&limit=50&direction=desc', headers=headers).json()
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
todays = [o for o in orders if o.get('created_at', '').startswith(today)]
print(f"\n=== ORDERS TODAY ({len(todays)}) ===")
for o in todays:
    t = o['created_at'][11:19]
    print(f"  {t} | {o['symbol']} | {o['side']} {o['qty']} | {o['type']} | {o['status']}")
if not todays:
    print("  No orders placed today")

# Recent activities
acts = requests.get(f'{BASE}/v2/account/activities?page_size=20', headers=headers).json()
today_acts = [x for x in acts if x.get('transaction_time', '').startswith(today)]
print(f"\n=== FILLS TODAY ({len(today_acts)}) ===")
for x in today_acts:
    t = x.get('transaction_time', '')[:19]
    print(f"  {t} | {x.get('symbol')} | {x.get('side')} {x.get('qty')} @ ${float(x.get('price',0)):,.2f}")
if not today_acts:
    print("  No fills today")

# Bot log
from pathlib import Path
log_candidates = [
    Path(r"C:\Users\patel\Desktop\Python\Learn\fleet\logs\genesis_astro.log"),
    Path(r"C:\Users\patel\Desktop\Python\Learn\auto_medic_11th_bot.json"),
]
for lp in log_candidates:
    if lp.exists():
        print(f"\n=== BOT LOG: {lp.name} (last 20 lines) ===")
        lines = lp.read_text(encoding='utf-8', errors='replace').strip().splitlines()
        for l in lines[-20:]:
            print(" ", l)
        break
else:
    print("\n  No local bot log file found")
