from starlette.middleware.gzip import GZipMiddleware

from bocadillo import API


def test_if_asgi_middleware_is_applied():
    api = API(enable_gzip=False)
    api.add_asgi_middleware(GZipMiddleware, minimum_size=0)

    @api.route("/")
    class Index:
        async def get(self, req, res):
            pass

    response = api.client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
