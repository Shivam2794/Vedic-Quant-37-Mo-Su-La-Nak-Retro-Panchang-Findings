import sys
import re

file_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\ml_options_hedging_project\gup_alpaca_trader\run_daily.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Insert get_live_quote and smart_execute before execute_orders
smart_functions = """
def get_live_quote(symbol):
    try:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockLatestQuoteRequest
        from gup_alpaca_trader import config
        data_client = StockHistoricalDataClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY)
        req = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        res = data_client.get_stock_latest_quote(req)
        quote = res[symbol]
        return quote.bid_price, quote.ask_price
    except Exception as e:
        log(f"  [ERROR] Failed to fetch quote for {symbol}: {e}")
        return None, None

def smart_execute(client, symbol, qty, side, max_attempts=15):
    from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    from datetime import datetime
    import pytz
    import time
    
    bid, ask = get_live_quote(symbol)
    if not bid or not ask:
        log(f"  [WARNING] Falling back to Market Order for {symbol} due to missing quote.")
        return client.submit_order(MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=TimeInForce.DAY))
        
    mid = round((bid + ask) / 2, 2)
    limit_price = mid
    log(f"  [{symbol}] Initiating Smart Execution. Qty: {qty}, Side: {side.name}. Bid: {bid}, Ask: {ask}, Mid: {mid}")
    
    ET = pytz.timezone("US/Eastern")
    
    for attempt in range(max_attempts):
        now = datetime.now(ET)
        # If market closes in less than 2 minutes (15:58:00), force market order
        if now.hour == 15 and now.minute >= 58:
            log(f"  [{symbol}] Market close approaching. Forcing Market Order.")
            return client.submit_order(MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=TimeInForce.DAY))
            
        try:
            order = client.submit_order(LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price
            ))
            log(f"  [{symbol}] Attempt {attempt+1}: Submitted Limit {side.name} @ {limit_price}")
        except Exception as e:
            log(f"  [ERROR] Failed to submit limit order for {symbol}: {e}")
            return None
            
        time.sleep(5)
        
        try:
            status = client.get_order_by_id(order.id)
            if status.status in ["filled"]:
                log(f"  [{symbol}] SUCCESS! Filled at {status.filled_avg_price}")
                return status
            elif status.status in ["partially_filled"]:
                filled = float(status.filled_qty)
                log(f"  [{symbol}] Partially filled {filled}/{qty}. Canceling remainder...")
                client.cancel_order_by_id(order.id)
                qty = qty - filled
            else:
                client.cancel_order_by_id(order.id)
                
            if side == OrderSide.BUY:
                limit_price = round(limit_price + 0.01, 2)
            else:
                limit_price = round(limit_price - 0.01, 2)
                
        except Exception as e:
            log(f"  [ERROR] Exception in Smart Loop for {symbol}: {e}")
            
    log(f"  [{symbol}] Max attempts reached. Falling back to Market Order.")
    return client.submit_order(MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=TimeInForce.DAY))

def execute_orders(target_positions: dict):"""

content = content.replace("def execute_orders(target_positions: dict):", smart_functions)

# We need to manually replace the loop logic inside execute_orders
new_execution_logic = """
    for symbol in list(current_positions.keys()):
        if symbol not in target_positions:
            try:
                qty = int(current_positions[symbol]["qty"])
                order = smart_execute(client, symbol, qty, OrderSide.SELL)
                if order:
                    orders_executed.append({"action": "SELL", "symbol": symbol, "qty": qty, "order_id": str(order.id)})
            except Exception as e:
                log(f"  [ERROR] Failed to sell {symbol}: {e}")
                
    for symbol, target_dollars in target_positions.items():
        current_value = current_positions.get(symbol, {}).get("market_value", 0)
        diff = target_dollars - current_value
        
        if abs(diff) < total_equity * config.REBALANCE_THRESHOLD:
            log(f"  HOLD {symbol}: drift ${diff:,.0f} below threshold")
            continue
            
        bid, ask = get_live_quote(symbol)
        if not ask: continue
        mid_price = (bid + ask) / 2
        target_qty = int(abs(diff) / mid_price)
        if target_qty == 0:
            log(f"  HOLD {symbol}: Diff ${diff:,.0f} is less than 1 share.")
            continue
            
        try:
            if diff > 0:
                order = smart_execute(client, symbol, target_qty, OrderSide.BUY)
                if order:
                    orders_executed.append({"action": "BUY", "symbol": symbol, "qty": target_qty, "order_id": str(order.id)})
            else:
                order = smart_execute(client, symbol, target_qty, OrderSide.SELL)
                if order:
                    orders_executed.append({"action": "SELL", "symbol": symbol, "qty": target_qty, "order_id": str(order.id)})
        except Exception as e:
            log(f"  [ERROR] Failed to trade {symbol}: {e}")
            
    today = datetime.now(ET).strftime("%Y-%m-%d")
"""

pattern = re.compile(r"    for symbol in list\(current_positions\.keys\(\)\):.*?    today = datetime\.now\(ET\)\.strftime\('%Y-%m-%d'\)", re.DOTALL)
content = pattern.sub(new_execution_logic.strip("\n"), content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch successful!")
