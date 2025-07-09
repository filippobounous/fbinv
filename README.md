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
3. Start the desired API with `uvicorn` (the port can be set via
   `INVESTMENT_API_PORT` or `INVENTORY_API_PORT` in your `.env` file):
   ```bash
   uvicorn api.investment.main:app --port ${INVESTMENT_API_PORT:-8000}
   # or
   uvicorn api.inventory.main:app --port ${INVENTORY_API_PORT:-8001}
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

This launches two containers. The exposed ports can be customized via the
`INVESTMENT_API_PORT` and `INVENTORY_API_PORT` variables in your `.env` file.
Defaults are `8000` and `8001` respectively:

- **investment** – exposes the investment API on the configured port
- **inventory** – exposes the inventory API on the configured port

Any changes to the local source will be picked up the next time you rebuild the
containers.

For easier development you can mount the project directory and enable auto-
reloading inside the containers. Uncomment the `volumes` lines and the
`--reload` flags in `docker-compose.yml` to watch for changes without bringing
the services down.

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
