import pytest

from bocadillo import App, configure, useprovider, WebSocket


@pytest.fixture
def app(raw_app: App) -> App:
    return configure(raw_app, provider_modules=["tests.data.providerconf"])


async def say_hi(req, res, hello):
    res.text = hello


class SayHi:
    async def get(self, req, res, hello):
        res.text = hello


async def say_hi_to(req, res, hello_format, who):
    res.text = hello_format.format(who=who)


class SayHiTo:
    async def get(self, req, res, hello_format, who):
        res.text = hello_format.format(who=who)


@pytest.mark.parametrize("view", (say_hi, SayHi))
def test_basic(app: App, client, view):
    app.route("/hi")(view)
    r = client.get("/hi")
    assert r.status_code == 200
    assert r.text == "Hello, providers!"


@pytest.mark.parametrize("view", (say_hi_to, SayHiTo))
def test_with_route_parameter(app: App, client, view):
    app.route("/hi/{who}")(view)
    r = client.get("/hi/peeps")
    assert r.status_code == 200
    assert r.text == "Hello, peeps!"


def test_provider_name(app: App, client):
    @app.route("/foo")
    async def say_foo(req, res, foo):
        res.text = foo

    r = client.get("/foo")
    assert r.status_code == 200
    assert r.text == "foo"


def test_websocket_clients_example(app: App, client):
    @app.websocket_route("/chat")
    async def chat(ws: WebSocket, clients: list):
        clients.add(ws)
        try:
            await ws.send_text(str(len(clients)))
            await ws.receive_text()
        finally:
            clients.remove(ws)

    @app.route("/clients")
    async def client_count(req, res, clients: list):
        res.json = {"count": len(clients)}

    with client.websocket_connect("/chat") as ws:
        assert ws.receive_text() == "1"
        r = client.get("/clients")
        assert r.status_code == 200
        assert r.json() == {"count": 1}


def test_useprovider(app: App, client):
    @app.route("/")
    @useprovider("set_called")
    async def index(req, res, spy):
        res.json = spy

    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["called"] is True
