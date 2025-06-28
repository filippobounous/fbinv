"""Returns Calculator for timeseries"""

from typing import Union, List, Callable, Any, Dict

import pandas as pd
import numpy as np

from .base import _BaseAnalytics
from ..utils.consts import DEFAULT_RET_WIN_SIZE

class ReturnsCalculator(_BaseAnalytics):
    """
    Returns Calculator
    
    Calculator for returns for various window sizes. Initialised with:
    use_ln_ret (bool) -> If to use ln(a/b) or just a/b
    ret_win_size (List[int]) -> the returns windows
    """

    @staticmethod
    def registry() -> Dict[str, Callable[[Any], Any]]:
        """Return mapping of available return calculations."""
        return {"returns": ReturnsCalculator.calculate}
    def __init__(
            self,
            use_ln_ret: bool = True,
            ret_win_size: Union[int, List[int]] = DEFAULT_RET_WIN_SIZE
        ) -> None:
        """Initialise the calculator."""
        self.use_ln_ret = use_ln_ret

        if isinstance(ret_win_size, int):
            self.ret_win_size = [ret_win_size]
        else:
            self.ret_win_size = ret_win_size

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log or simple returns from the 'close' column for specified periods.
        """
        if df.empty:
            raise ValueError("Input DataFrame is empty.")

        df = df.sort_index()

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
                'as_of_date': df.index,
                'is_ln_ret': self.use_ln_ret,
                'ret_win_size': n,
                'return': rets,
            })
            df_list.append(temp_df)

        return pd.concat(df_list).dropna().reset_index(drop=True)
