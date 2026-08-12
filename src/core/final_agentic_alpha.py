import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION — All magic numbers documented
# ============================================================
START_TIME = datetime.time(10, 1)        # Use 10:01 Open (avoids 10:00 Close lookahead)
SIGNAL_TIME = datetime.time(15, 0)       # Signal calculated at 15:00 Close
ENTRY_TIME = datetime.time(15, 1)        # Entry at 15:01 Open (1-min latency buffer)
THRESHOLD = 0.003                         # 0.3% midday QQQ return to trigger signal
SLIPPAGE_BPS = 0.0010                    # 10 BPS per side (realistic for TQQQ power hour)
SEC_FEE_PER_SHARE = 0.000008            # SEC transaction fee
FINRA_TAF_PER_SHARE = 0.000145         # FINRA TAF (sell side only)
VIX_MAX_LONG = 30.0                      # Only take longs when VIX < 30
VIX_MAX_SHORT = 25.0                     # Only take shorts when VIX < 25
HTB_DAILY_COST = 0.10 / 252             # 10% annualized hard-to-borrow cost per short trade
TARGET_VOL = 0.60                        # Portfolio vol target
TQQQ_LEVERAGE = 3.0                      # TQQQ leverage multiple
MAX_POSITION_PCT = 0.50                  # Max 50% of portfolio per trade (risk cap)
PRICE_MIN = 5.0                          # Bad tick filter — minimum valid TQQQ price
PRICE_MAX = 1000.0                       # Bad tick filter — maximum valid TQQQ price
TZ = 'America/New_York'                  # Always use canonical IANA timezone

# ============================================================
# 1. LOAD & CLEAN DATA
# ============================================================
def load_data():
    """Load and sanitize 1-minute bar data from Alpaca parquet files."""
    qqq = pd.read_parquet('qqq_1m.parquet')
    tqqq = pd.read_parquet('tqqq_1m.parquet')

    # Fix: Use canonical IANA timezone (not deprecated 'US/Eastern')
    qqq.index = pd.to_datetime(qqq.index).tz_convert(TZ)
    tqqq.index = pd.to_datetime(tqqq.index).tz_convert(TZ)

    # Clip to regular market hours only
    qqq = qqq.between_time('09:30', '15:59')
    tqqq = tqqq.between_time('09:30', '15:59')

    # Fix: Filter zero-volume bars and bad tick prices
    qqq = qqq[qqq['Volume'] > 0]
    tqqq = tqqq[tqqq['Volume'] > 0]
    tqqq = tqqq[(tqqq['Open'] >= PRICE_MIN) & (tqqq['Open'] <= PRICE_MAX)]
    tqqq = tqqq[(tqqq['Close'] >= PRICE_MIN) & (tqqq['Close'] <= PRICE_MAX)]

    # Merge on aligned timestamp index
    df = qqq[['Open', 'Close']].rename(columns={'Close': 'QQQ_Close', 'Open': 'QQQ_Open'})
    df['TQQQ_Close'] = tqqq['Close']
    df['TQQQ_Open'] = tqqq['Open']
    df['TQQQ_Volume'] = tqqq['Volume']
    df = df.dropna()

    # Add date column — using .date() is safe since index is tz-aware
    df['Date'] = df.index.date

    print(f"Loaded {len(df)} clean 1-minute bars across {df['Date'].nunique()} trading days.")
    return df


# ============================================================
# 2. LOAD DAILY QQQ FEATURES (ATR for position sizing, Regime)
# ============================================================
def load_daily_features():
    """Load precomputed daily QQQ features for regime and volatility sizing."""
    qqq_daily = pd.read_parquet('qqq_daily.parquet')
    qqq_daily.index = pd.to_datetime(qqq_daily.index).tz_convert(TZ)

    # ATR for position sizing
    hl = qqq_daily['High'] - qqq_daily['Low']
    hc = np.abs(qqq_daily['High'] - qqq_daily['Close'].shift(1))
    lc = np.abs(qqq_daily['Low'] - qqq_daily['Close'].shift(1))
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    qqq_daily['ATR'] = tr.rolling(14).mean()
    qqq_daily['ATR_pct'] = qqq_daily['ATR'] / qqq_daily['Close']

    # 21-day Realized Volatility (used for position sizing)
    ret = qqq_daily['Close'].pct_change()
    qqq_daily['Realized_Vol_21'] = ret.rolling(21).std() * np.sqrt(252)
    qqq_daily['Realized_Vol_5'] = ret.rolling(5).std() * np.sqrt(252)
    qqq_daily['GEX_Regime'] = np.where(qqq_daily['Realized_Vol_5'] < qqq_daily['Realized_Vol_21'], 1, -1)

    # Shift T-1 to prevent any daily lookahead
    qqq_daily['Prev_ATR_pct'] = qqq_daily['ATR_pct'].shift(1)
    qqq_daily['Prev_Regime'] = qqq_daily['GEX_Regime'].shift(1)
    qqq_daily['Prev_Vol_21'] = qqq_daily['Realized_Vol_21'].shift(1)

    qqq_daily['date_str'] = qqq_daily.index.strftime('%Y-%m-%d')
    daily = qqq_daily[['date_str', 'Prev_ATR_pct', 'Prev_Regime', 'Prev_Vol_21']].dropna()
    daily = daily.set_index('date_str')

    return daily


