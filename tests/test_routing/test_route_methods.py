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


def test_allowed_method_must_be_valid_http_method(api: API):
    with pytest.raises(RouteDeclarationError):
        @api.route('/', methods=['foo'])
        def index(req, res):
            pass
