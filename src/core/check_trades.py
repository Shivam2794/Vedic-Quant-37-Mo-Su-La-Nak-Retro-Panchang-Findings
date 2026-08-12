import urllib.request
import json
from datetime import datetime

try:
    req = urllib.request.urlopen('http://127.0.0.1:8000/api/fleet-status')
    data = json.loads(req.read().decode())
    print(f'Total Bots: {data.get("summary", {}).get("total_bots")}')
    for bot in data.get('bots', []):
        name = bot.get('name')
        orders = bot.get('orders', [])
        history = bot.get('history', [])
        status = bot.get('status')
        if status != 'online':
            print(f'- {name}: OFFLINE (error: {bot.get("error")})')
            continue
        
        last_trade_date = 'Never'
        if history:
            trade_activities = [h for h in history if h.get('activity_type') == 'FILL']
            if trade_activities:
                last_trade_date = trade_activities[0].get('transaction_time', 'Unknown')
        
        if last_trade_date == 'Never' and orders:
            last_trade_date = orders[0].get('filled_at') or orders[0].get('created_at', 'Unknown')

        print(f'- {name}: Last Trade/Order: {last_trade_date}')
except Exception as e:
    print('Error:', e)
