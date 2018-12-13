import pytest

from bocadillo import API
from bocadillo.exceptions import HTTPError
from bocadillo.error_handlers import error_to_media


@pytest.mark.parametrize(
    "status",
    [
        "400 Bad Request",
        "401 Unauthorized",
        "403 Forbidden",
        "405 Method Not Allowed",
        "500 Internal Server Error",
        # Non-error codes are supported too. Be responsible.
        "200 OK",
        "201 Created",
        "202 Accepted",
        "204 No Content",
    ],
)
def test_if_http_error_is_raised_then_automatic_response_is_sent(
    api: API, status: str
):
    status_code, phrase = status.split(" ", 1)
    status_code = int(status_code)

    @api.route("/")
    def index(req, res):
        raise HTTPError(status_code)

    response = api.client.get("/")
    assert response.status_code == status_code
    assert phrase in response.text


@pytest.mark.parametrize(
    "exception_cls", [KeyError, ValueError, AttributeError]
)
def test_custom_error_handler(api: API, exception_cls):

    called = False

    @api.error_handler(KeyError)
    def on_key_error(req, res, exc):
        nonlocal called
        res.text = "Oops!"
        called = True

    @api.route("/")
    def index(req, res):
        raise exception_cls("foo")

    if exception_cls == KeyError:
        response = api.client.get("/")
        assert called
        assert response.status_code == 500
        assert response.text == "Oops!"
    else:
        response = api.client.get("/")
        assert response.status_code == 500
        assert not called


def test_media_handler(api: API):
    api.add_error_handler(HTTPError, error_to_media)

    @api.route("/")
    async def index(req, res):
        raise HTTPError(503)

    response = api.client.get("/")
    assert response.status_code == 503
    assert response.json() == {"error": "Service Unavailable", "status": 503}
