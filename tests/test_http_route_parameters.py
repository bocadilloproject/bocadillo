import pytest

from bocadillo import API
from bocadillo.routing import RouteDeclarationError


def test_parameter_is_passed_as_argument(api: API):
    @api.route("/greet/{person}")
    async def greet(req, res, person: str):
        res.text = person

    response = api.client.get("/greet/John")
    assert response.status_code == 200
    assert response.text == "John"


def test_if_route_expects_int_but_int_not_given_then_404(api: API):
    @api.route("/add/{x:d}/{y:d}")
    async def add(req, res, x, y):
        res.text = str(x + y)

    response = api.client.get("/add/1/foo")
    assert response.status_code == 404


def test_if_parameter_declared_but_not_used_then_error_raised(api: API):
    with pytest.raises(RouteDeclarationError):

        @api.route("/greet/{person}")
        async def greet(req, res):
            pass

    with pytest.raises(RouteDeclarationError):

        @api.route("/greet/{person}")
        class Greet:
            async def get(self, req, res):
                pass


def test_if_parameter_used_but_not_declared_then_error_raised(api: API):
    with pytest.raises(RouteDeclarationError):

        @api.route("/greet")
        async def greet(req, res, person):
            pass

    with pytest.raises(RouteDeclarationError):

        @api.route("/greet")
        class Greet:
            def get(self, req, res, person):
                pass
