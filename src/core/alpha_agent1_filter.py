"""
alpha_agent1_filter.py

This script downloads 20-year historical data for SPY and QQQ, calculates daily returns,
and identifies extreme "baskets" representing the top 5% of rallies and bottom 5% of shocks.
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ExtremeMarketFilter:
    def __init__(self, tickers=['SPY', 'QQQ'], years=20, percentile=0.05):
        self.tickers = tickers
        self.years = years
        self.percentile = percentile
        self.data = None
        self.returns = None
        self.baskets = {}

    def fetch_data(self):
        """Fetches historical adjusted close prices."""
        end_date = datetime.today()
        start_date = end_date - timedelta(days=self.years * 365.25)
        
        print(f"Downloading data for {self.tickers} from {start_date.date()} to {end_date.date()}...")
        df = yf.download(self.tickers, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        
        if 'Adj Close' in df.columns:
            self.data = df['Adj Close']
        else:
            self.data = df['Close']
            
        # Ensure it's a DataFrame even if one ticker is passed
        if isinstance(self.data, pd.Series):
            self.data = self.data.to_frame()
            
        return self.data

    def calculate_returns(self):
        """Calculates daily percentage returns."""
        if self.data is None:
            self.fetch_data()
        self.returns = self.data.pct_change().dropna()
        return self.returns

    def filter_extreme_baskets(self):
        """Identifies top % rallies and bottom % shocks."""
        if self.returns is None:
            self.calculate_returns()
            
        for ticker in self.tickers:
            if ticker not in self.returns.columns:
                continue
                
            col_returns = self.returns[ticker]
            
            # Bottom % corresponds to extreme shocks, Top % to extreme rallies
            shock_threshold = col_returns.quantile(self.percentile)
            rally_threshold = col_returns.quantile(1 - self.percentile)
            
            shocks = col_returns[col_returns <= shock_threshold].sort_values()
            rallies = col_returns[col_returns >= rally_threshold].sort_values(ascending=False)
            
            self.baskets[ticker] = {
                'shock_threshold': shock_threshold,
                'rally_threshold': rally_threshold,
                'shocks_data': shocks,
                'rallies_data': rallies,
                'shock_dates': list(shocks.index),
                'rally_dates': list(rallies.index)
            }
            
        return self.baskets

    def get_summary(self):
        """Returns a summary of the identified baskets."""
        summary = {}
        for ticker, data in self.baskets.items():
            summary[ticker] = {
                'Shock Threshold': f"{data['shock_threshold']:.2%}",
                'Rally Threshold': f"{data['rally_threshold']:.2%}",
                'Shock Days Count': len(data['shocks_data']),
                'Rally Days Count': len(data['rallies_data'])
            }
        return pd.DataFrame(summary).T

if __name__ == "__main__":
    # Execute the filtering logic
    market_filter = ExtremeMarketFilter(tickers=['SPY', 'QQQ'], years=20, percentile=0.05)
    
    # Run the pipeline
    market_filter.fetch_data()
    market_filter.calculate_returns()
    baskets = market_filter.filter_extreme_baskets()
    
    # Output results
    print("\n--- Extreme Market Baskets Summary ---")
    summary_df = market_filter.get_summary()
    print(summary_df)
    
    # Save the extreme dates to CSV for further downstream usage
    output_dir = os.path.dirname(os.path.abspath(__file__))
    for ticker in market_filter.tickers:
        if ticker in baskets:
            # Create a combined DataFrame for shocks and rallies
            shocks_df = baskets[ticker]['shocks_data'].to_frame('Return')
            shocks_df['Type'] = 'Shock'
            
            rallies_df = baskets[ticker]['rallies_data'].to_frame('Return')
            rallies_df['Type'] = 'Rally'
            
            combined = pd.concat([shocks_df, rallies_df]).sort_index()
            combined.index.name = 'Date'
            
            filename = os.path.join(output_dir, f"{ticker}_extreme_events.csv")
            combined.to_csv(filename)
            print(f"Saved extreme events for {ticker} to {filename}")
