import pytest

from bocadillo import API


def test_false_by_default(api: API):
    assert api.debug is False


def test_setter_updates_exception_and_error_middleware(api: API):
    api.debug = True
    assert api.debug is True
    assert api.exception_middleware.debug is True
    assert api.server_error_middleware.debug is True


def test_if_not_debug_then_no_debug_info_returned(api: API):
    @api.route("/")
    async def index(req, res):
        raise ValueError("Oops")

    client = api.build_client(raise_server_exceptions=False)
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
def test_debug_response(api: API, accept: str, content_type: str):
    api.debug = True

    @api.route("/")
    async def index(req, res):
        raise ValueError("Oops")

    client = api.build_client(raise_server_exceptions=False)
    r = client.get("/", headers={"accept": accept})
    assert r.status_code == 500
    assert r.headers["content-type"] == content_type
    assert 'raise ValueError("Oops")' in r.text
