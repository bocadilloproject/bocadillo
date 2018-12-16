from bocadillo import API


def test_startup_and_shutdown(api: API):
    message = None

    @api.on("startup")
    async def setup():
        nonlocal message
        message = "hi"

    @api.on("shutdown")
    async def cleanup():
        nonlocal message
        message = None

    @api.route("/")
    async def index(req, res):
        res.text = message

    # The Starlette TestClient calls startup and shutdown events when
    # used as a context manager.
    with api.client:
        assert message == "hi"
        response = api.client.get("/")
        assert response.text == "hi"
    assert message is None


def test_sync_handler(api: API):
    message = None

    @api.on("startup")
    def setup():
        nonlocal message
        message = "hi"

    with api.client:
        assert message == "hi"


def test_non_decorator_syntax(api: API):
    message = None

    async def setup():
        nonlocal message
        message = "hi"

    api.on("startup", setup)

    with api.client:
        assert message == "hi"
