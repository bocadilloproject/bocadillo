import pytest

from bocadillo import App, view
from bocadillo.constants import ALL_HTTP_METHODS


@pytest.mark.parametrize(
    "methods, method, status",
    [(["get", "post"], "get", 200), (["post"], "get", 405), ([], "put", 405)],
)
def test_allowed_methods(app: App, client, methods, method, status):
    @app.route("/")
    @view(methods=methods)
    async def index(req, res):
        pass

    response = getattr(client, method)("/")
    assert response.status_code == status


@pytest.mark.parametrize(
    "method", ["post", "delete", "put", "patch", "options"]
)
def test_unsafe_methods_not_supported_by_default(app: App, client, method):
    @app.route("/")
    async def index(req, res):
        pass

    response = getattr(client, method)("/")
    assert response.status_code == 405


def test_if_get_implemented_then_head_mapped(app: App, client):
    @app.route("/")
    class Index:
        async def get(self, req, res):
            pass

    assert client.head("/").status_code == 200


def test_if_get_in_function_view_methods_then_head_mapped(app: App, client):
    @app.route("/")
    @view(methods=["get"])
    async def index(req, res):
        pass

    assert client.head("/").status_code == 200


def test_if_methods_is_all_then_all_methods_allowed(app: App, client):
    @app.route("/")
    @view(methods=all)
    async def index(req, res):
        pass

    for method in map(str.lower, ALL_HTTP_METHODS):
        assert getattr(client, method)("/").status_code == 200
