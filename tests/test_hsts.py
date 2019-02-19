from bocadillo import App


def test_if_hsts_enabled_and_request_is_on_http_then_redirects_to_https():
    app = App(enable_hsts=True)

    @app.route("/")
    async def index(req, res):
        pass

    response = app.client.get("/", allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == "https://testserver/"
