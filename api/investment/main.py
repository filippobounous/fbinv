"""Investment FastAPI application.

Run with::

    uvicorn api.investment.main:app --reload
"""

from fastapi import APIRouter, FastAPI

from .core import router as core_router
from .analytics import router as analytics_router

ROUTERS: list[APIRouter] = [core_router, analytics_router]

app = FastAPI(title="Investment API")

@app.get("/")
async def read_root() -> dict[str, str]:
    """Basic message showing the investment API is running."""
    return {"message": "Welcome to the Investment API"}

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health check for the investment API."""
    return {"status": "ok"}

for router in ROUTERS:
    app.include_router(router)
