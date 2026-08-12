"""
OPUS-8 Genesis Final: Asset-Specific Walk-Forward Genetic Engine
================================================================
This engine utilizes the specific optimal indicator ensembles discovered
by the OPUS-8 Matrix Grid Search. It dynamically evolves the parameters
for these specific indicators using a Walk-Forward Genetic Algorithm.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import random
import time
from deap import base, creator, tools, algorithms
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────
UNIVERSE = ['SPY', 'QQQ', 'TLT', 'GLD', 'BTC-USD']
START_DATE = '2005-01-01'
TRAIN_YEARS = 3
TEST_YEARS = 1

# The Optimal Configurations discovered from Phase 1 Grid Search
OPTIMAL_CONFIGS = {
    'SPY': {'logic': 'MAJORITY', 'inds': ['MACD', 'EMA3', 'AROON']},
    'QQQ': {'logic': 'OR3',      'inds': ['AROON', 'DONCHIAN', 'BB']},
    'GLD': {'logic': 'OR3',      'inds': ['AROON', 'DONCHIAN', 'BB']},
    'TLT': {'logic': 'MAJORITY', 'inds': ['MACD', 'AROON', 'DONCHIAN']},
    'BTC-USD': {'logic': 'OR2',  'inds': ['AROON', 'DONCHIAN']}
}

# ─────────────────────────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────────────────────────
def get_data(tickers, start_date):
    print("Downloading data...")
    df = yf.download(tickers, start=start_date, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        close = df['Close'].ffill()
    else:
        close = df[['Close']].ffill()
        close.columns = tickers
    return close.dropna()

# ─────────────────────────────────────────────────────────────────
# INDICATOR SIGNAL FUNCTIONS (Numpy Vectorized)
# ─────────────────────────────────────────────────────────────────
def calc_macd(close, fast, slow, sig):
    c = pd.Series(close)
    ema_fast = c.ewm(span=fast, adjust=False).mean()
    ema_slow = c.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=sig, adjust=False).mean()
    hist = macd_line - signal_line
    sig_arr = (hist > 0).values
    sig_arr = np.roll(sig_arr, 1); sig_arr[0] = False
    return sig_arr

def calc_ema3(close, f, m, s):
    c = pd.Series(close)
    ef = c.ewm(span=f, adjust=False).mean()
    em = c.ewm(span=m, adjust=False).mean()
    es = c.ewm(span=s, adjust=False).mean()
    sig_arr = ((ef > em) & (em > es)).values
    sig_arr = np.roll(sig_arr, 1); sig_arr[0] = False
    return sig_arr

def calc_aroon(close, period, up_t, dn_t):
    c = pd.Series(close)
    aroon_up = c.rolling(period).apply(lambda x: float(np.argmax(x))/period * 100, raw=True)
    aroon_dn = c.rolling(period).apply(lambda x: float(np.argmin(x))/period * 100, raw=True)
    sig_arr = ((aroon_up > up_t) & (aroon_dn < dn_t)).values
    sig_arr = np.roll(sig_arr, 1); sig_arr[0] = False
    return sig_arr

def calc_donchian(close, period):
    c = pd.Series(close)
    upper = c.rolling(period).max().shift(1)
    sig_arr = (c > upper).values
    sig_arr = np.roll(sig_arr, 1); sig_arr[0] = False
    return sig_arr

def calc_bb(close, window, std):
    c = pd.Series(close)
    sma = c.rolling(window).mean()
    dev = c.rolling(window).std() * std
    lower = sma - dev
    # Mean reversion buy: close crosses below lower band
    sig_arr = (c < lower).values
    sig_arr = np.roll(sig_arr, 1); sig_arr[0] = False
    return sig_arr

def get_signal(ind_name, close, p):
    if ind_name == 'MACD': return calc_macd(close, p[0], p[1], p[2])
    if ind_name == 'EMA3': return calc_ema3(close, p[0], p[1], p[2])
    if ind_name == 'AROON': return calc_aroon(close, p[0], p[1], p[2])
    if ind_name == 'DONCHIAN': return calc_donchian(close, p[0])
    if ind_name == 'BB': return calc_bb(close, p[0], p[1])
    return np.zeros(len(close), dtype=bool)

# ─────────────────────────────────────────────────────────────────
# GENETIC ALGORITHM EVALUATOR
# ─────────────────────────────────────────────────────────────────
def decode_individual(ind, ind_names):
    """Maps the linear genome to specific indicator parameters"""
    params = []
    idx = 0
    for name in ind_names:
        if name == 'MACD':
            f, s, sig = ind[idx], ind[idx+1], ind[idx+2]
            if f >= s: s = f + 5
            params.append([f, s, sig])
            idx += 3
        elif name == 'EMA3':
            f, m, s = ind[idx], ind[idx+1], ind[idx+2]
            if f >= m: m = f + 5
            if m >= s: s = m + 5
            params.append([f, m, s])
            idx += 3
        elif name == 'AROON':
            params.append([ind[idx], ind[idx+1], ind[idx+2]])
            idx += 3
        elif name == 'DONCHIAN':
            params.append([ind[idx]])
            idx += 1
        elif name == 'BB':
            params.append([ind[idx], ind[idx+1]/10.0]) # std is scaled by 10 in genome
            idx += 2
    return params

def evaluate(individual, close_prices, rets, ind_names, logic):
    params = decode_individual(individual, ind_names)
    
    sigs = []
    for i, name in enumerate(ind_names):
        sigs.append(get_signal(name, close_prices, params[i]))
        
    sigs = np.array(sigs) # Shape: (Num_Inds, T)
    
    if logic == 'MAJORITY':
        final_sig = np.sum(sigs, axis=0) >= 2
    elif logic == 'OR3' or logic == 'OR2':
        final_sig = np.any(sigs, axis=0)
    else:
        final_sig = np.zeros(len(close_prices), dtype=bool)
        
    strat_rets = final_sig * rets
    
    # Fitness: Sharpe Ratio
    mean_ret = np.mean(strat_rets)
    std_ret = np.std(strat_rets)
    if std_ret == 0: return (-999.0,)
    
    sharpe = (mean_ret / std_ret) * np.sqrt(252)
    return (sharpe,)

# ─────────────────────────────────────────────────────────────────
# WALK-FORWARD ENGINE
# ─────────────────────────────────────────────────────────────────
def setup_deap(ind_names):
    if hasattr(creator, "FitnessMax"):
        del creator.FitnessMax
    if hasattr(creator, "Individual"):
        del creator.Individual
        
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    
    toolbox = base.Toolbox()
    
    # Define bounds for each indicator's parameters
    def generate_gene(name):
        if name == 'MACD': return [random.randint(5, 50), random.randint(20, 200), random.randint(5, 50)]
        if name == 'EMA3': return [random.randint(5, 50), random.randint(20, 100), random.randint(50, 200)]
        if name == 'AROON': return [random.randint(10, 100), random.randint(70, 95), random.randint(10, 50)]
        if name == 'DONCHIAN': return [random.randint(10, 100)]
        if name == 'BB': return [random.randint(20, 200), random.randint(15, 30)] # 1.5 to 3.0 std
        return []

    def create_individual():
        genome = []
        for name in ind_names:
            genome.extend(generate_gene(name))
        return creator.Individual(genome)
        
    toolbox.register("individual", create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    # Custom mutation based on gene index would be better, but uniform int works
    toolbox.register("mate", tools.cxTwoPoint)
    
    def mutate_ind(ind, pb=0.2):
        for i in range(len(ind)):
            if random.random() < pb:
                # Add/sub small integer noise
                ind[i] = max(2, ind[i] + random.randint(-5, 5))
        return ind,
        
    toolbox.register("mutate", mutate_ind)
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    return toolbox

def optimize_window(close_prices, rets, ind_names, logic, toolbox):
    toolbox.register("evaluate", evaluate, close_prices=close_prices, rets=rets, ind_names=ind_names, logic=logic)
    pop = toolbox.population(n=40)
    hof = tools.HallOfFame(1)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    
    # Run GA (fewer gens for speed in walk-forward)
    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=10, 
                        stats=stats, halloffame=hof, verbose=False)
    
    best_ind = hof[0]
    best_params = decode_individual(best_ind, ind_names)
    return best_params

def main():
    print("="*60)
    print(" OPUS-8 GENESIS: Asset-Specific Walk-Forward Genetic Engine")
    print("="*60)
    
    data = get_data(UNIVERSE, START_DATE)
    dates = data.index
    
    all_strat_rets = pd.DataFrame(index=dates, columns=UNIVERSE).fillna(0.0)
    
    for ticker in UNIVERSE:
        print(f"\n[{ticker}] Starting Walk-Forward Optimization...")
        close_prices = data[ticker].values
        rets = data[ticker].pct_change().fillna(0).values
        
        config = OPTIMAL_CONFIGS[ticker]
        ind_names = config['inds']
        logic = config['logic']
        
        toolbox = setup_deap(ind_names)
        
        # Calculate steps
        days_per_year = 252
        train_days = TRAIN_YEARS * days_per_year
        test_days = TEST_YEARS * days_per_year
        
        start_idx = train_days
        
        while start_idx < len(dates):
            end_idx = min(start_idx + test_days, len(dates))
            train_close = close_prices[start_idx - train_days:start_idx]
            train_rets = rets[start_idx - train_days:start_idx]
            
            # 1. Optimize on Training Window
            best_params = optimize_window(train_close, train_rets, ind_names, logic, toolbox)
            
            # 2. Test on OOS Window
            test_close = close_prices[start_idx - train_days:end_idx] # need padding for rolling
            test_rets = rets[start_idx - train_days:end_idx]
            
            sigs = []
            for i, name in enumerate(ind_names):
                sigs.append(get_signal(name, test_close, best_params[i]))
            sigs = np.array(sigs)
            
            if logic == 'MAJORITY': final_sig = np.sum(sigs, axis=0) >= 2
            elif logic in ['OR3', 'OR2']: final_sig = np.any(sigs, axis=0)
            else: final_sig = np.zeros(len(test_close), dtype=bool)
            
            # Extract only the OOS portion
            oos_sig = final_sig[train_days:]
            oos_rets = test_rets[train_days:]
            
            all_strat_rets.loc[dates[start_idx:end_idx], ticker] = oos_sig * oos_rets
            
            start_idx += test_days

    # Post-process
    print("\nOptimization Complete. Generating Tearsheet...")
    all_strat_rets = all_strat_rets.loc[dates[train_days:]] # Drop initial train period
    
    # Portfolio is equal weight of the 5
    port_rets = all_strat_rets.mean(axis=1)
    port_cum = (1 + port_rets).cumprod()
    
    spy_rets = data['SPY'].pct_change().loc[all_strat_rets.index].fillna(0)
    spy_cum = (1 + spy_rets).cumprod()
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(port_cum, label='OPUS-8 Genesis (Asset-Specific WF)', color='blue', linewidth=2)
    plt.plot(spy_cum, label='SPY (Buy & Hold)', color='gray', alpha=0.7)
    plt.yscale('log')
    plt.title('OPUS-8 Genesis vs SPY (Log Scale)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_genesis_final.png')
    
    # Metrics
    def calc_metrics(r):
        cagr = (1 + r).cumprod().iloc[-1] ** (252 / len(r)) - 1
        vol = r.std() * np.sqrt(252)
        sharpe = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
        cum = (1 + r).cumprod()
        dd = (cum / cum.cummax() - 1).min()
        calmar = cagr / abs(dd) if dd < 0 else 0
        return cagr, vol, sharpe, dd, calmar
        
    p_cagr, p_vol, p_sharpe, p_dd, p_calmar = calc_metrics(port_rets)
    s_cagr, s_vol, s_sharpe, s_dd, s_calmar = calc_metrics(spy_rets)
    
    print(f"\nFinal Portfolio Metrics (Out-Of-Sample since {dates[train_days].date()}):")
    print(f"OPUS-8 Genesis -> CAGR: {p_cagr*100:.2f}%, Max DD: {p_dd*100:.2f}%, Sharpe: {p_sharpe:.2f}")
    print(f"SPY Buy & Hold -> CAGR: {s_cagr*100:.2f}%, Max DD: {s_dd*100:.2f}%, Sharpe: {s_sharpe:.2f}")
    
if __name__ == '__main__':
    main()