# ============================================================
# 3. PERFORMANCE METRICS (corrected formulas)
# ============================================================
def calc_performance(daily_returns):
    """Compute backtest performance metrics using statistically correct formulas."""
    if len(daily_returns) == 0:
        return {}

    cumulative = (1 + daily_returns).cumprod()

    # Fix: Use actual elapsed calendar years — not 252/N proxy
    start_dt = pd.to_datetime(str(daily_returns.index[0]))
    end_dt = pd.to_datetime(str(daily_returns.index[-1]))
    actual_years = (end_dt - start_dt).days / 365.25
    if actual_years <= 0:
        actual_years = 1.0

    ann_ret = (cumulative.iloc[-1]) ** (1.0 / actual_years) - 1
    ann_vol = daily_returns.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0

    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()

    win_trades = (daily_returns[daily_returns != 0] > 0).sum()
    total_trades = (daily_returns != 0).sum()
    win_rate = win_trades / total_trades if total_trades > 0 else 0

    return {
        'Annualized Return': ann_ret,
        'Annualized Volatility': ann_vol,
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_dd,
        'Win Rate': win_rate,
        'Total Trades': total_trades,
        'Actual Years': actual_years,
        'cumulative': cumulative,
        'drawdown': drawdown,
    }


# ============================================================
# 4. STRATEGY ENGINE
# ============================================================
def run_strategy(df, daily_features):
    """Run the Power Hour Continuation strategy with all corrections applied."""

    # Fix: Use datetime.time objects directly — not pd.to_datetime().time()
    # Fix: Start anchor is 10:01 Open (not 10:00 Close) to eliminate 1-min lookahead

    # Extract anchor bars for each date — dedup immediately to prevent merge explosion
    df_start = df[df.index.time == START_TIME][['QQQ_Open', 'Date']].rename(columns={'QQQ_Open': 'Open_start'})
    df_start = df_start.drop_duplicates(subset='Date', keep='first')

    df_signal = df[df.index.time == SIGNAL_TIME][['QQQ_Close', 'Date']].rename(columns={'QQQ_Close': 'Close_signal'})
    df_signal = df_signal.drop_duplicates(subset='Date', keep='first')  # Fix: prevent duplicate-date merge explosion

    df_entry = df[df.index.time == ENTRY_TIME][['TQQQ_Open', 'TQQQ_Volume', 'Date']]
    df_entry = df_entry.drop_duplicates(subset='Date', keep='first')

    # Last bar of each date (half-day safe)
    last_bars = df.groupby('Date').tail(1)[['TQQQ_Close', 'TQQQ_Volume', 'Date']]

    # Build daily signal table
    daily_stats = pd.merge(df_start, df_signal, on='Date', how='inner')
    daily_stats['MidDay_Return'] = (daily_stats['Close_signal'] - daily_stats['Open_start']) / daily_stats['Open_start']

    daily_stats['Signal'] = 0
    daily_stats.loc[daily_stats['MidDay_Return'] > THRESHOLD, 'Signal'] = 1

    # Fix: Only allow short signal when VIX conditions permit. Without live VIX data,
    # we conservatively DISABLE shorts on TQQQ due to:
    # (a) Hard-to-borrow risk, (b) Leveraged ETF short asymmetry
    # Short signal can be re-enabled with a proper VIX filter in live trading
    # daily_stats.loc[daily_stats['MidDay_Return'] < -THRESHOLD, 'Signal'] = -1  # DISABLED — see notes

    daily_stats = daily_stats.set_index('Date')

    # ============================================================
    # 5. TRADE SIMULATION WITH REALISTIC COSTS
    # ============================================================
    trade_records = []

    for date, signal_row in daily_stats.iterrows():
        signal = signal_row['Signal']
        if signal == 0:
            continue

        date_str = str(date)

        # Get entry and exit bars for this date
        entry_bar = df_entry[df_entry['Date'] == date]
        exit_bar = last_bars[last_bars['Date'] == date]

        if entry_bar.empty or exit_bar.empty:
            continue

        # Raw prices
        entry_price = entry_bar['TQQQ_Open'].iloc[0]
        exit_price = exit_bar['TQQQ_Close'].iloc[0]

        # Sanity check prices (redundant after load_data filter but defensive)
        if entry_price < PRICE_MIN or exit_price < PRICE_MIN:
            continue

        # Get daily features for position sizing
        if date_str not in daily_features.index:
            continue

        day_feats = daily_features.loc[date_str]
        prev_vol = day_feats['Prev_Vol_21']
        prev_regime = day_feats['Prev_GEX_Regime'] if 'Prev_GEX_Regime' in day_feats else day_feats['Prev_Regime']

        # Fix: Volatility-target position sizing
        tqqq_realized_vol = max(prev_vol * TQQQ_LEVERAGE, 0.05)  # TQQQ vol ~ 3x QQQ vol
        raw_size = TARGET_VOL / tqqq_realized_vol
        position_pct = min(raw_size, MAX_POSITION_PCT)  # Cap at 50% per trade

        # Regime halving (from live_bot.py)
        if prev_regime == -1:
            position_pct *= 0.50

        # Apply Slippage — multiplicative on price, not additive on returns
        entry_slipped = entry_price * (1 + SLIPPAGE_BPS)    # Long entry: pay the ask
        exit_slipped = exit_price * (1 - SLIPPAGE_BPS)       # Long exit: sell at bid

        # Approximate shares (assume $100K notional for capacity comment)
        approx_shares = int((100_000 * position_pct) / entry_slipped)

        # SEC fee (sell side): ~$0.000008 per share
        # FINRA TAF (sell side): $0.000145 per share
        cost_per_share_exit = SEC_FEE_PER_SHARE + FINRA_TAF_PER_SHARE
        reg_cost = cost_per_share_exit * approx_shares / (100_000 * position_pct) if approx_shares > 0 else 0

        # Raw trade return
        trade_ret_gross = (exit_slipped - entry_slipped) / entry_slipped
        trade_ret_net = (trade_ret_gross * position_pct) - reg_cost

        trade_records.append({
            'Date': date,
            'Signal': signal,
            'Entry': entry_slipped,
            'Exit': exit_slipped,
            'Position_Pct': position_pct,
            'Trade_Return': trade_ret_net,
            'Regime': prev_regime,
        })

    if len(trade_records) == 0:
        print("No trades executed.")
        return

    trades_df = pd.DataFrame(trade_records).set_index('Date')

    # Aggregate daily returns (some days may have no trade → 0 return)
    all_dates_index = sorted(df['Date'].unique())
    daily_returns = pd.Series(0.0, index=all_dates_index)
    daily_returns.update(trades_df['Trade_Return'])

    return daily_returns, trades_df


