import pytest

from bocadillo import App
from bocadillo.constants import ALL_HTTP_METHODS


@pytest.mark.parametrize("method", ALL_HTTP_METHODS)
def test_method(app: App, method: str):
    req_method = None

    @app.route("/")
    class Index:
        async def handle(self, req, res):
            nonlocal req_method
            req_method = req.method

    r = getattr(app.client, method.lower())("/")
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
def test_url(app: App, attr, value):
    url = None

    @app.route("/foo")
    async def index(req, res):
        nonlocal url
        url = req.url

    app.client.get("/foo", params={"bar": "err"})
    assert url is not None

    if attr is None:
        assert url == value
    else:
        assert getattr(url, attr) == value


def test_headers(app: App):
    @app.route("/")
    async def index(req, res):
        assert req.headers["x-foo"] == req.headers["X-Foo"] == "foo"

    r = app.client.get("/", headers={"X-Foo": "foo"})
    assert r.status_code == 200


@pytest.mark.parametrize("data, status", [("{", 400), ("{}", 200)])
def test_parse_json(app: App, data: str, status: int):
    @app.route("/")
    class Index:
        async def post(self, req, res):
            res.media = await req.json()

    assert app.client.post("/", data=data).status_code == status


@pytest.mark.parametrize(
    "get_stream", [lambda req: req, lambda req: req.stream()]
)
def test_stream_request(app: App, get_stream):
    @app.route("/")
    class Index:
        async def get(self, req, res):
            chunks = [
                chunk.decode() async for chunk in get_stream(req) if chunk
            ]
            res.media = chunks

    # For testing, we use a chunk-encoded request. See:
    # http://docs.python-requests.org/en/master/user/advanced/#chunk-encoded-requests

    message = "Hello, world!"

    def stream():
        for _ in range(3):
            yield message

    response = app.client.get("/", data=stream())
    assert response.json() == [message] * 3
