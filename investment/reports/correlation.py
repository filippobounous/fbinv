"""Reporting tools such as correlation calculations."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Security, Portfolio
class Correlation:
    """Compute correlations between securities or portfolios."""
    def __init__(
        self,
        securities: Optional[List["Security"]] = None,
        portfolios: Optional[List["Portfolio"]] = None,
    ) -> None:
        pass