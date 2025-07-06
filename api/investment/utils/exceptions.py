"""Common exception groupings used by the API."""

from investment.utils.exceptions import (
    AlphaVantageException,
    DataSourceMethodException,
    SecurityMappingError,
    TransactionsException,
    TwelveDataException,
)

EXPECTED_EXCEPTIONS: tuple[type[Exception], ...] = (
    AlphaVantageException,
    DataSourceMethodException,
    SecurityMappingError,
    TransactionsException,
    TwelveDataException,
    RuntimeError,
    ValueError,
    KeyError,
)
