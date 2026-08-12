import pandas as pd
import numpy as np
import json
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV
import os
import warnings
warnings.filterwarnings('ignore')

# -------------------------------------------------------------
# PHASE 3: TRIPLE BARRIER LABELING
# -------------------------------------------------------------

def get_grinder_barriers(df, entry_indices, params):
    events = []
    
    total_cost_bps = 3
    cost_dec = (total_cost_bps / 10000.0)
    
    df_vol = df['YZ_Vol'].values
    df_open = df['Open'].values
    df_high = df['High'].values
    df_low = df['Low'].values
    df_close = df['Close'].values
    
    sl_mult = params['sl_mult']
    tp_mult = params['tp_mult']
    vb_mult = params['vb_mult']
    
    for idx in entry_indices:
        trade_idx = idx + 1
        if trade_idx >= len(df): continue
            
        vol_t = df_vol[idx]
        if np.isnan(vol_t) or vol_t == 0: continue
        
        tp_pct = tp_mult * (vol_t / np.sqrt(252))
        sl_pct = sl_mult * (vol_t / np.sqrt(252))
        v_barrier = max(1, int(vb_mult * (0.15 / vol_t)))
        
        entry_price = df_open[trade_idx]
        
        hit_barrier = False
        exit_idx = trade_idx
        exit_ret = 0
        
        direction = params['direction']
        
        for k in range(v_barrier):
            curr_idx = trade_idx + k
            if curr_idx >= len(df):
                exit_idx = len(df) - 1
                if direction == 'long':
                    exit_ret = (df_close[exit_idx] / entry_price) - 1.0
                else:
                    exit_ret = (entry_price / df_close[exit_idx]) - 1.0
                hit_barrier = True
                break
                
            high_p = df_high[curr_idx]
            low_p = df_low[curr_idx]
            
            if direction == 'long':
                if low_p <= entry_price * (1 - sl_pct):
                    exit_idx = curr_idx
                    exit_ret = -sl_pct
                    hit_barrier = True
                    break
                elif high_p >= entry_price * (1 + tp_pct):
                    exit_idx = curr_idx
                    exit_ret = tp_pct
                    hit_barrier = True
                    break
            else: # short
                if high_p >= entry_price * (1 + sl_pct):
                    exit_idx = curr_idx
                    exit_ret = -sl_pct
                    hit_barrier = True
                    break
                elif low_p <= entry_price * (1 - tp_pct):
                    exit_idx = curr_idx
                    exit_ret = tp_pct
                    hit_barrier = True
                    break
                
        if not hit_barrier:
            exit_idx = min(trade_idx + v_barrier - 1, len(df) - 1)
            if direction == 'long':
                exit_ret = (df_close[exit_idx] / entry_price) - 1.0
            else:
                exit_ret = (entry_price / df_close[exit_idx]) - 1.0
            
        net_ret = exit_ret - cost_dec * 2
        label = 1 if net_ret > 0 else 0
        
        events.append({
            't0': idx,
            't1': exit_idx,
            'label': label,
            'entry_price': entry_price
        })
        
    return pd.DataFrame(events)

def get_uniqueness_weights(events, n_samples):
    # Count concurrent active labels
    weights = np.zeros(n_samples)
    for i, row in events.iterrows():
        t0, t1 = int(row['t0']), int(row['t1'])
        # Add 1 to the count of active trades for these bars
        weights[t0:t1+1] += 1
        
    event_weights = []
    for i, row in events.iterrows():
        t0, t1 = int(row['t0']), int(row['t1'])
        # Average uniqueness = 1 / average concurrent trades
        avg_concurrency = np.mean(weights[t0:t1+1])
        event_weights.append(1.0 / avg_concurrency if avg_concurrency > 0 else 1.0)
        
    events['weight'] = event_weights
    return events

# -------------------------------------------------------------
# PHASE 3.5: SEQUENCE-AWARE META LABELING (LSTM + XGBOOST)
# -------------------------------------------------------------

class ContextLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=16, output_dim=8, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        out, (hn, cn) = self.lstm(x)
        # Take the last time step
        context = self.fc(out[:, -1, :])
        return context

