import pytest

from bocadillo import App, provider, useprovider, WebSocket


@pytest.fixture(autouse=True)
async def hello_provider():
    @provider
    async def hello_format():
        return "Hello, {who}!"

    @provider
    async def hello(hello_format) -> str:
        return hello_format.format(who="providers")


def test_function_based_view(app: App, client):
    @app.route("/hi")
    async def say_hi(req, res, hello):
        res.text = hello

    r = client.get("/hi")
    assert r.status_code == 200
    assert r.text == "Hello, providers!"


def test_function_based_view_with_route_parameters(app: App, client):
    @app.route("/hi/{who}")
    async def say_hi(req, res, hello_format, who):
        res.text = hello_format.format(who=who)

    r = client.get("/hi/peeps")
    assert r.status_code == 200
    assert r.text == "Hello, peeps!"


def test_class_based_view(app: App, client):
    @app.route("/hi")
    class SayHi:
        async def get(self, req, res, hello):
            res.text = hello

    r = client.get("/hi")
    assert r.status_code == 200
    assert r.text == "Hello, providers!"


def test_class_based_view_with_route_parameters(app: App, client):
    @app.route("/hi/{who}")
    class SayHi:
        async def get(self, req, res, hello_format, who):
            res.text = hello_format.format(who=who)

    r = client.get("/hi/peeps")
    assert r.status_code == 200
    assert r.text == "Hello, peeps!"


@pytest.fixture(autouse=True)
def clients_provider():
    @provider(scope="app")
    async def clients():
        return set()


def test_websocket_clients_example(app: App, client):
    @app.websocket_route("/chat")
    async def chat(ws: WebSocket, clients):
        clients.add(ws)
        await ws.send_text(str(len(clients)))

    @app.route("/clients")
    async def client_count(req, res, clients):
        res.json = {"count": len(clients)}

    with client.websocket_connect("/chat") as ws:
        assert ws.receive_text() == "1"

    r = client.get("/clients")
    assert r.status_code == 200
    assert r.json() == {"count": 1}


@pytest.mark.parametrize("by_name", (False, True))
def test_useprovider(app: App, client, by_name):
    called = False

    @provider
    async def set_called():
        nonlocal called
        called = True

    @app.route("/")
    @useprovider("set_called" if by_name else set_called)
    async def index(req, res):
        pass

    r = client.get("/")
    assert r.status_code == 200
    assert called
