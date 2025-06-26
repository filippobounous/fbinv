"""Custom warnings configuration."""

import warnings


def custom_warning_formatter(
    message: str,
    category: type,
    filename: str,
    lineno: int,
    file=None,
    line=None,
) -> str:
    """Return simplified warning messages."""
    return f"{message}\n"


warnings.formatwarning = custom_warning_formatter