def build_sequence_dataset(df, events, seq_len=60):
    latent_cols = [c for c in df.columns if c.startswith('Latent_')]
    
    X_seq = []
    X_tab = []
    y = []
    w = []
    
    for i, row in events.iterrows():
        t0 = int(row['t0'])
        if t0 < seq_len - 1:
            continue # Need enough history
            
        seq = df.loc[t0-seq_len+1:t0, latent_cols].values
        tab = df.loc[t0, latent_cols + ['YZ_Vol', 'RSI_14']].values
        
        X_seq.append(seq)
        X_tab.append(tab)
        y.append(row['label'])
        w.append(row['weight'])
        
    return np.array(X_seq), np.array(X_tab), np.array(y), np.array(w)

def seq_bootstrap(events_df, n_samples=None):
    if n_samples is None:
        n_samples = len(events_df)
        
    t0_array = events_df['t0'].values
    t1_array = events_df['t1'].values
    
    max_t = int(np.max(t1_array)) + 1
    c = np.zeros(max_t)
    phi = []
    
    for _ in range(n_samples):
        inv_c = 1.0 / (1.0 + c)
        u = np.zeros(len(events_df))
        for j in range(len(events_df)):
            t0 = int(t0_array[j])
            t1 = int(t1_array[j])
            length = t1 - t0 + 1
            if length > 0:
                u[j] = np.sum(inv_c[t0:t1+1]) / length
                
        prob = u / np.sum(u)
        drawn_idx = np.random.choice(len(events_df), p=prob)
        phi.append(drawn_idx)
        
        t0 = int(t0_array[drawn_idx])
        t1 = int(t1_array[drawn_idx])
        c[t0:t1+1] += 1
        
    return phi

