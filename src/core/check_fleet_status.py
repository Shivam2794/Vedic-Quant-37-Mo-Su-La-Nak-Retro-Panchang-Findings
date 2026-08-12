import urllib.request
import json
import datetime

bots = [
    {
        "name": "Hybrid 8-Sleeve",
        "key": "PKM2SKS4PCTIZPTW65DSDOWIWF",
        "secret": "FsxCaEAjnx7eJPnZyoJCYsAYjGuHbYeFBDeCXKjSM5Mp"
    },
    {
        "name": "Advanced Momentum",
        "key": "PKJUAZONBOCJCW4QMRO3KOJK6D",
        "secret": "DV37wqiXTDDMDCDMjqW24GRDBjFuDRe1BuySHvqRXk5H"
    },
    {
        "name": "Omni-V2 Screener",
        "key": "PKE4JL6V7OWYR77YW4W5VZLL55",
        "secret": "8c3JnT3trG2ShRHjucKYbzntDmJ3ACT8ZcG9Bf11i2PL"
    },
    {
        "name": "Standard Astro Trading",
        "key": "PKU2HZUY2BGOC7M5AAEOSSBYF2",
        "secret": "3gYp9q9mPFukBrYoaqGuiDVguAEGuzsjcasbCoZXJa47"
    },
    {
        "name": "Advance Auto Research Astro",
        "key": "PKB5NPW6CNM4CIJSZYE4SZ5YDY",
        "secret": "J4HDDHVTUdhoKthu2ejKBBX4Z2yUCRUXZfy5vWDA9eYd"
    },
    {
        "name": "DSP PMCC & Iron Diagonal",
        "key": "PKDX2DI75GASRKIKANIJESFWSW",
        "secret": "4XoaPfzHtQTk44hqmLbMKB8yS691hB9Be6zxkP7yKmug"
    },
    {
        "name": "Poor Man's Option",
        "key": "PKN72GWPJLA5IQQJTI3EHOT5QV",
        "secret": "94amGJyrFpyPidRyfusbzHJiZLsBYGp1aVc6NzyB87eL"
    },
    {
        "name": "V4 ML-Driven Strategy",
        "key": "PKSNHPADP6WIE75ZXQTW3SXGMA",
        "secret": "CfxdmZQDuKzGx4GBJoeP5nuRKmr7TiYQMXmwS46bbdGs"
    }
]

today = datetime.datetime.now().strftime('%Y-%m-%d')
start_of_day = f"{today}T00:00:00Z"

for bot in bots:
    print(f"=== {bot['name']} ===")
    headers = {
        "APCA-API-KEY-ID": bot["key"],
        "APCA-API-SECRET-KEY": bot["secret"],
        "accept": "application/json"
    }
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
        print(f"  Error checking {bot['name']}: {e}")
    print("\n")
