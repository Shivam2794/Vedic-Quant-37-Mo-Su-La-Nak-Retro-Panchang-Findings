import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def rsi(series, period=2):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period-1, adjust=False).mean()
    ema_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

def run_omni_ensemble_ultimate():
    print("[*] Downloading Data for Ultimate Omni-Ensemble...")
    tickers = ['UPRO', 'TMF', 'SPY', '^VIX', '^VIX3M', 'SVXY', 'VIXY', 'SHV']
    df = yf.download(tickers, start="2012-01-01", end="2024-01-01")['Close']
    df = df[~df.index.duplicated(keep='first')]
    df = df.ffill().dropna()
    
    returns = df.pct_change().dropna()
    
    # ---------------------------------------------------------
    # STRATEGY 1: Volatility-Targeted Hedgefundie
    # ---------------------------------------------------------
    upro_w = 0.55
    tmf_w = 0.45
    
    base_hf_ret = returns['UPRO'] * upro_w + returns['TMF'] * tmf_w
    hf_vol20 = base_hf_ret.rolling(20).std() * np.sqrt(252)
    TARGET_VOL = 0.10
    
    df['YearMonth'] = df.index.to_period('M')
    month_ends = df.groupby('YearMonth').tail(1).index
    hf_weights = pd.DataFrame(np.nan, index=df.index, columns=['UPRO', 'TMF', 'SHV'])
    
    for date in month_ends:
        if date not in hf_vol20.index: continue
        cv = hf_vol20.loc[date]
        if isinstance(cv, pd.Series): cv = cv.iloc[0]
        if pd.isna(cv) or cv == 0: continue
            
        mult = TARGET_VOL / cv
        mult = min(mult, 1.0)
        hf_weights.loc[date, 'UPRO'] = upro_w * mult
        hf_weights.loc[date, 'TMF'] = tmf_w * mult
        hf_weights.loc[date, 'SHV'] = 1.0 - mult

    hf_weights = hf_weights.ffill().shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # STRATEGY 2: High-Winrate Mean Reversion (Swing)
    # ---------------------------------------------------------
    spy = df['SPY']
    if isinstance(spy, pd.DataFrame): spy = spy.iloc[:, 0]
        
    sma200 = spy.rolling(200).mean()
    sma5 = spy.rolling(5).mean()
    rsi2 = rsi(spy, 2)
    ma20 = spy.rolling(20).mean()
    std20 = spy.rolling(20).std()
    lower_bb = ma20 - (2 * std20)
    
    swing_weights = pd.Series(0.0, index=df.index)
    in_position = False
    
    for i in range(len(df)):
        date = df.index[i]
        if pd.isna(sma200.iloc[i]): continue
        if in_position and spy.iloc[i] > sma5.iloc[i]:
            in_position = False
        if not in_position and spy.iloc[i] < lower_bb.iloc[i] and rsi2.iloc[i] < 5 and spy.iloc[i] > sma200.iloc[i]:
            in_position = True
        if in_position:
            swing_weights.loc[date] = 1.0

    swing_weights = swing_weights.shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # STRATEGY 3: VRP Hedged
    # ---------------------------------------------------------
    term_structure = df['^VIX'] / df['^VIX3M']
    vrp_weights = pd.DataFrame(0.0, index=df.index, columns=['SVXY', 'VIXY', 'SHV'])
    
    for i in range(len(df)):
        date = df.index[i]
        raw_ts = term_structure.iloc[i]
        if pd.isna(raw_ts):
            vrp_weights.loc[date, 'SHV'] = 1.0
            continue
        if raw_ts > 1.05:
            vrp_weights.loc[date, 'VIXY'] = 1.0
        elif raw_ts < 0.95: 
            vrp_weights.loc[date, 'SVXY'] = 1.0
        else:
            vrp_weights.loc[date, 'SHV'] = 1.0

    vrp_weights = vrp_weights.shift(1).fillna(0.0)
    
    # ---------------------------------------------------------
    # COMBINE ENSEMBLE (40% HF / 40% Swing / 20% VRP)
    # ---------------------------------------------------------
    valid_idx = returns.index.intersection(hf_weights.index).intersection(swing_weights.index).intersection(vrp_weights.index)[200:]
    hf_weights = hf_weights.loc[valid_idx]
    swing_weights = swing_weights.loc[valid_idx]
    vrp_weights = vrp_weights.loc[valid_idx]
    r = returns.loc[valid_idx]
    
    r_shv = 0.02 / 252
    
    hf_delta = hf_weights.diff().abs().sum(axis=1).fillna(0)
    hf_ret = (hf_weights['UPRO'] * r['UPRO']) + (hf_weights['TMF'] * r['TMF']) + (hf_weights['SHV'] * r_shv)
    hf_ret -= (hf_delta * SLIPPAGE_BPS)
    
    swing_delta = swing_weights.diff().abs().fillna(0)
    swing_ret = (swing_weights * r['SPY']) + ((1.0 - swing_weights) * r_shv)
    swing_ret -= (swing_delta * SLIPPAGE_BPS)
    
    vrp_delta = vrp_weights.diff().abs().sum(axis=1).fillna(0)
    vrp_ret = (vrp_weights['SVXY'] * r['SVXY']) + (vrp_weights['VIXY'] * r['VIXY']) + (vrp_weights['SHV'] * r_shv)
    vrp_ret -= (vrp_delta * SLIPPAGE_BPS)
    
    port_ret = (hf_ret * 0.40) + (swing_ret * 0.40) + (vrp_ret * 0.20)
    
    # Target entire ensemble to 8% Volatility to absolutely CRUSH the drawdown
    ens_vol = port_ret.rolling(20).std() * np.sqrt(252)
    ens_weights = pd.Series(1.0, index=port_ret.index)
    for date in month_ends:
        if date not in ens_vol.index: continue
        cv = ens_vol.loc[date]
        if pd.isna(cv) or cv == 0: continue
        ens_weights.loc[date] = 0.08 / cv
    
    ens_weights = ens_weights.ffill().shift(1).fillna(1.0)
    ens_weights = ens_weights.clip(upper=1.5) # Cap leverage at 1.5x
    
    port_ret = (port_ret * ens_weights) + ((1.0 - ens_weights) * r_shv)
    
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    
    cum_ret = (1 + port_ret).cumprod()
    max_dd = ((cum_ret - cum_ret.cummax()) / cum_ret.cummax()).min()
    
    print("========================================================")
    print(f"[*] ULTIMATE OMNI-ENSEMBLE (HF + Swing + VRP) RESULTS")
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
    run_omni_ensemble_ultimate()
