"""Utilities for configuring warning output."""

import warnings


def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
    """Return a simplified warning format string."""

    return f"{message}\n"


warnings.formatwarning = custom_warning_formatter
