import numpy as np
import pandas as pd
from typing import Union, Tuple
from scipy import stats

class ZeroBetaHedger:
    """
    Implements Zero-Beta (Market Neutral) correlation and hedging logic.
    Calculates beta against a benchmark and derives appropriate hedge ratios 
    to neutralize market risk.
    """
    
    def __init__(self, lookback: int = 60, use_kalman: bool = False):
        """
        :param lookback: Number of periods for rolling beta calculation.
        :param use_kalman: Use Kalman filter for dynamic beta estimation (placeholder for advanced logic).
        """
        self.lookback = lookback
        self.use_kalman = use_kalman
        
    def calculate_static_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculates the static beta of an asset relative to the market using OLS.
        """
        aligned = pd.concat([asset_returns, market_returns], axis=1).dropna()
        if len(aligned) < 2:
            return 0.0
            
        cov_matrix = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])
        market_var = cov_matrix[1, 1]
        
        if market_var == 0:
            return 0.0
            
        beta = cov_matrix[0, 1] / market_var
        return float(beta)
        
    def calculate_rolling_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> pd.Series:
        """
        Calculates the rolling beta of an asset relative to the market.
        """
        aligned = pd.concat([asset_returns, market_returns], axis=1).dropna()
        if len(aligned) < self.lookback:
            return pd.Series(np.nan, index=aligned.index)
            
        # Rolling covariance and variance
        roll_cov = aligned.iloc[:, 0].rolling(window=self.lookback).cov(aligned.iloc[:, 1])
        roll_var = aligned.iloc[:, 1].rolling(window=self.lookback).var()
        
        rolling_beta = roll_cov / roll_var
        return rolling_beta
        
    def get_hedge_ratio(self, beta: Union[float, pd.Series]) -> Union[float, pd.Series]:
        """
        Returns the hedge ratio required for a Zero-Beta portfolio.
        If beta is 1.5, we need to short 1.5 units of the market for every 1 unit of the asset.
        
        Zero-Beta constraint: W_asset * Beta_asset + W_market * Beta_market = 0
        Assuming Beta_market = 1.0, W_market = -W_asset * Beta_asset
        Here we return the ratio W_market / W_asset = -Beta_asset
        """
        return -beta
        
    def construct_zero_beta_portfolio(self, 
                                      asset_prices: pd.Series, 
                                      market_prices: pd.Series, 
                                      capital: float = 100000.0) -> pd.DataFrame:
        """
        Constructs a rolling zero-beta portfolio tracking the capital allocation.
        """
        asset_ret = asset_prices.pct_change()
        market_ret = market_prices.pct_change()
        
        rolling_beta = self.calculate_rolling_beta(asset_ret, market_ret)
        hedge_ratio = self.get_hedge_ratio(rolling_beta)
        
        # Shift hedge ratio by 1 to prevent look-ahead bias (we trade at the close based on today's beta)
        target_hedge = hedge_ratio.shift(1)
        
        # Assuming we allocate `capital` fully to the long leg and short the market equivalent to hedge ratio
        # Leverage is used for the short leg.
        long_exposure = capital
        short_exposure = capital * target_hedge
        
        portfolio_ret = (asset_ret * long_exposure + market_ret * short_exposure) / capital
        
        df = pd.DataFrame({
            'Asset_Return': asset_ret,
            'Market_Return': market_ret,
            'Rolling_Beta': rolling_beta,
            'Hedge_Ratio': target_hedge,
            'Portfolio_Return': portfolio_ret,
            'Cumulative_Return': (1 + portfolio_ret.fillna(0)).cumprod() - 1
        })
        
        return df.dropna()

if __name__ == "__main__":
    # Example Usage
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=252, freq="B")
    
    # Simulate market returns
    mkt_ret = np.random.normal(0.0005, 0.01, size=252)
    mkt_price = 100 * (1 + pd.Series(mkt_ret, index=dates)).cumprod()
    
    # Simulate asset returns with beta=1.2 and some alpha + noise
    alpha = 0.0002
    beta_true = 1.2
    asset_ret = alpha + beta_true * mkt_ret + np.random.normal(0, 0.005, size=252)
    asset_price = 50 * (1 + pd.Series(asset_ret, index=dates)).cumprod()
    
    hedger = ZeroBetaHedger(lookback=30)
    
    print("Static Beta:", hedger.calculate_static_beta(pd.Series(asset_ret, index=dates), pd.Series(mkt_ret, index=dates)))
    
    df_portfolio = hedger.construct_zero_beta_portfolio(asset_price, mkt_price)
    print("\nZero-Beta Portfolio Sample:")
    print(df_portfolio.tail())
