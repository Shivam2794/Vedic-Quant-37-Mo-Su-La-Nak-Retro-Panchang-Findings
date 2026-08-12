import pandas as pd
import numpy as np
from typing import Union

class MarketShockFilter:
    """
    Filter rules for predicting market shocks with a minimum 90% confidence threshold.
    """
    def __init__(self, confidence_threshold: float = 0.90):
        self.confidence_threshold = confidence_threshold

    def filter_predictions(self, df: pd.DataFrame, probability_col: str = 'shock_probability') -> pd.DataFrame:
        """
        Filters a DataFrame of predictions to return only those with a shock probability
        greater than or equal to the confidence threshold.
        
        Args:
            df (pd.DataFrame): DataFrame containing predictions.
            probability_col (str): The name of the column containing the shock probabilities.
            
        Returns:
            pd.DataFrame: A filtered DataFrame.
        """
        if probability_col not in df.columns:
            raise ValueError(f"Column '{probability_col}' not found in the DataFrame.")
            
        return df[df[probability_col] >= self.confidence_threshold].copy()

    def apply_complex_rules(self, df: pd.DataFrame, 
                            probability_col: str = 'shock_probability',
                            volatility_col: str = 'volatility_index',
                            volatility_threshold: float = 20.0,
                            return_col: str = 'predicted_return',
                            return_threshold: float = -0.05) -> pd.DataFrame:
        """
        Applies a more complex set of rules to identify high-confidence market shocks.
        Requires the model's confidence to be >= 90%, and optionally applies 
        filters on volatility or predicted return magnitude.
        
        Args:
            df (pd.DataFrame): DataFrame containing market data and predictions.
            probability_col (str): Column with the shock probability.
            volatility_col (str): Column with the volatility index (e.g., VIX).
            volatility_threshold (float): Minimum volatility required to validate the shock.
            return_col (str): Column with predicted return.
            return_threshold (float): Maximum predicted return to qualify as a shock (should be negative).
            
        Returns:
            pd.DataFrame: Filtered DataFrame meeting all shock criteria.
        """
        high_conf_df = self.filter_predictions(df, probability_col)
        
        if volatility_col in high_conf_df.columns:
            high_conf_df = high_conf_df[high_conf_df[volatility_col] >= volatility_threshold]
            
        if return_col in high_conf_df.columns:
            high_conf_df = high_conf_df[high_conf_df[return_col] <= return_threshold]
            
        return high_conf_df

def main():
    print("Initializing Market Shock Filter with 90% confidence threshold...")
    shock_filter = MarketShockFilter(confidence_threshold=0.90)
    
    # Mock data to demonstrate filtering logic
    data = {
        'date': pd.date_range(start='2026-06-01', periods=5),
        'shock_probability': [0.15, 0.85, 0.92, 0.99, 0.45],
        'volatility_index': [15.2, 18.5, 22.1, 25.4, 19.0],
        'predicted_return': [-0.01, -0.04, -0.12, -0.15, -0.02]
    }
    df = pd.DataFrame(data)
    
    print("\nOriginal Data:")
    print(df)
    
    filtered_df = shock_filter.filter_predictions(df)
    print(f"\nFiltered for >= {shock_filter.confidence_threshold * 100}% Confidence:")
    print(filtered_df)
    
    complex_filtered_df = shock_filter.apply_complex_rules(df)
    print("\nFiltered with Complex Rules (>=90% Confidence, Volatility >= 20.0, Return <= -5%):")
    print(complex_filtered_df)

if __name__ == "__main__":
    main()
