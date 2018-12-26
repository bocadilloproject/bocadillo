from bocadillo import API


def test_if_hsts_enabled_and_request_is_on_http_then_redirects_to_https():
    api = API(enable_hsts=True)

    @api.route("/")
    class Index:
        async def get(self, req, res):
            pass

    response = api.client.get("/", allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == "https://testserver/"
