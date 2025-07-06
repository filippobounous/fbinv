# Personal Finance Toolkit

This project contains a collection of modules for managing investments and household inventory. It also exposes FastAPI services for both domains.

## Features

- **Investment module** – tools for retrieving market data, portfolio management and analytics
- **Inventory module** – utilities for tracking items, rooms and houses
- **FastAPI apps** – REST interfaces located under `api/`

## Setup

1. Create a Python virtual environment and install the package:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. Copy `.env.example` to `.env` and fill in the required variables.
3. Start the desired API with `uvicorn`:
   ```bash
   uvicorn api.investment.main:app --reload
   # or
   uvicorn api.inventory.main:app --reload
   ```

The FastAPI apps are protected by optional API keys. See `api/README.md` for details on how to generate and use them.

## Docker

You can also run the APIs using Docker. First copy `.env.example` to `.env` and fill
in the required values. The Dockerfile is based on `python:3.11.4-slim` and
installs the latest security patches to minimize vulnerabilities. Build and start
the services with docker-compose:

```bash
docker compose up --build
```

This launches two containers:

- **investment** – exposes the investment API on port `8000`
- **inventory** – exposes the inventory API on port `8001`

Any changes to the local source will be picked up the next time you rebuild the
containers.
