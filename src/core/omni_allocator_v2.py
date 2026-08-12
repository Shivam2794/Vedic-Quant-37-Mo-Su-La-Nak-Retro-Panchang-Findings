import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 5 / 10000

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def run_omni_allocator_v2():
    print("[*] Downloading Data for Omni-Allocator v2...")
    tickers = ['SPY', '^VIX', '^VIX3M', 'SVXY', 'VIXY', '^IRX', 'BTC-USD']
    df = yf.download(tickers, start="2014-09-17", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    daily_cash_yield = (df['^IRX'] / 100) / 252
    daily_cash_yield = daily_cash_yield.fillna(0.0001)
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    
    # ---------------------------------------------------------
    # STRATEGY 1: Bitcoin Trend (Vol-Targeted)
    # ---------------------------------------------------------
    btc = df['BTC-USD']
    if isinstance(btc, pd.DataFrame): btc = btc.iloc[:, 0]
        
    sma50 = btc.rolling(50).mean()
    sma200 = btc.rolling(200).mean()
    
    btc_weights = pd.Series(0.0, index=df.index)
    for i in range(len(df)):
        if pd.isna(sma200.iloc[i]): continue
        if sma50.iloc[i] > sma200.iloc[i]:
            btc_weights.iloc[i] = 1.0

    btc_weights = btc_weights.shift(1).fillna(0.0)
    
    btc_ret_stream = btc_weights * returns['BTC-USD']
    btc_vol20 = btc_ret_stream.rolling(20).std() * np.sqrt(252)
    btc_vol_weights = pd.Series(1.0, index=df.index)
    for date in month_ends:
        if date not in btc_vol20.index: continue
        cv = btc_vol20.loc[date]
        if pd.isna(cv) or cv == 0: continue
        mult = 0.20 / cv # Target 20% BTC Vol
        mult = min(mult, 1.0)
        btc_vol_weights.loc[date] = mult
    
    btc_vol_weights = btc_vol_weights.ffill().shift(1).fillna(0.0)
    final_btc_weights = btc_weights * btc_vol_weights
    
    # ---------------------------------------------------------
    # STRATEGY 2: Swing Trading (SPY)
    # ---------------------------------------------------------
    spy = df['SPY']
    if isinstance(spy, pd.DataFrame): spy = spy.iloc[:, 0]
        
    spy_sma200 = spy.rolling(200).mean()
    spy_sma5 = spy.rolling(5).mean()
    rsi2 = rsi(spy, 2)
    ma20 = spy.rolling(20).mean()
    std20 = spy.rolling(20).std()
    lower_bb = ma20 - (2 * std20)
    
    swing_weights = pd.Series(0.0, index=df.index)
    in_position = False
    
    for i in range(len(df)):
        date = df.index[i]
        if pd.isna(spy_sma200.iloc[i]): continue
        if in_position and spy.iloc[i] > spy_sma5.iloc[i]:
            in_position = False
        if not in_position and spy.iloc[i] < lower_bb.iloc[i] and rsi2.iloc[i] < 5 and spy.iloc[i] > spy_sma200.iloc[i]:
            in_position = True
        if in_position:
            swing_weights.loc[date] = 1.0

    swing_weights = swing_weights.shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # STRATEGY 3: VRP Hedged
    # ---------------------------------------------------------
    term_structure = df['^VIX'] / df['^VIX3M']
    vrp_weights = pd.DataFrame(0.0, index=df.index, columns=['SVXY', 'VIXY'])
    
    for i in range(len(df)):
        date = df.index[i]
        raw_ts = term_structure.iloc[i]
        if pd.isna(raw_ts): continue
            
        if raw_ts > 1.05:
            vrp_weights.loc[date, 'VIXY'] = 1.0
        elif raw_ts < 0.95: 
            vrp_weights.loc[date, 'SVXY'] = 1.0

    vrp_weights = vrp_weights.shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # TRUE MARGIN ALLOCATOR
    # ---------------------------------------------------------
    valid_idx = returns.index.intersection(final_btc_weights.index).intersection(swing_weights.index).intersection(vrp_weights.index)[200:]
    r = returns.loc[valid_idx]
    daily_cash_yield = daily_cash_yield.loc[valid_idx]
    
    master_weights = pd.DataFrame(0.0, index=valid_idx, columns=['BTC-USD', 'SPY', 'SVXY', 'VIXY'])
    
    # Weight allocations
    w_btc = 0.15
    w_swing = 0.45
    w_vrp = 0.15
    
    master_weights['BTC-USD'] = final_btc_weights.loc[valid_idx] * w_btc
    master_weights['SPY'] = swing_weights.loc[valid_idx] * w_swing
    master_weights['SVXY'] = vrp_weights.loc[valid_idx, 'SVXY'] * w_vrp
    master_weights['VIXY'] = vrp_weights.loc[valid_idx, 'VIXY'] * w_vrp
    
    # Return on assets
    asset_ret = (master_weights * r[master_weights.columns]).sum(axis=1)
    
    # Cash accounting
    gross_exposure = master_weights.abs().sum(axis=1)
    cash_position = 1.0 - gross_exposure
    
    borrow_spread = 0.01 / 252
    cash_ret = pd.Series(0.0, index=valid_idx)
    
    for date, cash in cash_position.items():
        if cash > 0:
            cash_ret.loc[date] = cash * daily_cash_yield.loc[date]
        else:
            cash_ret.loc[date] = cash * (daily_cash_yield.loc[date] + borrow_spread)
            
    # Slippage
    delta = master_weights.diff().abs().fillna(0)
    slip_btc = delta['BTC-USD'] * (30 / 10000)
    slip_spy = delta['SPY'] * (5 / 10000)
    slip_svxy = delta['SVXY'] * (15 / 10000)
    slip_vixy = delta['VIXY'] * (15 / 10000)
    
    total_slippage = slip_btc + slip_spy + slip_svxy + slip_vixy
    
    port_ret = asset_ret + cash_ret - total_slippage
    
    # ---------------------------------------------------------
    # DYNAMIC ENSEMBLE VOLATILITY TARGETING
    # ---------------------------------------------------------
    ENS_TARGET_VOL = 0.05 # Target 5% to force DD < 20%
    ens_vol = port_ret.rolling(20).std() * np.sqrt(252)
    ens_multiplier = pd.Series(1.0, index=port_ret.index)
    
    for date in month_ends:
        if date not in ens_vol.index: continue
        cv = ens_vol.loc[date]
        if pd.isna(cv) or cv == 0: continue
            
        mult = ENS_TARGET_VOL / cv
        mult = min(mult, 0.5)
        ens_multiplier.loc[date] = mult
        
    ens_multiplier = ens_multiplier.ffill().shift(1).fillna(1.0)
    
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    for i, date in enumerate(valid_idx):
        mult = ens_multiplier.loc[date]
        w = master_weights.loc[date] * mult
        gross = w.abs().sum()
        cash = 1.0 - gross
        
        a_ret = (w * r.loc[date, w.index]).sum()
        
        if cash > 0:
            c_ret = cash * daily_cash_yield.loc[date]
        else:
            c_ret = cash * (daily_cash_yield.loc[date] + borrow_spread)
            
        if i > 0:
            prev_w = master_weights.loc[valid_idx[i-1]] * ens_multiplier.loc[valid_idx[i-1]]
            d = (w - prev_w).abs()
            s = (d['BTC-USD'] * 30/10000) + (d['SPY'] * 5/10000) + (d['SVXY'] * 15/10000) + (d['VIXY'] * 15/10000)
        else:
            s = 0.0
            
        final_port_ret.loc[date] = a_ret + c_ret - s
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * final_port_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] DYNAMIC OMNI-ALLOCATOR V2 (BTC/SPY/VRP)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    
    spy_r = r['SPY']
    bm_cagr = (1 + spy_r).prod() ** (252 / len(spy_r)) - 1
    bm_sharpe = np.sqrt(252) * spy_r.mean() / (spy_r.std() + 1e-9)
    bm_max_dd = (((1 + spy_r).cumprod() - (1 + spy_r).cumprod().cummax()) / (1 + spy_r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_allocator_v2()
