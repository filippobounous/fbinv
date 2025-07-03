# Investment Package

This repository contains tools for handling investment data.

## Installation

Use `pip` to install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

Automated tests can be executed with:

```bash
python run_tests.py
```

This command uses the `python-dotenv` (>=1.0) package to load environment
variables from a `.env` file if present. Ensure the dependencies are
installed before running the tests.

All dependencies specify minimum versions in both `setup.py` and
`requirements.txt` to ensure consistent installation across environments.
