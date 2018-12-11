import pytest

from bocadillo import API
from bocadillo.constants import ALL_HTTP_METHODS
from tests.utils import RouteBuilder


def test_can_register_class_based_view(builder: RouteBuilder):
    builder.class_based("/")


@pytest.mark.parametrize("method", map(str.lower, ALL_HTTP_METHODS))
def test_if_method_not_implemented_then_405(builder: RouteBuilder, method: str):
    builder.class_based("/")

    response = getattr(builder.api.client, method)("/")
    assert response.status_code == 405


def test_if_method_implemented_then_as_normal(api: API):
    @api.route("/")
    class Index:
        def get(self, req, res):
            res.text = "Get!"

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == "Get!"


def test_if_handle_is_implemented_then_bypasses_other_methods(api: API):
    @api.route("/")
    class Index:
        def handle(self, req, res):
            res.text = "Handle!"

        def get(self, req, res):
            res.text = "Get!"

    response = api.client.get("/")
    assert response.status_code == 200
    assert response.text == "Handle!"
