from bocadillo import API


def test_chunked_response(api: API):
    @api.route("/")
    async def index(req, res):
        res.chunked = True

    r = api.client.get("/")
    assert r.headers["transfer-encoding"] == "chunked"
