import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

def calc_metrics(returns, risk_free=0.02):
    if len(returns) == 0:
        return 0, 0, 0
    cum_ret = (1 + returns).cumprod()
    cagr = (cum_ret.iloc[-1] ** (252 / len(returns))) - 1
    
    vol = returns.std() * np.sqrt(252)
    sharpe = (cagr - risk_free) / vol if vol > 0 else 0
    
    roll_max = cum_ret.cummax()
    drawdown = (cum_ret - roll_max) / roll_max
    max_dd = drawdown.min()
    return cagr, max_dd, sharpe

def optimize_relief_rotation_v4():
    print("[*] BRUTAL INSPECTION FIX: Fetching auto_adjust=True (Total Return) and SHV (Real Cash Yield)...")
    tickers = ["QQQ", "DIA", "TLT", "SHV", "HYG", "^VIX"]
    
    try:
        # auto_adjust=True handles all dividend/split adjustments automatically directly in the 'Close' column
        raw_data = yf.download(tickers, start="2010-01-01", end="2024-01-01", progress=False, auto_adjust=True)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
        
    data = raw_data['Close'].dropna()
    returns = data.pct_change()
    
    # Check column formats based on yfinance versions
    qqq = data['QQQ'] if isinstance(data, pd.DataFrame) else data.xs('QQQ', axis=1, level=1)
    dia = data['DIA']
    tlt = data['TLT']
    shv = data['SHV']
    hyg = data['HYG']
    vix = data['^VIX']
    
    # 1. ENSEMBLE RELATIVE MOMENTUM (20d, 60d)
    qqq_mom = (qqq.pct_change(20) + qqq.pct_change(60)) / 2
    dia_mom = (dia.pct_change(20) + dia.pct_change(60)) / 2
    
    # 2. CREDIT CONTAGION GATE (HYG Momentum)
    credit_panic = hyg.pct_change(20) < -0.015 
    
    # 3. VOLATILITY REGIME
    vix_spike = vix > 25
    bear_market = (qqq.pct_change(120) < 0) & (dia.pct_change(120) < 0)
    
    # 4. INFLATION REGIME GATE
    bonds_toxic = tlt.pct_change(120) < 0
    
    risk_off = credit_panic | vix_spike | bear_market
    
    weight_qqq = pd.Series(0.0, index=data.index)
    weight_dia = pd.Series(0.0, index=data.index)
    weight_tlt = pd.Series(0.0, index=data.index)
    weight_shv = pd.Series(0.0, index=data.index)
    
    # RISK OFF ALLOCATION:
    weight_tlt[risk_off & ~bonds_toxic] = 1.0
    weight_shv[risk_off & bonds_toxic] = 1.0
    
    # RISK ON ALLOCATION:
    risk_on = ~risk_off
    qqq_is_stronger = qqq_mom > dia_mom
    
    weight_qqq[risk_on & qqq_is_stronger] = 1.0
    weight_dia[risk_on & ~qqq_is_stronger] = 1.0
    
    # BRUTAL FIX: SHIFT WEIGHTS TO PREVENT LOOKAHEAD BIAS
    weight_qqq = weight_qqq.shift(1).fillna(0)
    weight_dia = weight_dia.shift(1).fillna(0)
    weight_tlt = weight_tlt.shift(1).fillna(0)
    weight_shv = weight_shv.shift(1).fillna(0)
    
    # Calculate Base Returns
    strat_returns = (weight_qqq * returns['QQQ']) + (weight_dia * returns['DIA']) + \
                    (weight_tlt * returns['TLT']) + (weight_shv * returns['SHV'])
                    
    # BRUTAL FIX: TRANSACTION COSTS (10 bps per one-way trade)
    turnover = weight_qqq.diff().abs() + weight_dia.diff().abs() + \
               weight_tlt.diff().abs() + weight_shv.diff().abs()
    turnover = turnover / 2.0
    tcost_bps = 0.0010  
    strat_returns = strat_returns - (turnover * tcost_bps)
    
    cagr, max_dd, sharpe = calc_metrics(strat_returns)
    
    # BRUTAL FIX: VOLATILITY TARGETING WITH BORROWING COSTS
    rolling_vol = strat_returns.rolling(20).std() * np.sqrt(252)
    target_vol = 0.15
    leverage = (target_vol / rolling_vol.replace(0, np.nan)).clip(lower=0.5, upper=2.0).shift(1).fillna(1.0)
    
    # Borrowing Cost
    borrowing_cost = np.where(leverage > 1.0, (leverage - 1.0) * returns['SHV'], 0.0)
    
    vt_returns = (strat_returns * leverage) - borrowing_cost
    
    lev_turnover = leverage.diff().abs()
    vt_returns = vt_returns - (lev_turnover * tcost_bps)
    
    vt_cagr, vt_max_dd, vt_sharpe = calc_metrics(vt_returns)
    
    bm_returns = (0.5 * returns['QQQ']) + (0.5 * returns['DIA'])
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(bm_returns)
    
    print("\n========================================================")
    print("BRUTAL INSPECTION FINAL: BULLETPROOF RELIEF ROTATION V4")
    print("========================================================")
    print(f"BENCHMARK (50% QQQ / 50% DIA) (Total Return):")
    print(f"CAGR: {bm_cagr*100:.2f}% | Max DD: {bm_dd*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print("--------------------------------------------------------")
    print(f"V4 BASE (Total Return + 10bps Slippage + SHV Safety):")
    print(f"CAGR: {cagr*100:.2f}% | Max DD: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")
    print("--------------------------------------------------------")
    print(f"V4 VOL-TARGETED (Slippage + Borrowing Costs Deducted):")
    print(f"CAGR: {vt_cagr*100:.2f}% | Max DD: {vt_max_dd*100:.2f}% | Sharpe: {vt_sharpe:.2f}")
    print("========================================================\n")

if __name__ == "__main__":
    optimize_relief_rotation_v4()
