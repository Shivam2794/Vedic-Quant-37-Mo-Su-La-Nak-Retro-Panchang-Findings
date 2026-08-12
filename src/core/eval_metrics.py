import pandas as pd
import numpy as np
import subprocess
import os
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

BQ_CMD = r"C:\Users\Shivam Patel\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd"
CAUSAL_CORE_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\causal_core.csv"
RETURNS_PATH = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"

def run_query(sql):
    tmp_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\tmp_features_metrics.csv"
    cmd = f'"{BQ_CMD}" query --use_legacy_sql=false --format=csv --max_rows=1000000 "{sql}" > "{tmp_path}"'
    subprocess.run(cmd, shell=True)
    df = pd.read_csv(tmp_path)
    os.remove(tmp_path)
    return df

def calculate_max_drawdown(returns):
    if len(returns) == 0: return 0.0
    cum_returns = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cum_returns)
    drawdown = (cum_returns - peak) / peak
    return np.min(drawdown)

def calculate_metrics():
    core_df = pd.read_csv(CAUSAL_CORE_PATH)
    features = core_df['feature'].tolist()
    
    feature_cols = ", ".join(features)
    sql = f"SELECT ticker, date, {feature_cols} FROM `antigravity_quant.feature_matrix` WHERE RAND() < 0.1 ORDER BY date"
    df_features = run_query(sql)
    df_features['date'] = pd.to_datetime(df_features['date']).dt.date.astype(str)
    
    df_returns = pd.read_parquet(RETURNS_PATH)
    df_returns['date'] = pd.to_datetime(df_returns['date']).dt.date.astype(str)
    
    target = 'fwd_return_63d'
    merged = df_features.merge(df_returns[['ticker', 'date', target]], on=['ticker', 'date'], how='inner')
    merged = merged.dropna().sort_values('date').reset_index(drop=True)
    
    X = merged[features]
    y = merged[target]
    
    tscv = TimeSeriesSplit(n_splits=5)
    model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, subsample=0.8, colsample_bytree=0.8, n_jobs=-1, random_state=42)
    
    all_win_pct = []
    all_mdd = []
    all_trades_per_yr = []
    all_arith_cagr = []
    all_geom_cagr = []
    
    for fold, (train_index, test_index) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        # Calculate years in test set
        dates_in_test = merged.iloc[test_index]['date']
        years_in_test = (pd.to_datetime(dates_in_test.max()) - pd.to_datetime(dates_in_test.min())).days / 365.25636042
        if years_in_test == 0: years_in_test = 1
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        
        signals = np.where(predictions > 0, 1, 0)
        strategy_returns = y_test[signals == 1]
        
        if len(strategy_returns) > 0:
            # Note: We sampled 10% of the DB. To get true trades/year across the 69 tickers, we multiply by 10.
            total_trades = len(strategy_returns) * 10 
            trades_per_yr = total_trades / years_in_test
            
            wins = len(strategy_returns[strategy_returns > 0])
            win_pct = (wins / len(strategy_returns)) * 100
            
            mdd = calculate_max_drawdown(strategy_returns.values)
            
            # 63-day horizon is exactly 1/4 of a 252-day trading year
            periods_per_year = 252 / 63
            
            # Arithmetic CAGR: sum(returns) adjusted by periods
            arith_cagr = np.mean(strategy_returns) * periods_per_year
            
            # Geometric CAGR: proper compounding of geometric mean return
            geom_mean = np.exp(np.mean(np.log1p(strategy_returns))) - 1
            geom_cagr = ((1 + geom_mean) ** periods_per_year) - 1
            
        else:
            trades_per_yr = 0
            win_pct = 0
            mdd = 0
            arith_cagr = 0
            geom_cagr = 0
            
        all_win_pct.append(win_pct)
        all_mdd.append(mdd)
        all_trades_per_yr.append(trades_per_yr)
        all_arith_cagr.append(arith_cagr)
        all_geom_cagr.append(geom_cagr)

    print(f"Metrics across 69 Equities (63-Day Horizon):")
    print(f"Mean Win Rate: {np.mean(all_win_pct):.2f}%")
    print(f"Mean Arithmetic CAGR: {np.mean(all_arith_cagr)*100:.2f}%")
    print(f"Mean Geometric CAGR: {np.mean(all_geom_cagr)*100:.2f}%")
    print(f"Mean Max Drawdown: {np.mean(all_mdd)*100:.2f}%")
    print(f"Average Trades per Year (Fleet-wide): {np.mean(all_trades_per_yr):.0f}")
    
if __name__ == "__main__":
    calculate_metrics()
