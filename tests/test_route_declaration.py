import pytest

from bocadillo import API
from bocadillo.exceptions import RouteDeclarationError
from tests.utils import RouteBuilder


def test_index_returns_404_by_default(api: API):
    assert api.client.get("/").status_code == 404


def test_if_route_not_registered_then_404(api: API):
    assert api.client.get("/test").status_code == 404


def test_if_route_registered_then_not_404(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            pass

    assert api.client.get("/").status_code != 404


def test_default_status_code_is_200_on_routes(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            pass

    assert api.client.get("/").status_code == 200


def test_route_must_start_with_slash(api: API):
    class Index:
        async def get(self, req, res):
            pass

    with pytest.raises(RouteDeclarationError):
        api.route("foo")(Index)
