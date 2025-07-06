# Investment Package

This repository contains tools for handling investment data.

## Installation

Use `pip` to install the required dependencies:

```bash
pip install -r requirements.txt
```

1. Create a Python virtual environment and install the package:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. Copy `.env.example` to `.env` and fill in the required variables.
3. Start the desired API with `uvicorn`:
   ```bash
   uvicorn api.investment.main:app
   # or
   uvicorn api.inventory.main:app
   ```
   Add `--reload` if you want automatic code reloading during development.

The FastAPI apps are protected by optional API keys. See `api/README.md` for details on how to generate and use them.

## Docker

You can also run the APIs using Docker. First copy `.env.example` to `.env` and fill
in the required values. The `.env` file is ignored during Docker builds so your
credentials stay local. The Dockerfile is based on `python:3.11.4-slim` and
installs the latest security patches to minimize vulnerabilities. Build and start the services with
docker-compose:

```bash
docker compose up --build
```

This launches two containers:

- **investment** – exposes the investment API on port `8000`
- **inventory** – exposes the inventory API on port `8001`

Any changes to the local source will be picked up the next time you rebuild the
containers.

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
