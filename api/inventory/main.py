"""Inventory FastAPI application.

Run with::

    uvicorn api.inventory.main:app --reload
"""

from fastapi import APIRouter, Depends, FastAPI

from inventory.config import FASTAPI_INVENTORY_API_KEY

from ..security import create_api_key_dependency

ROUTERS: list[APIRouter] = []

app = FastAPI(
    title="Inventory API",
    dependencies=[Depends(create_api_key_dependency(FASTAPI_INVENTORY_API_KEY))],
)


@app.get("/")
async def read_inventory_root() -> dict[str, str]:
    """Basic message showing the inventory API is running."""
    return {"message": "Welcome to the Inventory API"}


@app.get("/health")
async def inventory_health_check() -> dict[str, str]:
    """Simple health check for the inventory API."""
    return {"status": "ok"}


for router in ROUTERS:
    app.include_router(router)
