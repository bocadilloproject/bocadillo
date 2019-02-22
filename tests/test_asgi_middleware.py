from starlette.middleware.gzip import GZipMiddleware

from bocadillo import App


def test_if_asgi_middleware_is_applied():
    app = App(enable_gzip=False)
    app.add_asgi_middleware(GZipMiddleware, minimum_size=0)

    @app.route("/")
    async def index(req, res):
        pass

    response = app.client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
