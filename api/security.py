"""Reusable API key security dependency for FastAPI apps."""

import secrets
from typing import Callable, Optional

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def create_api_key_dependency(expected_key: Optional[str]) -> Callable[[str], None]:
    """Return a dependency that validates ``expected_key``."""

    def verify_api_key(api_key: str = Security(_API_KEY_HEADER)) -> None:
        if expected_key is None or not secrets.compare_digest(api_key or "", expected_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )

    return verify_api_key
