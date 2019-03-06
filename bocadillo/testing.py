from typing import TYPE_CHECKING

from starlette.testclient import TestClient

if TYPE_CHECKING:
    from .applications import App


def create_client(app: "App", **kwargs) -> TestClient:
    """Create a test client."""
    return TestClient(app, **kwargs)
