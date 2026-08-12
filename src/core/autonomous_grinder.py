import yfinance as yf
import pandas as pd
import numpy as np
import itertools
import random
import time
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# RELENTLESS GRINDER: Vectorized Permutation Engine
# ---------------------------------------------------------

SLIPPAGE_BPS = 10 / 10000  # 10 bps per trade
ITERATIONS = 50000

def get_data():
    print("[*] Downloading ASGBL Universe Data...")
    tickers = ['SPY', 'TLT', 'GLD', 'LQD', 'SHV']
    data = yf.download(tickers, start="2010-01-01", end="2024-01-01", auto_adjust=True)['Close']
    data = data.ffill().dropna()
    return data

def compute_features(df):
    print("[*] Pre-computing Alpha Library Primitives...")
    feat = pd.DataFrame(index=df.index)
    
    # Base Returns
    returns = df.pct_change()
    
    for asset in df.columns:
        # Moving Averages
        for w in [20, 50, 200]:
            feat[f'{asset}_MA_{w}'] = df[asset].rolling(w).mean()
            feat[f'{asset}_Above_MA_{w}'] = (df[asset] > feat[f'{asset}_MA_{w}']).astype(int)
        
        # Momentum
        for w in [21, 63, 126, 252]:
            feat[f'{asset}_Mom_{w}'] = df[asset].pct_change(w)
            feat[f'{asset}_Mom_Pos_{w}'] = (feat[f'{asset}_Mom_{w}'] > 0).astype(int)
            
        # Volatility
        for w in [21, 63]:
            feat[f'{asset}_Vol_{w}'] = returns[asset].rolling(w).std() * np.sqrt(252)
            
        # Z-Scores (Mean Reversion)
        for w in [20, 50]:
            roll_mean = df[asset].rolling(w).mean()
            roll_std = df[asset].rolling(w).std()
            feat[f'{asset}_Z_{w}'] = (df[asset] - roll_mean) / (roll_std + 1e-8)
            feat[f'{asset}_Oversold_{w}'] = (feat[f'{asset}_Z_{w}'] < -2).astype(int)
            feat[f'{asset}_Overbought_{w}'] = (feat[f'{asset}_Z_{w}'] > 2).astype(int)
            
    # Macro Spreads
    feat['Yield_Spread_Pos'] = (returns['TLT'].rolling(63).mean() > returns['SHV'].rolling(63).mean()).astype(int)
    feat['Credit_Spread_Pos'] = (returns['LQD'].rolling(63).mean() > returns['TLT'].rolling(63).mean()).astype(int)
    feat['Gold_Ratio_Pos'] = ((df['GLD'] / df['SPY']).pct_change(63) > 0).astype(int)
    
    # Target Return (SPY Next Day)
    feat['Target_Ret'] = returns['SPY'].shift(-1)
    
    feat = feat.dropna()
    return feat, returns.loc[feat.index]

def generate_random_rule(binary_columns):
    """Generates a random boolean combination of 2 to 3 binary indicators."""
    num_conds = random.randint(1, 3)
    selected = random.sample(list(binary_columns), num_conds)
    
    rule_str = ""
    for i, col in enumerate(selected):
        invert = random.choice([True, False])
        condition = f"(feat['{col}'] == 0)" if invert else f"(feat['{col}'] == 1)"
        if i == 0:
            rule_str += condition
        else:
            op = random.choice([' & ', ' | '])
            rule_str += op + condition
            
    return rule_str, selected

