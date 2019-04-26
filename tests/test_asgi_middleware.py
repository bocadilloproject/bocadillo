import pytest

from bocadillo import App, configure, create_client


def test_asgi_middleware(app: App, client):
    params = None
    received_app = False
    called = False

    class Middleware:
        def __init__(self, app, **kwargs):
            nonlocal params, received_app
            params = kwargs
            received_app = isinstance(app, App)
            self.app = app

        async def __call__(self, scope, receive, send):
            nonlocal called
            await self.app(scope, receive, send)
            called = True

    app.add_asgi_middleware(Middleware, hello="world")
    assert not received_app
    assert params == {"hello": "world"}

    @app.route("/")
    async def index(req, res):
        pass

    client.get("/")
    assert called


@pytest.mark.parametrize(
    ["route", "origin", "expected", "expected_body"],
    [
        ("/", "localhost:8001", "localhost:8001", "Hello"),
        ("/", "ietf.org", "ietf.org", "Hello"),
        ("/", "unknown.org", None, "Hello"),
        ("/sub/", "localhost:8001", "localhost:8001", "OK"),
        ("/sub/", "ietf.org", "ietf.org", "OK"),
        ("/sub/", "unknown.org", None, "OK"),
    ],
)
def test_middleware_called_if_routed_to_sub_app(
    raw_app, route: str, origin: str, expected: str, expected_body: str
):
    app = configure(
        raw_app,
        cors={"allow_origins": ["example.com", "localhost:8001", "ietf.org"]},
    )

    @app.route("/")
    async def index(req, res):
        res.text = "Hello"

    sub = App()

    @sub.route("/")
    class SubApp:
        async def get(self, req, res):
            res.text = "OK"

    app.mount("/sub", sub)

    client = create_client(app)
    res = client.get(route, headers={"origin": origin})

    assert res.text == expected_body

    if not expected:  # unknown origin -> no allow-origin header
        assert "access-control-allow-origin" not in res.headers
    else:  # allowed origin -> allow-origin header"
        assert "access-control-allow-origin" in res.headers
        assert res.headers.get("access-control-allow-origin") == expected


def test_asgi2_middleware_not_supported(app: App):
    class Middleware:
        def __init__(self, app):
            pass

        def __call__(self, scope):
            pass

    with pytest.raises(ValueError) as ctx:
        app.add_asgi_middleware(Middleware)

    error = str(ctx.value).lower()
    for phrase in "asgi2", "please upgrade", "asgi3", "scope, receive, send":
        assert phrase in error
