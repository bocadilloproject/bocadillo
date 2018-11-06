import pytest

from bocadillo import API
from bocadillo.exceptions import RouteDeclarationError


def test_parameter_is_passed_as_argument(api: API):
    @api.route('/greet/{person}')
    def greet(req, res, person: str):
        res.content = person

    response = api.client.get('/greet/John')
    assert response.status_code == 200
    assert response.text == 'John'


def test_if_route_expects_int_but_int_not_given_then_404(api: API):
    @api.route('/add/{x:d}/{y:d}')
    def add(req, res, x, y):
        res.content = str(x + y)

    response = api.client.get('/add/1/foo')
    assert response.status_code == 404


def test_if_parameter_not_included_in_signature_then_error_raised(api: API):
    with pytest.raises(RouteDeclarationError):
        @api.route('/greet/{person}')
        def greet(req, res):
            pass

    with pytest.raises(RouteDeclarationError):
        @api.route('/add/{x}/{y}')
        class Print:
            def get(self, req, res, x):
                pass


def test_if_parameter_not_declared_in_route_then_error_raised(api: API):
    with pytest.raises(RouteDeclarationError):
        @api.route('/greet')
        def greet(req, res, person):
            pass

    with pytest.raises(RouteDeclarationError):
        @api.route('/print')
        class Print:
            def get(self, req, res, x):
                pass
