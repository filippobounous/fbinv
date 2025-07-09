# FastAPI Security Guide

Each FastAPI application is secured with its own API key that must be provided
via the `X-API-Key` HTTP header. Two environment variables control the keys:

- `FASTAPI_INVESTMENT_API_KEY`
- `FASTAPI_INVENTORY_API_KEY`

If a key is not set, the corresponding API will reject all requests.

## How it Works

The `create_api_key_dependency` helper in `api/security.py` creates a FastAPI
dependency that compares the provided header against the expected key using a
constant-time comparison. Each app declares this dependency, so every endpoint
requires the correct key.

```python
from api.security import create_api_key_dependency
from investment.config import FASTAPI_INVESTMENT_API_KEY

app = FastAPI(
    title="Investment API",
    dependencies=[Depends(create_api_key_dependency(FASTAPI_INVESTMENT_API_KEY))],
)
```

Requests without a valid key receive `401 Unauthorized`.

There is one API instance per parent module in this repository. Currently the
following apps are available:

- `api.investment.main` – endpoints for the investment module
- `api.inventory.main` – endpoints for the inventory module

Run them individually with `uvicorn`:

```bash
uvicorn api.investment.main:app --reload
uvicorn api.inventory.main:app --reload
```

## Generating Keys

You can create a strong random key using Python or OpenSSL:

```bash
python -c 'import secrets; print(secrets.token_hex(32))'
# or
openssl rand -hex 32
```

Set the generated value in your environment or `.env` file:

```
FASTAPI_INVESTMENT_API_KEY=<your random key>
FASTAPI_INVENTORY_API_KEY=<your random key>
```

### Managing multiple keys

If you need multiple keys (for example one per client) you can generate several
values and store them in a database or file along with the owner information.
When a request arrives you can look up the supplied key and log the request
under that owner. If a key is compromised you can revoke it by removing it from
your store. Storing only hashed versions of the keys provides an extra security
layer.

## Verifying the Key

Follow these steps to confirm your API key is configured correctly:

1. Set `FASTAPI_INVESTMENT_API_KEY` (or `FASTAPI_INVENTORY_API_KEY`) in your
   environment or `.env` file.
2. Start the API using `uvicorn`. The port defaults to `8000` but can be
   customised with the `INVESTMENT_API_PORT` variable.
3. Call the `/health` endpoint with the same value in the `X-API-Key` header:

```bash
curl -H "X-API-Key: $FASTAPI_INVESTMENT_API_KEY" \
     http://localhost:${INVESTMENT_API_PORT:-8000}/health
```

You should receive `{"status": "ok"}` if the key matches. A response of
`{"detail": "Invalid or missing API key"}` indicates the header does not match
the value used when starting the server.

See `.env.example` for all available environment variables.

## Using the Endpoints

Most routes follow a simple pattern: **GET** endpoints accept a single code via the URL path, while **POST** endpoints accept a JSON array of codes. Always include the API key in the `X-API-Key` header.

### Single entity (GET)

```bash
curl -H "X-API-Key: $FASTAPI_INVESTMENT_API_KEY" \
     http://localhost:${INVESTMENT_API_PORT:-8000}/core/security/SPY%20US
```

### Multiple entities (POST)

```bash
curl -X POST http://localhost:${INVESTMENT_API_PORT:-8000}/core/security \
     -H "Content-Type: application/json" \
     -H "X-API-Key: $FASTAPI_INVESTMENT_API_KEY" \
     -d '["SPY US", "AAPL US"]'
```

Replace the codes with your desired tickers or portfolio identifiers. The response will be a JSON object keyed by code.
