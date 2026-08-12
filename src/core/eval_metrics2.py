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
    tmp_path = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\tmp_features_metrics2.csv"
    cmd = f'"{BQ_CMD}" query --use_legacy_sql=false --format=csv --max_rows=1000000 "{sql}" > "{tmp_path}"'
    subprocess.run(cmd, shell=True)
    df = pd.read_csv(tmp_path)
    os.remove(tmp_path)
    return df

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
    
    # We will accumulate all out-of-sample predictions to build a continuous equity curve
    all_dates = []
    all_actuals = []
    all_signals = []
    
    for fold, (train_index, test_index) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        dates_test = merged.iloc[test_index]['date']
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        signals = np.where(predictions > 0, 1, 0)
        
        all_dates.extend(dates_test)
        all_actuals.extend(y_test)
        all_signals.extend(signals)

    df_res = pd.DataFrame({'date': all_dates, 'actual': all_actuals, 'signal': all_signals})
    df_res['date'] = pd.to_datetime(df_res['date'])
    
    # Calculate portfolio daily returns: sum of returns for active signals / 69 (max positions)
    # We use 63D returns, so to approximate daily impact we divide by 63.
    df_res['daily_ret'] = np.where(df_res['signal'] == 1, df_res['actual'] / 63.0, 0)
    
    daily_portfolio = df_res.groupby('date')['daily_ret'].sum() / 69.0
    
    cum_returns = np.cumprod(1 + daily_portfolio.values)
    peak = np.maximum.accumulate(cum_returns)
    drawdown = (cum_returns - peak) / peak
    mdd = np.min(drawdown)
    
    active_trades = df_res[df_res['signal'] == 1]
    win_pct = len(active_trades[active_trades['actual'] > 0]) / len(active_trades) * 100
    
    years = (df_res['date'].max() - df_res['date'].min()).days / 365.25636042
    total_trades = len(active_trades) * 10 # scale back from 10% sample
    trades_per_yr = total_trades / years
    
    print(f"Mean Win Rate: {win_pct:.2f}%")
    print(f"Max Portfolio Drawdown: {mdd*100:.2f}%")
    print(f"Average Trades per Year (Fleet-wide): {trades_per_yr:.0f}")

if __name__ == "__main__":
    calculate_metrics()
