import pytest

from bocadillo import configure, create_client


@pytest.mark.parametrize(
    ["origin", "allowed"],
    [("localhost:8001", True), ("example.com", True), ("unknown.org", False)],
)
def test_allow_origin(raw_app, origin: str, allowed: bool):
    app = configure(
        raw_app, cors={"allow_origins": ["example.com", "localhost:8001"]}
    )

    @app.route("/")
    async def index(req, res):
        res.text = "OK"

    client = create_client(app)
    r = client.get("/", headers={"origin": origin})

    assert r.text == "OK"
    assert r.status_code == 200 if allowed else 400

    if allowed:  # allowed origin -> allow-origin header
        assert "access-control-allow-origin" in r.headers
        assert r.headers["access-control-allow-origin"] == origin
    else:  # unknown origin -> no allow-origin header
        assert "access-control-allow-origin" not in r.headers


def test_no_allowed_origins_by_default(raw_app):
    app = configure(raw_app, cors=True)

    @app.route("/")
    async def index(req, res):
        res.text = "OK"

    client = create_client(app)
    r = client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": "GET",
        },
    )
    assert r.status_code == 400, r.text


@pytest.mark.parametrize("method, allowed", [("GET", True), ("POST", False)])
def test_allow_method(raw_app, method, allowed):
    app = configure(
        raw_app,
        cors={"allow_origins": ["foobar.com"], "allow_methods": ["GET"]},
    )

    @app.route("/")
    async def index(req, res):
        pass

    client = create_client(app)
    r = client.options(
        "/",
        headers={
            "origin": "foobar.com",
            "access-control-request-method": method,
        },
    )
    assert r.status_code == 200 if allowed else 400
