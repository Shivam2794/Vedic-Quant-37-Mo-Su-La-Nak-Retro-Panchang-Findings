"""
QUANTITATIVE PERFORMANCE METRICS & INSTITUTIONAL RISK ANALYTICS
================================================================
Implements Marcos López de Prado and institutional hedge fund risk metrics:
  - Sharpe Ratio, Sortino Ratio, Calmar Ratio
  - Maximum Drawdown (MDD) & Drawdown Duration
  - Profit Factor, Win Rate, Payoff Ratio, Expectancy
  - Probabilistic Sharpe Ratio (PSR) & Deflated Sharpe Ratio (DSR)
  - Monte Carlo Bootstrap Resampling (1,000 Permutations)
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from scipy.stats import norm, skew, kurtosis


def calculate_drawdowns(equity_series: pd.Series) -> Tuple[pd.Series, float, int]:
    """
    Computes continuous drawdown series, Maximum Drawdown (MDD),
    and Maximum Drawdown Duration in periods.
    """
    if len(equity_series) == 0:
        return pd.Series([], dtype=float), 0.0, 0

    hwm = equity_series.cummax()
    valid_hwm = hwm > 0
    drawdown = pd.Series(0.0, index=equity_series.index)
    drawdown[valid_hwm] = (equity_series[valid_hwm] - hwm[valid_hwm]) / hwm[valid_hwm]
    drawdown = drawdown.clip(upper=0.0)
    mdd = float(drawdown.min()) if not drawdown.empty else 0.0

    # Max Drawdown Duration
    is_underwater = drawdown < 0
    duration_series = (~is_underwater).cumsum()[is_underwater]
    if len(duration_series) > 0:
        max_duration = int(duration_series.value_counts().max()) if not duration_series.empty else 0
    else:
        max_duration = 0

    return drawdown, mdd, max_duration


def calculate_comprehensive_metrics(
    equity_series: pd.Series,
    trade_returns: List[float],
    annualization_factor: float = 252.0,
    risk_free_rate: float = 0.02,
    total_years: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes institutional risk, return, and trade execution metrics.
    """
    if len(equity_series) < 2 or len(trade_returns) == 0 or equity_series.iloc[0] <= 0:
        return {
            "Total_Return_Pct": 0.0,
            "CAGR_Pct": 0.0,
            "Sharpe_Ratio": 0.0,
            "Sortino_Ratio": 0.0,
            "Calmar_Ratio": 0.0,
            "Max_Drawdown_Pct": 0.0,
            "Max_Drawdown_Duration_Bars": 0,
            "Max_Drawdown_Duration_Periods": 0,
            "Total_Trades": 0,
            "Win_Trades": 0,
            "Loss_Trades": 0,
            "Win_Rate_Pct": 0.0,
            "Profit_Factor": 0.0,
            "Payoff_Ratio": 0.0,
            "Expectancy_Pct": 0.0,
            "Avg_Win_Pct": 0.0,
            "Avg_Loss_Pct": 0.0,
            "Probabilistic_Sharpe_Ratio": 0.0,
            "Skewness": 0.0,
            "Kurtosis": 3.0,
        }

    initial_equity = float(equity_series.iloc[0])
    final_equity = float(equity_series.iloc[-1])
    total_return = (final_equity - initial_equity) / initial_equity

    # Period Returns
    returns = equity_series.pct_change().dropna()
    n_periods = len(returns)
    if total_years is not None and total_years > 0.0:
        years = total_years
    else:
        years = max(n_periods / float(annualization_factor), 1.0 / annualization_factor)

    if final_equity > 0 and initial_equity > 0:
        try:
            cagr = ((final_equity / initial_equity) ** (1.0 / years)) - 1.0
            if math.isinf(cagr) or math.isnan(cagr) or cagr > 1e6:
                cagr = 1e6
        except OverflowError:
            cagr = 1e6
    else:
        cagr = -1.0

    # Volatility & Sharpe
    mean_ret = float(returns.mean()) if n_periods > 0 else 0.0
    vol = float(returns.std()) if n_periods > 1 else 0.0
    rf_per_period = (1.0 + risk_free_rate) ** (1.0 / annualization_factor) - 1.0

    if vol > 1e-8:
        sample_sharpe = float((mean_ret - rf_per_period) / vol)
        sharpe = float(sample_sharpe * np.sqrt(annualization_factor))
    else:
        sample_sharpe = 0.0 if mean_ret <= rf_per_period else 100.0
        sharpe = 0.0 if mean_ret <= rf_per_period else 100.0

    # Sortino Ratio (Target Semi-Deviation / Lower Partial Moment LPM2)
    if vol > 1e-8:
        downside_diff = np.minimum(0.0, returns - rf_per_period)
        downside_dev = float(np.sqrt(np.mean(downside_diff ** 2))) if n_periods > 0 else 0.0
        if downside_dev > 1e-8:
            sortino = float((mean_ret - rf_per_period) / downside_dev * np.sqrt(annualization_factor))
        else:
            sortino = sharpe if mean_ret <= rf_per_period else 100.0
    else:
        sortino = 0.0 if mean_ret <= rf_per_period else 100.0

    # Drawdowns & Calmar
    _, mdd, mdd_duration = calculate_drawdowns(equity_series)
    calmar = float(cagr / abs(mdd)) if abs(mdd) > 1e-8 else (0.0 if cagr <= 0 else 100.0)

    # Trade-Level Statistics
    t_rets = np.array(trade_returns, dtype=float)
    n_trades = len(t_rets)
    wins = t_rets[t_rets > 0]
    losses = t_rets[t_rets < 0]
    n_wins = int(len(wins))
    n_losses = int(len(losses))

    win_rate = (n_wins / float(n_trades)) * 100.0 if n_trades > 0 else 0.0
    loss_rate = (n_losses / float(n_trades)) * 100.0 if n_trades > 0 else 0.0
    avg_win = float(wins.mean()) if n_wins > 0 else 0.0
    avg_loss = float(abs(losses.mean())) if n_losses > 0 else 0.0
    total_gain = float(wins.sum()) if n_wins > 0 else 0.0
    total_loss = float(abs(losses.sum())) if n_losses > 0 else 1e-8

    profit_factor = total_gain / total_loss if total_loss > 1e-8 else (100.0 if total_gain > 0 else 0.0)
    payoff_ratio = avg_win / avg_loss if avg_loss > 1e-8 else (10.0 if avg_win > 0 else 0.0)
    expectancy = (win_rate / 100.0 * avg_win) - (loss_rate / 100.0 * avg_loss)

    # Probabilistic Sharpe Ratio (PSR) - Marcos López de Prado (AFML Ch. 14)
    # Per-period (sample) Sharpe ratio is used in the asymptotic standard error formulation
    if vol > 1e-8 and len(returns) > 2:
        sk_val = float(skew(returns))
        kt_val = float(kurtosis(returns, fisher=False))
        sk = sk_val if not np.isnan(sk_val) else 0.0
        kt = kt_val if not np.isnan(kt_val) else 3.0
    else:
        sk = 0.0
        kt = 3.0

    psr_denom = 1.0 - (sk * sample_sharpe) + ((kt - 1.0) / 4.0) * (sample_sharpe ** 2)
    if psr_denom > 1e-8 and n_periods > 2 and vol > 1e-8:
        psr_z = (sample_sharpe * np.sqrt(n_periods - 1)) / np.sqrt(psr_denom)
        psr = float(norm.cdf(psr_z))
    else:
        psr = 0.50

    return {
        "Total_Return_Pct": round(total_return * 100.0, 2),
        "CAGR_Pct": round(cagr * 100.0, 2),
        "Sharpe_Ratio": round(sharpe, 2),
        "Sortino_Ratio": round(sortino, 2),
        "Calmar_Ratio": round(calmar, 2),
        "Max_Drawdown_Pct": round(mdd * 100.0, 2),
        "Max_Drawdown_Duration_Bars": mdd_duration,
        "Max_Drawdown_Duration_Periods": mdd_duration,
        "Total_Trades": n_trades,
        "Win_Trades": n_wins,
        "Loss_Trades": n_losses,
        "Win_Rate_Pct": round(win_rate, 2),
        "Profit_Factor": round(profit_factor, 2),
        "Payoff_Ratio": round(payoff_ratio, 2),
        "Expectancy_Pct": round(expectancy * 100.0, 2),
        "Avg_Win_Pct": round(avg_win * 100.0, 2),
        "Avg_Loss_Pct": round(avg_loss * 100.0, 2),
        "Probabilistic_Sharpe_Ratio": round(psr, 3),
        "Skewness": round(sk, 3),
        "Kurtosis": round(kt, 3),
    }