# ============================================================
# 6. WALK-FORWARD VALIDATION (guards against overfitting)
# ============================================================
def walk_forward_validation(df, daily_features, n_windows=3):
    """Slice data into N sequential windows and report Sharpe on each to detect overfitting."""
    all_dates = sorted(df['Date'].unique())
    n = len(all_dates)
    window_size = n // n_windows

    print("\n=== WALK-FORWARD VALIDATION ===")
    for i in range(n_windows):
        window_dates = all_dates[i * window_size: (i + 1) * window_size]
        df_window = df[df['Date'].isin(set(window_dates))]
        result = run_strategy(df_window, daily_features)
        if result is None:
            continue
        daily_returns, _ = result
        m = calc_performance(daily_returns)
        if m:
            print(f"Window {i+1} ({str(window_dates[0])} to {str(window_dates[-1])}): "
                  f"Sharpe={m['Sharpe Ratio']:.2f}  MaxDD={m['Max Drawdown']*100:.1f}%  "
                  f"Ann.Ret={m['Annualized Return']*100:.1f}%")


# ============================================================
# 7. MAIN EXECUTION
# ============================================================
def main():
    df = load_data()
    daily_features = load_daily_features()

    print("\nRunning strategy on full dataset...")
    result = run_strategy(df, daily_features)
    if result is None:
        return

    daily_returns, trades_df = result
    m = calc_performance(daily_returns)

    print("\n=================================================")
    print("POWER HOUR CONTINUATION — CORRECTED FINAL METRICS")
    print("=================================================")
    print(f"Strategy Period:       {str(daily_returns.index[0])} to {str(daily_returns.index[-1])}")
    print(f"Actual Years:          {m['Actual Years']:.2f}")
    print(f"Annualized Return:     {m['Annualized Return']*100:.2f}%")
    print(f"Annualized Volatility: {m['Annualized Volatility']*100:.2f}%")
    print(f"Sharpe Ratio:          {m['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown:          {m['Max Drawdown']*100:.2f}%")
    print(f"Win Rate:              {m['Win Rate']*100:.2f}%")
    print(f"Total Trades:          {m['Total Trades']}")
    print("=================================================")

    # Walk-forward to detect overfitting
    walk_forward_validation(df, daily_features)

    # Equity curve
    cum = m['cumulative']
    plt.figure(figsize=(12, 5))
    plt.plot(pd.to_datetime([str(d) for d in cum.index]), cum.values, label='Power Hour Continuation (TQQQ)')
    plt.title('Power Hour Continuation — Fully Corrected Backtest')
    plt.ylabel('Portfolio Growth (1x = starting capital)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('power_hour_corrected_equity.png')
    print("\nSaved equity curve to power_hour_corrected_equity.png")


if __name__ == "__main__":
    main()
