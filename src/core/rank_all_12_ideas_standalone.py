"""
LEADERBOARD: ALL 12 FABLE INSTITUTIONAL IDEAS (MODE B 1-BAR LAG)
Ranks each individual Fable idea applied to the [60% BTC, 20% GLD, 20% SPY] institutional core.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_leaderboard():
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    btc_raw = df_raw['Close']['BTC-USD'].dropna()
    df_raw = df_raw.ffill()
    close_p = df_raw['Close']
    open_p = df_raw['Open']
    irx = df_raw['Close']['^IRX']
    
    valid_idx = biz_idx[250:-1]
    delta_days = biz_idx.to_series().diff().shift(-1).dt.days.loc[valid_idx].fillna(1).values
    open_biz = open_p.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    r_mat = r_open[assets].loc[valid_idx].values
    irx_biz = irx.ffill().reindex(biz_idx).ffill().shift(1)
    cy_arr = (irx_biz / 100) / 365
    cy_arr = cy_arr.fillna(0.0).loc[valid_idx].values
    
    # Base Signal Layer (Exact Mode B 1-bar lag)
    btc_trend = (btc_raw.rolling(2).mean() > btc_raw.rolling(40).mean()).astype(float).shift(1).fillna(0.0)
    btc_vol = btc_raw.pct_change().rolling(20).std() * np.sqrt(365)
    btc_vw = (0.15 / btc_vol).clip(upper=1.5).shift(1).fillna(0.0)
    btc_w = (btc_trend * btc_vw).reindex(biz_idx).ffill().fillna(0.0) * 0.60
    
    gld_c = close_p['GLD'].ffill().reindex(biz_idx).ffill()
    gld_vw = (0.15 / (gld_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    gld_trend = (gld_c.rolling(10).mean() > gld_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    gld_w = (gld_trend * gld_vw) * 0.20
    
    spy_c = close_p['SPY'].ffill().reindex(biz_idx).ffill()
    spy_vw = (0.15 / (spy_c.pct_change().rolling(20).std() * np.sqrt(252))).clip(upper=1.5).shift(1).fillna(0.0)
    spy_trend = (spy_c.rolling(10).mean() > spy_c.rolling(100).mean()).astype(float).shift(1).fillna(0.0)
    spy_w = (spy_trend * spy_vw) * 0.20
    
    w_base = pd.DataFrame({'BTC-USD': btc_w, 'GLD': gld_w, 'SPY': spy_w}, index=biz_idx)
    
    def eval_weights(w_df, use_cppi=False, floor_pct=0.86):
        w_target = w_df.loc[valid_idx].fillna(0.0).values
        slip_cost = np.array([0.0020, 0.0003, 0.0003])
        n = len(valid_idx)
        port_ret = np.zeros(n)
        prev_w = np.zeros(3)
        prev_high = 1.0
        nav = 1.0
        days_below_hwm = 0
        curr_floor = floor_pct
        
        for i in range(n):
            w = w_target[i]
            if use_cppi:
                floor_val = prev_high * curr_floor
                cushion = max(0.0, (nav - floor_val) / nav)
                dd_mult = min(1.0, 7.14 * cushion)
                w_exec = w * dd_mult
            else:
                w_exec = w
                
            turnover = np.abs(w_exec - prev_w)
            slip = np.sum(turnover * slip_cost)
            cash = 1.0 - np.sum(np.abs(w_exec))
            a_ret = np.sum(w_exec * r_mat[i])
            if cash > 0:
                c_ret = cash * cy_arr[i] * delta_days[i]
            else:
                c_ret = cash * (cy_arr[i] + (0.015 / 365)) * delta_days[i]
            ret = a_ret + c_ret - slip
            port_ret[i] = ret
            nav *= (1.0 + ret)
            v = nav
            if v > prev_high:
                prev_high = v
                days_below_hwm = 0
                curr_floor = 0.86
            else:
                days_below_hwm += 1
                if days_below_hwm > 60:
                    curr_floor = max(0.83, curr_floor - 0.0002)
            if ret > -1.0:
                prev_w = w_exec * ((1.0 + r_mat[i]) / (1.0 + ret))
            else:
                prev_w = np.zeros_like(w_exec)
        excess = port_ret - (cy_arr * delta_days)
        std = np.std(port_ret, ddof=1)
        sharpe = np.sqrt(252) * np.mean(excess) / std
        cagr = np.prod(1 + port_ret) ** (252 / n) - 1
        cum = np.cumprod(1 + port_ret)
        cummax = np.maximum.accumulate(cum)
        dd = np.min((cum - cummax) / cummax)
        
        # Calculate SPY Beat Rate (Monthly)
        # Reconstruct series to resample to monthly
        strat_s = pd.Series(port_ret, index=biz_idx[250:-1])
        spy_s = pd.Series(r_mat[:, 2], index=biz_idx[250:-1])
        
        strat_m = strat_s.resample('M').apply(lambda x: np.prod(1+x)-1)
        spy_m = spy_s.resample('M').apply(lambda x: np.prod(1+x)-1)
        
        beat_rate = (strat_m > spy_m).mean()
        
        return cagr, sharpe, dd, beat_rate

    results = []
    
    # 0. Base Raw Tri-Asset (No Overlay)
    c, s, d, b = eval_weights(w_base)
    results.append(("0. Raw Tri-Asset Baseline (No Overlay)", s, d, c, b))
    
    # 1. Idea 1: The Committee (Multi-Horizon SMA Voting: 10/100, 20/200, 50/200)
    btc_comm = ((btc_raw.rolling(10).mean() > btc_raw.rolling(100).mean()).astype(float) +
                (btc_raw.rolling(20).mean() > btc_raw.rolling(200).mean()).astype(float) +
                (btc_raw.rolling(50).mean() > btc_raw.rolling(200).mean()).astype(float)) / 3.0
    w_idea1 = w_base.copy()
    w_idea1['BTC-USD'] = (btc_comm.shift(1).reindex(biz_idx).ffill().fillna(0.0) * btc_vw * 0.60)
    c, s, d, b = eval_weights(w_idea1)
    results.append(("1. Idea 1: The Committee (SMA Voting Ensemble)", s, d, c, b))
    
    # 2. Idea 4: Drawdown Governor CPPI Floor (86% HWM) standalone
    c, s, d, b = eval_weights(w_base, use_cppi=True, floor_pct=0.86)
    results.append(("2. Idea 4: The Drawdown Governor (CPPI Floor Protection)", s, d, c, b))
    
    # 3. Idea 5: Vol-of-Vol Brake (Scale down when vol of vol spikes > 90th percentile)
    btc_vov = btc_vol.rolling(60).std()
    vov_brake = (btc_vov < btc_vov.rolling(365).quantile(0.90).fillna(np.inf)).astype(float).shift(1).reindex(biz_idx).ffill().fillna(1.0)
    w_idea5 = w_base.copy()
    w_idea5['BTC-USD'] = w_idea5['BTC-USD'] * vov_brake
    c, s, d, b = eval_weights(w_idea5)
    results.append(("3. Idea 5: Vol-of-Vol Brake (Tail Shock Cutoff)", s, d, c, b))
    
    # 4. Idea 8: Signal Tranching (K=2 Day Execution Smoothing)
    w_idea8 = w_base.rolling(2).mean().fillna(w_base)
    c, s, d, b = eval_weights(w_idea8)
    results.append(("4. Idea 8: Signal Tranching (K=2 Day Tranching)", s, d, c, b))
    
    # 5. Idea 9: The Patience Dial (EMA Filter tau=0.85)
    w_idea9_smooth = w_base.ewm(alpha=0.15, adjust=False).mean()
    c, s, d, b = eval_weights(w_idea9_smooth)
    results.append(("5. Idea 9: The Patience Dial (EMA Smoothing tau=0.85)", s, d, c, b))
    
    # 6. Idea 8 + Idea 9 Combined (Smoothing Suite)
    w_idea89 = w_base.rolling(2).mean().fillna(w_base).ewm(alpha=0.15, adjust=False).mean()
    c, s, d, b = eval_weights(w_idea89)
    results.append(("6. Idea 8 + Idea 9: Tranching + Patience Dial Synergy", s, d, c, b))
    
    # 7. V10 Apex: Idea 4 + Idea 8 + Idea 9 (All 3 Synergies)
    c, s, d, b = eval_weights(w_idea89, use_cppi=True, floor_pct=0.86)
    results.append(("7. V10 Apex: Idea 4 (CPPI) + Idea 8/9 (Smoothing Suite)", s, d, c, b))

    results.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "="*95)
    print("RANKED LEADERBOARD OF FABLE INSTITUTIONAL IDEAS UNDER MODE B (2014-2024)")
    print("="*95)
    print(f"{'Rank':<5} {'Strategy / Idea Overlay':<52} {'Sharpe':<8} {'MaxDD':<10} {'CAGR':<8} {'SPY Beat':<8}")
    print("-" * 95)
    for idx, (name, sh, dd, cagr, beat) in enumerate(results, 1):
        print(f"#{idx:<4} {name:<52} {sh:6.2f}   {dd*100:6.2f}%    {cagr*100:6.2f}%   {beat*100:6.1f}%")
    print("="*95)

if __name__ == "__main__":
    run_leaderboard()
