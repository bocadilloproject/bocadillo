import pytest

from bocadillo import App, provider, WebSocket


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
        res.media = {"count": len(clients)}

    with client.websocket_connect("/chat") as ws:
        assert ws.receive_text() == "1"

    r = client.get("/clients")
    assert r.status_code == 200
    assert r.json() == {"count": 1}
