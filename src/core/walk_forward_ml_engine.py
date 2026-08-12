import yfinance as yf
import pandas as pd
import numpy as np
import time
import warnings
from xgboost import XGBClassifier
warnings.filterwarnings('ignore')

SLIPPAGE_BPS = 10 / 10000

def get_data():
    print("[*] Downloading Data...")
    tickers = ['SPY', 'TLT', 'LQD', 'GLD', 'SHV']
    df = yf.download(tickers, start="2008-01-01", end="2024-01-01")['Close']
    df = df.ffill().dropna()
    returns = df.pct_change().dropna()
    return df, returns

def compute_features(df):
    feat = pd.DataFrame(index=df.index)
    
    for col in ['SPY', 'TLT', 'LQD', 'GLD']:
        # Continuous Momentum
        feat[f'{col}_Mom_1M'] = df[col].pct_change(21)
        feat[f'{col}_Mom_3M'] = df[col].pct_change(63)
        feat[f'{col}_Mom_6M'] = df[col].pct_change(126)
        
        # Z-Scores (Reversion)
        ma20 = df[col].rolling(20).mean()
        std20 = df[col].rolling(20).std()
        feat[f'{col}_Z_20'] = (df[col] - ma20) / std20
        
        ma50 = df[col].rolling(50).mean()
        std50 = df[col].rolling(50).std()
        feat[f'{col}_Z_50'] = (df[col] - ma50) / std50
        
        # Moving Average Distance (Trend)
        ma200 = df[col].rolling(200).mean()
        feat[f'{col}_Dist_MA_200'] = (df[col] - ma200) / ma200
        feat[f'{col}_Dist_MA_50'] = (df[col] - ma50) / ma50
        
        # Volatility
        feat[f'{col}_Vol_20'] = df[col].pct_change().rolling(20).std()
        
    feat = feat.dropna()
    return feat

def run_ml_walk_forward():
    df, returns = get_data()
    feat = compute_features(df)
    
    # Target: SPY outperforms Cash (SHV) next day
    target = (returns['SPY'].shift(-1) > returns['SHV'].shift(-1)).astype(int)
    
    # Align dates
    returns = returns.loc[feat.index]
    target = target.loc[feat.index]
    
    # Drop the last row because target is NaN
    feat = feat.iloc[:-1]
    returns = returns.iloc[:-1]
    target = target.iloc[:-1]
    
    years = sorted(list(set(feat.index.year)))
    
    oos_returns = []
    
    print(f"[*] Starting Walk-Forward ML Optimization (Train: 4 Years, Test: 1 Year)")
    
    for i in range(len(years) - 4):
        train_years = years[i:i+4]
        test_year = years[i+4]
        
        train_mask = feat.index.year.isin(train_years)
        test_mask = feat.index.year == test_year
        
        X_train, y_train = feat.loc[train_mask], target.loc[train_mask]
        X_test, r_test = feat.loc[test_mask], returns.loc[test_mask]
        
        # Train XGBoost Model
        # Using a shallow tree with L2 regularization to prevent extreme overfitting
        model = XGBClassifier(
            n_estimators=100, 
            max_depth=3, 
            learning_rate=0.05, 
            reg_lambda=1.0, 
            random_state=42,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        
        # Predict Probabilities (OOS)
        # Prob of SPY outperforming SHV
        prob_spy = model.predict_proba(X_test)[:, 1]
        
        # Map Probability to Weights
        # To avoid massive daily turnover, we use a hysteresis threshold
        w_spy = np.zeros(len(prob_spy))
        w_tlt = np.zeros(len(prob_spy))
        
        current_spy = 1.0 # Default start
        for j in range(len(prob_spy)):
            p = prob_spy[j]
            if p > 0.55:
                current_spy = 1.0
            elif p < 0.45:
                current_spy = 0.0
                
            w_spy[j] = current_spy
            w_tlt[j] = 1.0 - current_spy
        
        # Calculate Returns
        # Note: prob_spy is generated based on today's close, executes at tomorrow's open (shift 1 applies to returns)
        # Wait, the target is `returns['SPY'].shift(-1)`. 
        # So X at time T predicts Returns at time T+1.
        # Thus, w_spy[T] multiplies r_test[T+1].
        # We need to shift weights by 1 to align with returns correctly in pandas.
        
        w_spy_series = pd.Series(w_spy, index=X_test.index).shift(1).fillna(0)
        w_tlt_series = pd.Series(w_tlt, index=X_test.index).shift(1).fillna(0)
        
        ret_spy = r_test['SPY'] * w_spy_series
        ret_tlt = r_test['TLT'] * w_tlt_series
        
        port_ret = ret_spy + ret_tlt
        
        # Slippage calculation
        delta_spy = w_spy_series.diff().abs().fillna(0)
        delta_tlt = w_tlt_series.diff().abs().fillna(0)
        total_turnover = delta_spy + delta_tlt
        
        port_ret -= (total_turnover * SLIPPAGE_BPS)
        
        test_sharpe = np.sqrt(252) * port_ret.mean() / (port_ret.std() + 1e-9)
        annual_turnover = total_turnover.sum() * 252 / len(X_test)
        
        print(f"[OOS {test_year}] Trained on {train_years[0]}-{train_years[-1]} | OOS Sharpe: {test_sharpe:.2f} | Annual Turnover: {annual_turnover:.2f}x")
        
        oos_returns.append(port_ret)

    final_oos_returns = pd.concat(oos_returns)
    final_sharpe = np.sqrt(252) * final_oos_returns.mean() / (final_oos_returns.std() + 1e-9)
    final_cagr = (1 + final_oos_returns).prod() ** (252 / len(final_oos_returns)) - 1
    
    cum_ret = (1 + final_oos_returns).cumprod()
    running_max = cum_ret.cummax()
    drawdown = (cum_ret - running_max) / running_max
    max_dd = drawdown.min()
    
    print("========================================================")
    print(f"[*] FINAL WFO XGBOOST RESULTS (CONTINUOUS WEIGHTING)")
    print(f"OOS CAGR: {final_cagr:.2%}")
    print(f"OOS Sharpe: {final_sharpe:.2f}")
    print(f"OOS Max DD: {max_dd:.2%}")
    
    # Benchmark SPY
    bm = returns['SPY'].loc[final_oos_returns.index]
    bm_cagr = (1 + bm).prod() ** (252 / len(bm)) - 1
    bm_sharpe = np.sqrt(252) * bm.mean() / (bm.std() + 1e-9)
    bm_cum_ret = (1 + bm).cumprod()
    bm_max_dd = ((bm_cum_ret - bm_cum_ret.cummax()) / bm_cum_ret.cummax()).min()
    print(f"[*] SPY BENCHMARK OOS CAGR: {bm_cagr:.2%} | Sharpe: {bm_sharpe:.2f} | Max DD: {bm_max_dd:.2%}")
    print("========================================================")

if __name__ == "__main__":
    run_ml_walk_forward()
