from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.portfolio import Portfolio
    from ..core.security import BaseSecurity
class Correlation:
    def __init__(
        self,
        securities: Optional[List["BaseSecurity"]] = None,
        portfolios: Optional[List["Portfolio"]] = None,
    ) -> None:
        pass
