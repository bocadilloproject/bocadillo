import pytest

from bocadillo import App
from bocadillo.testing import create_client


def test_false_by_default(app: App):
    assert app.debug is False


def test_setter_updates_exception_and_error_middleware(app: App):
    app.debug = True
    assert app.debug is True
    assert app.exception_middleware.debug is True
    assert app.server_error_middleware.debug is True


def test_if_not_debug_then_no_debug_info_returned(app: App):
    @app.route("/")
    async def index(req, res):
        raise ValueError("Oops")

    client = create_client(app, raise_server_exceptions=False)
    r = client.get("/")
    assert r.status_code == 500
    assert r.text == "500 Internal Server Error"


@pytest.mark.parametrize(
    "accept, content_type",
    [
        (None, "text/plain; charset=utf-8"),
        ("text/html", "text/html; charset=utf-8"),
    ],
)
def test_debug_response(app: App, accept: str, content_type: str):
    app.debug = True

    @app.route("/")
    async def index(req, res):
        raise ValueError("Oops")

    client = create_client(app, raise_server_exceptions=False)
    r = client.get("/", headers={"accept": accept})
    assert r.status_code == 500
    assert r.headers["content-type"] == content_type
    assert 'raise ValueError("Oops")' in r.text
