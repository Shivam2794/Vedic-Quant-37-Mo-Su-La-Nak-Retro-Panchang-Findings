import os
import ast
import pandas as pd
import numpy as np
import yfinance as yf
from opus8_matrix_1a_generator import (
    gen_macd, gen_ema3, gen_tema, gen_tema_sig, gen_aroon,
    gen_rsi, gen_rsi_cumret, gen_donchian, gen_bb, gen_stc,
    gen_supertrend, gen_alma, gen_adx, gen_fti, gen_autocorr,
    gen_hurst, gen_entropy, gen_sma200, gen_gjr_garch, gen_kama,
    UNIVERSE, MACRO, get_data
)

IN_DIR = r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\opus8_matrix_data'
RESULTS_FILE = os.path.join(IN_DIR, 'opus8_gridsearch_absolution_results.csv')
OUT_FILE = os.path.join(IN_DIR, 'opus8_portfolio_returns.csv')

def parse_top_strategies():
    results = []
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line: continue
            parts = line.split(',', 5)
            if len(parts) == 6:
                ticker, size, fams, logic, sharpe_str, params = parts
                try:
                    sharpe = float(sharpe_str)
                    results.append({
                        'Ticker': ticker,
                        'Size': int(size),
                        'Families': fams,
                        'Logic': logic,
                        'Sharpe': sharpe,
                        'Params': params
                    })
                except:
                    pass
                    
    df = pd.DataFrame(results)
    top_strats = {}
    
    for ticker in df['Ticker'].unique():
        ticker_df = df[df['Ticker'] == ticker].sort_values('Sharpe', ascending=False)
        top_row = ticker_df.iloc[0]
        
        fams = top_row['Families'].split('-')
        params_str = top_row['Params']
        param_dict = {}
        for block in params_str.split('|'):
            if ':' not in block: continue
            k, v = block.split(':', 1)
            k = k.strip()
            v = v.strip()
            param_dict[k] = ast.literal_eval(v)
            
        top_strats[ticker] = {
            'Logic': top_row['Logic'],
            'Families': fams,
            'Params': param_dict
        }
    return top_strats

def build_portfolio_returns():
    print("Parsing top strategies...")
    top_strats = parse_top_strategies()
    
    print("Fetching raw data...")
    df = get_data()
    dates = df.index.values
    
    # Rebuild macro risk array
    macro_df = yf.download(MACRO, start='1999-01-01', progress=False, auto_adjust=True)['Close']
    macro_df = macro_df.reindex(dates).ffill()
    hyg_lqd = macro_df['HYG'] / macro_df['LQD']
    hyg_lqd_ma = hyg_lqd.rolling(50).mean()
    credit_risk_on = (hyg_lqd > hyg_lqd_ma) | hyg_lqd_ma.isna()
    
    xly_xlp = macro_df['XLY'] / macro_df['XLP']
    xly_xlp_ma = xly_xlp.rolling(50).mean()
    econ_risk_on = (xly_xlp > xly_xlp_ma) | xly_xlp_ma.isna()
    
    risk_on_macro = (credit_risk_on | econ_risk_on).values
    vix = macro_df['^VIX'].fillna(0).values
    vix_crash = (vix > 40)
    
    risk_on_macro = np.roll(risk_on_macro, 1)
    risk_on_macro[0] = False
    vix_crash = np.roll(vix_crash, 1)
    vix_crash[0] = False
    
    returns_dict = {}
    
    for ticker, strat in top_strats.items():
        print(f"Reconstructing {ticker} ({strat['Logic']}) ...")
        
        if isinstance(df.columns, pd.MultiIndex):
            close = df['Close'][ticker].ffill().bfill().values
            high = df['High'][ticker].ffill().bfill().values if 'High' in df else close
            low = df['Low'][ticker].ffill().bfill().values if 'Low' in df else close
        else:
            close = df[ticker].ffill().bfill().values
            high, low = close, close
            
        sigs = []
        for fam in strat['Families']:
            p = strat['Params'][fam]
            if fam == 'MACD':      s = gen_macd(close, p)
            elif fam == 'EMA3':    s = gen_ema3(close, p)
            elif fam == 'TEMA':    s = gen_tema(close, p)
            elif fam == 'TEMA_SIG':s = gen_tema_sig(close, p)
            elif fam == 'AROON':   s = gen_aroon(high, low, p)
            elif fam == 'RSI':     s = gen_rsi(close, p)
            elif fam == 'RSI_CUMRET': s = gen_rsi_cumret(close, p)
            elif fam == 'DONCHIAN':s = gen_donchian(close, p)
            elif fam == 'BB':      s = gen_bb(close, p)
            elif fam == 'STC':     s = gen_stc(close, p)
            elif fam == 'SUPERTREND': s = gen_supertrend(high, low, close, p)
            elif fam == 'ALMA':    s = gen_alma(close, p)
            elif fam == 'ADX':     s = gen_adx(high, low, close, p)
            elif fam == 'FTI':     s = gen_fti(close, p)
            elif fam == 'AUTOCORR':s = gen_autocorr(close, p)
            elif fam == 'HURST':   s = gen_hurst(close, p)
            elif fam == 'ENTROPY': s = gen_entropy(close, p)
            elif fam == 'SMA200':  s = gen_sma200(close, p)
            elif fam == 'GJR_GARCH': s = gen_gjr_garch(close, p)
            elif fam == 'KAMA':    s = gen_kama(close, p)
            else:                  s = np.zeros(len(close), dtype=bool)
                
            s_shifted = np.roll(s, 1)
            s_shifted[0] = False
            sigs.append(s_shifted)
            
        votes = np.sum(sigs, axis=0)
        num_fams = len(strat['Families'])
        
        logic = strat['Logic']
        is_invested = np.zeros(len(close))
        
        if logic == 'OR': is_invested = (votes > 0).astype(float)
        elif logic == 'AND': is_invested = (votes == num_fams).astype(float)
        elif logic == 'MAJORITY': is_invested = (votes >= np.ceil(num_fams/2)).astype(float)
        elif logic == 'CONTINUOUS': is_invested = votes / float(num_fams)
        elif logic == 'ASYMMETRIC': is_invested = np.where(votes == num_fams, 1.0, votes / (num_fams * 2.0))
        
        # Apply macro
        if ticker not in ['TLT', 'GLD']:
            # Risk OFF
            is_invested[~risk_on_macro] = 0.0
            is_invested[vix_crash] = 0.0
            
        if isinstance(df.columns, pd.MultiIndex):
            orig_close = df['Close'][ticker].values
        else:
            orig_close = df[ticker].values
            
        raw_ret = np.zeros(len(close))
        raw_ret[1:] = np.diff(close) / close[:-1]
        raw_ret[np.isnan(raw_ret)] = 0.0
        
        # Transaction costs
        tc_bps = 0.0005
        prev_inv = np.roll(is_invested, 1)
        prev_inv[0] = 0.0
        costs = np.abs(is_invested - prev_inv) * tc_bps
        
        strat_ret = (raw_ret * is_invested) - costs
        
        # Nullify returns where the asset didn't exist
        strat_ret[np.isnan(orig_close)] = np.nan
        
        returns_dict[ticker] = strat_ret
        
    ret_df = pd.DataFrame(returns_dict, index=df.index)
    ret_df.to_csv(OUT_FILE)
    print(f"Portfolio returns saved to {OUT_FILE}")

if __name__ == '__main__':
    build_portfolio_returns()
