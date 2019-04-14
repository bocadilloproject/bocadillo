import pytest

from starlette.datastructures import FormData

from bocadillo import App
from bocadillo.constants import ALL_HTTP_METHODS


@pytest.mark.parametrize("method", ALL_HTTP_METHODS)
def test_method(app: App, client, method: str):
    req_method = None

    @app.route("/")
    class Index:
        async def handle(self, req, res):
            nonlocal req_method
            req_method = req.method

    r = getattr(client, method.lower())("/")
    assert req_method == method


@pytest.mark.parametrize(
    "attr, value",
    [
        (None, "http://testserver/foo?bar=err"),
        ("path", "/foo"),
        ("scheme", "http"),
        ("hostname", "testserver"),
        ("query", "bar=err"),
        ("is_secure", False),
    ],
)
def test_url(app: App, client, attr, value):
    url = None

    @app.route("/foo")
    async def index(req, res):
        nonlocal url
        url = req.url

    client.get("/foo", params={"bar": "err"})
    assert url is not None

    if attr is None:
        assert url == value
    else:
        assert getattr(url, attr) == value


def test_headers(app: App, client):
    @app.route("/")
    async def index(req, res):
        # Key access.
        assert req.headers["x-foo"] == "foo"
        with pytest.raises(KeyError):
            req.headers["x-bar"]

        # Case insensitivity.
        assert req.headers["x-foo"] == req.headers["X-Foo"] == "foo"

        # Defaults.
        assert req.headers.get("x-bar", 1) == 1

    r = client.get("/", headers={"X-Foo": "foo"})
    assert r.status_code == 200


def test_query_params(app: App, client):
    @app.route("/")
    async def index(req, res):
        assert req.url.query == "a=alpha&b=beta&b=BETA&b=Beta"

        # Key access.
        assert req.query_params["a"] == "alpha"
        with pytest.raises(KeyError):
            req.query_params["c"]

        # Defaults
        assert req.query_params.get("a") == "alpha"
        assert req.query_params.get("c") is None

        # Multiple values
        last_item = "Beta"
        assert req.query_params["b"] == last_item
        assert req.query_params.getlist("b") == ["beta", "BETA", "Beta"]

    r = client.get("/", params={"a": "alpha", "b": ["beta", "BETA", "Beta"]})
    assert r.status_code == 200


def test_raw_body(app: App, client):
    @app.route("/")
    async def index(req, res):
        body = await req.body()
        assert isinstance(body, bytes)
        res.content = body

    r = client.get("/", data="hello")
    assert r.status_code == 200
    assert r.content == b"hello"


def test_form_body(app: App, client):
    @app.route("/")
    async def index(req, res):
        form = await req.form()
        assert isinstance(form, FormData)
        # not actually a dict, so not immediately JSON-serializable
        res.json = dict(form)

    r = client.get("/", data={"foo": "bar"})
    assert r.status_code == 200
    assert r.json() == {"foo": "bar"}


@pytest.mark.parametrize("data, status", [("{", 400), ("{}", 200)])
def test_json_body(app: App, client, data: str, status: int):
    @app.route("/")
    class Index:
        async def post(self, req, res):
            res.json = await req.json()

    assert client.post("/", data=data).status_code == status


@pytest.mark.parametrize(
    "get_stream", [lambda req: req, lambda req: req.stream()]
)
def test_stream_request(app: App, client, get_stream):
    @app.route("/")
    class Index:
        async def get(self, req, res):
            chunks = [
                chunk.decode() async for chunk in get_stream(req) if chunk
            ]
            res.json = chunks

    # For testing, we use a chunk-encoded request. See:
    # http://docs.python-requests.org/en/master/user/advanced/#chunk-encoded-requests

    message = "Hello, world!"

    def stream():
        for _ in range(3):
            yield message

    response = client.get("/", data=stream())
    assert response.json() == [message] * 3
