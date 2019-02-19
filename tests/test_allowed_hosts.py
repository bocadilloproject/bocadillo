from bocadillo import App


def test_if_host_not_allowed_then_400():
    app = App(allowed_hosts=["example.com"])

    @app.route("/")
    async def index(req, res):
        pass

    response = app.client.get("/")
    assert response.status_code == 400
