"""Core endpoints for listing and retrieving investment information."""

from fastapi import APIRouter

from investment.core.portfolio import Portfolio
from investment.core.security.generic import Generic

router = APIRouter(prefix="/core")


@router.post("/portfolio")
async def get_portfolio_bulk(codes: list[str]) -> dict[str, dict]:
    """Return portfolio attributes for each provided code."""
    return {code: Portfolio(code).model_dump() for code in codes}


@router.post("/security")
async def get_security_bulk(codes: list[str]) -> dict[str, dict]:
    """Return security attributes for each provided code."""
    return {code: Generic(code).model_dump() for code in codes}


@router.get("/portfolio/{code}")
async def get_portfolio(code: str) -> dict:
    """Return portfolio attributes for ``code``."""
    return Portfolio(code).model_dump()


@router.get("/security/{code}")
async def get_security(code: str) -> dict:
    """Return security attributes for ``code``."""
    return Generic(code).model_dump()
