"""Inventory FastAPI application.

Run with::

    uvicorn api.inventory.main:app --reload
"""

from fastapi import APIRouter, FastAPI

ROUTERS: list[APIRouter] = []

app = FastAPI(title="Inventory API")

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
