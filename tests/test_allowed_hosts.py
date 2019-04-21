from bocadillo import configure, create_client


def test_if_host_not_allowed_then_400(raw_app):
    app = configure(raw_app, allowed_hosts=["example.com"])
    client = create_client(app)

    @app.route("/")
    async def index(req, res):
        pass

    response = client.get("/")
    assert response.status_code == 400
