from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.portfolio import Portfolio
    from ..core.security import Security
class Correlation:
    def __init__(
        self,
        securities: Optional[List["Security"]] = None,
        portfolios: Optional[List["Portfolio"]] = None,
    ) -> None:
        pass