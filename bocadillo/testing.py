from starlette.testclient import TestClient

from .applications import App


def create_client(app: App, **kwargs) -> TestClient:
    """Create a test client."""
    return TestClient(app, **kwargs)
