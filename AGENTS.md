# AGENTS Guidelines

These instructions apply to the entire repository. Any agent contributing changes must follow them.

## 1. Repository Overview
- The repo hosts two FastAPI services for *investment* and *inventory* data.
- Important directories:
  - `api/` – FastAPI apps and security helpers.
  - `investment/` – core models and analytics.
  - `inventory/` – inventory management modules.

## 2. Environment Setup
- Use Python **3.11**.
- Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

- Copy `.env.example` to `.env` and fill in all variables.
- To run the APIs via Docker, use `docker compose up --build`.

## 3. API Keys
- Set `FASTAPI_INVESTMENT_API_KEY` and `FASTAPI_INVENTORY_API_KEY`.
- Generate keys with:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

- Include the value in requests via the `X-API-Key` header.

## 4. Coding Style
- Follow **PEP 8** and use type hints.
- Format code with **black**, **flake8**, and **isort**.

## 5. Commit Message Guidelines
- Use the imperative mood, e.g. "Add test for portfolio".
- Keep the summary under 72 characters.
- Describe what changed and why.

## 6. Testing Instructions
- Run tests with:

```bash
python run_tests.py
```

- Install any missing dependencies from `requirements.txt`.
- If a command cannot run because of environment restrictions, note this in the PR.

## 7. Pull Request Notes
- Provide a concise summary of changes.
- Mention which tests were executed.
- Include references to changed files and line numbers using the format `F:path#L1-L2`.
- Summarize blocked network access in a dedicated **Network access** section if needed.

## 8. Version Compatibility
- Dependencies specify minimum versions in `setup.py` and `requirements.txt`.
- Ensure new code remains compatible with Python 3.11.
