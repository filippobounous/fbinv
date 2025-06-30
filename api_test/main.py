"""Example commands for interacting with the API.

The script assumes the Investment API runs at ``http://localhost:8000`` and
the Inventory API at ``http://localhost:8001``. Override these defaults by
setting the ``INVESTMENT_URL`` and ``INVENTORY_URL`` environment variables.
"""

import os
import requests

INVESTMENT_URL = os.getenv("INVESTMENT_URL", "http://localhost:8000")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://localhost:8001")

def main() -> None:
    """Run a couple of GET requests against the local APIs."""
    print("Investment root:", requests.get(f"{INVESTMENT_URL}/").json())
    print("Investment health:", requests.get(f"{INVESTMENT_URL}/health").json())
    print("Inventory root:", requests.get(f"{INVENTORY_URL}/").json())
    print("Inventory health:", requests.get(f"{INVENTORY_URL}/health").json())

if __name__ == "__main__":  # pragma: no cover - demo script
    main()

