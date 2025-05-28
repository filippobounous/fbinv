from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Security, Portfolio
class Correlation:
    def __init__(
        self,
        securities: Optional[List["Security"]] = None,
        portfolios: Optional[List["Portfolio"]] = None,
    ) -> None:
        pass