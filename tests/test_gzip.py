from bocadillo import App


def test_if_gzip_enabled_then_response_is_compressed():
    app = App(enable_gzip=True, gzip_min_size=0)

    @app.route("/")
    async def index(req, res):
        pass

    response = app.client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
