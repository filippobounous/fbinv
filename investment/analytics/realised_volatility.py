import numpy as np
import pandas as pd
from typing import List, Union, Dict, Callable

from ..utils.consts import DEFAULT_RV_WIN_SIZE, DEFAULT_RV_MODEL, TRADING_DAYS

class RealisedVolatilityCalculator:
    def __init__(
            self,
            rv_win_size: Union[int, List[int]] = DEFAULT_RV_WIN_SIZE,
            rv_model: Union[str, List[str]] = DEFAULT_RV_MODEL,
            dt: int = TRADING_DAYS,
        ) -> None:
        self.dt = dt
        
        if isinstance(rv_win_size, int):
            self.rv_win_size = [rv_win_size]
        else:
            self.rv_win_size = rv_win_size

        if isinstance(rv_model, str):
            self.rv_model = [rv_model]
        else:
            self.rv_model = rv_model

    @property
    def registry(self) -> Dict[str, Callable[[pd.DataFrame, int], pd.Series]]:
        return {
            "close_to_close": self._close_to_close,
            "parkinson":  self._parkinson,
            "garman_klass": self._garman_klass,
            "rogers_satchell": self._rogers_satchell,
            "yang_zhang": self._yang_zhang,
            "gk_yang_zhang": self._gk_yang_zhang,
        }

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_index()

        df_list = []
        for model in self.rv_model:
            method = self.registry.get(model)
            
            if not method:
                continue

            for win_size in self.rv_win_size:
                vols = method(df=df, rv_win_size=win_size)
                temp_df = pd.DataFrame({
                    "as_of_date": df.index,
                    "volatility_type": 'realised',
                    "rv_model": model,
                    "rv_win_size": win_size,
                    "volatility": vols,
                })
                df_list.append(temp_df)

        return pd.concat(df_list).dropna().reset_index(drop=True)

    def _close_to_close(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        log_ret: pd.Series = np.log(df['close']).diff()
        return log_ret.rolling(rv_win_size).std() * np.sqrt(self.dt)

    def _parkinson(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        rs: pd.Series = (1.0 / (4.0 * np.log(2))) * (np.log(df['high'] / df['low']) ** 2)
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _garman_klass(
        self,
        df: pd.DataFrame,
        rv_win_size: int,
        _return_initial_term: bool = False,
    ) -> pd.Series:
        term1 = 0.5 * (np.log(df['high'] / df['low']) ** 2)
        term2 = (2 * np.log(2) - 1) * (np.log(df['close'] / df['open']) ** 2)
        rs: pd.Series = term1 - term2
        if _return_initial_term:
            return rs
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _rogers_satchell(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        ho = np.log(df['high'] / df['open'])
        lo = np.log(df['low'] / df['open'])
        co = np.log(df['close'] / df['open'])
        rs: pd.Series = ho * (ho - co) + lo * (lo - co)
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)
    
    def _gk_yang_zhang(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        gk = self._garman_klass(df=df, rv_win_size=rv_win_size, _return_initial_term=True)
        yz = np.log(df['open'] / df['close'].shift(1)) ** 2
        rs: pd.Series = yz + gk
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _yang_zhang(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        log_open = np.log(df['open'])
        log_close: pd.Series = np.log(df['close'])

        log_oc: pd.Series = log_open - log_close.shift(1)
        log_co: pd.Series = log_close - log_open

        var_on = log_oc.rolling(rv_win_size).var()
        var_day = log_co.rolling(rv_win_size).var()
        rs2 = self._rogers_satchell(df, rv_win_size) ** 2  # already annualised, hence squared here

        k = 0.34 / (1.34 + (rv_win_size + 1) / (rv_win_size - 1))
        return np.sqrt(var_on + k * var_day + (1 - k) * rs2)
