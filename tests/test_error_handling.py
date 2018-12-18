import pytest

from bocadillo import API
from bocadillo.exceptions import HTTPError
from bocadillo.error_handlers import (
    error_to_media,
    error_to_text,
    error_to_html,
)


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


@pytest.mark.parametrize(
    "handler, check_response",
    [
        (error_to_html, lambda res: res.text == "<h1>403 Forbidden</h1>"),
        (
            error_to_media,
            lambda res: res.json() == {"error": "Forbidden", "status": 403},
        ),
        (error_to_text, lambda res: res.text == "403 Forbidden"),
    ],
)
def test_builtin_handlers(api: API, handler, check_response):
    api.add_error_handler(HTTPError, handler)

    @api.route("/")
    async def index(req, res):
        raise HTTPError(403)

    response = api.client.get("/")
    assert response.status_code == 403
    print(response.text)
    assert check_response(response)
