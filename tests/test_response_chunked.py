from bocadillo import App


def test_chunked_response(app: App):
    @app.route("/")
    async def index(req, res):
        res.chunked = True

    r = app.client.get("/")
    assert r.headers["transfer-encoding"] == "chunked"
