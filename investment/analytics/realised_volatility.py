"""Realised Volatility Calculator for timeseries"""

from typing import List, Union, Dict, Callable

import numpy as np
import pandas as pd

from .base import _BaseAnalytics
from ..utils.consts import DEFAULT_RV_WIN_SIZE, DEFAULT_RV_MODEL, TRADING_DAYS, HL, OHLC

class RealisedVolatilityCalculator(_BaseAnalytics):
    """
    Realised Volatility Calculator
    
    Calculator for realised volatility with various methods. Initialised with:
    rv_win_size (List[int]) -> the realised volatility windows
    rv_model (Lis[str]) -> the realised volatility models to calculate for
    dt [int] -> The normalisation constant to use
    """
    def __init__(
            self,
            rv_win_size: Union[int, List[int]] = DEFAULT_RV_WIN_SIZE,
            rv_model: Union[str, List[str]] = DEFAULT_RV_MODEL,
            dt: int = TRADING_DAYS,
        ) -> None:
        """Store parameters and normalisation constant."""
        self.dt = dt

        if isinstance(rv_win_size, int):
            self.rv_win_size = [rv_win_size]
        else:
            self.rv_win_size = rv_win_size

        if isinstance(rv_model, str):
            self.rv_model = [rv_model]
        else:
            self.rv_model = rv_model

    @staticmethod
    def registry() -> Dict[
        str,
        Dict[str, Union[Callable[[pd.DataFrame, int], pd.Series], List[str]]]
    ]:
        """Registry of realised volatility methods and their required columns"""
        return {
            "close_to_close": {
                "method": RealisedVolatilityCalculator._close_to_close,
                "required": ["close"],
            },
            "parkinson": {
                "method": RealisedVolatilityCalculator._parkinson,
                "required": HL,
            },
            "garman_klass": {
                "method": RealisedVolatilityCalculator._garman_klass,
                "required": OHLC,
            },
            "rogers_satchell": {
                "method": RealisedVolatilityCalculator._rogers_satchell,
                "required": OHLC,
            },
            "yang_zhang": {
                "method": RealisedVolatilityCalculator._yang_zhang,
                "required": OHLC,
            },
            "gk_yang_zhang": {
                "method": RealisedVolatilityCalculator._gk_yang_zhang,
                "required": OHLC,
            },
        }

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates the realised volatility for a given pd.DataFrame."""
        df = df.sort_index()

        df_list = []
        for model in self.rv_model:
            model_dict = self.registry().get(model)

            if not model_dict:
                continue

            method = model_dict.get("method")
            required_columns = model_dict.get("required")

            if not all(c in df.columns for c in required_columns):
                continue

            for win_size in self.rv_win_size:
                vols = method(self, df=df, rv_win_size=win_size)
                temp_df = pd.DataFrame({
                    "as_of_date": df.index,
                    "volatility_type": 'realised',
                    "rv_model": model,
                    "rv_win_size": win_size,
                    "volatility": vols,
                })
                df_list.append(temp_df)

        return pd.concat(df_list).dropna().reset_index(drop=True).set_index()

    def _close_to_close(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        """Close-to-close volatility estimator."""
        log_ret: pd.Series = np.log(df['close']).diff()
        return log_ret.rolling(rv_win_size).std() * np.sqrt(self.dt)

    def _parkinson(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        """Parkinson volatility estimator."""
        rs: pd.Series = (1.0 / (4.0 * np.log(2))) * (np.log(df['high'] / df['low']) ** 2)
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _garman_klass(
        self,
        df: pd.DataFrame,
        rv_win_size: int,
        _return_initial_term: bool = False,
    ) -> pd.Series:
        """Garman–Klass volatility estimator."""
        term1 = 0.5 * (np.log(df['high'] / df['low']) ** 2)
        term2 = (2 * np.log(2) - 1) * (np.log(df['close'] / df['open']) ** 2)
        rs: pd.Series = term1 - term2
        if _return_initial_term:
            return rs
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _rogers_satchell(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        """Rogers–Satchell volatility estimator."""
        ho = np.log(df['high'] / df['open'])
        lo = np.log(df['low'] / df['open'])
        co = np.log(df['close'] / df['open'])
        rs: pd.Series = ho * (ho - co) + lo * (lo - co)
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _gk_yang_zhang(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        """Combination of Garman–Klass and Yang–Zhang estimators."""
        gk = self._garman_klass(df=df, rv_win_size=rv_win_size, _return_initial_term=True)
        yz = np.log(df['open'] / df['close'].shift(1)) ** 2
        rs: pd.Series = yz + gk
        return np.sqrt(rs.rolling(rv_win_size).mean()) * np.sqrt(self.dt)

    def _yang_zhang(self, df: pd.DataFrame, rv_win_size: int) -> pd.Series:
        """Yang–Zhang volatility estimator."""
        log_open = np.log(df['open'])
        log_close: pd.Series = np.log(df['close'])

        log_oc: pd.Series = log_open - log_close.shift(1)
        log_co: pd.Series = log_close - log_open

        var_on = log_oc.rolling(rv_win_size).var()
        var_day = log_co.rolling(rv_win_size).var()
        rs2 = self._rogers_satchell(df, rv_win_size) ** 2  # already annualised, hence squared here

        k = 0.34 / (1.34 + (rv_win_size + 1) / (rv_win_size - 1))
        return np.sqrt(var_on + k * var_day + (1 - k) * rs2)
