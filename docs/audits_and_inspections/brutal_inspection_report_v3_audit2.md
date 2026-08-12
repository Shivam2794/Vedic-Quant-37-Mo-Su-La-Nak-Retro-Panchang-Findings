# Brutal Inspection Report

**Grade:** FAILED

**Critical Flaws (Must Fix):**
1. **The Weekend Dilution Effect (Calendar vs Trading Day Misalignment):** Merging BTC (365 days/year) with SPY/TLT/GLD (252 days/year) and using `.ffill()` causes TradFi assets to print `0%` returns on weekends. This artificially dilutes the rolling 20-day standard deviation by injecting ~104 zero-return days annually. Because your calculated volatility (`cv`) is mathematically deflated, your `target_vol / cv` multipliers are dangerously inflated. You are applying stealth leverage to the portfolio and violating your 8% ensemble target limit. 
2. **Vol-Targeter Memory Loss (Un-hedged Tail Risk):** In `get_vol_target_weights`, you pass the strategy returns (`tlt_weights * returns['TLT']`). When the SMA trend is negative, the weight is `0`, causing the 20-day rolling vol to collapse to `0.0`. Your script explicitly ignores days where `cv == 0` (`if pd.isna(cv) or cv == 0: continue`), causing the vol-multiplier to remain at its default value of `1.0`. When the asset eventually triggers a buy signal, you re-enter the market at maximum unadjusted weight, completely blind to the asset's actual underlying volatility. You must measure volatility on the *raw asset returns*, not the strategy returns.
3. **Static Margin Abuse (Sharpe Hacking):** You calculate `daily_cash_yield = (df['^IRX'] / 100) / 252`. Because your DataFrame spans ~365 days a year (due to BTC), you are awarding the portfolio $1/252$ of the annual risk-free rate 365 times a year. You are artificially harvesting ~1.44x the actual risk-free rate, fraudulently padding the gross return.

**Structural Weaknesses:**
1. **CAGR Compression Math:** Your CAGR math uses the exponent `(252 / len(final_port_ret))`. Because `len` is measured in calendar days (e.g., ~3650 days for 10 years), the math assumes the backtest ran for 14.5 years instead of 10. Both your strategy CAGR and benchmark CAGR are mathematically compressed and wildly inaccurate.
2. **Dead Slippage Block:** Lines 127-132 calculate `total_slippage` based on unlevered `master_weights`. This entire variable is abandoned and never used (though you do correctly recalculate slippage inside the ensemble loop). 

**Micro-Optimizations:**
1. **Sharpe Ratio Denominator:** You are calculating Sharpe using `excess_ret.mean() / final_port_ret.std()`. The strict mathematical standard requires dividing by the standard deviation of the *excess returns*, i.e., `excess_ret.std()`.
2. **Vectorization Deficit:** You calculate the final portfolio return using a sluggish `for i, date in enumerate(valid_idx):` loop. This can be fully vectorized using `.shift()` on the weights and `np.where()` for the cash/margin rates.

**Final Verdict:**
The strategy properly mitigates lookahead bias (via rigorous `.shift(1)` logic) and avoids massive parameter overfitting (relying on standard 50/200 SMAs and Connors RSI). Furthermore, the Sharpe math does correctly subtract the risk-free rate in the numerator. However, the structural collision between crypto (365 days) and TradFi (252 days) completely compromises your volatility scaling and yield engine. Fix the temporal alignment and Vol-Targeter memory loss immediately.
