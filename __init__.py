"""Top-level package for the investment project.

This module exposes a helper function to run the entire test suite. It can be
imported from a Jupyter notebook to execute the project's tests programmatically.
"""

from pathlib import Path
import pytest

__all__ = ["run_tests"]

def run_tests(args=None):
    """Run all unit tests using pytest.

    Parameters
    ----------
    args : list[str] or None
        Additional command line arguments passed to pytest. If omitted,
        the tests are run quietly.

    Returns
    -------
    int
        The pytest exit code.
    """
    if args is None:
        args = ["-q", str(Path(__file__).parent / "tests")]
    return pytest.main(args)