def backtest_rule(feat, returns, rule_str):
    # Evaluate the logical rule string
    try:
        # Eval is safe here because we construct the strings from known column names
        signal = eval(rule_str).astype(int) 
    except Exception as e:
        print(f"Exception: {e} for rule {rule_str}")
        return -99, -99, -99, 0
        
    # Allocation: 100% SPY if signal == 1, else 100% TLT
    alloc_SPY = signal
    alloc_TLT = 1 - signal
    
    # Shift allocations by 1 day to prevent lookahead bias (execute at close, earn next day return)
    alloc_SPY = alloc_SPY.shift(1).fillna(0)
    alloc_TLT = alloc_TLT.shift(1).fillna(0)
    
    # Calculate Turnover
    turnover_SPY = alloc_SPY.diff().abs().fillna(0)
    turnover_TLT = alloc_TLT.diff().abs().fillna(0)
    total_turnover = turnover_SPY + turnover_TLT
    
    # Calculate Daily Returns with Slippage
    port_return = (alloc_SPY * returns['SPY']) + (alloc_TLT * returns['TLT'])
    cost = total_turnover * SLIPPAGE_BPS
    net_return = port_return - cost
    
    # Metrics
    cum_ret = (1 + net_return).cumprod()
    if len(cum_ret) < 252:
        return -99, -99, -99, 0
        
    cagr = (cum_ret.iloc[-1] ** (252 / len(cum_ret))) - 1
    daily_vol = net_return.std()
    
    if daily_vol == 0:
        return -99, -99, -99, 0
        
    sharpe = (cagr - 0.02) / (daily_vol * np.sqrt(252))
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    
    trades_per_year = total_turnover.sum() / (len(total_turnover) / 252)
    
    return cagr, sharpe, max_dd, trades_per_year

def run_grinder():
    print("========================================================")
    print("[*] ASGBL: RELENTLESS GRINDER INITIATED")
    print(f"[*] Targeting {ITERATIONS} Permutations")
    print("========================================================")
    
    df = get_data()
    feat, returns = compute_features(df)
    
    # Benchmark SPY
    spy_ret = returns['SPY'].loc[feat.index]
    spy_cum = (1 + spy_ret).cumprod()
    bm_cagr = (spy_cum.iloc[-1] ** (252 / len(spy_cum))) - 1
    bm_sharpe = (bm_cagr - 0.02) / (spy_ret.std() * np.sqrt(252))
    print(f"[*] SPY Benchmark CAGR: {bm_cagr*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    
    # Get all binary feature columns
    binary_cols = [c for c in feat.columns if feat[c].nunique() == 2 and c != 'Target_Ret']
    print(f"[*] Total Binary Primitives: {len(binary_cols)}")
    
    best_sharpe = -99
    best_rule = ""
    best_cagr = -99
    
    survivors = []
    
    start_time = time.time()
    
    for i in range(ITERATIONS):
        rule_str, components = generate_random_rule(binary_cols)
        cagr, sharpe, max_dd, trades = backtest_rule(feat, returns, rule_str)
        
        if sharpe > bm_sharpe and cagr > bm_cagr:
            survivors.append({
                'rule': rule_str,
                'components': components,
                'cagr': cagr,
                'sharpe': sharpe,
                'max_dd': max_dd,
                'trades_per_yr': trades
            })
            
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_rule = rule_str
            best_cagr = cagr
            
        if (i+1) % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"[*] Iteration {i+1}/{ITERATIONS} | Best Sharpe: {best_sharpe:.2f} | Time: {elapsed:.1f}s")
            
        if best_sharpe >= 1.0:
            print(f"!!! HOLY GRAIL FOUND !!! Target 1.0+ SR Achieved at iteration {i+1}")
            break
            
    print("========================================================")
    print("[*] GRIND COMPLETE")
    print(f"Total Survivors (Beating Market): {len(survivors)} / {ITERATIONS}")
    print("========================================================")
    
    if len(survivors) > 0:
        survivors_df = pd.DataFrame(survivors).sort_values(by='sharpe', ascending=False)
        survivors_df.to_csv('grinder_survivors.csv', index=False)
        print("Top 3 Rules Found:")
        for idx, row in survivors_df.head(3).iterrows():
            print(f"Rule: {row['rule']}")
            print(f" -> CAGR: {row['cagr']*100:.2f}%, Sharpe: {row['sharpe']:.2f}, Max DD: {row['max_dd']*100:.2f}%, Trades/Yr: {row['trades_per_yr']:.1f}")
            print("-")
    else:
        print("No rules survived the Brutal Inspector.")

if __name__ == "__main__":
    run_grinder()
