from bocadillo import App, ASGIMiddleware


def test_raw_asgi_middleware():
    initialized = False
    called = False

    class Middleware:
        def __init__(self, app):
            nonlocal initialized
            self.app = app
            initialized = True

        def __call__(self, scope: dict):
            nonlocal called
            called = True
            return self.app(scope)

    app = App()
    app.add_asgi_middleware(Middleware)

    assert initialized

    @app.route("/")
    async def index(req, res):
        pass

    app.client.get("/")
    assert called


def test_asgi_middleware():
    app = App()
    params = None
    received_app = False

    class Middleware(ASGIMiddleware):
        def __init__(self, parent, app: App, **kwargs):
            super().__init__(parent, app)
            nonlocal params, received_app
            params = kwargs
            received_app = isinstance(app, App)

    app.add_asgi_middleware(Middleware, hello="world")
    assert received_app
    assert params == {"hello": "world"}
