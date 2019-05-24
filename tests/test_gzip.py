from bocadillo import configure, create_client


def test_if_gzip_enabled_then_response_is_compressed(raw_app):
    app = configure(raw_app, gzip=True, gzip_min_size=0)

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    r = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert r.status_code == 200
    assert "content-encoding" in r.headers
    assert r.headers["content-encoding"] == "gzip"
