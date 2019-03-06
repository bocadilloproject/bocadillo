from bocadillo import App


def test_chunked_response(app: App, client):
    @app.route("/")
    async def index(req, res):
        res.chunked = True

    r = client.get("/")
    assert r.headers["transfer-encoding"] == "chunked"
