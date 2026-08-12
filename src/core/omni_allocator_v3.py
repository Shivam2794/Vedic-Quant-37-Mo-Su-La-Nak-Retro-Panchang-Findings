import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def get_vol_target_weights(raw_asset_returns, target_vol, month_ends):
    # Calculate volatility on the RAW asset, not the strategy, to avoid memory loss when allocation is 0
    vol20 = raw_asset_returns.rolling(20).std() * np.sqrt(252)
    vol_weights = pd.Series(np.nan, index=raw_asset_returns.index)
    for date in month_ends:
        if date not in vol20.index: continue
        cv = vol20.loc[date]
        if pd.isna(cv) or cv == 0: continue
        mult = target_vol / cv
        # Cap asset leverage natively
        mult = min(mult, 1.5)
        vol_weights.loc[date] = mult
    return vol_weights.ffill().shift(1).fillna(0.0)

def run_omni_allocator_v3():
    print("[*] Downloading Data for Omni-Allocator v3 (Structurally Sound)...")
    tickers = ['SPY', 'TLT', 'GLD', '^IRX', 'BTC-USD']
    df = yf.download(tickers, start="2014-09-17", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    # ---------------------------------------------------------
    # FIX: Filter to strict Business Days to prevent Weekend Dilution
    # ---------------------------------------------------------
    df = df[df.index.dayofweek < 5]
    
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
    btc_weights = (sma50 > sma200).astype(float).shift(1).fillna(0.0)
    # Target 20% vol on Bitcoin
    btc_vol_weights = get_vol_target_weights(returns['BTC-USD'], 0.20, month_ends)
    final_btc_weights = btc_weights * btc_vol_weights
    
    # ---------------------------------------------------------
    # STRATEGY 2: SPY Swing Trading
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
    # STRATEGY 3: TLT Trend (Vol-Targeted)
    # ---------------------------------------------------------
    tlt = df['TLT']
    if isinstance(tlt, pd.DataFrame): tlt = tlt.iloc[:, 0]
        
    tlt_sma50 = tlt.rolling(50).mean()
    tlt_sma200 = tlt.rolling(200).mean()
    tlt_weights = (tlt_sma50 > tlt_sma200).astype(float).shift(1).fillna(0.0)
    # Target 12% vol on TLT
    tlt_vol_weights = get_vol_target_weights(returns['TLT'], 0.12, month_ends)
    final_tlt_weights = tlt_weights * tlt_vol_weights
    
    # ---------------------------------------------------------
    # STRATEGY 4: GLD Trend (Vol-Targeted)
    # ---------------------------------------------------------
    gld = df['GLD']
    if isinstance(gld, pd.DataFrame): gld = gld.iloc[:, 0]
        
    gld_sma50 = gld.rolling(50).mean()
    gld_sma200 = gld.rolling(200).mean()
    gld_weights = (gld_sma50 > gld_sma200).astype(float).shift(1).fillna(0.0)
    # Target 12% vol on GLD
    gld_vol_weights = get_vol_target_weights(returns['GLD'], 0.12, month_ends)
    final_gld_weights = gld_weights * gld_vol_weights
    
    # ---------------------------------------------------------
    # TRUE MARGIN ALLOCATOR (Strict Base Allocations)
    # ---------------------------------------------------------
    valid_idx = returns.index[200:]
    r = returns.loc[valid_idx]
    daily_cash_yield = daily_cash_yield.loc[valid_idx]
    
    master_weights = pd.DataFrame(0.0, index=valid_idx, columns=['BTC-USD', 'SPY', 'TLT', 'GLD'])
    
    # Strict limits to keep portfolio drawdown below 20% natively
    # By removing the ensemble multiplier, the max portfolio leverage is strictly capped by these base allocations
    w_btc = 0.10
    w_spy = 0.30
    w_tlt = 0.30
    w_gld = 0.30
    
    master_weights['BTC-USD'] = final_btc_weights.loc[valid_idx] * w_btc
    master_weights['SPY'] = swing_weights.loc[valid_idx] * w_spy
    master_weights['TLT'] = final_tlt_weights.loc[valid_idx] * w_tlt
    master_weights['GLD'] = final_gld_weights.loc[valid_idx] * w_gld
    
    # Slippage per asset
    delta = master_weights.diff().abs().fillna(0)
    slip_btc = delta['BTC-USD'] * (30 / 10000)
    slip_spy = delta['SPY'] * (5 / 10000)
    slip_tlt = delta['TLT'] * (5 / 10000)
    slip_gld = delta['GLD'] * (5 / 10000)
    total_slippage = slip_btc + slip_spy + slip_tlt + slip_gld
    
    # Execution
    borrow_spread = 0.01 / 252
    final_port_ret = pd.Series(0.0, index=valid_idx)
    
    for date in valid_idx:
        w = master_weights.loc[date]
        gross = w.abs().sum()
        cash = 1.0 - gross
        
        a_ret = (w * r.loc[date]).sum()
        
        if cash > 0:
            c_ret = cash * daily_cash_yield.loc[date]
        else:
            c_ret = cash * (daily_cash_yield.loc[date] + borrow_spread)
            
        final_port_ret.loc[date] = a_ret + c_ret - total_slippage.loc[date]
    
    # ---------------------------------------------------------
    # CORRECTED SHARPE CALCULATION
    # ---------------------------------------------------------
    # Must subtract the risk-free rate from the numerator
    excess_ret = final_port_ret - daily_cash_yield
    
    cagr = (1 + final_port_ret).prod() ** (252 / len(final_port_ret)) - 1
    sharpe = np.sqrt(252) * excess_ret.mean() / (final_port_ret.std() + 1e-9)
    
    cum_ret = (1 + final_port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] DYNAMIC OMNI-ALLOCATOR V3 (Structurally Sound - Final)")
    print(f"CAGR: {cagr:.2%}")
    print(f"Sharpe: {sharpe:.2f}")
    print(f"Max DD: {max_dd:.2%}")
    
    spy_r = r['SPY']
    bm_cagr = (1 + spy_r).prod() ** (252 / len(spy_r)) - 1
    bm_excess = spy_r - daily_cash_yield
    bm_sharpe = np.sqrt(252) * bm_excess.mean() / (spy_r.std() + 1e-9)
    bm_max_dd = (((1 + spy_r).cumprod() - (1 + spy_r).cumprod().cummax()) / (1 + spy_r).cumprod().cummax()).min()
    print(f"[*] SPY BENCHMARK CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_omni_allocator_v3()
