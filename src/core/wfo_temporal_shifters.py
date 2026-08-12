import numpy as np
import pandas as pd
from typing import Iterator, Tuple, Union, Optional

class WalkForwardOptimizer:
    """
    Walk-Forward Optimization (WFO) temporal shifters.
    Generates train and test indices for time-series walk-forward validation.
    
    Supports:
    - Expanding Window (anchor start)
    - Rolling Window (fixed train length)
    - Purging (gap between train and test to prevent leakage)
    - Embargo (gap after test before next train, if needed)
    """

    def __init__(
        self,
        n_splits: int = 5,
        train_size: Optional[int] = None,
        test_size: Optional[int] = None,
        expand_train: bool = True,
        gap: int = 0
    ):
        """
        :param n_splits: Number of walk-forward splits.
        :param train_size: Fixed size of train window (if expand_train is False) or initial train size.
                           If None, calculated automatically based on n_splits and test_size.
        :param test_size: Size of each test window. If None, calculated automatically.
        :param expand_train: If True, uses expanding window. If False, uses rolling window.
        :param gap: Number of samples to purge between train and test sets to prevent data leakage.
        """
        self.n_splits = n_splits
        self.train_size = train_size
        self.test_size = test_size
        self.expand_train = expand_train
        self.gap = gap

    def split(self, X: Union[pd.DataFrame, np.ndarray, list]) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        Yields train and test indices.
        
        :param X: Array-like time series data.
        """
        n_samples = len(X)
        
        if self.n_splits > n_samples:
            raise ValueError(f"Cannot have number of splits n_splits={self.n_splits} greater than the number of samples: {n_samples}.")
            
        test_size = self.test_size
        train_size = self.train_size
        
        if test_size is None and train_size is None:
            # Auto-calculate sizes
            # Let train size be (n_samples // (n_splits + 1))
            # Let test size be the same.
            base_size = n_samples // (self.n_splits + 1)
            train_size = base_size
            test_size = base_size
        elif test_size is None:
            test_size = (n_samples - train_size - self.gap) // self.n_splits
        elif train_size is None:
            train_size = n_samples - (test_size * self.n_splits) - self.gap
            
        if train_size <= 0 or test_size <= 0:
            raise ValueError("Calculated train_size or test_size is <= 0. Adjust n_splits, gap, or data length.")

        for i in range(self.n_splits):
            if self.expand_train:
                # Expanding window
                current_train_start = 0
                current_train_end = train_size + i * test_size
            else:
                # Rolling window
                current_train_start = i * test_size
                current_train_end = current_train_start + train_size
                
            test_start = current_train_end + self.gap
            test_end = test_start + test_size
            
            if test_end > n_samples:
                # Stop if we exceed bounds
                if test_start < n_samples:
                    test_end = n_samples
                else:
                    break
                    
            yield np.arange(current_train_start, current_train_end), np.arange(test_start, test_end)


class PurgedWalkForwardCV:
    """
    Advanced WFO generator that handles time-indexed data directly.
    Allows specifying train/test sizes and gaps as pandas Timedeltas.
    """

    def __init__(
        self,
        train_duration: Union[str, pd.Timedelta],
        test_duration: Union[str, pd.Timedelta],
        gap_duration: Union[str, pd.Timedelta] = "0D",
        expand_train: bool = True
    ):
        self.train_duration = pd.Timedelta(train_duration)
        self.test_duration = pd.Timedelta(test_duration)
        self.gap_duration = pd.Timedelta(gap_duration)
        self.expand_train = expand_train

    def split(self, series: pd.Series) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        """
        :param series: Pandas Series or DataFrame with DatetimeIndex.
        """
        if not isinstance(series.index, pd.DatetimeIndex):
            raise ValueError("Input data must have a DatetimeIndex.")
            
        start_time = series.index.min()
        end_time = series.index.max()
        
        current_train_start = start_time
        current_train_end = current_train_start + self.train_duration
        
        while True:
            test_start = current_train_end + self.gap_duration
            test_end = test_start + self.test_duration
            
            if test_start >= end_time:
                break
                
            train_mask = (series.index >= current_train_start) & (series.index < current_train_end)
            test_mask = (series.index >= test_start) & (series.index < test_end)
            
            train_indices = np.where(train_mask)[0]
            test_indices = np.where(test_mask)[0]
            
            if len(train_indices) > 0 and len(test_indices) > 0:
                yield train_indices, test_indices
                
            if self.expand_train:
                current_train_end += self.test_duration
            else:
                current_train_start += self.test_duration
                current_train_end += self.test_duration


if __name__ == "__main__":
    # Example Usage
    print("Testing WalkForwardOptimizer (Index-based):")
    X = np.arange(100)
    wfo = WalkForwardOptimizer(n_splits=3, train_size=40, test_size=15, gap=5, expand_train=False)
    for i, (train_idx, test_idx) in enumerate(wfo.split(X)):
        print(f"Split {i+1}: Train size={len(train_idx)}, Test size={len(test_idx)}")
        print(f"  Train: [{train_idx[0]} ... {train_idx[-1]}]")
        print(f"  Test:  [{test_idx[0]} ... {test_idx[-1]}]\n")

    print("Testing PurgedWalkForwardCV (Time-based):")
    dates = pd.date_range("2020-01-01", "2020-12-31", freq="D")
    df = pd.DataFrame({"price": np.random.randn(len(dates))}, index=dates)
    
    cv = PurgedWalkForwardCV(train_duration="90D", test_duration="30D", gap_duration="7D", expand_train=True)
    for i, (train_idx, test_idx) in enumerate(cv.split(df)):
        train_dates = df.index[train_idx]
        test_dates = df.index[test_idx]
        print(f"Split {i+1}:")
        print(f"  Train: {train_dates.min().date()} to {train_dates.max().date()}")
        print(f"  Test:  {test_dates.min().date()} to {test_dates.max().date()}\n")
