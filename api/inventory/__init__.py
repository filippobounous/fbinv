"""Inventory API package.

Run the service with ``uvicorn``::

    uvicorn api.inventory.main:app --reload
"""

from .main import ROUTERS, app

__all__ = ["app", "ROUTERS"]
