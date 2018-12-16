from bocadillo import API


def test_startup_and_shutdown(api: API):
    data = None

    @api.on("startup")
    async def setup():
        nonlocal data
        data = {"message": "foo"}

    @api.on("shutdown")
    async def cleanup():
        nonlocal data
        data = None

    @api.route("/")
    async def index(req, res):
        res.media = data

    # The Starlette TestClient calls startup and shutdown events when
    # used as a context manager.
    with api.client:
        assert data == {"message": "foo"}
        response = api.client.get("/")
        assert response.json() == data
    assert data is None
