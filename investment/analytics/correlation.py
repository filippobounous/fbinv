"""Correlation calculator for securities and portfolios.

The :class:`CorrelationCalculator` assembles price or return series from
`BaseSecurity` and `Portfolio` objects and computes pairwise correlation
statistics.  It supports the standard Pearson, Spearman and Kendall
models, optional rolling windows, time lags and more specialised
measures such as partial and semi correlations.
"""

from typing import TYPE_CHECKING, Callable, Any

import numpy as np
import pandas as pd

from .base import BaseAnalytics
from ..utils.consts import DEFAULT_RET_WIN_SIZE, DEFAULT_CORR_MODEL

if TYPE_CHECKING:
    from ..core.portfolio import Portfolio
    from ..core.security.base import BaseSecurity

class CorrelationCalculator(BaseAnalytics):
    """Calculator for correlations between securities and portfolios.

    The calculator fetches historical price or return data from the
    supplied entities and aligns them into a single ``DataFrame``.  A
    variety of correlation measures can then be derived, including
    standard, rolling and lagged correlations as well as more technical
    partial and semi correlations.
    """

    @staticmethod
    def registry() -> dict[str, Callable[..., Any]]:
        """Mapping of correlation helper names to methods."""
        return {
            "calculate": CorrelationCalculator.calculate,
            "lagged": CorrelationCalculator.lagged,
            "partial": CorrelationCalculator.partial,
            "semi": CorrelationCalculator.semi,
            "mean_correlation": CorrelationCalculator.mean_correlation,
            "rolling_mean_correlation": CorrelationCalculator.rolling_mean_correlation,
        }

    def __init__(
        self,
        securities: list["BaseSecurity"] | None = None,
        portfolios: list["Portfolio"] | None = None,
    ) -> None:
        """Initialise the calculator with optional entities.

        Parameters
        ----------
        securities:
            A list of :class:`BaseSecurity` instances to analyse.
        portfolios:
            A list of :class:`Portfolio` instances to analyse.
        """
        self.securities: list["BaseSecurity"] = securities or []
        self.portfolios: list["Portfolio"] = portfolios or []

    def _gather_series(
        self,
        use_returns: bool,
        log_returns: bool,
        ret_win_size: int,
    ) -> pd.DataFrame:
        """Collect aligned price or return series for the stored entities.

        Parameters
        ----------
        use_returns:
            If ``True`` return percentage or logarithmic returns instead of
            prices.
        log_returns:
            When ``use_returns`` is ``True`` select log returns (``ln``) or
            simple percentage returns.
        ret_win_size:
            Window size used to compute returns when ``use_returns`` is
            enabled.

        Returns
        -------
        pandas.DataFrame
            A wide DataFrame indexed by date with one column per security or
            portfolio currency.  NaNs are dropped so all series are aligned.
        """

        series_list: list[pd.Series] = []

        all_objects = self.securities + self.portfolios
        for obj in all_objects:
            if use_returns:
                df = obj.get_returns(
                    use_ln_ret=log_returns, ret_win_size=ret_win_size
                )
                s = df.set_index("as_of_date")["return"].rename(obj.code)
            else:
                df = obj.get_price_history()
                s = df["close"].rename(obj.code)
            series_list.append(s)
            df_all = pd.concat(series_list, axis=1)

        return df_all.dropna(how="any").sort_index()

    def _pairwise_correlation(
        self,
        df: pd.DataFrame,
        corr_model: str,
        window: int | None,
        lag: int,
    ) -> pd.DataFrame | dict[tuple[str, str], pd.Series]:
        """Compute pairwise correlations for a ``DataFrame``.

        Parameters
        ----------
        df:
            DataFrame containing aligned series.
        corr_model:
            Correlation method. Supported values are ``pearson``, ``spearman``
            and ``kendall``.
        window:
            Size of the rolling window. ``None`` returns a full-sample matrix.
            Rolling computations rely on ``pandas.Series.rolling().corr``.
        lag:
            Number of periods to shift the second series in each pair for
            cross-correlation analysis.

        Returns
        -------
        pandas.DataFrame or Dict[Tuple[str, str], pandas.Series]
            If ``window`` is ``None``, a square correlation matrix is returned.
            Otherwise a dictionary keyed by the pair of column names with
            rolling correlation series.
        """

        if window is None and lag == 0:
            return df.corr(method=corr_model)

        columns = list(df.columns)
        if window is None:
            result = pd.DataFrame(index=columns, columns=columns, dtype=float)
        else:
            result = {}

        for i, col1 in enumerate(columns):
            for col2 in columns[i + 1 :]:
                s1 = df[col1]
                s2 = df[col2].shift(lag)

                if window is None:
                    corr_val = s1.corr(s2, method=corr_model)
                    result.loc[col1, col2] = corr_val
                    result.loc[col2, col1] = corr_val
                else:
                    corr_series = s1.rolling(window).corr(s2)
                    result[(col1, col2)] = corr_series.dropna()

        if window is None:
            np.fill_diagonal(result.values, 1.0)
            return result
        return result

    def calculate(
        self,
        use_returns: bool = False,
        log_returns: bool = True,
        ret_win_size: int = DEFAULT_RET_WIN_SIZE,
        corr_model: str = DEFAULT_CORR_MODEL,
        window: int | None = None,
        lag: int = 0,
    ) -> pd.DataFrame | dict[tuple[str, str], pd.Series]:
        """Calculate correlations for the stored securities and portfolios.

        Parameters
        ----------
        use_returns:
            If ``True`` correlations are computed on return series rather than
            raw prices.
        log_returns:
            Whether returns should be logarithmic. Ignored when
            ``use_returns`` is ``False``.
        ret_win_size:
            Window used for return calculations.
        corr_model:
            Correlation method (``pearson``, ``spearman`` or ``kendall``).
        window:
            Rolling window for time-varying correlations. ``None`` returns a
            static matrix.
        lag:
            Amount of lag applied to the second series in each pair.  Non-zero
            values allow basic lead/lag analysis.

        Returns
        -------
        pandas.DataFrame or Dict[Tuple[str, str], pandas.Series]
            Full correlation matrix or dictionary of rolling correlation
            series depending on ``window``.
        """

        df = self._gather_series(
            use_returns=use_returns,
            log_returns=log_returns,
            ret_win_size=ret_win_size,
        )

        return self._pairwise_correlation(
            df,
            corr_model=corr_model,
            window=window,
            lag=lag,
        )

    def mean_correlation(self, corr_matrix: pd.DataFrame) -> float:
        """Return the mean off-diagonal correlation from a matrix.

        Parameters
        ----------
        corr_matrix:
            Square matrix of correlation coefficients.

        Returns
        -------
        float
            Mean of all correlations excluding the diagonal so that only
            pairwise relationships contribute.
        """
        tri = corr_matrix.where(~np.eye(len(corr_matrix), dtype=bool)).stack()
        return float(tri.mean())

    def rolling_mean_correlation(
        self, corr_dict: dict[tuple[str, str], pd.Series]
    ) -> pd.Series:
        """Return the average rolling correlation across all pairs.

        Parameters
        ----------
        corr_dict:
            Dictionary mapping column name tuples to rolling correlation series.

        Returns
        -------
        pandas.Series
            Series containing the mean correlation at each point in time,
            computed across all pairwise rolling correlations.
        """
        combined = pd.concat(corr_dict.values(), axis=1)
        return combined.mean(axis=1)

    def lagged(
        self,
        lags: list[int],
        **kwargs,
    ) -> dict[int, pd.DataFrame | dict[tuple[str, str], pd.Series]]:
        """Compute correlations for multiple lags.

        Parameters
        ----------
        lags:
            List of lag values to evaluate.
        **kwargs:
            Additional keyword arguments forwarded to :meth:`calculate`.

        Returns
        -------
        Dict[int, Union[pd.DataFrame, Dict[Tuple[str, str], pandas.Series]]]
            Mapping of each lag value to the correlation matrix (or rolling
            correlations) computed with that lag applied.
        """
        results = {}
        for l in lags:
            results[l] = self.calculate(lag=l, **kwargs)
        return results

    def partial(
        self,
        use_returns: bool = False,
        log_returns: bool = True,
        ret_win_size: int = DEFAULT_RET_WIN_SIZE,
        corr_model: str = DEFAULT_CORR_MODEL,
    ) -> pd.DataFrame:
        """Return the partial correlation matrix.

        Parameters
        ----------
        use_returns, log_returns, ret_win_size:
            See :meth:`calculate` for definitions.
        corr_model:
            Correlation method to use.

        Returns
        -------
        pandas.DataFrame
            Partial correlation matrix controlling for all included series.
            The calculation uses the pseudoinverse of the full correlation
            matrix to form the precision matrix ``Ω`` and applies
            ``ρ_{ij·rest} = -Ω_{ij} / sqrt(Ω_{ii} Ω_{jj})``.
        """

        df = self._gather_series(
            use_returns=use_returns,
            log_returns=log_returns,
            ret_win_size=ret_win_size,
        )

        corr = df.corr(method=corr_model)
        inv = np.linalg.pinv(corr.values)
        partial = -inv / np.sqrt(np.outer(np.diag(inv), np.diag(inv)))
        np.fill_diagonal(partial, 1.0)
        return pd.DataFrame(partial, index=corr.index, columns=corr.columns)

    def semi(
        self,
        use_returns: bool = False,
        log_returns: bool = True,
        ret_win_size: int = DEFAULT_RET_WIN_SIZE,
        corr_model: str = DEFAULT_CORR_MODEL,
        window: int | None = None,
        lag: int = 0,
        downside: bool = True,
    ) -> pd.DataFrame | dict[tuple[str, str], pd.Series]:
        """Return downside or upside correlations using sign‑filtered data.

        Parameters
        ----------
        use_returns, log_returns, ret_win_size, corr_model, window, lag:
            See :meth:`calculate` for parameter meanings.
        downside:
            If ``True`` only negative observations are used; otherwise only
            positive ones are considered.  Filtering is applied prior to
            correlation so sample sizes may vary.

        Returns
        -------
        pandas.DataFrame or Dict[Tuple[str, str], pandas.Series]
            Correlation matrix or rolling correlation series depending on the
            ``window`` argument.
        """

        df = self._gather_series(
            use_returns=use_returns,
            log_returns=log_returns,
            ret_win_size=ret_win_size,
        )

        columns = list(df.columns)
        if window is None:
            result = pd.DataFrame(index=columns, columns=columns, dtype=float)
        else:
            result = {}

        for i, col1 in enumerate(columns):
            for col2 in columns[i + 1 :]:
                s1 = df[col1]
                s2 = df[col2].shift(lag)

                mask = (s1 < 0) & (s2 < 0) if downside else (s1 > 0) & (s2 > 0)
                s1_f = s1[mask]
                s2_f = s2[mask]

                if window is None:
                    corr_val = s1_f.corr(s2_f, method=corr_model)
                    result.loc[col1, col2] = corr_val
                    result.loc[col2, col1] = corr_val
                else:
                    corr_series = s1_f.rolling(window).corr(s2_f)
                    result[(col1, col2)] = corr_series.dropna()

        if window is None:
            np.fill_diagonal(result.values, 1.0)
            return result
        return result

__all__ = [
    "CorrelationCalculator",
]
