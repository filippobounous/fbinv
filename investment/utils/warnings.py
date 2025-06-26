"""Custom warnings configuration."""

import warnings

def custom_warning_formatter(
    message: str,
    **kwargs
) -> str:
    """Return simplified warning messages."""
    return f"{message}\n"

warnings.formatwarning = custom_warning_formatter
