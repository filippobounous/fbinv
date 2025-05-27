import warnings

def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
    return f"{message}\n"

warnings.formatwarning = custom_warning_formatter