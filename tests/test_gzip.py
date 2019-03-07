from bocadillo import App
from bocadillo.testing import create_client


def test_if_gzip_enabled_then_response_is_compressed():
    app = App(enable_gzip=True, gzip_min_size=0)

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    response = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
