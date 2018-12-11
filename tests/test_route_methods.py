import pytest

from bocadillo import API
from bocadillo.routing import RouteDeclarationError
from tests.utils import RouteBuilder


@pytest.mark.parametrize(
    "methods, method, status",
    [(["get", "post"], "get", 200), (["post"], "get", 405), ([], "put", 405)],
)
def test_allowed_methods(builder: RouteBuilder, methods, method, status):
    builder.function_based("/", methods=methods)

    response = getattr(builder.api.client, method)("/")
    assert response.status_code == status


@pytest.mark.parametrize(
    "method", ["post", "delete", "put", "patch", "options"]
)
def test_unsafe_methods_not_supported_by_default(api: API, method):
    @api.route("/")
    async def index(req, res):
        pass

    response = getattr(api.client, method)("/")
    assert response.status_code == 405


@pytest.mark.parametrize(
    "methods, method",
    [(["get", "post"], "get"), (["post"], "get"), ([], "put")],
)
def test_route_methods_ignored_on_class_based_views(api: API, methods, method):
    @api.route("/class", methods=methods)
    class Index:
        def get(self, req, res):
            pass

        def put(self, req, res):
            pass

    response = getattr(api.client, method)("/class")
    assert response.status_code == 200


def test_allowed_method_must_be_valid_http_method(builder: RouteBuilder):
    with pytest.raises(RouteDeclarationError):
        builder.function_based("/", methods=["foo"])

    builder.class_based("/", methods=["bar"])


def test_if_get_implemented_by_class_based_view_then_head_mapped(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            pass

    assert api.client.head("/").status_code == 200


def test_if_get_in_function_view_methods_then_head_mapped(api: API):
    @api.route("/", methods=["get"])
    async def index(req, res):
        pass

    assert api.client.head("/").status_code == 200
