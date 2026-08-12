import pandas as pd
import pyarrow as pa

class Chapter1Pipeline:
    """
    Chapter 1 Pipeline: 
    Handles Arrow ingestion, ASOF joins, and Multi-horizon bucketing (1H & 1D Short Swing).
    """
    
    @staticmethod
    def fetch_sip_market_data(tickers: list = None, start_date: str = "2000-01-01", end_date: str = None) -> dict:
        """
        SIP Market Data Hook for Chapter 1.
        Fetches historical market data for given tickers (default SPY and QQQ) using yfinance.
        Formats the data to be compatible with Chapter 1's ASOF joins and bucketing hooks.
        """
        import yfinance as yf
        import datetime
        
        if tickers is None:
            tickers = ['SPY', 'QQQ']
            
        if end_date is None:
            end_date = datetime.datetime.today().strftime('%Y-%m-%d')
            
        data_dict = {}
        for ticker in tickers:
            print(f"Fetching SIP market data for {ticker}...")
            df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, progress=False)
            
            if df.empty:
                continue
                
            df = df.reset_index()
            
            # Flatten multiindex columns if yfinance returns them
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]
                
            # Rename 'Date' or 'Datetime' to 'timestamp'
            date_col = 'Date' if 'Date' in df.columns else 'Datetime'
            if date_col in df.columns:
                df = df.rename(columns={date_col: 'timestamp'})
                
            # Convert remaining columns to lowercase for consistency with bucketing
            df = df.rename(columns={c: c.lower() for c in df.columns if c != 'timestamp'})
            
            # Drop timezone info if present to ensure ASOF join compatibility
            if pd.api.types.is_datetime64_tz_dtype(df['timestamp']):
                df['timestamp'] = df['timestamp'].dt.tz_localize(None)
                
            data_dict[ticker] = df
            
        return data_dict

    @staticmethod
    def arrow_ingestion(df: pd.DataFrame) -> pa.Table:
        """Converts a pandas DataFrame to an Apache Arrow Table for efficient zero-copy ingestion."""
        return pa.Table.from_pandas(df)

    @staticmethod
    def arrow_to_df(table: pa.Table) -> pd.DataFrame:
        """Converts an Apache Arrow Table back to a pandas DataFrame."""
        return table.to_pandas()

    @staticmethod
    def asof_join(market_df: pd.DataFrame, ephem_df: pd.DataFrame, on_col: str = 'timestamp') -> pd.DataFrame:
        """
        Performs an asof join, aligning ephemeris data (backward direction) to market data
        to prevent future data leakage.
        """
        market_df = market_df.sort_values(on_col)
        ephem_df = ephem_df.sort_values(on_col)
        
        joined_df = pd.merge_asof(
            market_df,
            ephem_df,
            on=on_col,
            direction='backward'
        )
        return joined_df

    @staticmethod
    def apply_short_swing_bucketing(df: pd.DataFrame, time_col: str = 'timestamp') -> dict:
        """
        Implements 1H and 1D Short Swing bucketing, dropping zero-volume or missing periods (e.g., weekends).
        Returns a dictionary containing the resampled dataframes.
        """
        df = df.set_index(time_col)
        
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        # Only aggregate columns that actually exist in the dataframe
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
        
        resampled_1h = df.resample('1h').agg(agg_dict)
        resampled_1d = df.resample('1D').agg(agg_dict)
        
        # Clean up data (drop zero volume/weekend closures)
        if 'volume' in resampled_1h.columns:
            resampled_1h = resampled_1h[resampled_1h['volume'] > 0]
            resampled_1d = resampled_1d[resampled_1d['volume'] > 0]
        else:
            resampled_1h = resampled_1h.dropna()
            resampled_1d = resampled_1d.dropna()
            
        return {
            '1H': resampled_1h.reset_index(),
            '1D': resampled_1d.reset_index()
        }
