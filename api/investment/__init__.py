"""Investment API package.

Use ``uvicorn`` to run the application from the command line::

    uvicorn api.investment.main:app --reload
"""

from .main import ROUTERS, app

__all__ = ["app", "ROUTERS"]
