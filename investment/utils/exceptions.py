"""Custom exception classes for the project."""

class DataSourceMethodException(Exception):
    """Raised when a data source method is unavailable."""

class AlphaVantageException(Exception):
    """Raised for AlphaVantage specific errors."""

class TwelveDataException(Exception):
    """Raised for TwelveData specific errors."""

class TransactionsException(Exception):
    """Raised when transaction data cannot be processed."""

class SecurityMappingError(Exception):
    """Raised for issues within the security mapping files."""

