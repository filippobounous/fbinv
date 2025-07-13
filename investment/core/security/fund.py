"""Fund class for mutual fund securities"""

from .isin import ISINSecurity


class Fund(ISINSecurity):
    """
    Fund Security.

    A mutual fund. Initialised with:
        code (str): The Bloomberg ticker for the mutual fund (ticker and exchange)
    """

    entity_type: str = "fund"


__all__ = [
    "Fund",
]
