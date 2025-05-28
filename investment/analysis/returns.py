import pandas as pd
import numpy as np
from typing import Union, List

class ReturnsCalculator:
    def __init__(self, ln_ret: bool = True, ret: bool = False, ret_win_size: List[int] = [1, 20, 60, 120, 252]):
        self.ln_ret = ln_ret
        self.ret = ret
        self.ret_win_size = ret_win_size

    @staticmethod
    def format_col_name(ln_ret: bool, ret: bool, ret_win_size: Union[int, List[int]]) -> List[str]:
        """
        Generate column names for returns based on the return type flags and window size(s).
        """
        if isinstance(ret_win_size, int):
            ret_win_size = [ret_win_size]

        col_names = []

        for n in ret_win_size:
            if ret:
                col_names.append(f'{n}d_ret')
            if ln_ret:
                col_names.append(f'{n}d_ln_ret')

        return col_names

    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log and/or simple returns from the 'close' column for specified periods.
        """
        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain a 'close' column.")

        result_df = df.copy()

        for n in self.ret_win_size:
            cols = self.format_col_name(ln_ret=self.ln_ret, ret=self.ret, ret_win_size=n)
            for col in cols:
                if col.endswith("d_ret") and col not in result_df.columns:
                    result_df[col] = result_df['close'].pct_change(n)
                elif col.endswith("d_ln_ret") and col not in result_df.columns:
                    result_df[col] = np.log(result_df['close'] / result_df['close'].shift(n))

        return result_df
