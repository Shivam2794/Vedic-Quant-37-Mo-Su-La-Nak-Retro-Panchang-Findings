import yfinance as yf
import pandas as pd
import numpy as np
import time
import random
import warnings
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def get_data():
    print("[*] Downloading Data...")
    tickers = ['SPY', 'TLT', 'LQD', 'GLD', 'SHV']
    df = yf.download(tickers, start="2008-01-01", end="2024-01-01", auto_adjust=False)['Close']
    df = df.ffill().dropna()
    returns = df.pct_change().dropna()
    
    # 60-day rolling volatility (annualized) for risk parity
    vol = returns.rolling(60).std() * np.sqrt(252)
    # Inverse vol weights
    inv_vol = 1.0 / vol
    
    # Normalize weights for Risk On (SPY + GLD)
    risk_on_weights = inv_vol[['SPY', 'GLD']].div(inv_vol[['SPY', 'GLD']].sum(axis=1), axis=0)
    
    # Normalize weights for Risk Off (TLT + SHV)
    risk_off_weights = inv_vol[['TLT', 'SHV']].div(inv_vol[['TLT', 'SHV']].sum(axis=1), axis=0)
    
    return df, returns, risk_on_weights, risk_off_weights

def compute_features(df):
    feat = pd.DataFrame(index=df.index)
    for col in ['SPY', 'TLT', 'LQD', 'GLD']:
        # Momentum
        feat[f'{col}_Mom_1M'] = df[col].pct_change(21)
        feat[f'{col}_Mom_3M'] = df[col].pct_change(63)
        feat[f'{col}_Mom_6M'] = df[col].pct_change(126)
        
        # Binary Mom
        feat[f'{col}_Mom_Pos_1M'] = (feat[f'{col}_Mom_1M'] > 0).astype(int)
        feat[f'{col}_Mom_Pos_3M'] = (feat[f'{col}_Mom_3M'] > 0).astype(int)
        
        # Reversion (Z-Score)
        ma20 = df[col].rolling(20).mean()
        std20 = df[col].rolling(20).std()
        z20 = (df[col] - ma20) / std20
        feat[f'{col}_Oversold_20'] = (z20 < -2).astype(int)
        feat[f'{col}_Overbought_20'] = (z20 > 2).astype(int)
        
        ma50 = df[col].rolling(50).mean()
        std50 = df[col].rolling(50).std()
        z50 = (df[col] - ma50) / std50
        feat[f'{col}_Oversold_50'] = (z50 < -2).astype(int)
        feat[f'{col}_Overbought_50'] = (z50 > 2).astype(int)
        
        # Trend Filter
        ma200 = df[col].rolling(200).mean()
        feat[f'{col}_Above_MA_200'] = (df[col] > ma200).astype(int)
        feat[f'{col}_Above_MA_20'] = (df[col] > ma20).astype(int)
        feat[f'{col}_Above_MA_50'] = (df[col] > ma50).astype(int)
        
    feat = feat.dropna()
    return feat

def generate_random_rule(binary_cols):
    num_conds = random.randint(2, 3)
    conds = random.sample(binary_cols, num_conds)
    
    rule_parts = []
    for c in conds:
        val = random.choice([0, 1])
        rule_parts.append(f"(feat['{c}'] == {val})")
        
    op = random.choice(['&', '|'])
    rule_str = f" {op} ".join(rule_parts)
    return rule_str