def train_hybrid_meta_labeler(df, events, params):
    print("Building Hybrid Meta-Labeler Dataset...")
    if len(events) < 50:
        print("[WARNING] Not enough events for meta-labeling.")
        return None, None
        
    X_seq, X_tab, y, w = build_sequence_dataset(df, events)
    if len(X_seq) < 50:
        print("[WARNING] Not enough valid sequences.")
        return None, None
    
    # Train test split (chronological for finance)
    split_idx = int(len(X_seq) * 0.8)
    
    X_seq_te = X_seq[split_idx:]
    X_tab_te = X_tab[split_idx:]
    y_te = y[split_idx:]
    w_te = w[split_idx:]
    events_te = events.iloc[split_idx:]
    
    first_test_t0 = events_te.iloc[0]['t0'] if len(events_te) > 0 else np.inf
    valid_tr_mask = events.iloc[:split_idx]['t1'] < first_test_t0
    
    X_seq_tr = X_seq[:split_idx][valid_tr_mask]
    X_tab_tr = X_tab[:split_idx][valid_tr_mask]
    y_tr = y[:split_idx][valid_tr_mask]
    w_tr = w[:split_idx][valid_tr_mask]
    
    print("Applying Sequential Bootstrapping to Training Set...")
    events_tr = events.iloc[:split_idx][valid_tr_mask].copy().reset_index(drop=True)
    phi_tr = seq_bootstrap(events_tr)
    
    X_seq_tr_boot = X_seq_tr[phi_tr]
    X_tab_tr_boot = X_tab_tr[phi_tr]
    y_tr_boot = y_tr[phi_tr]
    w_tr_boot = w_tr[phi_tr]
    
    print("Training Sequence Context LSTM...")
    X_seq_tensor = torch.tensor(X_seq_tr_boot, dtype=torch.float64)
    y_tensor = torch.tensor(y_tr_boot, dtype=torch.long)
    
    lstm_model = ContextLSTM(input_dim=X_seq.shape[2], hidden_dim=16, output_dim=8).double()
    # Define the projection layer and add it to the optimizer
    proj_layer = nn.Linear(8, 2).double()
    criterion = nn.CrossEntropyLoss()
    
    # Combine parameters for optimizer
    optim_params = list(lstm_model.parameters()) + list(proj_layer.parameters())
    optimizer = torch.optim.Adam(optim_params, lr=0.01, weight_decay=1e-4)
    
    for epoch in range(50):
        optimizer.zero_grad()
        context = lstm_model(X_seq_tensor)
        proj = proj_layer(context)
        loss = criterion(proj, y_tensor)
        loss.backward()
        optimizer.step()
        
    lstm_model.eval()
    with torch.no_grad():
        context_tr = lstm_model(torch.tensor(X_seq_tr_boot, dtype=torch.float64)).numpy()
        context_te = lstm_model(torch.tensor(X_seq_te, dtype=torch.float64)).numpy()
        
    X_hybrid_tr = np.hstack([X_tab_tr_boot, context_tr])
    X_hybrid_te = np.hstack([X_tab_te, context_te])
    
    print("Training XGBoost Meta-Labeler with Sample Weights & Isotonic Calibration...")
    xgb = XGBClassifier(
        max_depth=3,
        learning_rate=0.05,
        n_estimators=100,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective='binary:logistic'
    )
    
    if len(np.unique(y_tr_boot)) < 2:
        print("[WARNING] Only 1 class present in training data. Skipping XGBoost.")
        return lstm_model, None
        
    calibrated_xgb = CalibratedClassifierCV(estimator=xgb, method='isotonic', cv=3)
    calibrated_xgb.fit(X_hybrid_tr, y_tr_boot, sample_weight=w_tr_boot)
    
    preds_prob_tr = calibrated_xgb.predict_proba(X_hybrid_tr)[:, 1]
    preds_prob_te = calibrated_xgb.predict_proba(X_hybrid_te)[:, 1]
    
    print("Meta-Labeling Train Accuracy:", accuracy_score(y_tr_boot, preds_prob_tr > 0.5))
    print("Meta-Labeling Test Accuracy:", accuracy_score(y_te, preds_prob_te > 0.5))
    print("\nTest Classification Report:")
    print(classification_report(y_te, preds_prob_te > 0.5))
    
    # Kelly Criterion Calculation
    W = params['tp_mult'] / params['sl_mult']
    kelly = preds_prob_te - (1 - preds_prob_te) / W
    fractional_kelly = np.clip(kelly / 4.0, 0, 1)
    
    active_kelly = fractional_kelly[fractional_kelly > 0]
    if len(active_kelly) > 0:
        print(f"Average Fractional Kelly Size (when > 0): {np.mean(active_kelly):.2%}")
    else:
        print("No positive Kelly sizing in test set.")
    
    return lstm_model, calibrated_xgb

def execute_meta_pipeline(ticker):
    print(f"Executing Meta Labeling for {ticker}...")
    df = pd.read_parquet(f'{ticker}_daily_V17_latent.parquet')
    df = df.reset_index(drop=True)
    
    with open(f'{ticker}_trial_ledger.json', 'r') as f:
        ledger = json.load(f)
        
    # Get best trial parameters to generate base signals
    best_trial = max(ledger, key=lambda x: x['value'])
    params = best_trial['params']
    
    print(f"Generating base signals using best parameters: {params}")
    df['Signal'] = 0
    latent_col = f"Latent_{params['latent_dim']}"
    if params['direction'] == 'long':
        df.loc[df[latent_col] < -params['entry_z'], 'Signal'] = 1
    else:
        df.loc[df[latent_col] > params['entry_z'], 'Signal'] = 1
    
    entry_indices = df[df['Signal'] == 1].index.tolist()
    print(f"Total base signals generated: {len(entry_indices)}")
    
    events = get_grinder_barriers(df, entry_indices, params)
    events = get_uniqueness_weights(events, len(df))
    
    print(f"Events labeled: {len(events)}")
    print(f"Positive labels (1): {events['label'].sum()}")
    print(f"Negative labels (0): {len(events) - events['label'].sum()}")
    
    lstm, xgb = train_hybrid_meta_labeler(df, events, params)
    print(f"[SUCCESS] Phase 3 & 3.5 Complete for {ticker}.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", type=str, required=True)
    args = parser.parse_args()
    
    execute_meta_pipeline(args.ticker)
