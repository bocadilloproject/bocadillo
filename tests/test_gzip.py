from bocadillo import API


def test_if_gzip_enabled_then_response_is_compressed():
    api = API(enable_gzip=True, gzip_min_size=0)

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
