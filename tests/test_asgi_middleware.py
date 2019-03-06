from bocadillo import App, ASGIMiddleware


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
