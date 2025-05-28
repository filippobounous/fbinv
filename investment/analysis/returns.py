import pandas as pd
import numpy as np
from typing import List, Union

class ReturnsCalculator:
    def __init__(self, ln_ret: bool = True, ret: bool = False, n_days: Union[List[int], int] = [1, 20, 60, 120, 252]):
        self.ln_ret = ln_ret
        self.ret = ret

        if isinstance(n_days, int):
            n_days = [n_days]
        self.n_days = n_days

    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log and/or simple returns based on the 'close' column for multiple periods.

        Parameters:
            df (pd.DataFrame): Input DataFrame with a 'close' column.

        Returns:
            pd.DataFrame: DataFrame with added columns for each return series.
        """
        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain a 'close' column.")

        result_df = df.copy()

        for n in self.n_days:
            if self.ret:
                result_df[f'{n}d_ret'] = result_df['close'].pct_change(n)
            if self.ln_ret:
                result_df[f'{n}d_ln_ret'] = np.log(result_df['close'] / result_df['close'].shift(n))

        return result_df