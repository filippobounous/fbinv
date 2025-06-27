"""
Correlation class to calculate and analyse correlations between securities and
portfolios to then allow further analysis
""" # TODO

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.portfolio import Portfolio
    from ..core.security import BaseSecurity

class Correlation:
    """Placeholder for correlation calculations."""

    def __init__(
        self,
        securities: Optional[List["BaseSecurity"]] = None,
        portfolios: Optional[List["Portfolio"]] = None,
    ) -> None:
        """Store the input security and portfolio lists."""