def evaluate_rule(rule_str, feat, returns_window, on_weights_window, off_weights_window):
    # Rule determines Risk On (1) or Risk Off (0)
    signal = eval(rule_str)
    
    # We execute at the next day's open (use shift 1)
    signal = signal.shift(1).fillna(0)
    
    # Weights for Risk On (SPY, GLD)
    w_spy = np.where(signal == 1, on_weights_window['SPY'].shift(1).fillna(0), 0)
    w_gld = np.where(signal == 1, on_weights_window['GLD'].shift(1).fillna(0), 0)
    
    # Weights for Risk Off (TLT, SHV)
    w_tlt = np.where(signal == 0, off_weights_window['TLT'].shift(1).fillna(0), 0)
    w_shv = np.where(signal == 0, off_weights_window['SHV'].shift(1).fillna(0), 0)
    
    # Returns
    ret_spy = returns_window['SPY'] * w_spy
    ret_gld = returns_window['GLD'] * w_gld
    ret_tlt = returns_window['TLT'] * w_tlt
    ret_shv = returns_window['SHV'] * w_shv
    
    port_ret = ret_spy + ret_gld + ret_tlt + ret_shv
    
    # Slippage (calculate delta in weights)
    delta_spy = np.abs(np.diff(w_spy, prepend=0))
    delta_gld = np.abs(np.diff(w_gld, prepend=0))
    delta_tlt = np.abs(np.diff(w_tlt, prepend=0))
    delta_shv = np.abs(np.diff(w_shv, prepend=0))
    
    total_turnover = delta_spy + delta_gld + delta_tlt + delta_shv
    port_ret -= (total_turnover * SLIPPAGE_BPS)
    
    total_turnover_amount = total_turnover.sum()
    
    sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
    cagr = (1 + port_ret).prod() ** (252 / len(port_ret)) - 1
    
    return sharpe, cagr, port_ret, total_turnover_amount

def run_walk_forward():
    df, returns, on_weights, off_weights = get_data()
    feat = compute_features(df)
    
    # Align dates
    returns = returns.loc[feat.index]
    on_weights = on_weights.loc[feat.index]
    off_weights = off_weights.loc[feat.index]
    
    binary_cols = [c for c in feat.columns if feat[c].nunique() == 2]
    
    years = sorted(list(set(feat.index.year)))
    
    oos_returns = []
    
    print(f"[*] Starting Walk-Forward Optimization (Train: 4 Years, Test: 1 Year)")
    
    # Walk forward windows
    for i in range(len(years) - 4):
        train_years = years[i:i+4]
        test_year = years[i+4]
        
        train_mask = feat.index.year.isin(train_years)
        test_mask = feat.index.year == test_year
        
        f_train, r_train = feat.loc[train_mask], returns.loc[train_mask]
        on_train, off_train = on_weights.loc[train_mask], off_weights.loc[train_mask]
        
        best_sharpe = -99
        best_rule = "(feat['SPY_Above_MA_200'] == 1)"
        
        # Train (generate 500 random rules per window to find the best regime model)
        for _ in range(500):
            rule_str = generate_random_rule(binary_cols)
            sharpe, cagr, _, turnover_amt = evaluate_rule(rule_str, f_train, r_train, on_train, off_train)
            
            # Constraint: No more than 400% annualized turnover (to prevent slippage bleed)
            annual_turnover = turnover_amt * 252 / len(f_train)
            if annual_turnover > 4.0:
                continue
                
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_rule = rule_str
                
        # Test (OOS)
        f_test, r_test = feat.loc[test_mask], returns.loc[test_mask]
        on_test, off_test = on_weights.loc[test_mask], off_weights.loc[test_mask]
        
        test_sharpe, test_cagr, test_ret, test_turnover = evaluate_rule(best_rule, f_test, r_test, on_test, off_test)
        oos_returns.append(test_ret)
        
        test_annual_turnover = test_turnover * 252 / len(f_test)
        print(f"[OOS {test_year}] Trained on {train_years[0]}-{train_years[-1]} | Best Rule: {best_rule} | OOS Sharpe: {test_sharpe:.2f} | Annual Turnover: {test_annual_turnover:.2f}x")

    final_oos_returns = pd.concat(oos_returns)
    final_sharpe = np.sqrt(252) * final_oos_returns.mean() / (final_oos_returns.std() + 1e-9)
    final_cagr = (1 + final_oos_returns).prod() ** (252 / len(final_oos_returns)) - 1
    
    # Calculate Max DD
    cum_ret = (1 + final_oos_returns).cumprod()
    running_max = cum_ret.cummax()
    drawdown = (cum_ret - running_max) / running_max
    max_dd = drawdown.min()
    
    print("========================================================")
    print(f"[*] FINAL STRICTLY OUT-OF-SAMPLE RESULTS (RISK PARITY)")
    print(f"OOS CAGR: {final_cagr:.2%}")
    print(f"OOS Sharpe: {final_sharpe:.2f}")
    print(f"OOS Max DD: {max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_walk_forward()
