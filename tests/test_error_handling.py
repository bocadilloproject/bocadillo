import pytest

from bocadillo import API
from bocadillo.exceptions import HTTPError


@pytest.mark.parametrize('status', [
    '400 Bad Request',
    '401 Unauthorized',
    '403 Forbidden',
    '405 Method Not Allowed',
    '500 Internal Server Error',
    # Non-error codes are supported too. Be responsible.
    '200 OK',
    '201 Created',
    '202 Accepted',
    '204 No Content',
])
def test_if_http_error_is_raised_then_automatic_response_is_sent(
        api: API, status: str):
    status_code, phrase = status.split(' ', 1)
    status_code = int(status_code)

    @api.route('/')
    def index(req, res):
        raise HTTPError(status_code)

    response = api.client.get('/')
    assert response.status_code == status_code
    assert response.text == phrase
