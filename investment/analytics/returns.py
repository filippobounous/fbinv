import pandas as pd
import numpy as np
from typing import Union, List

class ReturnsCalculator:
    def __init__(self, use_ln_ret: bool = True, ret_win_size: Union[int, List[int]] = [1, 20, 60, 120, 252]):
        self.use_ln_ret = use_ln_ret

        if isinstance(ret_win_size, int):
            self.ret_win_size = [ret_win_size]
        else:
            self.ret_win_size = ret_win_size

    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log and/or simple returns from the 'close' column for specified periods.
        """
        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if 'close' not in df.columns:
            raise ValueError("DataFrame must contain a 'close' column.")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame index must be a DatetimeIndex.")

        df_list = []
        for n in self.ret_win_size:
            if self.use_ln_ret:
                rets = np.log(df['close'] / df['close'].shift(n))
            else:
                rets = df['close'].pct_change(n)
            
            temp_df = pd.DataFrame({
                'value': rets,
                'is_ln_ret': self.use_ln_ret,
                'as_of_date': df.index,
                'ret_win_size': n
            })
            df_list.append(temp_df)

        return pd.concat(df_list).dropna().reset_index(drop=True)
