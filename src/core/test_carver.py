import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from carver_master_strategy import CarverSystem

def synthetic_prices(n=2600, seed=7, s0=200.0, mu_arr=None, sig_arr=None):
    """5-state Markov regime (bull/bear/chop) with persistent vol clustering."""
    rng = np.random.default_rng(seed)
    P = np.array([[0.95, 0.02, 0.03], [0.02, 0.96, 0.02], [0.02, 0.02, 0.96]])
    
    if mu_arr is None:
        mu_arr = [0.0012, -0.0005, 0.0]
    if sig_arr is None:
        sig_arr = [0.030, 0.065, 0.025]
        
    mu, sig = np.array(mu_arr), np.array(sig_arr)
    st, logs, v_out = 0, [], []
    for _ in range(n):
        st = rng.choice(3, p=P[st])
        logr = mu[st] + sig[st] * rng.normal()
        logs.append(logr)
        v_out.append(np.exp(logr))
        
    idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq="D")
    prices = pd.Series(v_out, index=idx).cumprod() * s0
    return prices

def main():
    print("Generating Synthetic Data...")
    # Generate Synthetic BTC
    btc = synthetic_prices(n=2600, seed=42, s0=100.0)
    
    # Generate Synthetic SPY
    spy = synthetic_prices(n=2600, seed=7, s0=200.0, mu_arr=[0.0005, -0.0002, 0.0], sig_arr=[0.01, 0.02, 0.015])
    
    # Generate Synthetic XLU (defensive, less vol, sometimes outperforming in SPY drawdowns)
    xlu = synthetic_prices(n=2600, seed=10, s0=50.0, mu_arr=[0.0003, -0.0001, 0.0], sig_arr=[0.008, 0.015, 0.01])
    
    print("Instantiating Carver System...")
    sys = CarverSystem(target_vol=0.20, capital=100000, ann_days=252)
    
    print("Generating Target Weights with Macro Regime Override...")
    weights = sys.generate_target_weights(btc, xlu_prices=xlu, spy_prices=spy)
    
    print("Running Backtest...")
    res = sys.backtest(btc, weights)
    
    eq = res['equity'].dropna()
    cagr = (eq.iloc[-1]**(1/(len(eq)/252))) - 1.0
    r = eq.pct_change().dropna()
    sharpe = (r.mean() / r.std()) * np.sqrt(252)
    
    pk = eq.cummax()
    dd = (eq - pk) / pk
    max_dd = dd.min()
    
    print("--- SYNTHETIC BACKTEST RESULTS ---")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"CAGR:         {cagr*100:.1f}%")
    print(f"Max Drawdown: {max_dd*100:.1f}%")

if __name__ == '__main__':
    main()
