"Expose a utility to run all relevant tests"

from pathlib import Path
import pytest
from dotenv import load_dotenv


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
    load_dotenv()
    if args is None:
        args = ["-q", str(Path(__file__).parent / "tests")]
    return pytest.main(args)


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(run_tests())



