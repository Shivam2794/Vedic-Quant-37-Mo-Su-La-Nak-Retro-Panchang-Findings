import yfinance as yf
import pandas as pd
import numpy as np

# Suppress SettingWithCopyWarning
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

def backtest_drift_regime():
    print("[*] Backtesting Strategy #1: Drift Regime Cross-Sectional Factor")
    # Top 20 liquid S&P 500 stocks
    tickers = ["AAPL","MSFT","GOOG","AMZN","META","TSLA","NVDA","JPM","BAC","WFC",
               "PG","JNJ","XOM","CVX","HD","MA","V","UNH","ABBV","LLY"]
    
    try:
        data = yf.download(tickers, start="2015-01-01", end="2024-01-01", progress=False)['Close']
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    # Drop any that don't have full history
    data = data.dropna(axis=1)
    returns = data.pct_change()
    
    # 1. Drift Regime Condition: >60% positive days in trailing 63 days
    is_positive = (returns > 0).astype(float)
    rolling_positive_pct = is_positive.rolling(window=63).mean()
    drift_regime = (rolling_positive_pct > 0.60).astype(float)
    
    # 2. Short-Term Reversal: 5-day return. We want to buy if 5-day return is deeply negative
    return_5d = data.pct_change(5)
    
    # Value Proxy: Distance below 20-day MA
    ma_20 = data.rolling(20).mean()
    val_proxy = (ma_20 - data) / ma_20 # Positive means it's below MA (cheap)
    
    # Signal = Drift Regime * Value * Reversal
    # We buy (weight > 0) when it's in a drift regime, it's cheap, and 5d return is negative
    raw_signal = drift_regime * (val_proxy > 0).astype(float) * (return_5d < 0).astype(float)
    
    # To rank cross-sectionally, we just equal weight whatever passes the filter
    pos_sum = raw_signal.sum(axis=1).replace(0, np.nan)
    weights = raw_signal.div(pos_sum, axis=0).fillna(0)
    
    # Shift to avoid lookahead
    weights = weights.shift(1)
    
    strat_returns = (weights * returns).sum(axis=1)
    cagr, max_dd, sharpe = calc_metrics(strat_returns)
    
    print("--------------------------------------------------")
    print("STRATEGY 1: DRIFT REGIME")
    print(f"CAGR: {cagr*100:.2f}% | Max Drawdown: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")
    print("--------------------------------------------------\n")


def backtest_relief_rotation():
    print("[*] Backtesting Strategy #2: Relief-Gated Relative Rotation (QQQ-DIA)")
    try:
        data = yf.download(["QQQ", "DIA", "^VIX", "^TNX"], start="2015-01-01", end="2024-01-01", progress=False)['Close']
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
        
    data = data.dropna()
    qqq = data['QQQ']
    dia = data['DIA']
    vix = data['^VIX']
    tnx = data['^TNX']
    
    qqq_ret = qqq.pct_change()
    dia_ret = dia.pct_change()
    
    # Relative states
    qqq_mom = qqq.pct_change(20)
    dia_mom = dia.pct_change(20)
    relative_strength = qqq_mom - dia_mom
    
    # Relief conditions
    vix_relief = (vix < 20) | (vix.diff(5) < 0)
    rate_relief = tnx.diff(20) < 0
    relief_condition = vix_relief | rate_relief
    
    # Allocation mapping
    # If QQQ is stronger AND we have relief -> 100% QQQ
    # Else -> 100% DIA (defensive/value)
    
    qqq_weight = np.where((relative_strength > 0) & relief_condition, 1.0, 0.0)
    dia_weight = 1.0 - qqq_weight
    
    qqq_weight = pd.Series(qqq_weight, index=data.index).shift(1).fillna(0)
    dia_weight = pd.Series(dia_weight, index=data.index).shift(1).fillna(0)
    
    strat_returns = (qqq_weight * qqq_ret) + (dia_weight * dia_ret)
    cagr, max_dd, sharpe = calc_metrics(strat_returns)
    
    # Benchmark 50/50
    bm_returns = (0.5 * qqq_ret) + (0.5 * dia_ret)
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(bm_returns)
    
    print("--------------------------------------------------")
    print("STRATEGY 2: RELIEF-GATED QQQ-DIA ROTATION")
    print(f"CAGR: {cagr*100:.2f}% | Max Drawdown: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")
    print(f"Benchmark 50/50 -> CAGR: {bm_cagr*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print("--------------------------------------------------\n")


def backtest_gold_atr():
    print("[*] Backtesting Strategy #3: Forecast-to-Fill Gold (GLD)")
    try:
        data = yf.download(["GLD"], start="2015-01-01", end="2024-01-01", progress=False)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
        
    data = data.dropna()
    close = data['Close']['GLD'] if isinstance(data.columns, pd.MultiIndex) else data['Close']
    high = data['High']['GLD'] if isinstance(data.columns, pd.MultiIndex) else data['High']
    low = data['Low']['GLD'] if isinstance(data.columns, pd.MultiIndex) else data['Low']
    
    returns = close.pct_change()
    
    # State variables: Trend and Momentum
    ma_200 = close.rolling(200).mean()
    mom_20 = close.pct_change(20)
    
    # Smoothed trend-momentum regime
    trend_up = (close > ma_200).astype(float)
    mom_up = (mom_20 > 0).astype(float)
    signal = trend_up * mom_up # 1 if uptrend AND positive momentum, else 0
    
    # ATR Calculation
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    
    # Volatility targeting (15% annualized)
    daily_vol_target = 0.15 / np.sqrt(252)
    rolling_vol = returns.rolling(20).std()
    # Fractional Kelly sizing proxy: limit leverage to max 2.0
    raw_leverage = daily_vol_target / rolling_vol.replace(0, np.nan)
    leverage = raw_leverage.clip(lower=0, upper=2.0)
    
    weight = signal * leverage
    weight = weight.shift(1).fillna(0)
    
    # Frictional cost (0.7 bps linear)
    turnover = weight.diff().abs()
    tcost = turnover * 0.00007
    
    strat_returns = (weight * returns) - tcost
    cagr, max_dd, sharpe = calc_metrics(strat_returns)
    
    bm_cagr, bm_dd, bm_sharpe = calc_metrics(returns)
    
    print("--------------------------------------------------")
    print("STRATEGY 3: FORECAST-TO-FILL GOLD")
    print(f"CAGR: {cagr*100:.2f}% | Max Drawdown: {max_dd*100:.2f}% | Sharpe: {sharpe:.2f}")
    print(f"Benchmark GLD Buy&Hold -> CAGR: {bm_cagr*100:.2f}% | Sharpe: {bm_sharpe:.2f}")
    print("--------------------------------------------------\n")


if __name__ == "__main__":
    backtest_drift_regime()
    backtest_relief_rotation()
    backtest_gold_atr()
