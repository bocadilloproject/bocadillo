import pytest

from bocadillo import App, ASGIMiddleware, configure, create_client


def test_asgi_middleware(app: App, client):
    params = None
    received_app = False
    called = False

    class Middleware(ASGIMiddleware):
        def __init__(self, inner, app: App, **kwargs):
            super().__init__(inner, app)
            nonlocal params, received_app
            params = kwargs
            received_app = isinstance(app, App)

        def __call__(self, scope):
            nonlocal called
            called = True
            return super().__call__(scope)

    app.add_asgi_middleware(Middleware, hello="world")
    assert received_app
    assert params == {"hello": "world"}

    @app.route("/")
    async def index(req, res):
        pass

    client.get("/")
    assert called


def test_pure_asgi_middleware(app: App, client):
    initialized = False
    called = False

    class Middleware:
        def __init__(self, inner):
            nonlocal initialized
            self.inner = inner
            initialized = True

        def __call__(self, scope: dict):
            nonlocal called
            called = True
            return self.inner(scope)

    app.add_asgi_middleware(Middleware)

    assert initialized

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
