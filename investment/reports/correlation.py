from typing import List, Optional, Dict, Tuple, Union, TYPE_CHECKING

import pandas as pd

from ..analytics.correlation import CorrelationCalculator
from ..utils.consts import DEFAULT_RET_WIN_SIZE, DEFAULT_CORR_MODEL

if TYPE_CHECKING:
    from ..core.portfolio import Portfolio
    from ..core.security import BaseSecurity


class CorrelationReport:
    """Generate correlation analyses for portfolios and securities."""

    def __init__(
        self,
        securities: Optional[List["BaseSecurity"]] = None,
        portfolios: Optional[List["Portfolio"]] = None,
    ) -> None:
        """Store entity lists for later analysis."""
        self.calculator = CorrelationCalculator(securities, portfolios)

    def correlation_matrix(
        self,
        use_returns: bool = False,
        log_returns: bool = True,
        ret_win_size: int = DEFAULT_RET_WIN_SIZE,
        corr_model: str = DEFAULT_CORR_MODEL,
        lag: int = 0,
    ) -> pd.DataFrame:
        """Return a simple correlation matrix."""
        return self.calculator.calculate(
            use_returns=use_returns,
            log_returns=log_returns,
            ret_win_size=ret_win_size,
            corr_model=corr_model,
            lag=lag,
        )

    def rolling_correlations(
        self,
        window: int,
        use_returns: bool = False,
        log_returns: bool = True,
        ret_win_size: int = DEFAULT_RET_WIN_SIZE,
        corr_model: str = DEFAULT_CORR_MODEL,
        lag: int = 0,
    ) -> Dict[Tuple[str, str], pd.Series]:
        """Return rolling correlations for all pairs."""
        result = self.calculator.calculate(
            use_returns=use_returns,
            log_returns=log_returns,
            ret_win_size=ret_win_size,
            corr_model=corr_model,
            window=window,
            lag=lag,
        )
        assert isinstance(result, dict)
        return result

    def lagged_matrices(
        self,
        lags: List[int],
        use_returns: bool = False,
        log_returns: bool = True,
        ret_win_size: int = DEFAULT_RET_WIN_SIZE,
        corr_model: str = DEFAULT_CORR_MODEL,
    ) -> Dict[int, Union[pd.DataFrame, Dict[Tuple[str, str], pd.Series]]]:
        """Return correlations across multiple lags."""
        return self.calculator.lagged(
            lags=lags,
            use_returns=use_returns,
            log_returns=log_returns,
            ret_win_size=ret_win_size,
            corr_model=corr_model,
        )
