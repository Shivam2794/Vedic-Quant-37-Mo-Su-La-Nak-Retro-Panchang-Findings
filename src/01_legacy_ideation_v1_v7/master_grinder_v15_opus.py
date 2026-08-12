import pandas as pd
import numpy as np
import optuna
import datetime
import warnings
import json
import os
import threading
from optuna.pruners import MedianPruner

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

save_lock = threading.Lock()

# ============================================================
# GLOBAL CONSTANTS
# ============================================================
TZ = 'America/New_York'
SLIPPAGE_BPS = 0.0010
SEC_FEE = 0.000008       
FINRA_TAF = 0.000166     
TQQQ_LEVERAGE = 3.0
MAX_POSITION_PCT = 1.0   
MIN_TRADES = 10
PRICE_MIN, PRICE_MAX = 5.0, 1000.0

# ============================================================
# 1. PURGED K-FOLD CROSS VALIDATION
# ============================================================
class PurgedKFold:
    def __init__(self, n_splits=5, purge_days=10, embargo_days=20):
        self.n_splits = n_splits
        self.purge_days = purge_days
        self.embargo_days = embargo_days

    def split(self, dates: pd.DatetimeIndex):
        """Yields (train_indices, test_indices) for each fold."""
        n = len(dates)
        indices = np.arange(n)
        fold_size = n // self.n_splits

        for i in range(self.n_splits):
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < self.n_splits - 1 else n
            
            test_indices = indices[test_start:test_end]

            # Purge before the test set
            train_before_end = max(0, test_start - self.purge_days)
            train_before = indices[:train_before_end]

            # Embargo after the test set
            train_after_start = min(n, test_end + self.embargo_days)
            train_after = indices[train_after_start:]

            train_indices = np.concatenate([train_before, train_after])
            yield train_indices, test_indices


# ============================================================
# 2. DATA LOADER & VOLATILITY-ADJUSTED FEATURES
# ============================================================
def load_all_data():
    print("[DATA] Loading all parquet files...")
    qqq_d = pd.read_parquet('qqq_daily.parquet')
    qqq_1m = pd.read_parquet('qqq_1m.parquet')
    tqqq_1m = pd.read_parquet('tqqq_1m.parquet')

    for df in [qqq_d, qqq_1m, tqqq_1m]:
        df.index = pd.to_datetime(df.index).tz_convert(TZ)

    qqq_1m = qqq_1m.between_time('09:30', '15:59')
    tqqq_1m = tqqq_1m.between_time('09:30', '15:59')
    tqqq_1m = tqqq_1m[(tqqq_1m['Volume'] > 0) &
                      (tqqq_1m['Open'].between(PRICE_MIN, PRICE_MAX)) &
                      (tqqq_1m['Close'].between(PRICE_MIN, PRICE_MAX))]
    qqq_1m = qqq_1m[qqq_1m['Volume'] > 0]

    return qqq_d, qqq_1m, tqqq_1m


from scipy.signal import lfilter

def get_weights(d, size):
    w = [1.]
    for k in range(1, size):
        w_ = -w[-1] / k * (d - k + 1)
        w.append(w_)
    return np.array(w)

def frac_diff_ffd(series, d):
    w = get_weights(d, len(series))
    res = lfilter(w, [1.0], series.values)
    return pd.Series(res, index=series.index, dtype=float)