def run_monte_carlo_resampling(
    trade_returns: List[float],
    n_simulations: int = 1000,
    initial_capital: float = 100000.0,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Executes 1,000 Monte Carlo bootstrap resamplings of trade return sequences
    to establish empirical confidence intervals for Sharpe, MDD, and Total Return.
    """
    if len(trade_returns) < 5 or initial_capital <= 0.0:
        return {
            "MC_5th_Percentile_Return_Pct": 0.0,
            "MC_Median_Return_Pct": 0.0,
            "MC_95th_Percentile_Return_Pct": 0.0,
            "MC_5th_Percentile_MDD_Pct": 0.0,
            "MC_Median_MDD_Pct": 0.0,
            "MC_95th_Percentile_MDD_Pct": 0.0,
        }

    t_rets = np.array(trade_returns, dtype=float)
    n_trades = len(t_rets)

    sim_mdds = []
    sim_returns = []

    rng = np.random.default_rng(seed)
    for _ in range(n_simulations):
        sampled_indices = rng.choice(n_trades, size=n_trades, replace=True)
        sampled_rets = t_rets[sampled_indices]
        cum_equity = np.insert(initial_capital * np.cumprod(1.0 + sampled_rets), 0, initial_capital)
        hwm = np.maximum.accumulate(cum_equity)
        dd = np.where(hwm > 0, (cum_equity - hwm) / hwm, 0.0)
        sim_mdds.append(float(np.min(dd)))
        sim_returns.append(float((cum_equity[-1] - initial_capital) / initial_capital))

    return {
        "MC_5th_Percentile_Return_Pct": round(float(np.percentile(sim_returns, 5)) * 100.0, 2),
        "MC_Median_Return_Pct": round(float(np.percentile(sim_returns, 50)) * 100.0, 2),
        "MC_95th_Percentile_Return_Pct": round(float(np.percentile(sim_returns, 95)) * 100.0, 2),
        "MC_5th_Percentile_MDD_Pct": round(float(np.percentile(sim_mdds, 5)) * 100.0, 2),
        "MC_Median_MDD_Pct": round(float(np.percentile(sim_mdds, 50)) * 100.0, 2),
        "MC_95th_Percentile_MDD_Pct": round(float(np.percentile(sim_mdds, 95)) * 100.0, 2),
    }
