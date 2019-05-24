import pytest

from bocadillo import App, Router, configure, create_client


def test_index_returns_404_by_default(app: App, client):
    assert client.get("/").status_code == 404


def test_if_route_not_registered_then_404(app: App, client):
    assert client.get("/test").status_code == 404


def test_if_route_registered_then_not_404(app: App, client):
    @app.route("/")
    async def index(req, res):
        pass

    assert client.get("/").status_code != 404


def test_default_status_code_is_200_on_routes(app: App, client):
    @app.route("/")
    async def index(req, res):
        pass

    assert client.get("/").status_code == 200


def test_leading_slash_is_added_if_not_present(app: App, client):
    @app.route("foo")
    async def index(req, res):
        pass

    assert client.get("/foo").status_code == 200


def test_trailing_slash_not_redirected(app, client):
    @app.route("/foo")
    async def foo(req, res):
        pass

    assert client.get("/foo/").status_code == 404


@pytest.mark.parametrize("redirect", (None, True, False))
def test_redirect_trailing_slash(raw_app, redirect):
    settings = {}
    if redirect is not None:
        settings["redirect_trailing_slash"] = redirect

    app = configure(raw_app, **settings)
    client = create_client(app)

    @app.route("/foo/")
    async def foo(req, res):
        pass

    r = client.get("/foo", allow_redirects=False)

    if redirect or redirect is None:
        assert r.status_code == 302
    else:
        assert r.status_code == 404


@pytest.mark.parametrize(
    "path, status",
    [
        ("/", 404),
        ("/1", 404),
        ("/tacos", 200),
        ("/tacos/", 200),
        ("/tacos/1", 200),
        ("/tacos/gluten-free", 200),
    ],
)
def test_include_router(app, client, path, status):
    router = Router()

    @router.route("/")
    async def get_tacos(req, res):
        pass

    @router.route("/{pk}")
    async def get_taco(req, res, pk):
        pass

    # Starts with same prefix than router, but should not be shadowed by it.
    @app.route("/tacos/gluten-free")
    async def gluten_free_tacos(req, res):
        pass

    app.include_router(router, prefix="/tacos")
    assert client.get(path).status_code == status
