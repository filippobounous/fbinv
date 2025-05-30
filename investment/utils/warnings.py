import warnings

from typing import Optional, TextIO, Type


def custom_warning_formatter(
    message: str,
    category: Type[Warning],
    filename: str,
    lineno: int,
    file: Optional[TextIO] = None,
    line: Optional[str] = None,
) -> str:
    return f"{message}\n"


warnings.formatwarning = custom_warning_formatter
