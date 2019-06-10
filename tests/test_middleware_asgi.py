import pytest
from starlette.responses import PlainTextResponse

from bocadillo import App, HTTPError


class ASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


def test_asgi_middleware(app: App, client):
    params = None
    received_app = False
    called = False

    class Middleware(ASGIMiddleware):
        def __init__(self, app, **kwargs):
            super().__init__(app)
            nonlocal params, received_app
            params = kwargs
            received_app = isinstance(app, App)

        async def __call__(self, scope, receive, send):
            nonlocal called
            called = True
            await super().__call__(scope, receive, send)

    app.add_middleware(Middleware, hello="world")
    assert not received_app
    assert params == {"hello": "world"}

    @app.route("/")
    async def index(req, res):
        pass

    client.get("/")
    assert called


def test_send_response_in_middleware(app: App, client):
    class Middleware(ASGIMiddleware):
        async def __call__(self, scope, receive, send):
            response = PlainTextResponse("OK")
            await response(scope, receive, send)

    app.add_middleware(Middleware)

    r = client.get("/")
    assert r.status_code == 200
    assert r.text == "OK"


def test_error_handling(app: App, client):
    class NotAvailableMiddleware(ASGIMiddleware):
        async def __call__(self, scope, receive, send):
            raise HTTPError(503)

    app.add_middleware(NotAvailableMiddleware)

    r = client.get("/")
    assert r.status_code == 503
    assert "Service Unavailable" in r.text


def test_middleware_called_if_routed_to_sub_app(app: App, client):
    called = False

    class Middleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            nonlocal called
            called = True
            await self.app(scope, receive, send)

    app.add_middleware(Middleware)

    sub = App()

    @sub.route("/")
    async def sub_index(req, res):
        pass

    app.mount("/sub", sub)

    r = client.get("/sub/")
    assert r.status_code == 200
    assert called


def test_asgi2_middleware_not_supported(app: App):
    class Middleware(ASGIMiddleware):
        def __call__(self, scope):
            pass

    with pytest.raises(ValueError) as ctx:
        app.add_middleware(Middleware)

    error = str(ctx.value).lower()
    for phrase in "asgi2", "please upgrade", "asgi3", "scope, receive, send":
        assert phrase in error
