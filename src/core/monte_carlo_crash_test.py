import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def run_monte_carlo_crash_tests():
    print("[*] Downloading Data for Monte Carlo Crash & Tail-Risk Stress Testing...")
    df_raw = yf.download(['BTC-USD', 'SPY', '^IRX'], start="2014-01-01", end="2024-01-01", progress=False, auto_adjust=False)
    
    biz_idx = df_raw['Close']['SPY'].dropna().index
    df_raw = df_raw.ffill()
    
    close_prices = df_raw['Close']['BTC-USD']
    open_prices = df_raw['Open']['BTC-USD']
    irx = df_raw['Close']['^IRX']
    
    # Calculate strategy weights (2/40 SMA, 15% VolTarget)
    sma_fast = close_prices.rolling(2).mean()
    sma_slow = close_prices.rolling(40).mean()
    trend = (sma_fast > sma_slow).astype(float).shift(1).fillna(0.0)
    
    vol20 = close_prices.pct_change().rolling(20).std() * np.sqrt(365)
    vol_w = (0.15 / vol20).clip(upper=1.5).shift(1).fillna(0.0)
    
    target_weights_365 = trend * vol_w
    weights_biz = target_weights_365.ffill().reindex(biz_idx).ffill()
    open_biz = open_prices.ffill().reindex(biz_idx).ffill()
    r_open = (open_biz.shift(-1) / open_biz) - 1
    
    valid_idx = biz_idx[250:-1]
    strat_weights = weights_biz.loc[valid_idx].values
    btc_returns = r_open.loc[valid_idx].values
    
    print("\n" + "="*65)
    print(" 1. EMPIRICAL POSITION SIZING DURING HISTORICAL BTC CRASHES")
    print("="*65)
    print(f"Average Strategy Exposure (Weight) when Long: {np.mean(strat_weights[strat_weights > 0]):.2%}")
    print(f"Maximum Strategy Exposure (Weight):         {np.max(strat_weights):.2%}")
    print(f"Median Strategy Exposure (Weight) when Long:  {np.median(strat_weights[strat_weights > 0]):.2%}")
    
    # Let's test synthetic flash crashes while holding the AVERAGE long weight and MAX long weight
    avg_w = np.mean(strat_weights[strat_weights > 0])
    max_w = np.max(strat_weights)
    
    print("\n" + "="*65)
    print(" 2. SYNTHETIC FLASH CRASH STRESS TEST (INSTANTANEOUS HIT)")
    print("="*65)
    for crash_pct in [-0.30, -0.50, -0.70]:
        port_hit_avg = avg_w * crash_pct
        port_hit_max = max_w * crash_pct
        print(f"If BTC Flash Crashes {crash_pct:.0%}:")
        print(f"  -> Portfolio Hit at Average Long Weight ({avg_w:.1%}): {port_hit_avg:.2%}")
        print(f"  -> Portfolio Hit at Maximum Long Weight ({max_w:.1%}): {port_hit_max:.2%}")
        
    print("\n" + "="*65)
    print(" 3. BLOCK-BOOTSTRAP MONTE CARLO SIMULATION (10,000 PATHS)")
    print("    Simulating 10-year future paths with clustered tail shocks")
    print("="*65)
    np.random.seed(42)
    num_sims = 10000
    path_len = len(valid_idx)
    block_size = 20 # 20-day blocks to preserve volatility clustering
    
    # Calculate daily strategy returns
    strat_daily_ret = strat_weights * btc_returns
    
    num_blocks = int(np.ceil(path_len / block_size))
    sim_cagrs = np.zeros(num_sims)
    sim_max_dds = np.zeros(num_sims)
    
    for s in range(num_sims):
        start_indices = np.random.randint(0, path_len - block_size, size=num_blocks)
        sampled_ret = np.concatenate([strat_daily_ret[idx:idx+block_size] for idx in start_indices])[:path_len]
        
        cum = np.cumprod(1 + sampled_ret)
        cagr = cum[-1] ** (252 / path_len) - 1
        cummax = np.maximum.accumulate(cum)
        dd = np.min((cum - cummax) / cummax)
        
        sim_cagrs[s] = cagr
        sim_max_dds[s] = dd
        
    print(f"Median Monte Carlo Max Drawdown:        {np.median(sim_max_dds):.2%}")
    print(f"95th Percentile Worst Max Drawdown:     {np.percentile(sim_max_dds, 5):.2%}")
    print(f"99th Percentile Worst Max Drawdown:     {np.percentile(sim_max_dds, 1):.2%}")
    print(f"99.9th Percentile Worst Max Drawdown:   {np.percentile(sim_max_dds, 0.1):.2%}")
    
    print("\n" + "="*65)
    print(" 4. MERTON JUMP-DIFFUSION MONTE CARLO (-50% to -70% POISSON JUMPS)")
    print("    Injecting sudden catastrophic jumps randomly into future paths")
    print("="*65)
    # We inject random Poisson jump shocks (-50% on BTC) averaging 1 every 2 years
    jump_prob = 1.0 / 500.0 # ~1 jump per 2 years
    sim_jump_dds = np.zeros(num_sims)
    
    for s in range(num_sims):
        start_indices = np.random.randint(0, path_len - block_size, size=num_blocks)
        sampled_ret = np.concatenate([strat_daily_ret[idx:idx+block_size] for idx in start_indices])[:path_len]
        sampled_w = np.concatenate([strat_weights[idx:idx+block_size] for idx in start_indices])[:path_len]
        
        # Inject catastrophic Poisson jumps where BTC drops between -50% and -70% in a single day
        jumps = np.random.uniform(-0.70, -0.50, size=path_len) * (np.random.rand(path_len) < jump_prob)
        # Portfolio loss from jump is weight * jump
        jump_port_ret = sampled_ret + (sampled_w * jumps)
        
        cum = np.cumprod(1 + jump_port_ret)
        cummax = np.maximum.accumulate(cum)
        sim_jump_dds[s] = np.min((cum - cummax) / cummax)
        
    print(f"Median Max Drawdown under -50% to -70% Jump-Diffusion:     {np.median(sim_jump_dds):.2%}")
    print(f"95th Percentile Worst Max Drawdown under Jump-Diffusion:   {np.percentile(sim_jump_dds, 5):.2%}")
    print(f"99th Percentile Worst Max Drawdown under Jump-Diffusion:   {np.percentile(sim_jump_dds, 1):.2%}")
    print("="*65)

if __name__ == "__main__":
    run_monte_carlo_crash_tests()
