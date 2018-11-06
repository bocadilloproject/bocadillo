import pytest

from bocadillo import API
from bocadillo.exceptions import RouteDeclarationError

@pytest.mark.parametrize('methods, method, expected_status_code', [
    (['get', 'post'], 'get', 200),
    (['post'], 'get', 405),
    ([], 'put', 405),
])
def test_allowed_methods(api: API, methods, method, expected_status_code):
    @api.route('/', methods=methods)
    def index(req, res):
        pass

    response = getattr(api.client, method)('/')
    assert response.status_code == expected_status_code


@pytest.mark.parametrize('methods, method', [
    (['get', 'post'], 'get'),
    (['post'], 'get'),
    ([], 'put'),
])
def test_route_methods_are_ignored_on_class_based_views(
        api: API, methods, method):
    @api.route('/class', methods=methods)
    class Index:
        def get(self, req, res):
            pass

        def put(self, req, res):
            pass

    response = getattr(api.client, method)('/class')
    assert response.status_code == 200


def test_allowed_method_must_be_valid_http_method(api: API):
    with pytest.raises(RouteDeclarationError):
        @api.route('/', methods=['foo'])
        def index(req, res):
            pass

    with pytest.raises(RouteDeclarationError):
        @api.route('/', methods=['bar'])
        class Index:
            pass
