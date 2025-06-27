"""Base class for initialisations from the mapping csv files available"""

from abc import abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING, List, Union

import pandas as pd
from pydantic import BaseModel

from ..analytics.realised_volatility import RealisedVolatilityCalculator
from ..analytics.returns import ReturnsCalculator
from ..datasource import LocalDataSource
from ..utils.consts import DEFAULT_RET_WIN_SIZE, DEFAULT_RV_WIN_SIZE, DEFAULT_RV_MODEL

if TYPE_CHECKING:
    from ..datasource import BaseDataSource

class BaseMappingEntity(BaseModel):
    """
    BaseMappingEntity.
    
    Returns required attributes to a class from the base csv mapping files.
    Initialised with:
        entity_type (str): The entity type to select the correct load_method.
        code (str): The code for the entity to select the correct parameters.
    """
    entity_type: str
    code: str
    _local_datasource: LocalDataSource = LocalDataSource

    def __init__(self, **kwargs):
        """Initialise entity attributes from the local mapping files."""
        super().__init__(**kwargs)

        lds: LocalDataSource = self._local_datasource()

        load_methods = {
            "composite": lds.load_composite_security,
            "currency_cross": lds.load_security,
            "etf": lds.load_security,
            "fund": lds.load_security,
            "portfolio": lds.load_portfolio,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di: Dict[str, Any] = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)

    @abstractmethod
    def get_price_history(
        self,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
        intraday: bool = False,
    ) -> pd.DataFrame:
        """Returns time series of prices."""

    def get_returns(
        self,
        use_ln_ret: bool = True,
        ret_win_size: Union[int, List[int]] = DEFAULT_RET_WIN_SIZE,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        """Returns the returns series"""
        df = self.get_price_history(datasource=datasource, local_only=local_only, intraday=False)

        return ReturnsCalculator(
            ret_win_size=ret_win_size, use_ln_ret=use_ln_ret
        ).calculate(df=df)

    def get_realised_volatility(
        self,
        rv_model: Union[str, List[str]] = DEFAULT_RV_MODEL,
        rv_win_size: Union[int, List[int]] = DEFAULT_RV_WIN_SIZE,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
    ) -> pd.DataFrame:
        """Returns the realised volatility series"""
        df = self.get_price_history(datasource=datasource, local_only=local_only, intraday=False)

        return RealisedVolatilityCalculator(
            rv_win_size=rv_win_size, rv_model=rv_model
        ).calculate(df=df)
