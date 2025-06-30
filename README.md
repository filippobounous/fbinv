# Personal Project

This repository contains utilities for managing investment data and inventory.
It includes analytics tools, portfolio management helpers, data source wrappers,
and functionality for tracking items across locations.

## Running tests

The package provides a small helper called `run_tests()` which executes the
project's test suite. It simply calls `pytest` under the hood, so ensure that
all test-related dependencies are installed before running it.

### Example (Jupyter Notebook)

```python
import personal

personal.run_tests()
```
