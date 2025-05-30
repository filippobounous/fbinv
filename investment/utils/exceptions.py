"""Custom exception types for the investment package."""

class DataSourceMethodException(Exception):
    """Raised when a datasource method is used incorrectly."""


class AlphaVantageException(Exception):
    """Errors returned from the Alpha Vantage API."""


class TwelveDataException(Exception):
    """Errors returned from the TwelveData API."""


class TransactionsException(Exception):
    """Raised when there is an issue processing transactions."""


class SecurityMappingError(Exception):
    """Raised when there is a problem with the security mapping."""