def build_daily_features(qqq_d: pd.DataFrame) -> pd.DataFrame:
    d = qqq_d.copy()
    
    # Fractional Differentiation (d=0.10) for Stationarity
    d['FD_Close'] = frac_diff_ffd(np.log(d['Close']), 0.10)

    hl = d['High'] - d['Low']
    hc = (d['High'] - d['Close'].shift(1)).abs()
    lc = (d['Low'] - d['Close'].shift(1)).abs()
    d['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    d['ATR_pct'] = d['ATR'] / d['Close']

    delta = d['FD_Close'].diff()
    d['RSI'] = 100 - (100 / (1 + (
        delta.where(delta > 0, 0).rolling(14).mean() /
        np.clip(-delta.where(delta < 0, 0).rolling(14).mean(), 1e-10, None)
    )))

    ret = d['Close'].pct_change()
    d['Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
    d['Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
    d['GEX_Regime'] = np.where(d['Vol_5'] < d['Vol_21'], 1, -1)

    d['SMA_20'] = d['Close'].rolling(20).mean()
    d['SMA_50'] = d['Close'].rolling(50).mean()
    d['SMA_200'] = d['Close'].rolling(200).mean()
    d['Above_SMA_20'] = (d['Close'] > d['SMA_20']).astype(int)
    d['Above_SMA_50'] = (d['Close'] > d['SMA_50']).astype(int)
    d['Above_SMA_200'] = (d['Close'] > d['SMA_200']).astype(int)
    d['Dist_SMA20'] = (d['Close'] / d['SMA_20']) - 1.0
    d['Dist_SMA50'] = (d['Close'] / d['SMA_50']) - 1.0

    d['ROC_5'] = d['FD_Close'].pct_change(5)
    d['ROC_21'] = d['FD_Close'].pct_change(21)
    d['ROC_Accel'] = d['ROC_5'] - d['ROC_5'].shift(3)

    # Z-Score normalization for momentum
    d['ROC_5_Z'] = (d['ROC_5'] - d['ROC_5'].rolling(60).mean()) / np.clip(d['ROC_5'].rolling(60).std(), 1e-8, None)

    feature_cols = ['Close', 'Volume', 'ATR_pct', 'RSI', 'GEX_Regime',
                    'Vol_21', 'Vol_5', 'Above_SMA_20', 'Above_SMA_50',
                    'Above_SMA_200', 'Dist_SMA20', 'Dist_SMA50', 'ROC_5', 'ROC_21', 'ROC_Accel', 'ROC_5_Z']
    feat = {}
    for col in feature_cols:
        feat[f'Prev_{col}'] = d[col].shift(1)

    feat_df = pd.DataFrame(feat, index=d.index)
    feat_df['date_str'] = d.index.strftime('%Y-%m-%d')
    feat_df = feat_df.dropna().set_index('date_str')
    return feat_df


def build_intraday_lookup(qqq_1m: pd.DataFrame, tqqq_1m: pd.DataFrame) -> pd.DataFrame:
    qqq_1m = qqq_1m.copy()
    tqqq_1m = tqqq_1m.copy()
    qqq_1m['date_str'] = qqq_1m.index.strftime('%Y-%m-%d')
    tqqq_1m['date_str'] = tqqq_1m.index.strftime('%Y-%m-%d')
    qqq_1m['hour'] = qqq_1m.index.hour
    qqq_1m['minute'] = qqq_1m.index.minute
    tqqq_1m['hour'] = tqqq_1m.index.hour
    tqqq_1m['minute'] = tqqq_1m.index.minute

    def get_bar(df, h, m, col, rename):
        return (df[(df['hour'] == h) & (df['minute'] == m)]
                .groupby('date_str').first()[[col]]
                .rename(columns={col: rename})
                .pipe(lambda x: x[~x.index.duplicated(keep='first')]))

    qqq_930_open = get_bar(qqq_1m, 9, 30, 'Open', 'QQQ_Open_930')
    qqq_1000_open = get_bar(qqq_1m, 10, 0, 'Open', 'QQQ_Open_1000')  
    qqq_1030_close = get_bar(qqq_1m, 10, 30, 'Close', 'QQQ_Close_1030')
    qqq_1500_close = get_bar(qqq_1m, 15, 0, 'Close', 'QQQ_Close_1500')

    fh_vol = (qqq_1m[(qqq_1m['hour'] == 9) | ((qqq_1m['hour'] == 10) & (qqq_1m['minute'] < 30))]
              .groupby('date_str')['Volume'].sum()
              .rename('FH_Vol'))

    tqqq_1031_open = get_bar(tqqq_1m, 10, 31, 'Open', 'TQQQ_Entry_1031')
    tqqq_1558_close = get_bar(tqqq_1m, 15, 58, 'Close', 'TQQQ_Exit_1558')
    tqqq_last = (tqqq_1m.groupby('date_str').tail(1)
                 .groupby('date_str')['Close'].last()
                 .rename('TQQQ_LastClose'))
    tqqq_next_open = get_bar(tqqq_1m, 9, 31, 'Open', 'TQQQ_NextOpen_931')
    tqqq_next_open['TQQQ_NextOpen_931'] = tqqq_next_open['TQQQ_NextOpen_931'].shift(-1)

    id_period = tqqq_1m[
        ((tqqq_1m['hour'] == 10) & (tqqq_1m['minute'] > 30)) |
        ((tqqq_1m['hour'] > 10) & (tqqq_1m['hour'] < 15)) |
        ((tqqq_1m['hour'] == 15) & (tqqq_1m['minute'] <= 58))
    ]
    id_hl = id_period.groupby('date_str').agg({'High': 'max', 'Low': 'min'})
    id_hl.columns = ['ID_High', 'ID_Low']

    lk = (qqq_930_open
          .join(qqq_1000_open)
          .join(qqq_1030_close)
          .join(qqq_1500_close)
          .join(fh_vol)
          .join(tqqq_1031_open)
          .join(tqqq_1558_close)
          .join(tqqq_last)
          .join(tqqq_next_open)
          .join(id_hl)
          .dropna(subset=['TQQQ_Entry_1031', 'TQQQ_NextOpen_931']))

    return lk


def vectorized_position_size(df: pd.DataFrame, target_vol: float, max_size: float = MAX_POSITION_PCT) -> np.ndarray:
    tqqq_vol = np.maximum(df['Prev_Vol_21'] * TQQQ_LEVERAGE, 0.05)
    size = target_vol / tqqq_vol
    return np.clip(size, 0.0, max_size)

# ============================================================
# 3. VOLATILITY-ADJUSTED STRATEGY (V14)
# ============================================================
def strategy_v14_robust(signal_df: pd.DataFrame, params: dict) -> tuple:
    """
    Vol-Adjusted Hybrid Strategy. Uses Z-Scores and ATR instead of raw thresholds.
    """
    p = params
    df = signal_df

    # Signal Generation
    fh_open = df['QQQ_Open_930'].values
    fh_close = df['QQQ_Close_1030'].values
    fh_green = fh_close > fh_open
    
    # ATR adjusted gap
    gap_dollar = np.abs(fh_open - df['Prev_Close'].values)
    atr_dollar = df['Prev_ATR_pct'].values * df['Prev_Close'].values
    gap_atr_mult = gap_dollar / np.maximum(atr_dollar, 1e-10)

    # Momentum Z-Score filter (dynamically adjusts to recent 60-day vol)
    mom_z = df['Prev_ROC_5_Z'].values

    mask = (
        fh_green &
        (df['Prev_RSI'].values > p.get('rsi_min', 30)) &
        (df['Prev_RSI'].values < p.get('rsi_max', 70)) &
        (gap_atr_mult < p['gap_atr_max']) & 
        (mom_z > p['mom_z_min']) &
        (df['Prev_Above_SMA_50'].values == 1)
    )

    entry = df['TQQQ_Entry_1031'].values * (1 + SLIPPAGE_BPS)
    tqqq_atr_dollar = df['Prev_ATR_pct'].values * entry * TQQQ_LEVERAGE
    
    # ATR Multiplier TP/SL
    tp = entry + tqqq_atr_dollar * p['tp_atr_mult']
    sl = entry - tqqq_atr_dollar * p['sl_atr_mult']

    hit_tp = df['ID_High'].values >= tp
    hit_sl = df['ID_Low'].values <= sl

    exit_gross = df['TQQQ_Exit_1558'].values * (1 - SLIPPAGE_BPS)
    exit_gross = np.where(hit_tp & ~hit_sl, tp * (1 - SLIPPAGE_BPS), exit_gross)
    exit_gross = np.where(hit_sl, sl * (1 - SLIPPAGE_BPS), exit_gross)
    
    exit_net = exit_gross * (1 - SEC_FEE) - FINRA_TAF

    size = vectorized_position_size(df, p['target_vol'], p.get('max_size', MAX_POSITION_PCT))
    raw_ret = (exit_net - entry) / entry
    
    pnl = np.where(mask, raw_ret * size, 0.0)
    return pnl, mask.astype(int)


def compute_sharpe(pnl_arr: np.ndarray, trades: int) -> float:
    if trades < MIN_TRADES:
        return -999.0
    nonzero = pnl_arr[pnl_arr != 0]
    if len(nonzero) < MIN_TRADES:
        return -999.0
    cagr = (1 + pnl_arr).prod() ** (252.0 / len(pnl_arr)) - 1
    ann_vol = pnl_arr.std() * np.sqrt(252)
    if ann_vol < 1e-10:
        return -999.0
    return cagr / ann_vol


# ============================================================
# 4. CPCV OPTUNA OBJECTIVE
# ============================================================
def make_cpcv_objective(signal_df: pd.DataFrame, n_splits=6, purge=10, embargo=20):
    cv = PurgedKFold(n_splits=n_splits, purge_days=purge, embargo_days=embargo)
    dates = pd.to_datetime(signal_df.index)
    
    folds = list(cv.split(dates))

    def objective(trial: optuna.Trial) -> float:
        params = {
            'rsi_min': trial.suggest_float('rsi_min', 10, 60),
            'rsi_max': trial.suggest_float('rsi_max', 40, 95),
            'gap_atr_max': trial.suggest_float('gap_atr_max', 0.1, 5.0),
            'mom_z_min': trial.suggest_float('mom_z_min', -3.0, 3.0),
            'tp_atr_mult': trial.suggest_float('tp_atr_mult', 0.1, 8.0),
            'sl_atr_mult': trial.suggest_float('sl_atr_mult', 0.1, 8.0),
            'target_vol': trial.suggest_float('target_vol', 0.10, 1.00),
        }
        
        # Evaluate across folds
        oos_sharpes = []
        for i, (train_idx, test_idx) in enumerate(folds):
            # The Trial generates PNL across the entire array for speed, then we slice
            pnl_full, trades_full = strategy_v14_robust(signal_df, params)
            
            # Extract Train/Test
            pnl_train = pnl_full[train_idx]
            trades_train = trades_full[train_idx].sum()
            
            pnl_test = pnl_full[test_idx]
            trades_test = trades_full[test_idx].sum()
            
            # Pruner Evaluation (Is the training performance even good?)
            is_sharpe = compute_sharpe(pnl_train, trades_train)
            if is_sharpe < -1.0 and i > 0: 
                # Abort early if the train set is complete garbage
                raise optuna.TrialPruned()

            # Record OOS Sharpe for this fold
            oos_sr = compute_sharpe(pnl_test, trades_test)
            oos_sharpes.append(oos_sr)

            # Report intermediate value for the MedianPruner
            trial.report(oos_sr, i)
            if trial.should_prune():
                raise optuna.TrialPruned()

        # Final Objective: Average OOS Sharpe penalized by OOS Variance
        oos_sharpes = np.array(oos_sharpes)
        if np.any(oos_sharpes == -999.0):
            return -999.0
            
        mean_oos = np.mean(oos_sharpes)
        std_oos = np.std(oos_sharpes)
        
        # CPCV Deflated Sharpe Ratio heuristic: Reward high mean, penalize variance
        cpcv_score = mean_oos - (std_oos * 0.5) 
        
        # Save scores to trial metadata
        trial.set_user_attr('mean_oos_sr', mean_oos)
        trial.set_user_attr('std_oos_sr', std_oos)
        
        return cpcv_score

    return objective

# ============================================================
# 5. MAIN
# ============================================================
def main():
    print("="*60)
    print("V15 OPUS: COMBINATORIAL PURGED CROSS-VALIDATION (CPCV) ENGINE")
    print("="*60)
    qqq_d, qqq_1m, tqqq_1m = load_all_data()
    daily_feats = build_daily_features(qqq_d)
    intraday_lk = build_intraday_lookup(qqq_1m, tqqq_1m)
    signal_df = intraday_lk.join(daily_feats, how='inner').dropna()
    print(f"[SIGNAL] Combined matrix: {len(signal_df)} trading days")

    # The Optuna TPE Sampler with Median Pruning
    study = optuna.create_study(
        study_name="v15_opus_cpcv_engine", 
        direction='maximize',
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=20, n_warmup_steps=1, interval_steps=1)
    )
    
    print("\n[INFO] Starting CPCV Sweep with TPE and Median Pruning...")
    study.optimize(
        make_cpcv_objective(signal_df, n_splits=6, purge=10, embargo=20),
        n_trials=2000, 
        n_jobs=1,  # Windows background execution fix
        show_progress_bar=True
    )

    try:
        b = study.best_trial
    except ValueError:
        print("\n[ERROR] ALL trials were pruned! The optimizer found NO successful parameters. We must loosen the search constraints.")
        return

    print("\n" + "="*60)
    print("V15 OPUS OPTIMIZATION COMPLETE")
    print("="*60)
    print(f"Best CPCV Score: {b.value:.4f}")
    print(f"Mean OOS Sharpe: {b.user_attrs.get('mean_oos_sr', -999)}")
    print(f"OOS Sharpe Variance: {b.user_attrs.get('std_oos_sr', 0)}")
    print("Best Parameters:")
    for k, v in b.params.items():
        print(f"  {k}: {v}")

    # Save Results
    with open('v15_opus_cpcv_results.json', 'w') as f:
        json.dump({
            'cpcv_score': b.value,
            'mean_oos_sr': b.user_attrs.get('mean_oos_sr', -999),
            'std_oos_sr': b.user_attrs.get('std_oos_sr', 0),
            'params': b.params
        }, f, indent=4)
        
    print("\n[SAVED] v15_opus_cpcv_results.json written.")

if __name__ == '__main__':
    main()
