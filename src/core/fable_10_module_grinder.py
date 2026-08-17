import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from fable_generated_grinder import run_fable_grinder

def get_data():
    assets = ['BTC-USD', 'GLD', 'SPY']
    tickers = assets + ['^IRX']
    df_raw = yf.download(tickers, start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
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
    
    # Base Signal Layer
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
    return w_base, r_mat, cy_arr, delta_days, valid_idx, btc_raw, btc_vol, btc_vw

def eval_weights_series(w_df, r_mat, cy_arr, delta_days, valid_idx, use_cppi=False, floor_pct=0.86, slippage_multiplier=1.0):
    w_target = w_df.loc[valid_idx].fillna(0.0).values
    slip_cost = np.array([0.0020, 0.0003, 0.0003]) * slippage_multiplier
    n = len(valid_idx)
    port_ret = np.zeros(n)
    prev_w = np.zeros(3)
    prev_high = 1.0
    nav = 1.0
    curr_floor = floor_pct
    days_below_hwm = 0
    
    # Store daily turnover for custom pre-2018 penalty
    turnover_arr = np.zeros(n)
    
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
        turnover_arr[i] = turnover[0] # Only track BTC turnover for pre-2018 penalty
        
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
            
    return pd.Series(port_ret, index=valid_idx), pd.Series(turnover_arr, index=valid_idx)

def run_pre2018_execution_test(port_ret, btc_turnover_series, valid_idx):
    # Fable Point 7: Pre-2018 costs at 75bps
    # We will subtract an additional 55bps per BTC turnover (since 20bps was already charged) prior to Jan 2018.
    
    ret_adj = port_ret.copy()
    pre_2018_mask = valid_idx < pd.Timestamp("2018-01-01")
    
    # Extra 55bps slippage on BTC turnover
    extra_slip = btc_turnover_series[pre_2018_mask] * 0.0055 
    ret_adj.loc[pre_2018_mask] -= extra_slip
    
    std = np.std(ret_adj, ddof=1)
    sharpe = np.sqrt(252) * np.mean(ret_adj) / std if std > 0 else 0
    return sharpe

def main():
    print("Building Alpha & Armor Modules...")
    w_base, r_mat, cy_arr, delta_days, valid_idx, btc_raw, btc_vol, btc_vw = get_data()
    
    strategies = {}
    biz_idx = w_base.index
    
    # 0. Base Raw Tri-Asset
    ret, turn = eval_weights_series(w_base, r_mat, cy_arr, delta_days, valid_idx)
    strategies['0_Base_60_20_20'] = (ret, turn)
    
    # 1. Idea 1: The Committee
    btc_comm = ((btc_raw.rolling(10).mean() > btc_raw.rolling(100).mean()).astype(float) +
                (btc_raw.rolling(20).mean() > btc_raw.rolling(200).mean()).astype(float) +
                (btc_raw.rolling(50).mean() > btc_raw.rolling(200).mean()).astype(float)) / 3.0
    w_idea1 = w_base.copy()
    w_idea1['BTC-USD'] = (btc_comm.shift(1).reindex(biz_idx).ffill().fillna(0.0) * btc_vw * 0.60)
    ret, turn = eval_weights_series(w_idea1, r_mat, cy_arr, delta_days, valid_idx)
    strategies['1_Idea_1_Committee'] = (ret, turn)
    
    # 2. Idea 2: Trend + RSI
    rsi = 100 - (100 / (1 + btc_raw.diff().clip(lower=0).rolling(14).mean() / btc_raw.diff().clip(upper=0).abs().rolling(14).mean()))
    rsi_sig = (rsi < 70).astype(float).shift(1).reindex(biz_idx).ffill().fillna(1.0)
    w_idea2 = w_base.copy()
    w_idea2['BTC-USD'] = w_idea2['BTC-USD'] * rsi_sig
    ret, turn = eval_weights_series(w_idea2, r_mat, cy_arr, delta_days, valid_idx)
    strategies['2_Idea_2_TrendRSI'] = (ret, turn)
    
    # 3. Idea 3: Adaptive MA
    btc_ama = btc_raw.rolling(10).mean() # simplified
    w_idea3 = w_base.copy()
    w_idea3['BTC-USD'] = (btc_raw > btc_ama).astype(float).shift(1).reindex(biz_idx).ffill().fillna(0.0) * btc_vw * 0.6
    ret, turn = eval_weights_series(w_idea3, r_mat, cy_arr, delta_days, valid_idx)
    strategies['3_Idea_3_AdaptiveMA'] = (ret, turn)
    
    # 4. Idea 4: CPPI Drawdown Governor
    ret, turn = eval_weights_series(w_base, r_mat, cy_arr, delta_days, valid_idx, use_cppi=True)
    strategies['4_Idea_4_CPPI'] = (ret, turn)
    
    # 5. Idea 5: Vol-of-Vol Brake
    btc_vov = btc_vol.rolling(60).std()
    vov_brake = (btc_vov < btc_vov.rolling(365).quantile(0.90).fillna(np.inf)).astype(float).shift(1).reindex(biz_idx).ffill().fillna(1.0)
    w_idea5 = w_base.copy()
    w_idea5['BTC-USD'] = w_idea5['BTC-USD'] * vov_brake
    ret, turn = eval_weights_series(w_idea5, r_mat, cy_arr, delta_days, valid_idx)
    strategies['5_Idea_5_VoVBrake'] = (ret, turn)
    
    # 6. Idea 6: Bollinger Band
    std20 = btc_raw.rolling(20).std()
    ma20 = btc_raw.rolling(20).mean()
    bb_sig = (btc_raw < ma20 + 2*std20).astype(float).shift(1).reindex(biz_idx).ffill().fillna(1.0)
    w_idea6 = w_base.copy()
    w_idea6['BTC-USD'] = w_idea6['BTC-USD'] * bb_sig
    ret, turn = eval_weights_series(w_idea6, r_mat, cy_arr, delta_days, valid_idx)
    strategies['6_Idea_6_Bollinger'] = (ret, turn)
    
    # 7. Idea 7: Vol Adjusted Momentum
    w_idea7 = w_base.copy()
    w_idea7['BTC-USD'] = w_idea7['BTC-USD'] * 0.8
    ret, turn = eval_weights_series(w_idea7, r_mat, cy_arr, delta_days, valid_idx)
    strategies['7_Idea_7_VolMom'] = (ret, turn)
    
    # 8. Idea 8: Signal Tranching
    w_idea8 = w_base.rolling(2).mean().fillna(w_base)
    ret, turn = eval_weights_series(w_idea8, r_mat, cy_arr, delta_days, valid_idx)
    strategies['8_Idea_8_Tranching'] = (ret, turn)
    
    # 9. Idea 9: Patience Dial
    w_idea9 = w_base.ewm(alpha=0.15, adjust=False).mean()
    ret, turn = eval_weights_series(w_idea9, r_mat, cy_arr, delta_days, valid_idx)
    strategies['9_Idea_9_Patience'] = (ret, turn)
    
    # 10. V10 Apex (CPPI + Tranching + Patience)
    w_v10 = w_base.rolling(2).mean().fillna(w_base).ewm(alpha=0.15, adjust=False).mean()
    ret, turn = eval_weights_series(w_v10, r_mat, cy_arr, delta_days, valid_idx, use_cppi=True)
    strategies['10_V10_Apex'] = (ret, turn)
    
    base_ret = strategies['0_Base_60_20_20'][0]
    btc_ret = pd.Series(r_mat[:, 0], index=valid_idx)
    
    print("\n" + "="*80)
    print("FABLE'S 9-POINT GRINDER: ALL 10 MODULES")
    print("="*80)
    
    # Run Fable's Code on All 10
    for name, (ret, turn) in strategies.items():
        print(f"\nEvaluating: {name}")
        # Run Fable's Core 6 Points
        fable_res = run_fable_grinder(ret, btc_ret, base_ret)
        
        # Run My Point 7: Pre-2018 Strict Slippage
        pre2018_sr = run_pre2018_execution_test(ret, turn, valid_idx)
        print(f"[7] PRE-2018 75BPS + GAP PENALTY: Sharpe {pre2018_sr:.3f}")
        
    print("\n[8] CROSS-CORRELATION MATRIX (Top 3 Overlays)")
    df_corr = pd.DataFrame({
        'Idea4': strategies['4_Idea_4_CPPI'][0],
        'Idea5': strategies['5_Idea_5_VoVBrake'][0],
        'Idea9': strategies['9_Idea_9_Patience'][0]
    })
    print(df_corr.corr())
    
if __name__ == "__main__":
    main()
