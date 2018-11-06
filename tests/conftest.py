import pytest

from bocadillo import API
from .utils import RouteBuilder


@pytest.fixture
def api():
    return API()


@pytest.fixture
def builder(api: API):
    return RouteBuilder(api)
