import pytest

from bocadillo import API
from bocadillo.constants import ALL_HTTP_METHODS
from bocadillo.views import view


def test_can_register_class_based_view(api: API):
    @api.route("/")
    class Index:
        pass


@pytest.mark.parametrize("method", map(str.lower, ALL_HTTP_METHODS))
def test_if_method_not_implemented_then_405(api: API, method: str):
    @api.route("/")
    class Index:
        pass

    response = getattr(api.client, method)("/")
    assert response.status_code == 405


def test_if_method_implemented_then_as_normal(api: API):
    @api.route("/")
    class Index:
        async def get(self, req, res):
            res.text = "Get!"

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == "Get!"


def test_if_handle_is_implemented_then_bypasses_other_methods(api: API):
    @api.route("/")
    class Index:
        async def handle(self, req, res):
            res.text = "Handle!"

        async def get(self, req, res):
            res.text = "Get!"

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == "Handle!"


def test_sync_handler(api: API):
    @api.route("/")
    class Index:
        def get(self, req, res):
            pass

    assert api.client.get("/").status_code == 200


def test_function_based(api: API):
    @api.route("/")
    @view()
    def index(req, res):
        pass

    assert api.client.get("/").status_code == 200


def test_view_decorator_is_optional(api: API):
    @api.route("/")
    def index(req, res):
        pass

    assert api.client.get("/").status_code == 200
